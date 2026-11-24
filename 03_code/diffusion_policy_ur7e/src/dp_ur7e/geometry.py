"""Metric TCP geometry and an explicitly uncalibrated simulation input map."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


def finite_vector(value, size: int, name: str) -> np.ndarray:
    result = np.asarray(value, dtype=np.float64)
    if result.shape != (size,) or not np.all(np.isfinite(result)):
        raise ValueError(f"{name} must contain {size} finite numbers")
    return result.copy()


def pose_matrix(pose) -> np.ndarray:
    """UR pose [x,y,z,rx,ry,rz], metres and rotation-vector radians, to SE(3)."""
    value = finite_vector(pose, 6, "UR pose")
    r = value[3:]
    angle = float(np.linalg.norm(r))
    skew = np.array([[0, -r[2], r[1]], [r[2], 0, -r[0]], [-r[1], r[0], 0]])
    if angle < 1e-8:
        rotation = np.eye(3) + skew + 0.5 * (skew @ skew)
    else:
        rotation = (
            np.eye(3)
            + np.sin(angle) / angle * skew
            + (1 - np.cos(angle)) / angle**2 * (skew @ skew)
        )
    transform = np.eye(4)
    transform[:3, :3] = rotation
    transform[:3, 3] = value[:3]
    return transform


def report_tcp_position(actual_tcp_pose, active_tcp_offset, report_tcp_offset) -> np.ndarray:
    """Re-express the active controller TCP at the report's flange-relative TCP.

    The active offset is a declared operator configuration, not RTDE readback.
    If active and report offsets match, the measured position is unchanged.
    """
    base_active = pose_matrix(actual_tcp_pose)
    flange_active = pose_matrix(active_tcp_offset)
    flange_report = pose_matrix(report_tcp_offset)
    return (base_active @ np.linalg.inv(flange_active) @ flange_report)[:3, 3]


@dataclass
class PlanarMapping:
    """Invertible orthonormal two-axis map; it does not certify physical calibration."""

    origin_m: object
    axes: object
    pixels_per_m: object
    anchor_px: object
    bounds_px: object

    def __post_init__(self):
        self.origin_m = finite_vector(self.origin_m, 3, "mapping origin")
        self.axes = np.asarray(self.axes, dtype=np.float64).copy()
        if (
            self.axes.shape != (2, 3)
            or not np.all(np.isfinite(self.axes))
            or not np.allclose(self.axes @ self.axes.T, np.eye(2), atol=1e-6)
        ):
            raise ValueError("mapping axes must be two finite orthonormal base-frame vectors")
        self.pixels_per_m = finite_vector(self.pixels_per_m, 2, "pixels_per_m")
        self.anchor_px = finite_vector(self.anchor_px, 2, "anchor_px")
        self.bounds_px = finite_vector(self.bounds_px, 2, "bounds_px")
        if np.any(self.pixels_per_m <= 0) or self.bounds_px[0] >= self.bounds_px[1]:
            raise ValueError("mapping scales must be positive and bounds increasing")

    def to_model(self, position_m) -> np.ndarray:
        value = self.anchor_px + self.pixels_per_m * (
            self.axes @ (finite_vector(position_m, 3, "TCP position") - self.origin_m)
        )
        self._check_bounds(value)
        return value.astype(np.float32)

    def to_base(self, model_xy) -> np.ndarray:
        value = finite_vector(model_xy, 2, "model action")
        self._check_bounds(value)
        return self.origin_m + self.axes.T @ ((value - self.anchor_px) / self.pixels_per_m)

    def _check_bounds(self, xy):
        if np.any(xy < self.bounds_px[0]) or np.any(xy > self.bounds_px[1]):
            raise ValueError(
                f"simulation coordinates outside {self.bounds_px.tolist()}: {xy.tolist()}"
            )
