"""Causal observation history and concurrent acquisition lifecycle."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
import numpy as np
from .camera import CameraFrame
from ..geometry import PlanarMapping, finite_vector
from .camera import image_tensor
import threading
import time
from .camera import FrameStore


@dataclass(frozen=True)
class RobotSample:
    host_monotonic_s: float
    controller_timestamp_s: float
    report_tcp_position_m: np.ndarray
    actual_tcp_pose: np.ndarray
    q_rad: np.ndarray
    safety_mode: int
    robot_mode: int

    def validate(self):
        finite_vector(self.report_tcp_position_m, 3, "report TCP")
        finite_vector(self.actual_tcp_pose, 6, "actual TCP pose")
        finite_vector(self.q_rad, 6, "actual joint angles")
        if not np.isfinite(self.host_monotonic_s) or not np.isfinite(self.controller_timestamp_s):
            raise ValueError("robot timestamps must be finite")


class ObservationHistory:
    def __init__(
        self,
        mapping: PlanarMapping,
        n_obs=2,
        period_s=0.1,
        max_age_s=0.5,
        max_skew_s=0.05,
    ):
        if n_obs < 1 or min(period_s, max_age_s, max_skew_s) <= 0:
            raise ValueError("observation count and timing limits must be positive")
        self.mapping = mapping
        self.n_obs = int(n_obs)
        self.period_s = float(period_s)
        self.max_age_s = float(max_age_s)
        self.max_skew_s = float(max_skew_s)
        self.frames = deque(maxlen=256)
        self.robots = deque(maxlen=2048)
        self.camera_stream_locked = False

    def add_frame(self, frame: CameraFrame) -> bool:
        frame.validate()
        if self.frames:
            previous = self.frames[-1]
            if frame.stream_id != previous.stream_id:
                if self.camera_stream_locked:
                    raise ValueError(
                        "camera bridge restarted; restart shadow runner to reset history"
                    )
                self.frames.clear()
                self.frames.append(frame)
                return True
            if frame.sequence <= previous.sequence:
                return False
            if frame.host_monotonic_s <= previous.host_monotonic_s:
                raise ValueError("camera host timestamps did not advance")
        self.frames.append(frame)
        return True

    def add_robot(self, sample: RobotSample) -> bool:
        sample.validate()
        if self.robots:
            previous = self.robots[-1]
            if sample.controller_timestamp_s < previous.controller_timestamp_s:
                raise ValueError("controller clock reset; restart acquisition")
            if sample.controller_timestamp_s == previous.controller_timestamp_s:
                return False
            if sample.host_monotonic_s <= previous.host_monotonic_s:
                raise ValueError("robot host timestamps did not advance")
        self.robots.append(sample)
        return True

    def build(self, now: float):
        if not self.frames or not self.robots or not np.isfinite(now):
            raise ValueError("waiting for camera and robot history")
        latest = self.frames[-1].host_monotonic_s
        if now < latest or now - latest > self.max_age_s:
            raise ValueError("latest camera sample is stale or from a different host clock")
        selected_frames, selected_robots = [], []
        for index in range(self.n_obs):
            target = latest - (self.n_obs - 1 - index) * self.period_s
            candidates = [f for f in self.frames if f.host_monotonic_s <= target + 1e-7]
            if not candidates or target - candidates[-1].host_monotonic_s > self.max_skew_s:
                raise ValueError("insufficient camera history at requested observation rate")
            frame = candidates[-1]
            states = [s for s in self.robots if s.host_monotonic_s <= frame.host_monotonic_s]
            if not states:
                raise ValueError("no causal robot state preceding camera sample")
            state = states[-1]
            if frame.host_monotonic_s - state.host_monotonic_s > self.max_skew_s:
                raise ValueError("camera/robot acquisition skew exceeds limit")
            if (
                now - frame.host_monotonic_s > self.max_age_s
                or now - state.host_monotonic_s > self.max_age_s
            ):
                raise ValueError("observation window contains stale data")
            if now - frame.host_monotonic_s + max(0, frame.ros_age_at_receive_s) > self.max_age_s:
                raise ValueError("image was already delayed before ROS callback")
            selected_frames.append(frame)
            selected_robots.append(state)
        if len({f.sequence for f in selected_frames}) != self.n_obs:
            raise ValueError("observation history would reuse a camera frame")
        obs = {
            "image": np.stack([image_tensor(f.rgb) for f in selected_frames])[None],
            "agent_pos": np.stack(
                [self.mapping.to_model(s.report_tcp_position_m) for s in selected_robots]
            )[None],
        }
        evidence = {
            "sync_mode": "host_monotonic_causal",
            "camera_sequences": [f.sequence for f in selected_frames],
            "camera_host_monotonic_s": [f.host_monotonic_s for f in selected_frames],
            "camera_ros_stamp_s": [f.ros_stamp_s for f in selected_frames],
            "camera_ros_age_at_receive_s": [f.ros_age_at_receive_s for f in selected_frames],
            "camera_source_shape_hw": [list(f.source_shape_hw) for f in selected_frames],
            "camera_source_encoding": [f.source_encoding for f in selected_frames],
            "robot_host_monotonic_s": [s.host_monotonic_s for s in selected_robots],
            "robot_controller_timestamp_s": [s.controller_timestamp_s for s in selected_robots],
            "acquisition_skew_s": [
                f.host_monotonic_s - s.host_monotonic_s
                for f, s in zip(selected_frames, selected_robots)
            ],
            "report_tcp_position_m": [s.report_tcp_position_m.tolist() for s in selected_robots],
            "actual_tcp_pose_m_rad": [s.actual_tcp_pose.tolist() for s in selected_robots],
            "q_rad": [s.q_rad.tolist() for s in selected_robots],
            "safety_mode": [s.safety_mode for s in selected_robots],
            "robot_mode": [s.robot_mode for s in selected_robots],
        }
        self.camera_stream_locked = True
        return obs, evidence


class SensorSession:
    def __init__(self, cfg):
        self.cfg = cfg
        self.robot = None
        self.history = None
        self.mapping = None
        self.stop_event = threading.Event()
        self.lock = threading.Lock()
        self.frames, self.states = deque(maxlen=512), deque(maxlen=2048)
        self.failure = None
        self.threads = []

    def __enter__(self):
        from .robot_state import ReceiveOnlyRobot

        self.robot = ReceiveOnlyRobot.connect(self.cfg["robot"])
        try:
            initial = self.robot.read()
            mapping = self.cfg["mapping"]
            self.mapping = PlanarMapping(
                initial.report_tcp_position_m,
                mapping["axes_in_ur_base"],
                mapping["pixels_per_m"],
                mapping["anchor_px"],
                mapping["model_bounds_px"],
            )
            obs = self.cfg["observation"]
            self.history = ObservationHistory(
                self.mapping,
                obs["n_obs_steps"],
                1 / obs["rate_hz"],
                obs["max_age_s"],
                obs["max_acquisition_skew_s"],
            )
            self.history.add_robot(initial)
            for target in [self._robot_loop, self._camera_loop]:
                thread = threading.Thread(target=self._guard, args=(target,), daemon=True)
                self.threads.append(thread)
                thread.start()
            return self
        except BaseException:
            self.__exit__(None, None, None)
            raise

    def _guard(self, operation):
        try:
            operation()
        except Exception as exc:
            with self.lock:
                self.failure = exc
            self.stop_event.set()

    def _robot_loop(self):
        while not self.stop_event.is_set():
            sample = self.robot.read()
            with self.lock:
                self.states.append(sample)
            self.stop_event.wait(1 / self.cfg["robot"]["receive_hz"])

    def _camera_loop(self):
        store = FrameStore(self.cfg["paths"]["frame_store"])
        previous = None
        while not self.stop_event.is_set():
            try:
                frame = store.read()
            except FileNotFoundError:
                self.stop_event.wait(0.02)
                continue
            identity = (frame.stream_id, frame.sequence)
            if identity != previous:
                age = time.monotonic() - frame.host_monotonic_s
                if (
                    age < 0
                    or age + max(0, frame.ros_age_at_receive_s)
                    > self.cfg["observation"]["max_age_s"]
                ):
                    self.stop_event.wait(0.01)
                    continue
                if frame.frame_id != self.cfg["camera"]["expected_frame_id"]:
                    raise ValueError("camera frame_id differs from platform configuration")
                with self.lock:
                    self.frames.append(frame)
                previous = identity
            self.stop_event.wait(1 / self.cfg["camera"]["frame_store_poll_hz"])

    def observation(self):
        with self.lock:
            if self.failure is not None:
                raise RuntimeError("sensor acquisition failed") from self.failure
            frames, states = list(self.frames), list(self.states)
            self.frames.clear()
            self.states.clear()
        for state in states:
            self.history.add_robot(state)
        for frame in frames:
            self.history.add_frame(frame)
        return self.history.build(time.monotonic())

    def __exit__(self, *_):
        self.stop_event.set()
        for thread in self.threads:
            thread.join(timeout=3)
        if self.robot is not None:
            self.robot.close()
