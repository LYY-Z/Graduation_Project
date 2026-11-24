from pathlib import Path

ROOT=Path('G:/毕设')
contents={
'README.md':'''# 机器人运动控制研究工作区

面向 Go2-W 轮足机器人与 UR7e 机械臂，开展适应、扰动恢复和学习控制的论文调研、复现与实验。

## 入口

- [研究交接与长期要求](02_learning/00_research_handoff.CN.md)：当前状态、已有证据和论文工作规范。
- [当前文献调研](02_learning/motion_control/README.md)：TAM、GRAM、SADL 及补充论文。
- [学习资料](02_learning/README.md)：Diffusion Policy、LocoFormer、FLAIR 的论文与代码讲解。
- [PPT 与讲稿](02_learning/reports/README.md)：各主题当前交付版本。
- [代码索引](03_code/README.md)：活动项目与参考仓库。
- [归档索引](99_archive/README.md)：旧源码、旧文档和整理记录。

## 目录

```text
01_papers/     论文、补充材料和技术报告
02_learning/   学习资料、研究调研、平台说明和汇报
03_code/       活动代码与参考实现
99_archive/    压缩归档和整理记录
```

旧服务器镜像和重复工程不作为运行入口。实际复现、平台迁移及实机验证的状态分别以项目文档和原始记录为准。
''',
'02_learning/README.md':'''# 学习与研究资料

继续当前工作先读[研究交接](00_research_handoff.CN.md)。论文原文在 `01_papers/`，源码在 `03_code/`。

| 主题 | 入口 | 内容 |
|---|---|---|
| 当前研究 | [文献调研](motion_control/README.md) | 自适应运动控制、扰动恢复、复现与迁移判断 |
| Diffusion Policy | [学习路线](diffusion_policy/README.md) | 基础、DDPM、论文、源码与 UR7e 部署 |
| LocoFormer | [学习手册](locoformer/README.md) | 长历史、跨本体、Transformer-XL、PPO 与疑问索引 |
| Go2-W 平台 | [硬件与接口](locoformer/go2_reproduction/01_go2w_hardware.CN.md) | 关节、电机、SDK、观测和控制接口 |
| FLAIR | [源码与复现](flair/README.md) | 指令链、在线补偿、六足实验和指标 |
| 汇报 | [PPT 与讲稿](reports/README.md) | 当前中文、英文交付材料 |
| 平台连接 | [VNC](platform/vnc/connect.md) | 既有服务器可视化连接资料 |
| 概念回顾 | [总学习地图](00_learning_map.md) | 快速定位训练、推理与控制概念 |

## 目录

```text
diffusion_policy/   扩散策略学习与 UR7e 工程讲解
locoformer/        论文、网络、PPO 和 Go2-W 平台资料
flair/             FLAIR 教材、复现记录和 results/
motion_control/    当前文献筛选与源码审查
platform/          平台连接说明
reports/           按主题保存的最终汇报
```

主线教材负责完整解释，疑问索引负责定位，汇报文件负责表达。早期创新方案反映当时的讨论，当前课题状态以研究交接为准。旧版本和生成来源见[归档](../99_archive/README.md)。
''',
'03_code/README.md':'''# 代码索引

| 目录 | 用途 |
|---|---|
| [diffusion_policy_ur7e](diffusion_policy_ur7e/README.CN.md) | 当前 UR7e 与腕部相机适配项目 |
| [diffusion_policy](diffusion_policy/README.md) | 原 Diffusion Policy 源码，供论文与实现学习 |
| [locoformer](locoformer/README.md) | lucidrains 第三方实现，供长历史策略与 PPO 学习 |
| [references](references/README.md) | FLAIR、TAM、BabyLocoFormer、MetaMorph 等参考仓库 |

活动项目的源码、权重、第三方依赖和测试保持原结构。旧服务器镜像、UR7e 旧副本和早期部署参考压缩保存在[归档](../99_archive/README.md)，不作为运行入口。

本目录不保留复制的 Linux Python 环境与安装缓存。服务器环境按各项目文档独立准备；本次目录整理未连接或修改服务器。
''',
'02_learning/reports/README.md':'''# 汇报材料

每个主题保留当前需要的材料。中文为 `CN`，英文为 `EN`。

| 主题 | PPT | 讲稿与配套材料 |
|---|---|---|
| 适应与扰动恢复文献调研 | [中文](motion_control/report.CN.pptx) · [英文](motion_control/report.EN.pptx) | [中文讲稿](motion_control/speech.CN.md) · [英文讲稿](motion_control/speech.EN.md) |
| FLAIR 阅读、复现与历史研究方案 | [中文](flair/report.CN.pptx) · [英文](flair/report.EN.pptx) | [中文讲稿](flair/speech.CN.md) |
| LocoFormer 论文阅读 | [中文](locoformer/paper.CN.pptx) · [英文](locoformer/paper.EN.pptx) | [中文讲稿](locoformer/paper.speech.CN.md) · [英文讲稿](locoformer/paper.speech.EN.md) |
| LocoFormer 复现计划 | [中文](locoformer/reproduction.CN.pptx) · [英文](locoformer/reproduction.EN.pptx) | 讲稿见 PPT 备注 |
| Diffusion Policy 论文阅读 | [中文](diffusion_policy/report.CN.pptx) | [讲稿](diffusion_policy/speech.CN.docx) · [知识回顾](diffusion_policy/knowledge_review.CN.docx) |
| UR7e 部署进展 | — | [汇报文档](ur7e/deployment_brief.CN.md) |

文献调研为 7 页正文和 6 页附录，逐页讲稿已写入备注。其他主题反映各自汇报时的状态，当前课题判断以[研究交接](../00_research_handoff.CN.md)为准。

旧汇报版本与构建来源见[归档索引](../../99_archive/README.md)。
''',
'99_archive/README.md':'''# 归档

日常入口为[学习资料](../02_learning/README.md)、[汇报材料](../02_learning/reports/README.md)和[代码](../03_code/README.md)。这里保存追溯与恢复资料。

2026-11-23 整理记录集中在 `workspace_cleanup_20261123/`：

| 文件 | 内容 |
|---|---|
| [legacy_code.zip](workspace_cleanup_20261123/legacy_code.zip) | UR7e 旧工程、旧服务器源码快照、依赖锁定和原始实机日志 |
| [legacy_documents.zip](workspace_cleanup_20261123/legacy_documents.zip) | 旧 PPT、研究方案、专题草稿及原工作记录 |
| [presentation_sources.zip](workspace_cleanup_20261123/presentation_sources.zip) | 汇报生成脚本、审查文本、来源数据与源插图 |
| [prior_archives.zip](workspace_cleanup_20261123/prior_archives.zip) | 整理前已有归档，保留原目录层次 |
| [documentation_before.zip](workspace_cleanup_20261123/documentation_before.zip) | 整理前文档，供追踪链接和入口变更 |
| [清理记录](workspace_cleanup_20261123/cleanup_report.md) | 目录变更、验证结果和空间统计 |

归档文件已逐项读取并校验 SHA-256。重复 checkpoint 仅保留当前项目 `03_code/diffusion_policy_ur7e/models/` 中的一份；恢复旧工程时按清理记录中的哈希补齐。复制的 Linux 环境、安装缓存、未完成下载和可再生渲染产物未归档。

归档包含原始工作记录，仅供项目内部追溯，公开发布前应单独审查连接配置和敏感信息。
''',
}
for rel,text in contents.items():
    p=ROOT/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text,encoding='utf-8')

