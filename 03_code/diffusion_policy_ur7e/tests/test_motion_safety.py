"""Safety invariants; no model, ROS or hardware is imported or connected."""

import numpy as np
import pytest


def api():
    # A missing feature is a test failure, rather than a collection/import error.
    try:
        from dp_ur7e.control import safety as motion_safety
    except ImportError:
        pytest.fail("guarded motion safety module has not been implemented")
    return motion_safety


def guard():
    return api().ActionGuard([0.3, -0.2, 0.4, 0, 3.14, 0])


def test_first_prediction_is_norm_limited_then_smoothed():
    g = guard()
    p = g.propose([10, 10, -40], g.initial_pose, source_age_s=0.8)
    assert np.linalg.norm(p[:3] - g.initial_pose[:3]) == pytest.approx(0.00004)
    np.testing.assert_array_equal(p[2:], g.initial_pose[2:])


def test_every_diagonal_step_stays_inside_euclidean_cap():
    g = guard()
    pose = g.initial_pose.copy()
    for _ in range(3):
        target = g.propose([4, 5, 6], pose, source_age_s=0.7)
        assert np.linalg.norm(target[:3] - pose[:3]) <= 0.0002 + 1e-12
        g.commit(target, pose)
        pose = target


def test_alternating_predictions_are_temporally_smoothed():
    g = guard()
    first = g.propose([1, -0.2, 0.4], g.initial_pose, source_age_s=0.5)
    g.commit(first, g.initial_pose)
    second = g.propose([-1, -0.2, 0.4], first, source_age_s=0.5)
    assert abs(second[0] - first[0]) < 0.00004


@pytest.mark.parametrize("bad", [[np.nan, 0, 0], [0, np.inf, 0], [0, 0], [0] * 4])
def test_non_finite_or_wrong_shape_rejected(bad):
    with pytest.raises(ValueError):
        guard().propose(bad, [0.3, -0.2, 0.4, 0, 3.14, 0], source_age_s=0.5)


@pytest.mark.parametrize("age", [1.5001, -0.1, np.nan])
def test_stale_or_invalid_source_rejected(age):
    g = guard()
    with pytest.raises(ValueError):
        g.propose([1, 1, 1], g.initial_pose, source_age_s=age)


def test_no_fourth_command_is_possible():
    g = guard()
    pose = g.initial_pose.copy()
    for _ in range(3):
        p = g.propose([1, 1, 1], pose, source_age_s=0.5)
        g.commit(p, pose)
        pose = p
    with pytest.raises(ValueError, match="command budget"):
        g.propose([1, 1, 1], pose, source_age_s=0.5)


def test_guard_is_not_mutated_by_preview():
    g = guard()
    a = g.propose([1, 1, 1], g.initial_pose, source_age_s=0.5)
    b = g.propose([1, 1, 1], g.initial_pose, source_age_s=0.5)
    np.testing.assert_array_equal(a, b)
    assert g.commands == 0
    assert g.path_m == 0


def test_external_displacement_and_height_changes_rejected():
    g = guard()
    for axis, delta in [(0, 0.0021), (2, 0.0003), (3, 0.01)]:
        pose = g.initial_pose.copy()
        pose[axis] += delta
        with pytest.raises(ValueError):
            g.propose([1, 1, 1], pose, source_age_s=0.5)


def test_cannot_bypass_final_limits_with_handcrafted_target():
    g = guard()
    bad = g.initial_pose.copy()
    bad[0] += 0.001
    with pytest.raises(ValueError):
        g.commit(bad, g.initial_pose)


def test_cumulative_path_budget_counts_all_directions():
    g = guard()
    pose = g.initial_pose.copy()
    for direction in [1, -1, 1]:
        target = pose.copy()
        target[0] += direction * 0.0002
        g.commit(target, pose)
        pose = target
    assert g.path_m == pytest.approx(0.0006)


def test_limits_are_frozen_and_cannot_be_widened():
    from dataclasses import FrozenInstanceError

    with pytest.raises(ValueError):
        api().MotionLimits(max_step_m=0.002)
    limits = api().MotionLimits()
    with pytest.raises(FrozenInstanceError):
        limits.max_step_m = 1


def test_hard_limits_are_positive_finite_and_use_integer_command_count():
    for kw in [
        {"max_step_m": np.nan},
        {"max_step_m": -1},
        {"max_commands": True},
        {"max_commands": 1.5},
        {"smoothing_gain": 0},
    ]:
        with pytest.raises(ValueError):
            api().MotionLimits(**kw)


def test_visible_profile_is_bounded_and_starts_with_half_millimetre():
    limits = api().MotionLimits.visible()
    assert limits.max_step_m == 0.001
    assert limits.max_path_m == 0.003
    assert limits.radius_m == 0.003
    g = api().ActionGuard([0.3, -0.2, 0.4, 0, 3.14, 0], limits)
    p = g.propose([1, 1, 1], g.initial_pose, source_age_s=0.8)
    assert np.linalg.norm(p[:2] - g.initial_pose[:2]) == pytest.approx(0.0005)
