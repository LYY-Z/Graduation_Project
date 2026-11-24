import json

import pytest


def test_unprepared_backend_cannot_fall_back_to_installed_sdk(tmp_path):
    try:
        from dp_ur7e.control.robot import load_backend
    except ImportError:
        pytest.fail("private no-retry backend loader is missing")
    with pytest.raises(ValueError, match="prepared"):
        load_backend(tmp_path)


def test_backend_rejects_paths_outside_package(tmp_path):
    try:
        from dp_ur7e.control.robot import load_backend
    except ImportError:
        pytest.fail("private no-retry backend loader is missing")
    (tmp_path / ".runtime/control_backend").mkdir(parents=True)
    (tmp_path / ".runtime/control_backend/manifest.json").write_text(
        json.dumps({"binary": "../foreign.so", "sha256": "x", "source_hashes": {}})
    )
    with pytest.raises(ValueError):
        load_backend(tmp_path)
