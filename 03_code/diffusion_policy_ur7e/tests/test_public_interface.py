"""Public entry contracts; all checks are independent of ROS, models and robots."""

import importlib
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest
import yaml


ROOT = Path(__file__).resolve().parents[1]
MODULES = [
    "hardware.camera_bridge",
    "hardware.camera",
    "hardware.robot_state",
    "hardware.observations",
    "inference.policy",
    "control.safety",
    "control.robot",
    "pipeline",
    "geometry",
    "recording",
    "config",
    "cli",
]


def run_cli(*args):
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT / "src") + os.pathsep + env.get("PYTHONPATH", "")
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run(
        [sys.executable, "-m", "dp_ur7e", *args],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        timeout=15,
    )


def test_canonical_modules_exist_and_import_in_both_orders_without_side_effects():
    script = """
import importlib, importlib.abc, sys
class NoDevices(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split('.')[0] in {'torch', 'rclpy', 'rtde_control', 'rtde_receive', 'rtde_io', 'cv2'}:
            raise AssertionError('unexpected optional import: ' + fullname)
sys.meta_path.insert(0, NoDevices())
for name in NAMES:
    importlib.import_module('dp_ur7e.' + name)
"""
    for names in [MODULES, MODULES[::-1]]:
        env = dict(os.environ)
        result = subprocess.run(
            [sys.executable, "-c", "NAMES=" + repr(names) + "\n" + script],
            env=env,
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=15,
        )
        assert result.returncode == 0, result.stderr


def test_public_template_resolves_paths_from_project_root(tmp_path, monkeypatch):
    from dp_ur7e.config import load_config

    template = ROOT / "config.example.yaml"
    assert template.is_file(), "public configuration template has not been created"
    monkeypatch.chdir(tmp_path)
    cfg = load_config(template)
    assert cfg["paths"]["upstream"] == ROOT / "third_party/diffusion_policy"
    assert cfg["paths"]["frame_store"] == ROOT / ".runtime/wrist_rgb.npz"
    assert cfg["robot"]["active_tcp_offset_verified_on_pendant"] is False
    assert cfg["robot"]["ip"] == "192.0.2.1"
    assert cfg["execution"]["implementation"] == "guarded"


def test_help_exposes_all_modes_without_needing_a_local_configuration():
    result = run_cli("--help")
    assert result.returncode == 0, result.stderr
    for command in ["inspect", "camera-bridge", "capture", "shadow", "preview", "execute"]:
        assert command in result.stdout


def test_execute_requires_site_declaration_before_configuration_or_devices():
    result = run_cli("execute", "--config", "missing-local-config.yaml")
    assert result.returncode == 2
    assert "--site-ready" in result.stderr
    assert "Traceback" not in result.stderr


def test_site_flag_cannot_enable_a_read_only_command():
    result = run_cli("shadow", "--site-ready", "--config", "missing-local-config.yaml")
    assert result.returncode == 2
    assert "only" in result.stderr.lower() and "execute" in result.stderr


def test_inspect_can_report_absent_weights_without_loading_them(tmp_path):
    template = ROOT / "config.example.yaml"
    assert template.is_file(), "public template missing"
    cfg = yaml.safe_load(template.read_text(encoding="utf-8"))
    cfg["project_root"] = str(ROOT)
    cfg["paths"]["checkpoint"] = ".runtime/not-downloaded-test.ckpt"
    path = tmp_path / "config.yaml"
    path.write_text(yaml.safe_dump(cfg), encoding="utf-8")
    result = run_cli("inspect", "--config", str(path))
    assert result.returncode == 0, result.stderr
    info = json.loads(result.stdout)
    assert info["checkpoint_present"] is False
    assert info["checkpoint_sha256_verified"] is False
    assert info["model_loaded"] is False
    assert info["hardware_connected"] is False


def test_hardware_modes_reject_the_documentation_address_before_connecting():
    result = run_cli("capture", "--config", "config.example.yaml")
    assert result.returncode == 2
    assert "documentation" in result.stderr.lower()


def test_unprepared_backend_remains_fail_closed_in_relocated_directory(tmp_path):
    try:
        module = importlib.import_module("dp_ur7e.control.robot")
    except ImportError:
        pytest.fail("canonical control module has not been created")
    with pytest.raises(ValueError, match="prepared"):
        module.load_backend(tmp_path)


def test_backend_rejects_an_empty_source_manifest_before_importing_native_code(tmp_path):
    try:
        module = importlib.import_module("dp_ur7e.control.robot")
    except ImportError:
        pytest.fail("canonical control module has not been created")
    location = tmp_path / ".runtime/control_backend"
    location.mkdir(parents=True)
    binary = location / "not-native.so"
    binary.write_bytes(b"not executable")
    (location / "manifest.json").write_text(
        json.dumps(
            {
                "binary": ".runtime/control_backend/not-native.so",
                "sha256": hashlib.sha256(binary.read_bytes()).hexdigest(),
                "source_hashes": {},
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="source manifest is empty"):
        module.load_backend(tmp_path)


def test_candidate_manifest_cannot_escape_the_private_backend_directory(tmp_path):
    module = importlib.import_module("dp_ur7e.control.robot")
    with pytest.raises(ValueError, match="manifest is outside"):
        module.load_backend(tmp_path, manifest_path=tmp_path / "foreign.json")