p=ROOT/'02_learning/locoformer/go2_reproduction/README.md'
t=p.read_text(encoding='utf-8').replace('../../04_review/deliverables/locoformer/go2w_reproduction_brief.refined.CN.pptx','../../reports/locoformer/reproduction.CN.pptx')
t=t.replace('旧专题资料保留供追溯，当前入口以本页为准。','旧专题草稿已压缩归档。这里记录 LocoFormer 方向的阶段性规划，当前研究状态见[研究交接](../../00_research_handoff.CN.md)。')
p.write_text(t,encoding='utf-8')
p=ROOT/'02_learning/flair/README.md';t=p.read_text(encoding='utf-8')
t=t.replace('| 4 | [Go2-W 研究与论文计划](04_go2w_paper_plan.md) | 为何选 FLAIR，试探反馈的创新点，实验怎样支撑论文中的每项结论 |','| 历史方案 | [Go2-W 研究与论文计划](04_go2w_paper_plan.md) | 早期主动试探方案，仅作研究过程回顾 |')
t=t.replace('原有 Go2-W 选题文档中有一版“历史模型分段复用”方案。当前汇报和本目录第 4 篇使用后续确定的试探反馈方案。','第 4 篇和旧汇报保留早期选题，不作为当前确定课题。当前研究状态见[研究交接](../00_research_handoff.CN.md)，六足结果见[复现总结](reproduction_summary.md)。')
p.write_text(t,encoding='utf-8')

