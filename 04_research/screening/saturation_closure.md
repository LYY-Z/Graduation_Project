# 轮足 + 学习预印本全量登记（arXiv，2024-01 至 2026-11-25）

日期：2026-11-25。**范围已缩小**：协调方按用户决定改为"只做预印本部分"，即原任务 1（arXiv 轮足 + 学习全量登记）。引文闭合、CoRL 2026 补漏、workshop 列表、中文文献、多轮饱和检验**均未完成**，第 6 节只记录中止前已拿到的结果，不作结论依据。
已有普查分工：会议 → `venue_sweep_2025_2026.md`；期刊 → `venue_sweep_journals.md`；本文只补 arXiv 预印本。
标记：【核】为本次读 arXiv 摘要、comments 或 journal-ref 所得；【评】为判断。"已登记"指该 arXiv 号已出现在 `04_research/`、`06_reports/` 任一文件里（共 397 个 arXiv 号）。

---

## 1. 检索记录

接口：arXiv API（`export.arxiv.org/api/query`），按提交日期倒序，每页 300 条，在客户端按首版日期 ≥ 2024-01-01 过滤；每次请求间隔 3.2 s。脚本和原始 JSON 放在会话 scratchpad 的 `satclose/` 目录（`arx.py`、`arx2.py`、`arx3.py`、`merged.json`）。

| 轮次 | 查询式 | ≥2024 命中（去重后） | 新增 |
|---|---|---|---|
| R1 短语 | 28 条 `ti:"…" OR abs:"…"`，限 `cat:cs.RO OR abs:reinforcement OR abs:learning`：wheel-legged、wheeled-legged、wheeled legged、legged-wheeled、wheeled quadruped(al)、wheel-leg、hybrid wheel、Go2-W/Go2W、B2-W/B2W、wheeled biped(al)、roller skating、skating、leg-wheel、quadruped with wheels、wheeled humanoid、transformable wheel 等 | 118 | 118 |
| R2 词元 | 不限类目。`abs:{wheel,wheels,wheeled} AND abs:{legged,legs,leg,quadruped,quadrupedal,biped,bipedal,humanoid}` 共 24 条，`ti:` 同组合 24 条；另有 Go2+wheel\*、Go2-W、B2W、"B2-W"、skating/skates/skate + robot/legged、ANYmal+wheels、Tron1、Diablo、Ascento、Swiss-Mile、LimX、"leg-wheel"、"wheel-leg"、hybrid locomotion+wheel\*、driving and walking、walking and driving、rolling and walking、wheeled locomotion+reinforcement、M20、Lite3+wheel\*、transformable+wheel+legged | 271 | **+153** |
| R3 补漏 | 19 条：skateboard(ing)、"passive wheels"、"wheeled feet"、"wheel-foot"、"foot-wheel"、Centauro、"hybrid locomotion"、"wheel-leg hybrid"、rolling+quadruped+RL、driving+legged+RL、"in-wheel"+robot、wheeled+"sim-to-real"、"Swiss Mile"、Unitree+wheel\*、"Deep Robotics"、Lynx+robot、tire+legged、slip+wheel\*+legged | 49 个新候选（"in-wheel" 带来的 152 条噪声已剔除） | 主动驱动轮的轮足 + 学习：**0**；被动轮/滑板：+4；Centauro 上的 LLM 规划：+2 |

要点：
- **R1 漏检严重**：arXiv 对带连字符的短语检索很不稳定，`all:"wheel-legged"` 历来只命中 77 条。而 `abs:wheeled AND abs:legged` 命中 235 条，和 arXiv 网页检索 "wheeled legged"（236 条）一致。arXiv 会做词干归并（wheel/wheels/wheeled、leg/legs/legged 归为同一词），所以 R2 里同义组合的命中数完全相同。R1 查到的条目中只有 4 篇不在 R2 里，都无关（差速车、空地机器人、软体蛇、空中机械臂）。
- **召回自检**：把项目已有轮足笔记（`wheel_legged.md`、`go2w_rerank.md`、`round3_policy_wheel.md`、`cross_domain_sweep.md`、`options_overview.CN.md`）里的 35 个 arXiv 号与收割结果比对。漏掉 15 个，逐个看过，全部不是轮足论文（对称性、MoE-Loco、热约束、Flow PG 等）。因此"已知轮足预印本"的召回率为 100%。
- **停止依据**：R3 用 19 条新查询式没有新增任何"主动驱动轮 + 学习"的论文。中止前的引文数据（第 6 节）里，S2 返回的 548 篇 2024 年后施引文献中也**没有**新的 arXiv 轮足预印本。这两点是本次的饱和证据。它只覆盖预印本，不覆盖期刊和会议。

