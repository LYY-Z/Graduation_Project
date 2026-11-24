"""Plan a source-only SFTP deployment; --apply uploads to a NEW directory, never runs code."""

from __future__ import annotations
import argparse
import getpass
import json
from pathlib import Path, PurePosixPath
import stat

try:
    from verify_bundle import public_files, digest
except ImportError:
    import importlib.util

    _spec = importlib.util.spec_from_file_location(
        "release_files", Path(__file__).with_name("verify_bundle.py")
    )
    _module = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_module)
    public_files, digest = _module.public_files, _module.digest

ROOT = Path(__file__).resolve().parents[1]


def validate_destination(value):
    """Require an explicit absolute project directory, not a broad home/root target."""
    if not value.startswith("/") or ".." in value.split("/") or "." in value.split("/"):
        raise ValueError("remote root must be an unambiguous absolute project directory")
    target = PurePosixPath(value)
    if len(target.parts) < 4 or str(target) in {"/", "/home", "/tmp", "/root"}:
        raise ValueError("remote root must name a dedicated project directory")
    return str(target)


def upload(sftp, files, destination):
    """Create a new target and transfer files only. No command channel is opened."""
    try:
        sftp.stat(destination)
    except FileNotFoundError:
        pass
    else:
        raise FileExistsError("remote target already exists; choose a new project directory")
    parent = str(PurePosixPath(destination).parent)
    if not stat.S_ISDIR(sftp.stat(parent).st_mode):
        raise ValueError("remote parent directory does not exist")
    sftp.mkdir(destination)
    made = {destination}
    for path in files:
        relative = path.relative_to(ROOT).as_posix()
        remote = destination + "/" + relative
        folder = str(PurePosixPath(remote).parent)
        pending = []
        while folder not in made:
            pending.append(folder)
            folder = str(PurePosixPath(folder).parent)
        for item in reversed(pending):
            sftp.mkdir(item)
            made.add(item)
        sftp.put(str(path), remote + ".upload")
        sftp.rename(remote + ".upload", remote)
        # Verify remote content by streaming the uploaded file back through a hash.
        import hashlib

        remote_hash = hashlib.sha256()
        with sftp.open(remote, "rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                remote_hash.update(chunk)
        if remote_hash.hexdigest() != digest(path):
            raise ValueError("SFTP content verification failed: " + relative)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", required=True)
    parser.add_argument("--user", required=True)
    parser.add_argument("--remote-root", required=True)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--include-model", action="store_true")
    parser.add_argument(
        "--password", action="store_true", help="Prompt locally; never save the password"
    )
    args = parser.parse_args(argv)
    destination = validate_destination(args.remote_root)
    files = list(public_files(ROOT, include_model=args.include_model))
    print(
        json.dumps(
            {
                "mode": "upload" if args.apply else "dry_run",
                "destination": destination,
                "files": len(files),
                "bytes": sum(p.stat().st_size for p in files),
                "remote_commands": False,
            },
            indent=2,
        )
    )
    if not args.apply:
        return
    import paramiko

    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.RejectPolicy())
    try:
        client.connect(
            args.host,
            username=args.user,
            password=getpass.getpass("SSH password: ") if args.password else None,
            timeout=15,
        )
        with client.open_sftp() as sftp:
            upload(sftp, files, destination)
    finally:
        client.close()


if __name__ == "__main__":
    main()
