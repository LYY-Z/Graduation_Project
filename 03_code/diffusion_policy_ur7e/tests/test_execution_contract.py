"""Regression tests for translating model predictions into bounded commands."""

import importlib
import sys

import numpy as np
import pytest

from dp_ur7e.geometry import PlanarMapping
from dp_ur7e.control.robot import require_dashboard_ready
from dp_ur7e.control.safety import ActionGuard


def api():
    try:
        from dp_ur7e import pipeline as execution
    except ImportError:
        pytest.fail("separate execution runner has not been implemented")
    return execution


def inputs():
    mapping = PlanarMapping(
        [0.3, -0.2, 0.4], [[1, 0, 0], [0, 1, 0]], [1000, 1000], [256, 256], [0, 512]
    )
    guard = ActionGuard([0.3, -0.2, 0.4, 0, 3.14, 0])
    output = {
        "action": np.full((1, 8, 2), 300.0),
        "action_pred": np.full((1, 10, 2), 100.0),
    }
    output["action"][0, 0] = [400, 200]
    return mapping, guard, output


def test_first_executable_action_not_raw_prediction_history_is_selected():
    m, g, o = inputs()
    row = api().prepare_candidate(
        o, m, g, g.initial_pose, source_age_s=0.6, horizon=10, n_action_steps=8
    )
    assert row["raw_action_px"] == [400, 200]
    np.testing.assert_allclose(row["desired_base_xyz_m"], [0.444, -0.256, 0.4])
    assert (
        np.linalg.norm(np.array(row["target_pose_m_rad"])[:3] - g.initial_pose[:3])
        <= 0.00004 + 1e-12
    )
    assert g.commands == 0


@pytest.mark.parametrize("bad", [-1, 513, np.nan, np.inf])
def test_invalid_model_output_rejected_before_any_target(bad):
    m, g, o = inputs()
    o["action"][0, 0, 0] = bad
    with pytest.raises(ValueError):
        api().prepare_candidate(
            o, m, g, g.initial_pose, source_age_s=0.5, horizon=10, n_action_steps=8
        )


def test_incorrect_horizon_is_not_silently_sliced():
    m, g, o = inputs()
    o["action"] = o["action"][:, :7]
    with pytest.raises(ValueError):
        api().prepare_candidate(
            o, m, g, g.initial_pose, source_age_s=0.5, horizon=10, n_action_steps=8
        )


def test_source_stamp_covers_oldest_frame_and_its_robot_state():
    evidence = {
        "camera_host_monotonic_s": [10.0, 10.1],
        "camera_ros_age_at_receive_s": [0.03, 0.01],
        "robot_host_monotonic_s": [9.96, 10.09],
    }
    assert api().observation_source_stamp(evidence) == pytest.approx(9.96)
    evidence["camera_ros_age_at_receive_s"][0] = 0.08
    assert api().observation_source_stamp(evidence) == pytest.approx(9.92)


def test_live_execution_requires_site_flag_before_loading_or_connecting():
    with pytest.raises(ValueError, match="site"):
        api().run_execution({}, execute=True, site_ready=False)


def test_run_rejects_unverified_tcp_before_loading_or_connecting():
    with pytest.raises(ValueError, match="TCP"):
        api().run_execution(
            {"robot": {"active_tcp_offset_verified_on_pendant": False}},
            execute=True,
            site_ready=True,
        )


def test_importing_execution_cannot_load_any_hardware_or_ml_library():
    api()
    importlib.import_module("dp_ur7e.control.robot")
    assert not {"rtde_control", "rtde_io", "rtde_receive", "torch"}.intersection(sys.modules)


@pytest.mark.parametrize(
    "field,value",
    [
        ("running", "Program running: true"),
        ("is in remote control", "false"),
        ("safetystatus", "Safetystatus: PROTECTIVE_STOP"),
    ],
)
def test_dashboard_blocks_existing_program_local_mode_and_protective_stop(field, value):
    status = {
        "robotmode": "Robotmode: RUNNING",
        "safetystatus": "Safetystatus: NORMAL",
        "running": "Program running: false",
        "is in remote control": "true",
    }
    status[field] = value
    with pytest.raises(ValueError):
        require_dashboard_ready(status)
