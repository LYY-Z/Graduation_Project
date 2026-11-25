# 第三轮：已有候选统一评分（2026-11-24）

范围与口径：只用仓库已有材料（`STATUS.CN.md`、`review.CN.md` §0.4–0.8、`candidates/*.md`、`screening/*.md`、`02_learning/locoformer/`），没有上网，没有重读论文原文，没有运行任何东西。所有判断是【评价】，周数是材料里的粗估，未实测。

用户标准：论文价值与创新点最重要，近两年优先，难复现的高价值论文也要评估。条件：Go2-W 实机（带激光雷达，robot_lab + rl_sar 链路）；服务器 Blackwell sm_120（torch≥2.7 / Isaac Sim 5.x）；工期 3–4 个月。

## 1. 评分口径

| 项 | 含义 | 刻度 |
|---|---|---|
| V 论文价值 | 发表级别、方法实质、实验证据。发表级别标核实程度：**已核**（材料写明读到论文集/PMLR/Crossref 页）、**自述**（README/项目页/arXiv 评论栏）、**未核实** | 5 最高 |
| I 创新空间 | 最好的一个 Go2-W 延伸点 + 查重结论。"未找到"只对材料里记录的检索范围成立 | 5 最大 |
| R 复现难度 | 代码、栈兼容、算力、真机数据 | **5 最难** |
| D 部署难度 | 是否需外接 GPU 笔记本/重规划、动捕或外部定位、lowcmd、无现成部署代码 | **5 最难** |
| 3–4 月 | 是 / 勉强 / 否（含创新点验证，不只是复现） | — |

## 2. 总表（按 V+I 降序）

| 候选 | 发表（核实程度） | V | I | V+I | R | D | 3–4 月 |
|---|---|---|---|---|---|---|---|
| SimDist | RSS 2026（已核） | 4 | 4 | 8 | 5 | 5 | 勉强（偏否） |
| MoE-CTS | RSS 2026（已核，Oral/Poster 未查） | 4 | 3 | 7 | 4 | 2 | 勉强 |
| 具身尺度律 | CoRL 2025（已核） | 4 | 3 | 7 | 5 | 4 | 否 |
| D3 | CoRL 2025（arXiv 评论栏与 PMLR 页；Oral 为项目页自述） | 4 | 3 | 7 | 2 | 3 | 勉强（查重未做） |
| Multi-Loco | CoRL 2025（已核，PMLR） | 3 | 3 | 6 | 3 | 3 | 勉强 |
| PACE | IJRR 2026（已核 Crossref，无卷期页码） | 4 | 2 | 6 | 3 | 3 | 是（创新点未成立） |
| LocoFormer | CoRL 2025（已核，PMLR liu25a） | 4 | 2 | 6 | 5 | 3 | 否 |
| DIAL-MPC | ICRA 2025 Best Paper Finalist（未核实，README 自述） | 4 | 2 | 6 | 3 | 5 | 否（无外部定位）/ 勉强（有动捕） |
| SPI-Active | CoRL 2025 Oral（PMLR 已核，Oral 为 README 自述） | 4 | 2 | 6 | 4 | 3 | 勉强 |
| LocoWM | 预印本（已核无录用信息） | 2 | 3 | 5 | 2 | 2 | 是 |
| CaT | IROS 2024（自述） | 2 | 3 | 5 | 2 | 2 | 是 |
| GRAM | RA-L 2026（未核实） | 3 | 2 | 5 | 4 | 2 | 勉强 |
| FLORES | RA-L 2026（未核实，来自子代理） | 3 | 2 | 5 | 4 | 3 | 勉强（偏否） |
| RWM-U | 预印本 + ICLR 2026 workshop 海报（已核） | 2 | 2 | 4 | 3 | 3 | 勉强 |

按"价值+创新"前 5：SimDist（8）、MoE-CTS / 具身尺度律 / D3（并列 7）、Multi-Loco（6，与 PACE、LocoFormer、DIAL-MPC、SPI-Active 并列，取 I 较高者）。注意 V+I 只是粗排，R、D 和可完成性要一并看：具身尺度律、LocoFormer 价值高但对本工期基本不可达。

## 3. 逐篇说明

