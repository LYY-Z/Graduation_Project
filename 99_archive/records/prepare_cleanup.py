import collections
import hashlib
import json
import re
import zipfile
from pathlib import Path

ROOT = Path('G:/毕设')
AUDIT = ROOT / '99_archive/workspace_cleanup_20261123'
inventory = json.loads((AUDIT / 'inventory.before.json').read_text(encoding='utf-8'))
files = {f['path']: f for f in inventory['files']}

moves = {}
def move(src, dst):
    if not (ROOT / src).exists():
        raise FileNotFoundError(src)
    if (ROOT / dst).exists():
        raise FileExistsError(dst)
    moves[src] = dst

move('02_learning/research_screening_2026_11_21', '02_learning/motion_control')
move('02_learning/flair_results', '02_learning/flair/results')
move('02_learning/flair_reproduction_execution.md', '02_learning/flair/reproduction_execution.md')
move('02_learning/flair_reproduction_summary.md', '02_learning/flair/reproduction_summary.md')
move('02_learning/VNC', '02_learning/platform/vnc')
move('02_learning/04_review/.build_tam/gram.pdf', '01_papers/GRAM.pdf')
move('02_learning/04_review/.build_tam/sadl.pdf', '01_papers/SADL.pdf')
supp = '03_code/50_LocoFormer_Generalist_Locom_Supplementary Material'
for name in ['LocoFormer_Appendix.pdf', 'CoRL_locoformer.mp4']:
    move(f'{supp}/{name}', f'01_papers/locoformer_supplementary/{name}')

report_root = '02_learning/04_review/deliverables'
for name in ['report.CN.pptx', 'speech.CN.docx', 'knowledge_review.CN.docx']:
    move(f'{report_root}/diffusion_policy/{name}', f'02_learning/reports/diffusion_policy/{name}')
for src, dst in [
    ('FLAIR_Paper_Review_and_Go2W_Research.CN.pptx', 'report.CN.pptx'),
    ('FLAIR_Paper_Review_and_Go2W_Research.EN.pptx', 'report.EN.pptx'),
    ('FLAIR_Presenter_Notes.CN.md', 'speech.CN.md'),
]: move(f'{report_root}/flair/{src}', f'02_learning/reports/flair/{dst}')
for src, dst in [
    ('LocoFormer_Report.CN.pptx', 'paper.CN.pptx'),
    ('LocoFormer_Report.EN.pptx', 'paper.EN.pptx'),
    ('LocoFormer_Reproduction_Plan.CN.pptx', 'reproduction.CN.pptx'),
    ('LocoFormer_Reproduction_Plan.EN.pptx', 'reproduction.EN.pptx'),
    ('speech.CN.md', 'paper.speech.CN.md'),
    ('speech.EN.md', 'paper.speech.EN.md'),
]: move(f'{report_root}/locoformer/{src}', f'02_learning/reports/locoformer/{dst}')
for src, dst in [
    ('motion_control_review.CN.pptx', 'report.CN.pptx'),
    ('motion_control_review.EN.v3.pptx', 'report.EN.pptx'),
    ('speech.CN.md', 'speech.CN.md'),
    ('speech.EN.md', 'speech.EN.md'),
]: move(f'{report_root}/motion_control/{src}', f'02_learning/reports/motion_control/{dst}')
move(f'{report_root}/ur7e/deployment_brief.CN.md', '02_learning/reports/ur7e/deployment_brief.CN.md')