---

## 2. 判定口径

- **收录**：平台带轮且腿参与运动，包括主动驱动轮的轮足（四足、双足、人形）、被动轮滑或滑板、轮式人形；方法含学习（RL、模仿、学习型估计或模型、VLA/大模型）。
- **单列不入主表**：轮足但非学习（MPC、WBC、机构设计），只列与对齐有关的条目（第 4 节）。
- **排除**：纯轮式车、空地两栖、只在摘要里拿"wheeled robots"作对比的足式论文、物理学或生成视频等误命中。
- 录用状态取自 arXiv comments 或 journal-ref；没有写明的记为"预印本"。会议和期刊普查对这类论文另有判定，以那两份为准。代码列：摘要或 comments 里有 github 或项目页的记"项目页/代码"，否则记"—"（未逐篇查仓库）。

---

## 3. 轮足 + 学习预印本完整清单（69 篇）

### 3.1 主动驱动轮的轮足（四足、双足、轮足人形），共 43 篇

| # | arXiv | 标题（简） | 平台 | 主题 | 录用状态【核】 | 代码 | 已登记 |
|---|---|---|---|---|---|---|---|
| 1 | 2402.06143 | RL for Blind Stair Climbing with Legged and Wheeled-Legged Robots | 多平台，含轮足双足 | 盲爬楼梯，位置式指令 | 预印本 | 视频 | 是 |
| 2 | 2403.10948 | Wheeled Humanoid with Unknown Payloads: Equilibrium Point Estimation via Real-to-Sim Adaptation | 轮足人形 | **real-to-sim**，估计质量和质心 | 预印本 | — | 是 |
| 3 | 2403.16535 | Arm-Constrained Curriculum Learning for Loco-Manipulation of the Wheel-Legged Robot | 轮足 + 机械臂 | 移动操作，课程学习 | 预印本 | 项目页 | 否 |
| 4 | 2405.01792 | Learning Robust Autonomous Navigation and Locomotion for Wheeled-Legged Robots（Lee 等） | ANYmal 轮足 | 运动 + 导航 | Science Robotics 2024 | — | 是 |
| 5 | 2409.09845 | Friction-Aware Safety Locomotion for Wheeled-legged Robots using VLM and RL | 轮足双足 | VLM 预估摩擦系数后输入 RL | Humanoids 2025 | — | 是 |
| 6 | 2410.12345 | A Data-driven Contact Estimation Method for Wheeled-Biped Robots | 轮足双足 | 接触估计，更新步从真机力矩学得 | 预印本 | — | 否 |
| 7 | 2412.03012 | Whole-Body Loco-Manipulation … Wheeled-Quadrupedal-Manipulator | 轮足四足 + 机械臂 | 6D 末端位姿跟踪 | 预印本（会议普查记为 RA-L） | 项目页 | 是 |
| 8 | 2503.10028 | LEVA: high-mobility logistic vehicle with legged suspension | 腿式悬架轮式车 | RL 爬楼梯 | ICRA 2025 | — | 否 |
| 9 | 2506.05516 | Learning to Recover（L2R）：wheel-leg coordination for fallen robots | 轮足四足 | 跌倒恢复 | 预印本 | 项目页 | 是 |
| 10 | 2506.11470 | Multi-Loco（RL 增强扩散，跨形态） | 含轮足 | 跨形态 | CoRL 2025（会议普查） | — | 是 |
| 11 | 2509.02986 | CTBC: Contact-Triggered Blind Climbing for Wheeled Bipedal Robots | 多台轮足双足（轮径、胎材不同） | 爬台阶 | 预印本 | — | 是 |
| 12 | 2509.23745 | LocoFormer | 足式 + 轮式（未见过的形态） | 长上下文适应 | CoRL 2025 | — | 是 |
| 13 | 2510.09980 | ATRos | 轮足四足 | 节能敏捷混合运动 | IROS 2025 轮足 workshop | — | 是 |
| 14 | 2510.23902 | Stand, Walk, Navigate（低成本轮足四足） | 低成本轮足四足 | 恢复感知的视觉导航 | IROS 2025 轮足 workshop | — | 是 |
| 15 | 2601.10723 | Energy-Efficient Omnidirectional Locomotion for Wheeled Quadrupeds | 改装 Go1 轮足 | 功率预测选步态 + 残差 RL | IROS 2025 | 项目页 | 是 |
| 16 | 2603.10878 | RL-Augmented MPC for Non-Gaited Legged and Hybrid Locomotion | Centauro 轮足人形（120 kg） | RL 出步态，MPC 执行；**不做 DR 零样本上真机** | 预印本 | 代码 | 是 |
| 17 | 2604.23761 | AWARE: Reflexive Obstacle Evasion | DEEP Robotics M20 | 分层 RL 反射式避障 | RA-L 2026 | 项目页 | 是 |
| 18 | 2605.13058 | MUJICA | **Go2-W** | 多技能统一，含电机约束 | 预印本（会议普查记为 ICRA26） | — | 是 |
| 19 | 2606.01332 | S2M-Trek: multi-sphere transport | 轮足四足 | 背上运球，Deep Sets | 预印本（会议普查记为 CoRL26） | — | 是（会议普查） |
| 20 | 2606.14270 | Robust Fall Recovery for Armless Bipedal-Wheeled Robots（FTSR） | 轮足双足 | 跌倒恢复，力引导师生 | RA-L 2026 | 项目页 | 是（会议普查） |
| 21 | 2606.21387 | Long-Distance Navigation of Go2-W using DRL（Matsuzawa） | **Go2-W** | 长距离导航，抬腿散热 | 预印本 | — | 是 |
| 22 | 2606.26313 | Racing a Wheeled Quadruped: Active Load Transfer Mitigation | **Go2-W** | 自行车模型 MPC + 低层 RL，主动侧倾 | AVEC 2026 | 代码（只有 MPC） | 是 |
| 23 | 2606.30243 | KYON: semi-modular wheel-legged quadruped | KYON 轮足 + 双臂 | 平台论文，WBC + RL | 预印本 | — | 否 |
| 24 | 2607.02205 | Actuator Reality Shaping | 机械臂、伺服、**轮足（斜坡）**、人形 | 改真机执行器去贴合仿真 | 预印本 | 项目页 | 是 |
| 25 | 2608.01015 | KING: kinematic GNN for legged and wheeled robots | 足式 + 轮式 | 学习型运动学里程计，可少样本适配 | IROS 2026 | 项目页 | 是 |
| 26 | 2608.20251 | Video2DoorTraversal | 轮足移动操作 | 单段视频 real-to-sim 门孪生 | 预印本 | 项目页 | 否 |
| 27 | 2609.03889 | FWBC-VLA | 轮足移动操作（摘要级） | VLA + 力感知 WBC | 预印本 | — | 是 |
| 28 | 2609.13779 | Force-Aware RL with Hybrid Sensorless Force Estimation | 轮足 + 机械臂 | 无传感器力估计（模型 + 残差网络） | 预印本 | — | 是 |
| 29 | 2609.18193 | WAVE-Go | 轮足 | 世界模型图像目标导航 | 预印本 | 代码 | 是 |
| 30 | 2610.00878 | UniTrackPLA | Go2-W（摘要级） | 全景-语言-动作，导航与跟随 | 预印本 | 项目页 | 否 |
| 31 | 2610.07409 | RACER: Residual-Adaptive Estimation for Wheeled-Quadruped Racing | 轮式四足 | 规划器单轮车模型加神经残差，LoRRA 仿真到真机低秩微调 | 预印本 | — | 是 |
| 32 | 2610.18093 | LynxScenes dataset | LYNX M20 | 室外轮足感知/导航数据集（833 h） | 预印本 | — | 否 |
| 33 | 2610.23883 | Wheeled-Quadruped Long-Range Throwing | 轮足四足 + 机械臂 | SQP + 参考引导 RL | 预印本 | — | 否 |
| 34 | 2610.26550 | Learning Wheel Motion Uncertainty for LIO on Quadrupedal Wheel-Legged Robots | 轮足四足 | **学习每轮、分方向的打滑协方差** | 预印本 | 项目页 | 是 |
| 35 | 2610.29845 | RangeNav | B2-W 等（摘要级） | LiDAR 预训练导航 | 预印本 | 项目页 | 否 |
| 36 | 2610.33172 | RAIWAY: large-wheeled bipedal, contact-informed blind locomotion | 自研轮足双足（20 英寸轮） | 仿真接触蒸馏成潜变量 | RA-L 2026 | 视频 | 是 |
| 37 | 2610.33584 | HA-DiPO: heterogeneous cooperative transport | 异构足式（含轮足，摘要级） | 多智能体扩散策略 | 预印本，投 RA-L | 项目页 | 否 |
| 38 | 2611.24155 | BEV-Diffusion: cross-robot traversability | 跨机器人（含轮足，摘要级） | 纯相机可通行性导航 | 预印本 | — | 否 |
| 39 | 2611.25788 | Passage-Conditioned Navigation for Wheeled-Legged Robots | 轮足 | 示教通行条件导航 | 预印本 | — | 否 |
| 40 | 2409.01326 / 2408.08282 | Centauro 上的 LLM 行为规划（与 HYPERmotion 2406.14655 同组） | Centauro 轮足人形 | LLM/学习型高层规划 | IROS 2024 等 | 项目页 | 否 |
| 41 | 2510.09963 | LLM-HBT: heterogeneous robots behavior tree | 异构（含轮足） | LLM 行为树 | 预印本，投 ICRA26 | — | 否 |
| 42 | 2602.17393 | Contact-Anchored Proprioceptive Odometry（足式与轮足） | 四足 + 轮足 | 本体里程计（模型法，作对齐参考） | 预印本 | — | 是 |
| 43 | 2605.10696 | VRA: voltage-constrained actuation | **轮足四足实机** | 电压可实现加速度接口（模型法） | RSS 2026 | — | 仅会议普查有标题 |

