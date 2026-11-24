# LocoFormer 学习与复习手册

本手册围绕 *LocoFormer: Generalist Locomotion via Long-context Adaptation*，把本次学习中分散的概念、公式、代码与疑问串成一条完整路径。目标是能够解释机器人怎样交互、历史怎样进入网络、奖励怎样影响参数，以及部署时为什么不更新权重仍能适应。

整理依据为当前对话中可见的技术提问、论文原文和本地参考代码。重复出现的“没看懂”保留为同一问题的不同阻塞点；“下一节”等推进指令不单独列项。本文重新组织解释，不声称逐字恢复没有完整保留的历史回答。

## 1. 先选阅读路线

| 当前需求 | 阅读位置 |
|---|---|
| 准备 Go2-W 复现组会汇报 | [复现汇报主文档](reproduction/README.md) |
| 回答论文贡献、相关工作、跨机器人接口与实验依据 | [06 研究定位与证据分析](06_research_positioning_and_evidence.md) |
| 先恢复整篇论文的全局理解 | [01 论文与完整流程](01_paper_and_full_pipeline.md#overview) |
| 混淆任务、Trial、Episode、segment、batch | [01 概念与时间尺度](01_paper_and_full_pipeline.md#concepts) |
| 不清楚网络内部怎样算、怎样利用历史 | [02 网络与长记忆](02_network_and_memory.md) |
| 不清楚奖励怎样变成梯度和参数更新 | [03 强化学习与PPO](03_reinforcement_learning_and_ppo.md) |
| 要对照真实函数调用、配置与张量 | [04 代码阅读与复现边界](04_code_and_reproduction.md) |
| 忘了当初某个疑问怎样解决 | [05 疑问归纳与复习索引](05_questions_and_review.md) |
| 准备汇报 | 先看01，再看05末尾的复述与自测；[汇报PPT](../reports/locoformer/paper.CN.pptx)、[逐页演讲稿](../../99_archive/history.zip) |

理解算法可按01→02→03→04阅读；准备研究汇报时，先读06建立问题、方法、比较与证据的主线，再用其他章节补充技术解释。以后可用05定位既有疑问。

复现准备另设[Go2-W复现手册](reproduction/README.md)，按硬件、参考项目、核心实现和工作计划组织。论文学习与复现规划分别维护。

## 2. 六份文档各自负责什么

1. **01：把对象与阶段放对位置。** 按论文顺序解释问题、任务分布、跨Trial训练、部署和实验。
2. **02：把历史的信息流讲清楚。** 从数字数组、MLP、QKV到segment、因果掩码、SG和KV-cache。
3. **03：把参数更新的计算链算清楚。** 从回报、TD、GAE到PPO裁剪、Critic损失、两条样本两轮更新。
4. **04：把解释对应到当前源码。** 给出默认配置、主要函数、数据形状、时间线和复现前需要核对的差异。
5. **05：保留学习过程中的阻塞点。** 按概念层级归并疑问，提供简答、误解诊断、跳转和自测。
6. **06：把算法理解转为研究分析。** 说明贡献、跨本体接口、相关工作、基线与指标、证据边界和公开资源。

## 3. 阅读中必须分清的三类内容

| 标记 | 依据与含义 |
|---|---|
| 论文事实 | 来自本地论文正文、图表及附录。论文未披露的参数不补写成作者设置 |
| 原理补充 | 为理解Transformer、PPO、GAE、自动求导而补充的通用知识或手算例子 |
| 参考实现 | 来自本地 `03_code/locoformer`。这是lucidrains/Phil Wang的第三方实现，不等同于作者训练源码 |

例如，“6层、段长128、约18秒最大可能历史影响”是论文中的示例；“12个环境、每个256步、段长16、优化4轮”是本地Microduck入口默认值。两者不能混成一套配置。

本文教学中使用的二选一动作、单参数Actor、标量平方误差Critic和普通梯度下降，都明确标为手算。Microduck入口实际使用连续Beta动作分布、HLGauss Critic损失和Adam。

## 4. 主要资料

- [本地论文](../../01_papers/locoformer/paper.pdf)：本次核对版本为arXiv:2509.23745v1。
- [本地参考仓库](../../03_code/locoformer/README.md)：核对日期2026-11-02，Git提交 `79ce9d72d1137015e0212284f06656c83bb414e7`，核对时工作区无未提交更改。
- [论文项目页](https://generalist-locomotion.github.io/)：作者实机视频与项目介绍。
- [PPO原论文](https://arxiv.org/abs/1707.06347)：交互采样与多轮代理目标优化。
- [GAE原论文](https://arxiv.org/abs/1506.02438)：由时序差分构造优势估计。
- [Transformer-XL原论文](https://arxiv.org/abs/1901.02860)：段间递归与长上下文。
- [PyTorch自动求导说明](https://docs.pytorch.org/docs/stable/notes/autograd.html)：计算图、反向传播与无梯度模式。

## 5. 这套材料不能替代什么

它可以帮助理解论文和阅读当前参考代码，但不代表已经完成论文复现、训练、实机部署或成功率验收。本次只整理文档和核对源码，没有运行训练、模型推理或硬件控制。完整作者配置、任务生成参数和复现实验仍需进一步获得与验证。

返回：[总学习入口](../README.md) · [Diffusion Policy路线](../diffusion_policy/README.md)