legacy_code = ['03_code/diffusion_policy_ur7e_v1', '03_code/lyy_ws', '03_code/ur7e_deployment_reference']
reproducible_prefixes = [
    '03_code/lyy_ws/diffusion_policy_ur7e/.envs/',
    '03_code/lyy_ws/diffusion_policy_ur7e/.cache/',
    '03_code/ur7e_deployment_reference/preparation_tools/dependencies/',
]
reproducible_files = {
    '03_code/lyy_ws/diffusion_policy_reproduction/data/pusht.zip.partial',
    '03_code/ur7e_deployment_reference/preparation_tools/ruff.exe',
    '03_code/ur7e_deployment_reference/preparation_tools/ruff-0.8.6-py3-none-win_amd64.whl',
}
checkpoint = '03_code/diffusion_policy_ur7e/models/pusht_image_transformer.ckpt'
digest = lambda p: hashlib.file_digest(p.open('rb'), 'sha256').hexdigest() if hasattr(hashlib, 'file_digest') else hashlib.sha256(p.read_bytes()).hexdigest()
checkpoint_sha = digest(ROOT / checkpoint)
duplicate_weights = []
for prefix in legacy_code:
    for rel in files:
        if rel.startswith(prefix + '/') and rel.endswith('.ckpt'):
            if digest(ROOT / rel) != checkpoint_sha:
                raise RuntimeError('Nonduplicate checkpoint requires preservation: ' + rel)
            duplicate_weights.append(rel)

supp_zip = '03_code/50_LocoFormer_Generalist_Locom_Supplementary Material.zip'
with zipfile.ZipFile(ROOT / supp_zip) as z:
    for name in ['LocoFormer_Appendix.pdf', 'CoRL_locoformer.mp4']:
        if hashlib.sha256(z.read(name)).hexdigest() != digest(ROOT / supp / name):
            raise RuntimeError('Supplement mismatch: ' + name)

legacy_docs = [
    '02_learning/flair_reproduction_plan.md',
    '02_learning/flair_reproduction_plan_advisor.md',
    '02_learning/go2w_adaptive_control_workplan.md',
    '02_learning/go2w_research_briefing.md',
    '02_learning/go2w_research_topic.md',
]
deletes = legacy_code + legacy_docs + [
    '02_learning/04_review',
    '02_learning/locoformer/go2_reproduction/.build',
    '02_learning/locoformer/go2_reproduction/archive',
    '02_learning/locoformer/go2_reproduction/details',
    supp, supp_zip, 'money', 'NVIDIA Corporation', 'inspect.ndjson',
]
deletes += [p.name for p in ROOT.iterdir() if p.name.startswith(('.chart-data-', '.codex_presentation_validation'))]
prior_roots = [p.relative_to(ROOT).as_posix() for p in (ROOT / '99_archive').iterdir() if p.is_dir() and p != AUDIT]
prior_files = [p.relative_to(ROOT).as_posix() for p in (ROOT / '99_archive').iterdir() if p.is_file()]
deletes += prior_roots + prior_files

def within(rel, prefix):
    return rel == prefix or rel.startswith(prefix + '/')

def is_moved(rel):
    return any(within(rel, src) for src in moves)

def reproducible(rel):
    return rel in reproducible_files or any(rel.startswith(p) for p in reproducible_prefixes) or '/__pycache__/' in rel or rel.endswith(('.pyc', '.pyo'))

groups = collections.defaultdict(list)
discarded = []
for rel in files:
    if any(within(rel, p) for p in legacy_code):
        if rel in duplicate_weights:
            discarded.append((rel, 'Identical checkpoint retained in active project'))
        elif reproducible(rel):
            discarded.append((rel, 'Rebuildable copied environment, dependency/cache or incomplete download'))
        else:
            groups['legacy_code.zip'].append(rel)
    elif any(within(rel, p) for p in prior_roots + prior_files):
        groups['prior_archives.zip'].append(rel)
    elif rel.startswith('02_learning/04_review/.build') or '/go2_reproduction/.build/' in rel or rel.startswith('.chart-data-'):
        if is_moved(rel):
            continue
        name = Path(rel).name
        ext = Path(rel).suffix.lower()
        source = ext in {'.mjs','.js','.py','.json','.jsonl','.md','.txt','.yaml','.yml','.tex','.css','.html','.csv','.xlsx'}
        source_image = ext in {'.png','.jpg','.jpeg','.svg'} and not re.search(r'(?i)(slide[-_ ]?\d|page[-_ ]?\d|preview|montage|contact|thumbnail|render)', rel)
        # Keep authoring text and source illustrations, not repeated renders or draft exports.
        if source or source_image:
            groups['presentation_sources.zip'].append(rel)
        else:
            discarded.append((rel, 'Regenerable presentation render/export artifact'))
    elif rel.startswith('02_learning/04_review/') and not is_moved(rel):
        groups['legacy_documents.zip'].append(rel)
    elif any(within(rel, p) for p in legacy_docs + ['02_learning/locoformer/go2_reproduction/archive','02_learning/locoformer/go2_reproduction/details','money']):
        groups['legacy_documents.zip'].append(rel)
    elif rel.startswith('.codex_presentation_validation') or rel == 'inspect.ndjson':
        discarded.append((rel, 'Superseded presentation validation trace'))
    elif within(rel, supp) or rel == supp_zip:
        if is_moved(rel):
            continue
        discarded.append((rel, 'Verified duplicate supplement archive or macOS metadata'))

