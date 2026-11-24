"""Explicit guarded control boundary, private backend validation and feedback confirmation."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import socket
import time
from dataclasses import dataclass
import numpy as np
from ..geometry import finite_vector
from .safety import rotation_distance


def load_backend(root, *, manifest_path=None):
    """Load the active backend, or a private candidate for an import-only build probe.

    Execution uses the active manifest. Candidate manifests are constrained to the
    same private directory and undergo identical source, binary and capability checks.
    """
    root = Path(root).resolve()
    report = (
        root / manifest_path
        if manifest_path is not None
        else root / ".runtime/control_backend/manifest.json"
    ).resolve()
    if root / ".runtime/control_backend" not in report.parents:
        raise ValueError("backend manifest is outside its private directory")
    if not report.is_file():
        raise ValueError("private guarded backend has not been prepared")
    manifest = json.loads(report.read_text(encoding="utf-8"))
    binary = (root / manifest["binary"]).resolve()
    if root / ".runtime/control_backend" not in binary.parents:
        raise ValueError("guarded backend binary is outside its private directory")
    if (
        not binary.is_file()
        or hashlib.sha256(binary.read_bytes()).hexdigest() != manifest["sha256"]
    ):
        raise ValueError("guarded backend binary hash mismatch")
    hashes = manifest.get("source_hashes")
    if not isinstance(hashes, dict) or not hashes:
        raise ValueError("guarded backend source manifest is empty")
    for relative, expected in hashes.items():
        source = (root / relative).resolve()
        if root / "third_party/ur_rtde_guarded/source" not in source.parents:
            raise ValueError("backend source is outside the audited vendor directory")
        if hashlib.sha256(source.read_bytes()).hexdigest() != expected:
            raise ValueError("backend sources differ from the verified build")
    spec = importlib.util.spec_from_file_location("dp_ur7e_rtde_control", binary)
    if spec is None or spec.loader is None:
        raise ValueError("guarded backend is not a loadable extension")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if (
        module.guarded_no_reconnect is not True
        or module.guarded_immediate_motion_dispatch is not True
        or not callable(getattr(module.RTDEControlInterface, "guarded_ready", None))
        or module.guarded_command_timeout_s != 1.0
        or module.guarded_send_timeout_s != 0.5
    ):
        raise ValueError("control backend does not expose audited guarded capabilities")
    return module


@dataclass(frozen=True)
class Feedback:
    host_s: float
    controller_s: float
    pose: np.ndarray
    q: np.ndarray
    speed: np.ndarray
    force: np.ndarray
    safety_mode: int
    robot_mode: int


def read_feedback(receiver):
    for _ in range(5):
        stamp = float(receiver.getTimestamp())
        arrays = [
            finite_vector(method(), 6, name)
            for method, name in [
                (receiver.getActualTCPPose, "TCP pose"),
                (receiver.getActualQ, "joint position"),
                (receiver.getActualTCPSpeed, "TCP speed"),
                (receiver.getActualTCPForce, "TCP force"),
            ]
        ]
        safety, mode = int(receiver.getSafetyMode()), int(receiver.getRobotMode())
        if float(receiver.getTimestamp()) == stamp:
            return Feedback(time.monotonic(), stamp, *arrays, safety, mode)
    raise RuntimeError("feedback packet changed during every read attempt")


def dashboard_status(host):
    # Read-only requests. No play, power, unlock, mode change or recovery commands.
    result = {}
    with socket.create_connection((host, 29999), timeout=3) as connection:
        connection.settimeout(3)
        stream = connection.makefile("rwb", buffering=0)
        try:
            result["greeting"] = stream.readline(4096).decode().strip()
            for query in [
                "robotmode",
                "safetystatus",
                "running",
                "is in remote control",
            ]:
                stream.write((query + "\n").encode())
                result[query] = stream.readline(4096).decode().strip()
        finally:
            stream.close()
    return result


def require_dashboard_ready(status):
    expected = {
        "robotmode": "Robotmode: RUNNING",
        "safetystatus": "Safetystatus: NORMAL",
        "running": "Program running: false",
        "is in remote control": "true",
    }
    if any(status.get(k) != v for k, v in expected.items()):
        raise ValueError("dashboard is not idle, normal and remotely controlled: " + str(status))


def connect_control(host, *, root):
    # Called only after explicit execution opt-in, idle dashboard and readiness checks.
    backend = load_backend(root)
    return backend.RTDEControlInterface(host, frequency=125.0)


class GuardedRobot:
    def __init__(
        self,
        control,
        read,
        guard,
        baseline,
        *,
        read_ready=None,
        clock=time.monotonic,
        sleep=time.sleep,
        emit=None,
    ):
        self.control, self.read, self.guard, self.baseline = (
            control,
            read,
            guard,
            baseline,
        )
        self.clock, self.sleep, self.emit = clock, sleep, emit or (lambda event: None)
        self.read_ready = read_ready
        self.last_controller = baseline.controller_s
        self.last_advance = clock()
        self.closed = False

    def check_feedback(self, state):
        for name in ["pose", "q", "speed", "force"]:
            finite_vector(getattr(state, name), 6, name)
        if not np.isfinite(state.host_s) or not 0 <= self.clock() - state.host_s <= 0.1:
            raise ValueError("feedback is stale or timestamp invalid")
        if not np.isfinite(state.controller_s) or state.controller_s < self.last_controller:
            raise ValueError("controller timestamp reset or invalid")
        if state.controller_s > self.last_controller:
            self.last_controller, self.last_advance = state.controller_s, self.clock()
        elif self.clock() - self.last_advance > 0.15:
            raise ValueError("controller timestamp has stopped advancing")
        if state.safety_mode != 1 or state.robot_mode != 7:
            raise ValueError("robot is not in normal running/safety mode")
        origin = self.guard.initial_pose
        if np.linalg.norm(state.pose[:3] - origin[:3]) > self.guard.limits.radius_m:
            raise ValueError("actual TCP outside initial envelope")
        if (
            abs(state.pose[2] - origin[2]) > 0.00015
            or rotation_distance(state.pose, origin) > 0.002
        ):
            raise ValueError("actual height or orientation departed from lock")
        if np.max(np.abs(state.q - self.baseline.q)) > np.deg2rad(1):
            raise ValueError("actual joint displacement exceeds one degree")
        if (
            np.linalg.norm(state.speed[:3]) > max(0.002, 1.5 * self.guard.limits.speed_m_s)
            or np.linalg.norm(state.speed[3:]) > 0.01
        ):
            raise ValueError("actual TCP speed exceeds monitor limit")
        if (
            np.linalg.norm(state.force[:3]) > 50
            or np.linalg.norm(state.force[:3] - self.baseline.force[:3]) > 5
            or np.linalg.norm(state.force[3:] - self.baseline.force[3:]) > 0.5
        ):
            raise ValueError("force/torque departed from stationary baseline")

    def stop(self):
        self.control.stopL(self.guard.limits.acceleration_m_s2)

    def move(self, target, *, source_stamp_s):
        before = self.read()
        self.check_feedback(before)
        self.guard.validate_target(target, before.pose)
        if np.linalg.norm(before.speed[:3]) > 0.0001:
            raise ValueError("robot is not stationary before dispatch")
        offset = finite_vector(self.control.getTCPOffset(), 6, "active TCP offset")
        if not np.allclose(offset, [0, 0, 0.244, 0, 0, 0], atol=1e-6, rtol=0):
            raise ValueError("controller active TCP offset does not match confirmed report TCP")
        target = finite_vector(target, 6, "final target")
        if not self.control.isPoseWithinSafetyLimits(target.tolist()):
            raise ValueError("controller rejected target pose safety limits")
        q_target = finite_vector(
            self.control.getInverseKinematics(target.tolist(), before.q.tolist()),
            6,
            "target IK",
        )
        if np.max(np.abs(q_target - before.q)) > 0.01 or np.max(
            np.abs(q_target - self.baseline.q)
        ) > np.deg2rad(1):
            raise ValueError("target IK changes joint branch or exceeds small-angle limit")
        if not self.control.isJointsWithinSafetyLimits(q_target.tolist()):
            raise ValueError("controller rejected target joint safety limits")
        progress_before = self.control.getAsyncOperationProgress()
        if progress_before >= 0:
            raise ValueError("a previous async motion is still running")
        if self.read_ready is None:
            raise ValueError("control ready readback is required")
        # Controller query ACK is followed by a clear command. Wait for its ready
        # readback BEFORE final feedback/source checks, never queue a motion in C++.
        deadline = self.clock() + 0.3
        stable_since = None
        while self.clock() < deadline:
            ready = self.read_ready()
            if ready == 1:
                if stable_since is None:
                    stable_since = self.clock()
                if self.clock() - stable_since >= 0.02:
                    break
            else:
                stable_since = None
            self.sleep(0.01)
        else:
            raise TimeoutError("controller did not become stably ready before dispatch")
        # Recheck fresh state and original observation age after all controller queries.
        fresh = self.read()
        self.check_feedback(fresh)
        self.guard.validate_target(target, fresh.pose)
        if np.linalg.norm(fresh.speed[:3]) > 0.0001:
            raise ValueError("robot is not stationary at final dispatch check")
        age = self.clock() - source_stamp_s
        if not np.isfinite(age) or not 0 <= age <= self.guard.limits.max_source_age_s:
            raise ValueError("prediction became stale before dispatch")
        row = {
            "event": "motion",
            "target": target.tolist(),
            "actual_before": fresh.pose.tolist(),
            "source_age_at_send_s": age,
            "completed": False,
            "speed_m_s": self.guard.limits.speed_m_s,
            "acceleration_m_s2": self.guard.limits.acceleration_m_s2,
        }
        self.emit(
            {
                "event": "motion_dispatch_intent",
                **{k: v for k, v in row.items() if k != "event"},
            }
        )
        # A slow audit write must not turn a formerly fresh target into a stale command.
        fresh = self.read()
        self.check_feedback(fresh)
        self.guard.validate_target(target, fresh.pose)
        if np.linalg.norm(fresh.speed[:3]) > 0.0001:
            raise ValueError("robot is not stationary after audit write")
        age = self.clock() - source_stamp_s
        if not np.isfinite(age) or not 0 <= age <= self.guard.limits.max_source_age_s:
            raise ValueError("prediction became stale after audit write")
        self.guard.commit(target, fresh.pose)
        row.update(actual_before=fresh.pose.tolist(), source_age_at_send_s=age)
        pending = []
        started = self.clock()
        try:
            if not self.control.moveL(
                target.tolist(),
                self.guard.limits.speed_m_s,
                self.guard.limits.acceleration_m_s2,
                True,
            ):
                raise RuntimeError("moveL command was not acknowledged")
            pending.append({"event": "motion_command_acknowledged", "target": target.tolist()})
            settled = 0
            while self.clock() - started <= self.guard.limits.move_timeout_s:
                state = self.read()
                self.check_feedback(state)
                # Confine actual motion to the commanded short segment plus tracking tolerance.
                vector = target[:3] - fresh.pose[:3]
                fraction = np.clip(
                    np.dot(state.pose[:3] - fresh.pose[:3], vector)
                    / max(np.dot(vector, vector), 1e-30),
                    0,
                    1,
                )
                if np.linalg.norm(state.pose[:3] - (fresh.pose[:3] + fraction * vector)) > 0.00015:
                    raise ValueError("actual motion departed from short target segment")
                progress = self.control.getAsyncOperationProgress()
                finished = progress < 0 and progress != progress_before
                distance = float(np.linalg.norm(target[:3] - fresh.pose[:3]))
                arrival_tolerance = min(0.00005, 0.4 * distance)
                near = np.linalg.norm(state.pose[:3] - target[:3]) <= arrival_tolerance
                still = np.linalg.norm(state.speed[:3]) <= 0.0001
                settled = settled + 1 if finished and near and still else 0
                pending.append(
                    {
                        "event": "motion_feedback",
                        "elapsed_s": self.clock() - started,
                        "pose": state.pose.tolist(),
                        "q": state.q.tolist(),
                        "speed": state.speed.tolist(),
                        "force": state.force.tolist(),
                        "controller_s": state.controller_s,
                        "async_progress": progress,
                    }
                )
                if settled >= 3:
                    row.update(
                        completed=True,
                        actual_after=state.pose.tolist(),
                        elapsed_s=self.clock() - started,
                    )
                    for event in pending:
                        self.emit(event)
                    self.emit(row)
                    return row
                self.sleep(0.02)
            raise TimeoutError("bounded move did not settle before timeout")
        except BaseException:
            try:
                self.stop()
            except Exception as exc:
                self.emit({"event": "stop_failed", "error": repr(exc)})
            for event in pending:
                try:
                    self.emit(event)
                except Exception:
                    break
            raise

    def close(self):
        if self.closed:
            return
        self.closed = True
        errors = []
        for action in [self.stop, self.control.stopScript, self.control.disconnect]:
            try:
                action()
            except Exception as exc:
                errors.append(exc)
        if errors:
            raise errors[0]
