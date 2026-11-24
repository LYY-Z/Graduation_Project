"""Auditable local run artifacts; numerical previews have no command channel."""

from __future__ import annotations

import importlib.metadata
import json
import os
import platform
import socket
import uuid
from datetime import datetime, timezone
from pathlib import Path

import numpy as np


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def environment_versions():
    result = {
        "python": platform.python_version(),
        "os": platform.platform(),
        "hostname": socket.gethostname(),
    }
    for name in [
        "torch",
        "torchvision",
        "diffusers",
        "robomimic",
        "ur-rtde",
        "numpy",
        "PyYAML",
    ]:
        try:
            result[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            result[name] = None
    return result


class RunWriter:
    def __init__(self, root, metadata):
        self.created_utc = utc_now()
        self.directory = Path(root) / (
            datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "_" + uuid.uuid4().hex[:8]
        )
        self.directory.mkdir(parents=True, exist_ok=False)
        self.events = (self.directory / "events.jsonl").open("x", encoding="utf-8", buffering=1)
        self.metadata(metadata)

    def metadata(self, value):
        # Metadata updates are complete JSON replacements; runtime artifact only.
        temp = self.directory / "metadata.json.tmp"
        temp.write_text(
            json.dumps(
                {**value, "created_utc": self.created_utc},
                ensure_ascii=False,
                indent=2,
                default=str,
                allow_nan=False,
            ),
            encoding="utf-8",
        )
        os.replace(temp, self.directory / "metadata.json")

    def append(self, record):
        line = json.dumps({"utc": utc_now(), **record}, ensure_ascii=False, allow_nan=False)
        self.events.write(line + "\n")
        self.events.flush()

    def observation(self, index, arrays):
        target = self.directory / "observations" / f"{index:06d}.npz"
        target.parent.mkdir(exist_ok=True)
        with target.open("xb") as f:
            np.savez(f, **arrays)

    def close(self):
        self.events.close()


def preview_actions(action_xy, mapping):
    raw = np.asarray(action_xy)
    converted, valid = [], []
    for row in raw:
        try:
            converted.append(mapping.to_base(row).tolist())
            valid.append(True)
        except ValueError:
            converted.append(None)
            valid.append(False)
    return {
        "raw_action_px": raw.tolist(),
        "within_engineering_bounds": valid,
        "unverified_base_xyz_m": converted,
        "calibration_status": "engineering_mapping_not_calibrated",
        "executed": False,
    }
