"""Validate dependency isolation and imports without loading weights or opening devices."""

from __future__ import annotations
import argparse
import hashlib
import importlib
import importlib.metadata
import json
from pathlib import Path
import site
import sys

ROOT = Path(__file__).resolve().parents[1]
PREFIX = ROOT / ".envs/inference"
REPORTS = ROOT / "runs/validation/environment"


def digest(path):
    value = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def protected_snapshot(base=None):
    """Read existing Conda environment metadata and user settings without changing them."""
    prefixes = {Path(base).resolve()} if base else set()
    registry = Path.home() / ".conda/environments.txt"
    if registry.is_file():
        prefixes.update(
            Path(line.strip()).resolve()
            for line in registry.read_text().splitlines()
            if line.strip()
        )
    if base and (Path(base) / "envs").is_dir():
        prefixes.update(p.resolve() for p in (Path(base) / "envs").iterdir() if p.is_dir())
    packages = {}
    for prefix in sorted(prefixes):
        if prefix == PREFIX.resolve() or not (prefix / "conda-meta").is_dir():
            continue
        packages[str(prefix)] = {
            path.name: digest(path)
            for path in sorted((prefix / "conda-meta").iterdir())
            if path.is_file()
        }
    settings = [Path.home() / ".condarc", Path.home() / ".bashrc"]
    if base:
        settings.append(Path(base) / ".condarc")
    return {
        "prefixes": packages,
        "settings": {str(p): digest(p) if p.is_file() else None for p in settings},
    }


def save(name, data):
    REPORTS.mkdir(parents=True, exist_ok=True)
    (REPORTS / name).write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["baseline", "verify", "ros"])
    parser.add_argument("--conda-base", type=Path)
    parser.add_argument("--allow-cpu", action="store_true")
    args = parser.parse_args(argv)
    if args.mode == "baseline":
        if (REPORTS / "protected_before.json").exists():
            raise FileExistsError("preserve the existing isolation baseline")
        if not args.conda_base:
            parser.error("baseline requires --conda-base")
        report = protected_snapshot(args.conda_base)
        save("protected_before.json", report)
    elif args.mode == "ros":
        report = {"python": sys.executable, "modules": {}, "ros_node_created": False}
        for name in ["rclpy", "numpy", "yaml", "cv2", "sensor_msgs.msg"]:
            module = importlib.import_module(name)
            report["modules"][name] = str(module.__file__)
        save("ros_imports.json", report)
    else:
        if Path(sys.prefix).resolve() != PREFIX.resolve() or site.ENABLE_USER_SITE:
            raise RuntimeError("use the project inference Python with PYTHONNOUSERSITE=1")
        sys.path.insert(0, str(ROOT / "third_party/diffusion_policy"))
        sys.path.insert(0, str(ROOT / "src"))
        origins = {}
        for name in [
            "numpy",
            "scipy",
            "cv2",
            "yaml",
            "torch",
            "torchvision",
            "diffusers",
            "robomimic",
            "hydra",
            "dill",
            "einops",
            "rtde_receive",
        ]:
            module = importlib.import_module(name)
            origin = Path(module.__file__).resolve()
            if PREFIX.resolve() not in origin.parents:
                raise RuntimeError("dependency escaped inference prefix: " + name)
            origins[name] = str(origin)
        for name in [
            "diffusion_policy.policy.diffusion_transformer_hybrid_image_policy",
            "diffusion_policy.policy.diffusion_unet_hybrid_image_policy",
        ]:
            importlib.import_module(name)
        torch = sys.modules["torch"]
        cuda = bool(torch.cuda.is_available())
        if not cuda and not args.allow_cpu:
            raise RuntimeError("CUDA unavailable; use --allow-cpu for dependency checks only")
        baseline = json.loads((REPORTS / "protected_before.json").read_text())
        current = protected_snapshot(args.conda_base)
        save("protected_after.json", current)
        if baseline != current:
            raise RuntimeError("protected environment metadata/settings changed")
        report = {
            "python": sys.version,
            "sys_prefix": sys.prefix,
            "modules": origins,
            "package_versions": {
                d.metadata["Name"]: d.version
                for d in importlib.metadata.distributions()
                if d.metadata.get("Name")
            },
            "cuda_available": cuda,
            "policy_constructed": False,
            "checkpoint_deserialized": False,
            "inference_run": False,
            "robot_connected": False,
            "protected_environments_unchanged": True,
        }
        save("verification.json", report)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