p=ROOT/'02_learning/00_research_handoff.CN.md';t=p.read_text(encoding='utf-8')
t=t.replace('| 保留的旧工程 | `03_code/diffusion_policy_ur7e_v1/`、`03_code/lyy_ws/`，不要误当唯一最新版 |','| 旧工程与实机日志 | `99_archive/workspace_cleanup_20261123/legacy_code.zip`，保留原目录供追溯 |')
t=t.replace('`02_learning/flair_reproduction_execution.md`、`flair_reproduction_summary.md`','`02_learning/flair/reproduction_execution.md`、`02_learning/flair/reproduction_summary.md`')
t=t.replace('- `motion_control_review.CN.pptx`：本次交接从当前中文画布导出的 13 页副本。','- `report.CN.pptx`：当前 13 页中文版。')
t=t.replace('- `motion_control_review.EN.v3.pptx`：最近实际交付的英文版本。`EN.pptx`、`EN.v2.pptx` 是较早导出，不作为最新版。','- `report.EN.pptx`：当前英文版，内容承接整理前的 EN.v3；较早导出已归档。')
t=t.replace('构建依据位于 `02_learning/04_review/.build_tam/`：中文布局源 `visual_screening.mjs`、`appendix_audit.mjs`；三篇 PDF、原图与审查文本；英文翻译映射和独立构建脚本。','构建来源已压缩至 `99_archive/workspace_cleanup_20261123/presentation_sources.zip`，保留布局代码、翻译、讲稿数据、源图和审查文本。TAM、GRAM、SADL 原文集中在 `01_papers/`。')
t=t.replace('`go2w_research_topic.md`、`go2w_research_briefing.md`、早期 FLAIR 计划等保留了当时的历史模型复用方案，','`legacy_documents.zip` 中的 `go2w_research_topic.md`、`go2w_research_briefing.md` 和早期 FLAIR 计划保留了历史模型复用方案，')
t += '\n\n## 18. 2026-11-23 目录整理更新\n\n根目录现仅有论文、学习、代码和归档四个主目录。汇报已统一为 `02_learning/reports/<topic>/`，文献调研为 `02_learning/motion_control/`，FLAIR 执行、总结与结果归入 `02_learning/flair/`。旧服务器镜像和旧 UR7e 副本已校验压缩，复制的 Linux 环境和安装缓存不再保留。原始实验日志、依赖清单和旧源码仍可从归档恢复，服务器未连接、未修改。\n\n较早消息中的旧路径不再有效，以[工作区入口](../README.md)和[清理记录](../99_archive/workspace_cleanup_20261123/cleanup_report.md)为准。当前中文和英文 PPT 均使用 `report.CN.pptx`、`report.EN.pptx`，不要再使用 EN.v1/v2/v3 等旧路径。\n'
p.write_text(t,encoding='utf-8')
print('Refreshed indexes and handoff.')
