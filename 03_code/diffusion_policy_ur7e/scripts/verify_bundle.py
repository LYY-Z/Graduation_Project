"""Verify pinned sources and optional weights without model or device initialization."""

from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED = {
    ".git",
    ".local",
    ".runtime",
    ".envs",
    ".venv",
    ".cache",
    "runs",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    "build",
    "dist",
}


def digest(path):
    result = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b""):
            result.update(block)
    return result.hexdigest()


def public_files(root, *, include_model=False):
    """Select public project files; never include local configuration or run data."""
    root = Path(root).resolve()
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        parts = path.relative_to(root).parts
        if any(part in EXCLUDED for part in parts):
            continue
        # A vendored sdist may include locked egg-info as original source material.
        # Only project-generated installation metadata is disposable.
        if parts[0] != "third_party" and any(part.endswith(".egg-info") for part in parts):
            continue
        if path.name in {"config.yaml", "config.local.yaml", ".env"} or path.name.startswith(
            ".env."
        ):
            continue
        if path.suffix in {".pyc", ".part", ".so", ".pyd"}:
            continue
        if path.suffix == ".ckpt" and not include_model:
            continue
        if path.is_symlink() or root not in path.resolve().parents:
            raise ValueError("public source contains an escaping path: " + str(path))
        yield path


def verify(root=ROOT, *, check_model=False):
    """Check content hashes against source locks. Does not deserialize a checkpoint."""
    root = Path(root).resolve()
    locked = json.loads((root / "third_party/sources.json").read_text(encoding="utf-8"))
    counts = {}
    for name in ["diffusion_policy", "ur_rtde_guarded"]:
        entry = locked[name]
        source_root = (root / entry["root"]).resolve()
        if root not in source_root.parents or not entry["files"]:
            raise ValueError("invalid locked source root")
        for item in entry["files"]:
            path = (source_root / item["path"]).resolve()
            if (
                source_root not in path.parents
                or not path.is_file()
                or digest(path) != item["sha256"]
            ):
                raise ValueError("locked source differs: " + item["path"])
        counts[name] = len(entry["files"])
    patch = locked["ur_rtde_guarded"]["patch"]
    patch_path = (root / patch["path"]).resolve()
    if root not in patch_path.parents or digest(patch_path) != patch["sha256"]:
        raise ValueError("guarded SDK patch differs")
    model = json.loads((root / "models/checkpoint_manifest.json").read_text(encoding="utf-8"))
    checkpoint = root / "models" / model["file"]
    model_ok = False
    if check_model:
        if checkpoint.stat().st_size != model["bytes"] or digest(checkpoint) != model["sha256"]:
            raise ValueError("checkpoint size/SHA-256 mismatch")
        model_ok = True
    return {
        "upstream_files_verified": counts["diffusion_policy"],
        "sdk_files_verified": counts["ur_rtde_guarded"],
        "patch_verified": True,
        "checkpoint_verified": model_ok,
        "model_deserialized": False,
        "robot_connected": False,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-model", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    report = verify(check_model=args.check_model)
    report["public_files"] = [
        {"path": p.relative_to(ROOT).as_posix(), "sha256": digest(p)} for p in public_files(ROOT)
    ]
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "public_files"}, indent=2))


if __name__ == "__main__":
    main()
