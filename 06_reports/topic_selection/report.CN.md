# 运行中局部动力学变化下轮足机器人的选择性鲁棒适应

选题汇报　2026 年 11 月

## 一、研究背景与问题

本课题的实验平台为 Unitree Go2-W 轮足机器人，共 16 个驱动关节：12 个腿关节采用位置控制，4 个轮子采用速度控制。基于强化学习的运动控制已能在仿真中训练、零样本部署到真机，但机器人在运行中仍会遇到训练时未充分覆盖的变化，例如负载突然增加、地面摩擦改变、某个轮子的驱动能力下降。

目前处理这类变化有两类主要做法：
- **适应类方法**（如 RMA）：从最近的历史观测中推断当前环境，再据此调整动作。在训练见过的范围内表现好，超出范围时推断容易出错。
- **鲁棒类方法**（如域随机化、对抗训练）：训练一个对各种情况都能工作的保守策略。可靠，但在正常情况下性能偏低。

GRAM（RA-L 2026）把两者结合起来：根据推断结果的不确定程度，决定多大程度采用适应信息、多大程度退回鲁棒策略。但它的退回是整体的，只要不确定，所有适应信息一起被弱化。

实际运行中的变化往往是局部的。例如机器人已经适应了当前的地面和负载，途中右前轮驱动突然变弱：此时对地面和负载的判断大部分仍然有用，只有轮驱动相关的部分不再可信。整体退回会丢掉这些仍然有用的信息，使机器人不必要地变保守。

**本课题研究的问题**：运行中发生局部动力学变化时，能否保留仍然可信的适应信息，只对不可信的部分采取保守处理，从而在不牺牲正常性能的前提下更好地应对变化。

## 二、文献调研概况

调研覆盖 2025–2026 年的主要机器人会议（RSS、CoRL、ICRA、IROS、NeurIPS、ICLR、ICML）的录用列表，以及 Science Robotics、IJRR、T-RO、RA-L 等期刊同期的论文，另检索了轮足方向的预印本。筛选出与足式和轮足学习控制相关的会议论文 385 篇、期刊论文 151 篇、轮足预印本 69 篇，并对其中 258 篇顶刊顶会论文提取了作者自述的局限与未来工作。

几点主要结论：
1. **轮足方向的研究仍然很少**。轮足只占相关会议论文的约 2%，明确以 Go2-W 为平台的论文仅有 1 篇。
2. **适应与鲁棒控制是成熟方向**。历史编码器、教师—学生训练、域随机化都有大量工作，单纯组合这些方法已难以形成新贡献。因此创新需要针对某篇具体方法的明确不足展开。
3. **选择基础论文的标准**：顶刊或顶会正式发表；有完整的训练与评估代码；原平台与 Go2-W 接近；存在可以针对性改进的局限。

## 三、基础论文：GRAM

Queeney J., Cai X., Schperberg A., Corcodel R., Benosman M., How J. P. *GRAM: Generalization in Deep RL with a Robust Adaptation Module*. IEEE Robotics and Automation Letters, 11(2): 2218–2225, 2026. DOI: 10.1109/LRA.2025.3641155。官方代码：github.com/merlresearch/gram。

### 1. 作者要解决的问题

训练时可以获得环境参数（摩擦、质量等），部署时无法获得。作者希望用一个策略，同时在训练分布内取得好的性能，又能应对分布外的情况（论文式 1–2）。

### 2. 已有方法的局限

- 适应类方法："adaptation is only reliable for the range of ID scenarios seen during training"（p.1）——适应只在训练见过的范围内可靠。
- 鲁棒类方法："at the cost of conservative performance in ID environments"（p.1）——鲁棒性以分布内的保守表现为代价。
- 两者难以兼顾："making it challenging to achieve both with a single policy"（p.2）。

### 3. 方法设计

GRAM 以 RMA 式的教师—学生框架和 PPO 为基础，新增三项设计：

