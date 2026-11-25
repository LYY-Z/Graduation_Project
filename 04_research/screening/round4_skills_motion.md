# Round 4：运动技能与行为生成方向筛选（Go2-W）

> 检索日期：2026-11-25。检索手段：WebSearch + 打开 arXiv 摘要页、项目页，用 GitHub API 查仓库最近提交与 star 数。
> 本轮刻意避开：sim-to-real 执行器辨识/对齐、部署期适应、热约束、雷达避障。这些方向只在对比时出现。
> 标注约定：【已核实】指我打开过原始页面；【未核实】指只见到搜索摘要或二手转述；"venue 未列"指 arXiv 页面没有 journal-ref 或 comments 写明会议/期刊。

---

## 0. 一句话结论

轮足平台的"技能生成"这块，近两年真正用 Go2-W 做的工作很少：只查到 MUJICA、L2R、ATRos、长距离导航这几篇，且都没有开源代码。另一方面，运动模仿的工具链已经成熟，MimicKit 自带 Go2 的 DeepMimic/AMP/ADD 配置。两边一对，出现一个具体的空白：**现有运动数据（狗的动捕、Go2 的运动库）都没有轮子，怎样把它们用到 16 自由度、会滚动的轮足上？** 这个问题是轮足独有的，有现成代码可以复现，也能上实机，查重初判空白较大。我把它作为首推方向（方向 A），另给两个备选：B 是轮足特技的迭代模仿，C 是从无标签数据中发现并切换轮/腿模式。

---

## 1. 候选论文（12 篇主表 + 若干补充）

| # | 论文 | 发表状态（出处） | 代码（实际查看） | 平台 |
|---|---|---|---|---|
| 1 | MimicKit: A RL Framework for Motion Imitation and Control（Peng） | arXiv 2510.13794，venue 未列，属于框架/技术报告【已核实】 | github.com/xbpeng/MimicKit，Apache-2.0，2442★，最近提交 2026-11-18；支持 Isaac Gym / Isaac Lab 3.0-EA / Newton；仓库中有 `deepmimic_go2_*`、`amp_go2_*`、`add_go2_*` 配置和 `dataset_go2_locomotion.yaml`【已核实】 | Go2（仿真）、G1、人形 |
| 2 | Walk Like Dogs: Learning Steerable Imitation Controllers for Legged Robots from Unlabeled Motion Data（Kang, Coros 等，ETH） | arXiv 2507.00677，v1 2025-07，v2 2026-03-04，venue 未列【已核实】 | 未找到代码【已核实：arXiv 页无链接】 | 实机型号页面未写明【未核实】 |
| 3 | Flip Stunts on Bicycle Robots using Iterative Motion Imitation（IMI，RAI Institute） | **ICRA 2026**（项目页 imi-umv.github.io 与 RAI 页面）【已核实】 | 未见代码【已核实：项目页无链接】 | UMV 两轮自行车机器人 |
| 4 | ZEST: Zero-shot Embodied Skill Transfer for Athletic Robot Control | arXiv 2602.00401（2026-01），venue 未列【已核实】 | 无 | Atlas、G1、**Spot**（从关键帧动画学到连续后空翻） |
| 5 | SMP: Reusable Score-Matching Motion Priors for Physics-Based Character Control（Mu, …, Peng） | arXiv 2512.03028；项目页写的是 **ACM TOG / SIGGRAPH 2026**【已核实项目页表述】 | MimicKit 的方法列表中有 SMP【已核实】 | 仿真角色（非机器人实机） |
| 6 | DHAL: Discrete-Time Hybrid Automata Learning: Legged Locomotion Meets Skateboarding（UMich） | **RSS 2025**（roboticsproceedings.org/rss21/p127）【已核实】 | github.com/UMich-CURLY/DHAL，41★，最近提交 2025-05-12，基于 Isaac Gym + legged_gym/rsl_rl，无部署代码【已核实】 | Go1 + 滑板（四足踩被动轮） |
| 7 | Energy-Efficient Omnidirectional Locomotion for Wheeled Quadrupeds via Predictive Energy-Aware Nominal Gait Selection | **IROS 2025**，pp.18919–18925（arXiv 2601.10723 的 journal-ref）【已核实】 | 未列代码，只给项目页 sites.google.com/view/switching-wpg【已核实】 | 改装的 Go1 轮足（16 自由度） |
| 8 | Learning to Recover: Dynamic Reward Shaping with Wheel-Leg Coordination for Fallen Robots（L2R） | arXiv 2506.05516，v2 2025-10-08，venue 未列【已核实】 | 项目页有 "Code" 按钮，但看不到 URL【未核实】 | **Go2-W** 及另一轮足平台 |
| 9 | MUJICA: Multi-skill Unified Joint Integration of Control Architecture for Wheeled-Legged Robots | arXiv 2605.13058（2026-05），venue 未列【已核实】 | 无 | **Go2-W**（全向移动、高台攀爬、跌倒恢复，加一个技能选择器） |
| 10 | Behavior Foundations for Quadruped Robots: ABot-C0 Technical Report | arXiv 2607.07370（2026-07），技术报告【已核实存在】 | 未找到仓库【未核实】 | 四足（型号未核实） |
| 11 | QuadFM: Foundational Text-Driven Quadruped Motion Dataset for Generation and Control | arXiv 2603.24021（2026-03），venue 未列【已核实】 | github.com/GaoLii/QuadFM 只有 README，写着 "will be released soon"【已核实】 | 带 Orin 的四足（摘要未写型号；搜索摘要提到 Go2 X【未核实】） |
| 12 | DiffuseLoco: Real-Time Legged Locomotion Control with Diffusion from Offline Datasets | CoRL 2024（早于 2025，作为生成式策略的基线）【已核实 PDF 标题】 | github.com/HybridRobotics/DiffuseLoco，202★，最近提交 2025-04-14【已核实】 | Go1 等 |

