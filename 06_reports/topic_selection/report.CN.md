# 选题汇报：运行中局部动力学变化下轮足机器人的选择性鲁棒适应

日期：2026-11-26。用途：向老师汇报选题与论文调研，请老师确认方向。

**写法约定**：
- **【原文】** 论文原话：逐字引用英文并标页码（arXiv PDF 页码，与印刷页码可能不同），后附中文意译；
- **【核实】** 我们用 Crossref、论文集页面、GitHub 等核实的元数据；
- **【评价】** 我们的判断；**【设想】** 尚未验证的研究计划。

凡未核实、只读到摘要或原文没有的内容，均如实标注。

**详细依据**：
- 核心论文十项精读：[teacher_chain_core](../../04_research/candidates/teacher_chain_core.md)
- GRAM 精读与代码审查：[gram](../../04_research/candidates/gram.md)
- 其余论文：[teacher_chain_secondary](../../04_research/candidates/teacher_chain_secondary.md)
- 决策过程：[decision_memo](../../04_research/decision_memo.CN.md)
- 全部方向比较：[options_overview](../options_overview.CN.md)

---

## 0. 一页总览

| 项目 | 内容 |
|---|---|
| 平台 | Unitree Go2-W 开发版：12 个腿关节（位置控制）+ 4 个轮子（速度控制）；底层模式下没有官方机身速度 |
| 题目方向 | 运行中局部动力学变化下轮足机器人的选择性鲁棒适应 |
| 要解决的问题 | 运行中发生局部变化（如一个轮子驱动变弱、负载突变）时，原有适应信息只有一部分失效：全部相信会补偿错误，全部丢弃又过于保守 |
| 基础论文 | **GRAM**（RA-L 2026，官方代码；老师给的论文之一） |
| 基础论文的关键局限 | 不确定时**整体**退回鲁棒模式：不确定性与回退系数都是单个标量（论文式 6–9；代码 `gram_actor_critic.py` L620–696，已核实） |
| 核心创新【设想】 | 把可信度判断细化到 2 组有物理含义的因素（环境：摩擦与负载；执行器：轮驱动），只对不可信的部分保守，并训练"部分信息可信"条件下的鲁棒策略 |
| 与老师方向的关系 | 延续"运行中扰动的适应与恢复"；GRAM 的基础是 RMA 式历史编码器 |
| 备选 | MoE-CTS / RoboGauge（RSS 2026，与 Go2-W 适配性最好，偏评价与部署）；AugMPC（RA-L 2026，需要 Go2-W 的 MPC） |
| 保底 | GRAM 复现 + Go2-W 失效分析；其次 PACE（IJRR 2026）轮—地标定 |
| 关卡 | 第 1 周代码迁移评估；第 2–4 周"理想上限检验" |
| 现实发表目标 | RA-L、ICRA、IROS |

---

## 1. 选题方法

**调研范围**：
- 顶会 2025–2026（RSS、CoRL、ICRA、IROS、NeurIPS、ICLR、ICML）逐条翻录用列表，筛出 385 篇；
- 顶刊（Science Robotics、IJRR、T-RO、RA-L、Nature 系）2025 年至今的 38,332 篇逐条筛查，得 151 篇；
- 轮足 + 学习预印本 69 篇；
- 跨领域 10 个；
- 从 258 篇顶刊顶会论文中抽取作者自述的局限与未来工作。

**评价标准**（事先定好，统一使用）：

| 标准 | 内容 |
|---|---|
| 论文价值 | 基础论文须为顶刊顶会正式发表 |
| 价值信号 | 有无顶刊顶会同类工作、强课题组是否点名为未来工作、有无实际需求（用于区分"没人做"是新机会还是不值得做） |
| 创新 | 组合、解决局限、跨领域迁移、新能力、检验主张均可，但不能已被做过 |
| 可行 | 有代码或复现基础；能在服务器（Blackwell GPU）运行；Go2-W 实机条件；3–4 个月可完成 |

**意见来源**：老师给的论文（GRAM、TAM、LocoFormer、RMA、ASID、SADL、FLAIR、Diffusion Policy 等）、Claude 的调研、Codex 的独立评估，三方汇总见 §5。

**主要发现**：轮足只占顶会相关论文的 2%，明确使用 Go2-W 的论文全领域仅 1 篇。轮足与"仿真到真机辨识""安全约束""世界模型"等主题的交叉，在 2025–2026 年顶会中均为 0 篇。

