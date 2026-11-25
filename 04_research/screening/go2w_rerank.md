# Go2-W 单平台重排（取消 G1 之后）

日期：2026-11-24。性质：对已有候选按新门槛重评，并补查 2025–2026 年 Go2 / Go2-W 学习型运动控制论文。已有候选的论文细节沿用 `review.CN.md`、`screening/`、`candidates/`、`reviews/`，没有重读论文全文。本轮新打开的仓库（README、目录树、GitHub API 元数据）都已逐个核对，标注"已核"。没有安装或运行任何代码。

写法约定：【事实】来自论文页面或仓库；【评价】是本文判断；【猜想】是未验证的设想。

## 1. 门槛说明

| 门槛 | 内容（平台只有 Go2-W） |
|---|---|
| G1 | 取消 |
| G2 | 官方代码能支撑复现：训练、评估，最好有权重、资产 |
| G3 | 能在 sm_120（Blackwell）上运行：PyTorch ≥ 2.7（cu128）、Isaac Sim 5.x，或移植代价说得清 |
| G4 | 能落到 12 腿位置目标 + 4 轮速度目标；部署输入在 Go2-W 上可得（IMU、关节、轮速、上一动作；无外部定位，机体线速度需估计） |
| G5 | 单卡 48 GB、3–4 个月能做多种子、基线、消融 |
| G6（新增） | 复现之后是否有"有查重依据的改进空间"，以及已知查重风险 |

复现层级（后文"可达层级"用）：
- L1：原任务训练或推理跑通
- L2：对齐论文仿真指标
- L3：改成 Go2-W 的 12+4 动作，仿真里跑通
- L4：Go2-W 实机

通用事实（已核）：
- 【事实】`fan-ziqi/robot_lab` 的 `v2.3.2` 分支对应 Isaac Lab 2.3.2 和 Isaac Sim 4.5/5.0/5.1；`main` 对应 Isaac Lab 3.0.0。任务表里有 `RobotLab-Isaac-Velocity-Rough-Unitree-Go2W-v0`。
- 【事实】`unitreerobotics/unitree_rl_lab`（Apache-2.0，2026-05-25 推送）：README 标 Isaac Sim 5.1.0 / Isaac Lab 2.3.0，支持 Go2、H1、G1-29dof，有 `deploy/` 目录。它是平台工程，不是论文，不支持 Go2-W。
- 【评价】新栈的共同做法是 Isaac Sim 5.1 + torch 2.7 cu128 + rsl_rl。凡是仍停在 Isaac Sim 4.x、torch 2.2–2.5 cu121 的仓库，在 sm_120 上都要升级依赖再试；这是显式的移植工作，不是"换个环境"。

## 2. 重排表（已有候选）

评级含义：A = 可作基础论文；B = 可作组件、对照或备选；C = 只作查重或思想参考。"原评"指此前筛选里的评级。

