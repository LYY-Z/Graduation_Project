# 会议论文（四足/轮足）局限与未来工作抽取

日期 2026-11-25。来源：venue_sweep_2025_2026.md §2.1 会议主表（385 篇）。筛选：四足/轮足/平台写 legged 且实验在四足上，RSS/CoRL/ICRA/IROS/NeurIPS/ICLR/ICML；排除纯人形、双足、六足及非足式实验。初选 179 篇，抽取时发现 12 篇实为人形/双足/六足/无人机/纯仿真，移出主表（附录列出），**保留 167 篇，读到作者局限或未来工作 122 篇**。

**读取方式与可信度**：子代理经 WebSearch 找 arXiv 编号后读 arxiv.org/html 的 Conclusion/Limitations/Future Work；arXiv API 被限流（429）。"未读到"= 无预印本、仅有项目页/IEEE 页或结论段未写局限，未编造。局限列为 ≤40 字的摘写，非逐字引文，引用前需回原文核对。"代码"：摘要页或项目页出现链接记"有"，否则"无/未查"。Go2 仅在论文明确写 Unitree Go2 时标 Go2（含仅仿真出现者，见平台列）；"?"=无法确认。序号沿用源表 #。

## 1. 主表

| # | 标题 | 会议年份 | 平台 | 问题 | 方法核心 | 作者自述局限/未来工作 | 代码 | Go2 |
|---|---|---|---|---|---|---|---|---|
| 6 | Bridging the Sim-to-Real Gap for Athletic Loco-Manipulation | RSS25 | B2+Z1臂 | 敏捷腿式操作sim2real | 无监督执行器网络+任务微调 | 需任务参考轨迹;需逐任务设计环境;执行器网络仅覆盖机械臂。未来用生成模型合成参考、扩展到其他子系统 | 有 | 否 |
| 7 | DDAT: Diffusion Policies Enforcing Dynamically Admissible Robot Trajectories | RSS25 | Go2/Go1 | 扩散策略轨迹动力学可行 | 扩散+投影保证动力学可行 | 依赖完美仿真器;训练推理计算昂贵。未来做纯离线无仿真、加速以闭环实机运行 | 有 | Go2 |
| 8 | Discrete-Time Hybrid Automata Learning: Legged Locomotion Meets Skateboarding | RSS25 | Go1+滑板 | 四足滑板运动 | 离散时间混合自动机学习 | 无法泛化到极限滑板技巧;学得动力学不够精确;控制器与预测器耦合。未来环境生成 | 无/未查 | 否 |
| 9 | Gain Tuning Is Not What You Need: Reward Gain Adaptation for Constrained Locomotion Learning | RSS25 | B1(MuJoCo仿真+实机) | 约束运动学习免调增益 | ROGER奖励增益自适应 | 仅限本体约束与零惩罚最优系统;不含外感约束;约束严格可能减慢学习。复杂地形实机学习留待未来 | 无/未查 | 否 |
| 12 | Human2LocoMan: Learning Versatile Quadrupedal Manipulation with Human Pretraining | RSS25 | LocoMan(足端操作器四足) | 四足操作人类预训练 | XR遥操作+跨本体Transformer | 遥操作有学习成本;仅验证LocoMan;多任务协同训练未探索。未来扩展到多种机器人与更大数据 | 有 | 否 |
| 14 | Learned Perceptive Forward Dynamics Model for Safe and Platform-aware Robotic Navigation | RSS25 | ANYmal(仿真含ANYmal-On-Wheels) | 安全平台感知导航 | 感知前向动力学模型+MPPI | 仅几何域;仿真失败与实机失败不一致;未考虑社会规范与动态物体。未来自适应时间步、RGB输入、集成不确定性 | 有 | 否 |
| 17 | NaVILA: Legged Robot Vision-Language-Action Model for Navigation | RSS25 | Go2/Booster T1(实机),H1(仿真) | 足式视觉语言导航 | VLA高层指令+低层运动策略 | 实机部分场景失败、缺纠错;图像VLM计算量大。未来大规模逼真仿真训练、加入显式推理数据 | 有 | Go2 |
| 18 | SATA: Safe and Adaptive Torque-Based Locomotion Policies Inspired by Animal Learning | RSS25 | Go2 | 力矩级安全柔顺运动 | 仿动物学习的力矩策略 | 有载荷时姿态保持差、小腿触地;仅学会基础行走步态。未来扩展复杂地形与敏捷行为、混合肌肉式驱动 | 无/未查 | Go2 |
| 31 | Simulation Distillation: Pretraining World Models in Simulation for Rapid Real-World Adaptation | RSS26 | Go2(四足任务)/UR5e | 世界模型快速实机适应 | 仿真预训练世界模型+实机微调 | 冻结奖励/价值模型限制上限;未用互联网视频或更丰富感知;依赖足够广的仿真覆盖。未来选择性更新价值函数 | 有 | Go2 |
| 33 | Toward Reliable Sim-to-Real Predictability for MoE-based Robust Quadrupedal Locomotion | RSS26 | Go2 | sim2real可预测性评测 | MoE策略+RoboGauge评测套件 | 实机对比场景少;训练曲线不能代表地形性能。未来扩展到人形、融合外感知提升越障 | 有 | Go2 |
| 38 | Constrained Style Learning from Imperfect Demonstrations under Task Optimality | CoRL25 | ANYmal-D(实机)/GR1仿真 | 不完美示范风格学习 | CMDP拉格朗日约束风格奖励 | 不能区分示范中有益与有害特征。未来选择性识别并利用有益示范特征 | 有 | 否 |
| 39 | Contrastive Forward Prediction Reinforcement Learning for Adaptive Fault-Tolerant Legged Robots | CoRL25 | 四足(型号未明)/定制六足 | 腿式机器人关节故障容错 | 对比学习+前向预测误差反馈 | 仅靠本体感知,无视觉触觉。未来融合深度相机、力传感器等外感知 | 无/未查 | ? |
| 40 | Disentangled Multi-Context Meta-Learning: Unlocking Robust and Generalized Task Learning | CoRL25 | Go1 | 多上下文元学习鲁棒泛化 | 解耦上下文向量(基于CAVIA) | 依赖人工定义上下文标签;仅验证回归任务;适应依赖预采数据。未来自动发现上下文、实时选择性适应 | 有 | 否 |
| 41 | Divide, Discover, Deploy: Factorized Skill Learning with Symmetry and Style Priors | CoRL25 | ANYmal-D | 无监督技能发现 | 状态因子化+对称与风格先验 | 复杂交互任务(操作/避障)难学;对称抑制单足抬起;需手工设计。未来扩展更复杂行为与不同形态机器人 | 有 | 否 |
| 43 | FACET: Force-Adaptive Control via Impedance Reference Tracking for Legged Robots | CoRL25 | Go2(实机)/G1/B1+Z1 | 外力自适应柔顺控制 | RL跟踪虚拟质量弹簧阻尼 | 机器人与参考模型动力学差距;缺可靠力与加速度测量致sim2real;固定频率振荡步态。未来解决这些问题 | 无/未查 | Go2 |
| 44 | First Order Model-Based RL through Decoupled Backpropagation | CoRL25 | Go2(实机行走与双足站立) | 一阶梯度MBRL | 解耦反传:仿真轨迹+学习模型梯度 | 要求奖励可微;世界模型过简单不适合图像点云。未来扩展到视觉跑酷等复杂任务、结合更强世界模型 | 无/未查 | Go2 |
| 45 | From Tabula Rasa to Emergent Abilities: Discovering Robot Skills via Real-World Unsupervised Quality-Diversity | CoRL25 | A1 | 实机无监督技能发现 | URSA无监督质量多样性 | 非完全免复位;依赖VAE输入变量选取;仅探索见过的技能;直线漂移。未来从数据学安全边界、改进采样 | 无/未查 | 否 |
| 46 | Granular loco-manipulation: Repositioning rocks through strategic sand avalanche | CoRL25 | 四足(型号未明) | 沙坡推石loco-manipulation | DiffusiveGRAIN扩散预测雪崩动力学 | 纯视觉未捕捉质量等属性;穷举动作序列计算不可扩展;腿与障碍直接接触预测不准 | 无/未查 | ? |
| 50 | Learning a Unified Policy for Position and Force Control in Legged Loco-Manipulation | CoRL25 | B2+Z1臂/G1人形 | 位置力统一控制 | RL统一策略+历史状态估计力 | 高频与工作空间边缘力估计差;sim2real力精度有差距;仅单接触点。未来多点全身力交互 | 有 | 否 |
| 51 | Learning Deployable Locomotion Control via Differentiable Simulation | CoRL25 | ANYmal D(仿真Warp四足+实机) | 可微仿真用于足式运动 | 解析平滑接触模型+SHAC一阶梯度优化 | 墙钟时间高于PPO；PD执行器模型简化；需全可微；未来扩展人形/图像输入/可微崎岖地形 | 无/未查 | 否 |
| 53 | LocoFormer: Generalist Locomotion via Long-context Adaptation | CoRL25 | Go2/Go2-W/G1/H1(另仿真多机型) | 跨形态通用运动 | 长上下文Transformer在线自适应+RL | 训练资源消耗大；程序化任务空间需手工设计，未来可用LLM自动生成任务 | 有 | Go2-W |
| 54 | LocoTouch: Learning Dynamic Quadrupedal Transport with Tactile Sensing | CoRL25 | Go1 | 四足背载物动态运输 | 背部分布式触觉传感+自适应步态奖励 | 圆柱物沿躯干方向易失败；楼梯性能下降；未来加视觉触觉融合、扩展全身触觉 | 有 | 否 |
| 55 | Motion Priors Reimagined: Adapting Flat-Terrain Skills for Complex Quadruped Mobility | CoRL25 | ANYmal-D | 平地技能迁移复杂地形 | 动物运动先验+高层残差分层RL | 高层策略模式坍塌依赖单一步态；训练场景受限；未来扩展跳跃/爬行及间隙等地形 | 无/未查 | 否 |
| 56 | Multi-critic Learning for Whole-body End-effector Twist Tracking | CoRL25 | ANYmal D+Dynaarm机械臂 | 全身末端速度跟踪 | 基于twist指令的多critic RL | 仅适中崎岖地形；肩关节偶触限位；未来加入崎岖地形奖励与感知、训练中纳入关节限位 | 有 | 否 |
| 57 | Multi-Loco: Unifying Multi-Embodiment Legged Locomotion via Reinforcement Learning Augmented Diffusion | CoRL25 | 点足双足/轮式双足/人形/A1四足/Go2(零样本) | 多形态统一运动策略 | RL增强的掩码扩散策略 | 依赖观测-动作配对数据，不能用无动作标签动捕；未来无动作训练、新形态零/少样本适配 | 无/未查 | Go2 |
| 58 | Non-conflicting Energy Minimization in Reinforcement Learning based Robot Control | CoRL25 | Go2(实机)+DMControl/H1仿真 | RL控制能耗最小化 | PEGrad投影梯度消除能耗与任务冲突 | 能耗目标难与风格奖励结合，否则出现不可行行为；未来按优先级递归应用PEGrad | 无/未查 | Go2 |
| 59 | Omni-Perception: Omnidirectional Collision Avoidance of Legged Robots in Dynamic Environments | CoRL25 | G1/Go2(图示,实机平台未明确) | 动态环境全向避障 | 原始LiDAR点云+PD-RiskNet端到端RL | 茂密植被下性能下降；采样降低细节；细小稀疏物体漏检；未来加语义分割、在线微调 | 有 | ? |
| 60 | QuaDreamer: Controllable Panoramic Video Generation for Quadruped Robots | CoRL25 | Go2/Lite3 | 四足全景视频生成 | 基于步态抖动的可控全景视频扩散生成 | 仅控制垂直抖动，缺其他自由度控制；未来扩展RGB-X多传感器、IMU位姿、LLM标注 | 有 | Go2 |
| 63 | Sampling-based System Identification with Active Exploration for Legged Sim2Real Learning | CoRL25 | Go2/G1 | 足式sim2real系统辨识 | 采样式参数辨识+Fisher信息主动激励 | 人形仅限阶段1；仅离线；依赖多行为策略；高维下CMA-ES成本高 | 有 | Go2 |
| 64 | SDS – See it, Do it, Sorted: Quadruped Skill Synthesis from Single Video Demonstration | CoRL25 | Go1(实机)/ANYmal-D(仿真) | 单视频四足技能合成 | GPT-4o由视频生成奖励+PPO | 需侧视清晰视频；仅平地；单次训一技能；依赖仿真全状态；未来户外、多技能、人形 | 有 | 否 |
| 66 | Toward Real-World Cooperative and Competitive Soccer with Quadrupedal Robot Teams | CoRL25 | Go1 | 四足多机足球协作竞争 | 分层多智能体RL+Livox LiDAR感知 | 仅1v1/2v1；球遮挡LiDAR检测受影响；未来训练模拟遮挡、扩展人形 | 无/未查 | 否 |
| 67 | Towards Embodiment Scaling Laws in Robot Locomotion | CoRL25 | Go2/H1(实机)+约1000生成形态仿真 | 形态规模化缩放律 | GenBot-1K程序化形态+单策略训练 | 仅平地运动；形态设计空间固定；实机仅两平台；需更广物理平台验证 | 有 | Go2 |
| 69 | Unsupervised Skill Discovery as Exploration for Learning Agile Locomotion | CoRL25 | A1 | 敏捷运动探索 | 无监督技能发现作为RL探索 | 需人工指定引导探索的状态维度；观测噪声致训练不稳；未来提升技能发现鲁棒性 | 有 | 否 |
| 70 | Versatile Loco-Manipulation through Flexible Interlimb Coordination | CoRL25 | Spot+机械臂 | 灵活肢体协调移动操作 | ReLIC双控制模块动态分配肢体 | 接触点/语言接口为开环目标，实时反馈脆弱；依赖标准IK；未来模仿学习、学习式操作控制 | 有 | 否 |
| 72 | Actuator Dynamics Curricula for Narrow-Viability Tasks in Legged Robot Learning | CoRL26 | 足式 | 执行器动力学课程 | 未读到 | 未读到 | 无/未查 | ? |
| 75 | CA-GMT: Contact-Aware Low-Rank Adaptation of Motion Tracking for Whole-Body Teleoperation | CoRL26 | 足式 | 全身遥操作运动跟踪 | 未读到 | 未读到 | 无/未查 | ? |
| 80 | CMP: Robust Whole-Body Tracking for Loco-Manipulation via Competence Manifold Projection | CoRL26 | Go2+Hexfellow Saber机械臂 | 全身跟踪OOD鲁棒 | 胜任流形投影+同构潜空间安全估计 | 45次实机3次失败；球形边界罕见边界失效；未来环境条件化应对动力学变化、逼近绝对安全保证 | 有 | Go2 |
| 83 | Continual Quadruped Robots Coordination via Sementic Skill Discover | CoRL26 | Go2(1-4台) | 多四足持续协作 | 语义技能库检索+LoRA适配器 | 仅受控多四足任务族；检索未建模物理可迁移性；未来闭环技能管理、更细子技能 | 有 | Go2 |
| 85 | Damage-Aware Quadruped Locomotion: Zero-Shot Adaptation to Motor Failures via Pain-Inspired Reinforcement Learning | CoRL26 | 四足 | 电机故障下的运动适应 | 痛觉启发强化学习零样本适应 | 未读到 | 无/未查 | ? |
| 90 | FT-WBC: Learning Fault-Tolerant Whole-Body Control for Legged Loco-Manipulation | CoRL26 | Go2+机械臂 | 足式操作机器人执行器故障 | 上下身解耦策略+故障估计+姿态适应 | 仅单执行器故障，未处理多关节并发；评估限静止或顺序任务；行走中动态操作留作未来 | 有 | Go2 |
| 109 | Learning Contact Representation for Leg Odometry | CoRL26 | Go2实机+ANYmal仿真 | 腿式里程计足端接触检测 | 去噪自编码器+GMM后验调ZUPT协方差 | 后验仅为序数可靠性分数；各向同性协方差；未在乱石/陡坡验证；未来用VAE与步态周期先验 | 有 | Go2 |
| 110 | Learning Loco-Manipulation From SMPC Demonstrations With Sparse Offline-to-Online RL | CoRL26 | Spot+臂,G1 | 稀疏奖励的足式操作学习 | SMPC离线示范+稀疏奖励离线转在线RL | 策略局限于示范分布；底层控制器冻结无法适应；依赖状态信息，未来解冻底层、转视觉策略 | 有 | 否 |
| 112 | LoComposition: Terrain-Adaptive Energy-Efficient Quadruped Locomotion without Gait Priors | CoRL26 | Go2实机+Spot/ANYmal仿真 | 无步态先验的节能地形适应 | 任务/限位/能耗/感知分离奖励设计 | 仅测Go2特定地形；各速度均小跑；on-policy样本效率；无形式化安全保证；其他构型与板载状态估计待做 | 有 | Go2 |
| 116 | Mind the Phase: Effective Rank and Representation Health in Legged Locomotion | CoRL26 | Spot实机,ANYmal-D/H1仿真 | 策略表征健康度分析 | 按步态相位条件化Jacobian有效秩 | 未测RNN/Transformer等架构；未探非对称AC；并非所有平台上实机；未来扩展到其他机器人与地形 | 有 | 否 |
| 117 | MorFiC: Fixing Value Miscalibration for Zero-Shot Quadruped Transfer | CoRL26 | Go2训练,Go1/Go2实机 | 跨四足形态零样本迁移 | 形态隐变量FiLM调制critic | 迁移依赖形态距离，B1/ANYmal-C失败；受训练机器人锚定；未来结合少量多源训练、扩展到双足人形 | 有 | Go2 |
| 118 | Morphology-Conditioned World Model for Cross-Embodiment Quadrupedal Locomotion | CoRL26 | ANYmal-D/Go1实机(Go2仅仿真训练集) | 跨形态四足世界模型 | 形态条件化DreamerV3世界模型 | 限固定三段腿12DoF四足模板；评估仅盲走平地速度跟踪，无外感知与接触丰富地形 | 有 | 否 |
| 120 | MPC-Injection: Biasing Off-Policy Locomotion RL Toward Controller-Induced Behavior Basins | CoRL26 | Go2+2D walker | 离策略RL行为偏置 | MPC轨迹注入回放缓冲区 | 仅简单速度跟踪；长训练牵引可能减弱；依赖现成控制器；未来课程注入、在线选择MPC轨迹 | 有 | Go2 |
| 128 | PROOF: Perceptive Robustness via Out-of-Distribution Fallback for Legged Locomotion | CoRL26 | Go2 | 视觉退化下感知运动鲁棒性 | 师生蒸馏+不确定性门控回退本体感知 | 故障注入无法覆盖所有情况；对数方差非校准估计；未来减少手工OOD注入、改进不确定性评估 | 有 | Go2 |
| 135 | S2M-Trek: From Single to Multi-Sphere Transport via Per-Frame Deep Sets on a Wheel-Legged Robot | CoRL26 | 自研轮足 | 轮足背板多球体运输 | 逐帧Deep Sets置换不变编码 | 定量结果基于仿真，实机仅定性；未来标定触觉、重复随机实验、研究时序关联 | 有 | 否 |
| 136 | SHOES: Sim-to-real Hardware-adaptation via On-policy Expansion of Skills for Legged Robots | CoRL26 | Go2 | 穿鞋导致形态变化的适应 | 冻结策略+FiLM/线性适配器在线微调 | 系统不含物理复位，频繁摔倒的鞋不可行；未来加入跌倒检测、自主起身与复位管理 | 有 | Go2 |
| 148 | Trajectory-Level Automatic Curriculum Learning for Legged Locomotion on Unstructured Terrain | CoRL26 | Go2实机 | 非结构地形自动课程 | CVAE难度评估+MCMC轨迹采样 | 高度结构化动作(跑酷)需更有方向的探索；未来引入弱任务先验或示范引导采样 | 无/未查 | Go2 |
| 150 | Unified Whole-Body Control for Quadrupedal Tactile-Informed Loco-Manipulation | CoRL26 | Go2+WidowX臂 | 外力下触觉足式抓取操作 | 触觉隐变量+统一PPO策略 | 仿真难复现夹爪与触觉形变；伺服臂难建模，期望扭矩可控背驱臂提升动态性能 | 无/未查 | Go2 |
| 151 | Unleashing Infinite Motion: Scaling Expressive Quadrupedal Motion via Generative Video Priors | CoRL26 | Go2 | 四足表现性动作数据规模化 | 视频生成先验+URDF运动拟合+PPO跟踪 | 视频扩散语义控制不精确需人工筛选；机器人须全程在画，偏向原地动作，大位移需多视角 | 有 | Go2 |
| 160 | A Modular Residual Learning Framework to Enhance Model-Based Approach for Robust Locomotion | ICRA26/RA-L | Go1 | MPC模型失配下鲁棒运动 | 残差落足点RL+残差动力学监督学习 | 需更广泛条件评估；未来研究土壤柔软、顺应、湿滑等地形不确定性 | 无/未查 | 否 |
| 161 | Action-Informed Estimation and Planning: Clearing Clutter on Staircases Via Quadrupedal Pedipulation | ICRA26 | Spot四足 | 楼梯推物清障 | 动作感知估计+RL足推策略 | 里程计漂移/轻物体接触弱/相机视野窄；拟加任务规划、先验、接触估计 | 无/未查 | 否 |
| 162 | Active Dynamic Load Adaptation for Quadruped Locomotion on Complex Terrain | ICRA26 | 四足 | 动态负载复杂地形稳定 | 主动负载逆动力+地形前向模型RL | 未读到 | 无/未查 | ? |
| 163 | Adaptive Legged Locomotion Via Online Learning for Model Predictive Control | ICRA26/RA-L | Go2(仿真) | 未知残差动力学MPC | RFF在线学习残差+MPC | 结论未写局限/未来工作 | 有 | Go2 |
| 165 | Agile Hauler Curriculum: Learning High-Speed Locomotion for Robots under Demanding Payloads | ICRA26 | 足式 | 重载高速运动 | 课程学习 | 未读到 | 无/未查 | ? |
| 167 | AINav: Large Language Model-Based Adaptive Interactive Navigation | ICRA26 | Go2 | 无路时交互式导航 | LLM技能树+自适应重规划 | 简化视觉与预设可执行约束限泛化；拟用视觉基础模型、增技能、扩平台与长时程 | 无/未查 | Go2 |
| 168 | APREBot: Active Perception System for Reflexive Evasion Robot | ICRA26 | Go2 | 任意方向障碍反射避让 | LiDAR全向扫描+相机主动跟踪 | 未测运动中避障与密集障碍；拟扩展到更复杂场景 | 有 | Go2 |
| 171 | CAIMAN: Causal Action Influence Detection for Sample-Efficient Loco-Manipulation | ICRA26 | Go2 | 样本高效足式推物 | 因果动作影响探索 | 结论未写局限/未来工作 | 无/未查 | Go2 |
| 172 | Can a Robot Walk the Robotic Dog: Triple-Zero Collaborative Navigation for Heterogeneous Multi-Agent Systems | ICRA26 | 人形G1+Go2 Edu | 异构多机协同导航 | 零训练零先验MLLM引导TZPP | 复杂环境仍落后人类的隐式空间推理与长时程规划 | 有 | Go2 |
| 173 | Causal Transformer-Based Online Action Recognition for High-Level Control of a Unitree Go1 Robot | ICRA26 | Go1 | 人体动作识别控制机器人 | 因果Transformer在线识别 | 未读到 | 无/未查 | 否 |
| 178 | Collaborative Quadruped Transportation in 3D Terrain with Constrained Diffusion | ICRA26 | 四足 | 多四足3D地形协同运输 | 约束扩散上层轨迹+下层速度控制 | 未读到 | 无/未查 | ? |
| 180 | DAPPER: Discriminability-Aware Policy-To-Policy Preference-Based Reinforcement Learning for Query-Efficient Robot Skill Acquisition | ICRA26 | ANYmal | 偏好RL查询效率 | 多策略对比查询+可辨别性奖励 | 依赖手工特征；每轮重训贵；标签噪声；仅四足运动，拟扩展操作/人形 | 无/未查 | 否 |
| 181 | DeepSkate: Reinforcement Learning of a Robust Controller for Energy Efficient Quadruped Skating | ICRA26 | 四足(被动轮滑行,型号未读到) | 四足滑行节能鲁棒 | 端到端RL+sim2real | 仅读到摘要页，未见局限；称为轮足研究奠基 | 无/未查 | ? |
| 182 | Disturbance-Aware Adaptive Compensation in Hybrid Force-Position Locomotion Policy for Legged Robots | ICRA26 | Go2 | 负载/外力扰动 | 力位混合策略+动量扰动观测补偿 | 无理论保证；扰动仅限质心外力；拟研究更丰富扰动模型与理论分析 | 无/未查 | Go2 |
| 183 | Diverse Skill Discovery in Fourier Latent Space Via Unsupervised Learning | ICRA26 | A1(据摘要页) | 四足多样技能发现 | 傅里叶潜空间互信息奖励 | 未读到(arXiv全文未定位) | 无/未查 | 否 |
| 185 | DreamFlow: Local Navigation Beyond Observation Via Conditional Flow Matching in the Latent Space | ICRA26 | Go2 | 视野外局部导航 | 条件流匹配预测潜在地形 | 拟研究预测视距、端到端合并训练、多潜在预测应对动态环境 | 无/未查 | Go2 |
| 187 | Efficient and Versatile Quadrupedal Skating: Optimal Co-Design Via Reinforcement Learning and Bayesian Optimization | ICRA26 | Go1(被动轮) | 四足滑行设计与控制协同 | 贝叶斯优化轮设计+RL | 仅平地；拟扩展室外不平地形、轻耐用轮、更省样本；滑行与行走融合 | 无/未查 | 否 |
| 192 | Enhancing Robustness of Locomotion Policy for Quadrupedal Robot with Deep Disturbance Observer | ICRA26/RA-L | 四足 | 运动策略抗扰 | 深度扰动观测器+状态估计 | 未读到(无arXiv版) | 无/未查 | ? |
| 194 | Feasibility-Guided Planning Over Multi-Specialized Locomotion Policies | ICRA26 | A1 | 多专用策略规划 | Feasibility-Net+经典规划器 | 定位不准致过早切换；假设策略切换零代价；未列未来工作 | 有 | 否 |
| 195 | Flexible Locomotion Learning with Diffusion Model Predictive Control | ICRA26 | Go2 | 测试时灵活行为适配 | 扩散模型作动力学先验的MPC | 仅简单约束类；拟加视觉/语言输入、无离线数据交互微调 | 有 | Go2 |
| 196 | Floating-Base Deep Lagrangian Networks | ICRA26 | Go2仿真/Spot/HyQReal2/Talos | 浮动基动力学辨识 | 物理一致惯量参数化灰盒 | 拟用于运动与移动操作、作学习动力学模型或配合自适应控制 | 有 | Go2 |
| 197 | FT-CPG: Learning Central Pattern Generators for Fault-Tolerant Quadruped Locomotion under Multi-Joint Failures | ICRA26/RA-L | 四足 | 多关节故障下的四足运动 | 冻结CPG加每腿故障残差策略 | 未读到 | 无/未查 | ? |
| 198 | Full-Scale Autonomous Highway Inspection with Quadruped Robot: Multi-Level Locomotion Learning in Complex Environments | ICRA26 | 四足 | 高速公路自主巡检 | 多层级运动学习 | 未读到 | 无/未查 | ? |
| 199 | GIMloco: Generic Internal Model-Based Locomotion for Quadruped Robots | ICRA26 | 四足 | 仅本体感知的历史编码 | 一阶积分系统构造内部模型空间 | 未读到 | 无/未查 | ? |
| 200 | GRAM: Generalization in Deep RL with a Robust Adaptation Module | ICRA26 | Go2 | 分布内外动力学泛化 | 不确定度驱动的鲁棒自适应模块 | 极端OOD场景可能失败；拟结合其他鲁棒RL，扩展到其他机器人与任务 | 有 | Go2 |
| 202 | Hebbian Attractor Networks for Robot Locomotion | ICRA26 | Go1(仿真) | 在线可塑性步态适应 | 赫布更新加归一化形成吸引子 | 进化策略样本效率低；仅周期运动；拟做多吸引子与实机实验 | 有 | 否 |
| 207 | KiRAS: Keyframe Guided Self-Imitation for Robust and Adaptive Skill Learning in Quadruped Robots | ICRA26 | Solo-8/Go1 | 关键帧多技能与地形自适应 | 关键帧引导自模仿DRL | 拟做基于环境线索的自适应技能切换，并结合外感知扩展到导航 | 有 | 否 |
| 208 | Knowledge-Based Locomotion Policy for Quadruped Robots under Incomplete Terrain Observation | ICRA26 | 四足(表标Go2) | 地形观测不完整下的运动 | 知识引导运动策略 | 未读到 | 无/未查 | ? |
| 212 | Learning Autonomous and Safe Quadruped Traversal of Complex Terrains Using Multi-Layer Elevation Maps | ICRA26/RA-L | 四足 | 复杂地形安全自主通行 | 多层高程图分层控制 | 未读到 | 无/未查 | ? |
| 213 | Learning Collision-Free Object Goal Pushing for Quadruped Robots with Safe Corridors | ICRA26 | 四足 | 无碰撞物体推送 | 安全走廊约束的学习策略 | 未读到 | 有 | ? |
| 214 | Learning Forward Looking Adaptation to Dynamic Payloads for Quadruped Locomotion Via Physics-Informed Neural Networks | ICRA26 | 四足 | 动态负载前瞻自适应 | 物理信息神经网络前瞻自适应 | 未读到 | 无/未查 | ? |
| 217 | Learning Neural Observer-Predictor Models for Limb-Level Sampling-Based Locomotion Planning | ICRA26 | Vision 60 | 肢体级采样规划的动力学预测 | 神经观测器加预测器接入MPPI | 局限为仅平地运动；未来扩展到复杂不平地形 | 无/未查 | 否 |
| 218 | Learning Quadruped Walking from Seconds of Demonstration | ICRA26 | Go2 | 极少演示的模仿学习 | 潜变量变化正则化 | 未来分析正则化学习动力学，结合在线数据，测试更广平台与任务 | 有 | Go2 |
| 219 | Learning Quadrupedal Locomotion for a Heavy Hydraulic Robot Using an Actuator Model | ICRA26/RA-L | BeTheX-Q液压四足 | 重型液压机器人运动 | 解析液压执行器模型加RL | 未测偏离训练分布场景、执行器耐久性、1m/s以上速度；拟扩展地形与平台 | 无/未查 | 否 |
| 220 | Learning Task-Invariant Properties Via Dreamer: Enabling Efficient Policy Transfer for Quadruped Robots | ICRA26 | Go2 | 四足策略高效迁移 | Dreamer加任务不变属性辅助预测 | 长时运行因世界模型累积误差性能下降；拟用更丰富数据并提升长期预测 | 无/未查 | Go2 |
| 221 | Look Forward to Walk Backward: Efficient Terrain Memory for Backward Locomotion with Forward Vision | ICRA26 | Lite3四足 | 仅前向视觉的后退行走 | DeltaNet地形记忆 | 隐式记忆时域无保证，偶有失败；拟引入估计器不确定性 | 无/未查 | 否 |
| 223 | MARG: MAstering Risky Gap Terrains for Legged Robots with Elevation Mapping | ICRA26/T-RO | Go1/Go2 | 危险间隙地形通行 | 高程图加特权估计网络RL | 依赖LiDAR点云精度；仅能trot步态；拟扩展软滑不稳地形 | 无/未查 | Go2 |
| 224 | MemClaw-RAG: Memory-Driven Navigation and Adaptive Locomotion for Wheeled-Legged Robots in Dynamic Environments | ICRA26 | 轮足 | 动态环境记忆驱动导航 | RAG记忆加自适应运动 | 未读到 | 无/未查 | ? |
| 227 | MUJICA: Multi-Skill Unified Joint Integration of Control Architecture for Wheeled-Legged Robots | ICRA26 | Go2-W | 轮足多技能统一控制 | 单一本体感知策略加技能选择 | 拟扩展到更多运动技能，实现非结构化地形自适应协调 | 有 | Go2-W |
| 228 | MULE – Multi-Terrain and Unknown Load Adaptation for Effective Quadrupedal Locomotion | ICRA26/RA-L | Go1 | 多地形未知负载运动 | 名义策略加自适应修正策略 | 未读到明确局限或未来工作段 | 有 | 否 |
| 229 | Multi-Quadruped Cooperative Object Transport: Learning Decentralized Pinch-Lift-Move | ICRA26 | Go2(+D1机械臂) | 多四足协同搬运无法抓取物体 | 去中心化RL+星座奖励，捏-抬-移 | 臂动力学未知需手调增益、编码器偏移需外部标定；臂力矩限载荷(1-2kg)；sim2real差距大。未来：高层规划、自主接触分配、更丰富传感、更多地形及其他平台 | 有 | Go2 |
| 231 | Neural Internal Model Control: Learning a Robust Control Policy Via Predictive Error Feedback | ICRA26 | Aliengo+四旋翼 | 扰动下鲁棒控制 | 刚体模型预测+RL预测误差反馈 | 无独立局限节。未来：做更多实机实验、更多机器人；基线超参扫描有限；噪声大时预测模型精度更关键 | 有 | 否 |
| 232 | OmniNet: Omnidirectional Jumping Neural Network with Height-Awareness for Quadrupedal Robots | ICRA26/RA-L | 四足 | 全向跳跃与高度感知 | 未读到 | 未读到 | 无/未查 | ? |
| 234 | One Filter to Deploy Them All: Robust Safety for Quadrupedal Navigation in Unknown Environments | ICRA26/T-RO | Go1 | 未知环境四足导航安全 | 自适应安全滤波器+LiDAR(OCR-VN)零样本 | 结论段未自述局限或未来工作 | 无/未查 | 否 |
| 235 | OpenHEART: Opening Heterogeneous Articulated Objects with a Legged Manipulator | ICRA26 | Go2+ViperX300机械臂 | 开多种铰接物体 | 低维特征SAFE+ArtIEst估计+分层规划 | 当前仅在回合初给定固定物体位姿。未来：集成机载物体位姿估计 | 有 | Go2 |
| 238 | Phase-Aware Policy Learning for Skateboard Riding of Quadruped Robots Via Feature-Wise Linear Modulation | ICRA26 | Go1 | 四足骑滑板 | 相位条件FiLM的统一RL策略 | 未来：加入高层导航策略生成速度指令并调制相位时钟，以便及时上板等(原文被截断) | 无/未查 | 否 |
| 241 | Primal-Dual iLQR for GPU-Accelerated Learning and Control in Legged Robots | ICRA26/RA-L | Aliengo(文中提及Go2仅1处) | GPU加速腿足MPC | JAX并行Primal-Dual iLQR求解器 | 未来：把该MPC作为偏置用于运动策略学习；加入更完善的不等式约束处理方法 | 有 | 否 |
| 242 | Proprioceptive Image: An Image Representation of Proprioceptive Data from Quadruped Robots for Contact Estimation Learning | ICRA26 | 四足(型号未读明) | 接触估计 | 本体数据编码成图像+CNN | 未来：接入GNN/RL输入；结合相机等外感知；拓展到人形和机械臂 | 无/未查 | ? |
| 243 | RAMBO: RL-Augmented Model-Based Whole-Body Control for Loco-Manipulation | ICRA26/RA-L | Go2(四足与双足站立模式) | 全身移动操作 | QP模型控制前馈+RL反馈 | 仅用本体感知，状态估计漂移影响性能。未来：加入更多传感、全阶WBC动力学、人形应用、在线模型自适应 | 有 | Go2 |
| 244 | REBot: Reflexive Evasion Robot for Instantaneous Dynamic Obstacle Avoidance | ICRA26 | Go2 | 瞬时动态障碍规避 | RL耦合快速躲避与稳定恢复 | 障碍位置感知作为假设，留待后续；规避偏向后跳(腿型所致)；电机层sim2real差距仍在 | 有 | Go2 |
| 246 | Reinforcement Learning-Based Robust Wall Climbing Locomotion Controller in Ferromagnetic Environment | ICRA26 | 四足磁吸爬壁机器人(8kg,电永磁足) | 铁磁壁面爬行 | 三阶段课程+EPM吸附模型+随机失吸 | 未来：扩展到曲面、缝隙、不规则钢结构；实现地-壁-顶过渡等更丰富爬行技能 | 无/未查 | 否 |
| 247 | RENet: Fault-Tolerant Motion Control for Quadruped Robots Via Redundant Estimator Networks under Visual Collapse | ICRA26/RA-L | Go1 | 视觉失效下容错运动控制 | 冗余估计网络+异常检测切换器 | 缺乏完整3D语义理解，对强光等光照变化鲁棒性有限。未来：先进语义感知、提升RL鲁棒与安全、扩展到人形 | 有 | 否 |
| 249 | Risk-Aware Reinforcement Learning with Bandit-Based Adaptation for Quadrupedal Locomotion | ICRA26 | Go2 | 风险自适应四足运动 | CVaR约束RL+UCB老虎机在线选策略 | 假设平均回报平稳(非平稳场景可能失效)；老虎机沿用训练奖励，忽略执行风险。未来：部署时引入显式风险度量 | 无/未查 | Go2 |
| 253 | Safe Whole-Body Loco-Manipulation Via Combined Model and Learning-Based Control | ICRA26 | Go2+D1机械臂+F/T传感器 | 安全的力跟随移动操作 | Reference Governor+神经卡尔曼滤波 | 未来：提升全自由度(尤其力矩)跟踪；在抓取不同物体数据上训练滤波器；人机交互中加入视觉 | 无/未查 | Go2 |
| 254 | Scalable Multi-Objective Robot Reinforcement Learning through Gradient Conflict Resolution | ICRA26 | Go2/G1等(IsaacLab仿真基准) | 多目标奖励冲突 | PPO多头critic+梯度冲突消解(GCR-PPO) | 种子方差增大、梯度手术增加训练时间；优先级方案无Pareto保证。未来：分析冲突、乘性/非线性奖励、提升效率、更难基准 | 有 | Go2 |
| 257 | SlipSense: Multimodal Sensing for Online Slip Detection in Legged Robots | ICRA26 | Go1 | 在线足端滑移检测 | 多模态力传感+自监督异常检测 | 仅验证于刚性均质地面与固定trot步态；二分类标签在阈值附近有歧义。未来：非结构地面、摩擦估计与滑移恢复、四足全装传感器 | 无/未查 | 否 |
| 259 | Spatio-Temporal Motion Retargeting for Quadruped Robots | ICRA26/T-RO | 多平台(A1/Go1/Go2/AlienGo/Solo,四平台实机) | 四足运动重定向 | 时空优化生成动力学可行参考+RL | 结论未列明确局限。未来：结合模型/学习控制器、双足及移动操作、用网络视频构建大规模运动数据 | 有 | Go2 |
| 261 | START: Traversing Sparse Footholds with Terrain Reconstruction | ICRA26 | DEEP Robotics Lite3 | 稀疏落脚点地形穿越 | 局部高程图重建+AdaSmpl单阶段训练 | 仅评估四种地形。未来：更多场景(楼梯、巨石)、更精细边缘保留的高程图、体素等中间表示 | 无/未查 | 否 |
| 264 | Swimming under Constraints: A Safe Reinforcement Learning Framework for Quadrupedal Bio-Inspired Propulsion | ICRA26 | 四足(型号未读明) | 四足仿生游泳 | 约束RL(ACPPO-PID)限制横向力与幅度 | 仅在静水中验证，强流/湍流下性能未知。未来：在线自适应与域随机化以适应开放水域 | 无/未查 | ? |
| 266 | TD-CD-MPPI: Temporal-Difference Constraint-Discounted Model Predictive Path Integral Control | ICRA26 | Solo12 | MPPI采样多、视野短 | TD终值函数+约束折扣调制 | 未读到 | 有 | 否 |
| 267 | Teaching to Individual Needs: Bidirectional Teacher-Student Learning for Wheeled-Legged Locomotion | ICRA26 | 轮足 | 未读到 | 未读到 | 未读到 | 无/未查 | ? |
| 268 | Tightly-Coupled LiDAR-IMU-Leg Odometry with Online Learned Leg Kinematics Incorporating Foot Tactile Information | ICRA26 | Go2 | 无特征/软地面里程计漂移 | LiDAR-IMU-腿运动学紧耦合+在线学习足力 | 未来扩展网络推断地形类别与外力以用于腿式控制;推广到更通用连杆参数并开源 | 有 | Go2 |
| 273 | Traversability-Aware Legged Navigation by Learning from Real-World Visual Data | ICRA26/T-RO | Go1 | 可通行性感知导航 | 价值函数估计可通行性+真机RL训练RGBD规划器 | 结论未述局限或未来工作 | 无/未查 | 否 |
| 275 | U2E: Uncertainty-Aware Modeling and Uncertainty-Guided Exploration with Deep Ensemble for Quadrupedal Robot | ICRA26 | 四足 | 未读到 | 未读到 | 未读到 | 无/未查 | ? |
| 280 | VOCALoco: Viability-Optimized Cost-Aware Adaptive Locomotion | ICRA26/RA-L | ANYmal-D | 地形下技能选择 | 预测各技能可行性与CoT后择优切换 | 未来将离散技能切换扩展为策略混合 | 有 | 否 |
| 281 | When the Adversary Knows You Better: Adversarial Training for Learning-Based Legged Robots | ICRA26 | 足式 | 未读到 | 未读到 | 未读到 | 无/未查 | ? |
| 282 | X-Nav: Learning End-To-End Cross-Embodiment Navigation for Mobile Robots | ICRA26 | Go2(仿真)+Jackal/TurtleBot2(真机轮式) | 跨本体端到端导航 | RL专家策略蒸馏为Transformer通用策略 | 将扩展到人形等更多本体及不同自由度;加入物体目标导航 | 有 | Go2 |
| 283 | 16 Ways to Gallop: Energetics and Body Dynamics of High-Speed Quadrupedal Gaits | IROS25 | A1 | 高速奔跑步态能耗分析 | 轨迹优化+Gazebo QP控制器验证 | 未来将在硬件上实现这些奔跑步态做真机验证 | 有 | 否 |
| 284 | A Unified Framework to Learn Collision-Free Loco-Manipulation Via Adversarial Motion Priors | IROS25 | 未读到(腿式机械臂) | 无碰撞移动操作 | 轨迹优化运动先验+MPPI避碰操作 | 未读到 | 有 | ? |
| 288 | An Online Terrain Classification Framework for Legged Robots Based on Fusion of Proprioceptive and Exteroceptive Sensors | IROS25 | 足式 | 未读到 | 未读到 | 未读到 | 无/未查 | ? |
| 294 | CROSS-GAiT: Cross-Attention-Based Multimodal Representation Fusion for Parametric Gait Adaptation in Complex Terrains | IROS25 | Vision60 | 复杂地形步态参数自适应 | 视觉与时序交叉注意力融合调步高/髋展 | 并非所有地形的潜在表征都已优化;未来细化表征、加传感数据、离线RL免标注 | 无/未查 | 否 |
| 297 | Efficient Learning of a Unified Policy for Whole-Body Manipulation and Locomotion Skills | IROS25 | X20+Z1 | 腿式机械臂全身控制 | 运动学模型融入RL+物理可行性奖励 | 机械臂工作空间内精度不一致;未来融合更多物理模型、构建高层规划器 | 有 | 否 |
| 298 | Energy-Efficient Motion Planner for Legged Robots | IROS25 | A1 | 腿式机器人节能规划 | 落足集合规划+速度自适应参数 | 高速非线性动力学挑战线性MPC假设;腿动力学耦合、硬件节能对比留作未来 | 无/未查 | 否 |
| 299 | Energy-Efficient Omnidirectional Locomotion for Wheeled Quadrupeds Via Predictive Energy-Aware Nominal Gait Selection | IROS25 | 轮足(改装Go1,16DoF) | 轮足全向节能运动 | 功率预测网络选步态+残差RL | 结论未述局限或未来工作 | 有 | 否 |
| 300 | Env-Mani: Quadrupedal Robot Loco-Manipulation with Environment-In-The-Loop | IROS25 | 四足(型号未读到) | 借环境支撑够取远处物体 | 特权教师-深度学生RL | 项目页未述局限(仅读到项目页,未读全文) | 有 | ? |
| 301 | Explosive Jumping with Rigid and Articulated Soft Quadrupeds Via Example Guided Reinforcement Learning | IROS25 | Go1(仿真) | 爆发式跳跃 | 单示范轨迹优化+示例引导RL | 未来将把学到的策略用于真实机器人 | 无/未查 | 否 |
| 303 | FR-Net: Learning Robust Quadrupedal Fall Recovery on Challenging Terrains through Mass-Contact Prediction | IROS25/RA-L | Go2 | 复杂地形摔倒恢复 | 质量-接触预测器+非对称AC奖励设计 | 仅估计本体与关节碰撞而非精确接触位置;未来考虑触觉传感器 | 无/未查 | Go2 |
| 304 | Gait in Eight: Efficient On-Robot Learning for Omnidirectional Quadruped Locomotion | IROS25 | HoneyBadger | 真机在线学习全向步态 | CrossQ离策略8分钟真机训练 | 步态不够直、速度未达目标;未来加视觉惯性里程计、视觉观测、预训练微调 | 有 | 否 |
| 305 | Generalized Locomotion in Out-Of-Distribution Conditions with Robust Transformer | IROS25 | Go1(实机)/A1(仿真)/六足(仿真) | 分布外条件下运动泛化 | 鲁棒Transformer控制器 | 无单独局限段；未来探索更强泛化能力、新障碍通行与新运动技能 | 无/未查 | 否 |
| 306 | HAC-LOCO: Learning Hierarchical Active Compliance Control for Quadruped Locomotion under Continuous External Disturbances | IROS25 | Go1 | 持续外力扰动下柔顺控制 | 分层主动柔顺强化学习 | 未来工作：基于感知反馈自适应选择力阈值与虚拟阻抗 | 无/未查 | 否 |
| 307 | Helpful DoggyBot: Open-World Object Fetching Using Legged Robots and Vision-Language Models | IROS25 | Go2 | 开放世界取物 | VLM+足式低层策略+1自由度夹爪 | 局限：夹爪灵巧性受限、依赖天花板相机导航、可能遮挡；未来：不损敏捷性增强操作，仅用机载传感器导航 | 有 | Go2 |
| 308 | HeStIa: Asynchronous Embodied Dynamic Locomotion Learning for Walking Robots through Multimodal Large Language Models | IROS25 | 足式(型号未读到) | 步行机器人动态运动学习 | 异步多模态大模型视觉-语言-运动融合 | 未读到 | 无/未查 | ? |
| 315 | Integrating Trajectory Optimization and Reinforcement Learning for Quadrupedal Jumping with Terrain-Adaptive Landing | IROS25 | A1 | 四足跳跃与地形自适应着陆 | 轨迹优化结合强化学习 | 未来：更快的轨迹优化与自适应奖励松弛方案 | 无/未查 | 否 |
| 316 | Interactive Navigation for Legged Manipulators with Learned Arm-Pushing Controller | IROS25 | Unitree B2+Z1机械臂 | 可推动障碍的交互导航 | 学习推动控制器+导航框架 | 局限：仅考虑推动技能；未来：加入更多样的操作能力 | 有 | 否 |
| 319 | Learning Accurate Whole-Body Throwing with High-Frequency Residual Policy and Pullback Tube Acceleration | IROS25 | ANYmal+DynaArm | 全身精确投掷 | 高频残差策略+回拉管加速优化 | 局限：残差仅跟踪竖直加速度、速度跟踪提升有限、假设物体质量可忽略；未来：估计物体惯性、改进残差策略 | 无/未查 | 否 |
| 320 | Learning Distributed End-To-End Hunting Locomotion for Multiple Quadruped Robots | IROS25 | 四足(型号未读到) | 多四足协同围猎运动 | 分布式端到端RL+引导向量特权信息 | 未读到(仅读到摘要，IEEE全文未取得) | 有 | ? |
| 323 | Learning Robust and Flexible Locomotion of Wheel-Legged Quadruped Robots in Complex Terrains | IROS25 | 轮足(改装Go1，据IEEE摘要) | 轮足四足复杂地形运动 | 仅IMU与关节传感的单策略RL | 未读到 | 无/未查 | 否 |
| 325 | Learning Symmetric Legged Locomotion Via State Distribution Symmetrization | IROS25 | 四足+人形(据摘要) | 足式运动策略对称性 | 不对称度DoA奖励+判别器 | 未读到 | 无/未查 | ? |
| 326 | Learning to Exploit Leg Odometry Enables Terrain-Aware Quadrupedal Locomotion | IROS25 | 四足(型号未读到) | 仅本体感知的地形感知 | 学习式腿部里程计+RL策略 | 未读到 | 无/未查 | ? |
| 327 | Learning to Traverse Challenging Terrain Using Vision and Forward Kinematics | IROS25 | A1(据IEEE摘要) | 视觉+前向运动学地形通行 | 前向运动学足端高度作训练标签 | 未读到 | 无/未查 | 否 |
| 328 | Learning Whole-Body Control for Small-Sized Quadruped Robots with a Flexible Spine | IROS25 | SQuRo-Lite(据摘要) | 柔性脊柱小型四足全身控制 | 教师-学生在线学习 | 未读到 | 无/未查 | 否 |
| 329 | Learning-Based Quadruped Robot Framework for Locomotion on Dynamic Rigid Platforms | IROS25 | 四足(型号未读到) | 动态刚性平台上的运动 | RL估计平台运动 | 未读到 | 无/未查 | ? |
| 330 | Legged Robot State Estimation Using Invariant Neural-Augmented Kalman Filter with a Neural Compensator | IROS25 | Go1(仿真)；实机型号未读到 | 足式机器人状态估计 | InEKF+神经补偿器 | 局限：依赖数据集，换机型需重训、实机无动捕评估受限；未来：改进补偿器结构，扩展到多种足式机器人 | 有 | 否 |
| 332 | Long-Horizon Locomotion and Manipulation on a Quadrupedal Robot with Large Language Models | IROS25 | Xiaomi Cyberdog2 | 长时程移动操作任务规划 | LLM推理层+RL低层技能 | 局限：技能集由专家固定、仅限较简单场景；未来：扩展更复杂任务并发现新技能 | 有 | 否 |
| 333 | LoopSR: Looping Sim-and-Real for Lifelong Policy Adaptation of Legged Robots | IROS25 | A1 | 部署后策略持续适应 | 真实数据回灌仿真持续训练 | 局限：需进一步理论分析、不含视觉；未来：用视觉输入在仿真中重建真实世界、学习新技能 | 有 | 否 |
| 334 | Manipulate-To-Navigate: Reinforcement Learning with Visual Affordances and Manipulability Priors | IROS25 | Boston Dynamics Spot | 先操作移障再导航 | RL+可供性图+可操作度先验 | 局限：分割误差、操作中视角变化、标定投影误差；未来：动作空间改3D世界坐标，推广到更多任务 | 无/未查 | 否 |
| 335 | MoE-Loco: Leveraging Mixture of Experts for Multi-Task Locomotion | IROS25 | Go2 | 多任务多步态运动 | 混合专家单策略 | 未来：引入相机与激光雷达感知增强复杂任务适应性 | 有 | Go2 |
| 336 | Mysteric-Net: MIMO Hysteretic Friction-Aware Lagrangian-Based Network for Legged Robot | IROS25 | 未知 | 未读到 | 未读到 | 未读到 | 无/未查 | ? |
| 338 | Non-Gaited Legged Locomotion with Monte-Carlo Tree Search and Supervised Learning | IROS25/RA-L | Aliengo(四足) | 无固定步态的足端规划 | MCTS+监督学习价值函数引导MPC | 未来整合视觉反馈；采用更复杂高效的机器人模型 | 无/未查 | 否 |
| 340 | Playful DoggyBot: Learning Agile and Precise Quadrupedal Locomotion | IROS25 | Go2 | 四足敏捷精确交互 | 感知控制解耦RL+被动夹爪 | 实机与仿真有差距(硬件/sim2real/检测噪声)；检测频率不足；将拓展任务范围 | 无/未查 | Go2 |
| 341 | Preference Aligned Diffusion Planner for Quadrupedal Locomotion Control | IROS25 | Go1 | 有限数据下扩散规划不稳 | 离线扩散+在线弱偏好对齐 | 未来融入视觉、语言等额外模态 | 有 | 否 |
| 343 | QuietPaw: Learning Quadrupedal Locomotion with Versatile Noise Preference Alignment | IROS25 | Go2 | 降低足端噪声 | 噪声条件约束策略CNCP | 扩展到更复杂环境；引入人在环个性化噪声调节 | 无/未查 | Go2 |
| 346 | RoboDuet: Learning a Cooperative Policy for Whole-Body Legged Loco-Manipulation | IROS25/RA-L | Go1+ARX5臂(零样本迁移A1/Go2) | 四足臂全身操作 | 双策略协作训练 | 需接高层规划与碰撞检测；仅能固定目标位姿处理坡/碎石，未做楼梯 | 有 | 否 |
| 347 | Robust Ladder Climbing with a Quadrupedal Robot | IROS25 | ANYmal D | 四足爬梯 | RL+钩状末端执行器 | 未来实现上下梯；学生加深度相机以适应工业现场梯 | 有 | 否 |
| 348 | SF-TIM: A Simple Framework for Enhancing Quadrupedal Robot Jumping Agility by Combining Terrain Imagination and Measurement | IROS25 | Lite3/X30(四足) | 四足跳跃 | 地形想象奖励+高程图 | 仅聚焦跳跃、受2.5D高程图限制；仅用约80%扭矩；将增加高度指令通道 | 有 | 否 |
| 352 | TAR: Teacher-Aligned Representations Via Contrastive Learning for Quadrupedal Locomotion | IROS25 | Go2 | 特权教师到学生对齐 | 对比学习对齐表征 | 拓展到off-policy RL；真实世界持续微调；跨多种形态评估 | 有 | Go2 |
| 355 | Thruster-Enhanced Locomotion: A Decoupled Model Predictive Control with Learned Contact Residuals | IROS25 | Husky-β(推进器四足) | 推进器辅助窄道行走 | 腿Raibert+推进器MPC+接触残差 | 未读到 | 无/未查 | 否 |
| 356 | Transferable Latent-To-Latent Locomotion Policy for Efficient and Versatile Motion Control of Diverse Legged Robots | IROS25 | A1/Go1/Go2等仿真,Go1实机 | 跨机器人迁移 | 潜空间预训练策略+轻量编解码 | 精进恢复模块；扩展到多实体多任务场景 | 无/未查 | 否 |
| 357 | Unified Locomotion Transformer with Simultaneous Sim-To-Real Transfer for Quadrupeds | IROS25 | A1 | 师生蒸馏多阶段繁琐 | Transformer单阶段RL+模仿 | 新任务需重训；未来探索持续学习与跨任务/本体泛化 | 有 | 否 |
| 358 | UniLegs: Universal Multi-Legged Robot Control through Morphology-Agnostic Policy Distillation | IROS25 | Go2实机(仿真A1/Aliengo/ANYmal/六足/八足) | 跨构型通用控制 | 教师蒸馏到Transformer学生 | 未读到 | 无/未查 | Go2 |
| 365 | Real-DRL: Teach and Learn in Reality | NeurIPS25 | 四足(型号未写明)+cart-pole | 实机学习安全 | Student-Teacher-Trigger框架 | Trigger持续监控负担大；加入未来安全状态预警，可用可达性方法 | 有 | ? |
| 371 | Synthesizing Whole-Body Loco-Manipulation without Human Demonstration | NeurIPS26 | 未知 | 未读到 | 未读到 | 未读到 | 无/未查 | ? |
| 374 | Language Guided Skill Discovery | ICLR25 | Ant四足仿真+Franka臂 | 技能语义多样性 | LLM引导技能发现 | 部分语义视觉更易捕获；未来引入轨迹级语义差异 | 无/未查 | 否 |
| 383 | Learning to Reconfigure: Configuration-Control Co-optimization of Reconfigurable Robots for Heterogeneous Locomotion | ICML26 | 未知 | 未读到 | 未读到 | 未读到 | 无/未查 | ? |