---

## 2. 推荐度排序总表

| 排名 | 论文 | 出处【核实】 | 定位 | 一句话理由 |
|---|---|---|---|---|
| **1** | **GRAM** | RA-L 11(2):2218–2225，2026 | **主线基础论文** | 问题直接对口；原平台 Go2；完整训练评估代码；局限明确（整体回退） |
| 2 | MoE-CTS / RoboGauge | RSS 2026，DOI 10.15607/RSS.2026.XXII.156 | 条件备选（偏评价） | 不依赖机身速度，与 Go2-W 适配性最好；创新偏"评价与筛选" |
| 3 | PACE | IJRR 2026，DOI 10.1177/02783649261459628 | 第二保底 | 级别最高、最稳；运动训练环境未公开，开拓性弱 |
| 4 | AugMPC | RA-L 11(5):5797–5804，2026 | 条件备选（需 MPC） | 学习与控制分工最清楚；需自建 Go2-W 的全刚体 MPC |
| 5 | Random Joint Masking | ICRA 2024 | 相关工作 / 基线思路 | 足式容错代表作；无代码；"局部执行器变化"已并入主线 |
| 6 | TAM | CoRL 2026（Spotlight 仅见项目页） | 相关工作 | 级别高，但只适用于固定基座机械臂 |
| 7 | SimDist | RSS 2026，DOI 10.15607/RSS.2026.XXII.017 | 相关工作 | 思想好，但需机身速度、外接 GPU 做规划 |
| 8 | LocoFormer | CoRL 2025，PMLR 305:532–546 | 相关工作 | 含 Go2-W 实机；无官方代码，训练规模极大 |
| 9 | HIMLoco / DreamWaQ | ICLR 2024 / ICRA 2023 | **主线的对比基线** | 已有 Go2-W 开源移植（HIMLoco-for-Go2W、DreamWaQ_Go2W） |
| 10 | RMA | RSS 2021 | 方法背景 | 历史编码器的经典来源 |
| 11 | DreamFLEX | ICRA 2025 | 相关工作 | 关节故障估计 + 调制；无代码 |
| 12 | ESCP / SADL / ASID | AAAI 2022 / IJRR 2026 / ICLR 2024 | 相关工作 | 突变适应、情境识别、主动辨识 |
| 13 | PEGrad / LoComposition / CaT | CoRL 2025 / 预印本 / IROS 2024 | 相关工作 | 能效与约束；单独成题创新不足 |
| 14 | FLAIR | Nature Communications 17:3715，2026 | 相关工作 | 在线补偿；原为履带与六足，与全身轮足控制差距大 |
| 15 | 其余（热约束、TEMPO、Omni-Perception、Fu 等、VR-Robo、StreamVLN、DIAL-MPC、FPO++、QOED、Diffusion Policy、Hao 2023、Lee 2024、滑移转向装载机） | 见 §4 | 相关工作或不适用 | 见 §4 |

---

## 3. 主要论文逐篇分析（按老师的论证链）

### 3.1 GRAM（推荐度 1，主线）

*GRAM: Generalization in Deep RL with a Robust Adaptation Module*。Queeney、Cai、Schperberg、Corcodel、Benosman、How（MERL、MIT、Amazon Robotics）。【核实】RA-L 11(2):2218–2225，2026，DOI 10.1109/LRA.2025.3641155；代码 merlresearch/gram。