| 候选 | 状态 | 代码与栈（已核） | Go2-W 适配要点 | 可达层级 | 改进空间与查重风险 | 新评级与原因 |
|---|---|---|---|---|---|---|
| PACE（Bjelonic 等） | IJRR 2026，Crossref 有记录（证据卡已核） | Apache-2.0，Isaac Sim ≥5.0，Python 3.11；只有 ANYmal D 配置，无运动训练环境和权重 | 腿关节原流程；轮改速度指令辨识（作者 issue #36 说"预期可用"，未验证）；需要 Go2-W 能开放低层 `lowcmd` 做 chirp 激励（STATUS 未决项） | L1 辨识链可跑；L3 要自己写 Go2-W 任务（robot_lab 可补）；L4 取决于 lowcmd | 【事实】第三方仓库 `godhandcrash/go2-pace-sim2real`（6 星，2026-08，无许可证）已把 PACE 参数用到 Go2；作者同事已用于轮足。"PACE 搬到轮足"不算贡献。猜想：轮速回路与位置回路混合辨识、辨识参数在线更新，均未查重 | B（原 A）。双平台理由消失后，它是 sim-to-real 前端而不是运动学习方法，创新要自己找。作为底座仍然可复现性最高 |
| RWM-U（ETH） | arXiv 预印本，ICLR 2026 workshop 海报（证据卡已核） | MIT；README 标 Isaac Sim 4.5.0 / Isaac Lab 2.2.1 / Python 3.10，依赖 `rsl_rl_rwm`（torch ≥2.6）；只发布 ANYmal D 平地任务，无真实数据管线与部署 | 关节位置接口，加 4 轮速度要改模型输入输出；观测里有机体线速度，Go2-W 要么估计要么去掉；世界模型离线数据要自己在 Go2-W 上采 | L1：ANYmal 任务；L3：要自己建 Go2-W 数据与模型；L4：要自己写数据采集与部署 | 证据卡：代码与论文有多处不一致；部署时 OOD 检测、仿真加真实微调查重度高；离线选择 λ 与审计证据矛盾 | B（原 A，精读后已降为备选）。取消双平台没有改善它的核心问题：发布范围窄、发表级别低 |
| DSRL | CoRL 2025（PMLR 已核） | JAX（cuda12），基于 openpi | 动作块扩散策略的潜噪声引导；Go2-W 的高斯 RL 策略上它等价于有界残差 RL | 只能 L1 | 查重高：残差 RL、UARL、Stability-Aligned 已占 | C。它的价值在 UR7e 一侧，Go2-W 上没有对应问题 |
| DIAL-MPC | ICRA 2025 | Apache-2.0，JAX/MJX，CUDA ≥12.3，对新 GPU 友好；有 Go2 实机脚本 | README 明写"需要外部定位模块提供机体位置与速度"（已核）；无轮模型，要自建 MJCF 与轮地接触；实机实时性（issue 报告 20 Hz 不稳）未验证 | L1 Go2；L3 要自建 Go2-W 模型；L4 因定位依赖基本不可达 | 学习先验加采样 MPC 已被 ProxPI、TD-CD-MPPI、SGPS、Residual MPC 占据 | C（原 A 条件）。G4 不成立：Go2-W 部署无外部定位。仅作对照 |
| SPI-Active | CoRL 2025 Oral（PMLR 已核） | 无许可证；IsaacGym Preview 4 + Python 3.8 + uv（已核）；TODO 里 "Release Sim2real" 未勾 | 只针对 Go2 的质量、质心、惯量与电机模型；无轮；IsaacGym 在 sm_120 上大概率要整体移植（猜想） | L1 取决于 IsaacGym 能否在 Blackwell 运行（未验证）；L4 无发布代码 | 主动激励辨识已有先例；与 PACE 同层，且 PACE 栈更新 | C（原 B）。栈旧、无 sim2real、Go2 专用 |
| Dao & Fern（本体分布匹配） | arXiv 预印本 2026-04，无录用信息 | 无代码（本轮再核：arXiv 页面与 GitHub 搜索均未找到） | Go2 实机，5 分钟数据，思想可迁移 | 只能自己重实现，L0 | 与 UAN、ASAP delta-action 重叠 | C（不变）。没有代码就没有复现 |
| Rapid Embodiment Adaptation | 预印本 2026-08 | 无代码 | Go2 锁腿与 5 kg 负载 | 无 | 历史估计加条件策略，阶段比较 §4 已列为被占据 | C（不变） |
| NaVILA | RSS 2025 | VLA 部分 Apache-2.0，权重在 HF；低层 `yang-zj1026/legged-loco`（MIT，2025-03 后无推送）要求 Isaac Lab 1.1.0、Isaac Sim 4.1、torch 2.2.2（已核） | 低层是 Go2 和 H1 的腿足速度策略，无轮；高层输出速度指令，Go2-W 上接口可行，但 8B 视觉语言模型训练与评估远超单卡本科工期 | L1 仅推理；L3、L4 工作量大 | 高层 VLA 与低层 RL 分层是现成范式，改进要在 VLN 侧，与运动控制主线脱节 | C（原 B）。低层栈停在 Isaac Lab 1.1，高层太重 |
| GRAM | RA-L 2026（既有审计） | BSD-3；README 要求 Isaac Lab 1.0.0、rsl_rl 2.0.0、Isaac Sim 4.1.0.0；environment.yaml 固定 torch 2.2.2 cu118（已核）；无权重；2026-07 仍有推送 | 已有 Go2 环境，没有轮通道，要补 4 轮速度；训练历史编码器，部署不用特权标签；机体线速度不是必需输入（未逐项核） | L1 要先从 Isaac Lab 1.0 升到 2.3，API 改名较多（评价：中等到较重）；L3 补轮通道；L4 作者有 Go2 实机但部署代码未发布 | 历史编码加自适应策略已被 ESCP、RMA 系、GRAM 自己占住（review §4）；突变时刻调度要自己加 | B（原"优先"）。方法对口，但栈迁移加新颖性拥挤，不再排前 |
| TAM | CoRL 2026（项目页确认） | 七类机械臂 preset，无 Go2-W；低层桥接未公开 | 力矩层残差，Go2-W 位置加速度接口不对口 | 无 | — | C（原 B）。只服务机械臂，Go2-W 上无意义 |
| FADA | CoRL 2026（README 自述） | Apache-2.0，Isaac Sim 5.1.0（已核，与服务器同代）；基于 Holosoma；仓库仅 G1、T1 oracle 权重；标题与 README 都是 humanoid；2026-09 推送 | 需要在 Holosoma 里新增 Go2-W 机型、资产、轮速通道（审计已指出轮速 adapter 是接口扩展）；Holosoma 是否已含 Go2 未核 | L1 对 G1/T1；L3 工作量中到大；L4 部署代码有，但对象是人形 | 固定目标域的一次离线 LoRA 适配；任务内突变、触发式适配是审计提出的空白，但 CAPABLE、SLowRL、Stability-Aligned 邻近，需查重 | B（不变）。栈对，但对象不是轮足，改造量大 |
| SimDist | RSS 2026（README 自述 "Accepted"） | MIT；有 `checkpoints/models`、`checkpoints/rl`、`datasets/real`、`datasets/sim`；`go2_ros2_ws` 含实机部署与 Docker；`docs/` 有预训练、部署、适应三步（已核）。但安装文档写 torch 2.5.1 cu121 + Isaac Sim 4.5.0，Isaac Lab 以子模块固定在 `157c6b7`。Manipulation 代码未发布 | 它是目前核到的唯一"Go2 世界模型 + 实机适应"整包。Go2-W 要改：专家 RL、数据生成、世界模型输入输出加 4 轮速度；实机需要 SLAM（point_lio_unilidar）或动捕定位，Go2-W 是否有同款雷达未核 | L1：整条 Go2 链可跑（权重数据都在），但 torch 2.5.1 cu121 无 sm_120 内核，要升到 torch ≥2.7 与 Isaac Sim 5.x（评价：中等）；L3 中等；L4 取决于定位 | 世界模型加采样规划加真实数据微调：与 RWM-U、QWM、LLA-MPPI 邻近；轮地接触建模是否空白需查重 | B（升至本表较高档）。代码完整度在已有候选里最高；风险是依赖栈旧和在线规划需要定位 |
| CaT（约束即终止） | IROS 2024 | MIT；已有 Isaac Lab 实现，文档指向 Isaac Lab 2.1.0（已核）；只有 Solo12 任务 | 算法几乎不改 PPO，约束可改成 Go2-W 的轮速、髋热负荷等；这类需求有现实依据（Go2-W 长距离导航论文报告髋关节过热） | L1 Solo12；L3 改 Go2-W 任务不重；L4 取决于部署链 | 约束 RL 已有大量先例；2024 工作，创新要靠 Go2-W 特有的约束（猜想） | B（不变）。小而干净，适合当组件，不适合当唯一底座 |
| AugMPC | RA-L 2026 | GPL-2.0，需要 xbot2、Horizon MPC、多核 CPU；实机仅 Centauro | 对轮足有参考，但栈重 | L1 都有风险 | 与另一代理的轮足检索重叠 | C（原 B）。栈与许可证都重，不适合本科工期 |
| UAN / Actuator Reality Shaping / TeAR / NeuralActuator | 预印本或机械臂专用 | UAN 为 OmniIsaacGymEnvs（已停维护）；其余无码或仅机械臂 | 与 Go2-W 腿关节执行器层相关，但没有可复现底座 | — | 作 PACE 方向的查重对象 | C |

