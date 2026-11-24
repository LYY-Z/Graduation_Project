"""Workspace-only material organization; filesystem moves use the paired PowerShell step."""
from pathlib import Path
import hashlib
import json
import os
import re
import sys
import urllib.parse
import zipfile

ROOT = Path(__file__).resolve().parents[2]
RECORDS = ROOT / '99_archive/records'
PLAN = RECORDS / 'organization.json'
PREFIX = 'organization_20261123/'


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for part in iter(lambda: f.read(1024 * 1024), b''):
            h.update(part)
    return h.hexdigest()


def owned_docs():
    result = [ROOT / 'README.md', ROOT / '03_code/README.md',
              ROOT / '03_code/references/README.md', ROOT / '99_archive/README.md']
    result += list((ROOT / '02_learning').rglob('*.md'))
    project = ROOT / '03_code/diffusion_policy_ur7e'
    result += list(project.glob('*.md')) + list((project / 'docs').rglob('*.md'))
    return sorted(set(p for p in result if p.is_file()))


def prepare():
    if PLAN.exists():
        raise RuntimeError('Preparation already exists; inspect it instead of duplicating the archive.')
    moves = {}
    def move(old, new):
        assert (ROOT / old).is_file(), old
        assert not (ROOT / new).exists(), new
        moves[old] = new
    papers = {
        'chi-et-al-2024-diffusion-policy-visuomotor-policy-learning-via-action-diffusion.pdf': 'diffusion_policy/paper.pdf',
        'LocoFormer.pdf': 'locoformer/paper.pdf',
        'locoformer_supplementary/LocoFormer_Appendix.pdf': 'locoformer/supplementary.pdf',
        'locoformer_supplementary/CoRL_locoformer.mp4': 'locoformer/video.mp4',
        'FLAIR.pdf': 'flair/paper.pdf', 'FLAIR_supplementary.pdf': 'flair/supplementary.pdf',
        'GRAM.pdf': 'research/GRAM.pdf', 'TAM.pdf': 'research/TAM.pdf', 'SADL.pdf': 'research/SADL.pdf',
        'TAM_references/ASID_Active_System_Identification.pdf': 'research/ASID.pdf',
        'TAM_references/RMA_Rapid_Motor_Adaptation.pdf': 'research/RMA.pdf',
        'main.tex': 'manipulator_report/main.tex',
        'Technical_Report_Manipulator (2).pdf': 'manipulator_report/report.pdf',
    }
    for old, new in papers.items():
        move('01_papers/' + old, '01_papers/' + new)
    base = '02_learning/locoformer/go2_reproduction/'
    move(base + '01_go2w_hardware.CN.md', '02_learning/platform/go2w.CN.md')
    for old, new in [('02_reference_projects.CN.md', 'references.CN.md'),
                     ('03_core_implementation.CN.md', 'interfaces.CN.md'),
                     ('04_reproduction_workplan.CN.md', 'workplan.CN.md')]:
        move(base + old, '02_learning/locoformer/reproduction/' + new)
    for p in (ROOT / (base + 'assets')).iterdir():
        if p.is_file():
            dest = '02_learning/platform/assets/' if p.name.startswith('go2w_') else '02_learning/locoformer/assets/'
            move(p.relative_to(ROOT).as_posix(), dest + p.name)
    move('02_learning/research/reviews/hardware_interface_audit.md', '02_learning/platform/interfaces.CN.md')
    for p in (ROOT / '02_learning/diffusion_policy/06_refactored_code').rglob('*'):
        if p.is_file():
            old = p.relative_to(ROOT).as_posix()
            move(old, old.replace('/06_refactored_code/', '/05_code_and_deployment/'))
    for p in (ROOT / '02_learning/flair/results').iterdir():
        if p.is_file():
            folder = 'data' if p.suffix == '.csv' else 'figures' if p.suffix == '.png' else 'provenance'
            move(p.relative_to(ROOT).as_posix(), '02_learning/flair/results/' + folder + '/' + p.name)
    superseded = [
        '02_learning/diffusion_policy/00_learning_map.md',
        '02_learning/flair/reproduction_execution.md',
        '02_learning/flair/reproduction_summary.md',
        '02_learning/research/briefing.CN.md',
        '02_learning/research/reviews/additional_review.CN.md',
        base + 'README.md', base + 'LocoFormer_Go2W_reproduction_briefing.md',
    ]
    superseded += [p.relative_to(ROOT).as_posix() for p in (ROOT / '02_learning/diffusion_policy/05_deployment').rglob('*') if p.is_file()]
    aliases = {p: '99_archive/history.zip' for p in superseded}
    aliases['02_learning/diffusion_policy/00_learning_map.md'] = '02_learning/diffusion_policy/README.md'
    for name in ['reproduction_execution.md', 'reproduction_summary.md']:
        aliases['02_learning/flair/' + name] = '02_learning/flair/reproduction.CN.md'
    for name in ['README.md', 'LocoFormer_Go2W_reproduction_briefing.md']:
        aliases[base + name] = '02_learning/locoformer/reproduction/README.md'
    aliases['02_learning/research/briefing.CN.md'] = '02_learning/research/review.CN.md'
    aliases['02_learning/research/reviews/additional_review.CN.md'] = '02_learning/research/review.CN.md'
    for p in superseded:
        if '/05_deployment/' in p and p.endswith('.md') and not p.endswith(('05_code_organization_plan.md', 'technical_report_insert.md')):
            aliases[p] = '02_learning/diffusion_policy/deployment_record.CN.md'
    snapshot = sorted(set(p.relative_to(ROOT).as_posix() for p in owned_docs()) | set(superseded))
    archive_entries = []
    archive = ROOT / '99_archive/history.zip'
    with zipfile.ZipFile(archive, 'a', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        if any(n.startswith(PREFIX) for n in z.namelist()):
            raise RuntimeError('Archive prefix exists; do not duplicate.')
        for name in snapshot:
            raw = (ROOT / name).read_bytes()
            z.writestr(PREFIX + name, raw)
            archive_entries.append({'path': name, 'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)})
        z.writestr(PREFIX + 'entries.json', json.dumps(archive_entries, ensure_ascii=False, indent=2))
    with zipfile.ZipFile(archive) as z:
        for item in archive_entries:
            assert hashlib.sha256(z.read(PREFIX + item['path'])).hexdigest() == item['sha256']
    protected = {}
    for p in (ROOT / '03_code').rglob('*'):
        if p.is_file() and p.suffix.lower() != '.md':
            protected[p.relative_to(ROOT).as_posix()] = digest(p)
    presentations = {p.relative_to(ROOT).as_posix(): digest(p) for p in (ROOT / '02_learning/reports').rglob('*') if p.is_file()}
    move_hashes = {old: digest(ROOT / old) for old in moves}
    plan = {'root': str(ROOT), 'archive_prefix': PREFIX, 'archive_entries': archive_entries,
            'moves': moves, 'move_hashes': move_hashes, 'superseded': superseded, 'aliases': aliases,
            'document_origins': [p.relative_to(ROOT).as_posix() for p in owned_docs()],
            'protected': protected, 'presentations': presentations, 'status': 'prepared'}
    PLAN.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'moves': len(moves), 'superseded': len(superseded), 'archived_files': len(archive_entries), 'protected_files': len(protected)}, ensure_ascii=False))


