# 粗筛：RL 的 sim-to-real 与在线适应/鲁棒控制

筛选日期：2026-11-24。性质：第一轮粗筛，只读摘要、方法/实验概述、README 与目录树，没有精读全文，没有运行任何代码。写法约定：【事实】来自论文页面或仓库；【评价】是本文作者判断；【猜想】是尚未验证的研究设想。

## 1. 检索范围

**已排除（阶段比较 §3、§4、§8 已审查或已查重，不重复报告）**：GRAM、ESCP、SADL、TAM、UARL、RecoveryChaining、SimDist、FADA、OCCAM、OSCAR、GrBAL/ReBAL、TARC、ReLCE、DOMINO、Stability-Aligned Residual Adaptation（2603.07775）、CAPABLE、RMA 系。TAM 在本轮又被搜索命中，其页面信息与已审查结论一致（CoRL 2026 录用，实机 Franka，未列代码），不再展开。

**检索方式**：WebSearch（标准模式，约 20 条查询）加 WebFetch 打开 arXiv 摘要页和项目页，加 GitHub REST API 读取仓库元数据、目录树、README、提交与 issue。查询方向：actuator network / 执行器间隙；跨本体（腿足加机械臂）；UR 系列 RL sim-to-real；轮足 RL；延迟/频率/动作平滑；教师-学生与在线 SysID；残差与实机微调；恢复；自动域随机化；2025–2026 的 CoRL、RSS、ICRA、NeurIPS、ICLR 相关关键词。

**没有做到的**：没有逐条翻 CoRL 2025 / RSS 2026 / ICRA 2026 / IROS 2025 / RA-L 的官方论文目录，只靠搜索引擎（仅返回美国结果、对 2026 年条目覆盖不稳）命中。因此漏检是可能的，尤其是发表在 RA-L、IROS 的工作。没有打开 Hugging Face 页面核对权重文件。发表状态以论文页面、项目页、PMLR 页面或仓库 README 自述为准，除非另注，未到会议官网二次核对。

## 2. 候选总览

| # | 论文 | 状态 | 代码 | 双平台 | 评级 |
|---|---|---|---|---|---|
| 1 | PACE / Bjelonic 等，系统化 sim-to-real（执行器与关节辨识） | IJRR 2026（arXiv 页面自述） | 有（SysID 全链；无 locomotion 训练环境与权重） | 腿足为主；机械臂/轮需自行适配 | A |
| 2 | UAN，Fey 等，Athletic Loco-Manipulation | 预印本 2025（项目页标 arXiv Preprint） | 有（旧栈；无权重） | 腿足加机械臂臂关节都有 | B |
| 3 | SPI-Active，Sobanbabu 等 | CoRL 2025（Oral） | 有（IsaacGym，仅 Go2） | 仅腿足 | B |
| 4 | Actuator Reality Shaping，Yamamori 等 | 预印本 2026-07 | 无 | 7 自由度臂加轮足加人形 | B |
| 5 | NeuralActuator，Dou 等 | RSS 2026（项目页与 README 自述） | 有（含数据集、HF 权重声称） | 仅机械臂 | B |
| 6 | Isaac Lab Deploy：UR10e reach / gear assembly | 官方工程文档（非论文） | 有（Isaac Lab 主干） | 仅机械臂（UR） | B |
| 7 | ASAP，He 等 | RSS 2025 | 有（旧栈，人形） | 仅人形 | C |
| 8 | Dao & Fern，本体分布匹配的仿真器适应 | 预印本 2026-04 | 无 | 仅 Go2 | C |
| 9 | Rapid Embodiment Adaptation，Li 等 | 预印本 2026-08 | 无 | 仅 Go2 | C |
| 10 | SLowRL，Daneshmand 等 | 预印本 2026-03 | 无 | 仅 Go2 | C |
| 11 | TeAR，Sagar & Senanayake | 预印本 2026-09 | 无 | 仅机械臂 | C |
| 12 | LocoFormer，Liu 等 | CoRL 2025 | 无官方代码 | 腿足/人形，无机械臂 | C |
| 13 | Robot Trains Robot，Hu 等 | CoRL 2025 | 仅项目网站仓库 | 人形加机械臂做教师 | C |
| 14 | 轮足/Go2-W 相关：Go2-W 长距离导航、ATRos | 预印本 / IROS 2025 workshop | 无 | 仅轮足 | C（作平台背景） |
| 15 | AAAI-26 动作平滑 ASAP（Kwak & Hwang） | AAAI-26 录用 | 页面未列 | 通用，非实机 | C |

