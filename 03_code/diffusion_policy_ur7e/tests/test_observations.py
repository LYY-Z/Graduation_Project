import numpy as np
import pytest

from dp_ur7e.hardware.camera import CameraFrame
from dp_ur7e.geometry import PlanarMapping
from dp_ur7e.hardware.observations import ObservationHistory, RobotSample


def history():
    m = PlanarMapping([0, 0, 0], [[1, 0, 0], [0, 1, 0]], [1000, 1000], [256, 256], [0, 512])
    return ObservationHistory(m, n_obs=2, period_s=0.1, max_age_s=0.5, max_skew_s=0.05)


def frame(seq, t):
    return CameraFrame(np.full((96, 96, 3), seq, np.uint8), seq, t, 1000 + t, "rgb_optical")


def sample(t, x=0.01):
    return RobotSample(t, t + 100, np.array([x, 0, 0]), np.zeros(6), np.zeros(6), 1, 7)


def test_causal_alignment_and_observation_shapes():
    h = history()
    h.add_robot(sample(1.99))
    h.add_robot(sample(2.09, 0.02))
    h.add_frame(frame(1, 2.0))
    h.add_frame(frame(2, 2.1))
    obs, evidence = h.build(now=2.15)
    assert obs["image"].shape == (1, 2, 3, 96, 96)
    np.testing.assert_allclose(obs["agent_pos"][0], [[266, 256], [276, 256]])
    assert evidence["camera_sequences"] == [1, 2]
    assert evidence["sync_mode"] == "host_monotonic_causal"


def test_insufficient_history_does_not_duplicate_first_frame():
    h = history()
    h.add_robot(sample(2))
    h.add_frame(frame(1, 2))
    with pytest.raises(ValueError):
        h.build(now=2.01)


def test_future_robot_sample_is_not_used_for_earlier_image():
    h = history()
    h.add_robot(sample(2.01))
    h.add_frame(frame(1, 2.0))
    h.add_frame(frame(2, 2.1))
    with pytest.raises(ValueError):
        h.build(now=2.11)


def test_stale_history_is_rejected():
    h = history()
    h.add_robot(sample(1.99))
    h.add_robot(sample(2.09))
    h.add_frame(frame(1, 2.0))
    h.add_frame(frame(2, 2.1))
    with pytest.raises(ValueError):
        h.build(now=3.0)


def test_repeated_frame_does_not_grow_history():
    h = history()
    assert h.add_frame(frame(1, 2.0)) is True
    assert h.add_frame(frame(1, 2.0)) is False


def test_controller_timestamp_must_advance():
    h = history()
    assert h.add_robot(sample(1)) is True
    assert h.add_robot(sample(1)) is False


def test_future_host_time_is_rejected():
    h = history()
    h.add_robot(sample(1.99))
    h.add_robot(sample(2.09))
    h.add_frame(frame(1, 2))
    h.add_frame(frame(2, 2.1))
    with pytest.raises(ValueError):
        h.build(now=1.9)
