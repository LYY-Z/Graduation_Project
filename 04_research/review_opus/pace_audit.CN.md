# PACE 证据审核（Opus 复核）

日期：2026-11-25。审核对象：[决策备忘](../decision_memo.CN.md)与 [PACE 证据卡](../candidates/pace.md)中关于 PACE 的说法。本文只做核对和评价，没有修改其他文件。

## 0. 审核范围与方法

| 来源 | 版本与读取方式 |
|---|---|
| 论文 | arXiv 2509.06342 **v2 PDF**（30 页，2026-07-31），用 `pdftotext -layout` 逐页抽取并逐页阅读；图表密集页（p16 图 9 与表 4）另外以页面图像核对。下文页码（p）指 PDF 页码，节号指论文节号 |
| 代码 | `leggedrobotics/pace-sim2real` 浅克隆，HEAD = `7ad0f45`（v0.2.0，2026-10-13），**今天仍是 main 最新提交**。行号均相对仓库根目录 |
| issue | GitHub API 读取 #1–#36 的正文与全部评论原文（2026-11-25） |
| 发表状态 | Crossref API、OpenAlex API、doi.org 跳转；SAGE 页面返回 403 |
| 兼容性 | Isaac Lab `v2.3.0` / `v2.3.2` 源码（raw.githubusercontent） |

