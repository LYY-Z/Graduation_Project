import numpy as np
import pytest

from dp_ur7e.geometry import PlanarMapping, report_tcp_position

REPORT = [0, 0, 0.244, 0, 0, 0]


def test_report_tcp_is_not_added_twice():
    np.testing.assert_allclose(
        report_tcp_position([0.2, 0.3, 0.4, 0, 0, 0], REPORT, REPORT), [0.2, 0.3, 0.4]
    )


def test_tcp_offset_is_rotated_in_flange_frame():
    actual = [0.2, 0.3, 0.4, np.pi / 2, 0, 0]
    np.testing.assert_allclose(
        report_tcp_position(actual, [0] * 6, REPORT), [0.2, 0.056, 0.4], atol=1e-8
    )


def test_replace_existing_offset_instead_of_accumulating():
    np.testing.assert_allclose(
        report_tcp_position([0, 0, 0.5, 0, 0, 0], [0, 0, 0.13, 0, 0, 0], REPORT),
        [0, 0, 0.614],
    )


@pytest.mark.parametrize("bad", [[0] * 5, [0, 0, float("nan"), 0, 0, 0]])
def test_invalid_pose_rejected(bad):
    with pytest.raises(ValueError):
        report_tcp_position(bad, REPORT, REPORT)


def mapping():
    return PlanarMapping(
        [0.1, 0.2, 0.3], [[1, 0, 0], [0, -1, 0]], [1000, 1000], [256, 256], [0, 512]
    )


def test_one_centimetre_maps_to_ten_pixels_and_y_sign_is_explicit():
    np.testing.assert_allclose(mapping().to_model([0.11, 0.22, 0.3]), [266, 236], atol=1e-4)


def test_model_action_maps_back_to_base_position_without_execution():
    np.testing.assert_allclose(mapping().to_base([266, 236]), [0.11, 0.22, 0.3])


def test_out_of_range_state_is_rejected_not_silently_clipped():
    with pytest.raises(ValueError):
        mapping().to_model([1.0, 0.2, 0.3])


def test_non_orthogonal_mapping_axes_rejected():
    with pytest.raises(ValueError):
        PlanarMapping([0, 0, 0], [[1, 0, 0], [1, 0, 0]], [1000, 1000], [256, 256], [0, 512])
