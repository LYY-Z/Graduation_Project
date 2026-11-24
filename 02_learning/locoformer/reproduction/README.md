# LocoFormer 复现规划与实现审查

这是 LocoFormer 方向形成的阶段性方案，不是已完成复现或当前最终选题。论文学习见[学习手册](../README.md)，共享平台事实见[Go2-W 硬件](../../platform/go2w.CN.md)与[接口审查](../../platform/interfaces.CN.md)。

| 顺序 | 文档 | 用途 |
|---|---|---|
| 1 | [参考项目](references.CN.md) | 第三方 LocoFormer、BabyLocoFormer 及其他项目实现了什么、能复用什么、缺少什么 |
| 2 | [统一接口与核心实现](interfaces.CN.md) | 三种输入统一方式、关节槽位、输出映射、策略与跨 Trial 记忆 |
| 3 | [复现工作计划](workplan.CN.md) | 原方向的阶段步骤、条件、交付和验收 |

原汇报概览与旧索引已收敛到本页；细节分别保留在三份文档中。[复现汇报 PPT](../../reports/locoformer/reproduction.CN.pptx)是对应阶段的汇报材料。原稿保存在 [history.zip](../../../99_archive/history.zip) 的 `organization_20261123/02_learning/locoformer/go2_reproduction/`。

作者原始发布的缺失和第三方实现的适用范围均是当时的审查结果，后续可根据新发布重评。当前开放调研要求见[研究交接](../../00_research_handoff.CN.md)。