**补充（不单独展开）**
- **ATRos**（arXiv 2510.09980）：投稿至 IROS 2025 Workshop on Wheeled-Legged Robots；代码 "Coming Soon"；实机用 Go2W EDU，加能量感知奖励【已核实项目页】。
- **Go2-W 长距离导航**（arXiv 2606.21387，2026-06）：本体感知策略扩展到 16 自由度，并分析了关节发热。这是之前几轮的方向，这里只作对照。
- **BeyondMimic 代码** HybridRobotics/whole_body_tracking：2442★，最近提交 2026-10-16，README 写明已退役、迁移到 mjlab（3463★，最近提交 2026-11-25，MuJoCo Warp 后端）【已核实】。只有人形。
- **robot_lab**（fan-ziqi）：含 **Go2W** 资产，Isaac Lab v3.0，1989★，最近提交 2026-10-20【已核实】。可直接作为 Go2-W 的仿真底座。
- **CopyQuad**（arXiv 2610.16737，2026-10）：从单段侧视视频学狗/马步态，零样本上实机，无代码【已核实】。
- **STMR** 时空运动重定向（arXiv 2404.11557 v3 2025-07）：venue 未列，无代码【已核实】。
- **Multi-AMP 轮腿**（Vollenweider 等，arXiv 2203.14912，2022，ETH 轮腿 ANYmal）：方向 A 最接近的旧工作，查重时必须引用。
- **Pedipulate**（arXiv 2402.10837，2024，ANYmal 用腿操作）与 **Go2 后腿站立推车**（arXiv 2507.20382，Humanoids 2025，据搜索摘要【未核实】）：用腿做操作的代表工作。
- **Diff-CAST**（arXiv 2605.08804）：用扩散先验替代 AMP 判别器给风格奖励，venue 未列，无代码【已核实】。
- **MoE-Loco**（arXiv 2503.08564）：四足/双足多任务 MoE，venue 未列，无代码【已核实】。
- **UMV 系统论文**（arXiv 2602.22118）：自行车机器人用约束 RL 做跳跃、翘头、前空翻，venue 未列【已核实】。

### 1.1 逐篇要点

