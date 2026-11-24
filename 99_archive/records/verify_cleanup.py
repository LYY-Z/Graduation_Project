import hashlib
import json
import os
import re
import zipfile
from pathlib import Path
from urllib.parse import unquote
import xml.etree.ElementTree as ET

ROOT=Path('G:/毕设');AUDIT=ROOT/'99_archive/workspace_cleanup_20261123'
before=json.loads((AUDIT/'inventory.before.json').read_text(encoding='utf-8'))
plan=json.loads((AUDIT/'plan.json').read_text(encoding='utf-8'))
protected=['03_code/diffusion_policy_ur7e/','03_code/diffusion_policy/','03_code/locoformer/','03_code/references/']
issues=[];protected_count=0
for f in before['files']:
    rel=f['path']
    if any(rel.startswith(p) for p in protected) and not rel.endswith('.md'):
        p=ROOT/rel;protected_count+=1
        if not p.is_file():issues.append({'missing_protected':rel})
        elif p.stat().st_size!=f['size'] or abs(p.stat().st_mtime-f['mtime'])>0.01:issues.append({'changed_protected':rel})
ck=ROOT/plan['checkpoint']['path']
h=hashlib.sha256()
with ck.open('rb') as stream:
    for b in iter(lambda:stream.read(8*1024*1024),b''):h.update(b)
if h.hexdigest()!=plan['checkpoint']['sha256']:issues.append({'checkpoint':'hash mismatch'})

pattern=re.compile(r'(!?\[[^\]\n]*\]\()(<[^>\n]+>|[^\)\s]+)(\))')
docs=[ROOT/'README.md',ROOT/'03_code/README.md',ROOT/'03_code/references/README.md',ROOT/'99_archive/README.md']
docs+=list((ROOT/'02_learning').rglob('*.md'))
docs+=[p for p in (ROOT/'03_code/diffusion_policy_ur7e').rglob('*.md') if '/third_party/' not in p.as_posix()]
for doc in docs:
    for m in pattern.finditer(doc.read_text(encoding='utf-8-sig',errors='replace')):
        target=unquote(m.group(2).strip('<>'))
        if target.startswith(('#','http:','https:','mailto:','plugin:','app:','artifact:','data:','/')) or re.match(r'^[A-Za-z]:',target):continue
        target=re.sub(r':\d+$','',target.split('#')[0])
        if target.endswith('workspace_cleanup_20261123/cleanup_report.md'):continue
        if not (doc.parent/target).exists():issues.append({'broken_link':doc.relative_to(ROOT).as_posix(),'target':target})

ns={'a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
presentations=[]
for p in sorted((ROOT/'02_learning/reports').rglob('*.pptx')):
    with zipfile.ZipFile(p) as z:
        bad=z.testzip()
        if bad:issues.append({'pptx_crc':str(p),'entry':bad})
        slides=[n for n in z.namelist() if re.match(r'ppt/slides/slide\d+\.xml$',n)]
        notes=[n for n in z.namelist() if re.match(r'ppt/notesSlides/notesSlide\d+\.xml$',n)]
        presentations.append({'path':p.relative_to(ROOT).as_posix(),'slides':len(slides),'notes':len(notes)})
        if '/motion_control/' in p.as_posix() and (len(slides)!=13 or len(notes)!=13):issues.append({'motion_control_pages':str(p)})

original_bytes=sum(f['size'] for f in before['files'])
current_bytes=0;current_count=0
for folder,children,names in os.walk(ROOT,followlinks=False):
    for name in names:
        p=Path(folder)/name
        try:current_bytes+=p.stat().st_size;current_count+=1
        except OSError:pass
result={'protected_files_checked':protected_count,'checkpoint_sha256':h.hexdigest(),'markdown_files_checked':len(docs),'issues':issues,'presentations':presentations,'before':{'bytes':original_bytes,'files':len(before['files'])},'interim_after':{'bytes':current_bytes,'files':current_count}}
(AUDIT/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=True))
if issues:raise SystemExit(1)