| 环节 | 内容 |
|---|---|
| 作者的问题 | 动力学泛化：训练时可获得环境上下文，部署时不可得；希望一个策略同时应对训练分布内与分布外（p.2，式 1–2） |
| 已有局限与挑战 | 【原文 p.1】情境 RL / 教师—学生："adaptation is only reliable for the range of ID scenarios seen during training"（适应只在训练见过的范围内可靠）。【原文 p.1】鲁棒 RL："at the cost of conservative performance in ID environments"（以分布内保守表现为代价）。【原文 p.2】"making it challenging to achieve both with a single policy"（难以用单个策略同时做到两者） |
| 方法设计 | 基于 RMA 式教师—学生 + PPO + 对抗 RL。新增：①认知不确定性网络（epinet），8 次采样求均值与方差（式 5）；②最终表示 = (1−α)·鲁棒表示 + α·适应估计，α = exp(−(σ̂²−β)⁺)，鲁棒表示为 0（式 9）；③并行环境交替做"适应训练"和"带推力对抗的鲁棒训练"，共用一个策略网络（p.4） |
| 任务与训练 | Go2 速度跟踪。观测：关节角、关节速度、投影重力、基座角速度（**不含机身线速度**）；动作：12 维目标关节角，PD 200 Hz，策略 50 Hz；历史 16 步，隐变量 8 维（表 I）。训练上下文 26 维：摩擦、附加质量、12 维电机强度、12 维关节零偏（表 II） |
| Benchmark | Isaac Lab 仿真 + Go2 真机；训练在平地。测试：近/远分布外（6/9 kg、5°/10° 坡、5/10 cm 粗糙、关节冻结）。运行中变化：仿真第 10 s 加 9 kg（图 4）；真机走上泡沫、湿滑白板 |
| Baseline | 鲁棒 RL、情境 RL、域随机化，加三个消融（p.5–6） |
| 关键结果 | 归一化回报（分布内 / 近外 / 远外）：GRAM 0.92 / 0.79 / 0.58；鲁棒 RL 0.87 / 0.74 / 0.59；情境 RL 0.94 / 0.75 / 0.42；域随机化 0.93 / 0.74 / 0.43（表 III）。真机困难场景成功次数：GRAM 15/15，鲁棒 RL 12/15，情境 RL 2/15（表 V） |
| 作者自述局限 | 【转述 p.8】分布外泛化取决于对抗者对最坏动力学的覆盖，只试了标准对抗者和四足 |
| 【评价】不足 | ①**回退是整体的**（本课题切入点）；②鲁棒分支只用"推力"对抗训练；③远分布外上与鲁棒 RL 持平（0.58 对 0.59）；近分布外一个消融（0.80）略高于 GRAM（0.79）；④未报告仿真种子数 |
| 复现与 Go2-W 适配 | 有 6 种算法的训练评估代码，**无权重、无真机代码、无"运行中加负载"的代码**。基于 Isaac Lab 1.0 / Isaac Sim 4.1 / torch 2.2，需迁移到 Isaac Lab 2.3（约 1–2 周）；Go2-W 适配再约 1–2 周。观测不含机身线速度，与 Go2-W 条件吻合 |

### 3.2 MoE-CTS / RoboGauge（推荐度 2，条件备选）

*Toward Reliable Sim-to-Real Predictability for MoE-based Robust Quadrupedal Locomotion*。西安交通大学。【核实】RSS 2026，DOI 10.15607/RSS.2026.XXII.156；代码 RoboGauge（MIT）、Isaac Lab 复现版（Apache-2.0）。

| 环节 | 内容 |
|---|---|
| 问题 | 【原文 p.1】"In practice, however, sim-to-real gap and reward overfitting in complex terrains can produce policies that fail to transfer, while physical validation remains risky and inefficient."（仿真到真机差距与奖励过拟合使策略迁移失败，实机验证有风险且低效） |
| 已有局限 | 【原文 p.2】"Moreover, the lack of reliable quantitative proxies compels researchers to rely on direct physical validation, a process that remains prohibitively risky and inefficient."（缺可靠的定量代理指标，只能实机验证）。【原文 p.3】"the limited expressive capacity of the student model often precludes it from accurately inferring the features encoded by the teacher"（学生模型表达力不足） |
| 方法 | 在 CTS（并行教师—学生）上加：①多专家（MoE）学生编码器 + 负载均衡损失；②奖励与课程改进；③RoboGauge：MuJoCo 中的三层评估，用仿真到仿真预测实机可迁移性 |
| 任务与观测 | Go2 多地形速度跟踪；观测为 IMU 角速度、重力、关节位置与速度、指令、上一动作，**不含机身线速度**；历史 5 步；PD（kp=20、kd=0.5），50 Hz |
| Baseline 与结果 | DreamWaQ、HIM、CTS，每种 3 个种子，按 RoboGauge 分数选最优（p.6）。RoboGauge 总分：本文 0.6713、CTS 0.5786、HIM 0.5379、DreamWaQ 0.5054（表 IV）。实机侧向冲击 18/20 对内置控制器 5/20（表 VI） |
| 作者自述未来工作 | 【原文 p.9】"Future research will extend RoboGauge to broader morphologies like humanoid robots and integrate exteroceptive perception"（无单独局限节） |
| 【评价】不足 | ①"可预测性"只由一个模型的指标误差支持（表 III），没有跨多个策略的排序相关性；②MoE 增益与训练配方改进混在一起，未隔离；③用 RoboGauge 选模型又用它比较，存在循环；④实机 85/85 是"步数"，不是独立试验次数 |
| Go2-W 适配 | 【评价】**最好**：不依赖机身速度，同族机器人，许可宽松。需加轮子动作与奖励，并把 RoboGauge 改到 Go2-W 资产。**未选为主线的原因**：创新偏"评价与筛选"，而非直接改进运动控制；需要策略池和大量重复实机实验 |

