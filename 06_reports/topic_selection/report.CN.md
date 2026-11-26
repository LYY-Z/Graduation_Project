# 轮足机器人学习运动控制：论文调研汇报

## 一、调研概况

**平台**：Unitree Go2-W 开发版，12 个腿关节采用位置控制，4 个轮子采用速度控制。

**方向**：学习驱动或学习与控制结合的运动控制，重点关注运行中扰动和动力学变化下的适应与恢复。

**检索范围与筛选**：

| 环节 | 范围 | 数量 |
|---|---|---|
| 会议 | RSS、CoRL、ICRA、IROS、NeurIPS、ICLR、ICML（2025–2026），逐条查看录用列表 | 筛出相关论文 385 篇 |
| 期刊 | Science Robotics、IJRR、T-RO、RA-L、Nature 系（2025 年至今），共 38,332 篇 | 筛出相关论文 151 篇 |
| 预印本 | arXiv 上的轮足 + 学习论文| 69 篇 |
| 略读 | 四足和轮足相关的顶刊顶会论文，阅读摘要、结论与局限 | 258 篇 |
| 精读 | 方法、代码、实验条件逐项核对 | 8 篇（见第三部分） |

**几点观察**：
1. 轮足方向的研究较少，在相关会议论文中约占 2%；以 Go2-W 为实验平台的论文只有 1 篇。
2. 适应与鲁棒控制是成熟方向，历史编码器、教师—学生训练、域随机化都有大量工作，创新需要针对具体论文的局限展开。
3. 精读论文的选择标准：顶刊或顶会正式发表；与本方向相关；有代码或足够详细的方法描述；能迁移到 Go2-W。

## 二、Go2-W 平台条件

| 项目 | 情况 |
|---|---|
| 底层控制 | 官方 SDK 支持 16 个电机的底层控制（腿：位置 + PD；轮：速度） |
| 机身速度 | 进入底层控制模式后读不到官方的机身速度估计，需要自建状态估计（激光雷达里程计或动捕） |
| 电机数据 | 每个电机可读位置、速度、估计力矩、温度；读不到单个电机的电流，整机电压电流可读 |
| 机载算力 | 8 核主控不对用户开放，用户程序需运行在 Jetson Orin 扩展模块或外接电脑上；运行强化学习策略可行（50 Hz）；简化的质心 MPC 需要 Orin NX 级别的扩展模块；全身 MPC 的公开案例都在外接电脑上运行 |
| 服务器 | 2 块 Blackwell 架构显卡，需要较新的软件版本（Isaac Sim 5.x、PyTorch 2.7 以上） |

## 三、精读论文

以下 8 篇按与本方向的相关程度和可实施程度排序。每篇按"问题—已有局限—方法—实验—局限"整理，并列出迁移到 Go2-W 的条件和可能的创新点。原文引用的页码为 arXiv 版本页码。

### 1. GRAM：鲁棒适应模块

Queeney 等，*GRAM: Generalization in Deep RL with a Robust Adaptation Module*，IEEE RA-L 11(2):2218–2225，2026。代码：github.com/merlresearch/gram。

| 项目 | 内容 |
|---|---|
| 问题 | 训练时可以获得环境参数，部署时无法获得。希望一个策略同时在训练分布内表现好，又能应对分布外情况 |
| 已有局限 | 适应类方法："adaptation is only reliable for the range of ID scenarios seen during training"（p.1）；鲁棒类方法："at the cost of conservative performance in ID environments"（p.1） |
| 方法 | 在教师—学生框架上，用认知不确定性网络估计历史编码的不确定程度。最终表示 = (1 − α)·鲁棒表示 + α·适应估计，不确定时自动退向鲁棒策略；并行环境交替进行适应训练和带推力对抗的鲁棒训练 |
| 实验 | Go2 速度跟踪。观测不含机身线速度；训练只在平地；测试包括 6/9 kg 负载、5°/10° 坡、粗糙地面、关节冻结，以及运行中突然加 9 kg 负载 |
| 结果 | 归一化回报（分布内 / 近分布外 / 远分布外）：GRAM 0.92 / 0.79 / 0.58，鲁棒 RL 0.87 / 0.74 / 0.59，域随机化 0.93 / 0.74 / 0.43（表 III）。真机困难场景成功 15/15，鲁棒 RL 12/15（表 V） |
| 作者自述局限 | 分布外泛化取决于对抗训练对最坏情况的覆盖，只试了标准对抗者和四足（p.8） |
| 阅读发现的不足 | ①不确定性和回退系数都是单个标量，退回是整体的（式 6–9，代码已核对）；②鲁棒训练只用推力一种对抗；③远分布外与鲁棒 RL 持平；④未报告随机种子数 |
| 迁移条件 | 有完整的训练与评估代码，但无训练好的模型、无真机部署代码、无运行中变化的实现；基于 Isaac Lab 1.0，需迁移到新版本，再适配 Go2-W。 |
| 算力与硬件 | 训练：4096 个并行环境，强化学习 1 万次迭代 + 适应模块 5 千次迭代（原文）；显卡与训练时间未报告，估计单卡约 3–4 小时。部署：原文 "all computation is performed onboard"，策略 50 Hz。本服务器可承受 |
| 可能的创新点 | ①选择性退回：按物理因素（环境、轮驱动等）分别判断可信度，只对不可信的部分保守；②针对单一因素的分布外鲁棒训练；③面向轮足的局部执行器变化（如单轮驱动变弱） |

