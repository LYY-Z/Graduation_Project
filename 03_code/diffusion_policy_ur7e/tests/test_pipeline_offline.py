"""Integration through real pipeline/guards with doubles only at ML and device edges.

These tests do not exercise a neural network, the RTDE native transport, or physics.
They exercise the actual observation history, tensor adapter, action mapping,
command guards, completion monitor, and on-disk records.
"""

from collections import Counter
from contextlib import nullcontext
import json
from pathlib import Path
import sys
import time
from types import SimpleNamespace

import numpy as np
import pytest

from dp_ur7e import pipeline
from dp_ur7e.config import load_config
from dp_ur7e.geometry import PlanarMapping
from dp_ur7e.hardware.camera import CameraFrame
from dp_ur7e.hardware.observations import ObservationHistory, RobotSample

ROOT = Path(__file__).resolve().parents[1]


class Tensor:
    def __init__(self, value):
        self.value = value

    def to(self, **_):
        return self

    def detach(self):
        return self

    def cpu(self):
        return self

    def numpy(self):
        return self.value


class Policy:
    device = SimpleNamespace(type="cpu")
    dtype = "float32"

    def predict_action(self, obs):
        assert obs["image"].value.shape == (1, 2, 3, 96, 96)
        assert obs["agent_pos"].value.shape == (1, 2, 2)
        return {
            "action": Tensor(np.full((1, 8, 2), 300.0)),
            "action_pred": Tensor(np.full((1, 10, 2), 300.0)),
        }


class Receive:
    def __init__(self):
        self.pose = np.array([0.3, -0.2, 0.4, 0.0, 3.14, 0.0])
        self.tick = 100.0
        self.getters = 0
        self.disconnected = False

    def getTimestamp(self):
        if self.getters % 2 == 0:
            self.tick += 0.008
        self.getters += 1
        return self.tick

    def getActualTCPPose(self):
        return self.pose.copy()

    def getActualQ(self):
        return np.zeros(6)

    def getActualTCPSpeed(self):
        return np.zeros(6)

    def getActualTCPForce(self):
        return np.zeros(6)

    def getSafetyMode(self):
        return 1

    def getRobotMode(self):
        return 7

    def disconnect(self):
        self.disconnected = True


class Control:
    def __init__(self, receive):
        self.receive = receive
        self.progress = -1
        self.targets = []
        self.closed = False

    def getTCPOffset(self):
        return [0, 0, 0.244, 0, 0, 0]

    def isPoseWithinSafetyLimits(self, _):
        return True

    def getInverseKinematics(self, _, near):
        return near

    def isJointsWithinSafetyLimits(self, _):
        return True

    def getAsyncOperationProgress(self):
        return self.progress

    def guarded_ready(self):
        return 1

    def moveL(self, target, speed, acceleration, asynchronous):
        assert speed == 0.002 and acceleration == 0.005 and asynchronous is True
        self.targets.append(np.asarray(target))
        self.receive.pose = np.asarray(target)
        self.progress -= 1
        return True

    def stopL(self, _):
        return True

    def stopScript(self):
        return True

    def disconnect(self):
        self.closed = True


@pytest.mark.parametrize("execute", [False, True])
def test_pipeline_from_synthetic_rgb_to_records_and_bounded_completion(
    tmp_path, monkeypatch, execute
):
    receiver = Receive()
    control = Control(receiver)
    cfg = load_config(ROOT / "config.example.yaml")
    cfg["_root"] = tmp_path
    cfg["paths"]["runs"] = tmp_path / "runs"
    cfg["robot"]["active_tcp_offset_verified_on_pendant"] = True
    cfg["robot"]["ip"] = "127.0.0.1"
    details = {"horizon": 10, "n_action_steps": 8}
    torch = SimpleNamespace(
        manual_seed=lambda _: None, from_numpy=Tensor, inference_mode=nullcontext
    )
    monkeypatch.setitem(sys.modules, "torch", torch)
    monkeypatch.setitem(
        sys.modules, "rtde_receive", SimpleNamespace(RTDEReceiveInterface=lambda *a, **kw: receiver)
    )
    monkeypatch.setattr(pipeline, "load_policy", lambda _: (Policy(), details))
    # fcntl is not available on Windows; this test substitutes only that OS boundary.
    monkeypatch.setattr(pipeline, "execution_lock", lambda _: nullcontext())
    monkeypatch.setattr(
        pipeline,
        "dashboard_status",
        lambda _: {
            "robotmode": "Robotmode: RUNNING",
            "safetystatus": "Safetystatus: NORMAL",
            "running": "Program running: false",
            "is in remote control": "true",
        },
    )
    connections = []

    def connect(host, *, root):
        connections.append((host, root))
        return control

    monkeypatch.setattr(pipeline, "connect_control", connect)

    class Sensors:
        sequence = 0

        def __init__(self, _):
            self.mapping = PlanarMapping(
                receiver.pose[:3], [[1, 0, 0], [0, 1, 0]], [1000, 1000], [256, 256], [0, 512]
            )

        def __enter__(self):
            return self

        def __exit__(self, *_):
            pass

        def observation(self):
            history = ObservationHistory(self.mapping)
            now = time.monotonic()
            for index, age in enumerate([0.12, 0.02]):
                stamp = now - age
                history.add_robot(
                    RobotSample(
                        stamp - 0.001,
                        100 + index,
                        receiver.pose[:3].copy(),
                        receiver.pose.copy(),
                        np.zeros(6),
                        1,
                        7,
                    )
                )
                history.add_frame(
                    CameraFrame(
                        np.zeros((96, 96, 3), np.uint8),
                        self.sequence + index,
                        stamp,
                        100 + index,
                        "optical",
                        "synthetic",
                    )
                )
            self.sequence += 2
            return history.build(now)

    monkeypatch.setattr(pipeline, "SensorSession", Sensors)
    directory = pipeline.run_execution(cfg, execute=execute, site_ready=execute)
    events = [json.loads(line) for line in (directory / "events.jsonl").read_text().splitlines()]
    counts = Counter(row["event"] for row in events)
    assert counts["filtered_prediction"] == 3
    assert counts["completed"] == 1
    assert counts["failed"] == 0
    assert len(list((directory / "observations").glob("*.npz"))) == 3
    assert receiver.disconnected
    if execute:
        assert len(connections) == 1
        assert counts["motion_command_acknowledged"] == 3
        motions = [row for row in events if row["event"] == "motion"]
        assert len(motions) == 3 and all(row["completed"] for row in motions)
        assert control.closed
        for row in motions:
            target, before = np.array(row["target"]), np.array(row["actual_before"])
            assert np.linalg.norm(target[:3] - before[:3]) <= 0.001 + 1e-12
            np.testing.assert_array_equal(target[2:], before[2:])
    else:
        assert not connections and not control.targets
        assert counts["motion_dispatch_intent"] == 0
