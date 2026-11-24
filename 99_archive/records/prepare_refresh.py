from pathlib import Path
import hashlib
import json
import zipfile

ROOT=Path('G:/毕设');OLD=ROOT/'99_archive/workspace_cleanup_20261123'
moves={
 '99_archive/workspace_cleanup_20261123/legacy_code.zip':'99_archive/code.zip',
 '02_learning/platform/vnc/connect.md':'02_learning/platform/vnc.md',
}
research={
 'selection_report.CN.md':'review.CN.md',
 'meeting_brief.CN.md':'briefing.CN.md',
 'README.md':'README.md',
 'additional_review.CN.md':'reviews/additional_review.CN.md',
 'dynamics_literature.md':'reviews/dynamics_literature.md',
 'fault_literature.md':'reviews/fault_literature.md',
 'policy_literature.md':'reviews/policy_literature.md',
 'hardware_interface_audit.md':'reviews/hardware_interface_audit.md',
 'platform_and_benchmark_review.md':'reviews/platform_and_benchmark_review.md',
 'proceedings_catalog.json':'evidence/proceedings_catalog.json',
 'primary_review_records.json':'evidence/primary_review_records.json',
 'source_link_checks.jsonl':'evidence/source_link_checks.jsonl',
 'check_source_links.py':'tools/check_source_links.py',
 'screen_proceedings.py':'tools/screen_proceedings.py',
}
for src,dst in research.items():moves['02_learning/motion_control/'+src]='02_learning/research/'+dst

old_archives={
 'legacy_documents.zip':'documents',
 'presentation_sources.zip':'presentations',
 'prior_archives.zip':'older_archives',
 'documentation_before.zip':'document_snapshots',
}
history=ROOT/'99_archive/history.zip'
if history.exists():raise FileExistsError(history)
records=[]
with zipfile.ZipFile(history,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as out:
 for name,prefix in old_archives.items():
  with zipfile.ZipFile(OLD/name) as source:
   for item in source.infolist():
    if item.is_dir():continue
    data=source.read(item.filename);dest=prefix+'/'+item.filename
    out.writestr(dest,data);records.append({'entry':dest,'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)})
 docs=[ROOT/'README.md',ROOT/'02_learning/README.md',ROOT/'99_archive/README.md']+list((ROOT/'02_learning').rglob('*.md'))
 for p in sorted(set(docs)):
  data=p.read_bytes();dest='before_refresh/'+p.relative_to(ROOT).as_posix()
  out.writestr(dest,data);records.append({'entry':dest,'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)})
 raw=ROOT/'02_learning/motion_control/primary_review_aids.jsonl'
 data=raw.read_bytes();dest='superseded/primary_review_aids.jsonl'
 out.writestr(dest,data);records.append({'entry':dest,'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)})
 out.writestr('README.txt','Historical documents, presentation sources and pre-refresh snapshots. The current research direction remains open. Original archive groups and paths are preserved. See entries.json for SHA-256 checks.\n')
 out.writestr('entries.json',json.dumps(records,ensure_ascii=False,indent=2))
with zipfile.ZipFile(history) as z:
 for item in records:
  if hashlib.sha256(z.read(item['entry'])).hexdigest()!=item['sha256']:raise RuntimeError(item['entry'])

# The prior compressed audit duplicates raw records that remain in records/.
with zipfile.ZipFile(OLD/'audit_records.zip') as z:
 for item in z.infolist():
  if item.is_dir():continue
  p=OLD/item.filename
  if not p.is_file() or hashlib.sha256(p.read_bytes()).digest()!=hashlib.sha256(z.read(item.filename)).digest():raise RuntimeError('Raw audit mismatch: '+item.filename)

for src,dst in moves.items():
 if not (ROOT/src).exists():raise FileNotFoundError(src)
 if (ROOT/dst).exists():raise FileExistsError(dst)
remove=[
 '02_learning/00_learning_map.md',
 '02_learning/flair/04_go2w_paper_plan.md',
 '02_learning/motion_control/primary_review_aids.jsonl',
 '02_learning/motion_control',
 '02_learning/platform/vnc',
]+['99_archive/workspace_cleanup_20261123/'+name for name in old_archives]+['99_archive/workspace_cleanup_20261123/audit_records.zip']
aliases={
 '02_learning/00_learning_map.md':'02_learning/README.md',
 '02_learning/flair/04_go2w_paper_plan.md':'99_archive/history.zip',
 '02_learning/motion_control/primary_review_aids.jsonl':'99_archive/history.zip',
}
for name in old_archives:aliases['99_archive/workspace_cleanup_20261123/'+name]='99_archive/history.zip'
aliases['99_archive/workspace_cleanup_20261123/audit_records.zip']='99_archive/records'
plan={'root':str(ROOT),'moves':moves,'remove':remove,'aliases':aliases,
 'record_move':{'source':'99_archive/workspace_cleanup_20261123','target':'99_archive/records'},
 'history':{'path':'99_archive/history.zip','sha256':hashlib.sha256(history.read_bytes()).hexdigest(),'entries':len(records)},
 'code_sha256':hashlib.sha256((OLD/'legacy_code.zip').read_bytes()).hexdigest(),
 'research':research}
(OLD/'refresh_plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'history_entries_verified':len(records),'history_MiB':round(history.stat().st_size/1048576,2),'moves':len(moves),'remove_targets':len(remove)},ensure_ascii=True))