### 2. MoE-CTS / RoboGauge：仿真到真机可预测性

Wu 等，*Toward Reliable Sim-to-Real Predictability for MoE-based Robust Quadrupedal Locomotion*，RSS 2026。代码：RoboGauge（MIT）、Isaac Lab 复现版（Apache-2.0）、Go2 部署代码。

| 项目 | 内容 |
|---|---|
| 问题 | "sim-to-real gap and reward overfitting in complex terrains can produce policies that fail to transfer, while physical validation remains risky and inefficient"（p.1） |
| 已有局限 | "the lack of reliable quantitative proxies compels researchers to rely on direct physical validation"（p.2）；学生模型表达能力不足，难以还原教师信息（p.3） |
| 方法 | 在并行教师—学生框架上加入多专家编码器；改进奖励与课程；提出 RoboGauge，在 MuJoCo 中多地形、多扰动评估，用于预测实机表现 |
| 实验 | Go2，7 种地形；与 DreamWaQ、HIM、CTS 比较，每种 3 个随机种子 |
| 结果 | RoboGauge 总分 0.6713，CTS 0.5786（表 IV）；实机侧向冲击成功 18/20，Unitree 内置控制器 5/20（表 VI） |
| 作者自述未来工作 | 扩展到人形等形态，加入外部感知（p.9） |
| 阅读发现的不足 | 可预测性只用一个模型验证；多专家的增益与训练配方改进没有分开比较；用 RoboGauge 选模型又用它比较 |
| 迁移条件 | 有训练好的 Go2 模型；需增加轮子的动作与奖励，并把评估工具改到 Go2-W。 |
| 算力与硬件 | 训练：8192 个并行环境（原文），仓库检查点约 8–14 万次迭代；论文未报告训练时间，仓库在 RTX 4090 上实测约 2.3–4.4 秒/迭代，估计单卡约 3.5–4 天。部署：Orin NX 或网线连接的外接电脑，策略 50 Hz（仓库说明）。本服务器可承受，但单次训练需数天；其 Isaac Lab 版本要求 Isaac Sim 6.2，与服务器的 5.1 不一致 |
| 可能的创新点 | ①轮足版的评估工具与指标；②用多个策略验证"仿真评分能否预测实机排序"；③隔离多专家结构本身的贡献 |

### 3. PACE：系统化的执行器辨识

Bjelonic 等，*Towards bridging the gap: Systematic sim-to-real transfer for diverse legged robots*，IJRR 2026。代码：辨识部分开源。