**① MimicKit**
- 核心：统一实现 DeepMimic（逐帧跟踪）、AMP（对抗风格先验）、ADD（对抗差分判别器）、SMP（扩散分数先验）等方法，可在多个仿真后端之间切换。
- Go2-W 上的可能创新：仓库里已有 Go2 的 DeepMimic/AMP/ADD，换成 Go2-W 资产（robot_lab 中有）后，就可以研究轮子自由度怎样参与模仿（见方向 A）。
- 难点：MimicKit 偏图形学，缺少四足实机所需的域随机化、观测噪声、ONNX 导出和 SDK 部署，这部分要自己补；可以参考 robot_lab / unitree_rl_lab 的部署流程。Isaac Lab 3.0-EA 和 Newton 理论上支持 Blackwell，但 sm_120 上的实测**未核实**，建议第一周先跑通。

**② Walk Like Dogs**
- 核心：先做运动学-动力学重定向，把无标签的狗动捕数据转到机器人形态；再用 VAE 做可操控的运动合成，RL 控制器负责跟踪。速度命令变化时，步态切换自发出现，不需要手动标注模式。
- Go2-W 创新：把"无标签数据中的模式发现"推广到"腿式模式 + 轮式模式"（见方向 C）。
- 难点：无代码，需要从 MimicKit/AMP 组件自己拼；重定向用到 IK + MPC，工程量中等。

**③ IMI（ICRA 2026）**
- 核心：参考运动可以不可行（手工绘制、轨迹优化、不顾安全约束的手动控制都行）；用 RL 跟踪后，把策略的 rollout 当作下一轮参考，迭代修正。在 UMV 上实现了首个无辅助自行车前空翻。
- Go2-W 创新：轮足特技的参考很难写出物理上可行的版本，例如滚动起跳上台、两轮"翘头"站立、带滚动的转身。IMI 的思路正好适用，而 16 自由度、混合接触的平台比 UMV 复杂得多（见方向 B）。
- 难点：无代码，但算法本身很简单（外层循环 + DeepMimic 跟踪），复现风险低。主要风险在实机特技的安全性。

**④ ZEST**
- 核心：动捕、单目视频、关键帧动画都可以作为参考，在中等强度的域随机化下零样本上实机；Spot 从关键帧学会了后空翻。
- Go2-W 意义：说明"关键帧动画加跟踪"在四足上可行，可以作为方向 B 的直接佐证和 related work。
- 难点：无代码，团队是大机构，工程细节不可复制。只作为引用。

**⑤ SMP（SIGGRAPH 2026）**
- 核心：先离线训练一个运动扩散模型，冻结后通过 score distillation 给出风格奖励。训练策略时不再需要原始数据，也不用像 AMP 那样每个控制器都重训判别器，还能把多种风格组合起来。
- Go2-W 创新：用扩散先验代替 AMP 判别器，给轮足提供"腿部风格"奖励；同时轮子自由度不进入先验，从而规避数据里没有轮子的问题（方向 A 的一个变体）。这也是"生成式模型用于运动"的一个低风险入口：部署的仍是 MLP。
- 难点：只在仿真角色上做过，四足实机未见报道；扩散先验训练和 SDS 奖励的稳定性需要摸索。

**⑥ DHAL（RSS 2025）**
- 核心：把离散混合自动机嵌进 VAE + RL，自动识别接触模式并切换，不需要事先分割轨迹；任务是四足踩滑板。
- Go2-W 创新：Go2-W 的"滚动 / 迈步 / 混合"天然是混合系统，可以用来解释和约束模式切换（方向 C）。
- 难点：Isaac Gym Preview 4 在 Blackwell 上能否运行**未核实**（存疑），可能需要移植到 Isaac Lab；仓库只有 4 次提交，没有部署代码。

**⑦ 能量感知步态选择（IROS 2025）**
- 核心：功率预测网络预测未来 1 s 内各名义步态的能耗，从中选能耗最低的，再由 RL 残差修正。文中报告能耗比固定步态最多低 35%【已核实摘要】。
- Go2-W 意义：方向 C 最直接的对比基线（它是显式选择 + 残差；方向 C 是从数据中隐式发现模式）。
- 难点：无代码；平台是改装 Go1，不是 Go2-W。

**⑧ L2R（Go2-W 跌倒恢复）**
- 核心：非对称 PPO + 按 episode 动态奖励塑形 + 课程学习，用轮腿协同完成跌倒恢复。摘要报告恢复成功率最高 99.1%，峰值力矩降低 15.8–26.2%【数字来自 arXiv 摘要/搜索摘要，未逐一核对正文】。
- Go2-W 意义：说明 Go2-W 上的技能类工作可以发表；也说明"跌倒恢复"这个点已被占用，不建议再做。

