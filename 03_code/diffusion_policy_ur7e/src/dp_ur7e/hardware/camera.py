"""RGB conversion and atomic frame exchange; independent of ROS and torch."""

from __future__ import annotations

import numpy as np
import json
import os
import uuid
from dataclasses import dataclass
from pathlib import Path


def decode_rgb_image(message) -> np.ndarray:
    """Decode a sensor_msgs/Image-like object, including padded row stride."""
    height, width, step = int(message.height), int(message.width), int(message.step)
    if message.encoding not in {"rgb8", "bgr8"}:
        raise ValueError(f"unsupported RGB encoding: {message.encoding}")
    if height <= 0 or width <= 0 or step < width * 3:
        raise ValueError("invalid image dimensions or row stride")
    raw = np.frombuffer(bytes(message.data), dtype=np.uint8)
    if raw.size != height * step:
        raise ValueError("image buffer size does not match height * step")
    image = raw.reshape(height, step)[:, : width * 3].reshape(height, width, 3)
    if message.encoding == "bgr8":
        image = image[..., ::-1]
    return np.ascontiguousarray(image)


def resize_for_policy(rgb: np.ndarray, size_hw=(96, 96), roi_xywh=None) -> np.ndarray:
    """Explicit ROI or centre-square crop, then area resize. Requires OpenCV at runtime."""
    import cv2

    if rgb.ndim != 3 or rgb.shape[2] != 3 or rgb.dtype != np.uint8:
        raise ValueError("RGB must be HWC uint8")
    height, width = rgb.shape[:2]
    if roi_xywh is None:
        side = min(height, width)
        x, y, w, h = (width - side) // 2, (height - side) // 2, side, side
    else:
        if len(roi_xywh) != 4 or any(int(v) != v for v in roi_xywh):
            raise ValueError("ROI must be integer [x,y,width,height]")
        x, y, w, h = map(int, roi_xywh)
        if min(x, y) < 0 or min(w, h) <= 0 or x + w > width or y + h > height:
            raise ValueError("ROI lies outside source image")
    out_h, out_w = map(int, size_hw)
    if min(out_h, out_w) <= 0:
        raise ValueError("output image size must be positive")
    return np.ascontiguousarray(
        cv2.resize(rgb[y : y + h, x : x + w], (out_w, out_h), interpolation=cv2.INTER_AREA)
    )


def image_tensor(rgb: np.ndarray) -> np.ndarray:
    if rgb.shape != (96, 96, 3) or rgb.dtype != np.uint8:
        raise ValueError("checkpoint requires RGB uint8 shape (96,96,3)")
    return np.ascontiguousarray(rgb.transpose(2, 0, 1), dtype=np.float32) / 255.0


@dataclass(frozen=True)
class CameraFrame:
    rgb: np.ndarray
    sequence: int
    host_monotonic_s: float
    ros_stamp_s: float
    frame_id: str
    stream_id: str = "default"
    source_shape_hw: tuple = (96, 96)
    source_encoding: str = "rgb8"
    ros_age_at_receive_s: float = 0.0

    def validate(self):
        if self.rgb.dtype != np.uint8 or self.rgb.shape != (96, 96, 3):
            raise ValueError("frame must be 96x96 uint8 RGB")
        if (
            self.sequence < 0
            or not np.isfinite(self.host_monotonic_s)
            or not np.isfinite(self.ros_stamp_s)
        ):
            raise ValueError("invalid sequence or timestamp")
        if not self.frame_id or not self.stream_id:
            raise ValueError("frame_id and stream_id are required")
        if not np.isfinite(self.ros_age_at_receive_s) or self.ros_age_at_receive_s < -0.05:
            raise ValueError("invalid ROS image age")


class FrameStore:
    def __init__(self, path):
        self.path = Path(path)

    def write(self, frame: CameraFrame):
        frame.validate()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temp = self.path.with_name(self.path.name + "." + uuid.uuid4().hex + ".tmp")
        metadata = {
            "schema_version": 1,
            "sequence": int(frame.sequence),
            "host_monotonic_s": float(frame.host_monotonic_s),
            "ros_stamp_s": float(frame.ros_stamp_s),
            "frame_id": frame.frame_id,
            "stream_id": frame.stream_id,
            "source_shape_hw": list(frame.source_shape_hw),
            "source_encoding": frame.source_encoding,
            "ros_age_at_receive_s": float(frame.ros_age_at_receive_s),
        }
        try:
            with temp.open("wb") as f:
                np.savez(f, rgb=frame.rgb, metadata_json=np.asarray(json.dumps(metadata)))
                f.flush()
                os.fsync(f.fileno())
            os.replace(temp, self.path)
        finally:
            if temp.exists():
                temp.unlink()

    def read(self) -> CameraFrame:
        with np.load(self.path, allow_pickle=False) as content:
            metadata = json.loads(str(content["metadata_json"].item()))
            if metadata.pop("schema_version") != 1:
                raise ValueError("unsupported frame schema")
            frame = CameraFrame(rgb=content["rgb"].copy(), **metadata)
        frame.validate()
        return frame
