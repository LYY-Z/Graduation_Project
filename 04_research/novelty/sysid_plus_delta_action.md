# 查重记录：两步对齐（物理/执行器辨识 + delta-action 残差）用于 Go2-W

检索日期 2026-11-25。写法约定：**【作者事实】**来自摘要或正文抽取，**【评价】**为本文判断。`04_research/novelty/` 此前不存在（无已有记录可参照格式），本文件按 `candidates/` 证据卡的写法自拟。

## 0. 被查重的设想

在 Unitree Go2-W（12 腿位置目标 + 4 轮速度目标）上缩小 sim-to-real 差距，分三步：

1. 用真机数据做执行器/物理参数辨识（PACE，或 CMA-ES 等黑盒辨识）。
2. 用 ASAP 式 delta-action 残差模型只学剩余差距（主要是轮地接触与打滑）。腿、轮分通道，轮通道以轮速等为条件。
3. 在对齐后的仿真里微调策略，比较 原始 / 只辨识 / 只 delta / 两步结合。

## 1. 检索范围与局限

- **ASAP 施引文献**：Semantic Scholar 引用列表 349 条；OpenAlex 引用列表 346 条。S2 列表先按关键词（delta、residual、sim-to-real、actuator、wheel、legged、dynamics、contact、align 等）过滤后读标题；OpenAlex 比 S2 多出的约 50 条也读了标题。**没有对 349 条逐条细读**，只读了关键词命中项与差集；标题不含这些词的施引文献可能漏看。
- **SPI-Active 施引（OpenAlex，42 条）、PACE 施引（OpenAlex，33 条）**：全部读了标题。Dao & Fern 在 OpenAlex 中施引数为 0，无法顺引用链往后查。
- **OpenAlex 标题摘要检索**：用 wheel-legged / wheeled-legged / wheeled quadruped / Go2-W / delta action / action delta / real-to-sim / residual / actuator network / system identification 等组合。带引号的多词与过严的布尔组合多次返回 0 条，这类 0 条**只说明该查询式无命中**。
- **arXiv API 与 WebSearch** 各做若干条，用于补查已知条目和轮足方向。
- **全文阅读方式**：Dao & Fern、QuadVerse、Contact-UAN、UAN、SimDist、ASAP、Actuator Reality Shaping 的细节来自 WebFetch 对 arXiv HTML 的抽取摘要，**不是逐页读 PDF**。ASAP 的 delta 网络结构在附录，抽取被截断；ASAP 与 QuadVerse 页面末尾约 1 万与 3 千字符未读。引用前须对照 PDF。
- **未做到**：Google Scholar（无法访问）；ICRA/IROS/CoRL/RSS 2026 论文集逐条翻查（只通过 OpenAlex 收录项和搜索命中，收录不全）；中文数据库（知网、万方）；GitHub 项目页逐个翻查。
- 因此下文的"未发现"都只表示**在上述范围内未发现**，不等于无人做过。

## 2. 最接近工作逐项对照

记号：(1) 辨识参数；(2) delta/残差学习；(3) 用对齐后的仿真微调策略；四路对比指 原始/只辨识/只残差/两者结合。

### 2.1 Dao & Fern，Simulator Adaptation for Sim-to-Real Learning of Legged Locomotion via Proprioceptive Distribution Matching（最接近）

- 作者：Jeremy Dao, Alan Fern。
- 状态：arXiv 预印本，2604.11090，2026-04-13，页面未写录用信息。https://arxiv.org/abs/2604.11090
- 平台：Go2（IsaacLab，PPO）；另提到 Digit 的失败尝试。无轮。
- **【作者事实】**：把"参数辨识（FricArm：关节摩擦与电枢）、action-delta 模型、残差执行器模型（ResidAct，力矩残差）"作为三种互相**独立**的仿真修改，用同一个"本体感知分布匹配"目标分别优化。action-delta 每关节一个小 MLP，输入过去 3 步关节位置和速度，输出位置目标残差，结构沿用 ASAP。
- 做了哪些：(1) 做（sim-to-sim 为主）；(2) 做；(3) 做（Go2 真机：用 64 条 4 秒真机轨迹拟合 ResidAct，再在修改后的仿真里 PPO 微调，漂移明显下降）。
- **没做**：抽取内容里**没有"先辨识再 delta"的串联**；没有四路结合对比；sim-to-real 只用了残差执行器模型，不是 delta-action；无轮。
- 与设想的差别：它把 sysid 与 delta 当作**并列备选**，设想是**串联并检验是否互补**；平台是纯腿式。**【评价】**这是对"在腿上比较 sysid 与 delta"覆盖最直接的一篇，第 (3) 步中"只辨识/只 delta"两格在腿通道上已有先例。