**⑨ MUJICA（Go2-W 多技能）**
- 核心：一个策略内含多种技能（全向移动、攀爬、恢复），用指示变量区分，配合 DC 电机约束，上层由本体感知的技能选择器切换。
- Go2-W 意义：**方向 B/C 查重时必须正面比较的工作**。它的技能靠奖励工程逐个设计，不做模仿，不用运动数据，不研究风格或自然度。这正是方向 A/B 的切入口。

**⑩ ABot-C0 / ⑪ QuadFM（四足行为基础模型）**
- 核心：大规模四足运动数据加通用跟踪控制器。ABot-C0 据二手摘要有 16,074 段片段，先训专家，再蒸馏成 flow-matching 策略，最后用残差 RL 修正【未核实正文】。QuadFM 含 11,784 段片段、文本标注，Gen2Control 联合训练生成器和控制器【已核实摘要】。
- Go2-W 意义：说明四足运动大模型是热点，但**数据全部是无轮四足**。这从侧面支撑方向 A 的问题：怎样把无轮数据复用到轮足上。
- 难点：数据和代码均未开放（QuadFM 仓库只是占位）。本科生 3–4 个月做不了基础模型，只能借用其中的问题定义。

**⑫ DiffuseLoco（CoRL 2024）**
- 核心：用离线数据训练多技能扩散策略，实时在机载端运行。
- Go2-W 意义：如果想做"扩散/flow 策略直接上 Go2-W"，这是唯一有代码的基线。但需要先有多技能离线数据，而且 Go2-W 机载算力能否支撑实时去噪**未核实**。我不推荐它作为主线。

---

## 2. 提炼的研究方向

### 方向 A（首推）：无轮运动数据向轮足的迁移模仿——"让会滚的狗学像狗"

**要解决的问题**
- 现有四足运动数据都没有轮子，包括狗动捕、Go2 运动库（MimicKit 的 go2 数据集、Kine2Go、QuadFM）。
- 直接拿到 Go2-W 上做逐帧跟踪（DeepMimic）有两个问题：
  - 足端位置被锁死，轮子只能刹住，Go2-W 最省能的"滚动"被浪费；
  - 如果不锁轮，足端会沿轮向滑移，跟踪误差奖励反而惩罚这种合理的滚动。
- AMP 类风格先验也一样：判别器从没见过滚动，会把滚动判为"不像"。
- **核心问题**：怎样定义模仿目标，使轮足既保留参考运动的腿部风格（姿态、相位、节律），又能自主利用轮子？

**为什么有价值**
1. 这是轮足平台独有的形态差异问题，不是把四足方法换个平台再跑一遍。
2. 四足基础模型（ABot-C0、QuadFM）和大规模数据集正在出现，但都没有轮子。谁解决了"无轮数据到轮足"，谁就能复用整个数据生态，后续创新空间大（文本驱动轮足、视频驱动轮足等）。
3. 和之前的方向（执行器对齐、适应）正交，有新意。

**推荐基础论文**
- 主：MimicKit（代码底座，自带 Go2 的 DeepMimic/AMP/ADD）。
- 方法对照：Multi-AMP 轮腿（2022，最近的旧工作）、Walk Like Dogs（2025，无标签狗数据）、SMP（SIGGRAPH 2026，可复用的扩散先验）。
- Go2-W 资产与部署：robot_lab（Go2W）+ unitree_rl_lab 的部署流程。

**本科可做的创新点草案**
- **方法：滚动容许的模仿目标（rolling-admissible imitation）**
  1. 把参考运动拆成两部分：腿部相对构型（关节角、足端相对机身的位置）和全局足端轨迹。
  2. 对腿部相对构型做严格跟踪或风格判别。
  3. 全局足端轨迹只约束法向（离地/着地）和垂直于轮向的分量，沿轮向的位移不罚，改为由速度任务奖励驱动。
  4. 判别器或扩散先验的输入去掉轮速和足端全局速度，只保留腿部特征，再加一个"滚动-迈步相位"特征。