### 3.3 PACE（推荐度 3，第二保底）

*Towards bridging the gap: Systematic sim-to-real transfer for diverse legged robots*。ETH Zurich RSL。【核实】IJRR 2026（在线优先，尚无卷期），DOI 10.1177/02783649261459628；辨识代码开源。

| 环节 | 内容 |
|---|---|
| 问题 | 【原文 p.1】"Yet controllers trained in simulation often fail to transfer reliably, and most existing approaches neglect actuator-specific energy losses or depend on complex, hand-tuned reward formulations."（仿真控制器迁移不可靠，多数方法忽略执行器能耗或依赖手调奖励） |
| 已有局限 | 【原文 p.1】"they often require specialized sensors, exhaustive parameter identification, or iterative expert tuning of heuristic models and reward functions."（需专用传感器、穷尽辨识或专家调参） |
| 方法 | 机器人悬空，只用关节编码器数据（一条 20–40 s 序列），CMA-ES 拟合每个关节的电枢、阻尼、摩擦、偏置和全机延迟（4n+1 个参数） |
| 结果 | 十余台机器人零样本迁移；ANYmal D 运输成本 1.27，相对 ANYmal C 的 1.86 降约 32%（表 5）。【评价】该对比跨机型、跨温度、跨奖励，不能完全归功于辨识 |
| 作者自述局限 | 【原文 p.21】"Current limitations include finite excitation bandwidth on suspended setups and temperature/aging dependencies that shift effective parameters."（悬挂激励带宽有限；温度与老化使参数漂移） |
| 【评价】 | 级别最高、问题清楚、最稳；但**运动训练环境与权重未公开**（作者在 issue #30 中确认），复现只能覆盖辨识部分；"补轮地参数"开拓性弱；作者在 issue #36 中自己指出悬空辨识"不会辨识滚动阻力、打滑" |

### 3.4 AugMPC（推荐度 4，条件备选：需要 MPC 支持）

*RL-Augmented MPC for Non-Gaited Legged and Hybrid Locomotion*。IIT。【核实】RA-L 11(5):5797–5804，2026，DOI 10.1109/LRA.2026.3675839（论文 PDF 本身未写）；代码 GPL-2.0。

| 环节 | 内容 |
|---|---|
| 问题 | 【原文 p.1】"a high-level RL agent provides gait and navigation commands to a low-level locomotion MPC. This offloads the combinatorial burden of contact timing from the MPC"（上层 RL 给下层 MPC 提供步态与导航指令，把接触时序的组合难题从 MPC 中拿走） |
| 已有局限 | 【原文 p.1】"optimizing over contacts leads to a Mixed-Integer Nonlinear Programming problem, which is often too complex to solve online."（在 MPC 中优化接触是混合整数非线性规划，难以在线求解）；无模型 RL "depend heavily on domain randomization and reward shaping"（严重依赖域随机化与奖励塑形） |
| 方法与训练 | 全刚体逆动力学 MPC（Horizon 框架）+ SAC；每只脚一个"飞行相注入"动作；800 个 MPC 并行；**不做域随机化**。【原文】"We assume no odometry or contact sensing is available on the robot"（假定无里程计与接触传感，速度由 MPC 估计） |
| 平台与结果 | 50 kg 简化四足、B2-W（仅仿真）、Centauro（120 kg，仿真 + 真机）；混合运动的运输成本约 0.12，腿式约 0.35（图 4） |
| 作者自述局限 | 【原文 p.8】"a systematic evaluation of robustness to strong and persistent external disturbances remains an important direction for future investigation."（对强、持续外扰的系统评估留作未来） |
| 【评价】不足 | **没有对比基线**；无扰动实验；种子数未报告；真机只有一台自家机器人 |
| Go2-W 适配 | **更正此前说法**：我们曾认为 AugMPC 需要机身速度，原文显示它不依赖里程计，这一点对 Go2-W 有利。真正的障碍是：需要 Go2-W 的完整刚体模型与 DDP 类 MPC（Horizon/Pinocchio/CasADi）；没有可直接用于 Go2-W 实机的轮足 MPC 开源实现（[开源 MPC 核查](../../05_experiments/go2w_mpc_opensource.CN.md)）；全身 MPC 公开案例都用外接 x86 电脑（[机载算力核查](../../05_experiments/go2w_onboard_compute.CN.md)）。估计搭建需 2–4 个月 |

