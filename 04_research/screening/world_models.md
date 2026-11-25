# 粗筛：世界模型与模型驱动 RL（真实机器人应用）

日期：2026-11-24。性质：第一轮粗筛，只读摘要、方法/实验、README 与目录树，没有运行任何代码。已审查过的 SimDist、QWM、SADL、GRAM、ReLCE、DOMINO 等不重复报告（见 `review.CN.md` §3/§4/§8、`reviews/platform_and_benchmark_review.md` §3）。

文中"作者事实"指论文或仓库自述，"评价"是本次筛选者判断，"猜想"是未经验证的研究设想。

## 0. 结论速览

| # | 候选 | 状态 | 初评 |
|---|---|---|---|
| 1 | RWM-U（不确定性感知机器人世界模型 + MOPO-PPO，离线） | arXiv 预印本 v3（2026-01） | **A** |
| 2 | RWM（机器人世界模型 + MBPO-PPO，在线） | arXiv v5；NeurIPS 2025 workshop 海报 | B |
| 3 | DIAL-MPC（GPU 采样 MPC，Go2 实机） | ICRA 2025 | B |
| 4 | DayDreamer（真实机 A1 / UR5 / xArm 上的 Dreamer） | CoRL 2022 | B |
| 5 | TD-MPC2（潜空间 MPPI 世界模型，基础框架） | ICLR 2024 | B |
| 6 | Whole-Body MPPI（RTWholeBodyMPPI，Go1 实机） | ICRA 2025 | C |
| 7 | Dream-MPC（梯度式潜空间 MPC） | ICML 2026 录用 | C |
| 8 | DreamTIP（Dreamer + 任务不变属性，Go2 实机） | ICRA 2026 录用 | C |
| 9 | LLA-MPPI（仿真器库选择 + MPPI，Go2 实机） | 预印本 | C |
| 10 | PL-MPC（TD-MPC 改进，KUKA iiwa14 零样本） | 预印本 | C |
| 11 | Coupled Local/Global World Models（扩散世界模型 + 一阶梯度 RL） | CoRL 2026 录用 | C |
| 12 | Recipe：在线模仿预训练世界模型的操作 sim2real | 预印本 v2 | C |
| 13 | WMP（世界模型感知，A1 实机） | 见条目，状态待核 | C |
| 14 | 其他无码或不相关项（2403.01962、MPPI-DK、CLIS-MPPI、2603.04029） | 见 §3 | C |

核心发现：本方向没有任何一篇同时在腿足和机械臂上实机验证且代码完整的世界模型论文。可落地性最高的是 ETH 的 RWM/RWM-U 公开链（Isaac Lab + rsl_rl，动作为关节位置目标，策略不用特权信息，真实数据约 1 小时），但官方只发布了 ANYmal D 平面速度跟踪一个任务，且论文的机械臂实验仅在仿真。

## 1. 检索范围

- 工具：WebSearch（标准模式，约 16 次查询）、WebFetch 读取 arXiv 摘要页、arXiv HTML、项目页、ICML 页面；对关键仓库使用 `git clone --depth 1` 到临时目录读取提交、目录树和 README（未安装、未运行）。
- 查询主题：Robotic World Model / 神经模拟器；世界模型腿足 sim-to-real 与适应；学习动力学 + MPPI/GPU 采样 MPC（腿足与机械臂、UR 系列）；DreamerV3 / TD-MPC2 / DayDreamer 实机与仿真预训练 + 真实微调；轮足 + 世界模型；机械臂神经模拟器离线 MBRL；全身 MPPI；DIAL-MPC。
- 来源：arXiv、NeurIPS/ICML 虚拟站、作者项目页、GitHub。
- 日期：检索于 2026-11-24。
- 限制：搜索引擎偏向美国站点与 arXiv，没有系统遍历 CoRL/RSS/ICRA/IROS/RA-L 的 2025–2026 官方目录；没有查 Google Scholar 引用链。因此"没有双平台世界模型论文"是在本次检索范围内的结论，不是穷尽性结论。

## 2. 候选

### 2.1 RWM-U：不确定性感知机器人世界模型（A）