## 3. 补查到的新候选

检索范围：WebSearch（约 14 条查询，US 地区，对 2026 年条目覆盖不稳）、arXiv 摘要页、GitHub API 与 README。没有逐条翻 CoRL 2025、RSS 2026、ICRA 2026、IROS 2025、RA-L 的官方目录，因此以下是"搜索命中且核过仓库"的结果，不是系统枚举。

| 候选 | 状态 | 代码与栈（已核） | Go2-W 适配要点 | 可达层级 | 改进空间与查重风险 | 评级与原因 |
|---|---|---|---|---|---|---|
| **LocoWM**：世界模型引导的残差适配（Zhao 等，CASIA；arXiv 2609.39179） | arXiv 预印本，2026-09-30 提交，页面无录用信息 | `zhaozijie2022/locowm`，Apache-2.0，2026-10-03 推送；README 写 Python 3.11、Isaac Sim 5.1.0、Isaac Lab 固定提交 `c91a125c73`、torch 2.7.0 cu128、rsl_rl 2.3.3（栈与服务器同代）；任务名 `Isaac-LocomotionGo2W-v1`、`Isaac-TransportGo2W-Adapter-v1`，另有 End-to-End、Reactive（无世界模型）、ReconWM 三个消融变体和评估脚本；基于 robot_lab、unitree_rl_gym。未发布权重，未见实机部署代码 | 【事实】论文 §3.1 动作是"腿位置目标 + 轮速度目标"；§4.5 在 Go2-W 实机零样本部署，任务有地形调平、加速补偿、推扰恢复；附录 B.1：策略只用本体感觉与 6 步历史，不含机体线速度（只在 critic 特权输入里）。限制段自述主实验只有 Go2-W 与三个预设任务 | L1、L3 几乎直接可达（已是 Go2-W）；L2 取决于能否对齐表格；L4 要自己写部署（rl_sar 路线，部署输入与论文一致） | 【事实】论文基线有 Base、End-to-End、React（Huang 等，2026）、Recon（Sun 等，2025）。【评价】"世界模型预测加残差校正"本身已被该论文占据；邻近：Stability-Aligned Residual Adaptation（2603.07775）、UARL。猜想的空白：世界模型不确定度给残差限幅或门控、轮打滑建模、非预设任务；均未查重 | A（条件）。唯一在平台、栈、动作接口、部署输入上同时对口的论文；条件是它只有预印本，且是三周前的新工作，同期竞争风险高，须尽早联系作者并做密集查重。它属于轮足方向，另一代理应会覆盖，本文只按重排给出位置 |
| **MoE-CTS / go2_rl_robotlab**：可靠 sim-to-real 可预测性（Wu 等，西安交大；arXiv 2602.00678） | RSS 2026（arXiv 评论栏写明，v4 2026-05-10） | `wertyuilife2/go2_rl_robotlab`，Apache-2.0，2026-10-14 推送，README 写"官方 MoE-CTS 实现"；固定 Isaac Lab 2.3.2.post1 + Python 3.11 + torch 2.7.0 cu128，自带改版 rsl_rl 3.3.0 和 robot_lab 2.3.0；任务 `RobotLab-Go2-v0`；`deploy/deploy_mujoco/deploy_go2.py` 是 MuJoCo sim2sim（torchscript，未见真机 SDK 调用）；有 RoboGauge 异步评估服务；另有 Isaac Lab 3.0 版 `wty-yy/go2_rl_lab`（license 标 NOASSERTION，需另核） | 【事实】Go2 实机（雪、沙、楼梯、坡、30 cm 障碍，最高 4 m/s），纯本体感觉。基于 robot_lab，而 robot_lab 已有 Go2W 任务，所以加轮通道有现成参照。需要补：4 轮速度动作、轮地接触、真机部署（仓库不含） | L1 很可能直接跑（栈对）；L2 有 RoboGauge 打分可对齐（README 表：0.6984 对 CTS 0.5786）；L3 中等；L4 要自己写部署 | 【评价】评价协议完整是它的最大价值：RoboGauge 能当作 Go2-W 的 sim-to-sim 预筛。MoE 加教师学生并行训练（CTS）；MoE 腿足策略先例较多，改成"轮式、步行、混合"专家路由是猜想，需查重 | A（条件）。栈最新、有实机、有评估套件；缺点是 Go2 无轮，且主贡献是策略结构与评估，不是适应机制 |
| **MPC-Injection**（Xing, Ree, Plancher；arXiv 2606.26392） | 评论栏写 CoRL 2026，页面未更多说明 | 页面无代码链接，未找到仓库 | Go2 实机，往 off-policy RL 注入 MPC 转移 | 无代码，只能重实现 | 与 AMP、奖励塑形对照 | C。无代码 |
| **GenPO**（Ding 等；NeurIPS 2025） | NeurIPS 2025（已核） | `wadx2019/genpo`，BSD-3，2026-01 推送；README 要 Isaac Sim 4.5 + torch 2.5.1 cu121，示例只给 `Isaac-Ant-v0` | 论文基准含 `Isaac-Velocity-Rough-Unitree-Go2-v0`，是否有 Go2 实机本轮没核到 | 栈要升级（sm_120） | 扩散策略加 on-policy RL，方法层贡献，与运动控制主线关系弱 | C。无实机证据，栈旧 |
| **FPO / FPO++**（Yi 等；arXiv 2602.02481） | 预印本，v2 2026-10-13 | 页面只有项目页，无仓库链接 | 实机为两台人形，不是四足 | 无 | — | C |
| **SAC 追上 PPO**（Sabatini, Li, Hutter；arXiv 2605.24975） | 预印本 | 页面无代码；用 Isaac Lab | 平台未指明 Go2；价值在 off-policy 实机微调 | 无 | 与 SLowRL、RWM 系邻近 | C，仅作查重 |
| **Diffusion-MPC**（Huang 等；arXiv 2510.04234） | 预印本 | 仅项目页站点仓库，无算法代码 | 实机腿足，机型页面未写 | 无 | — | C |
| **REAL**（Liu 等；arXiv 2603.17653） | 预印本 | 页面称代码"将发布"，未见仓库 | Go2 实机跑酷，需要深度相机，Go2-W 无对应硬件（未核） | 无 | — | C |
| **DreamTIP、LLA-MPPI、Safe RL 屏蔽（2610.20255）、HA-Teacher** | 见各自页面 | DreamTIP、LLA-MPPI 无代码；2610.20255 为 MJX 仿真无实机；HA-Teacher 仓库为 IsaacGym Preview 4 | — | — | — | C |
| `unitree_rl_lab`（工程） | 非论文 | 已核，Isaac Sim 5.1 / Isaac Lab 2.3.0 | 官方 Go2 环境，没有 Go2-W，部署有 C++ | 作环境底座 | — | 不评级，建议作为与 robot_lab 并列的参照 |

