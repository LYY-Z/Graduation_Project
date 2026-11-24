"""Explicit public commands; importing this module does not access any device."""

from __future__ import annotations

import argparse
import ipaddress
import json
from pathlib import Path
import signal

from .config import load_config


def inspect_config(cfg):
    """Report the local model contract without deserializing weights or devices."""
    import yaml

    from .inference.policy import sha256_file, validate_model_config

    sidecar = yaml.safe_load(cfg["paths"]["official_config"].read_text(encoding="utf-8"))
    validate_model_config(sidecar)
    manifest = json.loads(cfg["paths"]["checkpoint_manifest"].read_text(encoding="utf-8"))
    checkpoint = cfg["paths"]["checkpoint"]
    present = checkpoint.is_file()
    verified = False
    if present:
        if (
            checkpoint.stat().st_size != manifest["bytes"]
            or sha256_file(checkpoint) != manifest["sha256"]
        ):
            raise ValueError("checkpoint size or SHA-256 mismatch")
        verified = True
    return {
        "root": str(cfg["_root"]),
        "checkpoint": manifest,
        "checkpoint_present": present,
        "checkpoint_sha256_verified": verified,
        "ready_for_inference": verified,
        "input_shapes": {"image": [1, 2, 3, 96, 96], "agent_pos": [1, 2, 2]},
        "model_loaded": False,
        "hardware_connected": False,
    }


def main(argv=None):
    """Dispatch a single explicit mode; no configuration flag enables motion."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command",
        choices=["inspect", "camera-bridge", "capture", "shadow", "preview", "execute"],
    )
    parser.add_argument("--config", type=Path, default=Path("config.yaml"))
    parser.add_argument(
        "--site-ready",
        action="store_true",
        help="For execute only: operator confirms supervision, clear space, emergency stop and TCP",
    )
    args = parser.parse_args(argv)
    if args.command == "execute" and not args.site_ready:
        parser.error("execute requires --site-ready")
    if args.site_ready and args.command != "execute":
        parser.error("--site-ready is only valid with execute")
    try:
        cfg = load_config(args.config)
    except (FileNotFoundError, ValueError, KeyError, TypeError) as exc:
        parser.error(str(exc) + "; configure a local copy of config.example.yaml")
    if args.command == "inspect":
        print(json.dumps(inspect_config(cfg), indent=2, ensure_ascii=False))
        return
    address = ipaddress.ip_address(cfg["robot"]["ip"])
    documentation_ranges = [
        ipaddress.ip_network("192.0.2.0/24"),
        ipaddress.ip_network("198.51.100.0/24"),
        ipaddress.ip_network("203.0.113.0/24"),
    ]
    if any(address in net for net in documentation_ranges):
        parser.error(
            "documentation-only robot address: configure the actual device before hardware modes"
        )

    def terminate(signum, frame):
        raise KeyboardInterrupt("termination signal " + str(signum))

    old_handler = signal.signal(signal.SIGTERM, terminate)
    try:
        if args.command == "camera-bridge":
            from .hardware.camera_bridge import run_camera_bridge

            run_camera_bridge(cfg)
        elif args.command in {"capture", "shadow"}:
            from .pipeline import run_capture_shadow

            run_capture_shadow(cfg, inference=args.command == "shadow")
        else:
            from .pipeline import run_execution

            run_execution(cfg, execute=args.command == "execute", site_ready=args.site_ready)
    finally:
        signal.signal(signal.SIGTERM, old_handler)


if __name__ == "__main__":
    main()