### 3.5 第二档：认真考虑过但不作主线

| 论文 | 问题（原话） | 已有局限（原话） | 方法与结果 | 作者自述局限（原话） | 为何不作主线【评价】 |
|---|---|---|---|---|---|
| **Random Joint Masking**（ICRA 2024） | p1 "we propose a novel deep reinforcement learning framework to enable a quadrupedal robot to walk with impaired joints." | p2 "these methods often relied on a specific robot dynamic model, case-by-case models for various failure cases, and time-consuming model parameter tuning." | 随机屏蔽关节 + 关节状态估计 + 渐进课程；Go1；平均速度 RMSE 0.5787 → 0.1951（表 II） | p6 "there is a lot of room to improve in that the performance of impaired locomotion decreases according to the impaired joint positions"（截断引用） | 无代码、超参不全；只做单关节；基线弱（基线训练时没见过故障）。"局部执行器变化"已并入主线 |
| **TAM**（CoRL 2026；Spotlight 仅见项目页，论文集条目未查到） | p1 "A policy tuned for one robot often behaves differently on another, whether due to the sim-to-real gap, unknown payloads, or the differing dynamics of two instances of the same robot." | p1 "Domain randomization is not a panacea either, as it can result in overly conservative policies" | 把适应层放到力矩接口，学残差力矩；Franka 实机推箱成功率 76.2%，对 Direct 47.6%（表 1） | p9 "It assumes access to a torque interface, a usable ideal inverse torque-command map, and matched kinematic structure"；"deployment contacts ... may still be confused with robot-side mismatch." | 只适用于固定基座机械臂；Go2-W 是浮动机身且持续接触，前提不成立；仓库无许可证 |
| **SimDist**（RSS 2026） | p1 "Robot learning requires adaptation methods that improve reliably from limited, mixed-quality interaction data." | p2 "Existing end-to-end reinforcement learning methods often collapse when finetuning policies in new domains" | 仿真预训练世界模型，部署时只更新潜动力学；Go2 滑坡 4/5–5/5，IQL 0/5（表 IX） | p9 "freezing reward and value models can cap performance when the transferred value function saturates" | 观测含机身线速度与高度图；规划需 RTX 4090M 级笔记本；预训练约 4.9 亿步 + 28 h |
| **LocoFormer**（CoRL 2025） | p1 "Modern locomotion controllers are manually tuned for specific embodiments." | p2 "these controllers ... fail catastrophically in the case of large changes such as burnt out motors, broken legs, or modeling errors." | 程序化生成约 10 万台机器人 + Transformer-XL 长上下文；Go2-W 仿真零样本 0.97（表 1） | p9 "Training LocoFormer is highly resource-intensive compared to a specialist policy." | 无官方代码与权重；观测规格未公开；算力约为专才策略的 500 倍 |

---

## 4. 其余论文（简表）