（#42、#43 不是学习方法，但与第 4 节的对齐主题直接相关，所以留在主表，不另列。）

### 3.2 被动轮滑、滑板，共 17 篇

| # | arXiv | 标题（简） | 平台 | 录用状态 |
|---|---|---|---|---|
| 44 | 2402.04374 | SKOOTR 三足滑行机器人 | 自研 | 预印本（以设计为主） |
| 45 | 2409.07846 | Learning Skateboarding for Humanoid（REEM-C，仅仿真） | 人形 | 预印本 |
| 46 | 2503.01842 | DHAL: Legged Locomotion Meets Skateboarding | 四足 | RSS 2025 |
| 47 | 2505.06561 | Quadrupedal Skateboard Mounting via Reverse Curriculum | 四足 | 预印本 |
| 48 | 2510.05001 | TARS3D: walking and rolling（含 RL） | 自研 | Humanoids 2025 |
| 49 | 2601.04948 | SKATER: humanoid roller-skate swizzles | 人形 | Humanoids 2026 |
| 50 | 2602.03205 | HUSKY: Humanoid Skateboarding | G1 | RSS 2026 |
| 51 | 2602.09370 | PAPL: quadruped skateboard riding | 四足 | ICRA 2026 |
| 52 | 2603.18408 | Quadrupedal Skating co-design（RL + BO，被动轮） | 四足 | 预印本（会议普查记为 ICRA26） |
| 53 | 2606.31807 | RL Inline Skating Humanoid | 人形 | IROS 2026 |
| 54 | 2607.10815 | Humanoid Roller-Skating via AMP | 人形 | CLAWAR 2026 |
| 55 | 2610.16457 | SHOES（含溜冰鞋类足端变化的适应） | Go2 | CoRL 2026 |
| 56 | 2610.25962 | SkateNav: passive-wheel quadruped navigation | 被动轮四足 | 预印本 |
| 57 | 2611.26054 | Reference-Free Humanoid Skateboarding（K1） | 人形 | Humanoids 2026 |
| 58 | 2604.24916 | asRoBallet（球形人形，轮-球-地摩擦 sim2real） | 球平衡人形 | RSS 2026 |
| 59 | 2610.04238 | Humanoid Rickshaw Pulling（拖带轮式载荷） | 人形 | 预印本 |
| 60 | 2607.16302 | Rideable two-wheeled robot with quadruped form | 两轮 + 四肢 | 预印本 |