## 2. 按局限类型聚类

一篇可属多类（每篇最多 3 个标签，由子代理按所读局限段判定，粗粒度，仅供统计）。

| 局限类型 | 篇数 | 论文编号 |
|---|---|---|
| 泛化差 | 56 | 6, 8, 9, 12, 14, 17, 18, 31, 33, 38, 40, 41, 44, 45, 50, 55, 57, 59, 63, 67, 69, 83, 90, 109, 110, 112, 116, 117, 118, 120, 148, 160, 167, 172, 185, 200, 202, 218, 219, 220, 231, 243, 246, 247, 257, 261, 264, 282, 294, 305, 330, 332, 346, 352, 356, 357 |
| 其他 | 49 | 6, 7, 8, 14, 31, 38, 40, 43, 44, 50, 51, 53, 57, 58, 116, 161, 168, 172, 182, 185, 196, 200, 218, 219, 220, 227, 229, 231, 238, 241, 242, 244, 249, 254, 259, 268, 273, 282, 298, 299, 305, 306, 319, 332, 338, 340, 343, 355, 365 |
| 感知依赖 | 44 | 9, 14, 17, 33, 39, 44, 46, 59, 60, 66, 109, 110, 128, 148, 161, 167, 168, 185, 194, 195, 207, 221, 223, 229, 235, 242, 243, 244, 247, 253, 261, 268, 280, 294, 303, 307, 333, 334, 335, 338, 340, 341, 347, 348 |
| 无轮或不涉轮足 | 43 | 33, 39, 54, 55, 56, 60, 63, 64, 66, 67, 69, 70, 80, 83, 109, 112, 116, 117, 118, 120, 128, 136, 148, 150, 151, 160, 187, 196, 207, 217, 219, 221, 223, 228, 283, 294, 298, 304, 306, 315, 316, 333, 335 |
| 单一技能 | 42 | 6, 8, 12, 18, 41, 46, 55, 60, 64, 66, 83, 90, 110, 120, 135, 136, 151, 161, 167, 180, 187, 194, 207, 221, 223, 238, 246, 257, 264, 280, 297, 301, 303, 304, 307, 315, 316, 319, 332, 341, 347, 348 |
| 未读到 | 42 | 72, 75, 85, 162, 163, 165, 171, 173, 178, 181, 183, 192, 197, 198, 199, 208, 212, 213, 214, 224, 232, 234, 266, 267, 275, 281, 284, 288, 300, 308, 320, 323, 325, 326, 327, 328, 329, 336, 355, 358, 371, 383 |
| 负载或操作受限 | 21 | 12, 18, 43, 46, 50, 54, 70, 80, 90, 135, 150, 182, 228, 229, 253, 297, 307, 316, 319, 334, 346 |
| 计算或训练成本 | 16 | 6, 7, 9, 17, 31, 45, 46, 51, 53, 63, 151, 180, 195, 254, 315, 333 |
| 需特权信息或额外传感 | 16 | 7, 39, 43, 54, 57, 64, 69, 150, 180, 253, 257, 268, 304, 307, 352, 357 |
| 安全或约束不足 | 14 | 14, 41, 45, 56, 80, 112, 128, 136, 160, 195, 241, 247, 249, 365 |
| 仅平地或仿真 | 14 | 51, 54, 56, 64, 67, 118, 163, 187, 202, 217, 257, 334, 343, 374 |
| 未做实机 | 9 | 40, 135, 202, 231, 254, 283, 301, 330, 374 |
| 依赖动捕或外部定位 | 4 | 45, 194, 235, 330 |
| 未考虑能耗 | 1 | 298 |

