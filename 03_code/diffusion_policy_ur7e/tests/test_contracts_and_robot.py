from pathlib import Path

import numpy as np
import pytest
import yaml

from dp_ur7e.config import load_config
from dp_ur7e.inference.policy import validate_model_config, validate_predictions
from dp_ur7e.hardware.robot_state import ReceiveOnlyRobot


class FakeReceive:
    """Hardware boundary double: no network or robot-control methods."""

    def getTimestamp(self):
        return 100.0

    def getActualTCPPose(self):
        return [0.1, 0.2, 0.3, 0, 0, 0]

    def getActualQ(self):
        return [0.0] * 6

    def getSafetyMode(self):
        return 1

    def getRobotMode(self):
        return 7

    def disconnect(self):
        pass


def test_receive_only_reader_reports_tcp_without_extra_offset():
    robot = ReceiveOnlyRobot(FakeReceive(), [0, 0, 0.244, 0, 0, 0], [0, 0, 0.244, 0, 0, 0])
    result = robot.read()
    np.testing.assert_allclose(result.report_tcp_position_m, [0.1, 0.2, 0.3])
    assert result.controller_timestamp_s == 100.0
    assert result.host_monotonic_s > 0


def test_reader_rejects_packet_changing_during_getters():
    class Changing(FakeReceive):
        tick = 0

        def getTimestamp(self):
            self.tick += 1
            return self.tick

    robot = ReceiveOnlyRobot(Changing(), [0] * 6, [0] * 6)
    with pytest.raises(RuntimeError):
        robot.read()


def test_config_paths_resolve_against_package_root_not_cwd(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    root = Path(__file__).resolve().parents[1]
    cfg = load_config(root / "config.example.yaml")
    assert cfg["paths"]["upstream"] == root / "third_party/diffusion_policy"
    assert cfg["paths"]["checkpoint"].is_absolute()
    assert cfg["robot"]["report_tcp_offset_m_rad"] == [0, 0, 0.244, 0, 0, 0]


def model_cfg():
    return {
        "n_obs_steps": 2,
        "horizon": 16,
        "n_action_steps": 8,
        "policy": {
            "_target_": "diffusion_policy.policy.diffusion_transformer_hybrid_image_policy.DiffusionTransformerHybridImagePolicy"
        },
        "shape_meta": {
            "obs": {"image": {"shape": [3, 96, 96]}, "agent_pos": {"shape": [2]}},
            "action": {"shape": [2]},
        },
    }


def test_exact_simulation_observation_schema_accepted():
    validate_model_config(model_cfg())


def test_two_camera_model_cannot_silently_enter_single_image_runner():
    cfg = model_cfg()
    cfg["shape_meta"]["obs"]["camera_3"] = {"shape": [3, 240, 320]}
    with pytest.raises(ValueError):
        validate_model_config(cfg)


def test_prediction_shape_and_nan_are_checked_without_running_a_model():
    output = {"action": np.ones((1, 8, 2)), "action_pred": np.ones((1, 16, 2))}
    validate_predictions(output, horizon=16, n_action_steps=8)
    output["action"][0, 0, 0] = float("nan")
    with pytest.raises(ValueError):
        validate_predictions(output, horizon=16, n_action_steps=8)


def test_wrong_action_horizon_rejected():
    with pytest.raises(ValueError):
        validate_predictions({"action": np.ones((8, 2)), "action_pred": np.ones((1, 16, 2))}, 16, 8)


@pytest.mark.parametrize("count", [0.5, 1.5, True])
def test_prediction_limit_must_be_integer(tmp_path, count):
    root = Path(__file__).resolve().parents[1]
    content = yaml.safe_load((root / "config.example.yaml").read_text())
    content["project_root"] = str(root)
    content["inference"]["max_predictions"] = count
    path = tmp_path / "platform.yaml"
    path.write_text(yaml.safe_dump(content))
    with pytest.raises(ValueError):
        load_config(path)