| 论文 | 出处【核实】 | 作者的问题 / 局限（原话节选） | 未选原因【评价】 |
|---|---|---|---|
| HIMLoco | ICLR 2024 | p2 "This two-phase training paradigm complicates the training process and inevitably induces information loss" | 历史适应类已拥挤；**作主线基线**（有 Go2-W 移植） |
| DreamWaQ | ICRA 2023 | p6 "DreamWaQ's limitation lies in its adaptation mechanism, where it must first hit the obstacles with its legs." | 同上；**作主线基线** |
| RMA | RSS 2021 | p4 "domain randomization trades optimality for robustness leading to an over conservative policy" | 方法背景 |
| DreamFLEX | ICRA 2025 | p1 "these studies had a limited demonstration for overcoming various rough terrains." | 无代码；"故障估计 + 调制"已被做过 |
| ESCP | AAAI 2022 | p1 "previous methods show lagged and unstable context extraction, which are hard to handle sudden changes well." | 纯仿真、代码较旧；作突变适应的相关工作 |
| SADL | IJRR 2026（在线） | p25 "A more fundamental limitation relates to the model's generalization capabilities, particularly when encountering dynamics that are out-of-distribution" | 模型 + MPPI 规划，平台为地面车与四旋翼 |
| ASID | ICLR 2024 | p1 "The challenge with such model-based techniques is the requirement for an extremely accurate simulation" | 机械臂主动辨识 |
| FLAIR | Nat. Commun. 17:3715，2026 | p8 "FLAIR cannot fully recover operability when the force required to counteract a perturbation exceeds the maximal strength of the actuators." | 已复现；假设与全身轮足控制差距大 |
| Diffusion Policy | RSS 2023 / IJRR 2024 | p15 "diffusion policy has higher computational costs and inference latency" | 机械臂方向，平台已改为只做 Go2-W |
| Ségas 等（热约束） | **预印本** | p2 "temperatures barely change, making credit assignment of temperature-based rewards exceedingly challenging." | 未正式发表、无代码；方向在 2026 年较拥挤 |
| TEMPO | NeurIPS 2026（论文集页未核实） | p17 "it still relies on access to a pretrained critic that is reasonably informative under shift" | 无代码；真机在线更新有风险 |
| Omni-Perception | CoRL 2025 | p9 "Performance can degrade in environments dominated by highly unstructured vegetation" | 训练代码未公开；感知链长 |
| Fu 等（动作模仿） | Nat. Commun. 17:5857，2026 | p7 "its adaptation to environmental shifts is limited" | 轮子滚动时腿几乎不动，"像狗"的价值难论证 |
| VR-Robo | RA-L 10(8)，2025 | p7 "The current environment is limited to indoor scenes with static terrains" | 重建、对齐、部署代码未开源 |
| StreamVLN | ICRA 2026 | p1 "current VLN methods ... face trade-offs among fine-grained visual understanding, long-term context modeling and computational efficiency." | 需外接 GPU；感知与导航链最长 |
| CaT | IROS 2024 | p6 "Future work could explore more principled ways to define the termination conditions" | 约束工具，可作插件 |
| PEGrad | CoRL 2025 | p9 "we found it challenging to combine the energy minimization objective with style rewards." | 单独加能效创新不足 |
| LoComposition | **预印本**（CoRL 2026 录用未核实） | p9 "degraded sensing, and fully onboard state estimation remain future work." | 未核实录用 |
| DIAL-MPC | ICRA 2025（Best Paper Finalist，非获奖） | p7 "DIAL-MPC requires fast simulation to generate samples" | 需外部定位 |
| FPO++ | 预印本（CoRL 2026 据项目页） | p9 "FPO++ also takes more wall-clock time than Gaussian PPO" | 尚未导出具体的轮足问题 |
| QOED | RSS 2026 | p2 "identifying nuisance parameters and accounting for their influence remains a significant gap." | 偏辨识实验设计 |
| Hao 等（腿缩轴距转向） | RICAI 2023（仅读摘要） | "During the steering process, the tire longitudinal and lateral force are large" | 腿姿转弯的核心想法已被做过，且只见于小会 |
| Lee 等（轮足 ANYmal） | Science Robotics 9(89)，2024 | p1 "Existing approaches for hybrid locomotion build upon simple heuristics to decide when to step and when to drive" | 无代码；作轮足背景 |
| 滑移转向装载机 | Science Robotics 11(120)，2026 | p6 "we composed the overall behavior using hand-crafted switching conditions." | 作滑移转向的顶刊背景 |

**引文说明**：ESCP、StreamVLN、Hao 的自述局限原文未读到；DreamFLEX、Ségas、CaT、ASID 用未来工作或实验段的相邻句代替；RJM 一句因 PDF 断字而截断；FPO++ 摘要第二句与 QOED 一句未逐字核验。详见 [teacher_chain_secondary](../../04_research/candidates/teacher_chain_secondary.md)。

---

## 5. 三方意见整合

