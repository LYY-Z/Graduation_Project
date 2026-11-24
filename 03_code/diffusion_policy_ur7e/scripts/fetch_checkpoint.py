"""Fetch the pinned official checkpoint; publish it only after size/hash verification."""

from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import urllib.request
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]


def download(manifest, output):
    """Stream trusted-source bytes to a temporary file; never deserialize weights."""
    output = Path(output)
    if urlparse(manifest["url"]).scheme != "https":
        raise ValueError("checkpoint source must use HTTPS")
    expected_size = int(manifest["bytes"])
    expected_hash = manifest["sha256"]
    if expected_size <= 0 or len(expected_hash) != 64:
        raise ValueError("invalid checkpoint manifest")

    def file_hash(path):
        value = hashlib.sha256()
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                value.update(chunk)
        return value.hexdigest()

    if output.exists():
        if output.stat().st_size == expected_size and file_hash(output) == expected_hash:
            return {"verified": True, "downloaded": False, "bytes": expected_size}
        raise FileExistsError("refusing to replace an existing unverified checkpoint")
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(output.suffix + ".part")
    if temporary.exists():
        raise FileExistsError("inspect the previous partial download before retrying")
    value, size = hashlib.sha256(), 0
    try:
        request = urllib.request.Request(manifest["url"], headers={"User-Agent": "dp-ur7e/0.2"})
        with (
            urllib.request.urlopen(request, timeout=90) as response,
            temporary.open("xb") as stream,
        ):
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                size += len(chunk)
                if size > expected_size:
                    raise ValueError("checkpoint exceeds expected size")
                value.update(chunk)
                stream.write(chunk)
        if size != expected_size or value.hexdigest() != expected_hash:
            raise ValueError("checkpoint size/SHA-256 mismatch")
        temporary.replace(output)
    finally:
        if temporary.exists():
            temporary.unlink()
    return {"verified": True, "downloaded": True, "bytes": size, "sha256": value.hexdigest()}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=ROOT / "models/checkpoint_manifest.json")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    output = args.output or ROOT / "models" / manifest["file"]
    print(json.dumps(download(manifest, output), indent=2))


if __name__ == "__main__":
    main()