只有 1 篇评为 A，是因为没有一篇同时满足"RL 适应方法完整 + 官方代码 + 双平台成立 + 合理栈"。见 §4 的总体判断。

## 3. 逐篇说明

### 3.1 PACE（Bjelonic, Tischhauser, Hutter, ETH RSL）：评级 A

- **论文与链接**：Towards bridging the gap: Systematic sim-to-real transfer for diverse legged robots。[arXiv 2509.06342](https://arxiv.org/abs/2509.06342)；仓库 [leggedrobotics/pace-sim2real](https://github.com/leggedrobotics/pace-sim2real)；文档 https://pace.filipbjelonic.com 。
- **发表状态**：【事实】arXiv 页面写 v1 为 2025-09-08，v2 为 2026-07-31，并标注发表于 The International Journal of Robotics Research, 2026。我没有到 IJRR 官网二次核对，故记"IJRR 2026，arXiv 页面自述"。
- **作者研究的问题**：【事实】不靠大范围动力学随机化，而用少量物理参数加 PMSM 能量模型，辨识执行器与关节动力学（摩擦、延迟、增益等），使策略直接迁移。ANYmal 全成本 CoT 降低 32%。
- **方法类别与动作接口**：系统辨识（CMA-ES 并行拟合）加 RL 训练时的执行器模型。【事实】策略输出相对默认姿态的关节位置偏移，PD 转力矩，再由电机电流环跟踪。这与 Go2-W 腿关节的位置目标和 UR 的关节位置目标在形式上同类。
- **部署需要的输入**：本体感觉；辨识阶段需在机器人上采集 chirp 激励下的关节指令与编码器响应，不需要力矩传感器。训练时不依赖特权观测这一点来自论文摘要的"仅用标准关节编码器"描述，未逐项核对。
- **实验平台**：【事实】Tytan、ANYmal（D/C）、Minimal 三个主平台，另部署于约十种机器人（页面列出含 Aibo、NAO、GR-1、Allegro 与 Ability 灵巧手等，我只看到名单，没有核对每个的实验深度）。实机：是。
- **公开材料**：仓库 Apache-2.0，默认分支提交 `7ad0f45db5`（2026-10-13，v0.2.0），仓库 API 显示 2026-11-23 仍有推送，885 星。我实际看到：`scripts/pace/data_collection.py`、`scripts/pace/fit.py`、`scripts/rsl_rl/train.py` 与 `play.py`、`source/pace_sim2real/`（CMA-ES、`PaceDCMotor` 执行器、`anymal_pace_env_cfg.py`）、docs 目录。**只有 ANYmal D 一个任务配置。**【事实】issue #30（作者 2026-07-31 回复）：论文用的完整 locomotion 训练环境和奖励**不在仓库**，计划随后续工作发布，无日期。仓库没有策略权重。作者在 issue #36（2026-11-10）回答轮足适用性：自己没有在轮足上用过，"预期可用"，腿关节按原流程，轮子应改用速度指令并最小化轮速差。
- **软件栈与算力**：Isaac Lab，README 推荐 Isaac Sim 5.0 及以上（低于 5.0 缺少粘滞/动态摩擦支持）；Python 3.11。issue #34：作者暂不支持 Isaac Lab 3.0，社区有第三方适配（iit-DLSLab/sim2real-robot-identification）。论文称单张 RTX 3080，4096 并行环境，辨识约 10 到 24 小时每台机器人。这说明算力不是瓶颈。
- **双平台相关性**：腿足成立（Go2-W 的腿关节位置控制同类）。轮：需自行改成速度指令辨识（作者给了方向，未验证）。UR7e：【评价】问题形式（位置目标加跟踪响应）相同，但 UR 关节伺服在控制器内部，不是自己写 PD；辨识对象会变成"UR 的闭环跟踪特性"，PACE 的 PD 加电机模型假设不一定成立。
- **作者承认的局限**：【事实】悬空激励带宽有限（Tytan 约 8 Hz，ANYmal 约 2 Hz）；辨识与部署须保持相同固件补偿模式与滤波；温度与老化会漂移；假设被违反时失败。
- **可能的创新空间（猜想）**：把辨识扩展到"轮速度回路加位置回路"的混合执行器；把同一辨识框架用到 UR 关节闭环响应上，作为跨本体的统一 sim-to-real 前端；辨识结果随温度/负载在线更新（与"在线适应"结合）。其中机械臂部分风险最高。
- **初评 A**：开源 SysID 链完整、栈新（Isaac Lab、Isaac Sim 5.0 对新 GPU 友好度高于旧栈，但 Blackwell 兼容未核实）、接口与本项目一致、训练开销小。扣分点是缺 locomotion 环境与权重，且"系统辨识"本身偏工程，创新必须来自扩展对象。

### 3.2 UAN：Unsupervised Actuator Net（Fey, Margolis, Peticco, Agrawal, MIT）：评级 B

- **链接**：[arXiv 2502.10894](https://arxiv.org/abs/2502.10894)；[项目页](https://uan.csail.mit.edu)；仓库 [nolie-rolie/athletic-loco-manipulation](https://github.com/nolie-rolie/athletic-loco-manipulation)。
- **发表状态**：预印本（项目页写 "arXiv Preprint, 2025"，我没有查到录用信息）。同组后续 Contact-UAN（arXiv 2610.18991，G1 人形）只看到摘要级信息，未展开。
- **问题与方法**：【事实】用 RL 训练一个残差执行器网络，使仿真与真机关节编码器轨迹一致，无需力矩传感器。平台为 Unitree B2 加 Z1 机械臂（19 个驱动关节，其中臂 6 个加夹爪 1 个），UAN 在臂的各关节间共享。动作接口：位置目标，仿真中加 UAN 修正力矩。部署时策略不带 UAN（它只在仿真侧）。
- **部署输入**：本体感觉；UAN 训练需要真机按位置目标序列采集的编码器数据。
- **公开材料**：仓库提交 `06e30519e0`（2025-10-16），53 星，无许可证文件。我看到：`omniisaacgymenvs/tasks/b2_z1_wbc.py`、`z1_actuator_net.py`、`rsl_rl/`、docker、Makefile 目标（`make train-b2-z1-wbc`、`train-z1-actuator-net` 等）。README 称示例数据在 Google Drive（我没有打开）。**基于 OmniIsaacGymEnvs（README 针对 Isaac Sim 2023.1.0，已停止维护的旧框架）**；没有看到权重；没有实机部署代码。
- **算力与栈**：旧 Isaac Sim 与 OmniIsaacGymEnvs，在新 GPU 上迁移工作量大（【猜想】）。
- **双平台相关性**：【评价】这是本次检索中少有的"腿加臂在同一篇里都有实机执行器建模"的工作，思路可迁移；但它的臂是 Z1（直驱类伺服），UR 的内部控制器不开放力矩，UAN 的"修正力矩"在 UR7e 上只能在仿真侧用，实机回路不同。
- **作者局限**：论文里的实验限定于该机器人，未见多机型验证（我只读到摘要与项目页）。
- **创新空间（猜想）**：不改 UAN 本身，而是用位置目标到编码器响应的数据，学习 Go2-W 腿关节与 UR7e 的"闭环响应残差"，在两个平台共用同一训练配方。
- **初评 B**：思路相关性高，但代码栈旧、没有权重、需要自己采数据；复现成本主要在栈迁移。

### 3.3 SPI-Active（Sobanbabu, He, He, Yang, Shi）：评级 B

- **链接**：[arXiv 2505.14266](https://arxiv.org/abs/2505.14266)；[PMLR v305](https://proceedings.mlr.press/v305/sobanbabu25a.html)；仓库 [LeCAR-Lab/SPI-Active](https://github.com/LeCAR-Lab/SPI-Active)。
- **发表状态**：CoRL 2025（README 标 Oral；PMLR 页面存在）。阶段比较 §4 只把它当作"主动采集"先例，未审查代码，这里补代码核查。
- **问题与方法**：【事实】采样式系统辨识加主动探索：对已训练的多行为 RL 策略优化指令序列，辨识质量、质心、惯量与电机动力学模型参数；不需要可微仿真。论文称比基线好 42% 到 63%。
- **接口与输入**：策略接口为关节位置目标（沿用 HumanoidVerse 体系，未逐项核对）；需要真机采集轨迹。
- **平台**：Unitree Go2，实机。
- **公开材料**：提交 `edc07d0b95`（2025-11-26），233 星，无许可证文件。我看到 `spigym/`、`scripts/data/{walk,jump,sine,stand}.py`、`scripts/mass_opt.py`、`scripts/eval.py`、`active_sysid.md`、uv.lock。README 的 TODO：SPI 代码、主动探索、下游训练已勾选；**"Release Sim2real" 和数据回放未勾选**。没有权重。
- **栈与算力**：**IsaacGym Preview 4、Python 3.8、uv**。【猜想】旧 IsaacGym 在新架构 GPU 上大概率需要大幅迁移或无法运行，未验证。
- **双平台相关性**：腿足成立；机械臂：质量/惯量/电机模型辨识思想同样适用于负载与关节，但代码是 Go2 专用。
- **作者局限**：目前代码仅针对 Go2 的质量、质心、惯量加电机模型；sim2real 部分未发布。
- **创新空间（猜想）**：把主动辨识指令设计迁移到机械臂关节（激励轨迹设计比腿足更直接）；与 PACE 的执行器辨识互补比较。
- **初评 B**：方法相关、有代码，但栈旧、仅 Go2，且阶段比较已把"主动采集"列为已有先例。

### 3.4 Actuator Reality Shaping（Yamamori 等，ATR / 京都）：评级 B

- **链接**：[arXiv 2607.02205](https://arxiv.org/abs/2607.02205)；[项目页](https://syamamori.github.io/ActuatorRealityShaping.github.io/)。
- **发表状态**：预印本（2026-07-02 提交，07-07 修订；无录用信息）。
- **问题与方法**：【事实】反向思路：不调仿真去贴近硬件，而是用每关节二自由度前馈加反馈控制，让真实电机跟随仿真里理想的二阶参考动力学，策略在理想模型上训练后零样本部署，不需要学习的执行器模型。
- **接口**：【事实】每关节的 2-DOF 前馈-反馈控制器作为"标准化执行器接口"，位于策略与电机之间。需要能写关节级低层回路。
- **平台**：【事实】单关节高减速比伺服加外负载；7 自由度机械臂（reach）；轮足机器人 Moonbot-mini（31 DOF）；22 DOF 人形。实机：是。
- **公开材料**：页面只有论文 PDF 与视频，**没有代码**。
- **双平台相关性**：【评价】文中同时有臂与轮足，是本次最贴合"跨本体"表述的一篇。但它要求能接管关节级前馈-反馈回路。Go2-W 能否开放 `lowcmd` 级关节控制、UR7e 是否开放力矩/电流级，STATUS 里都还是未决项；在只能发位置/速度目标的接口上，它的前提不成立。
- **局限**：未读全文，作者局限未核对。
- **创新空间（猜想）**：在"只能发位置目标"的黑盒伺服上，用位置指令预整形（前馈）近似同样效果，作为受限接口版本；这需要自己实现，没有基线代码。
- **初评 B**：与项目表述最贴，但无代码、依赖低层接口，且是单一团队预印本。

### 3.5 NeuralActuator（Dou 等，MIT）：评级 B

- **链接**：[arXiv 2607.11734](https://arxiv.org/abs/2607.11734)；[项目页](https://people.csail.mit.edu/frankzydou/projects/NeuralActuator/index.html)；仓库子目录 [Frank-ZY-Dou/Dynamics-Modeling/NeuralActuator](https://github.com/Frank-ZY-Dou/Dynamics-Modeling/tree/main/NeuralActuator)。
- **发表状态**：RSS 2026（项目页与 README 自述，含 Outstanding Systems Paper Award 一说，我没有到 RSS 官网核对）。
- **问题与方法**：【事实】低成本伺服机械臂的神经执行器建模：Transformer 读取 9 帧历史（指令目标、本体状态、跟踪误差、执行器遥测），输出力矩替代量、外力估计、接触门控和电机状态分；通过可微仿真从位姿轨迹训练，不需要力矩标签。**不是 RL 论文**，下游只演示了冻结模块加行为克隆。
- **平台**：OpenManipulator-X（5 自由度）、SO-101（6 自由度）完整评估；Franka 仅离线负载力估计。全为机械臂，无腿足。
- **公开材料**：仓库提交 `541a93aac4`（2026-11-17），含 `NeuralActuator/README.md`、`configs/`（约 16 个）、`data/`（so101、franka、weight 等）、`models/`（gru、lnn 等）、`evaluate_actuator*.py`、`infer_actuator.py`、`hardware/`、`mjwarp/`；MIT 许可；README 称有 HF 数据集 NAD 与 11 个检查点（**我没有打开 HF 核对**）。
- **栈与算力**：可微仿真（Newton/Warp、MuJoCo Warp）；具体 GPU 需求未读。
- **双平台相关性**：只覆盖机械臂。【评价】可作为"机械臂侧执行器建模"的现成基线，但不能同时支撑腿足论点。
- **作者局限**：【事实】力矩替代量不可解释为可辨识的真实力矩；显式力耦合对标定失配更敏感；Franka 仅离线；未见几何的迁移只测两个物体；电机状态分只在受控的关节 3 受限场景验证。
- **创新空间（猜想）**：把"历史加遥测到残差"的建模思路搬到 Go2-W 腿关节，与 UR7e 共用一个结构；这与 UAN、TAM 的思路已有重叠，须查重。
- **初评 B**：代码与数据最完整，但不是 RL，且仅机械臂。

### 3.6 Isaac Lab Deploy：UR10e reach 与 gear assembly（NVIDIA，官方工程）：评级 B

- **链接**：[Isaac Lab 仓库](https://github.com/isaac-sim/IsaacLab)；[gear assembly 文档](https://isaac-sim.github.io/IsaacLab/main/source/policy_deployment/02_gear_assembly/gear_assembly_policy.html)；[NVIDIA 技术博客，2025-05-20](https://developer.nvidia.com/blog/bridging-the-sim-to-real-gap-for-industrial-robotic-assembly-applications-using-nvidia-isaac-lab/)。
- **性质**：不是论文，是官方环境与部署流程。放在这里是因为它是目前唯一看到的"UR 系列加 Isaac Lab 加 RL 加实机"完整工程链。
- **事实**：主干提交 `99a3acd776`（2026-11-24），release v3.0.0（2026-10-20）。目录 `source/isaaclab_tasks/isaaclab_tasks/contrib/deploy/` 下有 `reach/`（含 `ur_10e/`、`rizon_4s/`）和 `gear_assembly/`（`ur_10e/`、`rizon_4s/`，含 `rsl_rl_ppo_cfg.py`、`joint_pos_env_cfg.py`、`ros_inference_env_cfg.py`）。文档：动作为相对关节位置增量（`RelativeJointPositionActionCfg`，scale 0.025，6 维），随机化含执行器刚度 0.75–1.5 倍、阻尼 0.3–3 倍、关节摩擦 +0.3 到 0.7 Nm，训练约 12 到 24 小时，256 环境，无预训练权重；部署用 Isaac ROS 加自定义 ROS 推理节点，**阻抗控制器**。
- **UR 固件风险**：【事实】NVIDIA 博客称阻抗控制器是 URScript 500 Hz，用 UR 的 early-access 直接力矩控制接口（PolyScope 5 beta）。文档页没有给 PolyScope 版本要求。UR7e 在该接口上的支持**未核实**，也没有看到 UR7e 条目，只有 UR10e。
- **适应相关性**：只有域随机化，没有在线适应或辨识。
- **双平台相关性**：只机械臂。可作为 UR 侧的"最短可运行基线"和部署参照。
- **初评 B**：工程价值高、栈新；但 RL 适应方法为零，且依赖 UR 力矩接口。

### 3.7 ASAP（He 等，CMU）：评级 C

- **链接**：[arXiv 2502.01143](https://arxiv.org/abs/2502.01143)；仓库 [LeCAR-Lab/ASAP](https://github.com/LeCAR-Lab/ASAP)。
- **状态**：RSS 2025（README 标注）。
- **内容**：【事实】先在仿真预训练动作跟踪策略，再用真机数据训练 delta action model 修正仿真动力学，冻结后在仿真里微调策略。平台 Unitree G1 人形。
- **公开材料**：提交 `df5320cc47`（2026-01-06），MIT，2147 星；含 `humanoidverse/`、`sim2real/`、`scripts/`；README 徽章为 IsaacGym Preview4、IsaacSim 4.2.0、Genesis 0.2.1。
- **评价**：delta-action 思想对任意关节位置目标接口通用，但仓库是人形全身动作跟踪，且学习"仿真与真机的动作残差"这件事与 UAN、Dao & Fern 重叠。对本项目任务迁移成本高。
- **初评 C**：保留作思想参考。

### 3.8 其余预印本（均无公开代码，评 C）

- **Dao & Fern，Simulator Adaptation via Proprioceptive Distribution Matching**：[arXiv 2604.11090](https://arxiv.org/abs/2604.11090)，2026-04-13，无录用信息。【事实】把真机与仿真的关节观测与动作分布作为黑盒目标，辨识参数、动作增量模型、残差执行器模型；不需要时间对齐或动捕；不到 5 分钟数据；Go2 实机。页面未给代码。【评价】对"没有动捕的 Go2 辨识"非常对口，但无代码。
- **Rapid Embodiment Adaptation for Quadrupedal Locomotion**（Li, Ai, Bohlinger, Peters, Su, Christensen）：[arXiv 2608.01506](https://arxiv.org/abs/2608.01506)，2026-08，无录用信息。【事实】短历史估计本体参数加条件策略；Go2 实机，锁死一条腿与 5 kg 负载下稳定，半秒内辨识。项目页与摘要页均未给代码、仿真器、算力。【评价】与 ESCP、GRAM 同类（历史估计加条件策略），阶段比较 §4 已警示该组合不新。
- **SLowRL**（Daneshmand 等）：[arXiv 2603.17092](https://arxiv.org/abs/2603.17092)，2026-03，无录用信息。【事实】LoRA 低秩微调加恢复策略保证安全，直接在 Go2 实机上微调（jump、trot）；rank-1 即可恢复性能，微调时间减 46.5%。无代码。【评价】实机微调方向，安全性要求对 UR7e 更严。
- **TeAR**（Sagar & Senanayake）：[arXiv 2609.36182](https://arxiv.org/abs/2609.36182)，2026-09-28，无录用信息。【事实】用关节温度、电流、电压遥测对冻结策略的动作做修正，处理电机发热导致的执行器退化；论文称物理机械臂上发热场景提升 10 到 15%，但页面没写机械臂型号，也无代码。【评价】UR 是否开放温度与电流遥测需核实。
- **Go2-W 长距离导航**（Matsuzawa 等）：[arXiv 2606.21387](https://arxiv.org/abs/2606.21387)，2026-06 提交，2026-11-13 修订，无录用信息，无代码。【事实】轮式运动使髋关节负载大、过热，作者用周期性抬脚策略分摊；Tsukuba Challenge 2025 约 2.8 km。【评价】对 Go2-W 平台风险有信息价值：髋关节热负荷是实机持续运行的约束。
- **ATRos**：[arXiv 2510.09980](https://arxiv.org/abs/2510.09980)，IROS 2025 轮足 workshop 的 4 页短文，无代码，平台型号页面未写（另有来源称是 Go2W，我没有在该页面核实）。不作为候选，仅记录。
- **动作平滑 ASAP（Kwak & Hwang）**：[arXiv 2601.18479](https://arxiv.org/abs/2601.18479)，AAAI-26 录用（页面标注），在 Gymnasium 和 Isaac Lab 环境评估，页面未列代码，未见实机。与"动作平滑"主题对口，但无实机、无代码。

### 3.9 有发表但无官方代码的工作

- **LocoFormer**（Liu, Pathak, Agarwal, Skild AI）：[arXiv 2509.23745](https://arxiv.org/abs/2509.23745)，[PMLR v305](https://proceedings.mlr.press/v305/liu25a.html)，CoRL 2025。【事实】Transformer-XL 的长上下文跨回合适应，在程序化生成的大量本体上训练，实机包括 Go2 变体、G1、H1。我没有找到官方仓库；GitHub 上有 [lucidrains/locoformer](https://github.com/lucidrains/locoformer) 与 [BabyLocoFormer](https://github.com/linden713/BabyLocoFormer)，两者均非作者发布，我没有打开核查。训练规模大（大量本体加极端随机化），与单卡预算冲突，【评价】不适合作底座。
- **Robot Trains Robot**（Hu 等）：[arXiv 2508.12252](https://arxiv.org/abs/2508.12252)，CoRL 2025（PMLR v305）。【事实】带力传感器的机械臂当"教师"，在真机上自动适应与学习人形策略。仓库 robot-trains-robot.github.io 只含网站文件（index.html、rtr.pdf、media、static），**没有训练代码**。【评价】把机械臂当教师的设定与本项目的"被控对象是机械臂"不同。

## 4. 总体判断（评价，不是事实）

1. 腿足与机械臂**都有**实机并且**有完整 RL 适应代码**的论文，本轮没有找到。最接近的是 Actuator Reality Shaping（有两类实机，无代码，且要求关节级低层接口）和 UAN（有腿足加臂实机，代码为旧栈）。
2. 执行器/动力学间隙这一层（辨识、残差执行器、动作增量）在两个平台上都真实存在，且不依赖具体任务，是双平台最容易成立的共同问题；代码最扎实的是 PACE（腿足）和 NeuralActuator（机械臂），但两者不在同一平台，也都不是 RL 适应方法本身。
3. 在线历史适应类（Rapid Embodiment Adaptation、LocoFormer）属于阶段比较 §4 已列为被占据的组合，且本轮发现的均无代码。
4. 较旧的栈（SPI-Active 与 ASAP 的 IsaacGym、UAN 的 OmniIsaacGymEnvs）在可能的新 GPU 上需要移植；较新的栈（PACE 的 Isaac Sim 5.0、Isaac Lab 3.0）更有希望，但【猜想】Blackwell 兼容性我没有核实，须在服务器上实测。
5. 【猜想】一个可行的共同底座路线：PACE 式执行器辨识加 Isaac Lab 位置目标接口，作为两个平台共用的"sim-to-real 前端"，在其上做适应或残差。需先验证 Go2-W 腿关节和 UR7e 都能做激励数据采集，并且 PACE 的 DC 电机加 PD 模型对 UR 的闭环伺服是否成立。

## 5. 未覆盖或存疑

- 没有逐条翻会议官方目录（CoRL 2025、RSS 2026、ICRA 2026、IROS 2025、RA-L），可能漏掉未被搜索引擎收录的论文，尤其 ICRA 2026 与 IROS 2025 中的轮足或机械臂 RL sim-to-real 工作。
- 没有搜到专门针对 UR 系列的 2025–2026 正式发表的"关节空间 RL sim-to-real"论文（只找到 Isaac Lab/NVIDIA 工程、一篇 UR10e 硕士论文、一篇 2020 年 UR5e 的 Cartesian 空间工作）。这既可能是缺口，也可能是检索不足。
- UR7e 的直接力矩接口所需 PolyScope 版本、是否有等价于 UR10e 的 early-access 接口：本轮未核实。
- Go2-W 是否开放 `lowcmd` 低层控制：未核实（STATUS 未决项），影响 Actuator Reality Shaping 与 PACE 的辨识激励可行性。
- PACE 的 IJRR 发表状态以 arXiv 页面为准；NeuralActuator 的 RSS 2026 与获奖信息以项目页与 README 为准；两者未到官网核对。
- 未打开 Hugging Face 上的 NeuralActuator 数据集与权重；未打开 UAN README 中的 Google Drive 数据；未运行任何仓库。
- 实机上对延迟、控制频率、动作平滑的专题工作：本轮只找到 AAAI-26 的无实机动作平滑方法与较早的延迟随机化工作，没有 2025–2026 的实机代表作，视为缺口。
- 恢复技能：只搜到 FR-Net（arXiv 2509.11504，Go2 跌倒恢复，未确认发表状态与代码）等，未做代码核查，阶段比较中 RecoveryChaining 仍是较明确的参照。
- Isaac Sim 对 RTX PRO 5000（若为 Blackwell）的支持：Isaac Lab 文档提到 RTX PRO 6000，但没有核实 Isaac Sim 与 PyTorch 版本对应关系。