| 来源 | 主要建议 | 最终去向 |
|---|---|---|
| **老师** | 从运动控制的实际问题出发；关注运行中突变后的恢复；论文按问题—挑战—方法—实验—局限的链条阅读；能回答"为何优于已有学习方法与传统控制" | 作为全部评价的基础标准。GRAM（老师给的论文）作主线；RMA、ASID、SADL、LocoFormer、TAM、FLAIR 作相关工作 |
| **Claude** | 系统普查；价值信号检验；轮—腿冗余容错；PACE 轮—地标定；车辆动力学借鉴 | 容错问题并入主线（局部执行器变化）；PACE 作第二保底；普查结论用于论证领域空白 |
| **Codex** | 以 GRAM 为基础，研究"部分信息可信时的选择性鲁棒适应"；AugMPC、RoboGauge 为重点备选；理想上限检验 | 核心机制采纳；备选采纳 |
| **分歧与处理** | Codex 保留候选较多（LoComposition、SimDist、PACE/QOED、FPO++ 等）；Claude 主张只保留 4 项以免分散 | 最终只保留：主线 + 2 个条件备选 + 保底，其余作相关工作 |

**此前判断的更正**：①AugMPC 不依赖里程计（原以为需要机身速度）；②TAM 的障碍是"浮动基座 + 接触"使逆动力学前提不成立，不是"接口不匹配"（Go2-W 可发力矩指令）；③"轮足容错是空白"只限于检索范围，不能作为结论；④腿姿转弯因核心想法已见于 Hao 2023 而降级。

---

## 6. 研究方案

### 6.1 问题

运行中发生**局部**动力学变化时，能否**保留仍可信的适应信息，只对不可信的部分保守**，从而在不牺牲正常性能的前提下，比 GRAM 的整体回退恢复得更好？

**例子**：Go2-W 已适应当前地面与负载，途中右前轮驱动突然变弱。GRAM 会把整个适应估计一起弱化；但地面和负载的信息大部分仍然有用。更合理的做法是保留它们，只对轮驱动保守，由同一个全身策略协调腿和轮去补偿。

### 6.2 挑战

1. **因素能否区分**：一个轮子变弱会同时改变姿态与接触，16 步本体历史未必能区分"轮子弱"和"地面滑"；
2. **部分回退的组合没训练过**：直接拼接可能比整体回退更差；
3. **鲁棒训练信号**：GRAM 只用推力对抗，没有针对单组因素的分布外训练；
4. **轮足适配**：16 关节，轮为速度控制；
5. **部件没变化，不代表它的估计一定可信**：不能简单做成"只改坏轮子的控制"。

### 6.3 设计【设想】

| 挑战 | 设计 | 代码切入点（据代码审查） |
|---|---|---|
| 因素区分 | 先只分 2 组：环境（摩擦、负载）与执行器（轮驱动）；隐变量拆为 4 + 4 维；每组单独估不确定性与回退系数 | `context_env_wrapper.py`；`gram_actor_critic.py` L688–696、L620–628、L720–739 |
| 组合没训练过 | 训练时按组随机置为"不可信"，让策略见过所有组合 | `robust_masks` 改为每组一维（runner L198–219） |
| 鲁棒训练信号 | 不可信组的上下文采样扩到分布外，其余组保持分布内 | 参考仓库的 wide 配置 |
| 运行中变化 | 自写"运行中改质量、摩擦、单轮驱动增益"的事件 | `envs_utils.py` 新增 |
| 轮足适配 | 腿位置 + 轮速度两个动作项，16 维观测；参考 HIMLoco-for-Go2W 的资产与奖励 | 动作、执行器、奖励配置 |

### 6.4 实验

**变化类型**（运行中发生）：单轮驱动增益下降、单轮锁死、负载突变、地面摩擦突变及其组合；测试使用训练中没见过的幅度与组合。

| 对比组 | 作用 |
|---|---|
| 充分随机化的历史策略 | 强基线 |
| HIMLoco / DreamWaQ（Go2-W 版） | 已有适应方法 |
| 原版 GRAM（整体回退） | 基础论文 |
| 分组但不做选择性回退 | 检验"分组"本身是否足够 |
| 变化检测 + 历史重置 | 简单替代方法 |
| 传统控制：驱动响应估计 + 降速补偿 + 轮速重分配 | 回应传统控制方向 |
| 理想上限：直接告知哪组可信 | 检验机制上限 |
| 本文方法 + 消融 | — |