| 设计 | 内容 | 对应的问题 |
|---|---|---|
| 鲁棒适应模块 | 用认知不确定性网络（epinet）估计历史编码的均值与方差，8 次采样（式 5） | 判断当前的适应信息是否可信 |
| 按不确定性混合 | 最终表示 = (1 − α)·鲁棒表示 + α·适应估计，α = exp(−(σ̂² − β)⁺)，鲁棒表示取 0（式 9） | 不确定时自动退向鲁棒策略 |
| 联合训练 | 并行环境交替进行"适应训练"与"带推力对抗的鲁棒训练"，共用一个策略网络（p.4） | 同一策略同时具备两种能力 |

关键细节：不确定性是对 8 维隐变量的方差求和得到的一个标量，回退系数 α 也是一个标量，作用于整个隐变量（式 6–9；代码 `gram_actor_critic.py` 第 620–696 行）。也就是说，退回是整体的。

### 4. 任务与训练

- 任务：Go2 速度跟踪；
- 观测：关节角、关节速度、投影重力、基座角速度，不含机身线速度；
- 动作：12 维目标关节角，PD 控制 200 Hz，策略 50 Hz；
- 历史长度 16 步，隐变量 8 维（表 I）；
- 训练时随机化的环境参数共 26 维：摩擦、附加质量、各关节电机强度、各关节零偏（表 II）；
- 部署只使用本体历史，不需要特权信息。

### 5. 测试设置与对比

- 训练只在平地上进行；
- 测试分为近分布外与远分布外：6 kg / 9 kg 负载、5° / 10° 坡、5 cm / 10 cm 粗糙地面、关节冻结；
- 另有运行中变化：仿真中第 10 s 突然增加 9 kg 负载（图 4），真机上走上泡沫和湿滑白板；
- 对比方法：鲁棒 RL、情境 RL（教师—学生）、域随机化，以及三个消融。

### 6. 主要结果

| 方法 | 分布内 | 近分布外 | 远分布外 |
|---|---|---|---|
| GRAM | 0.92 | 0.79 | 0.58 |
| 鲁棒 RL | 0.87 | 0.74 | 0.59 |
| 情境 RL | 0.94 | 0.75 | 0.42 |
| 域随机化 | 0.93 | 0.74 | 0.43 |

数值为归一化平均回报（表 III）。真机共 105 次试验，困难场景的成功次数为 GRAM 15/15、鲁棒 RL 12/15、情境 RL 2/15（表 V）。

### 7. 贡献与不足

作者指出，分布外的泛化能力取决于对抗训练对最坏情况的覆盖程度，论文只尝试了标准对抗者和四足机器人（p.8）。

阅读中发现的不足：
1. **退回是整体的**。只有一个因素异常时，其余仍可信的适应信息也被一起丢弃。这是本课题的切入点。
2. 鲁棒训练只使用了"推力"一种对抗，没有针对质量、摩擦、电机等单一因素的分布外训练。
3. 远分布外的回报与鲁棒 RL 相当（0.58 对 0.59）；近分布外有一个消融（0.80）略高于完整方法（0.79）。
4. 未报告仿真实验的随机种子数。

### 8. 复现条件

- 官方代码包含 6 种算法的训练与评估，但没有预训练权重、真机部署代码，也没有"运行中改变负载"的实现；
- 代码基于 Isaac Lab 1.0 和 Isaac Sim 4.1，需迁移到 Isaac Lab 2.3 才能在实验室服务器（Blackwell 架构显卡）上运行，预计 1–2 周；
- 迁移到 Go2-W 需要增加轮子的速度动作、修改观测与奖励，预计 1–2 周。Go2-W 的开源强化学习项目（HIMLoco、DreamWaQ 的 Go2-W 版本）可作为参考。

## 四、候选方案比较

