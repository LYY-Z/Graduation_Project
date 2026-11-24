from types import SimpleNamespace

import numpy as np
import pytest

from dp_ur7e.hardware.camera import CameraFrame, FrameStore
from dp_ur7e.hardware.camera import decode_rgb_image, image_tensor


def message(encoding="rgb8", step=8, data=None):
    return SimpleNamespace(
        height=2,
        width=2,
        step=step,
        encoding=encoding,
        is_bigendian=0,
        data=data or bytes([255, 0, 0, 0, 255, 0, 99, 99, 0, 0, 255, 255, 255, 255, 99, 99]),
    )


def test_rgb_decoder_honours_padded_row_stride():
    np.testing.assert_array_equal(
        decode_rgb_image(message()),
        [[[255, 0, 0], [0, 255, 0]], [[0, 0, 255], [255, 255, 255]]],
    )


def test_bgr_decoder_converts_channels():
    np.testing.assert_array_equal(decode_rgb_image(message("bgr8"))[0, 0], [0, 0, 255])


@pytest.mark.parametrize("msg", [message("16UC1"), message(step=5), message(data=b"123")])
def test_malformed_images_rejected(msg):
    with pytest.raises(ValueError):
        decode_rgb_image(msg)


def test_tensor_is_chw_float_rgb_in_zero_one_range():
    a = np.full((96, 96, 3), 255, dtype=np.uint8)
    result = image_tensor(a)
    assert result.shape == (3, 96, 96)
    assert result.dtype == np.float32
    assert float(result[0, 0, 0]) == 1.0


def test_frame_store_round_trip_retains_timestamp_and_sequence(tmp_path):
    frame = CameraFrame(
        np.zeros((96, 96, 3), dtype=np.uint8),
        5,
        10.0,
        12.5,
        "wrist_camera_color_optical_frame",
    )
    store = FrameStore(tmp_path / "frame.npz")
    store.write(frame)
    got = store.read()
    assert got.sequence == 5 and got.host_monotonic_s == 10.0 and got.ros_stamp_s == 12.5
    assert got.frame_id == frame.frame_id
    assert not list(tmp_path.glob("*.tmp"))


def test_frame_store_rejects_bad_image_shape(tmp_path):
    with pytest.raises(ValueError):
        FrameStore(tmp_path / "frame.npz").write(CameraFrame(np.zeros((3, 2)), 1, 1, 1, "frame"))