### SimDist（V4 I4 R5 D5，勉强偏否）
- V：RSS 2026 已核（`candidates/simdist.md` §1，roboticsproceedings p017）。思路清楚（仿真预训练，真机只更新动力学），有 Go2 与 UR5e 实机；短板是 5 次/速度、无种子、缺"直接部署专家/DR 策略"基线，摘要与正文适应时间不一致（15–30 对 32–36 分钟，同卡 §6.1）。
- I：世界模型加轮速通道，做轮地打滑的快速适应。查重：最近 WAVE-Go（仅读摘要）、Wei 等 2610.26550、DreamTIP、ReDRAW 均未直接覆盖（同卡 §5.2）；风险是被看作"SimDist + 轮子"，须配 (a)(b)(c) 之一的方法贡献，同组后续抢先也不能排除。
- R5：Isaac Sim 4.5 / torch 2.5.1 / Isaac Lab 固定旧提交，JAX 0.6.0 在 sm_120 上能否运行未核（最大技术风险），底座改造 6–8 周，总计 11–15 周；仓库约 6 个月无提交。**真机数据未发布，只有权重**。
- D5：实机 MPPI 450 采样×8 迭代×Transformer，50 Hz，作者用 RTX 4090 级笔记本，需外接；定位用 `point_lio_unilidar`（针对 Unitree L1）或动捕，Go2-W 雷达型号与能否开放 `lowcmd` 都未核（同卡 §4.2）。

### MoE-CTS（V4 I3 R4 D2，勉强）
- V：RSS 2026 p156 已核（证据卡读到论文集页；`review.CN.md` §0.5 写"子代理报告，主模型未核到"，见 §4 矛盾）。Go2 实机 + RoboGauge 评估套件；但证据卡评价核心主张（MoE 增益、RoboGauge 预测力）证据偏弱，实质增量主要是评估工具和工程完整度（`candidates/moe_cts.md` §2.5、§7）。
- I：最好的延伸点是"RoboGauge-W"：轮足 sim-to-sim 预测器 + 多策略实机排序相关验证，查重最干净（未找到轮足上的 sim-to-real 可预测性套件，同卡 §6.3 方向 A）；"MoE 搬到 Go2-W"区别薄，不宜作创新点。风险：真机需 ≥6–10 个质量不同的策略，负结果可能。
- R4：栈与服务器同代（Isaac Lab 2.3.2、torch 2.7 cu128），有 Go2 权重；但论文数字来自 IsaacGym 版，只能复现 Lab 版 0.69 左右；训练 176k 迭代约 7 天/次（粗估，待测），3 种子 + 改造 + 消融在单卡上难放进 3–4 个月；Go2-W 改造 5–8 周（`candidates/moe_cts.md` §5.4、`screening/value_rerank.md`）。
- D2：纯本体、只需 IMU 与关节反馈；`unitree_cpp_deploy` 只面向 Go2 的 12 电机，Go2-W 链路和 `lowcmd` 未核。

### 具身尺度律 ESL（V4 I3 R5 D4，否）
- V：CoRL 2025 已核（PMLR ai25a），规模最大（1012 形态），S2 施引 30 条；但无函数拟合、无种子/误差棒、测试集同源、实机无量化、不含轮式（`candidates/embodiment_scaling.md` §2.4、§6）。
- I：方向 B"腿式到轮足的跨驱动类型迁移与需要多少轮式形态"未找到覆盖（同卡 §4）；方向 A"零样本 Go2-W"已被 LocoFormer 覆盖，不能单独当创新点。需与 A 合并，工作量 13–18 周 + 4–6 周。
- R5：原训练约 5 天×160 卡、数据 4–5 TB；旧版 Isaac Lab + torch 2.2.2 必须移植，且依赖 Articulation 私有字段；只能用作者专家权重做小规模趋势验证（同卡 §3.3–3.6）。
- D4：仓库无 Go2 部署代码，URMA 观测格式要自己导出；Go2-W 轮子不在原分布内，零样本大概率不成立（`screening/value_supplement.md` #1）。

### D3 Divide, Discover, Deploy（V4 I3 R2 D3，勉强）
- V：CoRL 2025，arXiv 评论栏与 PMLR 页已列；Oral 来自项目页自述；ETH 真机 ANYmal-D，作者报告不安全接触下降 85%（`screening/value_supplement.md` #3）。弱点：下游任务价值要自己论证。
- I：轮腿因子化技能发现，风格项加执行器温升/电流惩罚；**材料里没有对它做系统查重**（`value_supplement.md` §3 自己写明），I 评分只是基于方向合理性，是最不稳的一项。
- R2：官方代码 Isaac Lab 2.2 + rsl_rl 2.2.0，带 Docker，与 robot_lab 栈同系；需升到配套 Sim 5.1 的 Isaac Lab 并回归测试；4096 环境约 24 GB 显存，服务器够。
- D3：无 Go2-W 部署；ANYmal-D 与 Go2-W 质量、足端形态差异大，风格/对称先验要重设；技能库在实机如何调用要自己设计。