### 2.2 QuadVerse（最接近的"分阶段对齐"）

- 作者：Yuxiang Chen, Yuanhao Wang, Ziheng Zhang, Meng Zhang, Yu Liu, Yufei Jia, Tiancai Wang, Erjin Zhou, Jin Xie。
- 状态：arXiv 预印本，2606.07118v2，2026-06，页面未写录用信息。https://arxiv.org/abs/2606.07118
- 平台：Go2 真机；Go1、A2 仅仿真到仿真。无轮。
- **【作者事实】**：先用重建场景做**接触（摩擦）标定**（LLM 先验 + 网格搜索后验），再在已标定地形上回放约 10 分钟真机轨迹，训练动作空间残差补偿器（MLP 2×128，历史 20 帧，微调时限幅 ±δ）；冻结残差后放入仿真微调 HIM 运动策略，并训练导航策略。作者明确说先标定接触，是为了"降低地形接触误差与执行器非理想之间的纠缠"。
- 做了哪些：(1) 部分（只标定摩擦，**不辨识执行器参数**，执行器差异全由残差吸收）；(2) 做（动作空间 delta）；(3) 做。有"名义仿真 0.127 rad / 平地回放残差 0.064 rad / 完整 0.043 rad"的开环回放对比，以及真机导航"去掉残差"的消融。**没有**"只标定、不加残差"的执行器跟踪对照。
- 与设想的差别：它是"物理侧标定 → 残差"两步串联在腿式 Go2 上的先例，含对齐后微调策略。差别：标定对象是地面摩擦而非执行器参数；无轮；无四路完整对比；无腿轮分通道。

### 2.3 Fey 等，UAN：Bridging the Sim-to-Real Gap for Athletic Loco-Manipulation

- 作者：Nolan Fey, Gabriel B. Margolis, Martin Peticco, Pulkit Agrawal。
- 状态：**RSS 2025**（OpenAlex 记录 DOI 10.15607/rss.2025.xxi.125；arXiv 2502.10894）。
- 平台：Unitree B2 + Z1 Pro 机械臂。无轮。
- **【作者事实】**：无监督执行器网络，输出力矩残差，用关节编码器读数匹配，不需要力矩传感器；两阶段：先 UAN 标定仿真，再预训练/微调全身策略。对照有 Default、DR、ROA、Actuator Net、CEM（最接近"只辨识"）、UAN。**没有**"辨识 + UAN"的组合条件。
- 差别：残差在力矩空间；CEM 辨识是并列基线而非串联；无轮。

### 2.4 Contact-UAN（Fey 等，MIT）

- 作者：Nolan Fey, Khai Nguyen, Yash Prabhu, Gabriel B. Margolis, Pulkit Agrawal。
- 状态：arXiv 预印本 2610.18991，2026-10-13，未写录用信息。https://arxiv.org/abs/2610.18991
- 平台：Unitree G1 人形。
- **【作者事实】**：保留仿真物理先验、修正执行器动力学的残差世界模型，需要"接触一致的回放"；位置目标残差，另与力矩残差、监督力矩模型比较，下游性能相近，作者倾向位置残差。**明确不做额外的机器人专属辨识**（"No additional robot-specific SysID is performed"），无"辨识 + 残差"消融。
- 差别：人形、无辨识、无轮。其价值是给"位置目标残差 vs 力矩残差"提供证据，可作为我们选 delta-action 形式的依据。

### 2.5 ASAP 本身

- 作者：Tairan He 等（Guanya Shi 组）。**RSS 2025**，OpenAlex 记录 DOI 10.15607/rss.2025.xxi.066；arXiv 2502.01143。
- 平台：Unitree G1 人形；真机 delta 模型只覆盖 4 自由度踝关节；仿真到仿真有 IsaacGym 到 IsaacSim / Genesis。
- **【作者事实】**：delta-action 模型是 **PPO 训练的策略** π^Δ(s, a)，输出叠加在真机记录动作上；基线有 Oracle、Vanilla、SysID、DeltaDynamics。SysID 是**基线而不是前置步骤**，作者说是"与传统 SysID 不同的途径"。无轮、无四足实验。
- 差别：ASAP 把 sysid 与 delta 放在**对立**位置；设想把它们串联。