### 3.3 轮式人形或轮式底盘人形（腿不着地或只做升降），共 9 篇

2505.19530（触觉遥操作举重物）、2508.09846（双边遥操作，T-RO）、2407.12189（双边遥操作）、2609.11357（形态感知重定向 + 师生 DAgger）、2610.08381（From Legs to Wheels 重定向）、2611.03648（Pixel 全栈移动操作）、2604.21541（X2-N 可变形轮足人形，RA-L，以设计为主）、2611.07560（轮式人形标定）、2406.14655（HYPERmotion）。【评】这类平台和 Go2-W 的轮足动力学基本不相干，只作完整性登记。

**规模小结**：主动驱动轮的轮足 + 学习共 41 篇（#1–#41），再加 2 篇作对齐参考的模型法（#42–#43）；被动轮或滑板 17 篇；轮式人形 9 篇。其中 3.1 节里**本项目此前未登记的有 14 篇**（表中"已登记 = 否"），没有一篇属于"仿真—真机对齐"类（见第 5 节）。

---

## 4. 与"轮足仿真—真机对齐 / 执行器辨识 / 轮-地接触或打滑 / 车辆动力学借鉴"相关的条目

| arXiv | 和对齐的关系【核】 | 与 PACE 轮足对齐方向的距离【评】 |
|---|---|---|
| 2607.02205 Actuator Reality Shaping | 不改仿真，改真机：每个关节加二自由度前馈-反馈控制器，使闭环贴合仿真里的理想二阶参考；包含一台**速度控制轮的轮足机器人零样本上斜坡**的演示 | 方向相反（改真机，不改仿真），而且要求能改关节级低层。Go2-W 的低层是否开放尚未确认。已在 `sysid_plus_delta_action.md` 查重过，**不构成占位** |
| 2610.07409 RACER | 在 MPPI 的单轮车**运动学**模型上加神经残差，用来学 RL 速度跟踪器的闭环误差；先用仿真预训练，再用少量真机数据做低秩（LoRRA）微调；仿真中测试了地面系数和关节增益的域差 | 残差加在规划层，不是物理参数辨识，也不是关节或轮的执行器对齐。已登记 |
| 2606.26313 Racing a Wheeled Quadruped | **Go2-W 自行车模型**（车辆动力学）MPC，膝关节当主动悬架抗侧倾；低层 RL | 车辆动力学借鉴的**直接先例**，但只用于规划，没有建模轮胎滑移，也没有做仿真对齐。已登记（`cross_domain_sweep.md`） |
| 2403.10948 Wheeled Humanoid Real-to-Sim | 用数据驱动方法估计总质量和质心，把更准的非线性模型注入刚体仿真（real-to-sim），以减小仿真与真机差距 | **最接近"轮足 real-to-sim"的预印本**，但辨识对象是载荷的惯量参数，不是执行器或轮-地参数，服务对象是模型法控制器，平台是两轮人形。已登记 |
| 2603.10878 RL-Augmented MPC（Centauro） | 声称不做 DR 也能零样本上轮足人形真机 | 靠 MPC 吸收差距，没有对齐过程。已登记 |
| 2409.09845 Friction-Aware（VLM + RL） | 预测摩擦系数后作为 RL 的输入，针对轮足打滑 | 属于"把摩擦当观测"，不是辨识仿真参数。已登记 |
| 2610.26550 Wheel Motion Uncertainty LIO | 用学习方法得到每个轮子、分方向的打滑与失接触不确定性 | 只用于状态估计，可作为"轮-地打滑可学习"的旁证。已登记 |
| 2610.33172 RAIWAY | 把仿真里的轮-地多接触事件蒸馏成潜变量，部署时由本体感觉推断 | 属于隐式接触适应，没有显式对齐。已登记 |
| 2410.12345 Wheeled-Biped Contact Estimation | 贝叶斯滤波，更新步由真机力矩数据学得 | 接触估计，与对齐无关。**新登记** |
| 2608.01015 KING | 学习型运动学里程计，覆盖轮式和足式，一分钟数据即可适配新形态 | 估计层，与对齐无关 |
| 2602.17393 Contact-Anchored Odometry | 本体感觉里程计，统一处理四足和轮足 | 估计层 |
| 2605.10696 VRA（RSS 2026） | 在**轮足四足实机**上把关节加速度约束接到电压受限执行器的物理上，去掉不可实现的加速度 | 涉及执行器物理（电压、反电动势一类约束），但做的是执行层接口，不是仿真辨识。**此前只在会议普查里有标题，对齐查重未覆盖**。建议在 PACE 报告的执行器建模相关工作里补一句 |
| 2604.24916 asRoBallet | 轮-球-地滚动、侧向、扭转摩擦感知的 RL，零样本 sim2real | 平台是球平衡机器人，不是轮足；可作为"轮类接触摩擦 sim2real"的旁证。已登记 |
| 2608.20251 Video2DoorTraversal | real-to-sim 重建的是场景（门），不是动力学 | 无关 |
| 2610.38657 TERRA（R3 发现，CoRL 2026，行星车，非轮足） | 先在仿真训练世界模型，部署时用奖励加权的预测损失在线修正轮-土滑移和沉陷的模型误差 | 非轮足，属于车辆或行星车侧的在线适应参考。**新登记**，可放进车辆动力学借鉴的相关工作 |
| 2504.08604 Neural Fidelity Calibration（R3） | 扩散模型在线校准仿真物理系数和残差保真域 | 通用 sim2real 校准，摘要未写轮足。**新登记** |