def original(name):
    with zipfile.ZipFile(ROOT / '99_archive/history.zip') as z:
        return z.read(PREFIX + name).decode('utf-8-sig').replace('\r\n', '\n').replace('\r', '\n')


def write(name, text):
    p = ROOT / name
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('w', encoding='utf-8', newline='\n') as f:
        f.write(text.strip() + '\n')


LINK = re.compile(r'(!?\[[^\]\n]*\]\()(<[^>\n]+>|[^\)\s]+)(\))')


def repair_links(plan):
    mapping = {**plan['moves'], **plan['aliases']}
    inverse = {new: old for old, new in plan['moves'].items()}
    count = 0
    for p in owned_docs():
        dest = p.relative_to(ROOT).as_posix()
        origin = ROOT / inverse.get(dest, dest)
        text = p.read_text(encoding='utf-8-sig')
        def replace(match):
            nonlocal count
            token = match[2]
            target = token.strip('<>')
            if re.match(r'^(?:[a-zA-Z][\w+.-]*:|#|//)', target) and not re.match(r'^[gG]:[/\\]', target):
                return match[0]
            raw_path, sep, frag = target.partition('#')
            raw_path = urllib.parse.unquote(raw_path)
            line = ''
            line_match = re.search(r':(\d+)$', raw_path)
            if line_match:
                line = line_match[0]
                raw_path = raw_path[:line_match.start()]
            if not raw_path:
                return match[0]
            old_path = Path(os.path.abspath(str(origin.parent / raw_path)))
            try:
                old = old_path.relative_to(ROOT).as_posix()
            except ValueError:
                return match[0]
            new = mapping.get(old, old)
            # Unmapped relative links still need rebasing when their containing document moved.
            if new == old and origin == p:
                return match[0]
            if new.endswith('.zip'):
                line, sep, frag = '', '', ''
            fixed = os.path.relpath(ROOT / new, p.parent).replace('\\', '/') + line + (sep + frag if sep else '')
            if ' ' in fixed:
                fixed = '<' + fixed + '>'
            count += 1
            return match[1] + fixed + match[3]
        changed = LINK.sub(replace, text)
        # Non-link inline paths are documentation references, not executable source.
        for old_dir, new_dir in [
            ('06_refactored_code', '05_code_and_deployment'),
            ('go2_reproduction/02_reference_projects.CN.md', 'reproduction/references.CN.md'),
            ('go2_reproduction/03_core_implementation.CN.md', 'reproduction/interfaces.CN.md'),
            ('go2_reproduction/04_reproduction_workplan.CN.md', 'reproduction/workplan.CN.md')]:
            changed = changed.replace(old_dir, new_dir)
        if changed != text:
            p.write_text(changed, encoding='utf-8')
    return count