本轮检索的负面结论（均为检索范围内）：
- 没有找到 Go2 / Go2-W 上"论文已发表、官方代码在 Isaac Lab 2.x 以上、含实机部署代码"的整包。最接近的是 SimDist（有实机部署，但栈旧）和 MoE-CTS（栈新，但部署只有 MuJoCo）。
- 实机部署代码这一环，几乎每个仓库都缺，需要自己用 `rl_sar` 或 Unitree SDK 补。这一点对所有候选相同，不构成区分。

## 4. 前 5 名

1. **LocoWM**（A 条件）。唯一同时满足 Go2-W 动作接口、Isaac Sim 5.1 / torch 2.7 cu128、部署输入无机体线速度、有 Go2-W 实机和消融变体的论文。复现能直接做到 L3。主要风险：预印本、三周前才出现、与同类残差适配工作竞争。若选它，第一周要做密集查重并联系作者。
2. **MoE-CTS（go2_rl_robotlab）**（A 条件）。RSS 2026、栈最新、有实机、评估套件可直接用作 Go2-W 的预筛。缺口是 Go2 无轮、无真机部署代码，改进要自己从"轮足专家分工"或"评估驱动的策略选择"里找，创新性比第 1 名更依赖自己的设计。
3. **PACE**（B，作为底座）。复现最稳，但创新空间已被第三方 Go2 仓库、作者同事、轮足工作占去一部分。更适合作为第 1 或第 2 名之上的"仿真对齐"组件，而不是单独的基础论文。
4. **SimDist**（B）。唯一带权重、真实数据、实机部署文档的 Go2 世界模型整包。条件是升级 torch 与 Isaac Sim，并解决定位。适合想做"世界模型加真实微调"路线的情况。
5. **FADA**（B）。栈与服务器同代，少样本执行适配，空白点（任务内突变、触发式适配）有审计支撑。代价是对象是人形，要在 Holosoma 里新增 Go2-W。GRAM 与 CaT 并列第六：前者栈要迁移，后者创新空间小。

