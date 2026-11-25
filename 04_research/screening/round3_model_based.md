# 第三轮检索：基于模型 / 世界模型 / sim-to-real 在线适应 / 系统辨识 / 学习+MPC / 可微仿真 / 残差学习

核查日期：2026-11-24。范围：本方向论文，方法可迁到 Go2-W 即可。只读了 arXiv 摘要页、PMLR/RSS 页面、GitHub API（提交、目录树、README），未安装、未运行、未读全文。标记：**【事实】** 来自所见页面；**【评价】** 本次判断；**【未核实】** 没有查到。

检索渠道的限制（影响可信度）：检索工具只返回搜索摘要和页面片段，没有系统遍历 CoRL/RSS/ICRA/NeurIPS 2026 论文集；"无代码"指 arXiv 页与项目页没有给出仓库，**不等于确实没有**。已排除重复：SimDist、LocoWM、RWM-U、PACE、SPI-Active、DIAL-MPC、MoE-CTS、GRAM、CaT、LocoFormer、具身尺度律、Multi-Loco，以及此前粗筛已列出的 Rapid Embodiment Adaptation(2608.01506)、SLowRL(2603.17092)、MPPI-DK、Racing a Wheeled Quadruped(2606.26313)、ASAP/UAN/Actuator Reality Shaping 等只作"最接近工作"引用。

评分口径：V、I 越高越好；R、D 5=最难。

## 1. 主表

