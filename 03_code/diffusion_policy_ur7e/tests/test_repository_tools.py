"""Offline contracts for release, downloads, native build plans and deployment."""

import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def tool(name):
    path = ROOT / "scripts" / (name + ".py")
    assert path.is_file(), name + " has not been implemented"
    spec = importlib.util.spec_from_file_location("test_tool_" + name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_release_checks_both_pinned_source_trees_without_deserializing_a_model():
    report = tool("verify_bundle").verify(ROOT, check_model=False)
    assert report["upstream_files_verified"] == 369
    assert report["sdk_files_verified"] > 300
    assert report["model_deserialized"] is False
    assert report["robot_connected"] is False


def test_public_file_selection_excludes_local_material_and_machine_configuration(tmp_path):
    for name in [
        "README.md",
        "config.example.yaml",
        "config.yaml",
        ".local/secret.txt",
        ".runtime/frame.npz",
        "runs/x/events.jsonl",
        "models/model.ckpt",
        "src/a.py",
    ]:
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("fixture", encoding="utf-8")
    selection = {
        p.relative_to(tmp_path).as_posix() for p in tool("verify_bundle").public_files(tmp_path)
    }
    assert selection == {"README.md", "config.example.yaml", "src/a.py"}


def test_deployment_keeps_every_file_required_by_the_pinned_source_manifest():
    module = tool("verify_bundle")
    locked = json.loads((ROOT / "third_party/sources.json").read_text(encoding="utf-8"))
    required = {
        entry["root"] + "/" + item["path"]
        for entry in [locked["diffusion_policy"], locked["ur_rtde_guarded"]]
        for item in entry["files"]
    }
    selected = {path.relative_to(ROOT).as_posix() for path in module.public_files(ROOT)}
    assert required <= selected, sorted(required - selected)


def test_native_build_plan_stays_private_and_does_not_install_into_an_environment(tmp_path):
    commands = tool("build_backend").build_commands(
        tmp_path / "source",
        tmp_path / "build",
        tmp_path / "output",
        tmp_path / ".envs/inference/bin/python",
        jobs=2,
    )
    assert len(commands) == 2
    assert "--install" not in str(commands)
    assert "rtde_control" in commands[1]
    assert any("CMAKE_LIBRARY_OUTPUT_DIRECTORY=" in value for value in commands[0])
    assert any("FETCHCONTENT" in value for value in commands[0])


@pytest.mark.parametrize("existing", [False, True])
def test_failed_backend_probe_never_activates_a_candidate(tmp_path, existing):
    module = tool("build_backend")
    private = tmp_path / ".runtime/control_backend"
    candidate = private / "candidate/manifest.json"
    candidate.parent.mkdir(parents=True)
    candidate.write_text('{"candidate": true}', encoding="utf-8")
    active = private / "manifest.json"
    previous = b'{"working": true}\n'
    if existing:
        active.write_bytes(previous)

    def fail(*_, **__):
        raise RuntimeError("simulated coexistence probe failure")

    assert hasattr(module, "activate_backend"), "transactional activation is missing"
    with pytest.raises(RuntimeError, match="probe failure"):
        module.activate_backend(tmp_path, candidate, ["python", "probe"], fail)
    assert active.read_bytes() == previous if existing else not active.exists()


def test_backend_activation_occurs_only_after_successful_probe(tmp_path):
    module = tool("build_backend")
    private = tmp_path / ".runtime/control_backend"
    candidate = private / "candidate/manifest.json"
    candidate.parent.mkdir(parents=True)
    candidate.write_text('{"candidate": true}', encoding="utf-8")
    active = private / "manifest.json"
    active.write_text('{"working": true}', encoding="utf-8")
    calls = []

    def probe(*_, **__):
        assert active.read_text(encoding="utf-8") == '{"working": true}'
        calls.append("validated")

    assert hasattr(module, "activate_backend"), "transactional activation is missing"
    assert module.activate_backend(tmp_path, candidate, ["python", "probe"], probe) == active
    assert calls == ["validated"]
    assert active.read_bytes() == candidate.read_bytes()


@pytest.mark.parametrize(
    "destination", ["/", "/home", "relative/path", "/home/user/../other", "/home/user/."]
)
def test_deployment_rejects_ambiguous_or_broad_targets(destination):
    with pytest.raises(ValueError):
        tool("deploy").validate_destination(destination)


def test_deployment_accepts_a_named_absolute_project_directory():
    assert (
        tool("deploy").validate_destination("/home/example/lyy_ws/dp_project")
        == "/home/example/lyy_ws/dp_project"
    )


def test_checkpoint_download_rejects_bad_hash_before_publishing_the_file(tmp_path, monkeypatch):
    module = tool("fetch_checkpoint")

    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *_):
            pass

        def read(self, _):
            if getattr(self, "done", False):
                return b""
            self.done = True
            return b"bad!"

    monkeypatch.setattr(module.urllib.request, "urlopen", lambda *a, **kw: Response())
    manifest = {"url": "https://example.invalid/model", "bytes": 4, "sha256": "0" * 64}
    output = tmp_path / "model.ckpt"
    with pytest.raises(ValueError, match="SHA"):
        module.download(manifest, output)
    assert not output.exists()
