# 粗筛：轮足机器人（wheel-legged）学习型运动控制

核查日期：2026-11-24。本文只读摘要、方法、实验、局限和仓库 README/目录树；未安装依赖、未运行训练、未控制硬件。标记约定：**【事实】** 来自论文或仓库原文；**【评价】** 本次筛选者的判断；**【猜想】** 未经验证的研究设想。

## 1. 检索范围

- 检索渠道：WebSearch（约 12 轮）+ arXiv abs/html 页 + 项目页 href 抽取 + GitHub API（提交、目录树）。未用 Google Scholar、IEEE Xplore、Semantic Scholar，多数期刊全文（MDPI、Springer、Science Robotics）被 403 或重定向，只拿到摘要级信息。
- 关键词：wheeled/wheel-legged/legged-wheeled + reinforcement learning、Go2-W、B2-W、Tron1、M20、Diablo、ANYmal on wheels、Swiss-Mile、stairs、fall recovery、jumping/parkour、energy/slip/thermal、world model/diffusion、loco-manipulation。
- 时间：以 2024–2026 为主，少量 2024 年早期工作作背景。
- 已审查过、本次不重复：robot_lab/rl_sar 的 Go2-W 链路、MUJICA、Learning to Recover（见 `04_research/reviews/platform_and_benchmark_review.md`）。本次对它们只补**新核实到的事实**。已复核 robot_lab HEAD 仍为 `26acb225`（2026-10-20）、rl_sar HEAD 仍为 `376d42c9`（2026-08-16），与旧审查一致，无新提交。
- 未检索到：Swiss-Mile 的新学习型论文、B2-W 专用论文、Diablo/Tron1 的 Isaac Lab 实机论文（Omni-WBR 页面 404）、轮足 VLA、轮足世界模型。详见第 5 节。

## 2. 候选表

初评含义：A = 值得精读，且对 Go2-W 复现或创新有直接价值；B = 作参考或局部借鉴；C = 相关性弱或证据不足。注意：**没有任何一篇 Go2-W 论文同时公开训练环境、奖励、权重和部署代码**，所以没有"可直接复现的 Go2-W 基础论文"，A 级是"最值得读/借鉴"而非"可直接复现"。

