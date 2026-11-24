import json

import numpy as np
import pytest

from dp_ur7e.geometry import PlanarMapping
from dp_ur7e.recording import RunWriter, preview_actions


def test_runs_are_unique_and_records_remain_json(tmp_path):
    first = RunWriter(tmp_path, {"purpose": "contract_test"})
    second = RunWriter(tmp_path, {})
    assert first.directory != second.directory
    first.append({"value": [1, 2]})
    with pytest.raises(ValueError):
        first.append({"value": float("nan")})
    first.close()
    second.close()
    lines = (first.directory / "events.jsonl").read_text().splitlines()
    assert len(lines) == 1
    assert json.loads(lines[0])["value"] == [1, 2]


def test_session_metadata_update_keeps_creation_time(tmp_path):
    writer = RunWriter(tmp_path, {"mode": "capture"})
    initial = json.loads((writer.directory / "metadata.json").read_text())
    writer.metadata({"mode": "capture", "mapping_origin": [0, 0, 0]})
    updated = json.loads((writer.directory / "metadata.json").read_text())
    writer.close()
    assert updated["created_utc"] == initial["created_utc"]


def test_observations_saved_as_plain_arrays_without_overwrite(tmp_path):
    writer = RunWriter(tmp_path, {})
    arrays = {
        "image": np.zeros((1, 2, 3, 96, 96), dtype=np.float32),
        "agent_pos": np.zeros((1, 2, 2), dtype=np.float32),
    }
    writer.observation(0, arrays)
    with np.load(writer.directory / "observations/000000.npz", allow_pickle=False) as data:
        assert data["image"].shape == (1, 2, 3, 96, 96)
    with pytest.raises(FileExistsError):
        writer.observation(0, arrays)
    writer.close()


def test_out_of_bounds_prediction_is_flagged_and_preserved():
    mapping = PlanarMapping(
        [0.1, 0.2, 0.3], [[1, 0, 0], [0, 1, 0]], [1000, 1000], [256, 256], [0, 512]
    )
    result = preview_actions(np.array([[266, 256], [600, 200]]), mapping)
    assert result["raw_action_px"] == [[266, 256], [600, 200]]
    assert result["within_engineering_bounds"] == [True, False]
    assert result["unverified_base_xyz_m"][1] is None
    np.testing.assert_allclose(result["unverified_base_xyz_m"][0], [0.11, 0.2, 0.3])