本地副本：PDF 与文本在 `C:\Users\RJ903\AppData\Local\Temp\claude\3539a96fb9884e79\0bbc2a4c-0f01-4670-a802-983c2a0caf69\scratchpad\dl\pace_audit\pdf\`，issue 原文汇总在同目录上一级的 `issues_all.txt`。没有安装或运行任何代码。

标记：**正确** / **部分正确**（主体对，但缺少限定或节号、行号有误）/ **有误** / **无法核实**。

---

## 1. 结论摘要

### 1.1 有误或需要改写的说法

| # | 出处 | 原说法 | 问题 |
|---|---|---|---|
| E1 | 备忘 §4.5-1 | "PACE 在轮足上的**首个公开**应用" | PACE 论文 p12 §3.1 已列出 PACE 部署在 **LEVA**（ICRA 2025，带腿式悬架、可转向**轮子**的平台）；issue #36 作者也说同事已在轮足上用过。"首个"不成立，至多能说"首个公开**腿位置 + 轮速度**辨识流程与数据" |
| E2 | 备忘 §4.1 | 维护者在 #22 "**承认**激励可能没有覆盖运动区域" | 那是维护者的"first guess"（2026-06-09）。他在 2026-11-10 的追评中改口：覆盖率分析"does not yet establish what causes the limited improvement"，并列出执行器以外的失配来源（观测顺序、坐标系、状态估计延迟、机载滤波）。只引前一句是选择性引用 |
| E3 | 备忘 §3 | "论文的 ANYmal **结果**……不公开" | ANYmal 真机悬空数据**已公开**（论文 p21 Data Accessibility：doi 10.3929/ethz-c-000783505；issue #1）。不公开的是运动训练环境、奖励实现和策略权重（#30、#2）。另外**漏了一条关键事实**：论文的运动实验是用 **LeggedGym / Isaac Gym** 做的，不是 Isaac Lab（#30 作者原话） |
| E4 | 备忘 §4.1 | 把"着地"说成 PACE "缺失"的环节 | 作者是**有意**只用悬空数据（p11 "No data collected under ground contact is used"），并在讨论里明确主张 "In-air data suffices for contact tasks"（p20 §5）。这是作者的论点，不是作者承认的局限。备忘应写成"我们要检验作者的这一主张在轮子上是否成立" |
| E5 | 证据卡 §2.4-6 | 全机 LF-HFE 惯量约 4 倍"**未解释**" | 论文 p20 §5 给了解释（CAD 连杆惯量低估、补偿带来的视在惯量、转子惯量），并用附录 C 的单腿实验验证（p29–30，图 24）。另外这是 **TYTAN** 的数据 |
| E6 | 证据卡 §3、§6.3 | issue #19 "谐振峰未拟合，维护者回答是'模型结构不够'" | 维护者说的是"模型结构可能不够，**或**硬件 PD 与仿真不一致"。提问者随后确认原因是驱动器底层行为与仿真 PD 不一致，对齐后"identification results are now as expected"。**不是**模型类的局限 |
| E7 | 证据卡 §4.1、§4.2 | `data_collection.py:181-186`、`:137-141`、`:272-276`；`anymal_pace_env_cfg.py:184-198`、`:193` | 行号不存在（两个文件分别只有 176 行和 82 行）。正确位置：注入参数 `data_collection.py:60-65`，chirp 参数 `:17-19, :93-102`，保存 `:150-155`；PD 增益与限幅 `anymal_pace_env_cfg.py:13-27`，friction 重命名注释在 `:22` |
| E8 | 证据卡 §3、§6.6 | "issue #22、#25 显示用户在 dt、decimation、延迟位置上出错" | dt/decimation 的问题出自 **#16**；#25 是维护者自己的修复 PR，不是用户出错；#22 是维护者列出的检查项，不是用户已出错 |
| E9 | 证据卡 §2.3、§4.1 | actor 48 维、critic 353 维出自"§3.3，Table 8"；动作定义出自"§3.3，Eq.8" | 应为 **§2.3.1**（p9）与 **§2.3.2 Eq.8**（p9）。Table 8 只有 PPO 超参数（p30） |
| E10 | 证据卡 §2.1 | 域随机化"覆盖范围随**控制频率**快速膨胀" | 原文是随 **step frequency（步频）** 膨胀（p20 §5）。"随机化与在线适应可能进一步提升鲁棒性"出自 §3.3.3（p15），不在 Discussion |

另有若干措辞不严（卡 §2.4 的"30 次实验，约 5 小时"中 5 h 是拟合总耗时；"延迟拟合约 7.5 ms"是拟合出的延迟值，不是成本），见第 2 节。

### 1.2 第 6 条结论（审稿人意见，详见第 7 节）

- **方向可做，但现在的写法有一个核心漏洞**：轮子在地面上"走不准"的主要来源是**打滑和有效滚动半径**，表现为"轮速 ≠ 地速"。**只用本体感觉数据（关节、轮速、估计力矩、IMU）在原理上看不到这个差值**，所以"不用任何外部速度参考"的着地残差很可能拟合了力矩分布，却修不了用卷尺测出来的速度误差。
- **最大科学风险**：归因不可辨识。残差会吸收状态估计、观测处理、策略依赖的数据分布等非接触误差（这正是维护者在 #22 最后指出的方向）；作者本人又主张悬空数据足够。结果很可能是"差异不显著"或"说不清改进来自哪里"。
- **最大工程风险**：第一步在 Go2-W 上就做不干净。需要刚性悬挂（ANYmal 因绳索悬挂只能激励到 2 Hz，#4）、lowcmd 权限、500 Hz 记录，还要对轮速环滤波建模（#36）。issue 里 Unitree 用户的记录不好看：#11 的 Go2 用户结果"worse than a regular PD controller"，#18 的 A1 用户 5 Hz 以上振动、偏置撞边界，#22 的 Go2 用户运动指标"not consistently better"。
- **建议**：保留"不用动捕"，但**不要**坚持"零外部参考"。轮通道使用低成本速度参考（已有的激光雷达 LIO、卷尺加秒表、或轮速与 LIO 的比值），残差改为少数有物理意义的参数（滚动阻力系数、有效轮半径或纵向滑移、承重相关阻尼），并在第 1–4 周先做一个"差距是否集中在轮通道"的预实验，再决定是否立项。

---

## 2. 逐条核对：方法（审核要点 1）

| 说法（出处） | 判定 | 依据 |
|---|---|---|
| 悬空、固定基座、腿在空中，位置目标 chirp 激励（备忘 §3；卡 §2.3） | **正确** | p7 §2.1 "Fixed base"、"No contacts (legs free in air)"；"The chirp is applied at the joint position target level and tracked by a PD controller" |
| chirp 0.1–10 Hz（卡 §2.3） | **部分正确** | p12 §3.1.1："f0 = 0.1 Hz and a maximum frequency of 10 Hz"。但实际受悬挂结构限制：**ANYmal 2 Hz、TYTAN 全机 8 Hz**（p12 §3.1.1）；p7 §2.1 写 "2 Hz on ANYMAL; 10 Hz on TYTAN/MINIMAL"，两节数字不一致（卡已指出，正确）。#4 作者说明这是悬挂装置（Dyneema 绳加吊车）的限制，不是驱动器的限制 |
| 约 20 s 数据（备忘 §3；卡 §2.3、§2.5） | **部分正确** | "20 s" 是作者的标题式说法：p18 §4.1.2 "our approach relied on 20 s of in-air data"，p20、p21 结论同。但方法节写 "chirp signals of **20–60 s** per sequence"（p7 §2.1），实验节写 "Typical sequence duration is **20–40 s**"（p12 §3.1.1）。#17 作者说每台机器人采 **2–3 条**序列（一条拟合，其余验证）。合理口径是："一条 20–40 s 序列用于拟合，另加 1–2 条验证序列" |
| 4n+1 参数：每关节电枢、粘性阻尼、库仑摩擦、偏置，加一个全局延迟（备忘、卡 §2.3） | **正确（论文口径）** | p7 §2.2 Eq.(2) `p = [Ia, d, τf, q̃b, Td] ∈ R^{4n+1}`；p8 "typically 49 parameters"。**代码口径已变**：v0.2.0 的 ANYmal 示例默认 `separate_dynamic_friction=True`，变成 **5n+1 = 61** 个参数（`anymal_pace_env_cfg.py:35-36`，`CHANGELOG.rst:20-21`，`pace_sim2real_env_cfg.py:126-137`） |
| CMA-ES，4096 并行环境，σ = 0.5，参数归一化到 [-1, 1]（卡 §2.3、§4.1） | **正确** | p8 §2.2 "N = 4096"、CMA-ES；p12 §3.1.2 "σ = 0.5"、"[-1, 1]"；代码 `cma_es.py:42-46`、`fit.py:15`（默认 4096 环境）。论文自称"agnostic to the specific choice of optimizer"（p3 §1.1），没有和其他优化器比较，卡的判断正确 |
| 损失只用关节位置（卡 §4.1） | **正确** | p8 Eq.(3) 时间平均的关节位置平方误差；`cma_es.py:86` `torch.sum(torch.square(sim_dof_pos - real_dof_pos - bias), dim=1)`，所有关节加成一个标量。速度损失只是文档示例（`docs/tutorials/advanced.md:80-92`） |
| PD 增益、饱和不辨识（卡 §2.3） | **正确** | p8 "we do not include saturation limits as free parameters"；Eq.(7) 共同缩放不唯一，所以 PD 增益视为已知；`ki` 同理不辨识 |
| 延迟实现：论文描述"延迟指令"，论文结果用的是"延迟力矩"；v0.2.0 改为默认延迟指令（卡 §5.1；备忘未提） | **正确** | `CHANGELOG.rst:28-31` 原文："The actuator delay was applied to the computed torque, while the paper describes a delay of the commands … The results in the paper were produced with the previous implementation, which remains available via `delay_mode="effort"`."；实现在 `pace_actuator.py:81-93`，配置在 `pace_actuator_cfg.py:23-28`（本仓库 `utils/pace_actuator_cfg.py`）；`docs/tutorials/basics.md:148-153`。PR #25 中维护者的测试：25 ms 延迟下 `"effort"` 超调到约 2 倍幅值，`"command"` 只是时间平移。论文 p7 写的是 "a global command delay Td" |
| 延迟是全机共享的整数步（卡 §4.1） | **正确** | `cma_es.py:65`（单一 `delay_idx`）、`:146` `.to(torch.int)`；`docs/tutorials/best_practice.md:58-70`（离散化导致优化面不连续）。#33 显示 ANYmal 发布值约 3.24 步，截断成 3 步 × 2.5 ms = 7.5 ms，与论文一致 |
| 所需传感器：只要关节编码器，不需要机身状态（备忘 §3） | **辨识部分正确；整条链部分正确** | 辨识：p4 "encoder-only data"，p8 "directly observable from encoder-only in-air trajectories"；数据格式只有 `time / dof_pos / des_dof_pos`（`fit.py:61-64`），基座固定（`pace_sim2real_env_cfg.py:170`）。**但** PACE 论文的**策略**观测含基座线速度 `vB`、角速度和重力方向，且 "from a state estimator"（p9 §2.3.1）。也就是说：辨识不需要机身状态，部署的运动策略需要状态估计（不需要动捕）。对 Go2-W 底层模式"没有官方机身速度"这一点，这是策略侧的问题，不是 PACE 侧的问题，但备忘应分开写 |
| 无动力学随机化（卡 §2.3） | **部分正确** | p9 §2.3："we do not use dynamics randomization"，但**仍随机化任务、推力和地面摩擦**（"We randomize the task (pushes, ground friction) and terrains"）。地面摩擦随机化与"着地残差"直接相关，备忘与卡都没提 |
| 单个延迟可能不够用于轮速环（卡 §4.2） | **评价，合理** | 代码里所有执行器组共享一个延迟（`cma_es.py:138-147` 对每个 drive type 写入同一个 `delay_idx`） |

---

## 3. 逐条核对：实验与局限（审核要点 2）

| 说法（出处） | 判定 | 依据 |
|---|---|---|
| 没有消融（卡 §2.4-1；卡开头） | **正确** | 全文没有"去掉某个参数"、种群规模、激励带宽或优化器的消融。仅有的对照是 无模型 / 执行器网络 / PACE 三组策略（p15 §3.3.2），以及跨 PD 增益、跨轨迹的验证（p13 §3.2.2，图 15、20） |
| 没有定量跟踪误差表（卡 §2.4-2） | **部分正确** | 确实没有误差表。但有：图 7 的 CMA-ES 归一化得分曲线（p15，单位 rad²）；图 9e 与图 21 的稳态速度**小提琴图**（p16、p28）；正文给出 "mean 0.85 m/s"（p19 §4.2.2）。悬空对照（图 1c、图 8）只有相图与时间曲线，没有 RMSE。重复次数与置信区间都没有报告 |
| 执行器网络基线口径不等（卡 §2.4-3） | **正确，并且要补一句** | p15："The actuator-network baseline is the **ANYbotics LSTM** actuator model deployed on our platform, rather than a model retrained on the suspended, contact-free chirp data … **not as a controlled equal-data comparison**"。"20 s 对 4 min"比的是 Hwangbo 2019 原文的数据量，而实际部署的厂商 LSTM "was likely trained on a larger dataset"（p18 §4.1.2）。PACE 在 ANYmal 上的结论是与执行器网络 "competitive"（p20 §5），**不是优于** |
| 32% CoT 的基线是 ANYmal C 旧结果（卡 §2.4-4） | **正确，混杂因素比卡写的更多** | 表 4 标题 "ANYmal C and AoPS are from Bjelonic et al. (2023)"（p16）；表 5：ANYmal C 1.86 → ANYmal D 1.27（p18），(1.86−1.27)/1.86 ≈ 31.7%。混杂因素：不同代机器人；**环境温度 26 °C 对 10 °C**、平均速度 0.740 对 0.850 m/s（表 4，p16）；奖励不同（本文有物理能耗项）；作者把降幅归因于"无需动力学随机化 → 更直的膝步态"（p20 §5 "Energy shaping"）。作者还写了 "this outcome is not unique to PACE (e.g., Miller et al. (2025))"（p15 §3.3.3）。所以 32% **不能**当作"辨识本身"的证据，卡 §2.3 的判断正确 |
| ANYmal 地面：前进、侧移 1 m/s、偏航 2 rad/s；URDF-only 约 3 s 发散；执行器网络与 PACE 稳态约 0.85 m/s（卡 §2.4） | **正确** | p15 §3.3.2，p19 §4.2.2 |
| 400 m 跑道：ANYmal D 4.12 km、TYTAN 6.10 km，CoT 1.27 / 0.97（卡 §2.4） | **正确** | 表 4、表 5（p16、p18）；结论 p21 |
| 单驱动 30 次实验，电枢与解析值相符（转子 2%、接口 6%、附加质量 15%），固件补偿等效 8.1×10⁻³ kg·m²（卡 §2.4） | **正确；"约 5 小时"需改** | p13 §3.2.1、p18 §4.1.1。"totaling 5 h across all runs" 指拟合总耗时，不是实验时长 |
| 每平台约 10–24 h，单张 RTX 3080（卡 §2.4、§2.5） | **正确** | p12 §3.1 "single NVIDIA GeForce RTX 3080"；p18 §4 "converges within 10–24 h" |
| PPO 30000 次迭代（卡 §2.4） | **正确** | 表 8（p30）；#30 作者补充 "trained for 24h for about 30k iterations on rough terrain … LeggedGym" |
| 部署次数未报告，无多种子、无置信区间（卡 §2.4-5） | **正确** | 全文无此类统计。TYTAN 地面对比只有一次 90 s 记录（p15 §3.3.1，"SignalLogger buffer limit"） |
| 一次杠杆断裂的试验被排除（卡 §2.4-6） | **正确** | p18 §4.1.1 |

**作者承认的局限（原文位置）**

| 局限 | 判定 | 位置 |
|---|---|---|
| 悬空激励带宽有限 | **正确** | p21 §6 "finite excitation bandwidth on suspended setups"；p7 §2.1 |
| 温度与老化使参数漂移 | **正确** | p21 §6 "temperature/aging dependencies that shift effective parameters"；§2.4 假设 "Mild temperature dependence during data collection"（p11） |
| §2.4 假设被违反时失败 | **正确** | p21 §6 "Our approach fails if any of the assumptions from Section 2.4 are violated"；假设列表在 p10–11 |
| 能量模型不含铁损、逆变器、温度 | **正确** | p10 "Limitations of the energy model" |
| 负载相关的阻尼 | **证据卡与备忘都漏了，对选题有利** | p8 §2.2："Drive-level simplifications (e.g., **load-independent damping**) are common but imperfect; actual damping and torque–current maps are often **state dependent**." 这是作者自己承认"负载/状态相关"会带来误差，可作为着地残差的动机 |
| 着地 / 负载未覆盖 | **作者不认为是局限** | p11 明确只用悬空数据；p7 与附录 B（p27–29）论证站立时基座惯量比腿和驱动惯量大 1–2 个数量级，所以要隔离出驱动动力学；p20 §5 "In-air data suffices for contact tasks"。见 E4 |
| 未来工作 | **卡漏了关键一条** | p20 §5 "Future extensions"：① CMA-ES 加局部梯度；② **"Contact-parameter refinement when foot-force sensing or plates are available"**；③ 轻量在线适应（{Ia, d} 的全局缩放）。p21 还有电气约束、柔顺性建模。②与本选题直接重叠，属于**被同组抢先的风险**，备忘 §8 应引用这一条 |

---

## 4. issue 核对（审核要点 3）

### 4.1 #22：chirp 是否覆盖运动区域

链接：<https://github.com/leggedrobotics/pace-sim2real/issues/22>

- 提问者 Chole726（2026-06-03，**Unitree Go2**）原话："the joint response in simulation aligns reasonably well with the real collected data … PACE also significantly reduces joint position RMSE … However … the improvements in joint tracking error, velocity tracking, and torque smoothness are **not consistently better than the no-PACE baseline**. Occasionally, improvements are only seen in a subset of metrics, such as vertical velocity or pitch stability."
- 维护者 fbjelonic（2026-06-09）："my **first guess** would be that the identification trajectory may not be informative enough for the parts of the actuator behavior that matter during locomotion. A chirp trajectory can fit joint tracking well in one regime, but locomotion may excite different velocity, torque, saturation, delay, **contact-coupled**, or controller-frequency regimes."
- 提问者补充（2026-06-16）：400 Hz、0.1–10 Hz、幅值系数 0.3、20 s，Kp = 25、Kd = 1.0（辨识、训练、部署一致），仿真是**自己在 Isaac Gym 里重写的 DCMotor**。覆盖率分析："single-variable ranges … very well (mostly 100%). However, the joint (q, dq) occupancy is significantly lower."
- 维护者最新评论（2026-11-10）："The coverage analysis is also useful, although it **does not yet establish what causes the limited improvement** during locomotion (since the model usually generalizes well across the state space of the robot) … There may also be sources of mismatch **beyond the actuator dynamics** addressed by PACE—for example, observation ordering, coordinate frames, scaling, state-estimation delays, or filters running on the robot that are absent from simulation."

判定：备忘 §4.1 引用 **部分正确**（见 E2）。

### 4.2 "Go2 用户拟合好但运动提升小"的出处

- **主要出处就是 #22**（Chole726，Go2），原话见 4.1 第一条。更准确的转述是"运动指标**没有一致优于**无 PACE 基线，只在部分指标上有改进"，而不是"提升很小"。判定：**基本正确，措辞需收紧**。
- 另一条相关报告 **#11**（qin-yuhao，Go2，Kp = 15、Kd = 1.0，最高 10 Hz，2026-03-08）："The slight vibration of the robot dog at high frequencies results in inaccuracies in the real data … there are obvious problems with bias identification. Moreover, the model trained this way performs poorly, **worse than a regular PD controller**." 维护者认为轨迹叠加看起来"reasonably close"，并要求先排查参数加载和频率是否失配；该 issue 无后续即被关闭。<https://github.com/leggedrobotics/pace-sim2real/issues/11>
- **#18**（A1 用户）：悬挂装置在 5 Hz 以上振动明显，偏置撞到 ±0.1 rad 边界；维护者回答 PD 太硬、基座固定不够刚。<https://github.com/leggedrobotics/pace-sim2real/issues/18>
- **#24**：作者（2026-06-16）"We have **not tested PACE on Unitree platforms** yet"；第三方 giulioturrisi 指向 iit-DLSLab/sim2real-robot-identification，其中有 Go2/A2/Aliengo 的激励数据与辨识值（见第 6 节）。

### 4.3 #36：轮足，作者回复原文

链接：<https://github.com/leggedrobotics/pace-sim2real/issues/36>（提问 2026-10-26；作者 fbjelonic 回复 2026-11-10，issue 已关闭）。作者回复全文：

> I have not personally applied PACE to wheel-legged robots, but colleagues of mine have used it on such platforms. I would expect the identification approach to be applicable, with some adaptations for the wheels:
> - For the position-controlled hip and knee joints, you can follow the existing procedure.
> - For the wheels, I would use the same command interface as during locomotion, i.e., velocity commands, and minimize the difference between measured and simulated wheel velocities rather than positions. The simulation should also reproduce the velocity controller, including any filtering, delays, or integral action.
>
> I would recommend collecting the data with the wheels in the air. This isolates the actuator dynamics and avoids introducing unmeasured ground-contact forces into the identification. However, it will not identify rolling resistance, slip, or other wheel–ground interaction effects; those require separate modeling or validation.
>
> For excitation, I would start with velocity chirps in both directions, covering different speeds and including acceleration and deceleration. Removing ground contact does not inherently prevent identification, but a tightly tracking velocity controller can make some physical parameters difficult to distinguish from velocity measurements alone. Transient excitation is therefore important, and logging motor current or torque, if available, can help assess this.
>
> Finally, keep the base as stationary as possible. If it is suspended rather than rigidly mounted, coordinate the wheel excitation so that the reaction torques approximately cancel. Check the physical rotation directions and joint-axis conventions, since identical command signs do not necessarily achieve this.
>
> I would then validate the fitted model on separate in-air trajectories before evaluating it during ground locomotion.

判定：备忘 §3 "作者确认同事已在轮足上用过，并给出轮子用速度指令辨识的建议" **正确**。需要补两点：① 作者**公开**说了悬空辨识 "will not identify rolling resistance, slip … those require separate modeling or validation"。这既支持动机，也说明这个缺口对所有读者都是显而易见的下一步（抢先风险）。② 作者提醒"紧跟踪的速度环会让部分参数难以区分"，建议同时记录电流或力矩。

### 4.4 #30：训练环境未公开

链接：<https://github.com/leggedrobotics/pace-sim2real/issues/30>（作者回复 2026-07-31）。要点原文：
- "The complete locomotion environment used for the paper is not part of the current PACE repository. We are planning to open-source an updated version as part of separate follow-up work"
- "The trained locomotion policy checkpoints used for the paper are **not planned for release**."
- "the locomotion results reported in the paper were obtained using **LeggedGym / Isaac Gym, not Isaac Lab**."
- 课程（curriculum）：500 次迭代半衰期（衰减系数 0.9986092495）。

判定：STATUS 与卡中"训练环境未公开（#30）" **正确**。#2（2025-12-10）同样说明 RL 代码 "intentionally not part of this release"。

### 4.5 其他与卡相关的 issue

| issue | 卡中说法 | 判定 | 原文要点 |
|---|---|---|---|
| #19 | 谐振峰未拟合，维护者答"模型结构不够" | **有误**（E6） | 提问者："It turned out that the hardware drive's low-level behavior caused a mismatch with the PD gains used in simulation. After aligning the control logic, the identification results are now as expected." |
| #20 | 维护者提醒谨慎解释为物理粘性摩擦 | **正确** | "I would be cautious about interpreting this as physical viscous friction." |
| #21、#33 | 用作者共享的 ANYmal 数据，结果与 Table 6 不一致 | **正确** | #33 维护者："the differences you list are larger than publication rounding would explain … I need to check the original fitting and publication records"；#21 维护者怀疑关节顺序问题。**#21 的环境是 Isaac Sim 5.1 + Isaac Lab v2.3.2**（见第 6 节） |
| #34 | 不支持 Isaac Lab 3.0 | **正确** | "We haven't scheduled official Isaac Lab 3.0 support yet." |
| #17 | 卡未引用 | — | 每台机器人 2–3 条序列；跨 PD 增益参数漂移通常意味着增益不是 SI 单位或底层有缩放 |

---

## 5. 发表状态（审核要点 4）

| 项 | 结果 | 来源 |
|---|---|---|
| DOI | 10.1177/02783649261459628，doi.org 跳转到 `journals.sagepub.com/doi/10.1177/02783649261459628` | doi.org 响应头 |
| Crossref | type = journal-article；container = The International Journal of Robotics Research；标题与三位作者一致；published-online 与 issued 均为 **2026-07-31**；deposited 2026-08-03；**volume、issue、page、published-print、accepted 都为空**；article-number = 02783649261459628 | `api.crossref.org/works/10.1177/02783649261459628`（2026-11-25） |
| OpenAlex | publication_date 2026-07-31；biblio 的 volume/issue/页码全为 None；cited_by_count = 33 | `api.openalex.org` |
| SAGE 页面 | 两种 URL 均返回 **403**，未读到 | 本次请求 |
| arXiv | v2 PDF 首页写 "Published in The International Journal of Robotics Research (IJRR). DOI: 10.1177/02783649261459628"；Journal reference: "The International Journal of Robotics Research, 2026" | PDF p1；arXiv abs 页 |
| 仓库 | README 引用块 journal = IJRR，year = 2026，无卷期（`README.md:238-247`） | 代码 |

判定：备忘 §3 "IJRR 2026" 与卡 §1 **正确**。准确口径是"**IJRR 在线优先发表（OnlineFirst，2026-07-31），截至 2026-11-25 尚未分配卷期页码**"。引用时写 `IJRR, 2026, doi:10.1177/02783649261459628`，不要编卷期。

---

## 6. 代码对 Go2-W 的适配点与兼容性（审核要点 5）

### 6.1 轮子改用速度损失，需要改的地方

| 位置 | 现状 | 需要改什么 |
|---|---|---|
| `source/pace_sim2real/pace_sim2real/tasks/manager_based/pace/pace_sim2real_env_cfg.py:62` | 所有关节 `JointPositionActionCfg(joint_names=[".*"], use_default_offset=False)` | 拆成两个动作项：腿关节用位置动作，轮关节用 `JointVelocityActionCfg`（Isaac Lab 自带） |
| 新建 `go2w_pace_env_cfg.py`（参照 `anymal_pace_env_cfg.py:13-82`） | 只有 ANYmal 一种 `PaceDCMotorCfg` | 两个执行器组：腿（Kp/Kd 与部署一致）；轮 `stiffness=0`、`damping=轮 kd`。Isaac Lab `DCMotor` 的 PD 律 `τ = kp(q*−q) + kd(q̇*−q̇)` 在 kp = 0 时退化为速度环，与 Unitree 电机指令形式一致。`joint_order` 列出 16 个关节；`bounds_params` 改为 16 关节布局 |
| `scripts/pace/fit.py:61-64, 95-97` | 数据只有 `time/dof_pos/des_dof_pos`；`opt.tell` 只传 `joint_pos`；动作只填位置目标 | 数据增加 `dof_vel/des_dof_vel`（轮）；轮的动作列填速度目标；`tell` 同时传 `joint_vel` |
| `source/pace_sim2real/pace_sim2real/optim/cma_es.py:86` | 所有关节的位置误差（减偏置）加成一个标量 | 腿用位置误差，轮用速度误差（作者 #36 建议；`docs/tutorials/advanced.md:88-92` 有示例）。两种量纲（rad² 与 (rad/s)²）需要按通道方差归一，否则轮通道会主导或被忽略 |
| `cma_es.py:60-71`（参数布局与数量检查）、`pace_sim2real_env_cfg.py:126-137` | 硬编码 `4n+1`（或 `5n+1`）布局 | 轮的偏置无意义：把边界设为 [0, 0]，或改布局去掉。若轮速环延迟与腿不同（见下一行），要加第二个延迟索引，同时改这两处的数量检查 |
| `cma_es.py:138-147` | 每个执行器组写入**同一个**延迟 | 可选：按执行器组分别设延迟 |
| `scripts/pace/data_collection.py:64, 106-117` | 偏置 `[0.05]*12`、轨迹方向/偏置/幅值都是 12 维 ANYmal 硬编码 | 重写为 16 关节：轮用双向速度 chirp 加加减速瞬态（#36），左右轮反作用力矩相互抵消 |
| 仿真步长与指令频率 | `sim.dt = 0.0025`（400 Hz），decimation = 1（`anymal_pace_env_cfg.py:81-82`） | Go2 lowcmd 一般为 500 Hz：要么仿真用 `dt = 0.002`，要么重采样；辨识与训练的 `dt` 必须一致（#16） |
| 轮速滤波 | 代码没有 | 作者 #36 要求 "reproduce the velocity controller, including any filtering, delays, or integral action"；论文 p10 §2.4 也提醒驱动侧速度滤波会影响 D 项。对 kp = 0 的轮子，D 项就是整个控制律，所以这一项必须建模 |
| 真机采集 | 仓库**没有**真机采集代码（README "place your own real-world data in `data/`"） | 自己写，或复用 iit-DLSLab 的 ROS 2 采集脚本（见 6.3） |

### 6.2 与 Isaac Lab 2.3.x / Isaac Sim 5.1 的兼容性线索

| 线索 | 结果 |
|---|---|
| `setup.py:39-43` | classifiers 只列 Python 3.10/3.11 与 "Isaac Sim :: 4.5.0 / 5.0.0"。这只是元数据，不是版本约束。依赖只有 `psutil`、`cmaes`（`:18-21`）；`setup.py:8` 还 `import toml`，安装前环境里必须已有 toml |
| `README.md:51-64` | "developed and tested against Isaac Sim 5.0 / Isaac Lab (latest)"；Isaac Sim < 5.0 会缺粘性摩擦与动态摩擦的写入 |
| 用到的 API | `write_joint_armature_to_sim`、`write_joint_friction_coefficient_to_sim`、`write_joint_dynamic_friction_coefficient_to_sim`、`write_joint_viscous_friction_coefficient_to_sim` 以及对应的 `default_joint_*_coeff`，在 Isaac Lab **v2.3.0 和 v2.3.2** 的 `assets/articulation/articulation.py` 与 `articulation_data.py` 中都存在（v2.3.2：`articulation.py:840, 871, 947, 973`）；`DelayBuffer`（`utils/buffers`）、`DCMotorCfg.saturation_effort`、`friction / dynamic_friction / viscous_friction` 字段（`actuator_base_cfg.py:138, 156, 163`）也都存在。卡 §5.2 "未核实落在 2.3.0 还是 2.3.1"现已核实：**2.3.0 起即有** |
| 实际运行记录 | **#21 用户：Isaac Sim 5.1 + Isaac Lab v2.3.2 + 当时最新的仓库，`fit.py` 能跑**（结果差是数据关节顺序问题，与版本无关） |
| #34 | 官方暂不支持 Isaac Lab 3.0；第三方 iit-DLSLab 已适配 3.0 |
| v0.2.0 新增调用 | `write_joint_dynamic_friction_coefficient_to_sim` 在 2.3.x 中存在，v0.2.0 在 2.3.x 上**大概率**能运行，但没有直接运行记录（#21 用的是 v0.1.2 时期的代码）。**风险：低** |

### 6.3 可复用资源（卡和备忘都没有）

iit-DLSLab/sim2real-robot-identification（#24、#34 中第三方给出）：含 Go2 的真机激励数据（`datasets/go2/excitation_1..4.pt`、`trajectory_1.pt`）、Go2 的 Isaac Lab 辨识参数（`robot_model/go2/isaaclab_identified_parameters.py`）、`sysid_isaaclab/tasks/go2_pace_env_cfg.py`，以及基于 ROS 2（含 humble）的真机采集脚本（配合 unitree-ros2-dls）。它基于 Isaac Lab 3.0，要移植回 2.3。腿部电机若与 Go2 同型，可作为腿部参数的合理性参照（是否同型尚未核实）；**没有轮子**相关内容。

---

## 7. 审稿人意见：以 PACE 为基础，补一个不用动捕的着地本体感觉残差（轮通道）（审核要点 6）

### 7.1 总体评价

问题是真实的，作者自己也承认（p8 "load-independent damping … imperfect"；#36 "will not identify rolling resistance, slip"）。路线也合理：先辨识，再补残差。但现在的方案把"不用动捕"推到了"不用任何外部速度参考"，这会让核心主张不可检验。

### 7.2 最大的科学风险：轮地差距在本体感觉中不可观测，残差的归因无法辨识

1. **可观测性**。"走不准"（速度跟踪偏、转弯偏）在轮足上主要来自纵向滑移和有效滚动半径，也就是"轮速 × 半径 ≠ 地速"。本体感觉里的轮速、关节量、估计力矩和 IMU 都不直接测地速；IMU 积分会漂移，而策略本身的速度估计又依赖同样的假设。所以"让仿真与真机的本体感觉**分布**一致"可以对上滚动阻力带来的力矩或电流偏差，但**对不上滑移**。可能出现分布距离下降、而卷尺测出的速度误差不变的结果。
2. **归因**。分布匹配的残差会吸收所有未建模差异：状态估计延迟、观测缩放或顺序、机载滤波、地面摩擦随机化范围、策略变化导致的数据分布漂移。维护者在 #22 的最新回复恰好指向这些"执行器以外"的来源。数据依赖策略，而策略又会在对齐后的仿真里重新微调，这是一个闭环，需要有明确的停止准则和留出评估。
3. **与作者主张正面冲突**。作者主张 "In-air data suffices for contact tasks"（p20）。要发表"需要着地残差"，必须先用数据说明在 Go2-W 上：PACE 之后的剩余差距显著，且**集中在轮通道**。如果预实验显示差距主要在腿、或主要来自状态估计，主线就不成立。
4. **抢先风险**。作者在 p20 把 "Contact-parameter refinement when foot-force sensing or plates are available" 列为未来工作，并且同事已在轮足上使用 PACE（#36）。

### 7.3 最大的工程风险：第一步在 Go2-W 上做不干净，后面全部失去基准

- 需要刚性固定基座。ANYmal 用绳加吊车只能激励到 2 Hz（#4）；Unitree 用户的悬挂振动已导致偏置撞边界（#18）、结果差（#11）。轮子同时反转还会给基座施加反作用力矩（#36）。
- 需要 lowcmd 权限、稳定的 500 Hz 记录，并且辨识、训练、部署三处的 Kp/Kd、频率和延迟位置完全一致（#16、#22）。Go2-W 腿部部署刚度（20）与 robot_lab 仿真刚度（25）不一致（备忘 §2），这正是 #22 中维护者列出的首要排查项。
- 轮速环的固件滤波和积分项未知，而 kp = 0 时 D 项就是全部控制律（#36、p10 §2.4）。
- PACE 在 Unitree 平台上的"运动收益"本身在 issue 中**没有正面证据**（#11、#22；作者在 #24 说没在 Unitree 上测过）。"只辨识 vs 默认"这一组很可能就是不显著的，后面"两步结合"的增量就没有清晰的基准。

### 7.4 建议的修改（按优先级）

1. **第 1–4 周加入立项门槛**：在真机上用固定指令，比较悬空与着地时的稳态轮速跟踪、轮电流，以及"轮速 × 半径"与外部速度（LIO 或卷尺加秒表）的差。只有当差距显著且集中在轮通道时，才把着地残差作为主线；否则退回"PACE 在轮足上的受控复现与差距分解"。
2. **保留"不用动捕"，放弃"零外部参考"**：轮通道使用已有的激光雷达 LIO 作为速度参考（备忘 §5 已列为可选，建议改为必需），使滑移可观测。
3. **残差改为低维、有物理意义的参数**：滚动阻力系数、有效轮半径或纵向滑移刚度、承重相关的轮阻尼，用 PACE 同一套 CMA-ES 拟合，便于和 PACE 的"可解释参数"叙事一致，也便于回答"残差吸收了什么"。神经网络残差作为对照，不作为主方法。
4. **基线中加入"窄域随机化地面摩擦或滚动阻力"**：这是最简单的替代方案。论文本身也保留了地面摩擦随机化（p9）。如果它与残差效果相当，残差就不成立。
5. **修正备忘中的事实**：E1–E4；"20 s"改为"一条 20–40 s 拟合序列 + 1–2 条验证序列"；IJRR 写成在线优先、无卷期；运动结果来自 LeggedGym / Isaac Gym。

---

## 8. 证据卡其他条目的快速核对（未在上文列出的）

| 说法 | 判定 | 依据 |
|---|---|---|
| 作者、单位、标题 | 正确 | p1 |
| v1 2025-09-08，v2 2026-07-31 | 正确 | arXiv abs 页 |
| 代码 Apache-2.0，v0.2.0（2026-10-13），README "active development" | 正确 | `CHANGELOG.rst:4`；`README.md:128` |
| `docs/concepts/actuators.md`、`docs/real-world.md` 为 "Coming soon." | 正确 | 两个文件 |
| 域随机化"假设刚体动力学准确" | 正确 | p3 §1.3 |
| 执行器网络需要力矩传感器或大量搜索 | 正确 | p4 |
| 策略驱动标定：轨迹漂移、需要稳定策略、安全性中等 | 正确 | 表 1（p4），§1.3.1 |
| BO 在中等维度下变差 | 正确 | p3 §1.1 |
| 奖励常十余项手工项 | 正确 | p6 §1.4 |
| 十台附加机器人只有名单 | 正确 | p11 图 4、p12 §3.1。**补充**：名单中包括 LEVA（轮式、腿式悬架），见 E1 |
| `pace_actuator.py:19-93, :73, :83-87, :89-93`；`cma_es.py:126-135, :146, :42-46, :174-177, :100, :116, :179-181, :94, :213` | 正确 | 行号与内容均一致 |
| `rsl_rl_ppo_cfg.py:16` `cartpole_direct`，`[32,32]` | 正确 | `:16, :21-22` |
| `pace_sim2real_env_cfg.py:62` 动作为绝对关节位置 | 正确 | `:62` |
| 电枢等直接写入 PhysX 关节，执行器类不含 PMSM 能量模型 | 正确 | `cma_es.py:126-135`；`rewards.py` 只有模板函数 |
| 仓库 `data/` 只有仿真数据 | 部分正确 | git 中**没有** `data/` 目录；数据由 `data_collection.py` 在仿真中生成后写入 |
| `best_practice.md` §8 内存估算 | 正确 | `docs/tutorials/best_practice.md:121-131` |
| OmniReset / UWLab 相关说法 | 未复核 | 不在本次范围 |