- **对比实验（仿真 + 实机）**

  | 组 | 设置 |
  |---|---|
  | B1 | 纯任务 RL（robot_lab Go2W 速度跟踪，无参考） |
  | B2 | DeepMimic 严格跟踪，轮子锁死 |
  | B3 | DeepMimic 严格跟踪，轮子自由 |
  | B4 | 标准 AMP，判别器输入全部状态 |
  | Ours-a | 滚动容许跟踪 |
  | Ours-b | 腿部特征 AMP/ADD，加滚动相位 |
  | 可选 Ours-c | 把判别器换成冻结的 SMP 扩散先验 |

- **指标**
  - 风格相似度：腿关节轨迹与参考的 DTW 距离，或判别器分数；
  - 速度跟踪误差；
  - 运输代价 CoT（由关节功率估算，Go2-W 低层状态能读到电流/力矩，具体字段**未核实**）；
  - 足端侧滑；
  - 摔倒率。
- **消融**：去掉滚动相位特征；把沿轮向放松改为全放松；参考数据量减半。
- **实机**：平地变速行走/滚动，测 CoT、跟踪误差、录视频做风格对比。实机风险低，因为没有特技动作。
- **可选亮点**：用 CopyQuad 式的单段视频（真实狗视频）做一个"视频到 Go2-W"的演示，增强答辩观感。

**查重初判**
- 搜索 "wheel-legged + motion imitation / AMP / motion prior"，2025–2026 范围内没有找到直接对应的工作（检索记录见本文第 3 节）。
- 最近的是 2022 年 Multi-AMP 轮腿：它的参考来自 RL/TO 控制器的轮腿运动，本身带轮子，不涉及无轮数据迁移。
- IMI 和 UMV 是轮式平台，但参考是为本平台写的。
- 初判：**空白较明确**。但检索只用了通用搜索引擎，投稿前需要在 Google Scholar / Semantic Scholar 上再查 "wheel-legged imitation"、"morphology mismatch retargeting wheel"。

**风险**
- 风格对轮足有什么用？可能被认为是"花架子"。应对：用 CoT 和稳定性说话。AMP 文献（Escontrela 2022）报告过模仿先验能降低 CoT【已核实搜索摘要表述】；在轮足上，"腿用狗的节律、轮子负责省能"能否同时做到，本身就是可量化的问题。
- MimicKit 缺实机部署部分，需要 2–3 周补齐。
- 仿真后端在 sm_120 上的兼容性未核实。

**与之前方向相比**
- 优：新颖度高、轮足特有、有成熟代码底座、实机安全，后续可以接文本/视频驱动。
- 劣：要回答"为什么要像狗"的应用价值质疑，论证链不如"省能/安全"那样天然。

**应对传统控制的质疑**
- MPC/WBC 可以精确跟踪给定轨迹，但需要人写出带轮子的可行参考和接触序列。本方向的贡献恰恰是"参考不含轮子时，自动找出轮腿协同的方式"，这一点传统方法需要人工设计混合接触计划。
- 可以加一组"参考 + 简单 IK 锁轮"的模型基线作对照。

---

### 方向 B：轮足特技的迭代模仿——从不可行关键帧到实机技能

**要解决的问题**
- 轮足特技需要手写参考或逐技能设计奖励（MUJICA 就是逐技能设计奖励）。例如：
  - 滚动助跑后跳上台阶；
  - 后轮着地的两轮"翘头"站立/滑行；
  - 带轮转身的急停。
- 关键帧动画很直观，但对 16 自由度、轮地接触的系统往往不可行：会违反力矩上限，或出现轮子打滑、自碰撞。

**为什么有价值**
- IMI（ICRA 2026）只在 3 自由度级别的自行车机器人上验证过；ZEST 用关键帧让 Spot 学会了后空翻，但不涉及轮子。
- 把"不可行参考的迭代修正"推广到腿轮混合接触平台，是一个清晰的"方法 × 新平台类别"贡献，演示效果也很强。

**推荐基础论文**：IMI（ICRA 2026，主）、ZEST（佐证）、MimicKit DeepMimic-Go2（代码）、MUJICA（Go2-W 对照）。