---

## 5. 对已有结论的影响

**"PACE 轮足（执行器或轮-地）仿真—真机对齐方向空白"的判断不变。**
1. 在 41 篇"主动驱动轮的轮足 + 学习"预印本里，没有一篇做"用真机数据辨识仿真里的轮或腿执行器参数、或轮-地参数，再训练或评估 RL 策略"。最接近的四篇各差一层：RACER 加在规划层残差上；Actuator Reality Shaping 改的是真机而不是仿真；2403.10948 辨识的是载荷惯量，服务于模型法控制器；Racing Go2-W 用的是车辆模型规划，不做对齐。这四篇都已在 `novelty/sysid_plus_delta_action.md` 或 `cross_domain_sweep.md` 登记过。
2. 新登记条目里，与对齐沾边的只有 VRA（2605.10696，执行器电压约束，轮足实机）、TERRA（2610.38657，行星车轮-土在线适应）和 NFC（2504.08604，通用仿真系数校准）。三篇都不是"轮足 + 执行器或轮-地参数辨识 + RL"，所以只需作为相关工作补引，**不改变空白判断**。
3. Go2-W 专用预印本共 5 篇：MUJICA、Matsuzawa、Racing、UniTrackPLA，以及只在摘要提到 Go2-W 的 RB-TRG（2608.16433，规划）。其中 UniTrackPLA 是新登记，但属于 VLA 导航，与对齐无关。
4. 局限：本文只覆盖 arXiv。期刊和会议上**未挂 arXiv** 的轮足学习论文（见第 6 节的 S2 结果）只做了标题级核对，以期刊和会议两份普查为准。