### 2.6 SPI-Active

- 作者：Nikhil Sobanbabu, Guanqi He, Tairan He, Yuxiang Yang, Guanya Shi。
- 状态：**CoRL 2025**（PMLR v305）；arXiv 2505.14266。仓库 Sim2real 部分仍有 TODO（见 `04_research/reviews/dynamics_literature.md`）。
- 平台：Go2、G1。无轮。
- 做了 (1)(3)，**没有 delta/残差**。施引 42 条中没有发现把它与 delta 残差串联的工作。

### 2.7 PACE

- 作者：Filip Bjelonic, Fabian Tischhauser, Marco Hutter。
- 状态：IJRR 2026 在线发表（DOI 10.1177/02783649261459628；arXiv 2509.06342）。详见 `04_research/candidates/pace.md`。
- 平台：多种腿式机器人，论文无轮实验；仓库 issue 称作者同事在轮足上用过，未公开结果。
- 做了 (1)(3)，无 delta 残差。施引 33 条已读标题，未发现把 PACE 与 delta-action 串联的工作。OmniReset（arXiv 2603.15789）按 PACE 流程在 UR5e/UR7e 上做过辨识（机械臂）。

### 2.8 Sontakke 等，Residual Physics Learning and System Identification for Sim-to-real Transfer of Policies on Buoyancy Assisted Legged Robots（早期先例）

- 作者：Nitish Sontakke, Hosik Chae, Sangjoon Lee, Tianle Huang, Dennis W. Hong, Sehoon Ha。**IROS 2023**（OpenAlex）；arXiv 2303.09597。
- 平台：BALLU（浮力辅助轻型腿式机器人）。
- **【作者事实】**：先用真机数据优化仿真参数以建模执行器非线性（辨识），再用深度 RL 训练**外力策略**匹配真机轨迹，建模残差物理（EnvMimic），然后在改进的仿真里学行走和转向并上机。
- 差别：**"先辨识、后残差、再训策略"的结构在 2023 年已出现**。平台是 BALLU，不是轮足；残差形式是外力而非 delta-action；摘要层面看没有四路定量对比（全文未读）。

### 2.9 RSR（Real2Sim2Real）

- 作者：Suozhong Fan 等。*Mathematics* 2026，14(13):2358。https://doi.org/10.3390/math14132358（MDPI 页面 403，只读到 OpenAlex 摘要）。
- 平台：腱驱动双足。
- **【作者事实】**：第一阶段用真机关节数据在仿真中训练**力矩修正策略**，第二阶段训练显隐式估计的 RL。摘要中没有参数辨识步骤。
- 差别：残差形式相近，平台和结构不同；只作旁证。

### 2.10 SimDist（已知条目，核对）

- 作者：Jacob Levy 等。**RSS 2026**（OpenAlex DOI 10.15607/rss.2026.xxii.017）；arXiv 2603.15759。
- 平台：Go2（12 关节位置目标）与 UR5e；无轮。
- **【作者事实】**：仿真中预训练世界模型；真机适应只更新潜在动力学，作者称之为"监督式系统辨识"；无 sysid 或 delta-action 基线。打滑任务（PTFE 板）在腿上做过，不是轮。
- 与设想：方向不同（世界模型 + 规划），不涉及两步对齐。

### 2.11 SSRL

- 作者：Jacob Levy, Tyler Westenbroek, David Fridovich-Keil。*Learning to Walk from Three Minutes of Real-World Data with Semi-structured Dynamics Models*，arXiv 2410.09163；WebSearch 结果称 CoRL 2024（**未在论文集页面核对**）。
- 平台：Go1。半结构化动力学模型（黑盒外力 + 已知拉格朗日动力学）+ 模型型 RL，从零学步态。不是仿真对齐，与设想关系较远。

### 2.12 RWM-U

- 作者：Chenhao Li, Andreas Krause, Marco Hutter。arXiv 2504.16680；OpenAlex 记录来源为 arXiv，**未发现正式录用信息**。
- 带不确定性的世界模型，离线 MBRL；四足和人形实机。与两步对齐无关，只作背景。