注："无轮或不涉轮足"类多数论文并未自述此局限，是子代理依据平台判定，使用时请核实。

## 3. 作者明确写出"未来工作"且可衔接轮足/Go2-W 的条目

子代理共标 Y 32 篇，此处按 Go2 平台、负载/操作类优先取 20 条；"可衔接"为粗判，需回原文确认。

| # | 标题 | 平台 | 作者自述（摘写） |
|---|---|---|---|
| 18 | SATA: Safe and Adaptive Torque-Based Locomotion Policies Inspired by Animal Learning | Go2 | 有载荷时姿态保持差、小腿触地;仅学会基础行走步态。未来扩展复杂地形与敏捷行为、混合肌肉式驱动 |
| 54 | LocoTouch: Learning Dynamic Quadrupedal Transport with Tactile Sensing | Go1 | 圆柱物沿躯干方向易失败；楼梯性能下降；未来加视觉触觉融合、扩展全身触觉 |
| 58 | Non-conflicting Energy Minimization in Reinforcement Learning based Robot Control | Go2(实机)+DMControl/H1仿真 | 能耗目标难与风格奖励结合，否则出现不可行行为；未来按优先级递归应用PEGrad |
| 80 | CMP: Robust Whole-Body Tracking for Loco-Manipulation via Competence Manifold Projection | Go2+Hexfellow Saber机械臂 | 45次实机3次失败；球形边界罕见边界失效；未来环境条件化应对动力学变化、逼近绝对安全保证 |
| 90 | FT-WBC: Learning Fault-Tolerant Whole-Body Control for Legged Loco-Manipulation | Go2+机械臂 | 仅单执行器故障，未处理多关节并发；评估限静止或顺序任务；行走中动态操作留作未来 |
| 167 | AINav: Large Language Model-Based Adaptive Interactive Navigation | Go2 | 简化视觉与预设可执行约束限泛化；拟用视觉基础模型、增技能、扩平台与长时程 |
| 168 | APREBot: Active Perception System for Reflexive Evasion Robot | Go2 | 未测运动中避障与密集障碍；拟扩展到更复杂场景 |
| 182 | Disturbance-Aware Adaptive Compensation in Hybrid Force-Position Locomotion Policy for Legged Robots | Go2 | 无理论保证；扰动仅限质心外力；拟研究更丰富扰动模型与理论分析 |
| 185 | DreamFlow: Local Navigation Beyond Observation Via Conditional Flow Matching in the Latent Space | Go2 | 拟研究预测视距、端到端合并训练、多潜在预测应对动态环境 |
| 195 | Flexible Locomotion Learning with Diffusion Model Predictive Control | Go2 | 仅简单约束类；拟加视觉/语言输入、无离线数据交互微调 |
| 200 | GRAM: Generalization in Deep RL with a Robust Adaptation Module | Go2 | 极端OOD场景可能失败；拟结合其他鲁棒RL，扩展到其他机器人与任务 |
| 218 | Learning Quadruped Walking from Seconds of Demonstration | Go2 | 未来分析正则化学习动力学，结合在线数据，测试更广平台与任务 |
| 223 | MARG: MAstering Risky Gap Terrains for Legged Robots with Elevation Mapping | Go1/Go2 | 依赖LiDAR点云精度；仅能trot步态；拟扩展软滑不稳地形 |
| 227 | MUJICA: Multi-Skill Unified Joint Integration of Control Architecture for Wheeled-Legged Robots | Go2-W | 拟扩展到更多运动技能，实现非结构化地形自适应协调 |
| 307 | Helpful DoggyBot: Open-World Object Fetching Using Legged Robots and Vision-Language Models | Go2 | 局限：夹爪灵巧性受限、依赖天花板相机导航、可能遮挡；未来：不损敏捷性增强操作，仅用机载传感器导航 |
| 335 | MoE-Loco: Leveraging Mixture of Experts for Multi-Task Locomotion | Go2 | 未来：引入相机与激光雷达感知增强复杂任务适应性 |
| 352 | TAR: Teacher-Aligned Representations Via Contrastive Learning for Quadrupedal Locomotion | Go2 | 拓展到off-policy RL；真实世界持续微调；跨多种形态评估 |
| 56 | Multi-critic Learning for Whole-body End-effector Twist Tracking | ANYmal D+Dynaarm机械臂 | 仅适中崎岖地形；肩关节偶触限位；未来加入崎岖地形奖励与感知、训练中纳入关节限位 |
| 12 | Human2LocoMan: Learning Versatile Quadrupedal Manipulation with Human Pretraining | LocoMan(足端操作器四足) | 遥操作有学习成本;仅验证LocoMan;多任务协同训练未探索。未来扩展到多种机器人与更大数据 |
| 187 | Efficient and Versatile Quadrupedal Skating: Optimal Co-Design Via Reinforcement Learning and Bayesian Optimization | Go1(被动轮) | 仅平地；拟扩展室外不平地形、轻耐用轮、更省样本；滑行与行走融合 |

