"""Pure first-motion limits. These are engineering guards, not certified safety."""

from __future__ import annotations

from dataclasses import dataclass, fields

import numpy as np

from ..geometry import finite_vector, pose_matrix


@dataclass(frozen=True)
class MotionLimits:
    max_step_m: float = 0.0002
    radius_m: float = 0.002
    max_path_m: float = 0.0006
    speed_m_s: float = 0.001
    acceleration_m_s2: float = 0.005
    max_commands: int = 3
    smoothing_gain: float = 0.2
    max_source_age_s: float = 1.5
    move_timeout_s: float = 3.0

    def __post_init__(self):
        for field in fields(self):
            value = getattr(self, field.name)
            ceiling = {
                "max_step_m": 0.001,
                "radius_m": 0.003,
                "max_path_m": 0.003,
                "speed_m_s": 0.002,
                "smoothing_gain": 0.5,
            }.get(field.name, field.default)
            if isinstance(value, bool) or not np.isfinite(value) or not 0 < value <= ceiling:
                raise ValueError(field.name + " exceeds the positive hard ceiling")
        if not isinstance(self.max_commands, int):
            raise ValueError("max_commands must be an integer")

    @classmethod
    def visible(cls):
        return cls(
            max_step_m=0.001,
            radius_m=0.003,
            max_path_m=0.003,
            speed_m_s=0.002,
            smoothing_gain=0.5,
        )


def norm_clip(vector, maximum):
    size = float(np.linalg.norm(vector))
    return vector * min(1.0, maximum / max(size, 1e-30))


def rotation_distance(a, b):
    relative = pose_matrix(a)[:3, :3].T @ pose_matrix(b)[:3, :3]
    return float(np.arccos(np.clip((np.trace(relative) - 1) / 2, -1, 1)))


class ActionGuard:
    def __init__(self, initial_pose, limits=None):
        self.initial_pose = finite_vector(initial_pose, 6, "initial TCP pose")
        self.limits = limits or MotionLimits()
        self.last_step = np.zeros(2)
        self.last_target = self.initial_pose.copy()
        self.commands = 0
        self.path_m = 0.0

    def check_actual(self, actual):
        actual = finite_vector(actual, 6, "actual TCP pose")
        if np.linalg.norm(actual[:3] - self.initial_pose[:3]) > self.limits.radius_m:
            raise ValueError("actual TCP outside initial envelope")
        if abs(actual[2] - self.initial_pose[2]) > 0.00015:
            raise ValueError("unexpected actual height change")
        if rotation_distance(actual, self.initial_pose) > 0.002:
            raise ValueError("unexpected actual orientation change")
        if np.linalg.norm(actual[:3] - self.last_target[:3]) > 0.00015:
            raise ValueError("uncommanded displacement or tracking error")
        return actual

    def propose(self, desired_base_xyz, actual, *, source_age_s):
        if self.commands >= self.limits.max_commands:
            raise ValueError("command budget exhausted")
        if not np.isfinite(source_age_s) or not 0 <= source_age_s <= self.limits.max_source_age_s:
            raise ValueError("prediction source age exceeds limit")
        actual = self.check_actual(actual)
        desired = finite_vector(desired_base_xyz, 3, "raw mapped action")
        bounded = norm_clip(desired[:2] - actual[:2], self.limits.max_step_m)
        gain = self.limits.smoothing_gain
        step = gain * bounded + (1 - gain) * self.last_step
        remaining = self.limits.max_path_m - self.path_m
        if remaining <= 1e-12:
            raise ValueError("cumulative path budget exhausted")
        step = norm_clip(step, min(self.limits.max_step_m, remaining))
        target = self.initial_pose.copy()
        target[:2] = actual[:2] + step
        self.validate_target(target, actual)
        return target

    def validate_target(self, target, actual):
        target = finite_vector(target, 6, "final target")
        actual = self.check_actual(actual)
        if self.commands >= self.limits.max_commands:
            raise ValueError("command budget exhausted")
        distance = float(np.linalg.norm(target[:3] - actual[:3]))
        if distance > self.limits.max_step_m + 1e-12:
            raise ValueError("final target exceeds single-step limit")
        if self.path_m + distance > self.limits.max_path_m + 1e-12:
            raise ValueError("cumulative path budget exhausted")
        if np.linalg.norm(target[:3] - self.initial_pose[:3]) > self.limits.radius_m:
            raise ValueError("target outside initial envelope")
        if not np.array_equal(target[2:], self.initial_pose[2:]):
            raise ValueError("height and orientation are locked")
        return distance

    def commit(self, target, actual):
        distance = self.validate_target(target, actual)
        self.last_step = np.asarray(target)[:2] - np.asarray(actual)[:2]
        self.last_target = np.asarray(target).copy()
        self.path_m += distance
        self.commands += 1
