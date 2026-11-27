# 04 选题调研

**放什么**：选题过程中的决策、比较、证据卡、粗筛表、查重记录和文献审查。
**不放什么**：论文原文（[01_papers](../01_papers/README.md)）、学习讲解（[02_learning](../02_learning/README.md)）、实验记录（[05_experiments](../05_experiments/README.md)）、给老师的汇报（[06_reports](../06_reports/README.md)）。

当前进度见 [STATUS](../STATUS.CN.md)。选题结论：以 **GRAM** 为基础论文，方向为选择性鲁棒适应 + 轮腿冗余容错。

## 根目录文件

| 文件 | 内容 | 状态 |
|---|---|---|
| [decision_memo.CN.md](decision_memo.CN.md) | 选题决策备忘（第 5 版）：为什么选 GRAM、备选与保底、阶段关卡 | ★ 当前主文档 |
| [00_goals_and_standards.CN.md](00_goals_and_standards.CN.md) | 研究目标、老师要求、评价标准、协作方式 | 当前有效 |
| [learning_vs_model_based.CN.md](learning_vs_model_based.CN.md) | 学习控制 vs 传统控制的证据，用于回答控制方向的质疑 | 当前有效 |
| [review.CN.md](review.CN.md) | 早期 Go2-W 与 UR7e 候选比较 | 历史参考（双平台阶段） |

## 子目录

| 目录 | 内容 | 状态 |
|---|---|---|
| [candidates/](candidates/README.md) | 证据卡：每篇重点论文一份（问题、方法、实验、复现条件、创新空间），含 GRAM 代码审查和算力核实 | 主线相关：`gram.md`、`compute_requirements.md`、`fault_tolerance_base.md`、`teacher_chain_*.md`；其余为历史候选 |
| [screening/](screening/README.md) | 粗筛与扫描：按方向、会议期刊、局限性的候选表和打分 | 历史过程记录 |
| [novelty/](novelty/README.md) | 查重与可行性核查：每个拟议创新点一份 | 主线相关：`fault_tolerance_check.md`；其余为历史方向 |
| [reviews/](reviews/) | 四条路线的文献与开源审计：策略、动力学、故障恢复、平台与基准 | 背景参考（`fault_literature.md` 与主线相关） |
| [review_opus/](review_opus/) | 复核记录：最接近工作审核、选题终审、PACE 审核 | 历史参考 |
| `evidence/` | 检索目录、来源链接核查记录（JSON） | 数据记录 |
| `tools/` | 会议论文筛选、链接核查脚本 | 工具 |

## 推荐阅读顺序

1. [decision_memo.CN.md](decision_memo.CN.md)：最终选了什么、为什么；
2. [candidates/gram.md](candidates/gram.md)：GRAM 精读与代码审查摘要；
3. [novelty/fault_tolerance_check.md](novelty/fault_tolerance_check.md)：轮腿容错方向的查重；
4. [learning_vs_model_based.CN.md](learning_vs_model_based.CN.md)：准备回答传统控制的问题。

这些记录不代表每篇论文都完成了全文精读，也不代表已穷尽研究领域；候选排序随新证据更新。早期阶段草稿收录在 [history.zip](../99_archive/history.zip) 的 `organization_20261123/02_learning/research/`。