### Multi-Loco（V3 I3 R3 D3，勉强）
- V：CoRL 2025 已核（PMLR yang25a）；设定有价值（跨形态含轮式双足），但表 2 多项落在基线标准差内，教师即基线，实机无定量数字，价值在框架不在结果（`candidates/multi_loco.md` §3、§8）。
- I：方向 A"腿式扩散先验迁移到 Go2-W 轮通道"：未找到直接覆盖（Multi-Loco 有轮式双足，DMLoco 有四足，均无轮式四足）；"轮腿统一/切换"已被 LocoFormer、MUJICA 等覆盖，不能当创新点。前提：先用最小实验证明扩散先验比简单微调有增益（同卡 §6、§7）。
- R3：仓库很可能官方（作者账号与内容对应，但论文未链接）；Isaac Gym 需只借 `rl_alg` + EDM 流水线，环境改用 robot_lab；**有四个专家权重**，EDM 权重在外链未核；约 6–8 周。
- D3：策略纯本体，但扩散策略 50 Hz 机载推理要单独验证；部署栈依赖 LimX SDK，对 Go2-W 无用，要自搭。

### PACE（V4 I2 R3 D3，是）
- V：IJRR 2026，Crossref 已核（无卷期页码，SAGE 页 403 未读）（`candidates/pace.md` §1）。价值主要是工程化辨识流水线，无消融、无强基线（`screening/value_rerank.md`）。
- I：最可能成立的是"受限接口下的模型失配诊断"，但无数据支撑；H1（机械臂）被 OmniReset 与线性辨识挤压，H2（温度漂移）缺数据，H3 收益可能被抹平；"搬到轮足"不算创新，作者同事已用（issue #36，主模型读原页确认，`review.CN.md` §0.7）。
- R3：辨识链完整、算力小、栈同代（Isaac Sim 5.0）；但运动训练环境、奖励、权重不在仓库（issue #30），论文结果对应旧的延迟实现，核心结果无法对齐，只能对齐辨识链。
- D3：需悬吊架或吊车、`lowcmd` 权限（未核）、急停；不需要外接 GPU 或外部定位。适合作组件（执行器辨识前端），不适合单独作主线。

### LocoFormer（V4 I2 R5 D3，否）
- V：CoRL 2025，PMLR liu25a pp.532–546 已核（`02_learning/locoformer/06_research_positioning_and_evidence.md`、`candidates/embodiment_scaling.md` §5）；Go2-W 实机零样本，含后腿双足模式。
- I：它已覆盖"一个策略零样本控制 Go2-W"。材料里只有分析型后续设计（匹配预算的长/短上下文对照、跨 Trial 缓存、故障恢复时间量化），是我们的设想，**未经查重**（`01_paper_and_full_pipeline.md` 末段自己说明"不是原文已完成的消融"）。
- R5：**无官方代码和权重**；统一关节空间槽位表、奖励权重、超参、随机化范围均未披露；附录 C 约十万训练身体；本地只有 lucidrains 第三方实现（Microduck 示例，含论文之后的扩展）。
- D3：若训练成功，Transformer-XL 的 KV cache 实时推理对机载算力的需求未核；接口层（12 位置 + 4 轮速）本身与 rl_sar 对得上。

### DIAL-MPC（V4 I2 R3 D5，否 / 有动捕则勉强）
- V：ICRA 2025 Best Paper Finalist，仅 README 自述；`learning_and_control.md` 写"正式发表"，`world_models.md` 写"未核对官方录用目录"，标**未核实**。约 1000 星，Go2 实机跳跃；但不是学习方法，不贴"学习驱动"主线。
- I：学习先验/价值函数接入采样 MPC，ProxPI、TD-CD-MPPI、SGPS、Residual MPC 已占住主要组合（`screening/learning_and_control.md` §3.1）；轮足接触模型要自建，属工程而非创新。
- R3：无训练；JAX/MJX、CUDA≥12.3 对新 GPU 友好；Go2-W 无 MJCF 和轮地接触模型，要自建；issue 有 20 Hz 不稳定报告。
- D5：README 明写需要外部定位提供机体位置与速度；在线 GPU 采样需外接算力。Go2-W 的雷达 LIO 能否替代动捕未核；有动捕则降到 D4。

### SPI-Active（V4 I2 R4 D3，勉强）
- V：CoRL 2025 Oral，PMLR 已核（`screening/go2w_rerank.md`），Go2 实机；方法属采样式主动辨识，与 PACE 同层。
- I：主动激励辨识加轮速度环，作为 PACE 方向的"策略驱动标定"对照比独立主线更合适；与 PACE 重叠，创新点不成立（`go2w_rerank.md`、`rl_adaptation.md`）。
- R4：IsaacGym Preview 4 + Python 3.8，sm_120 上大概率整体移植（猜想）；**无许可证**；README TODO "Release Sim2real" 未勾；只针对 Go2 质量/质心/惯量与电机模型，无轮。
- D3：同 PACE：悬吊激励、`lowcmd`；sim2real 代码未发布，要自写。