| 项目 | 内容 |
|---|---|
| 问题 | "controllers trained in simulation often fail to transfer reliably, and most existing approaches neglect actuator-specific energy losses or depend on complex, hand-tuned reward formulations"（p.1） |
| 已有局限 | 现有方法 "often require specialized sensors, exhaustive parameter identification, or iterative expert tuning"（p.1） |
| 方法 | 机器人悬空，只用关节编码器数据（约 20–40 s），用 CMA-ES 拟合每个关节的电枢、阻尼、摩擦、偏置和全机延迟，使仿真执行器与真机一致 |
| 实验 | 十余台机器人零样本部署；ANYmal 上与执行器网络、无模型对比 |
| 结果 | 与执行器网络效果相当，所需数据更少；ANYmal D 运输成本 1.27（表 5） |
| 作者自述局限 | "finite excitation bandwidth on suspended setups and temperature/aging dependencies that shift effective parameters"（p.21） |
| 阅读发现的不足 | 没有消融实验和统计；没有与调过参数的域随机化比较；作者在代码仓库中说明悬空辨识不会辨识滚动阻力与打滑 |
| 迁移条件 | 需要刚性悬挂架（机身固定，腿和轮可自由运动）；运动训练环境与模型未公开，只能复现辨识部分；评估轮地效果时需要测量机身运动（相机加标签或雷达里程计） |
| 算力与硬件 | 辨识：单张 RTX 3080、4096 个并行环境，10–24 小时（原文）。运动策略：3 万次迭代，约 24 小时（作者在代码仓库中的说明，Isaac Gym）。部署硬件未报告。本服务器可承受 |
| 可能的创新点 | ①检验"悬空数据足够"在轮子上是否成立；②补充轮—地参数（滚动阻力、滑移）的标定；③温度和老化引起的参数漂移 |

### 4. AugMPC：强化学习与 MPC 结合

Patrizi 等，*RL-Augmented MPC for Non-Gaited Legged and Hybrid Locomotion*，IEEE RA-L 11(5):5797–5804，2026。代码：GPL-2.0。

| 项目 | 内容 |
|---|---|
| 问题 | 上层强化学习决定步态与接触时序，下层 MPC 负责执行，"This offloads the combinatorial burden of contact timing from the MPC"（p.1） |
| 已有局限 | MPC 中优化接触 "leads to a Mixed-Integer Nonlinear Programming problem, which is often too complex to solve online"（p.1）；无模型强化学习依赖大量域随机化和奖励设计 |
| 方法 | 全刚体逆动力学 MPC（Horizon 框架）+ SAC；每只脚一个控制是否抬起的动作；训练时 800 个 MPC 并行；不做域随机化；假设没有里程计，速度由 MPC 估计 |
| 实验 | 50 kg 简化四足、B2-W（仅仿真）、Centauro 轮足（120 kg，仿真与真机） |
| 结果 | 混合运动的运输成本约 0.12，纯腿式约 0.35（图 4）；仿真到仿真、仿真到真机零样本迁移 |
| 作者自述局限 | "a systematic evaluation of robustness to strong and persistent external disturbances remains an important direction for future investigation"（p.8） |
| 阅读发现的不足 | 没有对比基线；没有扰动实验；未报告种子数 |
| 迁移条件 | **需要为 Go2-W 建立完整刚体模型和实时 MPC**，目前没有可直接用于 Go2-W 实机的开源轮足 MPC，自建预计 2–4 个月；全身 MPC 可能需要**外接电脑**运行；训练需要大量 CPU 核心（服务器 96 线程可满足） |
| 算力与硬件 | 训练：AMD Threadripper 7970 + 128 GB 内存 + RTX 4090，800 个并行环境（每个环境一个 MPC），4–10 × 10⁶ 环境步；12 个仿真日约 5.8 小时（原文）。部署：Centauro 机载 i7-11800H CPU 实时运行 MPC，策略推理 0.334 ms（原文）。本服务器 GPU 足够，瓶颈在 CPU，96 线程应可承受，需实测；Go2-W 上需在 Orin 或外接电脑运行 MPC |
| 可能的创新点 | ①执行能力下降（如轮驱动变弱）后，上层接触决策与下层可实现运动如何共同调整；②补充对外扰和变化的系统评估 |

### 5. Random Joint Masking：关节受损下的运动

Kim 等，*Learning Quadrupedal Locomotion with Impaired Joints Using Random Joint Masking*，ICRA 2024。代码未公开。

