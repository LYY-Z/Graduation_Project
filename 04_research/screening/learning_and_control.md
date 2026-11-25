# 粗筛：学习与控制结合方向

日期：2026-11-24。粗筛，不是精读。除 DIAL-MPC、CBF-RL、AugMPC、mpc-rl 外，作者研究内容只读了 arXiv 摘要页，没有读方法和实验正文；"与传统控制的对照"一栏因此多数写"未核实"。

## 1. 检索范围

- **来源**：WebSearch（约 16 条查询）、arXiv 摘要页（WebFetch）、GitHub API（`api.github.com`，取 `pushed_at`、许可证、最近提交、根目录）、仓库 README。
- **查询主题**：DIAL-MPC 与 GPU 采样 MPC；采样 MPC 加学习先验或价值函数；RL 加 MPC 分层或残差；CBF/HJ 安全滤波/约束 RL 的腿足与机械臂实机；残差 RL 加经典控制器（阻抗、OSC）；PD 增益/刚度学习；学习型扰动观测器；元学习自适应控制；学习动力学加 MPPI；Go2-W 加 MPC/RL；L4DC 2026 录用。
- **已排除（review.CN.md §3、§4、§8 已审查）**：UARL、OSCAR、OCCAM、TARC、TAM、GRAM、ReLCE、DOMINO、Stability-Aligned Residual Adaptation（arXiv 2603.07775）、CAPABLE。
- **检索缺口**：
  - 没有拿到 L4DC 2026、CDC 2025、TAC、Science Robotics、NeurIPS/ICLR/ICML 2026 的录用目录，这些会议的相关论文基本没覆盖。
  - 没有找到同时在腿足和机械臂上做实机的单篇方法，下文"双平台相关性"逐篇说明。
  - 可微控制、学习特征的自适应控制（Neural-Fly 类）、学习型扰动观测器在腿足/机械臂上的 2025–2026 正式发表工作，本轮几乎没有命中，只有 OMAC（NeurIPS 2021）和一篇无代码的机械臂预印本。
  - WebSearch 为 US 地区，对 IEEE Xplore 收录状态的判断多靠 arXiv 评论字段，"正式发表"处已标明依据。

## 2. 总览

| # | 论文 | 状态 | 代码 | 初评 |
|---|---|---|---|---|
| 1 | DIAL-MPC | ICRA 2025 正式发表（Best Paper Finalist） | 有，Go2 实机链 | A（条件） |
| 2 | CaT 约束即终止 | IROS 2024 | 有，MIT | B（偏 A） |
| 3 | AugMPC / RL-Augmented MPC | RA-L 2026（DOI 已给出，arXiv 页未写录用） | 有，GPL-2.0 | B |
| 4 | Residual MPC | TRO 投稿预印本 | 未找到 | B |
| 5 | MPC-RL（π^n MPC） | 预印本 | 有，MIT | B |
| 6 | ProxPI | 预印本 | 无 | B |
| 7 | Stability-aware Residual RL（机械臂扰动补偿） | 预印本 | 无 | B |
| 8 | CBF-RL | ICRA 2026 录用 | 仅 2D 导航 demo | B |
| 9 | Safe Whole-Body Loco-Manipulation（Go2 加臂） | ICRA 2026 录用 | 无 | B |
| 10 | Reference-Free Sampling MPC | ICRA 2026 录用 | 无 | B |
| 11 | Racing a Wheeled Quadruped（Go2-W） | AVEC 2026 录用 | 仅高层 MPC 仿真 | C（但对 Go2-W 有参照价值） |
| 12 | Adaptive Legged Locomotion via Online Learning for MPC | RA-L（arXiv 页标注，录用状态未核） | 无 | C |
| 13 | Shield-Loco | 预印本 | 无 | C |
| 14 | UR5e 数据驱动无模型 CBF | IROS 2025 投稿稿 | 无 | C |
| 15 | TD-MPC2（代表性早期） | ICLR 2024 | 有，MIT，仍在更新 | B |
| 16 | ABS / One Filter / Variable Stiffness（代表性早期） | RSS 2024 / 预印本 / IFAC 2025 | ABS 有；其余未见 | C |

整体判断：本方向没有"腿足和机械臂都有公开实机链"的论文。采样 MPC 和 RL+MPC 在腿足上有公开代码，机械臂侧的实机工作多无代码。

## 3. 候选逐篇卡片