| 排序 | 论文 | 出处 | 优势 | 主要问题 | 定位 |
|---|---|---|---|---|---|
| 1 | GRAM | RA-L 2026 | 问题对口；原平台为 Go2；代码完整；局限明确 | 代码需迁移 | 基础论文 |
| 2 | MoE-CTS / RoboGauge | RSS 2026 | 不依赖机身速度，与 Go2-W 最契合；代码与评估工具开源 | 贡献偏向策略评价与筛选，需要大量重复实机实验 | 备选 |
| 3 | PACE | IJRR 2026 | 期刊级别最高；辨识流程清晰 | 运动训练环境未公开；在轮足上的延伸偏工程 | 保底 |
| 4 | AugMPC | RA-L 2026 | 学习与 MPC 分工清楚；不依赖里程计 | Go2-W 没有现成的轮足 MPC，自建需 2–4 个月；论文无对比基线 | 若实验室有轮足 MPC 可考虑 |
| 5 | Random Joint Masking | ICRA 2024 | 足式容错的代表方法 | 无代码，参数不全；只处理单关节 | 相关工作 |
| 6 | TAM | CoRL 2026 | 在力矩层做适应，与策略解耦 | 只适用于固定基座机械臂 | 相关工作 |
| 7 | SimDist | RSS 2026 | 世界模型适应，思路好 | 需要机身速度和外接 GPU 做在线规划 | 相关工作 |
| 8 | LocoFormer | CoRL 2025 | 包含 Go2-W 实机 | 无官方代码，训练规模极大 | 相关工作 |

### MoE-CTS / RoboGauge

Wu T. 等，RSS 2026。作者指出："the lack of reliable quantitative proxies compels researchers to rely on direct physical validation, a process that remains prohibitively risky and inefficient"（p.2）——缺少可靠的定量指标，只能依赖有风险且低效的实机验证。方法是在并行教师—学生框架上加入多专家编码器，并用 MuJoCo 中的评估工具 RoboGauge 预测实机表现。实机侧向冲击成功 18/20，Unitree 内置控制器为 5/20（表 VI）。

不足：可预测性只用一个模型验证；多专家的增益与训练配方改进没有分开比较。该方向更适合研究"怎样可靠地选出可部署策略"，与本课题直接改进控制的目标不同。

### PACE

Bjelonic F. 等，IJRR 2026。作者指出现有方法 "often require specialized sensors, exhaustive parameter identification, or iterative expert tuning"（p.1）。方法是让机器人悬空，只用关节编码器数据，通过 CMA-ES 拟合每个关节的电枢、阻尼、摩擦、偏置与延迟。作者自述局限："finite excitation bandwidth on suspended setups and temperature/aging dependencies that shift effective parameters"（p.21）。

用于 Go2-W 时，作者在代码仓库中说明悬空辨识不会辨识滚动阻力与打滑；论文的运动训练环境也未公开，复现只能覆盖辨识部分。因此作为保底方向：在 Go2-W 上复现悬空辨识，并补充轮—地参数的标定。

### AugMPC

Patrizi A. 等，RA-L 11(5):5797–5804，2026。上层强化学习决定步态与接触时序，下层全刚体 MPC 负责执行，"This offloads the combinatorial burden of contact timing from the MPC"（p.1）。作者假设机器人没有里程计和接触传感器，速度由 MPC 估计。作者将强外扰下的系统评估列为未来工作（p.8），论文中也没有对比基线。

在 Go2-W 上使用需要先建立完整的刚体模型和实时 MPC。目前没有可直接用于 Go2-W 实机的轮足 MPC 开源实现，全身 MPC 的公开案例也都运行在外接 x86 电脑上，自建预计 2–4 个月，超出本课题的工期。

### 其余三篇

- **Random Joint Masking**（Kim M. 等，ICRA 2024）：训练中随机屏蔽关节来模拟故障，并估计哪个关节受损。作者指出模型类方法 "relied on a specific robot dynamic model, case-by-case models for various failure cases"（p.2）。该论文未公开代码，超参数不全，只处理单关节故障。其研究的"执行器局部失效"已作为本课题的变化类型之一。
- **TAM**（Son D. 等，CoRL 2026）：把适应层放到力矩接口，学习残差力矩。作者明确其前提为 "a usable ideal inverse torque-command map, and matched kinematic structure"，并指出接触 "may still be confused with robot-side mismatch"（p.9）。Go2-W 机身浮动且持续与地面接触，不满足其前提。
- **SimDist**（Levy J. 等，RSS 2026）与 **LocoFormer**（Liu M. 等，CoRL 2025）：前者部署时需要机身线速度和高度图，在线规划依赖笔记本级 GPU；后者没有官方代码，作者自述 "Training LocoFormer is highly resource-intensive compared to a specialist policy"（p.9）。

其他调研过的论文及其局限见附录。

## 五、研究方案

### 1. 拟解决的挑战