def documents():
    plan = json.loads(PLAN.read_text(encoding='utf-8'))
    if plan['status'] != 'prepared':
        raise RuntimeError('Document rebasing is a one-time operation; verify the completed state instead.')
    # Rebase original documents first; newly authored documents use final paths directly.
    count = repair_links(plan)
    write('01_papers/README.md', '''
# 论文与原始资料

按研究主题保存正文及配套材料。已学习论文与正在调研的论文分组存放；目录分组不代表最终选题或论文优先级。

| 主题 | 正文与配套材料 | 学习或研究入口 |
|---|---|---|
| Diffusion Policy | [正文](diffusion_policy/paper.pdf) | [学习手册](../02_learning/diffusion_policy/README.md) |
| LocoFormer | [正文](locoformer/paper.pdf) · [附录](locoformer/supplementary.pdf) · [视频](locoformer/video.mp4) | [学习手册](../02_learning/locoformer/README.md) |
| FLAIR | [正文](flair/paper.pdf) · [补充材料](flair/supplementary.pdf) | [源码与复现](../02_learning/flair/README.md) |
| 当前调研 | [TAM](research/TAM.pdf) · [GRAM](research/GRAM.pdf) · [SADL](research/SADL.pdf) | [阶段比较](../02_learning/research/review.CN.md) |
| 适应方法参考 | [ASID：Active System Identification](research/ASID.pdf) · [RMA：Rapid Motor Adaptation](research/RMA.pdf) | [详细调研](../02_learning/research/README.md) |
| 机械臂技术报告 | [报告 PDF](manipulator_report/report.pdf) · [LaTeX 主文件](manipulator_report/main.tex) | [部署代码](../03_code/diffusion_policy_ur7e/README.CN.md) |

`manipulator_report/` 保存收到的报告与主文件。主文件引用的 `figures/` 和 `section/references` 未随材料提供；当前目录不是完整可编译的 LaTeX 工程。

原始 PDF、视频和 LaTeX 内容保持不变；译读、讲解、调研结论及汇报均放在 [02_learning](../02_learning/README.md)。
''')
    old_readme = original('02_learning/diffusion_policy/README.md')
    old_map = original('02_learning/diffusion_policy/00_learning_map.md')
    intro = '''# DDPM 与 Diffusion Policy 学习手册

这套资料按“基础 → 论文 → 官方源码 → 部署代码 → 复习”组织。首次学习按下表顺序阅读；复习时用疑问索引定位，不必重读全部章节。

| 顺序 | 内容 | 入口 |
|---|---|---|
| 1 | 机器学习、DDPM、机器人控制与 RL 背景 | [机器学习与模仿学习](01_foundations/01_ml_dl_and_imitation.md) · [DDPM 完整推导](01_foundations/02_ddpm_from_intuition_to_formula.md) · [控制与 RL](01_foundations/03_robot_control_and_rl.md) |
| 2 | 问题、建模、方法、网络、实验与局限 | [中文阅读](02_paper_study/00_paper_chinese_reading.md) · [问题与流程](02_paper_study/01_problem_and_full_pipeline.md) · [公式](02_paper_study/02_action_diffusion_and_formulas.md) · [网络与控制](02_paper_study/03_control_network_and_design.md) · [实验](02_paper_study/04_experiments_appendix_limits.md) |
| 3 | 官方仓库、配置、训练与评估 | [论文到源码](03_code_and_practice/01_paper_to_official_code.md) · [13 节代码教材](03_code_and_practice/code_study/README.md) · [最小复现](03_code_and_practice/02_minimal_reproduction_and_debug.md) |
| 4 | UR7e 硬件输入、checkpoint、推理与受限执行 | [六章部署代码教材](05_code_and_deployment/README.md) · [已完成部署记录](deployment_record.CN.md) |
| 5 | 查公式、回顾疑问和准备汇报 | [公式卡](04_review/01_symbols_and_formula_cards.md) · [疑问索引](04_review/02_faq_and_question_index.md) · [复述与自测](04_review/03_paper_recap_and_self_test.md) |

## 学习目标与复习路线
'''
    # Preserve the unique conceptual study guidance rather than just deleting its navigation file.
    map_body = old_map.split('## 学完这篇论文的终点', 1)[1]
    map_body = map_body.replace('## 路线 A：首次学习', '### 按顺序建立理解')
    map_body = map_body.replace('## 路线 B：公式复习', '### 公式复习').replace('## 路线 C：答辩复习', '### 汇报复习')
    # The later code routes repeat the table above; keep only their unique learning distinctions.
    map_body = map_body.split('## 路线 D：代码实践')[0]
    map_body = map_body.replace('## ', '### ').replace('#### ', '### ')
    write('02_learning/diffusion_policy/README.md', intro + map_body + '''

## 代码与验证资料

当前工程为 [diffusion_policy_ur7e](../../03_code/diffusion_policy_ur7e/README.CN.md)；原论文实现为 [diffusion_policy](../../03_code/diffusion_policy/README.md)。原始部署证据保存在 [code.zip](../../99_archive/code.zip)，整理后的事实与指标见[部署记录](deployment_record.CN.md)。旧部署六章、早期组织计划、清单与报告插入稿已收录 [history.zip](../../99_archive/history.zip) 的 `organization_20261123/`，现行代码学习统一使用 `05_code_and_deployment/`。

训练噪声 MSE 降低不等于闭环任务成功。原工程的实机记录与后续重构的离线检查分别解释，操作以当前项目 README 和 Guide 为准。

继续：[LocoFormer](../locoformer/README.md) · [学习总入口](../README.md) · [汇报资料](../reports/README.md)。
''')
    write('02_learning/diffusion_policy/deployment_record.CN.md', '''
# UR7e Diffusion Policy 部署记录

本记录集中说明已完成的部署链路、实现来源和实测依据。逐步代码讲解见[六章教材](05_code_and_deployment/README.md)，当前配置与启动方法见[项目 README](../../03_code/diffusion_policy_ur7e/README.CN.md)和 [Guide](../../03_code/diffusion_policy_ur7e/docs/guide.CN.md)。

## 1. 已完成的链路

```mermaid
flowchart LR
    C[腕部 RGB 相机] --> B[ROS 图像桥接与帧文件]
    R[UR7e RTDE 状态] --> O[两帧因果观测窗口]
    B --> O
    O --> P[公开 Push-T 策略与 EMA 权重]
    P --> A[二维动作序列]
    A --> G[坐标映射、平滑与限幅]
    G --> M[受限 moveL]
    M --> U[UR7e 实际运动]
    U --> F[控制柜位姿与关节反馈]
    F --> O
```

这是“采集 → 推理 → 执行一条小目标 → 再采集”的链路短测，尚不能视为真实 Push-T 任务复现或连续高频策略控制。夹爪未接入动作执行。

## 2. 原始实现与新增适配

| 部分 | 来源与处理 |
|---|---|
| 模型与策略 | 原 Diffusion Policy 实现，固定提交 `5ba07ac6661db573af695b419a7947ecb704690f`；使用已训练的仿真 Push-T 图像 Transformer checkpoint，没有重新训练 |
| 图像输入 | 单路腕部 RGB，经桥接、中心裁剪和缩放；每次构造两帧观测。不是论文实机的双相机设置 |
| 状态输入 | RTDE 读取 TCP 与关节反馈；TCP 平面位置映射到模型的 `agent_pos`，模型输入并非六关节角 |
| 推理 | EMA 参数，100 次 DDPM 去噪；计划长度 10，接口返回 8 步动作，受限执行取当前首条 |
| 输出适配 | 将二维输出映射为机器人平面目标；高度和姿态固定，再平滑、限制位移及累计预算 |
| 控制扩展 | 基于 ur_rtde 1.6.5 副本修改并独立编译，原版代码与补丁依据保留在归档中 |
| 当前工程 | `hardware`、`inference`、`control` 等模块化组织及操作方式以当前项目为准；重构的离线检查不替代实机复验 |

模型输入为 `image [1,2,3,96,96]` 和 `agent_pos [1,2,2]`。checkpoint 的 SHA-256 为：

```text
d68cdbcf9c21df724fb60f2573aa28a22a333f555225a2ec29cb6b7890608c56
```

## 3. 实机短测与数值

运行编号 `20261025T085457Z_live`。限制为单步 1 mm、累计命令距离 3 mm、起始位置周围半径 3 mm、命令速度 2 mm/s，最多 3 条目标。曾讨论的更大幅度方案已取消，不能作为本次设置。

| 指标 | 第 1 条 | 第 2 条 | 第 3 条 |
|---|---:|---:|---:|
| 命令距离（mm） | 0.5004 | 0.7740 | 0.8446 |
| 实测起止位移（mm） | 0.4950 | 0.7510 | 0.8314 |
| 到目标的位置误差（mm） | 0.0139 | 0.0250 | 0.0178 |
| 模型调用耗时（s） | 0.6024 | 0.6008 | 0.6025 |

累计命令距离约 **2.1190 mm**；第一条之前至末条之后的净实测位移约 **2.0223 mm**。两者定义不同，也不等于完整反馈轨迹的弧长。三条目标具有 ACK 与完成记录，共保存 **132 条反馈**。3/3 是同一次短测中的目标到位数，不是三个独立任务的成功率。

## 4. 证据与结论范围

原始代码和运行日志见 [code.zip](../../99_archive/code.zip)，包括对应运行的 `trial_result.json`、`metadata.json`、`events.jsonl` 和 `observations/`。其中记录输入帧、TCP/关节状态、模型版本、预测结果、目标、ACK 与运动反馈。此前失败运行也保留；不存在外部运动视频证据。

| 可以支持的结论 | 尚不能支持的结论 |
|---|---|
| 真实图像与状态进入公开模型，推理输出经过适配后驱动了真实末端，并得到反馈确认 | 真实 Push-T 成功率、可靠 sim-to-real 泛化或新策略算法贡献 |
| 小幅、固定高度与姿态的受限执行链路已验证 | 六自由度策略动作、夹爪控制、长期连续稳定运行 |
| 原工程有实机证据，重构工程有独立的离线验证材料 | 将旧实机结果直接算作重构工程的新实机验收 |

视觉和机器人状态采用主机时间上的因果配对，不是硬件同步；约 0.60 s 为模型调用耗时，不是全链路延迟。软件限幅不等于完整碰撞安全机制。

## 5. 资料分工

- 学习实现：[当前部署教材](05_code_and_deployment/README.md)。
- 操作和配置：[项目文档](../../03_code/diffusion_policy_ur7e/README.CN.md)。
- 原始机械臂报告：[PDF 与 LaTeX](../../01_papers/README.md)。
- 旧部署六章、早期目录方案、原始证据快照与报告插入稿：[history.zip](../../99_archive/history.zip)，内部路径 `organization_20261123/02_learning/diffusion_policy/05_deployment/`。

后续任务级实验需要独立定义场景、标定、成功标准、重复次数与统计口径，不能由本次链路短测推导。
''')
    flair = original('02_learning/flair/reproduction_execution.md')
    # This record already contains every result table from the former summary.
    flair = flair.replace('# FLAIR 六足仿真复现执行记录', '# FLAIR 六足仿真复现：范围、执行与结果', 1)
    flair = flair.replace('| 运行步骤与老师汇报 | [原执行计划](../../99_archive/history.zip)、[工作总结](reproduction_summary.md) |',
                          '| 汇报材料 | [汇报 PPT](../reports/flair/report.CN.pptx) · [逐页讲稿](../reports/flair/speech.CN.md) |')
    last = flair.index('Go2-W 迁移以车体前进速度')
    flair = flair[:last] + '''### 指标与后续研究的边界

本批次减力组总跟踪误差降幅约 13.0%；作者数据复算的 138.773% 则以健康/减力条件之间的额外误差为分母。两者不是同一指标，具体计算见[指标教材](03_reproduction_and_metrics.md)。论文的 GVR-Bot 实机比较也不能由六足结果代替。

六足 Chicane 主对照是已经完成的复现范围；Go2-W 迁移、其他六足故障和整篇论文全部实验不在本次完成结论之内。此前迁移设想保存在归档中，当前选题与研究方向以[研究交接](../00_research_handoff.CN.md)为准。

旧执行文档与旧总结已合并到本记录；完整原稿保留在 [history.zip](../../99_archive/history.zip) 的 `organization_20261123/02_learning/flair/`。
'''
    for old, new in plan['moves'].items():
        if old.startswith('02_learning/flair/results/'):
            flair = flair.replace(old.split('02_learning/flair/')[1], new.split('02_learning/flair/')[1])
    write('02_learning/flair/reproduction.CN.md', flair)
    p = ROOT / '02_learning/flair/README.md'
    t = p.read_text(encoding='utf-8').replace('；六足结果见[复现总结](reproduction.CN.md)。', '。六足执行步骤与结果统一见[复现记录](reproduction.CN.md)。')
    t = t.replace('[复现执行记录](reproduction.CN.md)', '[复现记录](reproduction.CN.md)')
    write(p.relative_to(ROOT).as_posix(), t)
    write('02_learning/platform/README.md', '''
# 实验平台资料

平台说明独立于具体论文维护，供调研、任务设计和后续部署共同引用。

| 内容 | 入口 |
|---|---|
| Go2-W 机械结构、电机、关节槽位、传感器及 SDK | [Go2-W 硬件手册](go2w.CN.md) |
| Go2-W 与 UR7e 的观察、控制接口及迁移约束 | [输入输出接口审查](interfaces.CN.md) |
| 服务器图形连接 | [VNC](vnc.md) |

`assets/` 保存 Go2-W 原始图片与关节示意图。硬件说明中的公开参数与当前设备的实测配置需要区分；接口审查不代表已经完成相应方法的实机验证。
''')
    write('02_learning/locoformer/reproduction/README.md', '''
# LocoFormer 复现规划与实现审查

这是 LocoFormer 方向形成的阶段性方案，不是已完成复现或当前最终选题。论文学习见[学习手册](../README.md)，共享平台事实见[Go2-W 硬件](../../platform/go2w.CN.md)与[接口审查](../../platform/interfaces.CN.md)。

| 顺序 | 文档 | 用途 |
|---|---|---|
| 1 | [参考项目](references.CN.md) | 第三方 LocoFormer、BabyLocoFormer 及其他项目实现了什么、能复用什么、缺少什么 |
| 2 | [统一接口与核心实现](interfaces.CN.md) | 三种输入统一方式、关节槽位、输出映射、策略与跨 Trial 记忆 |
| 3 | [复现工作计划](workplan.CN.md) | 原方向的阶段步骤、条件、交付和验收 |

原汇报概览与旧索引已收敛到本页；细节分别保留在三份文档中。[复现汇报 PPT](../../reports/locoformer/reproduction.CN.pptx)是对应阶段的汇报材料。原稿保存在 [history.zip](../../../99_archive/history.zip) 的 `organization_20261123/02_learning/locoformer/go2_reproduction/`。

作者原始发布的缺失和第三方实现的适用范围均是当时的审查结果，后续可根据新发布重评。当前开放调研要求见[研究交接](../../00_research_handoff.CN.md)。
''')
    research = (ROOT / '02_learning/research/review.CN.md').read_text(encoding='utf-8')
    research = research.replace('# Go2-W 与 UR7e 扰动恢复：论文选型比较报告', '# Go2-W 与 UR7e 运动控制：阶段文献比较')
    start = research.index('**筛选条件更新：')
    end = research.index('## 2. 三个候选分别解决什么')
    research = research[:start] + '''## 1. 这份比较如何使用

以下材料是截至 2026-11-22 的阶段性调查，按历史策略、通用连续控制与在线动力学三类比较。TAM、GRAM、SADL 等均为当前样本，可继续增加、替换和推翻原有排序；不限定强化学习，不预设最终共享一套权重或分别训练。

现有证据尚不足以确认一篇同时满足“官方完整发布、多类运行中扰动、Go2-W 与独立机械臂直接支持、迁移成本低”的方法。这不等于全网不存在，也不应成为停止调研的理由。评估时应分别判断原任务可运行、论文结果可对齐和目标硬件可部署，不能相互替代。

下文保留各方法的证据和代价，作为继续比较的起点；GPU 兼容性、部署可用观测与控制接口要独立审查。

''' + research[end:]
    research = research.replace('### 2.3 Situationally-Aware Dynamics Learning：变化检测和在线模型适应', '### 2.3 Situationally-Aware Dynamics Learning：工况识别与条件动力学')
    research = research.replace('**方法。** 在线变化检测、工况表示与条件概率动力学模型，再用 MPPI 规划控制。它是模型驱动适应控制，不能仅因涉及学习就称为 PPO 类强化学习。',
        '**方法。** 训练阶段建立不同工况的动力学表示与条件模型；测试阶段依据近期转移识别匹配工况，并用 MPPI 规划。应区分测试时工况匹配与重新更新模型参数，不宜笼统称为每步在线学习权重。它属于模型驱动控制，不是 PPO 类策略强化学习。')
    research = research.replace('## 5. 两个平台的输入输出怎样落地\n\n建议先避免更困难的“同一权重跨任意机器人”，采用如下共同算法、独立合同：',
        '## 5. 两个平台的输入输出怎样落地\n\n下表说明分别建立平台合同的一种路线；是否进一步共享编码器或权重，需由具体论文及研究问题决定：')
    research = research.replace('## 6. 适合课题讨论的研究问题', '## 6. 可继续讨论的研究问题')
    research = research.replace('现阶段最值得讨论的不是堆叠模块，而是下面这个可具体对照的问题：', '以下是由现有材料归纳的一项可对照问题，不排除其他更有价值的方向：')
    research = research.replace('本科阶段的可控范围应是：**一个主方法、一项明确机制修改、两个平台的有限代表任务和扰动组合**，而不是统一所有机器人、所有任务及所有故障。',
        '工作量需要与本科阶段的资源匹配：优先把研究问题、对照和方法贡献做清楚，再决定模块数量和实验范围，不以跨平台数量代替创新。')
    # Merge the unique supplementary audit into the main comparison.
    extra = original('02_learning/research/reviews/additional_review.CN.md')
    sections = []
    for heading in ['## 1. GRAM', '## 2. ReLCE', '## 3. DOMINO', '## 4. 新近直接相关工作']:
        a = extra.index(heading)
        b = extra.find('\n## ', a + 1)
        section = extra[a:b if b != -1 else len(extra)]
        section = re.sub(r'^## \d+\. ', '### ', section, count=1)
        section = section.replace('\n### 方法与复现材料', '\n#### 方法与复现材料').replace('\n### 扰动时序的明确边界', '\n#### 扰动时序的明确边界').replace('\n### 两平台的适用性', '\n#### 两平台的适用性')
        section = section.replace('本次未核实', '该轮未核实').replace('暂不取代主候选', '作为继续比较的样本')
        sections.append(section.strip())
    insertion = '## 8. 补充候选与复现成本\n\n本节合并原补充审查中的版本条件及相关工作，不另设重复综述。以下定位为原审查时的判断。\n\n' + '\n\n'.join(sections) + '\n\n'
    research = research.replace('## 8. 核查记录与阅读入口', insertion + '## 9. 核查记录与阅读入口')
    research = re.sub(r'^- \[新增候选与复现成本\].*\n', '', research, flags=re.M)
    write('02_learning/research/review.CN.md', research)
    write('02_learning/research/README.md', '''
# 研究调研

当前处于选题前的开放调研阶段。这里保存阶段比较与详细审查，可继续扩展方向、替换候选、重评已有建议。目标和长期标准见[研究交接](../00_research_handoff.CN.md)。

| 阅读层次 | 内容 |
|---|---|
| 综合比较 | [阶段文献比较](review.CN.md)：主要方法、贡献与局限、接口、复现成本及相关工作；已合并原补充审查 |
| 策略路线 | [策略、历史与强化学习](reviews/policy_literature.md) |
| 模型路线 | [动力学、辨识与模型控制](reviews/dynamics_literature.md) |
| 恢复路线 | [故障、扰动与恢复](reviews/fault_literature.md) |
| 平台和评估 | [硬件接口](../platform/interfaces.CN.md) · [平台与 benchmark](reviews/platform_and_benchmark_review.md) |
| 汇报 | [当前 PPT 与讲稿](../reports/README.md) |

详细路线文档保留各自的论文和源码证据，综合结论统一维护在 `review.CN.md`，汇报材料统一放在 `reports/`。原阶段汇报草稿与补充审查已收录 [history.zip](../../99_archive/history.zip) 的 `organization_20261123/02_learning/research/`。

`evidence/` 保存公开来源与目录记录；`tools/` 保存发现、核查链接的工具。这些记录不代表完成了每篇全文精读，也不代表已穷尽研究领域或完成性能复现。官方发布情况、版本条件和候选排序应随新证据持续更新。
''')
    # Keep the research handoff compact; only update navigation, not the agreed scope.
    p = ROOT / '02_learning/00_research_handoff.CN.md'
    t = p.read_text(encoding='utf-8')
    t = t.replace('[FLAIR 执行记录](flair/reproduction.CN.md)与[复现总结](flair/reproduction.CN.md)', '[FLAIR 复现记录](flair/reproduction.CN.md)')
    write(p.relative_to(ROOT).as_posix(), t)
    p = ROOT / '02_learning/diffusion_policy/05_code_and_deployment/README.md'
    t = p.read_text(encoding='utf-8').replace('[05_deployment教材](../deployment_record.CN.md)解释当时的代码与操作', '[部署记录](../deployment_record.CN.md)汇总当时的实现、指标与验证依据')
    write(p.relative_to(ROOT).as_posix(), t)
    p = ROOT / 'README.md'
    t = p.read_text(encoding='utf-8')
    t = t.replace('| [研究资料]', '| [论文原文](01_papers/README.md) | 按主题配套的正文、补充材料、视频与技术报告 |\n| [研究资料]', 1)
    t = t.replace('| [PPT 与讲稿]', '| [实验平台](02_learning/platform/README.md) | Go2-W 硬件、双平台接口与连接资料 |\n| [PPT 与讲稿]', 1)
    write('README.md', t)
    p = ROOT / '02_learning/README.md'
    t = p.read_text(encoding='utf-8').replace('| Go2-W 硬件和接口 | [硬件与 SDK](platform/go2w.CN.md) |', '| 实验平台 | [Go2-W 硬件、双平台接口与连接](platform/README.md) |')
    t = t.replace('论文在 `01_papers/`', '论文见[原始资料索引](../01_papers/README.md)')
    write(p.relative_to(ROOT).as_posix(), t)
    p = ROOT / '99_archive/README.md'
    t = p.read_text(encoding='utf-8').replace('本次目录与交接重构见[整理说明](records/refresh_summary.md)。', '最近一次资料合并和主题归类见[整理记录](records/organization_summary.md)。')
    t += '\n本次合并前的教材、记录和综述原稿保存在 `history.zip/organization_20261123/`，该批 `entries.json` 记录对应文件校验值。原始整理审计继续保存在 `records/`。\n'
    write(p.relative_to(ROOT).as_posix(), t)
    plan['status'] = 'documents_written'
    plan['repaired_links'] = count
    PLAN.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'status': plan['status'], 'repaired_links': count}, ensure_ascii=False))