**本科可做的创新点草案**
- **方法**：IMI 外循环 + 轮地一致性修正。每轮迭代后，用 rollout 更新参考时，把足端轨迹投影到"轮子纯滚动"约束上，再作为新参考；同时对力矩逼近上限的帧做时间伸缩。
- **技能**（选 2 个）：
  - S1：滚动接近，跳上 10–20 cm 台阶（MUJICA 也有高台攀爬，可直接对比）；
  - S2：两轮站立平衡 3–5 s 后恢复四轮。
- **对比**

  | 组 | 设置 |
  |---|---|
  | B1 | 纯奖励工程 RL（MUJICA 风格） |
  | B2 | 一次性 DeepMimic 跟踪不可行参考 |
  | B3 | 原版 IMI（不做轮地投影） |
  | Ours | IMI + 轮地一致性 |

- **指标**：成功率、迭代收敛轮数、峰值力矩/越限比例、参考与最终动作的偏离程度、调参工时（可量化"人工成本"）。
- **实机**：先做 S1 的低台阶版本，S2 加吊绳保护。

**查重初判**
- 没查到"轮足 + 迭代模仿"的工作。
- Go2-W 攀爬已有 MUJICA，但方法路线不同（奖励工程 vs 模仿）。
- NMPC 做轮足跳跃已有 arXiv 2602.21612（小型轮腿，非 RL）。
- 初判：方法与平台的组合有新意，但"特技"本身已有多家在做，新颖性主要体现在流程上。

**风险**
- 实机特技可能损伤电机或摔坏机器，Go2-W 开发版的维修成本需要先问清楚。
- 两轮站立对膝关节力矩要求高，可行性**未核实**，要先在仿真里看力矩余量。
- 3–4 个月内如果实机只能做低难度版本，演示效果会打折。

**与之前方向相比**
- 优：视觉冲击强，论文故事简单（"把关键帧变成实机技能"）。
- 劣：实机风险最高；对"技能有什么实际用途"的质疑需要用"降低技能开发人工成本"来回应。

**应对传统控制的质疑**：用 B1（奖励工程）和 NMPC 文献对比"开发一个新技能需要多少人工"。IMI 类方法的卖点是参考随便画、自动修正。

---

### 方向 C：从无标签运动数据中发现轮/腿/混合模式并切换（偏研究性，备选）

**要解决的问题**
- Go2-W 何时滚、何时迈、何时混合？已有做法分两类：
  - 显式选择：IROS 2025 的能量预测加名义步态，MUJICA 的指示变量加选择器；
  - 纯奖励涌现：ATRos、TARS 论文指出单靠奖励很难稳定涌现滚动。
- 能否像 Walk Like Dogs 那样，从无标签的混合数据中自动发现模式，并按命令和地形平滑切换？混合数据指：狗的腿式数据，加上仿真中滚动策略的 rollout。

**推荐基础论文**：Walk Like Dogs（主思路）、DHAL（RSS 2025，混合自动机、有代码）、能量感知步态选择（IROS 2025，对比基线）、MUJICA（对比基线）。

**创新点草案**
- 用 VAE 或 DHAL 式离散潜变量对混合数据建模，下层用 RL 跟踪。
- 对比：
  - 显式指示变量（MUJICA 式）；
  - 能量预测选择（IROS 2025 式，需自己复现简化版）；
  - 纯奖励涌现（ATRos 式）。
- 指标：不同速度和地形下的 CoT、切换平滑度（切换时刻的加速度/力矩尖峰）、地形通过率、学到的模式与人类直觉的一致性。

**查重与风险**
- 模式切换在 Go2-W 上已有 MUJICA、AWARE（M20）、Frontiers 2026 双足 MoE 等，比较拥挤。
- 能耗这个卖点和之前"能效"类方向有交叉。
- DHAL 基于 Isaac Gym，Blackwell 兼容性存疑。
- **我不建议作为主线**，但可以作为方向 A 的后续第二篇论文：A 做好后，数据和模型能直接延伸到 C。

---