1. **因素能否区分**：一个轮子变弱会同时改变机身姿态和地面接触，仅凭 16 步本体历史，未必能区分"轮子变弱"与"地面变滑"。
2. **部分退回的组合需要训练**：如果训练时没有见过"一部分信息可信、另一部分不可信"的输入，推理时直接组合，效果可能比整体退回更差。
3. **鲁棒训练信号不足**：GRAM 的鲁棒训练只针对推力，没有针对单一因素的分布外训练。
4. **轮足适配**：16 个关节，轮子为速度控制，执行器、观测和奖励都需要重新设计。

### 2. 方法

1. **按物理因素分组**：先分为两组，环境因素（地面摩擦、负载）与执行器因素（轮驱动），将 8 维隐变量拆分为两个 4 维部分，每组分别估计不确定性和回退系数。
2. **训练时随机组合可信状态**：每个训练环境随机指定哪些组"不可信"，使策略见过各种部分可信的组合。
3. **针对性的鲁棒训练**：对被指定为不可信的组，把该组参数的采样范围扩展到训练分布之外，其余组保持在分布内。
4. **运行中变化**：在仿真中实现运行过程中改变负载、摩擦和单轮驱动增益。

### 3. 实验设计

**变化类型**：均在运行中发生，包括单轮驱动增益下降、单轮锁死、负载突变、地面摩擦突变及其组合；测试使用训练中未出现的幅度和组合。

**对比方法**：

| 对比方法 | 目的 |
|---|---|
| 充分域随机化的历史编码策略 | 常用强基线 |
| HIMLoco、DreamWaQ（Go2-W 版本） | 已有适应方法 |
| 原版 GRAM | 基础论文 |
| 分组但不做选择性退回 | 检验分组本身是否足够 |
| 变化检测 + 重置历史 | 简单的替代方案 |
| 驱动响应估计 + 降速 + 轮速重新分配 | 传统控制方法 |
| 直接告知哪组可信 | 方法上限 |

**评价指标**：速度跟踪误差、路线完成率、变化后的恢复时间、摔倒次数，以及正常情况下的性能损失（用于检验鲁棒性是否靠全程保守换来）。

**统计方法**：仿真使用多个随机种子并报告种子数；真机每个条件至少 5 次，按随机顺序配对进行。

### 4. 与传统控制方法的关系

该方法与容错控制中的"可重构控制"思路一致：可信的信息照常使用，不可信的部分保守处理。区别在于，由学习方法完成可信度判断和全身的腿轮协调。实验中直接与传统方法（驱动响应估计、降速与轮速重新分配）对比，并按变化类型分别分析两类方法的适用情形。

### 5. 预期贡献

1. 将 GRAM 的整体退回扩展为按物理因素的选择性退回，并给出"部分信息可信"条件下的鲁棒训练方法；
2. 在轮足机器人上实现运行中局部动力学变化的适应与恢复，并在 Go2-W 实机上验证；
3. 通过消融实验分析分组、选择性退回和针对性鲁棒训练各自的作用。

与本课题相关的已有工作包括多因素上下文解耦（DMCM，CoRL 2025）和上下文不确定性估计（CERTAIN，ICML 2025）。本课题的区别在于面向运行中的局部变化，把因素可信度判断与条件鲁棒训练结合起来，并应用于轮足控制。

## 六、进度安排与风险

| 时间 | 工作内容 | 检查点 |
|---|---|---|
| 第 1 周 | 评估 GRAM 代码迁移工作量 | 迁移不可行则转为备选方向 |
| 第 2–4 周 | 在 Go2 仿真中复现 GRAM 的主要结果；进行上限检验：直接告知策略哪组可信，比较选择性退回与整体退回 | 若选择性退回没有明显优势，则调整为 GRAM 复现与失效分析 |
| 第 5–7 周 | 完成 Go2-W 适配 | — |
| 第 8–11 周 | 实现分组可信度估计与条件鲁棒训练，完成对比与消融实验 | — |
| 第 12–14 周 | Go2-W 实机实验：软件改变单轮驱动增益、增加负载、更换地面 | — |
| 第 15–16 周 | 整理结果，撰写论文 | — |