### 3.1 DIAL-MPC：Full-Order Sampling-Based MPC for Torque-Level Locomotion Control via Diffusion-Style Annealing

- **链接**：[arXiv 2409.15610](https://arxiv.org/abs/2409.15610) · [代码](https://github.com/LeCAR-Lab/dial-mpc) · [项目页](https://lecar-lab.github.io/dial-mpc)
- **发表状态**：ICRA 2025 正式发表，README 写 Best Paper Finalist。
- **作者研究的问题**：不训练、直接优化全阶动力学，实现腿足全阶力矩级 MPC。
- **方法类别与动作接口**：无学习的 GPU 采样 MPC（MPPI 加扩散式退火）。输出为关节位置目标，经 PD 转力矩；论文称力矩级。
- **部署输入**：关节状态加外部定位给出的基座位置和速度（README 明确"需要外部定位模块"）。不使用学习特权信息。
- **实验平台**：Go2 实机（跳跃等），仿真含 H1。
- **公开材料**：提交 `871c84f`（2025-05-28），Apache-2.0，约 1000 star。实际目录：`dial_mpc/{envs,deploy,core,examples,config}`，`envs` 含 `unitree_go2_env.py`、`unitree_h1_env.py`、`manipulation.py`（Allegro 手示例，不是机械臂）。`deploy` 含 `dial_plan.py`、`dial_real.py`、`dial_sim.py`、`localization`。未见训练权重，因为无训练。
- **软件栈与计算**：JAX，Brax/MJX，Ubuntu 22.04、Python 3.10、CUDA 12.6，README 建议 CUDA 不低于 12.3。无训练；部署端需 GPU 在线采样。论文称 Go2 达 50 Hz（来自检索摘要）；仓库 issue 有"GO2 deployment instability at 20 Hz on RTX 3090"，说明实机实时性受 GPU 影响。
- **与传统控制对照**：未核实正文。检索摘要只说明它和 RL 对比 [未核实]。
- **双平台相关性**：Go2 有现成链路；Go2-W 的轮子没有模型，需自行扩 MJX 模型和轮速接口。UR7e 没有现成任务，但 Hydrax（[vincekurtz/hydrax](https://github.com/vincekurtz/hydrax)，MIT，提交 `bd53d43` 2026-07-18，已内置 DIAL 算法，要求 CUDA 13）可用同一类 MPC 做机械臂；其示例是 pusht 等，未见 UR。
- **作者承认的局限**：README 称是 proof-of-concept，需外部定位；其余局限未读正文，未核实。
- **评价**：公开实机链是本方向里最完整的，GPU 采样 MPC 部署风险集中在实时性和状态估计。
- **猜想（创新空间）**：学习先验或价值函数接入采样 MPC，但 ProxPI（预印本）、TD-CD-MPPI（RA-L 2026）、SGPS（预印本）、Residual MPC 已占住若干组合，查重必须做。
- **初评 A（条件）**：有代码、有 Go2 实机、训练预算几乎为零。条件：有动捕或可靠里程计；愿意自行适配轮足与 UR7e。

### 3.2 CaT：Constraints as Terminations for Legged Locomotion Reinforcement Learning

- **链接**：[arXiv 2403.18765](https://arxiv.org/abs/2403.18765) · [代码](https://github.com/gepetto/constraints-as-terminations) · [项目页](https://constraints-as-terminations.github.io)
- **状态**：IROS 2024（项目页）。早期工作。
- **问题**：腿足 RL 中约束与奖励难以平衡。
- **方法**：约束违反转为随机终止概率，几乎不改 PPO。属约束 RL 的低成本做法，动作接口沿用原策略。
- **部署输入**：Solo-12 盲策略，仿真训练时用高度图，实机用动捕重建（项目页）。
- **实机**：Solo-12。
- **公开材料**：MIT，最近推送 2025-09-01。根目录 `exts`、`scripts`、`docker`、`assets`、`pyproject.toml`。未核实是否为 Isaac Lab 以及具体版本。
- **与传统控制对照**：未核实；本身是训练算法，不是控制器替代。
- **双平台相关性**：算法层不依赖形态，约束作为终止条件原则上可迁移到机械臂（猜想），但作者只做了腿足。
- **局限**：未核实。
- **猜想**：把"约束终止"换成 CBF 或不确定性触发的约束，或做自适应约束阈值。
- **初评 B（偏 A）**：代码许可友好，改动小，利于两个平台各自复现；但创新性在 2024 年已发表，且与控制理论结合较浅。

### 3.3 RL-Augmented MPC for Non-Gaited Legged and Hybrid Locomotion（AugMPC）

- **链接**：[arXiv 2603.10878](https://arxiv.org/abs/2603.10878) · [代码](https://github.com/AndrePatri/AugMPC)
- **状态**：DOI 10.1109/LRA.2026.3675839（RA-L 2026），arXiv 页无评论字段；README 的引用已写 RA-L。
- **问题**：MPC 需要预设步态，RL 负责决定接触时序。
- **方法**：高层 RL（SAC 为默认，PPO 可选）输出接触计划和 twist 指令，低层全刚体 MPC 执行。
- **部署输入**：MPC 状态加高度图（崎岖地形）。
- **平台**：仿真含 50–120 kg 多种有轮和无轮机器人（README 展示 B2W）；实机仅 Centauro（120 kg 轮足人形）。
- **公开材料**：提交 `d695aee`（2026-07-18），GPL-2.0，分支 `ibrido`。`aug_mpc/` 含 `training_envs`、`world_interfaces`、`controllers`、`agents`、`training_algs`；环境与世界接口在另一仓库 AugMPCEnvs，模型在 HuggingFace。文档中"扩展新控制器/新环境"章节仍是 TBD。
- **软件栈与计算**：Isaac Sim、xbot2、Horizon MPC、EigenIPC 共享内存；推荐用 ibrido-containers。README 称 Threadripper 7970 加 RTX 4090 上 800 个并行 MPC 环境，约 6 小时收敛（作者数据，我们未复现）。需要多核 CPU。
- **传统控制对照**：摘要未提基线，未核实。
- **双平台相关性**：对 Go2-W 轮足混合有直接参考；机械臂无。
- **局限**：未核实。
- **评价**：分层 RL+MPC 且含轮足，最贴近 Go2-W，但栈很重，MPC 并行依赖 CPU，GPL 许可约束衍生分发。
- **猜想**：可以只借接口思想，用 Go2-W 的简化车辆模型替代全刚体 MPC。
- **初评 B**：方向对口，复现栈和 CPU 需求偏重。

### 3.4 Residual MPC：Blending RL with GPU-Parallelized MPC

- **链接**：[arXiv 2510.12717](https://arxiv.org/abs/2510.12717)
- **状态**：预印本（评论写 TRO submission，未见录用）。仅 v1。
- **问题**：把 MPC 放进 RL 训练环路，训练太慢。
- **方法**：运动学-动力学全身 MPC 以 100 Hz 在 GPU 上并行，RL 学残差，在力矩层按系数混合。
- **平台、实机**：摘要未指明机器人，未写是否实机。
- **代码**：arXiv 页无；未另行搜索 GitHub，未找到。
- **对照**：摘要称优于纯 MPC 和纯 RL（样本效率、速度范围、零样本适应）；条件待读正文。二手摘要称训练约比端到端 RL 慢 8 倍（未核对原文）。
- **双平台相关性**：腿足；机械臂无。
- **评价**：这是"残差 RL 加经典控制器"最直接的近邻，也是查重对象。
- **初评 B**：方法最对口，但无公开代码、实机不明。

### 3.5 MPC-RL（π^n MPC，Accelerating and Scaling MPC-Guided RL）

- **链接**：[arXiv 2606.05687](https://arxiv.org/abs/2606.05687) · [代码](https://github.com/junhengl/mpc-rl)
- **状态**：预印本（8 页，无录用信息）。
- **问题**：MPC 引导 RL 训练中，批量 MPC 求解太贵。
- **方法**：质心 QP-MPC 的最优计划作为奖励塑形和评论家信息；训练时用，部署时是纯策略（据 README，策略学习跟踪 MPC 计划）。批量 GPU 求解器 π^n MPC（JAX 和 PyTorch）。
- **平台**：人形 Themis，含推箱子；摘要写有硬件验证。
- **公开材料**：提交 `97e3764`（2026-06-10），MIT。仅含训练环境、MPC、批量求解器；任务只有 Themis 的行走和推箱 2 个；mjlab（MuJoCo-Warp、rsl_rl），Python 3.11–3.13，CUDA 12，4096 环境训练 15000 到 25000 迭代。未见权重。
- **对照**：未核实。
- **双平台相关性**：质心模型与人形接触调度绑定，迁移到 Go2-W 要重写 MPC，到 UR7e 不适用。
- **评价**：训练时 MPC 引导加部署零 MPC 的思路可借鉴，但不是现成底座。
- **初评 B**：栈现代（mjlab）、单卡可训，但机器人绑定。

### 3.6 ProxPI：Proximal Prior Injection for Sampling-Based MPC under Learned-Prior Mismatch

- **链接**：[arXiv 2609.00941](https://arxiv.org/abs/2609.00941)
- **状态**：预印本，2026-09-01，仅 v1，12 页。
- **问题**：策略引导的 MPPI 在策略失配（分布外）时性能下降。
- **方法**：保持以名义值为中心的采样，把策略作为软邻近代价；分布内与现有方法持平，策略不准时能回到普通 MPPI 水平。
- **平台**：arXiv 页只说"仿真和实机"；检索摘要称用到 Go2、G1 和 FR3（用 ACT 策略作先验），**arXiv 页未确认，需读正文**。
- **代码**：未找到。
- **对照**：和策略中心热启动 MPPI、普通 MPPI 对比（摘要）。
- **评价**：同时涉及腿足和机械臂，与我们的方向最像，也是 DIAL-MPC 加学习先验这条创新线的直接查重对象。
- **初评 B**：无代码，需联系作者或自行实现；价值在"先验失配时保持下限"这一对传统方法公平的叙述。

### 3.7 Stability-aware Residual RL Framework for Robotic Manipulator Disturbance Compensation

- **链接**：[arXiv 2609.21307](https://arxiv.org/abs/2609.21307)
- **状态**：预印本，2026-09-18，14 页，仅 v1。
- **问题**：机械臂扰动补偿，需要稳定性保证。
- **方法**：解析扰动观测器加残差 RL；估计网络对齐历史与特权扰动上下文；由 ISS 分析给出状态相关动作界。
- **平台**：6 自由度机械臂，仿真加实机，型号页面未写；检索摘要称在 Isaac Lab 训练。实机追踪误差降 27.8%，未见扰动（基座振动）降 38.0%（作者数据）。
- **代码**：无。
- **对照**：摘要说优于常规控制器和扰动观测器，具体基线未核实。
- **双平台相关性**：机械臂强，腿足无。与已审查的 Stability-Aligned Residual Adaptation 属同一类，必须查重。
- **初评 B**：对 UR7e 侧是很好的参照，无代码，创新空间被前述工作挤占。

### 3.8 CBF-RL：Safety Filtering RL in Training with Control Barrier Functions

- **链接**：[arXiv 2510.14959](https://arxiv.org/abs/2510.14959) · [代码](https://github.com/lzyang2000/cbf-rl-demo)
- **状态**：ICRA 2026 录用（arXiv v6，2026-06-22）。
- **问题**：训练时引入 CBF 过滤和奖励项，让策略内化安全，部署时不需要在线滤波。
- **方法**：CBF 动作过滤加 CBF 奖励惩罚；PPO 一类。
- **平台**：导航任务和 G1 人形实机（避障和上楼梯）。
- **公开材料**：仓库已更名为 `cbf-rl-demo`，最近提交 `68955c8`（2026-03-13），无许可证。README 明确是机器人导航 demo，使用 rsl_rl 和类 IsaacGym 的向量化环境，含 naive、CBF、filter-only、reward-only 的训练脚本。**没有 G1 的训练与部署代码。**
- **对照**：作者对比 naive、filter-only、reward-only 消融；与 PID/LQR/MPC 对照未见。
- **双平台相关性**：算法形态无关，可用于 Go2-W 速度指令层和 UR7e 工作空间约束；但需要自己写 CBF（障碍与动力学模型）。
- **猜想**：对机械臂用关节限位/自碰撞 CBF，对轮足用速度/障碍 CBF，两平台共用同一"训练内化"框架。
- **初评 B**：思想轻、可迁移；官方代码只覆盖玩具环境。

### 3.9 Safe Whole-Body Loco-Manipulation via Combined Model and Learning-based Control

- **链接**：[arXiv 2603.02443](https://arxiv.org/abs/2603.02443)
- **状态**：ICRA 2026 录用。
- **问题**：腿足加机械臂的全身交互安全。
- **方法**：臂用模型导纳控制，腿用 RL 策略；Reference Governor 提供安全保证；神经网络增强的卡尔曼滤波估计基座速度。
- **平台**：Go2 加 6 自由度臂和腕部六维力传感器，实机。
- **代码**：无。
- **评价**：同一平台既有学习腿策略又有经典导纳臂，是少见的"经典控制和学习分工"，对双平台叙述有用；但臂不是 UR。
- **初评 B**：无代码；可作 Go2 上经典加学习分层的设计参照。

### 3.10 Reference-Free Sampling-Based MPC

- **链接**：[arXiv 2511.19204](https://arxiv.org/abs/2511.19204)
- **状态**：ICRA 2026 录用（v3，2026-04-16）。
- **方法**：MPPI 加三次 Hermite 样条参数化，CPU 实时，Go2 实机跑出小跑、跳跃，无参考无预训练。
- **代码**：arXiv 页无；未找到。
- **评价**：与 DIAL-MPC 同类，CPU 即可。检索摘要称含终端价值函数近似，arXiv 页未提，未核实。
- **初评 B**：无代码，仅作对照与查重。

### 3.11 Racing a Wheeled Quadruped: Active Load Transfer Mitigation via MPC

- **链接**：[arXiv 2606.26313](https://arxiv.org/abs/2606.26313) · [代码](https://github.com/meisman-ucb/go2w-roll-control-mpc)
- **状态**：AVEC 2026 录用（arXiv 评论）。
- **方法**：三层——离线赛道线、在线自行车模型 MPC（最小化横向载荷转移比）、底层全身 RL 策略（16 个执行器）。
- **平台**：**Go2-W 实机**，报告平均载荷转移比降低最高 44%，最快圈速提升 8.7%（作者数据）。
- **公开材料**：提交 `bcf7914`（2026-09-08），无许可证，9 star。只有高层 MPC 和仿真（`mpc.py`、`simulate.py`、`generate_raceline.py`、`config.py`），**没有 RL 策略或部署代码**。
- **评价**：证明 Go2-W 上 MPC+RL 分层可行，且指令接口（加速度、横滚和俯仰力矩）清晰；但应用面窄，不能作底座。
- **初评 C**：只作 Go2-W 先例参考。

### 3.12 Adaptive Legged Locomotion via Online Learning for MPC

- **链接**：[arXiv 2510.15626](https://arxiv.org/abs/2510.15626)
- **状态**：arXiv 页标注为 IEEE RA-L 论文，具体录用状态未核实；v2 2025-11-30。
- **方法**：MPC 加随机傅里叶特征在线最小二乘残差动力学，声称次线性动态后悔界（理论是亮点）。
- **平台**：Gazebo 和 MuJoCo 仿真四足；**无实机**。
- **代码**：无。
- **评价**：属"学习特征的自适应控制"，有理论，对传统控制公平性最好；缺实机和代码。
- **初评 C**：理论参照。

### 3.13 Shield-Loco：Shielding Locomotion Policies with Predictive Safety Filtering

- **链接**：[arXiv 2606.07193](https://arxiv.org/abs/2606.07193)
- **状态**：预印本，仅 v1。
- **方法**：采样优化修改喂给 RL 策略的落足点，完整物理模型加学习价值函数；四足实机，机型页面未写。
- **代码**：无。
- **初评 C**：对 Go2-W 不对口（落足点接口）。

### 3.14 Towards Data-Driven Model-Free Safety-Critical Control（UR5e）

- **链接**：[arXiv 2506.06931](https://arxiv.org/abs/2506.06931)
- **状态**：评论写"submitted to IROS 2025"，录用未核实。
- **方法**：神经网络学习 Lyapunov 函数，估计内置速度控制器的衰减率，得到无模型 CBF 安全条件（Chernoff 界）。
- **平台**：**UR5e 实机**，速度接口，与 UR7e 接口一致。
- **代码**：无。基线未核实。
- **初评 C**：不是 RL，但是少数确认 UR 系机械臂加 CBF 加实机的工作，可作 UR7e 速度层安全滤波的接口参照。

### 3.15 TD-MPC2：Scalable, Robust World Models for Continuous Control（代表性早期）

- **链接**：[arXiv 2310.16828](https://arxiv.org/abs/2310.16828) · [代码](https://github.com/nicklashansen/tdmpc2)
- **状态**：ICLR 2024 正式发表。
- **方法**：潜空间世界模型加 MPPI 规划，含操作和运动任务，多任务。
- **公开材料**：MIT，提交 `332f19e`（2026-10-02），推送 2026-10-20，仍在维护。目录 `tdmpc2/{envs,trainer,config.yaml,evaluate.py}`、`docker`、`datasets`。
- **实机**：原论文仿真。检索显示 arXiv 2610.14564 在 Go2 上使用了 TD-MPC2 架构作基线，规划是否上机未核实。
- **双平台相关性**：算法接口无关，必须各自搭仿真；与 SimDist 等世界模型方向有重叠，应由世界模型方向的筛选覆盖。
- **初评 B**。

### 3.16 其他代表性早期

- **ABS（RSS 2024）**：[代码](https://github.com/LeCAR-Lab/ABS)，提交 `9b95329`（2024-07-11），CC BY-NC 4.0，仅 Go1 EDU，Isaac Gym Preview 4、Python 3.8、ROS Noetic、Orin NX，README 声明只针对自己的硬件；含 PPO-Lagrangian 变体和到达-规避网络。无 Go2 移植，栈过旧。**C。**
- **One Filter to Deploy Them All（HJ 可达性安全滤波，Go1）**：[arXiv 2412.09989](https://arxiv.org/abs/2412.09989)，预印本，只有项目页，未见代码仓库。**C。**
- **Variable Stiffness for Robust Locomotion through RL**：[arXiv 2502.09436](https://arxiv.org/abs/2502.09436)，IFAC ROBOTICS 2025；策略同时输出关节刚度和目标位置，仅平地训练。检索未找到代码。**C。**
- **GainAdaptor**：[arXiv 2412.09520](https://arxiv.org/abs/2412.09520)，预印本，Go1，学习 PD 增益；未见代码。**C。**
- **OMAC（NeurIPS 2021）**：学习共享表示的在线元自适应控制，有非渐近保证，只有倒立摆和无人机实验；无腿足/机械臂。**不入选，仅作理论参照。**

## 4. 未覆盖或存疑

1. **可微控制**：本轮没有命中可作候选的 2025–2026 工作，需单独查（如可微仿真加 MPC、DiffTune 类）。
2. **机械臂 + 学习 + 经典控制的有代码实机工作**：没找到与 UR 直接对口的公开代码；ISS 残差（#7）、UR5e CBF（#14）都无代码。需要时先去 Isaac Lab 的 OSC/阻抗控制器与 rsl_rl 自己搭。
3. **学习特征的自适应控制、学习型扰动观测器**：只有 #7 和 #12，均无代码。
4. **Go2-W 实机上能不能传关节位置目标和轮速目标，以及 DIAL-MPC 类方法在 Go2-W 的频率**：本轮没验证，STATUS 已列为待核对。
5. **各论文与 PID/LQR/MPC 的对照**：多数只读了摘要，没读正文，"优势成立条件"没有记录；进入精读时优先补 DIAL-MPC、Residual MPC、ProxPI、CBF-RL 四篇。
6. **DIAL-MPC 的 50 Hz 说法**来自检索摘要而非论文正文，仓库 issue 显示 20 Hz 下有不稳定报告，需实测。
7. **未进入本表的 WebSearch 命中**：MPPI-DK（arXiv 2603.05385）、STRIDE（2603.08478，无代码）、Lagrangian 网络 RL-MPC（2603.14333，Go1 实机，无代码）、TD-CD-MPPI（RA-L 2026，Solo12）、FDM（RSS 2025，[代码](https://github.com/leggedrobotics/fdm)，提交 `06f5d80`，ANYmal 导航）、SGPS（2609.20575，Go2 实机，无代码）。其中 SGPS 与 FDM 更接近其他方向，若需要可补卡片。
8. **关于这些预印本日期**：2026-09 的 arXiv 编号来自检索页面，已通过摘要页确认提交日期。

## 5. 一句话建议（评价，非事实）

- 若走"采样 MPC 加学习先验"：DIAL-MPC 是最现实的公开底座，但 ProxPI、TD-CD-MPPI、SGPS、Residual MPC 已占住主要组合，创新点要放在两平台共用的接口或对传统方法的公平对比上。
- 若走"安全约束"：CaT 或 CBF-RL 的思想可跨平台，官方代码都偏小，要自己写两平台任务。
- 若走"残差/增益调度"：UR7e 侧有 #7，Go2-W 侧有 #4，但都无代码，优先级低于有代码的路线。