---

## 6. 中止前已拿到的其他结果（保留，未完成，不作结论依据）

- **引文闭合（部分）**：OpenAlex 的匿名每日额度在本次运行中耗尽（429，Retry-After 约 8.6 h），所以改用 Semantic Scholar 取施引文献。锚点为 PACE、Lee 2024、MUJICA、FLORES、ATRos、Matsuzawa、Multi-AMP、Keep Rollin'、Rolling in the Deep、WB-MPC gait。Bjelonic 的 Offline Motion Libraries 论文我给出的 arXiv 号错了（2112.01284 实为天文论文），已剔除，未补查。得到 2024 年后施引文献 548 篇（去重），标题含 wheel/skat 等词的 180 篇，其中 150 篇不在 arXiv 收割里，**全部是期刊或会议论文，没有 arXiv 号**。只有 4 篇带 arXiv 号，都不是轮足。这一结果支持"预印本已饱和"。
  - 这 150 篇里，标题显示属于学习类或与对齐相关的举例如下（只看了标题，留给期刊和会议普查核对）：Residual Policy Optimization With Trust Region（轮足，T-ASE 2025）、Self-Adaptive RL Control of an Ankle-Equipped Wheeled-Legged Robot（ROBIO 2025）、Safe RL for High-Obstacle Climbing in Heavy Wheeled-Legged Robots（CEP 2026）、Learning-Based Hybrid Locomotion for a Heavy Wheeled-Legged Robot（JIRS 2026）、Bio-inspired Sparse Expert Control（Defence Technology 2026）、Sparse MoE for Bipedal Wheel-Legged（Frontiers RAI 2026）、DRL in MoE for Blind Wheeled-Legged Quadrupedal Locomotion（2024）、State Estimation for Wheeled-Legged Robot with Slip Detection（ROBIO 2024）、Slip-Aware State Estimation for Skid-Steering Wheel-Legged Vehicles（CVCI 2025）、Vision-based Dynamic Modeling of Wheeled-Legged Robot Considering Slippage（Robotica 2024）、Collaborative Control … Considering Actuators Characteristics（2024）、Passive Wheels on Legged Robots: a Survey（Frontiers RAI 2026）。【评】从标题看，没有一篇是"轮足执行器或轮-地参数辨识 + RL 对齐"，但只看了标题。
  - **PACE 的施引文献**（S2 与 OpenAlex 合并，去重约 40 篇）逐条看了标题：**没有一篇是轮足**。与执行器对齐相关的有 Actuator Reality Shaping、Contact-UAN、高减速比四足扩展执行器辨识（Machines 2026）、Extending the Speed Limit via Refined Actuator Modeling（RA-L 2026）、What good is a good robot model?（IROS 2026）、Constraint-Aware Friction Identification for Parallel Legs（AIM 2026）、From Temperature-Limited to Battery-Limited。这说明 PACE 的后续工作目前都在足式或人形上，轮足仍是空位。
- **IROS 2025 轮足 workshop**（"The Future of Hybrid Mobility: Innovations in Wheeled-Legged Robots"，2025-10-24，杭州）：官网 sites.google.com/view/wheeledleggedrobotics 的 "Accepted Contributions" 页至今仍写着 "to be announced in October 2025"，**没有论文列表**。只通过 arXiv comments 确认了 2 篇：ATRos（2510.09980）和 Stand, Walk, Navigate（2510.23902）。
- **CoRL 2026 补漏**：脚本已写好（用非官方索引 corl26.md 中的 534 个 arXiv 链接批量取摘要，其余按标题匹配 arXiv），按指令中止，未运行完。
- **中文文献**：知网 kns.cnki.net 的证书与域名不符，curl 超时；百度学术返回"百度安全验证"（人机验证）；万方页面靠 JS 渲染，无法直接取结果。WebSearch 两轮没有找到 2024 年后"轮足/轮腿 + 强化学习"的中文学报或学位论文，只找到四足 RL 综述和中山大学学报的轮足建模论文（非学习）。结论是不可访问，未检索充分。
