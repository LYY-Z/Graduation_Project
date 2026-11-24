"""Cache all archives of a saved Conda solve, verifying SHA-256 before use."""

from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import urllib.request
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--solve-plan", type=Path, required=True)
    args = parser.parse_args(argv)
    plan = json.loads(args.solve_plan.read_text(encoding="utf-8"))
    if plan.get("success") is not True:
        raise ValueError("expected a successful complete Conda dry-run JSON")
    fetch = {item["name"]: item for item in plan["actions"]["FETCH"]}
    links = plan["actions"]["LINK"]
    if len(fetch) != len(links):
        raise ValueError("offline cache requires all linked package archives in FETCH")
    cache = ROOT / ".cache/conda_pkgs"
    cache.mkdir(parents=True, exist_ok=True)
    explicit = ["@EXPLICIT"]
    for item in links:
        record = fetch[item["name"]]
        if record["version"] != item["version"] or record["build"] != item["build_string"]:
            raise ValueError("saved fetch/link mismatch")
        name = record["fn"]
        if Path(name).name != name or not record.get("sha256"):
            raise ValueError("archive must have a plain filename and SHA-256")
        if urlparse(record["url"]).scheme != "https":
            raise ValueError("package URL must use HTTPS")
        path = cache / name

        def good():
            return (
                path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest() == record["sha256"]
            )

        if not good():
            temporary = path.with_suffix(path.suffix + ".part")
            if temporary.exists():
                raise FileExistsError("inspect previous partial archive: " + str(temporary))
            try:
                with (
                    urllib.request.urlopen(record["url"], timeout=90) as response,
                    temporary.open("xb") as stream,
                ):
                    while True:
                        chunk = response.read(1024 * 1024)
                        if not chunk:
                            break
                        stream.write(chunk)
                if hashlib.sha256(temporary.read_bytes()).hexdigest() != record["sha256"]:
                    raise ValueError("Conda archive SHA-256 mismatch")
                temporary.replace(path)
            finally:
                if temporary.exists():
                    temporary.unlink()
        explicit.append(path.as_uri() + "#" + record["md5"])
    report = ROOT / "runs/validation/environment/conda-solved-explicit.txt"
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text("\n".join(explicit) + "\n", encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