| # | 论文 / 出处 | V | I | R | D | 创新设想（Go2-W 实机可验证） | 最接近工作 | 3–4 个月判断 |
|---|---|---|---|---|---|---|---|---|
| 1 | **TEMPO：Efficient Test-Time Adaptation For Robot Policies**（Alfarra、Mazzaglia、Peschl、Dijkman、Louizos；arXiv 2610.20318，2026-10-14）。NeurIPS 2026 poster（NeurIPS 页与 arXiv 评论栏写录用；页面未标明是否主会场） | 4 | 4 | 2 | 3 | 在冻结 critic + 熵正则 + 难样本记忆的测试时策略更新框架上，加"通道分组更新"：只更新轮速通道或最后一层/LoRA，并用轮滑移、电机温度或扭矩余量作为约束，在 Go2-W 上做载荷/地面摩擦突变的机载在线适应。实机指标：突变后恢复时间、速度跟踪误差、不摔倒率 | TEMPO 本身（Go1/Go2/G1，MuJoCo Playground，Go2 小腿加载荷实机）；SLowRL（2603.17092，LoRA 实机微调 Go2）；LocoFormer（上下文适应，不更新权重）；GRAM、历史编码类（RMA 系） | **可完成。** 方法简单，可在 robot_lab 的 rsl_rl 上自行实现；风险在于论文只与"actor-only 冻结 critic"一个基线比、实机只有一个负载场景，创新点要在 Go2-W 上自己立基线 |
| 2 | **ASAP：Aligning Simulation and Real-World Physics**（He、Shi 等，CMU/NVIDIA；RSS 2025，roboticsproceedings.org/rss21/p066，DOI 10.15607/RSS.2025.XXI.066）。仓库 LeCAR-Lab/ASAP，MIT，2147 星，最近提交 `df5320c`（2026-01-06） | 5 | 3 | 3 | 2 | 把"真机轨迹→残差 delta-action 模型→在仿真中微调策略"迁到 Go2-W：delta 模型输入加轮速通道与电机温度/电池电压，作为轮足的"执行器残差"；真机数据只需 Go2-W 的 lowstate 日志，无动捕 | ASAP 本身（G1 人形）；PACE（参数式辨识）；UAN、Actuator Reality Shaping、Dao & Fern（#4）；SPI-Active | **可完成。** 只取 delta 模型部分（`humanoidverse/agents/delta_dynamics/`、`delta_a/`），不需要运动重定向流水线。主要工作是移植到 Isaac Lab 5.x 并采集 Go2-W 日志。问题：与 PACE/UAN 的差异要靠"轮通道 + 温度条件"来立，需防止被看作"换平台" |
| 3 | **RL-Augmented MPC for Non-Gaited Legged and Hybrid Locomotion（AugMPC）**（Patrizi 等，IIT；arXiv 2603.10878，2026-03-11；DOI 10.1109/LRA.2026.3675839，**推断**为 RA-L 2026，arXiv 页未直接写录用）。仓库 AndrePatri/AugMPC，GPL-2.0，最近提交 `d695aee`（2026-07-18），39 星 | 3 | 4 | 4 | 4 | 高层 RL 为 Go2-W 选择"接触时序 + 轮/腿模式 + twist"，低层用 MPC（轮式用滚动约束）；与纯 RL（robot_lab）对比：能耗、无域随机化下的 sim-to-real 差距。 | AugMPC 本身（Centauro 120 kg 轮足人形实机；仓库含 B2W 轮足仿真动图）；Racing a Wheeled Quadruped（Go2-W 的 MPC，仅高层仿真）；MPC-RL(π^n MPC)；DIAL-MPC | **偏紧。** 训练需 MPC 集群：README 用 Threadripper + RTX 4090 跑 800 个并行 MPC，约 6 h、1–10×10⁶ 步；安装推荐 ibrido-containers，Isaac Sim 版本、Go2-W 模型是否提供**未核实**；Go2 机载算力能否跑全刚体 MPC **未核实**，可能需外接笔记本 |
| 4 | **Simulator Adaptation via Proprioceptive Distribution Matching**（Dao、Fern；arXiv 2604.11090，2026-04-13；无录用信息，无代码链接） | 3 | 4 | 3 | 1 | 把真机/仿真关节观测+动作的**分布**距离作黑盒目标，辨识参数、delta 模型、残差执行器；创新点：对 Go2-W 的混合接口（腿位置+轮速）做分通道分布匹配，并加入"轮速—地面—滑移"项，无动捕、无时间对齐，5 分钟内数据 | 本文（Go2 四足，<5 分钟真机数据，sim2sim 与 privileged 状态匹配基线相当）；SPI-Active（需状态对齐）；PACE | **可完成。** 无代码需自己实现（黑盒优化 + Isaac Lab 并行 rollout），算力小；可与 #2 合并成一个"Go2-W 无动捕真实到仿真辨识 + delta 微调"方案。风险：发表级别（预印本）和 PACE 已有轮足使用 |
| 5 | **Learning Deployable Locomotion Control via Differentiable Simulation**（Schwarke、Klemm、Bagajo、Sleiman、Georgiev、Tordesillas、Hutter，ETH；CoRL 2025，PMLR v305 pp.3665–3684）。前作 DiffSim2Real（2411.02189，CoRL 2024 workshop） | 5 | 3 | 5 | 2 | 在可微仿真里加入滚动接触的光滑模型与轮速执行器，用解析梯度做**系统辨识 + 策略联合训练**，实机验证轮足速度跟踪；也可用解析梯度做 Go2-W 的参数辨识（比黑盒快） | 本文（ANYmal D 速度跟踪实机，自定义 NVIDIA Warp 刚体仿真器 + SHAC，单卡 RTX 2080 Ti）；Song/Kim/Scaramuzza，Learning Quadruped Locomotion Using Differentiable Simulation（CoRL 2024，PMLR v270 pp.258–271）；Open-DiffLoco（#6）；Trajectory-based actuator identification via differentiable simulation（2604.10351，无录用，无代码） | **难复现、价值高，收录并注明难点**：自定义 Warp 仿真器，检索未见代码（arXiv 与 PMLR 页）；作者自述限制：梯度范数随回溯步数指数增长（ANYmal 只能用 12 步）、不含粗糙地形、执行器只用简单 PD。工期内只能走 #6 的开源路线做小规模版本 |
| 6 | **Open-DiffLoco**（Opat，单作者；arXiv 2608.02069，2026-08-03，8 页通讯稿，无录用信息）。仓库 MartinOpat/open-diffloco，最近提交 `35256b6`（2026-08-05），18 星，许可证 NOASSERTION | 2 | 3 | 3 | 2 | 作为 Go2 上可微仿真（SHAC/JAVE）的**可跑底座**，做 Go2-W 的滚动接触 MJX 模型与可微系统辨识；看作原型工具而非主线论文 | Schwarke 等（#5）；Song 等 SHAC 四足；Open-DiffLoco 自身 | **作原型可行**：论文称 Go2 实机，训练 <6 GB 显存、20–60 分钟（RTX 5080）。风险：JAX/MJX 在 sm_120 上的兼容**未核实**；没有 Go2-W 模型；只有盲走、平地；价值主要来自后续创新，不适合单独作基础论文 |
| 7 | **QWM：Morphology-Conditioned World Model for Cross-Embodiment Quadrupedal Locomotion**（Danesh、Li、…、Berseth、Hutter、Lin；arXiv 2604.08780，v1 2026-04-09，v2 2026-08-17；无录用信息，无代码链接） | 3 | 3 | 4 | 2 | 给世界模型的形态条件加入"轮"描述（轮半径、轮速限、轮摩擦），检验"四足训练的世界模型零样本到轮足"；或作为 LocoFormer 之外的"想象中学习"对照 | 本文（声称四足族内首个零样本跨形态世界模型，ANYmal-D→Go1）；LocoFormer（CoRL 2025，Go2-W 实机）；RWM-U；URMA/具身尺度律 | **偏紧**：无代码、世界模型训练管线要自建（RWM-U 的仓库不含世界模型训练）；实机验证与 LocoFormer 重叠，创新要靠"轮通道 + 想象中训练"才立得住 |
| 8 | **DreamTIP：Learning Task-Invariant Properties via Dreamer**（Liang 等；arXiv 2604.02911，2026-04-03；**ICRA 2026 录用**，arXiv 评论栏）。无代码链接 | 3 | 2 | 3 | 2 | 把"任务不变属性"换成轮足相关（轮滑移、接地稳定性），用混合回放缓冲区做真机快速校准 | 本文（四足，Stair/Climb/Tilt/Crawl，真机 Climb 成功率 10%→100%，LLM 辅助选属性）；PIP-Loco；WMP | **可完成但创新薄**：Dreamer 训练在 Isaac Lab 上的成熟实现需自找，属性设计依赖 LLM、可复现性差；价值点（实机提升）只有单任务 |
| 9 | **PIP-Loco：Proprioceptive Infinite Horizon Planning**（Shirwatkar、Saxena、Chandra、Kolathaya，IISc；ICRA 2025，DOI 10.1109/ICRA55743.2025.11128382；arXiv 2409.09441；项目页 stochlab.com/PIP-Loco，未见 GitHub） | 3 | 3 | 4 | 4 | 把部署期 Dreamer 内部模型"无限视野 MPC 过滤动作/指令"迁到 Go2-W，用于轮滑移前预判和速度指令修正 | 本文；VIP-Loco（2603.14345）；Lagrangian NN 版（2506.16079、2603.14333，Go1 实机） | **偏紧**：2025 年发表，部署期要运行世界模型规划，Go2 机载算力能否实时**未核实**；无代码 |
| 10 | **SSRL：Learning to Walk from Three Minutes of Real-World Data with Semi-structured Dynamics Models**（Levy、Westenbroek、Fridovich-Keil；CoRL 2024，arXiv 评论为 "add CoRL footnote"；项目页写有视频与代码，**仓库未核实**） | 4 | 3 | 3 | 4 | 把"已知拉格朗日动力学 + 外力残差集成"换成轮足的已知刚体 + 轮-地接触力残差，真机从头学（或在仿真策略上微调）轮足步态；2024 年论文，不满足"近两年"偏好，但在"真实数据模型学习"线上最扎实 | 本文（Go1 实机，硬/软地面，3 分钟数据）；DayDreamer；RWM-U | **难在真机训练安全与状态估计**：需要稳定的状态估计和重置机制；实机工作量大，建议只作为方法参考 |