| 项目 | 内容 |
|---|---|
| 问题 | "enable a quadrupedal robot to walk with impaired joints"（p.1） |
| 已有局限 | 模型类方法 "relied on a specific robot dynamic model, case-by-case models for various failure cases, and time-consuming model parameter tuning"（p.2） |
| 方法 | 训练时随机屏蔽某个关节的动作和力矩；教师—学生结构估计哪个关节受损；按难度逐步加入故障的课程 |
| 实验 | Go1，单关节零力矩或锁死；仿真与室内外真机 |
| 结果 | 仿真平均速度误差从 0.5787 降到 0.1951（表 II） |
| 作者自述局限 | 性能随受损关节位置下降，仍有较大改进空间（p.6） |
| 阅读发现的不足 | 只处理单关节；基线训练时没见过故障，对比偏弱；无重复实验 |
| 迁移条件 | 无代码，课程阈值等参数不全，需自行实现；实机故障可用软件屏蔽电机模拟，**腿关节失效时需要悬挂保护** |
| 算力与硬件 | 仅说明在 Isaac Gym 训练，显卡、环境数、迭代数、训练时间均未报告；估计单卡数小时。实验使用 OptiTrack 动捕定位。本服务器可承受 |
| 可能的创新点 | ①轮足上的多种执行器失效（轮锁死、轮无力、腿关节失效）；②利用腿和轮互相补偿 |

### 6. TAM：力矩层适应

Son 等，*Torque Adaptation Module for Robust Motion Transfer in Manipulation*，CoRL 2026。代码已公开，未声明许可证。

| 项目 | 内容 |
|---|---|
| 问题 | "A policy tuned for one robot often behaves differently on another, whether due to the sim-to-real gap, unknown payloads, or the differing dynamics of two instances of the same robot"（p.1） |
| 已有局限 | 域随机化 "can result in overly conservative policies"（p.1）；RMA 类方法需要重新训练策略（p.2） |
| 方法 | 把适应层放到力矩接口，根据历史学习残差力矩，不需要修改上层策略 |
| 实验 | Franka 机械臂实机推箱、翻转、球板平衡等；仿真 7 种机械臂 |
| 结果 | 推箱成功率 76.2%，不做适应为 47.6%（表 1） |
| 作者自述局限 | 需要 "a usable ideal inverse torque-command map, and matched kinematic structure"；接触 "may still be confused with robot-side mismatch"（p.9） |
| 迁移条件 | 只适用于固定基座机械臂；Go2-W 机身浮动且持续与地面接触，不满足其理想逆动力学的前提；历史编码器需在 GPU 上运行 |
| 算力与硬件 | 训练显卡、时长、数据量均未报告；历史编码器约 440 万参数。部署：编码器在 GPU 上运行（RTX 3080 上约 1 ms、约 1.3 GB 显存），5 Hz；力矩修正在 CPU 上，1 kHz（原文）。训练可承受。部署（估计）：编码器规模不大，Jetson Orin 扩展模块自带 GPU，5 Hz 运行应可满足；但力矩修正原文为 1 kHz，Go2-W 底层通信通常约 500 Hz（需实测），只能降频运行 |
| 可能的创新点 | 轮子是单轴执行器，可尝试只对轮驱动做力矩层修正；但接触引起的误判仍需解决，难度较大 |

### 7. SimDist：仿真预训练世界模型

Levy 等，*Simulation Distillation: Pretraining World Models in Simulation for Rapid Real-World Adaptation*，RSS 2026。代码：MIT。

| 项目 | 内容 |
|---|---|
| 问题 | "Robot learning requires adaptation methods that improve reliably from limited, mixed-quality interaction data"（p.1） |
| 已有局限 | 端到端强化学习 "often collapse when finetuning policies in new domains"（p.2） |
| 方法 | 在仿真中预训练世界模型；部署时冻结编码器、奖励和价值函数，只用真机数据更新动力学部分；用 MPPI 在线规划 |
| 实验 | Go2 在光滑斜坡和泡沫上行走；UR5e 机械臂 |
| 结果 | 斜坡上 4/5 到 5/5 成功，对比方法 0/5（表 IX）；真机数据约 30 分钟 |
| 作者自述局限 | "freezing reward and value models can cap performance when the transferred value function saturates"（p.9） |
| 迁移条件 | 观测**需要机身线速度和高度图**（需要激光雷达定位或动捕）；在线规划需要**外接带 RTX 4090 级显卡的笔记本**；预训练数据量大（约 1 亿条数据、28 小时）；代码基于旧版软件，世界模型部分使用 JAX |
| 算力与硬件 | 训练：专家策略 4096 个并行环境、约 4.9 亿环境步；数据生成约 1 亿条、约 7 小时；世界模型预训练约 28 小时（均为单张 RTX 4500 Ada，原文）；专家训练时间未报告。部署：外接 RTX 4090 笔记本，50 Hz 在线规划（原文）。训练约 1.5–2 天，本服务器可承受；部署需外接 GPU 笔记本 |
| 可能的创新点 | ①在世界模型中加入轮子打滑，用于轮足快速适应；②检验"只更新动力学"在执行能力大幅变化时是否足够 |

