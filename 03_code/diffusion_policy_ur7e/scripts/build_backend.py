"""Build the private guarded RTDE extension on Linux; never connect to a robot."""

from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import platform
import shutil
import subprocess
import uuid

ROOT = Path(__file__).resolve().parents[1]


def build_commands(source, build, output, python, *, jobs=2):
    """Return CMake commands without an install target or global package update."""
    return [
        [
            "cmake",
            "-S",
            str(source),
            "-B",
            str(build),
            "-DCMAKE_BUILD_TYPE=Release",
            "-DEXAMPLES=OFF",
            "-DPYTHON_BINDINGS=ON",
            "-DPYTHON_EXECUTABLE=" + str(python),
            "-DCMAKE_LIBRARY_OUTPUT_DIRECTORY=" + str(output),
            "-DFETCHCONTENT_FULLY_DISCONNECTED=ON",
            "-DFETCHCONTENT_SOURCE_DIR_PYBIND11-SRC=" + str(Path(source) / "pybind11"),
        ],
        ["cmake", "--build", str(build), "--target", "rtde_control", "-j" + str(jobs)],
    ]


def activate_backend(root, candidate, probe_command, run):
    """Probe a private candidate before atomically changing the active manifest.

    A failed probe leaves both an existing backend and a first-build absence intact.
    The original candidate remains available for diagnosing failed builds.
    """
    root = Path(root).resolve()
    candidate = Path(candidate).resolve()
    private = root / ".runtime/control_backend"
    if private not in candidate.parents or not candidate.is_file():
        raise ValueError("candidate manifest must exist inside the private backend directory")
    run(probe_command, "coexistence_import", timeout=30)
    active = private / "manifest.json"
    temporary = private / ("manifest." + uuid.uuid4().hex + ".tmp")
    try:
        with temporary.open("xb") as stream:
            stream.write(candidate.read_bytes())
        temporary.replace(active)
    finally:
        if temporary.exists():
            temporary.unlink()
    return active


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--python", type=Path, default=ROOT / ".envs/inference/bin/python")
    parser.add_argument("--jobs", type=int, default=2)
    parser.add_argument(
        "--plan", action="store_true", help="Print commands without building or writing"
    )
    args = parser.parse_args(argv)
    if not 1 <= args.jobs <= 16:
        parser.error("--jobs must be between 1 and 16")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "_" + uuid.uuid4().hex[:8]
    work = ROOT / ".cache/guarded_control" / stamp
    source, build, output = work / "source", work / "build", work / "output"
    commands = build_commands(source, build, output, args.python.resolve(), jobs=args.jobs)
    if args.plan:
        print(
            json.dumps(
                {
                    "commands": commands,
                    "native_transport_test": True,
                    "install_environment": False,
                    "robot_connected": False,
                },
                indent=2,
            )
        )
        return
    if platform.system() != "Linux":
        parser.error("the audited guarded transport backend requires Linux")
    if not args.python.is_file():
        parser.error("--python must identify the prepared inference interpreter")
    if ROOT / ".envs" not in args.python.resolve().parents:
        parser.error("the backend interpreter must be inside this project's .envs directory")
    for executable in ["cmake", "g++"]:
        if not shutil.which(executable):
            parser.error(executable + " is required; this script does not install system packages")
    spec = importlib.util.spec_from_file_location(
        "source_verifier", ROOT / "scripts/verify_bundle.py"
    )
    verifier = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(verifier)
    verifier.verify(ROOT)
    audit = json.loads((ROOT / "third_party/sources.json").read_text(encoding="utf-8"))
    source_config = audit["ur_rtde_guarded"]
    if source_config["source_state"] != "guarded_patch_already_applied":
        raise ValueError("expected the locked, already-patched source; do not apply patch twice")
    work.mkdir(parents=True, exist_ok=False)
    shutil.copytree(ROOT / source_config["root"], source)
    output.mkdir()
    logs = ROOT / "runs/validation" / ("backend_" + stamp)
    logs.mkdir(parents=True, exist_ok=False)

    def run(command, name, timeout=600):
        result = subprocess.run(command, capture_output=True, text=True, timeout=timeout)
        (logs / (name + ".txt")).write_text(result.stdout + result.stderr, encoding="utf-8")
        if result.returncode:
            raise RuntimeError(name + " failed; see " + str(logs))
        return result.stdout

    for index, command in enumerate(commands):
        run(command, "cmake_" + str(index))
    transport = work / "test_guarded_transport"
    run(
        [
            "g++",
            "-std=c++11",
            "-I" + str(source / "include"),
            "-I" + str(build),
            str(ROOT / "tests/native/test_guarded_transport.cpp"),
            str(build / "CMakeFiles/rtde_control.dir/src/rtde.cpp.o"),
            str(build / "CMakeFiles/rtde_control.dir/src/robot_state.cpp.o"),
            "-lboost_system",
            "-lboost_thread",
            "-pthread",
            "-o",
            str(transport),
        ],
        "native_compile",
    )
    run([str(transport)], "native_loopback", timeout=30)
    candidates = list(output.glob("rtde_control*.so"))
    if len(candidates) != 1:
        raise RuntimeError("expected exactly one freshly built control extension")
    private = ROOT / ".runtime/control_backend" / stamp
    private.mkdir(parents=True, exist_ok=False)
    binary = private / ("dp_ur7e_" + candidates[0].name)
    shutil.copy2(candidates[0], binary)
    source_hashes = {
        source_config["root"] + "/" + item["path"]: item["sha256"]
        for item in source_config["files"]
    }
    report = {
        "schema_version": 1,
        "base_version": "1.6.5",
        "binary": binary.relative_to(ROOT).as_posix(),
        "sha256": hashlib.sha256(binary.read_bytes()).hexdigest(),
        "bytes": binary.stat().st_size,
        "source_hashes": source_hashes,
        "build_log_directory": logs.relative_to(ROOT).as_posix(),
        "native_loopback_tested": True,
        "robot_connected_during_build": False,
    }
    candidate = private / "manifest.json"
    candidate.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    probe = (
        "import sys;sys.path.insert(0," + repr(str(ROOT / "src")) + ");"
        "import rtde_receive;from pathlib import Path;"
        "from dp_ur7e.control.robot import load_backend;"
        "m=load_backend(Path("
        + repr(str(ROOT))
        + "),manifest_path=Path("
        + repr(str(candidate))
        + "));"
        "print('COEXISTENCE_IMPORT_OK',rtde_receive.__file__,m.__file__)"
    )
    manifest = activate_backend(ROOT, candidate, [str(args.python.resolve()), "-c", probe], run)
    print(
        json.dumps(
            {
                "manifest": str(manifest),
                "native_loopback_tested": True,
                "robot_connected": False,
                "system_environment_modified": False,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