## 2. 其余检出但未入表（一句话）

- Dao & Fern 之外的执行器辨识：Trajectory-based actuator identification via differentiable simulation（Kovalev 等，2604.10351，2026-04；仅编码器数据，真机训练后行走距离 +46%、转角偏差 −75%，**摘要自述**；无录用、无代码）。可作 #4、#5 的辨识对照。
- Learning Quadrupedal Locomotion for a Heavy Hydraulic Robot Using an Actuator Model（Lee 等，Hwangbo 组，2601.11143；**RA-L**，arXiv 评论栏写 Vol.10 No.12, 2025-12；液压 300 kg+，无代码）：与 Go2-W 的电机问题距离较远。
- QuadVerse（2606.07118，2026-06；3D 高斯重建标定摩擦先验 + 残差动力学补偿；无机型、无代码、无录用）：偏视觉-物理对齐，与 Go2-W 关系弱。
- DynaFlow（2509.19804）：可微仿真嵌入流匹配，Go1 实机；与运动控制主线距离大。

## 3. 对已有候选的新信息（一句话）

- RWM-U：检索摘要提示 arXiv 2504.16680 已有 v3（2026-01 修订），录用信息仍未见；QWM 的作者含 RWM-U 的 Chenhao Li 与 Hutter，说明 ETH 在把世界模型从单机走向跨形态，与 LocoFormer 路线正面竞争。
- SimDist 路线的可比参照：TEMPO（#1）、SLowRL 都是"机载/低成本真机适应"，且都不更新世界模型，可作对照基线。
- PACE：Dao & Fern（#4）与 Kovalev 等（2604.10351）两篇 2026-04 预印本都做"无动捕/仅编码器"的执行器辨识，说明"换平台的辨识"已拥挤；PACE 相关创新要靠轮-热条件化。

## 4. 评价与建议（评价，非事实）

- **没有同时满足"高价值 + 代码完整 + 与 Go2-W 贴合"的论文。** 最贴 Go2-W 的 AugMPC（唯一有轮足硬件且代码公开的 RL+MPC）工程最重；价值最高的可微仿真（#5）不可复现；最容易复现的（#1、#2、#4）方法实质较薄，创新要靠 Go2-W 特有通道（轮速、温度、滑移）。
- 值得一并考虑的组合：#2 + #4（无动捕的 Go2-W 真实到仿真残差）作为"系统辨识/残差"线；#1 作为"在线适应"线，二者可叠加为"离线残差 + 在线轻量更新"两级方案，但需先在 PACE/UAN/SLowRL 之外做逐项查重。
- 查重缺口：未全文核对 TEMPO 的 Go2 实机细节（机载算力型号）、AugMPC 的 Isaac Sim 版本与 Go2-W 支持、Open-DiffLoco 的 JAX 版本与 sm_120 兼容、ASAP 在 Isaac Lab 5.x 上的移植量；这些需要打开仓库依赖文件才能确认。