## 附录：初选后移出主表的论文

| # | 标题 | 会议 | 原因 |
|---|---|---|---|
| 2 | Adaptive Locomotion on Mud through Proprioceptive Sensing of Substrate Properties | RSS25 | 非四足轮足 |
| 61 | Real-Time Out-of-Distribution Failure Prevention via Multi-Modal Reasoning | CoRL25 | 非四足轮足(主实验为无人机) |
| 97 | HLO-AMP: Hierarchical Loco-Manipulation from Object-Aware Motion Priors | CoRL26 | 非四足轮足 |
| 107 | Koopman DCM: Unstable Eigenfunctions as Data-driven Representations for Legged Balancing | CoRL26 | 非四足轮足 |
| 123 | Perceptive Behavior Foundation Model: Adapting Human Motion Priors to Robot-Centric Terrain | CoRL26 | 非四足轮足 |
| 140 | SPOT: Spatial Perception-Oriented Long-Horizon Humanoid Teleoperation | CoRL26 | 非四足轮足 |
| 204 | HMC: Learning Heterogeneous Meta-Control for Contact-Rich Loco-Manipulation | ICRA26 | 非四足轮足 |
| 245 | Reinforcement Learning for Stair Locomotion of a Wheeled Bipedal Robot with Contact-Guided Behavior Cloning | ICRA26 | 非四足轮足(标题显示轮式双足，未找到预印本) |
| 292 | BeeTLe: Blind Terrain-Aware Learned Locomotion | IROS25 | 非四足轮足 |
| 314 | Impact of Static Friction on Sim2Real in Robotic Reinforcement Learning | IROS25 | 非四足轮足 |
| 364 | Periodic Skill Discovery | NeurIPS25 | 非四足轮足 |
| 381 | WholeBodyVLA: Towards Unified Latent VLA for Whole-body Loco-manipulation Control | ICLR26 | 非四足轮足 |
