import hashlib
import json
import zipfile
from pathlib import Path

audit=Path('G:/毕设/99_archive/workspace_cleanup_20261123')
plan=json.loads((audit/'plan.json').read_text(encoding='utf-8'))
verification=json.loads((audit/'verification.json').read_text(encoding='utf-8'))
members=[p for p in audit.iterdir() if p.is_file() and p.suffix in {'.json','.py','.ps1'}]
target=audit/'audit_records.zip'
records=[]
with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for p in sorted(members):
        data=p.read_bytes();z.writestr(p.name,data)
        records.append({'name':p.name,'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)})
with zipfile.ZipFile(target) as z:
    for record in records:
        if hashlib.sha256(z.read(record['name'])).hexdigest()!=record['sha256']:raise RuntimeError(record['name'])
manifest={
    'date':'2026-11-23','root':'G:/毕设','archives':{name:{'sha256':data['sha256'],'bytes':data['bytes'],'files':len(data['members'])} for name,data in plan['archives'].items()},
    'audit_records':{'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'bytes':target.stat().st_size,'members':records},
    'moves':plan['moves'],'checkpoint':plan['checkpoint'],'verification':verification,
    'compact_remove':[str(p) for p in members],
}
(audit/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print('Verified audit archive:',len(records),'records,',round(target.stat().st_size/1048576,2),'MiB')