| # | 论文与链接 | 发表状态 | 平台 | 作者研究的问题 | 方法与动作接口 | 部署输入 | 公开材料（实际所见） | 软件栈与算力 | 作者承认的局限 | 可能的创新空间（猜想） | 初评 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | [Long-Distance Real-World Navigation of the Legged-Wheeled Robot Go2-W Using DRL](https://arxiv.org/abs/2606.21387)（Matsuzawa 等） | 预印本，v1 2026-06-19，v2 2026-11-13；页面未标注录用 | **Go2-W 实机** | 长距离轮式行驶时髋关节负载集中、电机过热；用周期性抬腿分摊负载；Tsukuba Challenge 2025 自主行进约 2.8 km 含楼梯 | 本体感觉策略，输出 12 腿位置目标 + 4 轮速度目标；非对称 AC + PPO；两个 EMA 滤波观测共 171 维；抬腿由奖励项（leg_effort_std、action_curvature）与地形/摩擦设置间接诱导，无显式抬腿奖励；"站立/行驶"与"粗糙地形"为不同策略，手动切换 | 策略不用外部定位；critic 用特权信息（地形高度、机体线速度、摩擦、质量、延迟）。导航层用 FAST-LIO2 激光惯性里程计 + GICP 对先验地图 | 论文称仅公开定位模块 `simple_fastlio_localization`；**运动策略代码未声明公开**；arXiv 页无官方代码链接 | "extended Legged Gym"，未写 Isaac Gym/Lab 版本，未报训练算力 | 热抑制与粗糙地形通行不能在单策略内同时实现，切换靠人工；导航靠经典感知规划，不能避让移动障碍（遇来车需急停）；依赖先验三维地图与预定路线；未与纯轮/纯足机器人对比；温度**未**进入策略训练 | 猜想：把电机温度/热负载作为观测或约束进入策略，实现无人工切换的热感知步态（见第 4 节 U1）；用 Isaac Lab 重做（原为 Legged Gym） | **A**（同平台同接口，局限明确；无代码） |
| 2 | [MUJICA](https://arxiv.org/abs/2605.13058)（Li 等）；[项目页](https://hyzenthlayer.github.io/mujica/) | 预印本，2026-05-13 v1，页面无录用信息 | Go2-W 实机 | 单一纯本体策略覆盖全向移动、攀高台、倒地恢复；DC 电机约束建模 | P3O（带约束 PPO）+ 非对称 AC；技能指示变量 + 高层选择器（冻结技能策略上训练）；腿位置偏移 + 轮速度，PD 转力矩；GRU 在线估计机体线速度、碰撞概率、轮地距离 | 纯本体；估计器输入过去 6 帧；critic 特权 | 项目页 href 抽取：仅 arXiv、视频，另残留 `extreme-parkour` 模板链接；**无 MUJICA 自身代码**；论文无代码声明 | Isaac Lab（无版本）；单卡 RTX 4090，4096 并行环境；50 Hz 策略/200 Hz 物理；机载 Jetson Orin NX | 仅说"后续扩展更多技能并在非结构化地形上自适应协调"；无单独局限章节；高台 80 cm/1 m 与楼梯 20 cm 的失败案例未讨论 | 猜想：电机速度-力矩包线（torque-speed curve）建模在 Go2-W 上带来的 90%→3.5% 约束违反率下降，可作为"执行器感知"创新的现成对照与动机（U3） | **A**（Go2-W 实机 + 执行器建模；无代码需自行重写） |
| 3 | [Learning to Recover: Dynamic Reward Shaping with Wheel-Leg Coordination](https://arxiv.org/abs/2506.05516)（Deng 等）；[项目页](https://boyuandeng.github.io/L2R-WheelLegCoordination/) | 预印本，v1 2025-06-05，v2 2025-10-08；页面未标注录用 | KYON、Go2-W | 倒地后轮腿协同起身；稀疏奖励 | episode 动态奖励塑形 + 课程；声称腿轮协同使关节力矩消耗降低 15.85%–26.2% | 未逐项核对（旧审查已读） | 项目页 href 抽取：Paper(pdf)、Arxiv、Code 等锚点目标未解析出，页内唯一 GitHub 链接是网站模板作者的；**无法证实有代码** | 未核 | 旧审查已列局限；本次未重读正文 | 见第 4 节"恢复后接上行驶"（U6） | B（已审，重复内容不展开） |
| 4 | [ATRos: Learning Energy-Efficient Agile Locomotion for Wheeled-legged Robots](https://arxiv.org/abs/2510.09980)（Sun 等） | 预印本，2025-10-11；IROS 2025 轮足研讨会投稿（4 页） | **Go2W EDU 16 DoF，含初步实机** | 无预设步态的行驶-行走混合运动，能量感知奖励 | 12 腿位置目标（相对站姿，系数 k_l）+ 4 轮速度目标（系数 k_w），50 Hz；预测响应网络从历史估计机体速度与隐变量 | 纯本体 57 维；critic 特权；无外部估计器 | 无代码，仅项目页 | Isaac Gym（无版本），4096 环境；推理在 RTX 4090 上经有线以太网发命令（训练硬件未报） | 自述实机实验为初步；将提升越障稳定性、轮腿融合自然性；**全文无任何能耗量化数字**（无功率、COT） | 猜想：补上能效的量化评测与基准（COT、单位距离耗电），是现有"节能"声称的空缺（U2） | B（4 页研讨会稿，但平台恰为 Go2W） |
| 5 | [FLORES: A Reconfigured Wheel-Legged Robot for Enhanced Steering and Adaptability](https://arxiv.org/abs/2507.22345)（Song 等）；[仓库](https://github.com/ZhichengSong6/FLORES) | **正式发表**：IEEE RA-L vol.11 no.6 pp.7444–7451, 2026-06（arXiv v1 2025-07-30，v2 2026-04-26） | 自研 FLORES（前腿髋偏航代替髋横滚），与 B2W 对比 | 轮足转向与适应性，轮式/腿式平滑过渡 | HIMLoco（Hybrid Internal Model）+ 定制奖励；Isaac Gym 训练 → MuJoCo 验证 → ROS2 实机 | 纯本体 | 提交 `814db438`（2026-05-22 "update README"）。目录实见：`Mechanical/`（STEP 机械图）、`code/HIM_FLORES/`（`mdog_config.py`、`mdog_robot.py`，需复制到 HIMLoco）、`code/Mdog/`（ros2_control 控制器、MuJoCo 硬件接口、URDF）；**已提交权重** `May22_0943.pt`（FLORES）及 A1/Go2 的 `him.pt`/`policy.pt`；URDF/mesh 需自行放置（README 说明路径）。**不是 Go2-W** | Isaac Gym + legged_gym/HIMLoco；ROS2 Humble + libtorch 2.5.0；训练算力未写 | 未逐段核对论文局限 | 猜想：把其"训练→MuJoCo 交叉验证→ros2_control 部署"链路套到 Go2-W（Go2-W 已有 unitree_mujoco 配置的可能性未核），作为 sim2sim 门槛 | **A**（唯一核实到"环境+权重+部署"三者都有的轮足工作；非 Go2-W，旧栈 Isaac Gym 需移植到 sm_120） |
| 6 | [Quadrrl](https://github.com/lbnmahs/quadrrl)（Njoroge、Helal；软件） | 软件，无论文；README 给 `@software` 引用 | 含 Go2W、B2W、DeepRobotics M20、Zsibot ZSL1W 的 Isaac Lab 任务 | 跨形态/地形/工作流的四足运动基准 | RSL-RL PPO（另列 RL Games、SKRL、HARL）；任务名 `Quadrrl-Velocity-Rough-Unitree-Go2W-v0` | 本体 | 提交 `0307ca68`（2026-09-17），BSD-3；目录含 `notebooks/legged_vs_wheeled_performance.ipynb`、`scripts/analysis/run_legged_vs_wheeled_analysis.py`、`scripts/experiments/run_legged_vs_wheeled_seeds.sh`；README **未提预训练权重与部署代码**；19 星 | **Isaac Sim 5.1.0 + Isaac Lab 2.3.2（README 徽章）**，与服务器环境一致 | 无论文，无局限陈述 | 猜想：其"轮式 vs 足式"对比脚本可作为 Go2-W 评测基线雏形；与 robot_lab 重叠度需另核 | B（评测工具，非方法） |
| 7 | [AWARE: Unleashing the Agility of Wheeled-Legged Robots for High-Dynamic Reflexive Obstacle Evasion](https://arxiv.org/abs/2604.23761)（Zhao 等） | **IEEE RA-L 2026**（arXiv 页标注；v1 2026-04-26，v2 2026-09-22） | DeepRobotics M20（轮足）实机 | 动态障碍的反射式规避；滚动/踏步/混合主导的避让 | 分层 RL：威胁条件化高层输出速度指令 + 离散专家选择（Gumbel-Softmax）；低层输出关节位置 + 轮速度；PPO，5 个种子 | 部署用**动捕系统**提供机器人与障碍的位置速度；无机载威胁感知 | 项目页仅有论文链接，无代码 | Isaac Lab（无版本）；4096 环境；训练硬件未报 | 实机失败来自轮速/力矩饱和、姿态安全裁剪过保守、动捕与通信延迟、摩擦/执行器响应的仿真差距；阈值敏感性只在已测场景；计划接入更丰富感知 | 猜想：用机载感知替代动捕后的端到端反射规避（U5） | B |
| 8 | [CTBC: Contact-Triggered Blind Climbing for Wheeled Bipedal Robots](https://arxiv.org/abs/2509.02986)（Li 等） | 预印本 v1 2025-09-03，v3 2026-02-07；arXiv 页**未写**录用信息（项目页有 ICRA2026 格式 PDF，是否录用本次未证实） | LimX Tron1（8 DoF，轮半径 12.7 cm）、Cowarobot R0 | 轮双足盲爬楼：接触触发抬腿 + 指令学习 | 8 维动作（腿位置、轮速度）；接触触发引导前馈轨迹 | 纯本体；critic 特权（线速度、接触力、77 值高度扫描） | 无代码，仅项目页 | Isaac Gym 训练 + MuJoCo 交叉验证；单卡 RTX 4090 | 一阶段伸展步态使策略偏向前腿领先；纯盲；Tron1 实机 20 cm 台阶、仿真 22 cm 成功率 70%；计划做对称破缺奖励、与感知规划器结合 | 猜想：Go2-W 轮半径约 89 mm（见 go2w.CN.md），与 Tron1 差异大，"接触触发"思想能否迁移是开放问题 | B |
| 9 | [RAIWAY](https://arxiv.org/abs/2610.33172)（Nam 等，Hwangbo 组） | **已录用 RA-L**（arXiv 页标注；2026-10-23 v1） | 自研 20 英寸大轮双足 RAIWAY | 破碎地形上轮式滚动；楼梯到 15 cm | 接触信息作特权，压缩为隐表示，部署时由本体推断 | 纯本体，无接触传感器 | 无代码，仅演示视频 | 未核 | 未取得正文，局限未核 | 其"特权接触 → 隐变量"对应轮地接触估计，可借鉴到 Go2-W（U4） | B |
| 10 | [Learning Robust Autonomous Navigation and Locomotion for Wheeled-Legged Robots](https://arxiv.org/abs/2405.01792)（Lee 等，ETH） | **正式发表**：Science Robotics 2024, 9(89), DOI 10.1126/scirobotics.adi9641 | ANYmal 轮足版，苏黎世/塞维利亚数公里实机 | 行走-驾驶平滑切换；城市级导航 | 无模型 RL + 特权学习；分层 RL 把运动控制器与学习型导航控制器相连 | 导航层需地图/定位（具体未核） | 无代码（arXiv 页无链接，Science 页被 403） | 未核 | 未核（仅摘要） | 里程碑式工作，作为必引与对照；未核正文，不下结论 | B（2024，作背景） |
| 11 | [Reinforcement Learning for Blind Stair Climbing with Legged and Wheeled-Legged Robots](https://arxiv.org/abs/2402.06143)（Chamorro 等） | 预印本（2024-02）；页面未标注录用 | 多款四足与双足仿真；实机 Ascento 爬 15 cm 台阶 | 盲爬楼，位置式（非速度式）指令 | 非对称 AC，布尔爬楼模式输入，延迟随机化 | 纯本体 | 无代码 | 未核 | 实机仅 Ascento 15 cm | 猜想：位置式指令在轮足四足上是否有益未见验证 | C（2024，非四足轮足实机） |
| 12 | [Force-Aware RL with Hybrid Sensorless Force Estimation for Wheeled-Legged Loco-Manipulation](https://arxiv.org/abs/2609.13779)（Zeng 等） | 预印本 2026-09-12 | 轮足机械臂（型号页面未写）实机 | 无力传感器的末端力估计与力/位混合控制 | 广义动量观测器 + 残差网络，轴向选择器，整机策略 | 动量观测需动力学模型 | 无代码 | 未核 | 未核 | 与本课题（纯运动）相关度低 | C |
| 13 | [Learning Whole-Body Loco-Manipulation for Omni-Directional Task Space Pose Tracking with a Wheeled-Quadrupedal-Manipulator](https://arxiv.org/abs/2412.03012)（Jiang 等） | arXiv 页显示相关 DOI 10.1109/LRA.2024.3519856，**推断**为 RA-L，页面未明写 | 轮式四足机械臂实机 | 6D 末端位姿跟踪 | 奖励融合模块 + 师生训练 | 未核 | 无代码，仅项目页 | 未核 | 未核 | 同上 | C |
| 14 | [Stand, Walk, Navigate: Recovery-Aware Visual Navigation on a Low-Cost Wheeled Quadruped](https://arxiv.org/abs/2510.23902)（Solano、Quiroz） | 预印本；IROS 2025 轮足研讨会 | 自研低成本轮式四足，**仅仿真** | 深度相机导航 + 跌倒恢复 | PPO；运动策略基于 robot_lab；腿位置+轮速度；腿力矩上限 25 N·m，轮 6 N·m | 本体 + 深度相机；critic 用 187 维地形高度 | 无代码（引用 robot_lab） | Isaac Lab/Sim（无版本），RTX 3060 | 离散地形恢复成功率最低；定位丢失致导航失败；sim-to-real 未验证 | 低力矩执行器下的恢复可行性问题 | C |
| 15 | [Friction-Aware Safety Locomotion for Wheeled-legged Robots using VLMs and RL](https://arxiv.org/abs/2409.09845)（Peng 等） | **已录用 Humanoids 2025**（arXiv 页标注） | 自研轮式倒立摆，仿真 + 实机 | 打滑风险：VLM + RAG 估摩擦系数，RL 提前降速 | VLM 估 μ → 速度调节 | 需相机与 VLM | 无代码 | 未核 | 平台是轮倒立摆，非四足轮足 | 猜想：摩擦估计的视觉先验接入 Go2-W 策略（U4）；Go2-W 上未见 | C |
| 16 | [Adaptive multi-mode locomotion for bipedal wheel-legged robots (MoE-PPO)](https://www.frontiersin.org/journals/robotics-and-ai/articles/10.3389/frobt.2026.1788395/full) | **正式发表**：Frontiers in Robotics and AI，Brief Research Report，2026-02-25 | Diablo（轮双足），**仅仿真** | 单策略多模式、灾难性遗忘 | MoE 行动者，Top-1 门控 + 负载均衡损失，PPO | 纯本体 + 10 帧历史 | 数据声明"合理请求提供"，无代码 | Isaac Gym；RTX 3090 Ti，4096 环境 | 无实机；基线仅 PPO；障碍靠抬腿，刻意不含跳跃；高速碰撞与极端接触自恢复未解 | 与 MUJICA 的"技能选择器"路线竞争，证据较弱 | C |
| 17 | [Robust Locomotion Control of Quadrupedal Wheel-Legged Robots via Contrastive History-Aware RL](https://doi.org/10.3390/machines14050568)（Dai 等） | **正式发表**：Machines 14(5):568，2026（MDPI；页面标 early access） | 四足轮足，**平台型号未取到** | 无外部传感的状态估计；对比学习避免地形回归与力传感 | 对比学习历史编码 + RL；声称零样本 sim-to-real | 纯本体 | 全文被 403，代码声明未取得 | 未取得 | 未取得 | 未能核实，仅记录存在 | C（待核） |
| 18 | Learning-Based Hybrid Locomotion Control for a Heavy Wheeled-Legged Robot in Challenging Terrains（[Springer J Intell Robot Syst](https://link.springer.com/article/10.1007/s10846-026-02423-8)） | 搜索摘要称 2026-07 发表；**页面被重定向，全文未读，标题未能二次核对** | >340 kg 重型轮足 | 重型平台 RL 部署 | 启发式奖励 + 特权学习状态估计器（搜索摘要） | 未核 | 未核 | 未核 | 未核 | 未核 | 与 Go2-W 体量差距大 | C（存疑） |

**邻近但非轮足（仅作迁移参考，已打开 arXiv 摘要页）**

| 论文 | 状态 | 平台 | 要点 | 评价 |
|---|---|---|---|---|
| [Learning Thermal-Aware Locomotion Policies for an Electrically-Actuated Quadruped Robot](https://arxiv.org/abs/2603.01631) | 预印本 2026-03-02 | Unitree A1，3 kg 载荷 | 电机温度入观测 + 热约束奖励；基线约 7 分钟过热停机，本法 27 分钟以上 | 与 #1 的过热问题直接对应；无代码 |
| [Learning to Balance Motor Thermal Safety and Quadrupedal Locomotion Performance with Residual Policy](https://arxiv.org/abs/2605.27046) | 预印本 2026-05-26，v3 2026-07-03 | Unitree A1，3 kg 载荷 | 全身热模型进训练；名义策略 + 热状态残差策略；名义策略约 5 分钟过热，残差法 13 分钟以上 | 同上；无代码 |

## 3. 公开材料与平台总览（关键事实）

- **Go2-W 实机论文共 4 篇**：#1、#2、#3（含 Go2-W）、#4。**无一篇可核实地公开训练环境+权重+部署代码**。#1 仅公开定位模块；#2、#3 项目页无代码；#4 无代码。
- 唯一"环境+权重+部署"齐全的轮足工作是 #5 FLORES，但机器人是自研的，栈为 Isaac Gym/legged_gym/HIMLoco，与服务器 Blackwell 需移植。
- Go2-W 的现成工程底座仍是 robot_lab（Isaac Lab，`wheeled/unitree_go2w`）+ rl_sar（`policy/go2w/robot_lab/policy.pt`、`fsm_go2w.hpp`），以及 Quadrrl 的 Go2W 任务。这些是**平台代码**，不是论文方法。
- 软件栈方面：#1、#4、#8、#16 用 Isaac Gym/Legged Gym 系；#2、#7、#14 用 Isaac Lab；版本多数不报。迁到 sm_120 需要 Isaac Lab/Isaac Sim 5.x，Quadrrl 已声明 Isaac Sim 5.1 + Lab 2.3.2。
- 算力：已报的均为单卡消费级（RTX 3060/3090 Ti/4090），说明 48 GB 单卡足够，算力不是瓶颈。

## 4. 轮足方向的未解决问题汇总

下面每条分"作者事实"（出处）、"评价"、"猜想"。

**U1 热/负载感知：驾驶时的热管理与人工切换**
- 事实：#1 报告轮式行驶使髋关节负载集中、电机过热，靠抬腿分摊；且"热抑制与粗糙地形通行无法在单策略内实现，切换靠人工"，温度未进入策略训练。
- 事实：两篇 A1 热感知论文（2603.01631、2605.27046）已把电机温度进入策略，但平台是普通四足、载荷 3 kg，没有轮。
- 评价：Go2-W 上"温度进入策略"目前无人做，且问题由实机长距离实验自己暴露，动机扎实；但 Go2-W 低层是否开放电机温度读数（`motor_state.temperature` 字段存在，见 go2w.CN.md）需实机核实，温度模型需自建。
- 猜想：热状态条件化的单一策略，在冷态偏重效率、热态自动增加抬腿分摊；并作为"行驶-越障-热管理"统一策略，替代人工策略切换。

**U2 能效缺少量化与基准**
- 事实：#4 ATRos 标题含"节能"，但全文无任何能耗数字；#1 未与纯轮或纯足机器人对比；#3 报告的是恢复阶段的力矩消耗。
- 评价：多篇共同回避"同任务、同速度、实机功率/COT"的量化对比，这是方法论空缺，也是低风险的实证贡献。Go2-W 有电池 BMS 状态可读（go2w.CN.md），可做实机功耗。
- 猜想：给出行驶、行走、混合三种模式在不同速度/地形下的 COT 曲线，并以此设计模式切换/奖励。

**U3 执行器与 sim-to-real（力矩-速度包线、轮腿通道不对称）**
- 事实：#2 MUJICA 显示是否建模 DC 电机速度-力矩限制，会使力矩超限比例从 90% 以上降到 3.5% 以下，且参数取自 Unitree 官方电机手册；#7 AWARE 的实机失败包括轮速/力矩饱和与执行器响应差距；#14 假设低力矩执行器。
- 评价：16 通道里腿、轮电机参数不一（go2w.CN.md 记录模型 effort 与 Robot Lab 参数不同、不可混用），公开工作对"轮电机的真实响应、PD 增益、速度环延迟"几乎没有辨识。MUJICA 无代码，意味着这项建模无法直接复用。
- 猜想：对 Go2-W 的 12 个腿关节与 4 个轮做执行器辨识（可借 PACE 流程，见 STATUS），再在轮足策略中验证"辨识后的轮速度环"对打滑/抖动的影响。

**U4 轮地接触与打滑：几乎全靠盲策略的隐式适应**
- 事实：#9 RAIWAY 用接触特权信息训练、部署时推断；#15 用 VLM 估摩擦但平台是轮倒立摆；#1 把摩擦、质量、延迟只给 critic；#17 声称对比学习替代力传感，但未取得全文。
- 评价：没有一篇在 Go2-W 上显式研究轮的打滑、侧滑与不同摩擦的适应；轮地接触通常只出现在特权观测里，部署侧无显式打滑检测。
- 猜想：用轮速与 IMU/腿运动学的不一致量作打滑信号，做在线适应或安全降速（但需先确认其可观测性，Go2-W 无足端力传感器，go2w.CN.md 已说明）。

**U5 感知运动与导航接口：几乎都是纯本体，感知部分要么外置要么动捕**
- 事实：#1 的运动策略纯本体，导航靠 LIO + 先验地图；#7 AWARE 部署用动捕；#8 CTBC 把"与感知规划器结合"留作未来工作；#14 只在仿真。
- 评价：轮足上"学习型感知策略实机部署"几乎空白；运动策略与导航的接口多为速度指令加人工策略切换，"模式/技能"接口形式不统一。
- 猜想：本科周期内不宜做感知学习；更现实的是把"导航层可发出的模式/抬腿请求"作为标准接口，与 U1 结合。

**U6 多技能与模式切换：技能选择器是共同路线，但切换依据与稳定性缺少评测**
- 事实：#1 手动切换策略；#2 技能指示变量 + 选择器；#7 离散专家；#16 MoE 门控（仅仿真）；#10、#5 提供行走-驾驶平滑切换。
- 评价：作者几乎都只展示"能切换"，缺少对切换时序、抖动、误触发的系统评测；#7 自述只测了已测场景的阈值敏感性。
- 猜想：设计"模式切换稳定性"指标与基准（过渡力矩峰值、过渡时间、误切换率），并检验统一策略与分层策略。

**U7 跌倒恢复与后续运动衔接**
- 事实：#2、#3 覆盖恢复；#14 的恢复在仿真。#3 项目页未证实代码。
- 评价：恢复多作为独立技能，恢复后接回行驶/爬楼以及恢复的安全性（实机反复倒地损伤）极少讨论。
- 猜想：低风险但实机验证成本高，不建议作为本科主线。

**U8 负载与外部扰动：轮足上几乎空白**
- 事实：#1 随机化机体附加质量 −1 到 5 kg，但只作域随机化；官方载荷约 8 kg、最大约 12 kg（go2w.CN.md）。热感知论文在 A1 上做 3 kg 载荷。
- 评价：未检索到轮足上带载荷/推扰的系统评测，不等于不存在（检索范围有限）。
- 猜想：载荷与热管理可合并成一个问题（负载提高关节力矩，进而加速升温）。

**共同回避**：(a) 实机能耗量化；(b) 真实轮电机辨识；(c) 单策略统一"行驶/行走/越障"，多数仍靠多策略或选择器；(d) 开放代码——Go2-W 工作没有一篇给出完整训练+部署链；(e) 无统一 Go2-W 评测协议（地形、速度、能耗、热、成功率不一致，难以横向比较）。

## 5. 未覆盖或存疑点

- **未取得全文**：#10（Science Robotics）、#17（MDPI，403）、#18（Springer，重定向）。#17 的平台型号与代码声明未知。#18 标题只来自搜索摘要，未核。#3 L2R 本次只读摘要页，不重复旧审查。
- **未找到**：Go2-W/B2-W 上的跳跃或 parkour、轮足 VLA/世界模型/扩散策略（唯一的 LocoWM arXiv 2609.39179 摘要页未写平台，是否轮足不详，未纳入；WAM-Policy 2611.24011 是 Go2 Air 三足操作，非轮足，未深读）。Swiss-Mile 的学习型新论文、Tron1/Diablo 的 Isaac Lab 实机论文（Omni-WBR 项目页 404）。**这不等于不存在**，检索渠道有限。
- **发表状态存疑**：#8 CTBC 的 ICRA 2026 仅见项目页 PDF 文件名，arXiv 页未标，视为"预印本，录用待证"。#13 的 RA-L 是由 DOI 推断。
- **代码核实方式**：#2、#3、#7 通过项目页 HTML 的 href 抽取；#5、#6 通过 GitHub API 目录树与 README；其余通过 arXiv 页"代码"区只有第三方聚合器链接，判为无官方代码。项目页的"Code"按钮若为 JS 动态链接可能漏检。
- **版本时间敏感**：robot_lab/rl_sar/Quadrrl/FLORES 提交号均为 2026-11-24 所见；robot_lab main 已转 Isaac Lab 3.0，服务器环境应固定 v2.3.2（见旧审查）。
- **本次未验证**：任何论文的实验数字未复现；"A 级"是阅读价值判断，不是可复现性保证。