- **指标**：速度跟踪误差、路线完成率、变化后恢复时间、摔倒次数、**正常情况下的性能代价**（防止"更鲁棒"是靠全程保守换来的）。
- **统计**：仿真多种子，并报告种子数（补上 GRAM、MoE-CTS、AugMPC 等原文的共同不足）；真机每条件 ≥ 5 次，配对、随机顺序。

### 6.5 与传统控制的关系

本方法类似"部分故障下的可重构控制"：可信的部分照常使用，不可信的部分保守处理，由学习完成判断与全身协调。传统方法（驱动响应估计 + 降速 + 轮速重分配）作为基线放进实验，按变化类型分别报告各自的适用情形，不预设学习更好。

### 6.6 时间与关卡（约 16 周）

| 周 | 内容 | 关卡 |
|---|---|---|
| 1 | GRAM 代码迁移评估 | 不可行 → 换备选或保底 |
| 2–4 | Go2 仿真复现 GRAM 表 III 趋势；**理想上限检验** | "部分保守"不明显优于"整体保守" → 走保底 |
| 5–7 | Go2-W 适配 | — |
| 8–11 | 分组可信度 + 条件鲁棒训练；同预算对比与消融 | — |
| 12–14 | Go2-W 实机：用软件改单轮驱动增益、加负载、换地面 | — |
| 15–16 | 写作（第 13 周前完成保底版） | — |

### 6.7 风险

| 风险 | 应对 |
|---|---|
| 因素不可区分 | 理想上限检验先行；不可区分时如实报告可区分的边界 |
| 迁移耗时超预期 | 第 1 周评估；必要时先在旧环境中小规模验证 |
| 原代码无权重、无运行中变化 | 自训，自写事件，并在论文中写明 |
| 被认为"只是把标量改成向量" | 贡献落在"部分可信条件下的鲁棒训练"与系统消融上 |

**措辞约束**：不宣称首次解耦、首次不确定性适应或首次选择性鲁棒化。相关工作：DMCM（CoRL 2025，多因素上下文解耦）、CERTAIN（ICML 2025，上下文不确定性），已核实；Robust Factored MDPs（AAAI 2026）来自 Codex 引用，未单独核实。贡献限定为：面向运行中局部变化，把因素可信度与条件鲁棒训练结合，用于轮足控制。

---

## 7. 老师可能问的问题

| 问题 | 回答要点 |
|---|---|
| 创新是不是只把一个系数改成几个？ | 只改系数，推理时会遇到训练没见过的组合，可能更差。核心是"部分信息可信条件下的鲁棒训练"，并用"分组不回退""整体回退""理想上限"等消融证明贡献来源 |
| 为什么不选级别更高的 PACE（IJRR）或 TAM（CoRL）？ | PACE 运动训练环境未公开，补轮地参数开拓性弱，已作保底；TAM 前提是固定基座、无接触、有理想逆动力学，作者自己指出接触会被误判为机器人偏差，Go2-W 不满足 |
| 为什么不选与 Go2-W 适配最好的 MoE-CTS？ | 它的创新偏"评价与筛选策略"，需要策略池与大量实机重复；本课题更想直接改进控制。作为条件备选保留 |
| 为什么不用 AugMPC（学习 + MPC）？ | Go2-W 没有可用的轮足 MPC，自建需 2–4 个月；论文本身也没有对比基线和扰动实验。若实验室有轮足 MPC，可重新考虑 |
| GRAM 代码能直接跑吗？ | 不能：Isaac Lab 1.0 需迁移；无权重、无运行中变化代码，需自补。第 1 周评估 |
| 为什么不用域随机化？ | 作为对照组，在相同训练范围与预算下比较 |
| 为什么不用传统控制？ | 传统容错方法作为基线放进实验，不预设学习更好 |
| 因素分不开怎么办？ | 第 2–4 周理想上限检验先回答"分开是否有用"；实际分不开则如实报告并转保底 |
| 老师给的其他论文呢？ | 见 §2 与 §5：GRAM 选为主线，其余作相关工作或基线，未选原因均有出处 |

---

## 8. 请老师确认

1. 题目方向与基础论文（GRAM）。
2. 条件备选（MoE-CTS / RoboGauge、AugMPC）与保底（GRAM 失效分析、PACE）。
3. 实验室是否有可用于 Go2-W 的轮足 MPC（决定 AugMPC 是否可行）。
4. 实机条件：能否用软件改变单轮驱动增益；场地与每周的实机时间；扩展计算模块型号（Orin NX 或 Orin Nano）。