### 2.13 Actuator network（Hwangbo 2019）与 UAN

- Hwangbo 等，*Learning agile and dynamic motor skills for legged robots*，**Science Robotics** 2019（DOI 10.1126/scirobotics.aau5872）。ANYmal；力矩传感器监督的执行器网络。无"辨识 + 残差"串联。UAN 是其无力矩传感器版本，见 2.3。

### 2.14 其他读过摘要、差别明确的相关工作

| 工作 | 状态与出处 | 与设想的关系 |
|---|---|---|
| HALO（重载人形的可微仿真两阶段辨识） | IROS 2026（DOI 10.1109/iros61738.2026.11776388）；arXiv 2603.15084 | 只做辨识，无 delta/残差；ASAP 与 SPI-Active 的施引 |
| HumanoidNDM | arXiv 2610.34126，预印本 | 神经动力学模型 + 反传梯度微调策略，G1；无辨识步骤 |
| World Translation | arXiv 2607.18154，预印本 | 反向动力学提取 + 无配对域翻译，Go2 实机；不是辨识 + delta |
| FADA（Shi 组） | arXiv 2606.28476，预印本 | 冻结规划器只微调逆动力学模型，人形 |
| OSRAM | arXiv 2609.28878，预印本 | 适应的是参考指令而非仿真，双足 |
| Actuator Reality Shaping | arXiv 2607.02205，预印本 | 改造真机执行器去匹配理想仿真；有三轮的轮足机器人（YM070 速度控制轮，非 Go2-W）斜坡零样本演示，**未讨论打滑**；ASAP 式 delta 基线只在机械臂上评估 |
| RACER | arXiv 2610.07409，预印本 | 轮式四足赛车，残差动力学加在**规划器的单轮车运动学模型**上，学 RL 速度跟踪器的闭环误差，LoRRA 低秩适应；不是仿真对齐，不是 delta-action，不训练策略 |
| Matsuzawa 等 Go2-W 长距离导航 | arXiv 2606.21387，预印本 | Go2-W 实机 RL；发现轮式行驶使髋关节集中发热，用周期抬脚缓解；无仿真对齐 |
| Eisman 等 Go2-W 赛车滚转控制 | arXiv 2606.26313，预印本 | MPC + RL，Go2-W；无仿真对齐 |
| IDTD（2610.10905）、GAUGE（2609.32154） | arXiv 预印本 | 只做辨识或标定，无 delta |
| Real-to-Sim Adaptation 轮式倒立摆（arXiv 2403.10948） | arXiv 预印本 | 轮式倒立摆（简化模型）的 PSO 参数辨识，无学习残差 |

## 3. 逐项覆盖判断

| 子部分 | 状态 | 依据 |
|---|---|---|
| (1) 真机数据辨识执行器/物理参数 | 已被充分做过 | PACE（IJRR 2026）、SPI-Active（CoRL 2025）、HALO、Dao & Fern 的 FricArm |
| (2) ASAP 式 delta-action 残差，用在四足 | 已被做过 | Dao & Fern（Go2，ActionDelta）、QuadVerse（Go2，动作空间残差）；人形有 ASAP、Contact-UAN（位置残差） |
| 辨识与残差的串联（先物理后残差） | 已有先例，但不是"执行器辨识 + delta-action" | Sontakke 2023（BALLU）、QuadVerse（先标定摩擦，再残差） |
| (3) 对齐后的仿真微调策略 | 已被做过 | Dao & Fern、QuadVerse、UAN、Contact-UAN |
| 原始/只辨识/只 delta 的比较 | 腿上部分已有 | Dao & Fern 并列比较三者（sim-to-sim 为主）；UAN 有 CEM 对 UAN；QuadVerse 有名义/只残差/两者的回放对比 |
| 四路（含两步结合）在同一平台、同一预算下的受控比较 | **在检索范围内未发现** | Dao & Fern 的三种修改相互独立未串联；QuadVerse 缺"只标定"格；UAN、Contact-UAN 无"辨识 + 残差"条件 |
| **轮足平台**上的仿真对齐（辨识或 delta） | **未发现（检索范围：第 1 节）** | 最接近的是 RACER（规划器层残差）和 Actuator Reality Shaping（改真机执行器），层次与目的都不同 |
| **轮通道**专用残差（以轮速、负载等为条件）建模轮地接触/打滑 | **未发现（检索范围：第 1 节）** | Dao & Fern 与 QuadVerse 的残差都只覆盖腿关节 |
| 腿/轮分通道的 delta 模型 | 未发现（检索范围：第 1 节） | 腿侧逐关节小网络已是 ASAP/Dao & Fern 的做法 |