### 8. LocoFormer：长上下文跨机体运动

Liu 等，*LocoFormer: Generalist Locomotion via Long-context Adaptation*，CoRL 2025。无官方代码。

| 项目 | 内容 |
|---|---|
| 问题 | "Modern locomotion controllers are manually tuned for specific embodiments"（p.1）；希望一个模型控制未见过的腿式与轮式机器人 |
| 已有局限 | 现有控制器 "fail catastrophically in the case of large changes such as burnt out motors, broken legs, or modeling errors"（p.2） |
| 方法 | 程序化生成约 10 万种机器人，配合极宽的域随机化；Transformer-XL 保留跨回合的长历史，在测试时适应 |
| 实验 | 10 种未见机器人（含 Go2-W）；实机 Go2、Go2-W、G1、H1 |
| 结果 | 仿真平均 0.96（零样本）、0.98（少样本），专门训练的策略为 0.99（表 1） |
| 作者自述局限 | "Training LocoFormer is highly resource-intensive compared to a specialist policy"（p.9） |
| 迁移条件 | 无官方代码和模型；观测规格未公开；训练算力约为单机型策略的 500 倍 |
| 算力与硬件 | 训练：约 10 万种机器人，训练曲线图中使用 32、64、128 块 GPU；6 层模型 4 千次迭代约 28 小时（显卡数量未写明）；原文 "LocoFormer takes 500 times more compute for 100000 more robots"，即约为单机型策略的 500 倍。按单机型策略约 1 GPU·天推算，总量约 500 GPU·天，本服务器 2 块卡约需 250 天，不可承受 |
| 可能的创新点 | 只针对 Go2-W 的小规模长上下文版本，用于运行中执行器变化的适应 |

## 四、对比汇总

| 论文 | 发表 | 代码 | 需要机身速度 | 特殊设备与算力 | 迁移工作量 | 创新空间 |
|---|---|---|---|---|---|---|
| GRAM | RA-L 2026 | 有（需迁移） | 否 | 无；单卡约数小时 | 中 | 较大：局限明确 |
| MoE-CTS / RoboGauge | RSS 2026 | 有，含模型 | 否 | 无；单卡约 3.5–4 天 | 中 | 中：偏评价方向 |
| PACE | IJRR 2026 | 仅辨识部分 | 辨识时否 | 刚性悬挂架；评估需相机或雷达定位；辨识 10–24 小时 | 中 | 中：偏工程 |
| AugMPC | RA-L 2026 | 有（GPL） | 否（由 MPC 估计） | Orin 或外接电脑运行 MPC；训练以 CPU 为主，约 6 小时 | 大（MPC 需自建，2–4 个月） | 较大 |
| Random Joint Masking | ICRA 2024 | 无 | 否 | 腿故障实验需悬挂保护 | 中（需自行实现） | 中 |
| TAM | CoRL 2026 | 有 | — | 编码器需 GPU（Orin 估计可满足）；力矩修正需约 1 kHz 底层控制 | 不适用于浮动基座 | 小 |
| SimDist | RSS 2026 | 有（旧版本） | 是 | 外接 GPU 笔记本；雷达定位；训练约 1.5–2 天 | 大 | 中 |
| LocoFormer | CoRL 2025 | 无 | 未公开 | 约 500 GPU·天（估计），本服务器不可承受 | 很大 | 小 |

## 五、结合 Go2-W 轮足特点的两个方向

上面的论文大多以纯腿式机器人为平台。Go2-W 同时有腿和轮，这一结构特点可以引出以下两个方向，均可与第三部分的论文结合。

### 1. 轮—腿冗余容错