与此前排序的变化（评价）：
- PACE 从首选降为组件级；DIAL-MPC 因外部定位依赖降到 C；GRAM 因栈与拥挤度降到 B。
- 新栈且直接对口 Go2-W 的 LocoWM 与 MoE-CTS 升到最前，二者都是此前没有进入筛选的新发现。
- SimDist、CaT 的价值上升，原因是双平台门槛取消后，它们的"仅 Go2 / 仅腿足"不再扣分。

## 5. 未覆盖点与需要核对的事项

1. 检索缺口：没有遍历 CoRL 2025、RSS 2026、ICRA 2026、IROS 2025、RA-L、T-RO、Science Robotics、NeurIPS/ICLR 的官方目录；搜索引擎是 US 地区标准模式，对 2026 年条目覆盖不稳。因此"没找到"不代表不存在。
2. 新候选只读了 arXiv 摘要页、README 和仓库目录；LocoWM 读了论文 HTML 前 10 万字符，MoE-CTS 没有读正文。两者的消融、种子数、实机次数未核。
3. 没有核对：LocoWM 与 MoE-CTS 的 Isaac Lab 提交能否在 sm_120 上跑通（需服务器实测）；Holosoma 是否已含 Go2 资产；Go2-W 是否装有 SimDist 所需的雷达；Go2-W 是否开放 `lowcmd`（影响 PACE、SPI-Active）。
4. 发表状态依据：MoE-CTS 的 RSS 2026 来自 arXiv 评论栏与仓库 README，没有到 RSS 官网二次核对；SimDist 的 RSS 2026 来自仓库 README；FADA 的 CoRL 2026 来自仓库 README；MPC-Injection 的 CoRL 2026 来自 arXiv 评论栏。
5. LocoWM 的世界模型与残差机制和 `React (Huang et al., 2026)`、`Recon (Sun et al., 2025)` 的差别未读原文，改进点的新颖性必须在选定后逐项查重。
6. 本文不覆盖轮足专门方向，另一代理负责；LocoWM 在检索中偶然命中，仅按重排给出位置，需与其结果合并。
7. 未验证项：`godhandcrash/go2-pace-sim2real` 的质量、是否真的在实机运行，只读了 README 自述。