### LocoWM（V2 I3 R2 D2，是）
- V：预印本，无录用信息（已核）；方法偏薄（三个 MLP + 两阶段），无多种子、无视野消融、实机无次数，论文与代码有 9 处不一致（`candidates/locowm.md` §1、§2.5、§5.2、§7.1）。不满足"近两年已发表"的偏好。
- I：方向 C 受控检验"预测式是否优于反应式"（视野扫描、真值上界、多种子）再配 G3/G4 改进，未找到对同类做受控消融的工作；纯分析型贡献需配改进才有竞争力；增益可能落在种子方差内（头号不确定项）。方向 A（打滑）验证缺真值。
- R2：环境与服务器完全一致（Isaac Sim 5.1、torch 2.7 cu128、Python 3.11），训练、评价、三种基线齐全，Apache-2.0；无权重，单次训练估计 36–87 小时（待实测）。
- D2：原生 Go2-W、部署输入不含机体线速度，无外接 GPU/定位；但无部署代码，需自写导出、低通缩放、残差限幅（约 3–4 周）。

### CaT（V2 I3 R2 D2，是）
- V：IROS 2024（项目页自述；`review.CN.md` §0.7 称 DOI 来自二手来源，未打开 IEEE 页面）；方法小而干净，被表述为"早期工作"，约束 RL 先例多。不满足"近两年"。
- I：Go2-W 热/轮速约束作终止概率；未找到"CaT + 电机温度/轮足"（`review.CN.md` §0.7）。最近 Ségas（2611.22231，Go2，预印本，无代码）已占 Go2 热奖励，Matsuzawa（2606.21387，Go2-W）已有手工抬腿方案；必须与"阈值降速""热奖励"两条朴素基线对比，否则被看作平台迁移（`candidates/thermal_aware.md`、`candidates/multi_loco.md` §7）。
- R2：MIT，Isaac Lab（`go2w_rerank.md` 称文档指向 2.1.0，`learning_and_control.md` 称版本未核，见 §4），仅 Solo12 任务，无权重；方法小，robot_lab 已有 Go2-W 任务，4–6 周。
- D2：纯本体；轮电机温度可读性、整数度读数与滞后未核；长时间升温实机试验有硬件风险，瓶颈是实机时间而非算力。

### GRAM（V3 I2 R4 D2，勉强）
- V：RA-L 2026，来自既有审计，**未核实**（仓库内无出版社页核对记录）；方法对口（历史自适应 + 鲁棒），有 Go2 环境和作者 Go2 实机（部署代码未发布）。
- I：历史编码 + 自适应策略的组合已拥挤（`review.CN.md` §4）；突变时刻调度、轮通道、与 CAPABLE/ESCP 对比均需自己加新颖性。
- R4：官方提交要求 Isaac Lab 1.0.0、Isaac Sim 4.1、torch 2.2.2 cu118，已核；无权重；sm_120 未验证，先要升级 Isaac Lab 到 2.3；README 默认配置与论文曲线不对应（`review.CN.md` §8、`go2w_rerank.md`）。
- D2：纯本体；Go2 部署代码未发布，需自写。

### FLORES（V3 I2 R4 D3，勉强偏否）
- V：RA-L vol.11 no.6（`screening/wheel_legged.md` 子代理核对；`value_rerank.md` 标未核实，见 §4）；轮足；自研 FLORES 机器人，不是 Go2-W。
- I：方法是 HIMLoco + 定制奖励，创新空间材料未写、未查重；最有价值的用法是借其"训练、MuJoCo 交叉验证、ros2_control 部署"链路给 Go2-W 做 sim2sim 门槛。
- R4：Isaac Gym + legged_gym 需整体移植到 sm_120 可用的栈，约 8–10 周（评价，粗估）；有权重 `May22_0943.pt`、ROS2 部署、URDF。
- D3：ROS2 Humble + libtorch 2.5.0 部署链可借鉴，但控制器针对自研机器人，Go2-W 要重配。