| 项目 | 内容 |
|---|---|
| 问题 | 运行中某个电机失效时，利用另一套运动方式继续完成任务：轮子锁死或无力时改用腿行走，腿关节失效时依靠轮子滚动 |
| 相关工作 | 足式容错：FT-Net（RA-L 2023）、Random Joint Masking（ICRA 2024）、DreamFLEX（ICRA 2025）、FT-CPG（RA-L 2025）、Contrastive Forward Prediction（CoRL 2025）；IIT 的 Kyon 轮足论文（2026，预印本）将"轮足混合系统的容错"列为未来工作 |
| 现状 | 检索范围内未见轮足上的学习式容错；已有工作均为纯腿机器人，且以单关节故障为主；"估计故障并调整步态"已有 DreamFLEX 等工作 |
| 条件与难点 | 相关基础论文大多没有公开代码，需自行实现；实机故障可用软件屏蔽电机模拟，腿关节失效需悬挂保护；部分故障（如轮子无力时被动滚动）影响可能较小，需先测各类故障造成的退化程度 |
| 可结合的论文 | Random Joint Masking（故障注入与估计）；GRAM（作为"局部执行器变化"的一类具体情形） |

### 2. 腿姿辅助转向

| 项目 | 内容 |
|---|---|
| 问题 | Go2-W 的轮子不能转向，转弯靠左右轮差速，轮子横向擦地，耗能大、易打滑、转向不准。通过调整腿的姿态（轮距、前后轴距、各轮载荷）减少擦地，提高转弯效率与精度 |
| 相关工作 | Hao 等（RICAI 2023）已用缩短轴距辅助滑移转向（规划 + PID）；Go2-W 赛车论文（arXiv 2606.26313，AVEC 2026）用腿抑制转弯侧倾；滑移转向装载机的学习控制（Science Robotics 2026）；Lee 等轮足导航与运动（Science Robotics 2024） |
| 现状 | 用腿姿辅助转向的核心想法已有工作，但只见于小型会议，且未使用学习方法 |
| 条件与难点 | 需先用简化模型估算腿姿变化对转弯阻力的影响有多大；仿真器难以准确模拟轮子侧向擦地，需要用真机数据标定轮—地模型；收腿、蹲低需要腿部电机持续出力，可能抵消部分收益 |
| 可结合的论文 | PACE（执行器与轮—地参数标定） |

---

## 附录：其他调研论文

| 论文 | 出处 | 作者的问题或自述局限（原文） | 方向 |
|---|---|---|---|
| DreamFLEX | ICRA 2025 | "these studies had a limited demonstration for overcoming various rough terrains"（p.1） | 关节故障下的容错运动 |
| SADL | IJRR 2026 | "particularly when encountering dynamics that are out-of-distribution"（p.25） | 情境识别与条件动力学 |
| FLAIR | Nature Communications 17:3715, 2026 | "FLAIR cannot fully recover operability when the force required to counteract a perturbation exceeds the maximal strength of the actuators"（p.8） | 在线扰动补偿 |
| CaT | IROS 2024 | "current solvers fail to produce efficient policies respecting hard constraints"（摘要） | 约束强化学习 |
| PEGrad | CoRL 2025 | "we found it challenging to combine the energy minimization objective with style rewards"（p.9） | 能耗优化 |
| DIAL-MPC | ICRA 2025 | "requires fast simulation to generate samples"（p.7） | 采样式 MPC，需要外部定位 |
| Omni-Perception | CoRL 2025 | "Performance can degrade in environments dominated by highly unstructured vegetation"（p.9） | 激光雷达避障，训练代码未公开 |
| VR-Robo | RA-L 2025 | "limited to indoor scenes with static terrains"（p.7） | 三维重建视觉策略 |
| StreamVLN | ICRA 2026 | "face trade-offs among fine-grained visual understanding, long-term context modeling and computational efficiency"（摘要） | 视觉语言导航，需外接 GPU |
| Fu 等 | Nature Communications 17:5857, 2026 | "its adaptation to environmental shifts is limited"（p.7） | 动物动作模仿 |
| QOED | RSS 2026 | "identifying nuisance parameters and accounting for their influence remains a significant gap"（p.2） | 信息论主动探索 |
| Lee 等 | Science Robotics 9(89), 2024 | "Existing approaches for hybrid locomotion build upon simple heuristics to decide when to step and when to drive"（p.1） | 轮足混合运动，无代码 |
| Skid-steer loaders | Science Robotics 11(120), 2026 | "we composed the overall behavior using hand-crafted switching conditions"（p.6） | 滑移转向车辆的学习控制 |
| Hao 等 | RICAI 2023 | "the tire longitudinal and lateral force are large"（摘要） | 腿姿辅助轮足转向 |