## 4. 结论

**设想整体是否已被覆盖：部分覆盖。**

- 没有发现与设想整体一致的工作。但**三步中的每一步在腿式平台上都已有成熟或近似的先例**：Dao & Fern（2026，预印本）在 Go2 上比较了"参数辨识 / action-delta / 残差执行器"并做了对齐后微调；QuadVerse（2026，预印本）在 Go2 上做了"物理侧标定 → 动作空间残差 → 微调策略"的串联。对一篇以"辨识 + delta 两步结合"为主要卖点的毕设，这部分**不能作为创新点**，只能作为方法组件和对照。
- **仍有差异的点**只剩两处，且都在检索范围内未发现先例：
  1. **轮足平台**（Go2-W）上的辨识 + 残差对齐，尤其是**轮通道**残差：轮速目标、以轮速/指令/负载为条件，建模轮地接触与打滑。
  2. 在同一平台、同一数据预算下对"原始 / 只辨识 / 只 delta / 两步结合"做**四路受控比较**，并回答两步是否互补、残差是否在吸收本该由辨识解决的参数误差。
- **【评价】风险**：第 1 点容易被看作"把已有方法搬到轮足"（本仓库 `candidates/pace.md` 已有"仅扩展到轮足不算创新"的判断）。要成立，需要轮地接触上有数据支撑的发现，例如：辨识解决不了的差距集中在轮通道，或 delta 与辨识存在可测量的相互替代。Go2-W 缺少打滑真值（无动捕），需用 LIO/IMU 速度估计等代理量。

## 5. 被部分覆盖时的两个调整（有差异、本科 3–4 个月可做）

**调整 A（推荐）：把贡献从"两步组合"改为"轮足上辨识与残差的分工与相互替代"的受控研究。**
- 在 Go2-W 上做 2×2：{不辨识, PACE/CMA-ES 辨识} × {无 delta, 腿 delta + 轮 delta}，再加"先辨识再 delta"与"先 delta 再辨识"（或交替迭代）的顺序对比。
- 先在 sim-to-sim 里造已知真值差距（轮地摩擦、轮电机增益、延迟），按 Dao & Fern 的做法检验各步吸收了哪类差距、delta 是否造成参数漂移或重复吸收；再用真机数据验证。
- 指标：开环回放误差（腿位置、轮速）、下游策略速度跟踪误差、真机漂移。这样"轮通道的分工"是有结论的发现，而不只是"加了轮子"。
- 工作量：PACE 轮通道需改速度损失（`candidates/pace.md` §4.2 已记录）；delta 网络小；数据分悬吊（电机侧）与落地（轮地接触）两批采集。

**调整 B：聚焦轮地接触残差，用代理真值做打滑建模。**
- 只保留辨识作为前置（固定腿与轮电机侧），创新放在轮通道 delta：输入含轮速目标、实测轮速、机体速度估计、负载代理量；输出轮速目标修正。
- 以激光雷达里程计与轮里程计的速度差作打滑代理量，比较 delta 残差与"只辨识摩擦系数"的效果。
- 风险：代理真值噪声大；Matsuzawa 等已报告轮行驶时髋关节发热，采集时需控制时长。

两个调整都**不要把"首个在 Go2-W 上做 X"当作主要贡献**，这类说法只对本次检索范围成立。

## 6. 交付前复核清单

1. 对照 PDF 逐页重读 Dao & Fern 与 QuadVerse，确认前者没有串联实验、后者没有"只标定"对照。
2. 在 Google Scholar 与 RSS/ICRA/IROS/CoRL 2026 论文集里再查一遍 wheel-legged / wheeled quadruped + residual / delta / actuator / system identification。
3. 核对 SSRL 的 CoRL 2024 发表信息（本次只来自 WebSearch 结果）。
4. 确认 RACER 所用机型是否为 Go2-W（摘要只写 wheeled quadruped）。
5. 开题前对 Dao & Fern 与 QuadVerse 的后续版本和施引复查（二者均为 2026 年新预印本，施引很少）。