- 论文与链接：[Uncertainty-Aware Robotic World Model Makes Offline Model-Based RL Work on Real Robots](https://arxiv.org/abs/2504.16680)，Li、Krause、Hutter（ETH）。项目页 https://sites.google.com/view/uncertainty-aware-rwm
- 发表状态（作者事实）：arXiv 预印本，v3 修订于 2026-01-08；摘要页未列会议或期刊。本次未查到正式录用记录。
- 研究问题：只用离线数据（含少量真实数据）训练世界模型，再在模型想象中训练策略，如何避免策略利用模型误差。
- 方法与动作接口：自回归世界模型（RNN 集成，集成数 5）+ 认知不确定性惩罚 + MOPO-PPO。策略输出关节位置目标（ANYmal D 12 维）。
- 部署输入：策略观测为机体线/角速度、重力投影、速度指令、关节位置与速度、上一动作；不使用特权信息（接触、足高等仅作世界模型辅助输出）。机体线速度需要状态估计（真实实验用腿式里程计 + LiDAR 融合）。这一点对 Go2-W 要核实。
- 平台与实机：ANYmal D、Unitree G1 速度跟踪实机；Franka 到达任务仅在仿真。
- 公开材料（已打开核对）：
  - [leggedrobotics/robotic_world_model](https://github.com/leggedrobotics/robotic_world_model)，提交 `82147f9`（2026-10-29），65 个文件，MIT。含 Isaac Lab 扩展、在线预训练/微调环境、离线 `model_based/train.py`、可视化脚本。
  - 权重与数据：`assets/models/pretrain_rnn_ens.pt` 和一份 `state_action_data_0.csv`，资产目录共 31 MB。该数据只用作想象起点，不是论文的 1 小时真实数据集。
  - 只发布 ANYmal D 平面速度任务；没有 G1 配置，没有 Franka 任务，没有真实部署代码。
  - 依赖 [leggedrobotics/rsl_rl_rwm](https://github.com/leggedrobotics/rsl_rl_rwm)（提交 `18eebcd`，2026-01-10，含 `mbpo_ppo.py`、`system_dynamics.py`），需替换 Isaac Lab 自带 rsl_rl。
- 软件栈、算力与真实数据：README 标注 Isaac Sim 4.5.0、Isaac Lab 2.2.1、Python 3.10；rsl_rl_rwm 要求 torch>=2.6.0。论文用单张 RTX 4090（PyTorch 2.4.0、CUDA 12.6），世界模型约 1 小时，MOPO-PPO 为 4096 个想象环境、2500 迭代，未报总墙钟。真实数据约 20 万条转移、约 1 小时，由现有速度策略自动采集，最佳混合为 80 万仿真 + 20 万真实。
- 双平台相关性：Go2-W 腿 12 位置目标 + 4 轮速度目标，需要自行扩展世界模型输入输出和奖励；模型本身对观测/动作维数可配置（README 称可在 `SystemStateCfg` 等处配置）。UR7e 需要自己写 Isaac Lab 任务，论文只有仿真 Franka 到达，实机验证要自己完成。
- 作者承认的局限：策略质量受数据集限制；模型累积误差仍会损害泛化；真实数据缺少危险和信息量大的转移；真实性与多样性存在权衡。
- 评价：与项目约束最匹配的一条链：框架同 Isaac Lab 与 rsl_rl，与 Go2-W 的 robot_lab 链路技术栈接近；训练预算小；真实数据量小。风险是官方发布范围窄，Isaac Sim 4.5.0 对新架构 GPU 的支持未核实（本次未连服务器）。
- 猜想：(a) 把世界模型输入扩展为含轮速的混合动作并做 Go2-W 与 UR7e 的共享模型结构、分别训练；(b) 用世界模型不确定性在真实部署中判别分布外并触发数据采集或回退；(c) 把"仿真预训练 + 少量真实数据微调"对准具体的执行器/轮地接触差距。三者的新颖性均未查重。
- 初评 **A**：训练与数据预算小、栈与既有链路相近、关节位置接口直接；扣分点是只含一个 ANYmal 任务、预印本状态未定、机械臂无实机先例。

### 2.2 RWM：机器人世界模型（B）

- 论文与链接：[Robotic World Model: A Neural Network Simulator for Robust Policy Optimization in Robotics](https://arxiv.org/abs/2501.10100)，Li、Krause、Hutter。
- 发表状态：arXiv v5（2025-12-14）；NeurIPS 2025 页面显示为 workshop "Embodied World Models for Decision Making" 的海报，不是主会。arXiv 页未列录用信息。
- 问题与方法：学习长时程可预测的神经模拟器（双自回归 + 自监督），用 MBPO-PPO 在想象中训练策略，在线微调世界模型。
- 动作与输入：关节位置目标（ANYmal D 12 维，G1 29 维）；策略观测不含特权信息。
- 平台与实机：ANYmal D、G1 零样本实机；论文未给真实世界模型数据量，世界模型预训练用约 600 万仿真转移。
- 公开材料：与 2.1 同一仓库与提交（在线选项 `Finetune` 任务与 `rsl_rl_rwm` 中的 `mbpo_ppo.py`）。
- 算力：RTX 4090；RWM 预训练 50 分钟、MBPO-PPO 5 分钟、PPO 10 分钟（Table 1），附录又写世界模型约 1 小时，两处不一致。
- 双平台：同 2.1。
- 局限（作者）：弱于调优良好的高保真仿真无模型 RL；从零训练时策略利用模型误差，需要预训练；微调需额外环境交互；真实机在线学习风险高，平均失败超过 20 次，需要恢复策略。
- 评价：主要价值是作为 RWM-U 的前置模块；单独看，它依赖仿真做在线微调，对"用世界模型缩小真实差距"的贡献不如 RWM-U 直接。
- 初评 **B**：同一代码链，但状态为预印本 + workshop，主结论是"模型训练的策略不如调好的仿真 RL"，不构成独立基础论文。

### 2.3 DIAL-MPC：GPU 采样 MPC，Go2 实机（B）

- 论文：[Full-Order Sampling-Based MPC for Torque-Level Locomotion Control via Diffusion-Style Annealing](https://arxiv.org/abs/2409.15610)，Xue 等（CMU LeCAR）。
- 状态：ICRA 2025（据搜索结果与仓库自述；本次未核对官方录用目录）。
- 问题与方法：训练无关的全阶动力学采样 MPC，把 MPPI 看作单步扩散，加入扩散式退火；使用 MuJoCo MJX（JAX）做 GPU 并行 rollout。注意这里的"模型"是物理仿真器而不是学习得到的模型。
- 动作接口：配置中可选位置或力矩腿控制（`leg_control`）；部署经 `unitree_sdk2_python` / CycloneDDS 直接发低层指令。
- 部署输入：需要机体位姿/速度估计，内置 Vicon 与 ROS2 里程计插件，实验依赖外部定位。
- 平台与实机：Go2、H1 实机（跳跃、载荷）；仓库有 Allegro 手操作环境，没有机械臂实机。
- 公开材料（已核对）：[LeCAR-Lab/dial-mpc](https://github.com/LeCAR-Lab/dial-mpc)，提交 `871c84f`（2025-05-28），129 个文件，Apache-2.0；含 Go2/H1 的 MJX 模型 XML、仿真与实机部署脚本和示例配置。无训练权重概念。
- 软件栈与算力：Ubuntu >= 20.04、Python >= 3.10、CUDA >= 12.3（作者环境 CUDA 12.6）；实时运行需要机外 GPU 机器；真实数据需求为零，但需要精确的机器人 MJCF 与位姿源。
- 双平台：Go2 本体支持，Go2-W 没有现成模型（轮子需自建 MJCF 和接触）；UR7e 可用 MJCF 模型，需自写环境，实时性未知。
- 局限（作者）：未在本次读取的材料中逐条核实；依赖模型准确性与实时算力。
- 评价：这是"GPU 并行采样 MPC"方向里代码最完整的一例，但不是学习模型方法。
- 猜想：用世界模型/残差动力学代替或修正仿真器，在 Go2-W 与 UR7e 上做真实数据校正的采样 MPC。查重未做。
- 初评 **B**：栈新（CUDA 12.x，对新 GPU 友好），Go2 实机链完整；但不是世界模型方法，轮足与机械臂都需自建模型。

### 2.4 DayDreamer：真实机上的 Dreamer（B）

- 论文：[DayDreamer: World Models for Physical Robot Learning](https://arxiv.org/abs/2206.14176)，Wu 等。PMLR v205（CoRL 2022）。
- 问题与方法：不用仿真，直接在真实机上用 Dreamer（DreamerV2 系）在线学习，想象中训练 actor-critic。
- 平台：A1 四足约 1 小时从零学会翻身、站立、行走（摘要）；UR5 与 xArm 视觉抓放；Sphero 导航。
- 公开材料（已核对）：[danijar/daydreamer](https://github.com/danijar/daydreamer)，提交 `709016c`（2022-09-13），TensorFlow 2；README 有 A1、xArm、UR5 的 learner/actor 启动命令；`embodied/envs` 含 `a1.py`、`robot_interface.py`。机器人接口需要自己对接硬件，我没有看到 UR 的 RTDE 调用（仅 grep 未命中，不能断言没有）。
- 软件栈：TensorFlow 2，较旧；对 Blackwell 兼容性未核实。
- 双平台：它是本次检索中唯一同时有"腿式机 + UR5"真实机配置的世界模型代码；但是 A1 的 DayDreamer 动作为关节目标且依赖在线真实学习，Go2-W 轮足的安全与复位问题大；UR 任务是视觉抓放。
- 局限：论文自身为 2022 年工作；在线真实学习需要复位和人工监督。
- 评价：时间过久，不满足"2025–2026 为主"；但提供了真实机在线 MBRL 的流程参考。
- 初评 **B**：作为"双平台都有先例"的基线与对照来源，不适合作为创新基础。

### 2.5 TD-MPC2：潜空间 MPPI 世界模型（B）

- 论文与代码：[TD-MPC2](https://arxiv.org/abs/2310.16828)（ICLR 2024，未重新核对页面）；[nicklashansen/tdmpc2](https://github.com/nicklashansen/tdmpc2)，提交 `332f19e`（2026-10-02），492 个文件。
- 公开材料：训练与评估脚本、300+ 个检查点（DMControl、Meta-World、ManiSkill2、MyoSuite）、多任务数据集下载脚本、Docker。无实机代码。
- 方法：隐空间世界模型 + MPPI 规划；本次没有检索到官方实机示例。
- 评价：成熟的模型驱动框架，可作为想象/规划模块；腿足轮足与 UR7e 都需要自己做环境与实机。
- 初评 **B**：框架级，非"论文 + 实机"的整包。

### 2.6 Whole-Body MPPI（C）

- 论文与代码：Real-Time Whole-Body Control of Legged Robots with MPPI（[arXiv 2409.10469](https://arxiv.org/abs/2409.10469)），ICRA 2025（项目页自述）；[jrapudg/RTWholeBodyMPPI](https://github.com/jrapudg/RTWholeBodyMPPI)，提交 `55e6dc3`（2025-05-18），319 个文件，含 Go1 硬件接口、Docker、ROS 控制器、MuJoCo 模型。
- 方法：MuJoCo 作为 MPPI 的 rollout 模型，EKF 估计；Go1 推箱与爬箱。输出为关节目标轨迹。
- 评价：不是学习模型；只有 Go1 硬件，Go2/Go2-W 需移植。CPU 多线程为主。
- 初评 **C**：与 DIAL-MPC 同类但移植成本更高，无新信息。

### 2.7 Dream-MPC（C）

- 论文：[Dream-MPC: Gradient-Based MPC with Latent Imagination](https://arxiv.org/abs/2605.04568)，Spieler、Behnke；ICML 2026 录用（ICML 虚拟站海报页）。
- 代码（已核对）：[jspieler/dream-mpc](https://github.com/jspieler/dream-mpc)，提交 `8e68f7b`（2026-08-21），69 个文件，含 TD-MPC2/BMPC 集成、Docker、下载预训练 TD-MPC2 模型脚本。
- 范围：DMControl、Meta-World、HumanoidBench 24 个任务，仅仿真；无实机。
- 评价：规划器改进模块，可用于"世界模型 + 少量采样"的实时性问题；与项目的实机约束距离远。
- 初评 **C**。

### 2.8 DreamTIP（C）

- 论文：[Learning Task-Invariant Properties via Dreamer](https://arxiv.org/abs/2604.02911)，Liang 等；ICRA 2026 录用（arXiv 评论字段）。
- 内容：LLM 提出任务不变属性作为世界模型辅助目标，混合重放缓冲 + 正则化做真实适应；Go2 爬台阶实机 10% 到 100%。
- 公开材料：摘要页与搜索均未找到代码或项目页；真实数据量未在摘要给出。
- 评价：问题与 Go2 直接相关，但无代码，无法复现。仅作查重对象。
- 初评 **C**。

### 2.9 LLA-MPPI（C）

- [arXiv 2610.10465](https://arxiv.org/abs/2610.10465)（预印本，2026-10-07），Jung 等（CMU）：从 GPU 批量接触仿真器库中依窗口预测误差选模型，再用 MPPI；Go2 实机（载荷、断腿、推箱）。
- 项目页写 "coming soon"，没有仓库。不使用学习模型。
- 初评 **C**：与项目问题（运行中动力学变化）接近，但没有代码；仅作查重。

### 2.10 PL-MPC（C）

- [arXiv 2609.39751](https://arxiv.org/abs/2609.39751)（预印本 v1，2026-09-30）：TD-MPC 改进（混合多步 TD、基于分歧的终端价值、回报加权蒸馏）。HumanoidBench/DMControl 仿真，KUKA iiwa14 螺母对准零样本 sim2real。代码写"将发布"，未见仓库。
- 初评 **C**。

### 2.11 Coupled Local and Global World Models（C）

- [arXiv 2602.06219](https://arxiv.org/abs/2602.06219)，CoRL 2026 录用（v3，2026-10-11）：扩散世界模型 + 局部潜在代理做一阶梯度 RL；Push-T 与四足自我中心操作。
- 项目页有，仓库未见；规模和算力偏大。
- 初评 **C**。

### 2.12 Recipe：在线模仿预训练世界模型的操作 sim2real（C）

- [arXiv 2510.02538](https://arxiv.org/abs/2510.02538)，Wang 等（v2 2026-09-18），无录用信息；仿真在线模仿预训练 + 少量真实演示离线微调，sim2real 成功率提升至少 23.3%（摘要）。
- 无代码，机器人型号摘要页未给。
- 初评 **C**。

### 2.13 WMP（C）

- World Model-based Perception for Visual Legged Locomotion（[arXiv 2409.16784](https://arxiv.org/abs/2409.16784)）；发表状态本次未核实。
- [bytedance/WMP](https://github.com/bytedance/WMP)，提交 `c232c11`（2024-12-18），68 个文件，含 A1 AMP 配置与 dreamerv3-torch。
- 依赖 Isaac Gym Preview 3、torch cu117、Python 3.8，训练约 23 GB 显存；对新 GPU 与 Go2-W 都是旧栈。感知用深度输入，与本项目盲走输入不同。
- 初评 **C**。

## 3. 其他检出但未列为候选

- [2403.01962](https://arxiv.org/abs/2403.01962)：ICRA 2024，可微世界模型 + VAE 策略，真实机 2 分钟数据；未找到代码。
- [MPPI-DK 2603.05385](https://arxiv.org/abs/2603.05385)：Koopman 学习模型 + MPPI，四足实机；预印本，无代码。
- [CLIS-MPPI 2610.21239](https://arxiv.org/abs/2610.21239)：CDC 2026 录用，UR5e 实机 MPPI（关节速度，ROS）。摘要未说明学习动力学，无代码。可作 UR 侧 MPPI 实机先例。
- [2603.04029](https://arxiv.org/abs/2603.04029)：DreamerV3 在线持续 RL，用世界模型预测误差触发微调；已提交 IROS 2026（未录用）；仿真四足 + 小车；无代码。
- Hansen 等 Finetuning Offline World Models in the Real World（2310.16029，较早，只有搜索摘要，未核对代码）。

## 4. 未覆盖或存疑

1. 没有查到同时在腿足（或轮足）与机械臂上做真实实验的世界模型论文，且代码完整。若成立，则双平台实机要靠自己把同一方法移植到两个平台。
2. RWM-U 正式发表状态未确认；"代码待录用后发布"的论文文字与仓库已存在不一致，说明论文文字滞后。需要查 ETH 项目页或后续版本。
3. RWM/RWM-U 官方只含 ANYmal D 平面速度；G1 与 Franka 配置未公开。论文中 G1 与 Franka 结果不能当作可复现。
4. Isaac Sim 4.5.0 / Isaac Lab 2.2.1 在 RTX PRO 5000（若为 Blackwell）上是否可用没有核实；DIAL-MPC 的 JAX 栈与 TD-MPC2 的 PyTorch 栈同样未在目标 GPU 上验证。
5. DIAL-MPC 的论文局限、各实机实验的细节只读了 README，没有读论文正文。
6. TD-MPC2 的 ICLR 2024 状态、WMP 的发表状态、DIAL-MPC 与 Whole-Body MPPI 的 ICRA 2025 录用，都来自搜索摘要或作者页，未去官方目录核对。
7. 没有覆盖：CoRL/RSS 2025–2026 官方目录里可能存在的更多世界模型论文、Science Robotics、T-RO、RA-L 正式刊文；WMP 以外的视觉世界模型、人形世界模型。
8. 轮足（Go2-W 类）加世界模型的工作只检到 WAVE-Go（导航，未读正文）和 ATRos（无世界模型），没有可用结论。
9. 所有"训练算力"都来自论文自述，没有在本地复现。