### RWM-U（V2 I2 R3 D3，勉强）
- V：预印本，ICLR 2026 workshop 海报（已核，`candidates/rwm_u.md` §1），按标准不属"正式发表"。
- I：H1（机械臂）、H2（OOD 回退）、H3（仿真预训练 + 真实微调）均被覆盖；H4-a（离线选保守度 λ）唯一未覆盖，但依赖"离线指标能预测真机表现"，第三方审计证据指向相反（同卡 §7）。
- R3：纯离线训练路径只需 PyTorch，不依赖 Isaac Lab（代码核对）；但**无"用离线数据集训练世界模型"的发布脚本**，官方只发布 ANYmal 平地一个任务，G1、Franka、真实数据与部署均未发布，需自写；算力需求小（每配置约 10–20 GPU 小时）。
- D3：需先有可用策略来采真实数据；每平台约 1 小时真实数据；无外接 GPU 需求；Go2-W 基座线速度来源要解决。

## 4. 材料互相矛盾处

1. **Multi-Loco 权重**：`value_supplement.md` 写"无权重"，证据卡 `multi_loco.md` §5.2 更正为"有四个专家权重（biped/biped_wheel/humanoid/quadruped，约 7–11 MB）；EDM 扩散权重只在外链，可访问性未核"。本表以证据卡为准。
2. **SimDist 数据**：`value_rerank.md` 写"权重、sim/real 数据集都在"；`simdist.md` §4 与 `review.CN.md` §0.8 更正为"只有权重，真机数据未发布"（README 的 TODO 里 UR5e 操作代码也未发布，issue #2 催更无回应）。本表以证据卡为准。
3. **SimDist 发表**：`value_rerank.md` 标"自述"，`simdist.md` §1 与 `review.CN.md` §0.7 称论文集页已读到（RSS 2026 p017）。本表标已核。
4. **MoE-CTS 发表**：证据卡 §1 称读到论文集页 p156；`review.CN.md` §0.5 写"子代理报告，主模型未核到"，`go2w_rerank.md` 来自 arXiv 评论栏；§0.7 又写"论文集核到"。本表以证据卡为准标已核，Oral/Poster 未查。
5. **Multi-Loco / LocoFormer 发表**：`embodiment_scaling.md` §5 把 Multi-Loco 写成"预印本"，LocoFormer 在 `multi_loco.md` §7 写"预印本，venue 未核实"；而 `multi_loco.md` §1（PMLR yang25a）与 `embodiment_scaling.md` §5、`locoformer/06_…` 均已核到 CoRL 2025（LocoFormer：PMLR liu25a pp.532–546）。本表均标 CoRL 2025（已核）。
6. **DIAL-MPC 发表**：`learning_and_control.md` 写"正式发表"，`world_models.md` 写"未核对官方录用目录"，`review.CN.md` §0.7 标"README 与二手 DOI"。本表标未核实。
7. **FLORES 发表**：`wheel_legged.md` 写"正式发表"（子代理核对），`value_rerank.md` 标未核实。本表标未核实。
8. **CaT 栈版本**：`go2w_rerank.md` 称文档指向 Isaac Lab 2.1.0（已核），`learning_and_control.md` 称是否 Isaac Lab 及版本未核。本表按"2.1.0、需对齐 Sim 5.1"处理。
9. **PACE 轮足先例**：子代理曾判断"作者同事已在轮足上用过"有误；`review.CN.md` §0.7 记主模型读 issue #36 原页确认属实，本表按属实处理。
10. **ESL 与 Go2**：`value_supplement.md` 称"迁到 Go2-W 只需新增机器人资产与轮关节动作类型"；证据卡 `embodiment_scaling.md` §3.3、§3.6 说明还要移植 Isaac Lab、无 Go2 部署代码、轮子不在分布内。本表以证据卡为准。另：形态数 817/808、README Gendog 0–331 与"约 1000"的数字不一致，证据卡已记。
11. **D3 复现难度**：`value_supplement.md` 称"最接近服务器环境、复现成本最低"，同时写 Isaac Lab 2.2/Sim 4.5 需小版本升级；本表给 R2，不给 1。

## 5. 评分的局限

- 精读深度不一：MoE-CTS、PACE、LocoWM、SimDist、Multi-Loco、ESL、RWM-U 有证据卡；LocoFormer 有学习文档但无查重卡；CaT、DIAL-MPC、GRAM、FLORES、SPI-Active、D3 只有粗筛级材料，它们的 V、I 更不稳（尤其 D3 的 I）。
- 所有"未找到直接覆盖"依赖材料里记录的检索范围，另有两路新检索进行中，可能改变 I。
- 所有 sm_120 兼容性（JAX、旧版 Isaac Lab、torch）均为读码推断，未在服务器上实测。
- Go2-W 是否开放 `lowcmd`、雷达型号、电机温度可读性、机载算力在 STATUS §4 仍是未决项，直接影响各项 D 评分。
