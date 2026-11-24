import importlib
import sys
import time

import numpy as np
import pytest
from test_contracts_and_robot import model_cfg
from test_observations import history, sample

from dp_ur7e.hardware.camera import CameraFrame
from dp_ur7e.geometry import report_tcp_position
from dp_ur7e.hardware.camera import resize_for_policy
from dp_ur7e.inference.policy import validate_model_config
from dp_ur7e.hardware.observations import SensorSession


def test_importing_entry_points_does_not_import_hardware_or_torch():
    # Import-time side effects would make --help unsafe and break ROS/conda separation.
    for name in ["dp_ur7e.cli", "dp_ur7e.pipeline", "dp_ur7e.hardware.camera_bridge"]:
        importlib.import_module(name)
    assert "rtde_receive" not in sys.modules
    assert "rtde_control" not in sys.modules
    assert "rclpy" not in sys.modules
    assert "torch" not in sys.modules


def test_half_turn_tcp_rotation_is_handled():
    result = report_tcp_position([0, 0, 0.5, np.pi, 0, 0], [0] * 6, [0, 0, 0.244, 0, 0, 0])
    np.testing.assert_allclose(result, [0, 0, 0.256], atol=1e-8)


def test_camera_ros_delay_is_included_in_freshness():
    h = history()
    h.add_robot(sample(1.99))
    h.add_robot(sample(2.09))
    for seq, stamp in [(1, 2.0), (2, 2.1)]:
        h.add_frame(
            CameraFrame(
                np.zeros((96, 96, 3), np.uint8),
                seq,
                stamp,
                100,
                "rgb",
                ros_age_at_receive_s=0.49,
            )
        )
    with pytest.raises(ValueError):
        h.build(now=2.15)


def test_bridge_restart_requires_new_observation_history():
    h = history()
    h.add_robot(sample(1.99))
    h.add_robot(sample(2.09))
    h.add_frame(CameraFrame(np.zeros((96, 96, 3), np.uint8), 1, 2, 100, "rgb", stream_id="first"))
    h.add_frame(
        CameraFrame(np.zeros((96, 96, 3), np.uint8), 2, 2.1, 100.1, "rgb", stream_id="first")
    )
    h.build(now=2.15)
    with pytest.raises(ValueError):
        h.add_frame(
            CameraFrame(
                np.zeros((96, 96, 3), np.uint8),
                1,
                2.2,
                100.2,
                "rgb",
                stream_id="restarted",
            )
        )


def test_old_startup_stream_is_replaced_before_first_valid_observation():
    h = history()
    h.add_frame(CameraFrame(np.zeros((96, 96, 3), np.uint8), 9, 1, 100, "rgb", stream_id="old"))
    h.add_robot(sample(1.99))
    h.add_robot(sample(2.09))
    h.add_frame(CameraFrame(np.zeros((96, 96, 3), np.uint8), 1, 2, 101, "rgb", stream_id="new"))
    h.add_frame(CameraFrame(np.zeros((96, 96, 3), np.uint8), 2, 2.1, 101.1, "rgb", stream_id="new"))
    obs, evidence = h.build(now=2.15)
    assert evidence["camera_sequences"] == [1, 2]
    assert obs["image"].shape == (1, 2, 3, 96, 96)


def test_camera_pump_discards_persisted_stale_frame(monkeypatch):
    now = time.monotonic()
    cfg = {
        "camera": {"expected_frame_id": "rgb", "frame_store_poll_hz": 100},
        "paths": {"frame_store": "unused"},
        "observation": {"max_age_s": 0.5},
    }
    session = SensorSession(cfg)
    frames = [
        CameraFrame(np.zeros((96, 96, 3), np.uint8), 9, now - 10, 100, "rgb", stream_id="old"),
        CameraFrame(np.zeros((96, 96, 3), np.uint8), 1, now, 110, "rgb", stream_id="new"),
    ]

    class Store:
        def read(self):
            value = frames.pop(0)
            if not frames:
                session.stop_event.set()
            return value

    monkeypatch.setattr("dp_ur7e.hardware.observations.FrameStore", lambda path: Store())
    session._camera_loop()
    assert [f.stream_id for f in session.frames] == ["new"]


def test_center_crop_uses_middle_square_before_resize():
    image = np.zeros((96, 192, 3), np.uint8)
    image[:, 48:144] = [12, 34, 56]
    result = resize_for_policy(image)
    assert result.shape == (96, 96, 3)
    np.testing.assert_array_equal(result[0, 0], [12, 34, 56])
    np.testing.assert_array_equal(result[-1, -1], [12, 34, 56])


def test_invalid_roi_rejected():
    with pytest.raises(ValueError):
        resize_for_policy(np.zeros((96, 192, 3), np.uint8), roi_xywh=[180, 0, 96, 96])


def test_unknown_model_class_is_rejected_before_instantiation():
    cfg = model_cfg()
    cfg["policy"]["_target_"] = "some.package.ArbitraryConstructor"
    with pytest.raises(ValueError):
        validate_model_config(cfg)
