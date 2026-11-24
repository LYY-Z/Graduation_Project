"""Validated, root-relative deployment configuration."""

from __future__ import annotations

import ipaddress
from pathlib import Path

import numpy as np
import yaml

from .geometry import finite_vector


def load_config(path):
    path = Path(path).resolve()
    with path.open(encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    if not isinstance(cfg, dict) or cfg.get("schema_version") not in {1, 2}:
        raise ValueError("unsupported platform configuration schema")
    root = (path.parent / cfg["project_root"]).resolve()
    cfg["_root"] = root
    for name, relative in cfg["paths"].items():
        resolved = (root / relative).resolve()
        if root not in resolved.parents:
            raise ValueError(f"path {name} must stay inside this deployment package")
        cfg["paths"][name] = resolved
    execution = cfg.get("execution", {})
    if cfg["schema_version"] == 1:
        if execution.get("enabled") is not False or execution.get("implementation") != "absent":
            raise ValueError("legacy configuration must not authorize motion")
    elif (
        execution.get("implementation") != "guarded"
        or execution.get("default_mode") != "preview"
        or execution.get("enabled", False) is not False
    ):
        raise ValueError("execution configuration must default to guarded preview")
    ipaddress.ip_address(cfg["robot"]["ip"])
    if cfg["robot"]["state_interface"] != "rtde_receive_only":
        raise ValueError("unsupported robot state interface")
    for name in ["report_tcp_offset_m_rad", "declared_active_tcp_offset_m_rad"]:
        finite_vector(cfg["robot"][name], 6, name)
    if cfg["camera"]["image_shape_hw"] != [96, 96]:
        raise ValueError("prepared checkpoint image size is fixed at 96x96")
    if cfg["mapping"]["mode"] != "relative_anchor":
        raise ValueError("only the explicitly uncalibrated relative-anchor map is implemented")
    for key, value in [
        ("robot.receive_hz", cfg["robot"]["receive_hz"]),
        ("camera.publication_hz", cfg["camera"]["publication_hz"]),
        ("camera.frame_store_poll_hz", cfg["camera"]["frame_store_poll_hz"]),
        *[("observation." + k, v) for k, v in cfg["observation"].items()],
        ("inference.max_predictions", cfg["inference"]["max_predictions"]),
        ("inference.max_duration_s", cfg["inference"]["max_duration_s"]),
    ]:
        if not np.isfinite(value) or value <= 0:
            raise ValueError(key + " must be positive and finite")
    if cfg["observation"]["n_obs_steps"] != 2:
        raise ValueError("prepared checkpoint expects two observation steps")
    if cfg["robot"]["receive_hz"] > 500:
        raise ValueError("RTDE state receive frequency exceeds report maximum")
    count = cfg["inference"]["max_predictions"]
    if isinstance(count, bool) or not isinstance(count, int) or count < 1:
        raise ValueError("inference.max_predictions must be a positive integer")
    return cfg
