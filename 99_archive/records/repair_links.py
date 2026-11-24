import collections
import json
import os
import posixpath
import re
from pathlib import Path
from urllib.parse import unquote

ROOT = Path('G:/毕设')
AUDIT = ROOT / '99_archive/workspace_cleanup_20261123'
plan = json.loads((AUDIT / 'plan.json').read_text(encoding='utf-8'))
moves = plan['moves']
aliases = dict(plan['aliases'])
aliases.update({
    '02_learning/04_review/deliverables/locoformer/report.CN.pptx':'02_learning/reports/locoformer/paper.CN.pptx',
    '02_learning/04_review/deliverables/locoformer/report.EN.pptx':'02_learning/reports/locoformer/paper.EN.pptx',
    '03_code/diffusion_policy_ur7e_refactored':'03_code/diffusion_policy_ur7e',
})
old_dirs_to_archive = {
    '03_code/diffusion_policy_ur7e_v1':'legacy_code.zip',
    '03_code/lyy_ws':'legacy_code.zip',
    '03_code/ur7e_deployment_reference':'legacy_code.zip',
    '02_learning/locoformer/go2_reproduction/archive':'legacy_documents.zip',
    '02_learning/locoformer/go2_reproduction/details':'legacy_documents.zip',
    '02_learning/04_review/.build':'presentation_sources.zip',
    '99_archive/ur7e_refactor_legacy_20261026':'prior_archives.zip',
    '99_archive/review_cleanup':'prior_archives.zip',
    '99_archive/documentation_updates':'prior_archives.zip',
    '99_archive/learning':'prior_archives.zip',
    '99_archive/planning_records':'prior_archives.zip',
}

def relocate(rel):
    if rel in aliases:
        return aliases[rel]
    for src,dst in sorted(moves.items(),key=lambda kv:-len(kv[0])):
        if rel == src or rel.startswith(src+'/'):
            return dst+rel[len(src):]
    for src,name in sorted(old_dirs_to_archive.items(),key=lambda kv:-len(kv[0])):
        if rel == src or rel.startswith(src+'/'):
            return '99_archive/workspace_cleanup_20261123/'+name
    return rel

def original_location(current):
    for src,dst in sorted(moves.items(),key=lambda kv:-len(kv[1])):
        if current == dst or current.startswith(dst+'/'):
            return src+current[len(dst):]
    return current

documents=[]
for p in (ROOT/'02_learning').rglob('*.md'):documents.append(p)
documents.append(ROOT/'README.md')
for p in (ROOT/'03_code/diffusion_policy_ur7e').rglob('*.md'):
    if '/third_party/' not in p.as_posix():documents.append(p)
documents.extend([ROOT/'03_code/references/README.md'])
byname=collections.defaultdict(list)
for p in ROOT.rglob('*'):
    if p.is_file() and not p.is_symlink():byname[p.name.casefold()].append(p.relative_to(ROOT).as_posix())

pattern=re.compile(r'(!?\[[^\]\n]*\]\()(<[^>\n]+>|[^\)\s]+)(\))')
changes=[]
for doc in documents:
    current=doc.relative_to(ROOT).as_posix()
    old=original_location(current)
    text=doc.read_text(encoding='utf-8-sig',errors='replace')
    count=[0]
    def replace(m):
        raw=m.group(2);target=unquote(raw.strip('<>'))
        if target.startswith(('#','http:','https:','mailto:','plugin:','app:','artifact:','data:')):return m.group(0)
        if re.match(r'^[A-Za-z]:',target):
            if not target.lower().replace('\\','/').startswith('g:/毕设/'):return m.group(0)
            target=target.replace('\\','/')[len('G:/毕设/'):]
            resolved=target
        elif target.startswith('/'):
            return m.group(0)
        else:
            resolved=posixpath.normpath(posixpath.join(posixpath.dirname(old),target.replace('\\','/')))
        base,sep,fragment=resolved.partition('#')
        line=''
        lm=re.search(r':\d+$',base)
        if lm:line=lm.group(0);base=base[:-len(line)]
        moved=relocate(base)
        if not (ROOT/moved).exists():
            candidates=[x for x in byname.get(posixpath.basename(base).casefold(),[]) if not x.startswith('99_archive/')]
            if len(candidates)==1:moved=candidates[0]
        if not (ROOT/moved).exists():return m.group(0)
        if moved.endswith('.zip'):line='';fragment='';sep=''
        updated=posixpath.relpath(moved,posixpath.dirname(current) or '.')+line+(sep+fragment if sep else '')
        if ' ' in updated:updated='<'+updated+'>'
        result=m.group(1)+updated+m.group(3)
        if result!=m.group(0):count[0]+=1
        return result
    updated=pattern.sub(replace,text)
    # Refresh literal workspace locations while preserving historical filenames in prose.
    literals={
        '02_learning/04_review/deliverables/':'02_learning/reports/',
        '02_learning\\04_review\\deliverables\\':'02_learning\\reports\\',
        '02_learning/research_screening_2026_11_21/':'02_learning/motion_control/',
        '02_learning\\research_screening_2026_11_21\\':'02_learning\\motion_control\\',
        '02_learning/flair_results/':'02_learning/flair/results/',
        '02_learning\\flair_results\\':'02_learning\\flair\\results\\',
        '02_learning/VNC/':'02_learning/platform/vnc/',
        '02_learning\\VNC\\':'02_learning\\platform\\vnc\\',
    }
    for src,dst in literals.items():updated=updated.replace(src,dst)
    if updated!=text:
        doc.write_text(updated,encoding='utf-8')
        changes.append({'file':current,'repaired_links':count[0]})
(AUDIT/'link_changes.json').write_text(json.dumps(changes,ensure_ascii=False,indent=2),encoding='utf-8')
print('UPDATED',len(changes),'documents;',sum(x['repaired_links'] for x in changes),'links')

broken=[]
for doc in documents:
    for m in pattern.finditer(doc.read_text(encoding='utf-8',errors='replace')):
        target=unquote(m.group(2).strip('<>'))
        if target.startswith(('#','http:','https:','mailto:','plugin:','app:','artifact:','data:','/')) or re.match(r'^[A-Za-z]:',target):continue
        target=re.sub(r':\d+$','',target.split('#')[0])
        candidate=doc.parent/target
        if not candidate.exists():broken.append({'document':doc.relative_to(ROOT).as_posix(),'target':target})
(AUDIT/'broken_links.json').write_text(json.dumps(broken,ensure_ascii=False,indent=2),encoding='utf-8')
print('UNRESOLVED',len(broken))
for item in broken[:30]:print(json.dumps(item,ensure_ascii=True))
