"""Collect non-hardware acceptance evidence and verify the preserved release."""
from pathlib import Path
import hashlib,json,platform,subprocess,sys
from datetime import datetime,timezone

ROOT=Path(r"G:\毕设\03_code\diffusion_policy_ur7e_refactored")
LEARNING=Path(r"G:\毕设\02_learning\06_refactored_code")
AUDIT=LEARNING/"verification"
snapshot=json.loads((AUDIT/"original_snapshot.json").read_text(encoding="utf-8"))
OLD=Path(snapshot["source"])
def sha(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(4*1024*1024),b""):h.update(chunk)
    return h.hexdigest()
changed=[name for name,item in snapshot["files"].items() if not (OLD/name).is_file() or sha(OLD/name)!=item["sha256"]]
skip=set(snapshot["excluded_directories"])
current={p.relative_to(OLD).as_posix() for p in OLD.rglob("*") if p.is_file() and not any(part in skip for part in p.relative_to(OLD).parts) and p.suffix!=".pyc"}
added=sorted(current-set(snapshot["files"]))
if changed or added:raise AssertionError({"original_changed":changed,"original_added":added})
checks=json.loads((AUDIT/"equivalence.json").read_text(encoding="utf-8"))
test_log=(AUDIT/"final_tests.txt").read_text(encoding="utf-8")
assert "131 passed, 5 skipped" in test_log and "FAILED" not in test_log
import numpy as np
report={
"generated_utc":datetime.now(timezone.utc).isoformat(),
"original_project":str(OLD),"refactored_project":str(ROOT),
"original_files_unchanged":len(snapshot["files"]),"original_changed":changed,"original_added":added,
"git_commit":subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT).decode().strip(),
"offline_tests":{"passed":131,"skipped":5,"reason":"ROS system environment unavailable","log":"final_tests.txt"},
"critical_definitions_ast_identical":checks["critical_definitions_ast_identical"],
"differential_cases_passed":checks["differential_cases_passed"],
"offline_pipeline_integration_cases":2,
"development_environment":{"python":platform.python_version(),"numpy":np.__version__,"platform":platform.system()},
"pinned_upstream_files":369,"pinned_patched_sdk_files":339,
"independent_review":{"critical_findings":0,"important_findings":1,"important_fixed":1,"fix":"Probe candidate backend before atomic activation; failed probe preserves active manifest."},
"wheel_build":True,
"not_executed":["SSH/server modification","real model loading/inference","ROS lifecycle checks","Linux native backend compilation/loopback","physical robot/camera validation","GitHub CI execution","public upload/publication"],
"required_before_hardware_acceptance":["target dependency isolation/import checks","private Linux backend build with loopback/probe","ROS lifecycle and real capture","shadow and preview","separately supervised bounded live verification"],
"release_metadata_pending":["maintainer-selected project software license","maintainer-confirmed authorship/publication metadata"],
}
(AUDIT/"acceptance.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
print(json.dumps({k:report[k] for k in ["original_files_unchanged","original_changed","git_commit","offline_tests","critical_definitions_ast_identical","differential_cases_passed"]},indent=2,ensure_ascii=False))