def verify():
    plan = json.loads(PLAN.read_text(encoding='utf-8'))
    errors = []
    for old, new in plan['moves'].items():
        p = ROOT / new
        # Markdown changes only rebase links; verify original text from the archived source separately.
        if not p.exists():
            errors.append('Missing moved file: ' + new)
        elif p.suffix.lower() != '.md' and digest(p) != plan['move_hashes'][old]:
            errors.append('Changed moved source: ' + new)
    for collection in ['protected', 'presentations']:
        for name, expected in plan[collection].items():
            if not (ROOT / name).is_file() or digest(ROOT / name) != expected:
                errors.append('Changed ' + collection + ': ' + name)
    with zipfile.ZipFile(ROOT / '99_archive/history.zip') as z:
        for item in plan['archive_entries']:
            if hashlib.sha256(z.read(PREFIX + item['path'])).hexdigest() != item['sha256']:
                errors.append('Invalid archived original: ' + item['path'])
    for name in plan['superseded']:
        if (ROOT / name).exists():
            errors.append('Superseded original remains: ' + name)
    checked_links = 0
    for p in sorted(set(owned_docs() + [ROOT / '01_papers/README.md'])):
        for match in LINK.finditer(p.read_text(encoding='utf-8-sig')):
            target = match[2].strip('<>')
            if re.match(r'^(?:[a-zA-Z][\w+.-]*:|#|//)', target) and not re.match(r'^[gG]:[/\\]', target):
                continue
            target = urllib.parse.unquote(target.partition('#')[0])
            target = re.sub(r':\d+$', '', target)
            if not target:
                continue
            checked_links += 1
            if not (p.parent / target).exists():
                errors.append('Broken link: ' + p.relative_to(ROOT).as_posix() + ' -> ' + target)
    slides = {}
    for name in plan['presentations']:
        if name.endswith('.pptx'):
            with zipfile.ZipFile(ROOT / name) as z:
                assert z.testzip() is None
                slides[name] = len([n for n in z.namelist() if re.fullmatch(r'ppt/slides/slide\d+\.xml', n)])
    plan['verification'] = {'errors': errors, 'checked_links': checked_links,
        'protected_files': len(plan['protected']), 'preserved_report_files': len(plan['presentations']),
        'presentations': slides, 'archive_sha256': digest(ROOT / '99_archive/history.zip')}
    plan['status'] = 'verified' if not errors else 'verification_failed'
    PLAN.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding='utf-8')
    write('99_archive/records/organization_summary.md', '''
# 资料归类与合并记录

日期：2026-11-23。范围为本地资料目录；未连接服务器、安装环境、运行模型或控制硬件。

## 调整结果

- `01_papers/` 按 Diffusion Policy、LocoFormer、FLAIR、当前调研及机械臂报告成套归类，新增唯一论文索引。
- Go2-W 硬件、图片和双平台输入输出审查移入 `02_learning/platform/`，不再挂靠某一篇论文。
- Diffusion Policy 学习地图合入主题入口；旧部署资料收敛为一份部署记录，当前六章教材统一为 `05_code_and_deployment/`。
- FLAIR 执行记录与总结合成 `reproduction.CN.md`，结果按 `data/`、`figures/`、`provenance/` 分类。
- LocoFormer 复现资料收敛为参考项目、统一接口、工作计划三份详细文档与一份导航，重复汇报概览归档。
- 研究综述合入补充审查，去除独立汇报草稿；保留分路线详细证据和当前 PPT/讲稿。

合并前原稿已保存到 `history.zip/organization_20261123/`，批内 `entries.json` 记录逐项 SHA-256。原始实验数据、验证记录和代码归档保留。

## 核验

''' + f"- 已检查 {checked_links} 个本地文档链接。\n- 已逐项校验 {len(plan['protected'])} 个非 Markdown 代码/资产文件，以及 {len(plan['presentations'])} 份汇报文件。\n- {len(slides)} 份 PPT 内容保持不变，并通过压缩包完整性检查。\n- 移动的论文、视频、LaTeX、图片、CSV 和原始记录均已核对内容哈希。\n- 核验发现问题 {len(errors)} 项；详细清单见 `organization.json`。\n\n报告 LaTeX 主文件原已缺少引用的图和参考文件；本次仅成套保存已收到材料，未补写或编译报告。\n")
    print(json.dumps(plan['verification'], ensure_ascii=False, indent=2))
    if errors:
        sys.exit(1)


if __name__ == '__main__':
    {'prepare': prepare, 'documents': documents, 'verify': verify}[sys.argv[1]]()