| 风险 | 应对措施 |
|---|---|
| 不同因素难以区分 | 先通过上限检验判断区分是否有价值；若实际难以区分，分析可区分的边界并如实报告 |
| 代码迁移耗时超出预期 | 第 1 周完成评估，必要时先在原环境中小规模验证思路 |
| 原代码缺少权重和运行中变化的实现 | 自行训练并实现，在论文中说明 |
| 实机安全 | 先在仿真中完成全部测试；实机从低速、轮子相关的变化开始，配备急停 |

## 七、需要确认的事项

1. 研究方向与基础论文（GRAM）是否合适。
2. 实验室是否有可用于 Go2-W 的轮足 MPC。如有，AugMPC 方向可以作为备选。
3. 实机条件：能否通过软件改变单个轮子的驱动增益；实验场地与每周可用的实机时间。

---

## 附录：其他调研论文

| 论文 | 出处 | 作者的问题或自述局限（原文） | 与本课题的关系 |
|---|---|---|---|
| RMA | RSS 2021 | "domain randomization trades optimality for robustness leading to an over conservative policy"（p.4） | 历史编码器的来源，GRAM 的基础 |
| HIMLoco | ICLR 2024 | "This two-phase training paradigm complicates the training process and inevitably induces information loss"（p.2） | 对比基线 |
| DreamWaQ | ICRA 2023 | "its adaptation mechanism, where it must first hit the obstacles with its legs"（p.6） | 对比基线 |
| DreamFLEX | ICRA 2025 | "these studies had a limited demonstration for overcoming various rough terrains"（p.1） | 关节故障下的容错运动 |
| ESCP | AAAI 2022 | "previous methods show lagged and unstable context extraction, which are hard to handle sudden changes well"（摘要） | 突变环境中的快速适应 |
| SADL | IJRR 2026 | "particularly when encountering dynamics that are out-of-distribution"（p.25） | 情境识别与条件动力学 |
| ASID | ICLR 2024 | "the requirement for an extremely accurate simulation"（摘要） | 主动系统辨识 |
| FLAIR | Nature Communications 17:3715, 2026 | "FLAIR cannot fully recover operability when the force required to counteract a perturbation exceeds the maximal strength of the actuators"（p.8） | 在线扰动补偿 |
| Diffusion Policy | RSS 2023 / IJRR 2024 | "higher computational costs and inference latency"（p.15） | 生成式策略，面向机械臂 |
| CaT | IROS 2024 | "current solvers fail to produce efficient policies respecting hard constraints"（摘要） | 约束强化学习 |
| PEGrad | CoRL 2025 | "we found it challenging to combine the energy minimization objective with style rewards"（p.9） | 能耗优化 |
| DIAL-MPC | ICRA 2025 | "requires fast simulation to generate samples"（p.7） | 采样式 MPC，需要外部定位 |
| Omni-Perception | CoRL 2025 | "Performance can degrade in environments dominated by highly unstructured vegetation"（p.9） | 激光雷达避障 |
| VR-Robo | RA-L 2025 | "limited to indoor scenes with static terrains"（p.7） | 三维重建视觉策略 |
| StreamVLN | ICRA 2026 | "face trade-offs among fine-grained visual understanding, long-term context modeling and computational efficiency"（摘要） | 视觉语言导航 |
| Fu 等 | Nature Communications 17:5857, 2026 | "its adaptation to environmental shifts is limited"（p.7） | 动物动作模仿 |
| QOED | RSS 2026 | "identifying nuisance parameters and accounting for their influence remains a significant gap"（p.2） | 信息论主动探索 |
| Lee 等 | Science Robotics 9(89), 2024 | "Existing approaches for hybrid locomotion build upon simple heuristics to decide when to step and when to drive"（p.1） | 轮足混合运动 |
| Skid-steer loaders | Science Robotics 11(120), 2026 | "we composed the overall behavior using hand-crafted switching conditions"（p.6） | 滑移转向车辆的学习控制 |
| Hao 等 | RICAI 2023 | "the tire longitudinal and lateral force are large"（摘要） | 腿姿辅助轮足转向 |

注：引用页码为 arXiv 版本页码。各论文的完整分析见 `04_research/candidates/` 下的精读记录。