### 未入选但考虑过的方向（及原因）
- **用腿做操作/移动操作（pedipulation、推门、踢球）**：经典工作多为 2024 年及以前（Pedipulate、视觉腿操作），2025 年的 Go2 后腿站立推车（Humanoids 2025）无代码。Go2-W 的足端是轮子，难以稳定点接触按按钮；如果改成"用轮子推/滚物体"，任务定义新颖，但没有基线，3–4 个月风险大。
- **扩散/flow 策略直接上实机**：DiffuseLoco 有代码但较老；ABot-C0 的 flow 蒸馏未开源；Go2-W 机载实时去噪能力未核实。生成模型更适合作"奖励/先验"（SMP 路线，已并入方向 A 的 Ours-c），而不是作部署策略。
- **跌倒恢复**：L2R 已在 Go2-W 上做过，MUJICA 也包含此项，空间小。
- **四足行为基础模型**：数据和算力需求远超本科毕设，只借用其问题定义。

---

## 3. 总体判断与建议

1. **首推方向 A**。问题是轮足独有的（无轮数据到轮足），代码底座现成（MimicKit Go2 + robot_lab Go2W），实机风险低，查重初判空白明显，后续能自然延伸到 B（特技）和 C（模式发现）。
2. **时间线草案（A）**

   | 周次 | 工作 |
   |---|---|
   | 第 1–3 周 | 在 Blackwell 上跑通 MimicKit Go2 的 DeepMimic/AMP；接入 Go2W 资产 |
   | 第 4–6 周 | 实现 B1–B4 基线 |
   | 第 7–9 周 | 实现 Ours-a/b，完成消融 |
   | 第 10–12 周 | 补域随机化和部署流程，实机验证 |
   | 第 13–16 周 | 写论文 |

   可选 Ours-c（SMP 先验）只在进度富余时做。
3. **需要人工确认的事项**
   - MimicKit 的 Isaac Lab 3.0-EA 或 Newton 后端在 sm_120 上能否运行；
   - Go2-W 低层接口能读到哪些功率相关量（用于 CoT）；
   - 投稿前用 Semantic Scholar 复查 "wheel-legged" × "imitation / motion prior / retarget"；
   - L2R 代码是否公开。
4. **诚实声明**
   - 本轮检索以 Web 搜索引擎为主，没有系统翻阅 RSS/CoRL 2025 的接收列表，可能遗漏会议正式版；
   - 标为"venue 未列"的论文可能已被接收，但我没查到；
   - 文中所有数字均来自摘要或项目页，未逐一核对正文。

---

## 附：主要来源链接
- MimicKit: https://github.com/xbpeng/MimicKit ；arXiv 2510.13794
- Walk Like Dogs: https://arxiv.org/abs/2507.00677
- IMI: https://arxiv.org/abs/2603.27944 ；https://imi-umv.github.io
- ZEST: https://arxiv.org/abs/2602.00401
- SMP: https://arxiv.org/abs/2512.03028 ；https://xbpeng.github.io/projects/SMP/index.html
- DHAL: https://roboticsproceedings.org/rss21/p127.html ；https://github.com/UMich-CURLY/DHAL
- 能量感知轮足步态（IROS 2025）: https://arxiv.org/abs/2601.10723
- L2R: https://arxiv.org/abs/2506.05516 ；https://boyuandeng.github.io/L2R-WheelLegCoordination
- MUJICA: https://arxiv.org/abs/2605.13058
- ABot-C0: https://arxiv.org/abs/2607.07370
- QuadFM: https://arxiv.org/abs/2603.24021 ；https://github.com/GaoLii/QuadFM
- DiffuseLoco: https://arxiv.org/abs/2404.19264 ；https://github.com/HybridRobotics/DiffuseLoco
- ATRos: https://arxiv.org/abs/2510.09980
- Go2-W 导航: https://arxiv.org/abs/2606.21387
- robot_lab: https://github.com/fan-ziqi/robot_lab ；mjlab: https://github.com/mujocolab/mjlab ；BeyondMimic 代码: https://github.com/HybridRobotics/whole_body_tracking
- CopyQuad: https://arxiv.org/abs/2610.16737 ；STMR: https://arxiv.org/abs/2404.11557
- Multi-AMP 轮腿: https://arxiv.org/abs/2203.14912 ；Pedipulate: https://arxiv.org/abs/2402.10837 ；Go2 后腿站立: https://arxiv.org/abs/2507.20382
- Diff-CAST: https://arxiv.org/abs/2605.08804 ；MoE-Loco: https://arxiv.org/abs/2503.08564 ；UMV: https://arxiv.org/abs/2602.22118