# Retain originals of editable project documentation before repairing links.
for rel in files:
    if rel.endswith('.md') and (rel.startswith('02_learning/') or rel == 'README.md' or rel.startswith('03_code/diffusion_policy_ur7e/')):
        if '/third_party/' not in rel and '/.git/' not in rel and not any(within(rel,p) for p in legacy_code):
            groups['documentation_before.zip'].append(rel)

archives = {}
covered = set()
for name, members in groups.items():
    members = sorted(set(members))
    target = AUDIT / name
    if target.exists():
        raise FileExistsError(target)
    records = []
    with zipfile.ZipFile(target, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6, allowZip64=True) as z:
        for rel in members:
            z.write(ROOT / rel, rel)
            records.append({'path':rel,'size':(ROOT/rel).stat().st_size,'sha256':digest(ROOT/rel)})
    # Deletion is forbidden until every archived member has been read back and hashed.
    with zipfile.ZipFile(target) as z:
        for record in records:
            if hashlib.sha256(z.read(record['path'])).hexdigest() != record['sha256']:
                raise RuntimeError('Archive verification failed: ' + record['path'])
    archives[name] = {'members':records,'bytes':target.stat().st_size,'sha256':digest(target)}
    covered.update(members)
    print('VERIFIED',name,len(members),round(target.stat().st_size/1048576,2),'MiB',flush=True)

discard_set = {p for p,_ in discarded}
uncovered = [rel for rel in files if any(within(rel,p) for p in deletes) and not is_moved(rel) and rel not in covered and rel not in discard_set]
if uncovered:
    raise RuntimeError('Unclassified files would be removed: '+repr(uncovered[:40]))

# Files removed from active use are mapped to a real archive, or to a retained canonical report.
aliases = {}
for rel in files:
    if rel in covered and any(within(rel,p) for p in deletes):
        name = next(n for n,v in archives.items() if any(m['path']==rel for m in v['members']))
        aliases[rel] = '99_archive/workspace_cleanup_20261123/' + name
    if rel.startswith('02_learning/04_review/') and rel.endswith('.pptx') and not is_moved(rel):
        if '/flair/' in rel:
            aliases[rel] = '02_learning/reports/flair/report.CN.pptx'
        elif '/locoformer/' in rel:
            aliases[rel] = '02_learning/reports/locoformer/reproduction.CN.pptx' if 'go2' in Path(rel).name.lower() else '02_learning/reports/locoformer/paper.CN.pptx'
        elif '/motion_control/' in rel:
            aliases[rel] = '02_learning/reports/motion_control/report.EN.pptx'
        else:
            aliases[rel] = '02_learning/reports/diffusion_policy/report.CN.pptx'

plan = {
    'root':str(ROOT),'archive_verified':True,'moves':moves,'delete_targets':deletes,
    'archives':archives,'discarded_files':[{'path':p,'reason':why,'size':files[p]['size']} for p,why in discarded],
    'aliases':aliases,'checkpoint':{'path':checkpoint,'sha256':checkpoint_sha,'deduplicated':duplicate_weights},
    'skipped_reparse':inventory['skipped_reparse'],
}
(AUDIT/'plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding='utf-8')
print('READY',len(moves),'moves;',len(deletes),'delete targets;',len(covered),'archived files; no unclassified removals')
