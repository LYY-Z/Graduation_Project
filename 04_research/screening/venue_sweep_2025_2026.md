# 2025–2026 顶会录用列表普查（足式 / 轮足 / 人形 × 学习）

日期：2026-11-25。方法：**下载每个来源的完整录用/程序列表 → 正则初筛 → 人工逐条读标题判定**，不使用关键词搜索引擎。原始列表与脚本保存在会话 scratchpad 中（`dl/`、`py/`），可复跑。期刊部分已另交子代理，**期刊结果以 `venue_sweep_journals.md` 为准**；本文 2.2 节仅保留已完成的期刊初筛，供交叉核对。

## 1. 覆盖记录

| 来源 | 访问方式（完整列表） | 列表条目数 | 初筛命中 | 人工判定相关 | 备注 |
|---|---|---|---|---|---|
| RSS 2025 (XXI) | roboticsproceedings.org/rss21/index.html + 每篇摘要页 | 163 | 32 | 18 | 标题和摘要都扫过；摘要初筛补回 3 篇（如 FDM、DDAT） |
| RSS 2026 (XXII) | roboticsproceedings.org/rss22/index.html + 摘要页 | 210 | 34 | 18 | 同上 |
| CoRL 2025 | PMLR v305 目录 + 每篇摘要页 | 263 | 45 | 35 | 摘要初筛补回 7 篇 |
| CoRL 2026（Austin） | corl.org/program/accepted-papers（官方录用页，含 OpenReview 链接） | 687 | ≈104 | 86 | **只有标题**：OpenReview API 需要人机验证，取不到摘要 |
| ICRA 2026 | ras.papercept.net ICRA26 程序（周二至周四 ContentList，含摘要和关键词） | 2898 | 235 | 125 | 程序中含转到会议报告的 RA-L 论文；初筛用了标题、官方关键词（Legged Robots、Humanoid and Bipedal Locomotion 等）和摘要 |
| IROS 2025 | ras.papercept.net IROS25 程序（3 天 ContentList，含摘要和关键词） | 2672 | 231 | 78 | 同上 |
| NeurIPS 2025 | neurips.cc/static/virtual/data/neurips-2025-orals-posters.json | 5858 | 26 | 5 | 标题和摘要都扫过；多数命中属于 gait recognition 等无关内容 |
| NeurIPS 2026 | 同上 2026 json | 9111 | 19 | 7 | 同上 |
| ICLR 2025 / 2026 | iclr.cc virtual json | 3830 / 5468 | 18 / 10 | 3 / 6 | 同上 |
| ICML 2025 / 2026 | icml.cc virtual json | 3339 / 6646 | 6 / 5 | 1 / 3 | 同上 |
| Science Robotics / IJRR / T-RO / RA-L 2025–26 | Crossref `/journals/{ISSN}/works?filter=from-pub-date:2025-01-01,until-pub-date:2026-12-31,type:journal-article`（ISSN 依次为 2470-9476、0278-3649、1552-3098、2377-3766），逐条取全部标题 | 237 / 240 / 646 / 3779 | 25 / 15 / 36 / 241 | 13 / 6 / 9 / 117（初筛） | **期刊结果见 venue_sweep_journals.md**；本文仅为初筛。RA-L 和 T-RO 在 Crossref 中没有摘要，OpenAlex 返回 429，因此只按标题判定 |

**合计**：会议去重后 **385 篇**相关；加上期刊初筛后共 499 篇（跨源重复已合并，如"ICRA26/RA-L"）。
**判定口径**：平台是足式、轮足或人形，且方法含学习（RL、模仿、学习模型、大模型、学习型估计）。以下三类不收：纯上肢或灵巧手操作、人体步态识别或外骨骼、纯机构设计。纯模型或优化控制的**轮足**论文不进主表，但列入 3.3 轮足清单。
**已知漏检风险**：(1) CoRL26 和 RA-L 只按标题判定，标题里没有平台词的论文可能漏掉；(2) 标签是规则自动标注（只用标题，标题信息不足时补用摘要），另对约 40 篇做了人工修正，单篇可能有偏差，但适合做数量统计；(3)"代码"一列只在摘要或摘要页出现 github 等代码链接时标"有"，其余一律标"未查"，并不代表没有代码；(4) 平台一列同样来自标题和摘要，"Go2"只在明确写出时才标。

## 2. 相关论文总表

平台缩写："足式"表示摘要或标题只写 legged；"滑板/轮滑"指四足或人形踩滑板、穿轮滑。代码一列："有"表示摘要或摘要页出现代码链接，"未查"表示没有逐篇核查。

### 2.1 会议（主表）

| # | 标题 | 出处 | 平台 | 标签 | 代码 |
|---|---|---|---|---|---|
| 1 | A Unified and General Humanoid Whole-Body Controller for Fine-Grained Locomotion | RSS25 | 人形 | 技能/模仿 | 未查 |
| 2 | Adaptive Locomotion on Mud through Proprioceptive Sensing of Substrate Properties | RSS25 | 足式 | 适应 | 未查 |
| 3 | AMO: Adaptive Motion Optimization for Hyper-Dexterous Humanoid Whole-Body Control | RSS25 | 人形 | 适应 | 未查 |
| 4 | ASAP: Aligning Simulation and Real-World Physics for Learning Agile Humanoid Whole-Body Skills | RSS25 | 人形 | 技能/模仿、敏捷动作 | 未查 |
| 5 | BeamDojo: Learning Agile Humanoid Locomotion on Sparse Footholds | RSS25 | 人形 | 感知运动、敏捷动作 | 未查 |
| 6 | Bridging the Sim-to-Real Gap for Athletic Loco-Manipulation | RSS25 | 足式 | sim2real/辨识、敏捷动作、移动操作 | 未查 |
| 7 | DDAT: Diffusion Policies Enforcing Dynamically Admissible Robot Trajectories | RSS25 | 四足/Go2 | 安全/约束 | 有 |
| 8 | Discrete-Time Hybrid Automata Learning: Legged Locomotion Meets Skateboarding | RSS25 | 滑板/轮滑/四足 | 敏捷动作 | 未查 |
| 9 | Gain Tuning Is Not What You Need: Reward Gain Adaptation for Constrained Locomotion Learning | RSS25 | 四足 | 适应、安全/约束、训练算法 | 未查 |
| 10 | Gait-Net-augmented Implicit Kino-dynamic MPC for Dynamic Variable-frequency Humanoid Locomotion over Discrete Terrains | RSS25 | 人形 | 学习+MPC | 未查 |
| 11 | HOMIE: Humanoid Loco-Manipulation with Isomorphic Exoskeleton Cockpit | RSS25 | 人形 | 移动操作 | 未查 |
| 12 | Human2LocoMan: Learning Versatile Quadrupedal Manipulation with Human Pretraining | RSS25 | 四足 | 移动操作、训练算法 | 有 |
| 13 | LangWBC: Language-directed Humanoid Whole-Body Control via End-to-end Learning | RSS25 | 人形 | VLA/大模型、学习+MPC | 有 |
| 14 | Learned Perceptive Forward Dynamics Model for Safe and Platform-aware Robotic Navigation | RSS25 | 四足 | 感知运动、导航/VLN、安全/约束、世界模型/基于模型 | 有 |
| 15 | Learning Getting-Up Policies for Real-World Humanoid Robots | RSS25 | 人形 | 跌倒/起身 | 有 |
| 16 | Learning Humanoid Standing-up Control across Diverse Postures | RSS25 | 人形 | 跌倒/起身 | 有 |
| 17 | NaVILA: Legged Robot Vision-Language-Action Model for Navigation | RSS25 | 足式 | 感知运动、导航/VLN、VLA/大模型 | 未查 |
| 18 | SATA: Safe and Adaptive Torque-Based Locomotion Policies Inspired by Animal Learning | RSS25 | 足式 | 适应、安全/约束 | 未查 |
| 19 | CoCo-InEKF: State Estimation with Learned Contact Covariances in Dynamic, Contact-Rich Scenarios | RSS26 | 双足 | 状态估计 | 未查 |
| 20 | FlashSAC: Fast and Stable Off-Policy Reinforcement Learning for High-Dimensional Robot Control | RSS26 | 人形 | 训练算法、sim2real/辨识 | 未查 |
| 21 | Generalizing from References using a Multi-Task Reference and Goal-Driven RL Framework | RSS26 | 人形 | 感知运动 | 未查 |
| 22 | HAIC: Humanoid Agile Object Interaction Control via Dynamics-Aware World Model | RSS26 | 人形 | 敏捷动作、移动操作、世界模型/基于模型 | 未查 |
| 23 | HiWET: Hierarchical World-Frame End-Effector Tracking for Long-Horizon Humanoid Loco-Manipulation | RSS26 | 人形 | 移动操作 | 未查 |
| 24 | HUSKY: Humanoid Skateboarding System via Physics-Aware Whole-Body Control | RSS26 | 滑板/轮滑/人形 | 敏捷动作 | 未查 |
| 25 | Learning to Evolve: Multi-modal Interactive Fields for Robust Humanoid Navigation in Dynamic Environments | RSS26 | 人形 | 导航/VLN、能效/热 | 未查 |
| 26 | Mind Your Steps: A General Learning Framework for Accurate Humanoid Foothold Tracking | RSS26 | 人形 | 感知运动、导航/VLN | 未查 |
| 27 | Now You See That: Learning End-to-End Humanoid Locomotion from Raw Pixels | RSS26 | 人形 | 感知运动、sim2real/辨识、能效/热 | 未查 |
| 28 | OmniXtreme: Breaking the Generality Barrier in High-Dynamic Humanoid Control | RSS26 | 人形 | 敏捷动作、安全/约束 | 未查 |
| 29 | Perceptive Humanoid Parkour: Chaining Dynamic Human Skills via Motion Matching | RSS26 | 人形 | 感知运动、技能/模仿、敏捷动作 | 未查 |
| 30 | Rhythm: Learning Interactive Whole-Body Control for Dual Humanoids | RSS26 | 人形 | 学习+MPC、人机交互 | 未查 |
| 31 | Simulation Distillation: Pretraining World Models in Simulation for Rapid Real-World Adaptation | RSS26 | 四足 | 适应、世界模型/基于模型、训练算法 | 未查 |
| 32 | TeleGate: Whole-Body Humanoid Teleoperation via Gated Expert Selection with Motion Prior | RSS26 | 人形 | 技能/模仿 | 未查 |
| 33 | Toward Reliable Sim-to-Real Predictability for MoE-based Robust Quadrupedal Locomotion | RSS26 | 四足/Go2 | sim2real/辨识、训练算法 | 未查 |
| 34 | Unlocking In-the-Wild Loco-Manipulation with Robot-Free Egocentric Demonstration | RSS26 | 人形 | 感知运动、技能/模仿、移动操作 | 未查 |
| 35 | X-Loco: Towards Generalist Humanoid Locomotion Control via Synergetic Policy Distillation | RSS26 | 人形 | 训练算法、跨形态 | 未查 |
| 36 | Ψ₀: An Open Foundation Model Towards Universal Humanoid Loco-Manipulation | RSS26 | 人形 | VLA/大模型、移动操作、跨形态 | 未查 |
| 37 | CLONE: Closed-Loop Whole-Body Humanoid Teleoperation for Long-Horizon Tasks | CoRL25 | 人形 | 技能/模仿 | 有 |
| 38 | Constrained Style Learning from Imperfect Demonstrations under Task Optimality | CoRL25 | 四足 | 技能/模仿、安全/约束 | 有 |
| 39 | Contrastive Forward Prediction Reinforcement Learning for Adaptive Fault-Tolerant Legged Robots | CoRL25 | 四足/多足 | 适应、容错 | 有 |
| 40 | Disentangled Multi-Context Meta-Learning: Unlocking Robust and Generalized Task Learning | CoRL25 | 四足 | 适应 | 有 |
| 41 | Divide, Discover, Deploy: Factorized Skill Learning with Symmetry and Style Priors | CoRL25 | 四足 | 技能/模仿、训练算法 | 有 |
| 42 | Embrace Contacts: humanoid shadowing with full body ground contacts | CoRL25 | 人形 | 技能/模仿 | 有 |
| 43 | FACET: Force-Adaptive Control via Impedance Reference Tracking for Legged Robots | CoRL25 | 人形/四足 | 适应、技能/模仿 | 有 |
| 44 | First Order Model-Based RL through Decoupled Backpropagation | CoRL25 | 双足/四足/Go2 | 世界模型/基于模型 | 有 |
| 45 | From Tabula Rasa to Emergent Abilities: Discovering Robot Skills via Real-World Unsupervised Quality-Diversity | CoRL25 | 四足 | 技能/模仿、容错 | 有 |
| 46 | Granular loco-manipulation: Repositioning rocks through strategic sand avalanche | CoRL25 | 多足 | 移动操作 | 有 |
| 47 | Hand-Eye Autonomous Delivery: Learning Humanoid Navigation, Locomotion and Reaching | CoRL25 | 人形 | 导航/VLN、感知运动 | 有 |
| 48 | Hold My Beer: Learning Gentle Humanoid Locomotion and End-Effector Stabilization Control | CoRL25 | 人形 | 移动操作 | 有 |
| 49 | HuB: Learning Extreme Humanoid Balance | CoRL25 | 人形 | 敏捷动作、sim2real/辨识 | 有 |
| 50 | Learning a Unified Policy for Position and Force Control in Legged Loco-Manipulation | CoRL25 | 人形/四足 | 移动操作 | 有 |
| 51 | Learning Deployable Locomotion Control via Differentiable Simulation | CoRL25 | 四足 | 世界模型/基于模型 | 有 |
| 52 | Learning Impact-Rich Rotational Maneuvers via Centroidal Velocity Rewards and Sim-to-Real Techniques: A One-Leg Hopper Flip Case Study | CoRL25 | 足式 | sim2real/辨识、敏捷动作、训练算法 | 有 |
| 53 | LocoFormer: Generalist Locomotion via Long-context Adaptation | CoRL25 | 足式 | 适应、跨形态 | 有 |
| 54 | LocoTouch: Learning Dynamic Quadrupedal Transport with Tactile Sensing | CoRL25 | 四足 | 移动操作 | 有 |
| 55 | Motion Priors Reimagined: Adapting Flat-Terrain Skills for Complex Quadruped Mobility | CoRL25 | 四足 | 适应、技能/模仿 | 有 |
| 56 | Multi-critic Learning for Whole-body End-effector Twist Tracking | CoRL25 | 四足 | 移动操作 | 有 |
| 57 | Multi-Loco: Unifying Multi-Embodiment Legged Locomotion via Reinforcement Learning Augmented Diffusion | CoRL25 | 轮足/双足 | 跨形态、学习+MPC | 有 |
| 58 | Non-conflicting Energy Minimization in Reinforcement Learning based Robot Control | CoRL25 | 人形/四足/Go2 | 能效/热 | 有 |
| 59 | Omni-Perception: Omnidirectional Collision Avoidance of Legged Robots in Dynamic Environments | CoRL25 | 足式 | 感知运动、导航/VLN、技能/模仿 | 有 |
| 60 | QuaDreamer: Controllable Panoramic Video Generation for Quadruped Robots | CoRL25 | 四足 | 世界模型/基于模型、感知运动 | 有 |
| 61 | Real-Time Out-of-Distribution Failure Prevention via Multi-Modal Reasoning | CoRL25 | 四足 | 安全/约束、容错 | 有 |
| 62 | Robot Trains Robot: Automatic Real-World Policy Adaptation and Learning for Humanoids | CoRL25 | 人形 | 适应、sim2real/辨识 | 有 |
| 63 | Sampling-based System Identification with Active Exploration for Legged Sim2Real Learning | CoRL25 | 足式 | sim2real/辨识、训练算法 | 有 |
| 64 | SDS – See it, Do it, Sorted: Quadruped Skill Synthesis from Single Video Demonstration | CoRL25 | 四足 | 技能/模仿 | 有 |
| 65 | ToddlerBot: Open-Source ML-Compatible Humanoid Platform for Loco-Manipulation | CoRL25 | 人形 | 移动操作、sim2real/辨识 | 有 |
| 66 | Toward Real-World Cooperative and Competitive Soccer with Quadrupedal Robot Teams | CoRL25 | 四足 | 敏捷动作 | 有 |
| 67 | Towards Embodiment Scaling Laws in Robot Locomotion | CoRL25 | 人形/四足/多足 | 训练算法、跨形态 | 有 |
| 68 | TWIST: Teleoperated Whole-Body Imitation System | CoRL25 | 人形 | 技能/模仿 | 有 |
| 69 | Unsupervised Skill Discovery as Exploration for Learning Agile Locomotion | CoRL25 | 四足 | 技能/模仿、敏捷动作、训练算法 | 有 |
| 70 | Versatile Loco-Manipulation through Flexible Interlimb Coordination | CoRL25 | 足式 | 移动操作 | 有 |
| 71 | Visual Imitation Enables Contextual Humanoid Control | CoRL25 | 人形 | 感知运动、技能/模仿 | 有 |
| 72 | Actuator Dynamics Curricula for Narrow-Viability Tasks in Legged Robot Learning | CoRL26 | 足式 | sim2real/辨识、安全/约束、训练算法 | 未查 |
| 73 | ADAPT: Agile Diffusion Action Priors for Robust and Steerable Online Text-Driven Humanoid Control | CoRL26 | 人形 | 适应、VLA/大模型、敏捷动作 | 未查 |
| 74 | ADAPT: Analytical Disturbance-Aware Policy Training for Humanoid Locomotion | CoRL26 | 人形 | 适应 | 未查 |
| 75 | CA-GMT: Contact-Aware Low-Rank Adaptation of Motion Tracking for Whole-Body Teleoperation | CoRL26 | 足式 | 适应、技能/模仿 | 未查 |
| 76 | CAP: Continuously Adaptive Perception-Blind Humanoid Locomotion via Learned Denoising | CoRL26 | 人形 | 适应、感知运动 | 未查 |
| 77 | CHIP: Adaptive Compliance for Humanoid Control through Hindsight Perturbation | CoRL26 | 人形 | 适应 | 未查 |
| 78 | CLIFT: Turning Gemini Robotics On-Device into Humanoid Specialists via Non-Invasive Closed-Loop Iterative Fine-Tuning | CoRL26 | 人形 | 适应 | 未查 |
| 79 | Closing the Loop in Humanoid VLA: Persistent 3D Object Tokens for Verifiable Loco-Manipulation | CoRL26 | 人形 | VLA/大模型、移动操作 | 未查 |
| 80 | CMP: Robust Whole-Body Tracking for Loco-Manipulation via Competence Manifold Projection | CoRL26 | 足式 | 移动操作 | 未查 |
| 81 | Constrained Whole-Body Tracking for Humanoid Robots | CoRL26 | 人形 | 安全/约束 | 未查 |
| 82 | ContactMimic: Humanoid Object Interaction via Contact Control | CoRL26 | 人形 | 技能/模仿、移动操作 | 未查 |
| 83 | Continual Quadruped Robots Coordination via Sementic Skill Discover | CoRL26 | 四足 | 适应、技能/模仿 | 未查 |
| 84 | Counterfactual Video Generation Enables Scalable Humanoid Loco-Manipulation | CoRL26 | 人形 | 移动操作 | 未查 |
| 85 | Damage-Aware Quadruped Locomotion: Zero-Shot Adaptation to Motor Failures via Pain-Inspired Reinforcement Learning | CoRL26 | 四足 | 适应、容错 | 未查 |
| 86 | Echo in the Steps: Learning Perceptive Humanoid Parkour with Gated Memory | CoRL26 | 人形 | 感知运动、敏捷动作 | 未查 |
| 87 | EVOLVE: Egocentric Vision-based Humanoid Loco-Manipulation via Demonstration Editing | CoRL26 | 人形 | 感知运动、技能/模仿、移动操作 | 未查 |
| 88 | ExtremControl: Low-Latency Humanoid Teleoperation with Scaled Velocity Feedforward | CoRL26 | 人形 | 技能/模仿 | 未查 |
| 89 | FADA: Few-Shot Domain Adaptation via Dynamics Alignment for Humanoid Control | CoRL26 | 人形 | 适应 | 未查 |
| 90 | FT-WBC: Learning Fault-Tolerant Whole-Body Control for Legged Loco-Manipulation | CoRL26 | 足式 | 移动操作、学习+MPC、容错 | 未查 |
| 91 | General Humanoid Whole-Body Control via Pretraining and Fast Adaptation | CoRL26 | 人形 | 适应、训练算法 | 未查 |
| 92 | GRAIL: Generating Humanoid Loco-Manipulation from World Models | CoRL26 | 人形 | 移动操作、世界模型/基于模型 | 未查 |
| 93 | HAF-VLA: Hierarchical Action Flow Framework for Humanoid Vision-Language-Action Control | CoRL26 | 人形 | 感知运动、VLA/大模型 | 未查 |
| 94 | HEFT: Heavy Load Full-size Humanoid Teleoperation with Privileged Motion Guidance and Windowed Payload Curriculum | CoRL26 | 人形 | 技能/模仿、移动操作、训练算法 | 未查 |
| 95 | HERO: Learning Humanoid End-Effector Control for Visual Whole-Body Open-Vocabulary Object Grasping | CoRL26 | 人形 | 感知运动、移动操作 | 未查 |
| 96 | Hiking in the Wild: A Scalable Perceptive Legged Parkour Framework for Humanoid Robots | CoRL26 | 人形 | 感知运动、敏捷动作 | 未查 |
| 97 | HLO-AMP: Hierarchical Loco-Manipulation from Object-Aware Motion Priors | CoRL26 | 足式 | 技能/模仿、移动操作 | 未查 |
| 98 | HuG: Learning Humanoid Whole-Body Affordance-Aware Grasping with Active Perception | CoRL26 | 人形 | 感知运动、技能/模仿、移动操作 | 未查 |
| 99 | Humanoid Badminton: Learning Dynamic Racket Skills from Limited Human Motion Data | CoRL26 | 人形 | 技能/模仿、敏捷动作 | 未查 |
| 100 | Humanoid Hanoi: Investigating Shared Whole-Body Control for Skill-Based Box Rearrangement | CoRL26 | 人形 | 技能/模仿 | 未查 |
| 101 | Humanoid Navigation in Cluttered Environments with a Whole-Body Vision-Language-Action Model | CoRL26 | 人形 | 感知运动、导航/VLN、VLA/大模型 | 未查 |
| 102 | HumanoidMimicGen Data Generation for Loco-Manipulation via Whole-Body Planning | CoRL26 | 人形 | 技能/模仿、移动操作 | 未查 |
| 103 | HumanoidNDM: Closing the Training-Deployment Gap of Motion Tracking via Humanoid Neural Dynamics Model | CoRL26 | 人形 | sim2real/辨识、技能/模仿、世界模型/基于模型 | 未查 |
| 104 | HumanX: Toward Agile and Generalizable Humanoid Interaction Skills from Human Videos | CoRL26 | 人形 | 技能/模仿、敏捷动作、移动操作 | 未查 |
| 105 | HuMI: Humanoid Whole-Body Manipulation from Humanoid-Free Demonstrations | CoRL26 | 人形 | 技能/模仿、移动操作 | 未查 |
| 106 | InfiniDanceRobot: A Streaming and Closed-Loop Music-driven Dance Generation for Humanoid Robot | CoRL26 | 人形 | 技能/模仿 | 未查 |
| 107 | Koopman DCM: Unstable Eigenfunctions as Data-driven Representations for Legged Balancing | CoRL26 | 足式 | 世界模型/基于模型 | 未查 |
| 108 | LadderMan: Learning Humanoid Perceptive Ladder Climbing | CoRL26 | 人形 | 感知运动 | 未查 |
| 109 | Learning Contact Representation for Leg Odometry | CoRL26 | 足式 | 状态估计 | 未查 |
| 110 | Learning Loco-Manipulation From SMPC Demonstrations With Sparse Offline-to-Online RL | CoRL26 | 足式 | 技能/模仿、移动操作 | 未查 |
| 111 | LEGS: Fine-Tuning Teleop-Free VLAs for Humanoid Loco-manipulation in an Embodied Gaussian Splatting World | CoRL26 | 人形 | 适应、VLA/大模型、技能/模仿、移动操作 | 未查 |
| 112 | LoComposition: Terrain-Adaptive Energy-Efficient Quadruped Locomotion without Gait Priors | CoRL26 | 四足 | 适应、能效/热 | 未查 |
| 113 | MAPO: Mixture of Experts with Alternating Policy Optimization for Universal Humanoid Motion Tracking | CoRL26 | 人形 | 技能/模仿、训练算法、跨形态 | 未查 |
| 114 | MARCH: Model-Assisted Reinforcement Learning for the Perceptive Control of Humanoids over Sparse Footholds | CoRL26 | 人形 | 感知运动、世界模型/基于模型 | 未查 |
| 115 | MeshMimic: Geometry-Aware Humanoid Motion Learning through 3D Scene Reconstruction | CoRL26 | 人形 | 技能/模仿 | 未查 |
| 116 | Mind the Phase: Effective Rank and Representation Health in Legged Locomotion | CoRL26 | 足式 | 训练算法 | 未查 |
| 117 | MorFiC: Fixing Value Miscalibration for Zero-Shot Quadruped Transfer | CoRL26 | 四足 | sim2real/辨识 | 未查 |
| 118 | Morphology-Conditioned World Model for Cross-Embodiment Quadrupedal Locomotion | CoRL26 | 四足 | 世界模型/基于模型、跨形态 | 未查 |
| 119 | MotionDisco: Motion Discovery for Extreme Humanoid Loco-manipulation | CoRL26 | 人形 | 敏捷动作、移动操作 | 未查 |
| 120 | MPC-Injection: Biasing Off-Policy Locomotion RL Toward Controller-Induced Behavior Basins | CoRL26 | 足式 | 学习+MPC、训练算法 | 未查 |
| 121 | OmniContact: Chaining Meta-Skills via Contact Flow for Generalizable Humanoid Loco-Manipulation | CoRL26 | 人形 | 技能/模仿、移动操作 | 未查 |
| 122 | OpenHLM: An Empirical Recipe for Whole-Body Humanoid Loco-Manipulation | CoRL26 | 人形 | 移动操作 | 未查 |
| 123 | Perceptive Behavior Foundation Model: Adapting Human Motion Priors to Robot-Centric Terrain | CoRL26 | 足式 | 适应、感知运动、VLA/大模型、技能/模仿 | 未查 |
| 124 | PHUMA: Physically Reliable Humanoid Locomotion Dataset | CoRL26 | 人形 | 技能/模仿 | 未查 |
| 125 | Physics-Guided Biomechanical Gait Adaptation for Humanoid Locomotion on Extreme Sloped Terrains | CoRL26 | 人形 | 适应、敏捷动作 | 未查 |
| 126 | Playing Soccer Like Humans Do: Learning Versatile and Agile Humanoid Soccer via Latent Motion Priors | CoRL26 | 人形 | 技能/模仿、敏捷动作 | 未查 |
| 127 | Pro-HOI: Perceptive Root-guided Humanoid-Object Interaction | CoRL26 | 人形 | 感知运动、移动操作 | 未查 |
| 128 | PROOF: Perceptive Robustness via Out-of-Distribution Fallback for Legged Locomotion | CoRL26 | 足式 | 感知运动、跌倒/起身 | 未查 |
| 129 | Push the Limit: Learning High-Speed Sprinting and Aggressive Cornering on a Full-Scale Humanoid | CoRL26 | 人形 | 敏捷动作 | 未查 |
| 130 | Reactive Closed-Loop Motion Planning Towards Universal Humanoid Whole-Body Control | CoRL26 | 人形 | 跨形态 | 未查 |
| 131 | ResSafe: Learning Safety Filtering with Residual Reinforcement Learning for Humanoids | CoRL26 | 人形 | 安全/约束、学习+MPC | 未查 |
| 132 | RoboDreamer: Anticipatory Humanoid Locomotion with Predictive State-Space Models | CoRL26 | 人形 | 世界模型/基于模型 | 未查 |
| 133 | RoboNaldo: Accurate, Stable and Powerful Humanoid Soccer Shooting via Motion-Guided Curriculum Reinforcement Learning | CoRL26 | 人形 | 敏捷动作、能效/热、训练算法 | 未查 |
| 134 | RPL: Learning Robust Humanoid Perceptive Locomotion on Challenging Terrains | CoRL26 | 人形 | 感知运动 | 未查 |
| 135 | S2M-Trek: From Single to Multi-Sphere Transport via Per-Frame Deep Sets on a Wheel-Legged Robot | CoRL26 | 轮足 | 移动操作 | 未查 |
| 136 | SHOES: Sim-to-real Hardware-adaptation via On-policy Expansion of Skills for Legged Robots | CoRL26 | 足式 | sim2real/辨识、适应、技能/模仿 | 未查 |
| 137 | SIMPLE: Simulation-Based Policy Learning and Evaluation for Humanoid Loco-manipulation | CoRL26 | 人形 | 移动操作 | 未查 |
| 138 | SkillX: Unified Multi-Skill Policy Learning for Humanoid Soccer | CoRL26 | 人形 | 技能/模仿、敏捷动作 | 未查 |
| 139 | SOLO: Stable Omni-terrain Long-Horizon Perceptive Humanoid Locomotion | CoRL26 | 人形 | 感知运动 | 未查 |
| 140 | SPOT: Spatial Perception-Oriented Long-Horizon Humanoid Teleoperation | CoRL26 | 人形/四足 | 感知运动、技能/模仿 | 未查 |
| 141 | SSR: Scaling Surefooted and Symmetric Humanoid Traversal Toward the Open World | CoRL26 | 人形 | 导航/VLN、训练算法 | 未查 |
| 142 | SuperMimic: Scaling Humanoid Whole-Body Control with One Differentiable World Model | CoRL26 | 人形 | 技能/模仿、世界模型/基于模型、训练算法 | 未查 |
| 143 | SwingBot: Learning Whole-Body Brachiation for Humanoid Robots | CoRL26 | 人形 | 敏捷动作 | 未查 |
| 144 | TactileStep: Sole Tactile Learning for Regulating Foot--Terrain Interaction in Humanoid Locomotion | CoRL26 | 人形 | 移动操作 | 未查 |
| 145 | TEXEDO : Test Time Scaling for Controller-aware Language-conditioned Humanoid Motion Generation | CoRL26 | 人形 | VLA/大模型、技能/模仿、训练算法 | 未查 |
| 146 | TextOp: Real-time Interactive Text-Driven Humanoid Robot Motion Generation and Control | CoRL26 | 人形 | VLA/大模型、技能/模仿 | 未查 |
| 147 | Towards Professional Tennis Styles for Humanoid Robots with Adaptive Motion Planning and Tracking | CoRL26 | 人形 | 适应、技能/模仿、敏捷动作 | 未查 |
| 148 | Trajectory-Level Automatic Curriculum Learning for Legged Locomotion on Unstructured Terrain | CoRL26 | 足式 | 训练算法 | 未查 |
| 149 | TTT-Parkour: Rapid Test-Time Training for Perceptive Legged Humanoid Parkour | CoRL26 | 人形 | 适应、感知运动、敏捷动作 | 未查 |
| 150 | Unified Whole-Body Control for Quadrupedal Tactile-Informed Loco-Manipulation | CoRL26 | 四足 | 移动操作 | 未查 |
| 151 | Unleashing Infinite Motion: Scaling Expressive Quadrupedal Motion via Generative Video Priors | CoRL26 | 四足 | 技能/模仿、训练算法 | 未查 |
| 152 | Unsupervised Actuator Networks as a Residual World Model for Humanoid Control | CoRL26 | 人形 | sim2real/辨识、世界模型/基于模型、学习+MPC | 未查 |
| 153 | VLK: Learning Humanoid Loco-Manipulation from Synthetic Interactions in Reconstructed Scenes | CoRL26 | 人形 | 移动操作 | 未查 |
| 154 | VLM-Guided Contact Retargeting and Generative Partner Modeling for Humanoid-Human Interaction | CoRL26 | 人形 | VLA/大模型、技能/模仿、移动操作、人机交互 | 未查 |
| 155 | X-WBC: A Cross-Embodiment Foundation Model for Humanoid Whole-Body Control | CoRL26 | 人形 | VLA/大模型、跨形态 | 未查 |
| 156 | ZeroWBC: Learning Natural Whole-Body Humanoid Interaction from Human Egocentric Data | CoRL26 | 人形 | 感知运动、移动操作 | 未查 |
| 157 | λ-Reachability: Geometric-Horizon Safety Bellman Equations for Humanoid Safety | CoRL26 | 人形 | 安全/约束 | 未查 |
| 158 | A Lightweight Physics-Informed Neural Network for Sim-To-Real of Biped Robot | ICRA26/RA-L | 双足 | sim2real/辨识 | 未查 |
| 159 | A MATLAB/Simulink-Based Sim2Real Control Framework for the Unitree G1 Using ROS 2 and MuJoCo | ICRA26 | 人形 | sim2real/辨识、感知运动 | 未查 |
| 160 | A Modular Residual Learning Framework to Enhance Model-Based Approach for Robust Locomotion | ICRA26/RA-L | 四足 | 世界模型/基于模型、学习+MPC | 未查 |
| 161 | Action-Informed Estimation and Planning: Clearing Clutter on Staircases Via Quadrupedal Pedipulation | ICRA26 | 四足 | 感知运动、移动操作 | 未查 |
| 162 | Active Dynamic Load Adaptation for Quadruped Locomotion on Complex Terrain | ICRA26 | 四足 | 适应 | 未查 |
| 163 | Adaptive Legged Locomotion Via Online Learning for Model Predictive Control | ICRA26/RA-L | 四足 | 适应、学习+MPC | 未查 |
| 164 | Adaptive Motion Priors with Constrained Optimization | ICRA26 | 人形 | 适应、技能/模仿、安全/约束 | 未查 |
| 165 | Agile Hauler Curriculum: Learning High-Speed Locomotion for Robots under Demanding Payloads | ICRA26 | 足式 | 敏捷动作、移动操作、训练算法 | 未查 |
| 166 | Agility Meets Stability: Versatile Humanoid Control with Heterogeneous Data | ICRA26 | 人形 | 技能/模仿 | 未查 |
| 167 | AINav: Large Language Model-Based Adaptive Interactive Navigation | ICRA26 | 足式 | 适应、导航/VLN、VLA/大模型、世界模型/基于模型 | 未查 |
| 168 | APREBot: Active Perception System for Reflexive Evasion Robot | ICRA26 | 四足 | 感知运动、导航/VLN | 有 |
| 169 | AURA: Autonomous Upskilling with Retrieval-Augmented Agents | ICRA26 | 人形 | 技能/模仿、VLA/大模型 | 未查 |
| 170 | Behavior Foundation Model for Humanoid Robots | ICRA26 | 人形 | VLA/大模型 | 未查 |
| 171 | CAIMAN: Causal Action Influence Detection for Sample-Efficient Loco-Manipulation | ICRA26 | 足式 | 移动操作、训练算法 | 未查 |
| 172 | Can a Robot Walk the Robotic Dog: Triple-Zero Collaborative Navigation for Heterogeneous Multi-Agent Systems | ICRA26 | 人形/四足/Go2 | 导航/VLN、人机交互 | 有 |
| 173 | Causal Transformer-Based Online Action Recognition for High-Level Control of a Unitree Go1 Robot | ICRA26 | 四足 | 人机交互 | 未查 |
| 174 | CBF-RL: Safety Filtering Reinforcement Learning in Training with Control Barrier Functions | ICRA26 | 人形 | 安全/约束 | 未查 |
| 175 | CLF-RL: Control Lyapunov Function Guided Reinforcement Learning | ICRA26 | 双足 | 学习+MPC、世界模型/基于模型 | 未查 |
| 176 | CMoE: Contrastive Mixture of Experts for Motion Control and Terrain Adaptation of Humanoid Robots | ICRA26 | 人形 | 适应、训练算法 | 有 |
| 177 | COLA: Learning Human-Humanoid Coordination for Collaborative Object Carrying | ICRA26 | 人形 | 移动操作、人机交互 | 未查 |
| 178 | Collaborative Quadruped Transportation in 3D Terrain with Constrained Diffusion | ICRA26 | 四足 | 移动操作、安全/约束、人机交互 | 未查 |
| 179 | Control of Humanoid Robots with Parallel Mechanisms Using Differential Actuation Models | ICRA26 | 人形 | 学习+MPC | 未查 |
| 180 | DAPPER: Discriminability-Aware Policy-To-Policy Preference-Based Reinforcement Learning for Query-Efficient Robot Skill Acquisition | ICRA26 | 足式 | 技能/模仿、训练算法 | 未查 |
| 181 | DeepSkate: Reinforcement Learning of a Robust Controller for Energy Efficient Quadruped Skating | ICRA26 | 轮足/四足 | 敏捷动作、能效/热 | 未查 |
| 182 | Disturbance-Aware Adaptive Compensation in Hybrid Force-Position Locomotion Policy for Legged Robots | ICRA26 | 足式 | 适应 | 未查 |
| 183 | Diverse Skill Discovery in Fourier Latent Space Via Unsupervised Learning | ICRA26 | 四足 | 技能/模仿、训练算法 | 未查 |
| 184 | DreamControl: Human-Inspired Whole-Body Humanoid Control for Scene Interaction Via Guided Diffusion | ICRA26 | 人形 | 移动操作 | 有 |
| 185 | DreamFlow: Local Navigation Beyond Observation Via Conditional Flow Matching in the Latent Space | ICRA26 | 四足 | 导航/VLN、容错 | 有 |
| 186 | Dribble Master: Learning Agile Humanoid Dribbling through Legged Locomotion | ICRA26 | 人形 | 敏捷动作、感知运动 | 有 |
| 187 | Efficient and Versatile Quadrupedal Skating: Optimal Co-Design Via Reinforcement Learning and Bayesian Optimization | ICRA26 | 滑板/轮滑/四足 | 敏捷动作、能效/热 | 未查 |
| 188 | Efficiently Learning Robust Torque-Based Locomotion through Reinforcement with Model-Based Supervision | ICRA26/RA-L | 双足 | 感知运动、世界模型/基于模型、学习+MPC | 未查 |
| 189 | Ego-Vision World Model for Humanoid Contact Planning | ICRA26 | 人形 | 感知运动、世界模型/基于模型 | 未查 |
| 190 | Embodiment‑Aware Generalist Specialist Distillation for Unified Humanoid Whole-Body Control | ICRA26 | 人形 | 训练算法、跨形态 | 未查 |
| 191 | Embracing Bulky Objects with Humanoid Robots: Whole-Body Manipulation with Reinforcement Learning | ICRA26 | 人形 | 移动操作 | 有 |
| 192 | Enhancing Robustness of Locomotion Policy for Quadrupedal Robot with Deep Disturbance Observer | ICRA26/RA-L | 四足 | 状态估计 | 未查 |
| 193 | ExBody2: Advanced Expressive Humanoid Whole-Body Control | ICRA26 | 人形 | 技能/模仿 | 未查 |
| 194 | Feasibility-Guided Planning Over Multi-Specialized Locomotion Policies | ICRA26 | 足式 | 导航/VLN | 未查 |
| 195 | Flexible Locomotion Learning with Diffusion Model Predictive Control | ICRA26 | 足式 | 学习+MPC | 未查 |
| 196 | Floating-Base Deep Lagrangian Networks | ICRA26 | 人形/四足 | 世界模型/基于模型 | 未查 |
| 197 | FT-CPG: Learning Central Pattern Generators for Fault-Tolerant Quadruped Locomotion under Multi-Joint Failures | ICRA26/RA-L | 四足 | 容错、能效/热 | 未查 |
| 198 | Full-Scale Autonomous Highway Inspection with Quadruped Robot: Multi-Level Locomotion Learning in Complex Environments | ICRA26 | 四足 | 感知运动 | 未查 |
| 199 | GIMloco: Generic Internal Model-Based Locomotion for Quadruped Robots | ICRA26 | 四足 | 世界模型/基于模型 | 未查 |
| 200 | GRAM: Generalization in Deep RL with a Robust Adaptation Module | ICRA26 | 四足 | 适应 | 未查 |
| 201 | H-Zero: Cross-Humanoid Locomotion Pretraining Enables Few-Shot Novel Embodiment Transfer | ICRA26 | 人形/四足 | 训练算法、跨形态 | 未查 |
| 202 | Hebbian Attractor Networks for Robot Locomotion | ICRA26 | 四足 | 其他 | 未查 |
| 203 | HITTER: A HumanoId Table TEnnis Robot Via Hierarchical Planning and Learning | ICRA26 | 人形 | 敏捷动作 | 未查 |
| 204 | HMC: Learning Heterogeneous Meta-Control for Contact-Rich Loco-Manipulation | ICRA26 | 足式 | 移动操作 | 未查 |
| 205 | HumanoidExo: Scalable Whole-Body Humanoid Manipulation Via Wearable Exoskeleton | ICRA26 | 人形 | 移动操作 | 未查 |
| 206 | Iterative Learning-Based Centre-Of-Mass Impedance Control for Articulated-Soft Humanoid Robots | ICRA26 | 人形 | 技能/模仿 | 未查 |
| 207 | KiRAS: Keyframe Guided Self-Imitation for Robust and Adaptive Skill Learning in Quadruped Robots | ICRA26 | 四足 | 适应、技能/模仿 | 未查 |
| 208 | Knowledge-Based Locomotion Policy for Quadruped Robots under Incomplete Terrain Observation | ICRA26 | 四足/Go2 | 感知运动 | 未查 |
| 209 | Kungfubot2: Learning Versatile Motion Skills for Humanoid Whole-Body Control | ICRA26 | 人形 | 技能/模仿、敏捷动作、学习+MPC | 有 |
| 210 | Learn to Teach: Sample-Efficient Privileged Learning for Humanoid Locomotion Over Real-World Uneven Terrain | ICRA26/RA-L | 人形 | 训练算法、感知运动 | 有 |
| 211 | Learning Agile Striker Skills for Humanoid Soccer Robots from Noisy Sensory Input | ICRA26 | 人形 | 技能/模仿、敏捷动作 | 未查 |
| 212 | Learning Autonomous and Safe Quadruped Traversal of Complex Terrains Using Multi-Layer Elevation Maps | ICRA26/RA-L | 双足/四足 | 感知运动、导航/VLN、安全/约束 | 未查 |
| 213 | Learning Collision-Free Object Goal Pushing for Quadruped Robots with Safe Corridors | ICRA26 | 四足 | 移动操作、安全/约束 | 有 |
| 214 | Learning Forward Looking Adaptation to Dynamic Payloads for Quadruped Locomotion Via Physics-Informed Neural Networks | ICRA26 | 四足 | 适应、移动操作 | 未查 |
| 215 | Learning Humanoid Arm Motion Via Centroidal Momentum Regularized Multi-Agent Reinforcement Learning | ICRA26/RA-L | 人形 | 训练算法 | 未查 |
| 216 | Learning Motion Skills with Adaptive Assistive Curriculum Force in Humanoid Robots | ICRA26 | 人形 | 适应、技能/模仿、训练算法 | 未查 |
| 217 | Learning Neural Observer-Predictor Models for Limb-Level Sampling-Based Locomotion Planning | ICRA26 | 四足 | 世界模型/基于模型、学习+MPC | 未查 |
| 218 | Learning Quadruped Walking from Seconds of Demonstration | ICRA26 | 四足 | 技能/模仿 | 未查 |
| 219 | Learning Quadrupedal Locomotion for a Heavy Hydraulic Robot Using an Actuator Model | ICRA26/RA-L | 四足 | sim2real/辨识 | 未查 |
| 220 | Learning Task-Invariant Properties Via Dreamer: Enabling Efficient Policy Transfer for Quadruped Robots | ICRA26 | 四足 | 世界模型/基于模型、sim2real/辨识 | 未查 |
| 221 | Look Forward to Walk Backward: Efficient Terrain Memory for Backward Locomotion with Forward Vision | ICRA26 | 足式 | 感知运动 | 未查 |
| 222 | MAKP: Multi-Mode Accurate Kicking Policy for Humanoid Robots | ICRA26 | 人形 | 敏捷动作 | 未查 |
| 223 | MARG: MAstering Risky Gap Terrains for Legged Robots with Elevation Mapping | ICRA26/T-RO | 四足 | 感知运动、安全/约束 | 未查 |
| 224 | MemClaw-RAG: Memory-Driven Navigation and Adaptive Locomotion for Wheeled-Legged Robots in Dynamic Environments | ICRA26 | 轮足 | 适应、导航/VLN | 未查 |
| 225 | MILD: Tractable Terrain Modeling for Learning Improved Bipedal Locomotion on Deformable Surfaces | ICRA26/RA-L | 双足 | sim2real/辨识 | 未查 |
| 226 | Mixture-Of-Experts Policy for Smooth and Stable Multi-Posture Fall Recovery in Bipedal Robot | ICRA26 | 双足 | 训练算法、跌倒/起身 | 未查 |
| 227 | MUJICA: Multi-Skill Unified Joint Integration of Control Architecture for Wheeled-Legged Robots | ICRA26 | 轮足/四足/**Go2-W** | 技能/模仿 | 未查 |
| 228 | MULE – Multi-Terrain and Unknown Load Adaptation for Effective Quadrupedal Locomotion | ICRA26/RA-L | 四足 | 适应、感知运动、学习+MPC | 未查 |
| 229 | Multi-Quadruped Cooperative Object Transport: Learning Decentralized Pinch-Lift-Move | ICRA26 | 四足 | 移动操作 | 未查 |
| 230 | NaviGait: Navigating Dynamically Feasible Gait Libraries Using Deep Reinforcement Learning | ICRA26 | 双足 | 导航/VLN、学习+MPC | 有 |
| 231 | Neural Internal Model Control: Learning a Robust Control Policy Via Predictive Error Feedback | ICRA26 | 四足 | 世界模型/基于模型 | 有 |
| 232 | OmniNet: Omnidirectional Jumping Neural Network with Height-Awareness for Quadrupedal Robots | ICRA26/RA-L | 四足 | 敏捷动作 | 未查 |
| 233 | OmniRetarget: Interaction-Preserving Data Generation for Humanoid Whole-Body Loco-Manipulation and Scene Interaction | ICRA26 | 人形 | 技能/模仿、移动操作 | 有 |
| 234 | One Filter to Deploy Them All: Robust Safety for Quadrupedal Navigation in Unknown Environments | ICRA26/T-RO | 四足 | 导航/VLN、安全/约束 | 未查 |
| 235 | OpenHEART: Opening Heterogeneous Articulated Objects with a Legged Manipulator | ICRA26 | 足式 | 移动操作 | 有 |
| 236 | Opt2Skill: Imitating Dynamically-Feasible Whole-Body Trajectories for Versatile Humanoid Loco-Manipulation | ICRA26/RA-L | 人形 | 技能/模仿、移动操作 | 未查 |
| 237 | PACE: Physics Augmentation for Coordinated End-To-End Reinforcement Learning Toward Versatile Humanoid Table Tennis | ICRA26 | 人形 | 敏捷动作 | 有 |
| 238 | Phase-Aware Policy Learning for Skateboard Riding of Quadruped Robots Via Feature-Wise Linear Modulation | ICRA26 | 滑板/轮滑/四足 | 敏捷动作 | 未查 |
| 239 | PMG: Parameterized Motion Generator for Human-Like Locomotion Control | ICRA26 | 人形 | sim2real/辨识 | 有 |
| 240 | PPF: Pre-Training and Preservative Fine-Tuning of Humanoid Locomotion Via Model-Assumption-Based Regularization | ICRA26/RA-L | 人形 | 适应、训练算法 | 未查 |
| 241 | Primal-Dual iLQR for GPU-Accelerated Learning and Control in Legged Robots | ICRA26/RA-L | 足式 | 学习+MPC | 有 |
| 242 | Proprioceptive Image: An Image Representation of Proprioceptive Data from Quadruped Robots for Contact Estimation Learning | ICRA26 | 四足 | 状态估计 | 未查 |
| 243 | RAMBO: RL-Augmented Model-Based Whole-Body Control for Loco-Manipulation | ICRA26/RA-L | 双足/四足 | 移动操作、世界模型/基于模型、学习+MPC | 未查 |
| 244 | REBot: Reflexive Evasion Robot for Instantaneous Dynamic Obstacle Avoidance | ICRA26 | 四足 | 导航/VLN、技能/模仿 | 有 |
| 245 | Reinforcement Learning for Stair Locomotion of a Wheeled Bipedal Robot with Contact-Guided Behavior Cloning | ICRA26 | 轮足/双足 | 感知运动、导航/VLN | 未查 |
| 246 | Reinforcement Learning-Based Robust Wall Climbing Locomotion Controller in Ferromagnetic Environment | ICRA26 | 四足 | 学习+MPC、容错 | 未查 |
| 247 | RENet: Fault-Tolerant Motion Control for Quadruped Robots Via Redundant Estimator Networks under Visual Collapse | ICRA26/RA-L | 四足 | 感知运动、状态估计、容错 | 有 |
| 248 | Retargeting Matters: General Motion Retargeting for Humanoid Motion Tracking | ICRA26 | 人形 | 技能/模仿 | 未查 |
| 249 | Risk-Aware Reinforcement Learning with Bandit-Based Adaptation for Quadrupedal Locomotion | ICRA26 | 四足/Go2 | 适应、安全/约束 | 未查 |
| 250 | RL-Augmented Adaptive Model Predictive Control for Bipedal Locomotion Over Challenging Terrain | ICRA26 | 人形/四足 | 适应、学习+MPC | 有 |
| 251 | Robot Crash Course: Learning Soft and Stylized Falling | ICRA26 | 双足 | 跌倒/起身 | 未查 |
| 252 | RPG: Robust Policy Gating for Smooth Multi-Skill Transitions in Humanoid Fighting | ICRA26 | 人形 | 技能/模仿、敏捷动作 | 未查 |
| 253 | Safe Whole-Body Loco-Manipulation Via Combined Model and Learning-Based Control | ICRA26 | 四足/Go2 | 移动操作、安全/约束 | 未查 |
| 254 | Scalable Multi-Objective Robot Reinforcement Learning through Gradient Conflict Resolution | ICRA26 | 足式 | 移动操作、训练算法 | 有 |
| 255 | SEEC: Stable End-Effector Control with Model-Enhanced Residual Learning for Humanoid Loco-Manipulation | ICRA26 | 人形 | 移动操作、学习+MPC | 未查 |
| 256 | SignBot: Learning Human-To-Humanoid Sign Language Interaction | ICRA26 | 人形 | VLA/大模型、移动操作、人机交互 | 未查 |
| 257 | SlipSense: Multimodal Sensing for Online Slip Detection in Legged Robots | ICRA26 | 四足 | 状态估计 | 未查 |
| 258 | SoftMimic: Learning Compliant Whole-Body Control from Examples | ICRA26 | 人形 | 技能/模仿、学习+MPC | 未查 |
| 259 | Spatio-Temporal Motion Retargeting for Quadruped Robots | ICRA26/T-RO | 四足 | 技能/模仿 | 未查 |
| 260 | Standing Tall: Sim to Real Fall Classification and Lead Time Prediction for Bipedal Robots | ICRA26 | 双足 | 跌倒/起身 | 未查 |
| 261 | START: Traversing Sparse Footholds with Terrain Reconstruction | ICRA26 | 四足 | 感知运动 | 未查 |
| 262 | STATE-NAV: Stability-Aware Traversability Estimation for Bipedal Navigation on Rough Terrain | ICRA26/RA-L | 双足/四足 | 导航/VLN、学习+MPC | 未查 |
| 263 | SURF-Loco: Mastering Complex Industrial Terrains with 3D Surfel-Based Reinforcement Learning for Legged Robots | ICRA26 | 多足 | 感知运动 | 未查 |
| 264 | Swimming under Constraints: A Safe Reinforcement Learning Framework for Quadrupedal Bio-Inspired Propulsion | ICRA26 | 四足 | 安全/约束 | 未查 |
| 265 | Switch: Learning Agile Skills Switching for Humanoid Robots | ICRA26 | 人形 | 技能/模仿、敏捷动作 | 未查 |
| 266 | TD-CD-MPPI: Temporal-Difference Constraint-Discounted Model Predictive Path Integral Control | ICRA26 | 足式 | 安全/约束、学习+MPC | 未查 |
| 267 | Teaching to Individual Needs: Bidirectional Teacher-Student Learning for Wheeled-Legged Locomotion | ICRA26 | 轮足 | 训练算法 | 未查 |
| 268 | Tightly-Coupled LiDAR-IMU-Leg Odometry with Online Learned Leg Kinematics Incorporating Foot Tactile Information | ICRA26 | 足式 | 感知运动、状态估计 | 未查 |
| 269 | TOLEBI: Learning Fault-Tolerant Bipedal Locomotion Via Online Status Estimation and Fallibility Rewards | ICRA26 | 人形 | 训练算法、容错、跌倒/起身 | 未查 |
| 270 | Towards Adaptable Humanoid Control Via Adaptive Motion Tracking | ICRA26 | 人形 | 适应、技能/模仿 | 未查 |
| 271 | Track Any Motions under Any Disturbances | ICRA26 | 人形 | sim2real/辨识 | 未查 |
| 272 | TrajBooster: Boosting Humanoid Whole-Body Manipulation Via Trajectory-Centric Learning | ICRA26 | 人形（含轮式人形数据源） | 移动操作、感知运动、VLA/大模型 | 未查 |
| 273 | Traversability-Aware Legged Navigation by Learning from Real-World Visual Data | ICRA26/T-RO | 四足 | 感知运动、导航/VLN | 未查 |
| 274 | TWIST2: Scalable, Portable, and Holistic Humanoid Data Collection System | ICRA26 | 人形 | 感知运动、VLA/大模型 | 有 |
| 275 | U2E: Uncertainty-Aware Modeling and Uncertainty-Guided Exploration with Deep Ensemble for Quadrupedal Robot | ICRA26 | 四足 | 训练算法、sim2real/辨识 | 未查 |
| 276 | Unified Humanoid Fall-Safety Policy from a Few Demonstrations | ICRA26 | 人形 | 技能/模仿、安全/约束、跌倒/起身 | 有 |
| 277 | Unleashing Humanoid Reaching Potential Via Real-World-Ready Skill Space | ICRA26/RA-L | 人形 | 技能/模仿、sim2real/辨识 | 未查 |
| 278 | Unveiling the Impact of Data and Model Scaling on High-Level Control for Humanoid Robots | ICRA26 | 人形 | 训练算法 | 未查 |
| 279 | VB-Com: Learning Vision-Blind Composite Humanoid Locomotion against Deficient Perception | ICRA26 | 人形 | 感知运动 | 未查 |
| 280 | VOCALoco: Viability-Optimized Cost-Aware Adaptive Locomotion | ICRA26/RA-L | 四足 | 适应、安全/约束 | 未查 |
| 281 | When the Adversary Knows You Better: Adversarial Training for Learning-Based Legged Robots | ICRA26 | 足式 | 安全/约束、训练算法 | 未查 |
| 282 | X-Nav: Learning End-To-End Cross-Embodiment Navigation for Mobile Robots | ICRA26 | 四足 | 导航/VLN、跨形态 | 未查 |
| 283 | 16 Ways to Gallop: Energetics and Body Dynamics of High-Speed Quadrupedal Gaits | IROS25 | 四足 | 敏捷动作、能效/热 | 未查 |
| 284 | A Unified Framework to Learn Collision-Free Loco-Manipulation Via Adversarial Motion Priors | IROS25 | 四足 | 技能/模仿、移动操作 | 未查 |
| 285 | Achieving Precise and Reliable Locomotion with Differentiable Simulation-Based System Identification | IROS25 | 双足 | sim2real/辨识、世界模型/基于模型 | 未查 |
| 286 | Adaptive Step Duration for Accurate Foot Placement: Achieving Robust Bipedal Locomotion on Terrains with Restricted Footholds | IROS25 | 双足 | 适应、感知运动 | 未查 |
| 287 | Addressing Dimensional Scaling in Reinforcement Learning for Symbolic Locomotion Policies through Leveraging Inductive Priors | IROS25 | 双足 | 训练算法 | 未查 |
| 288 | An Online Terrain Classification Framework for Legged Robots Based on Fusion of Proprioceptive and Exteroceptive Sensors | IROS25 | 足式 | 感知运动、状态估计 | 未查 |
| 289 | AnyBipe: An Automated End-To-End Framework for Training and Deploying Bipedal Robots Powered by Large Language Models | IROS25 | 双足 | VLA/大模型、能效/热 | 未查 |
| 290 | ARC: Robots Adaptive Risk-Aware Robust Control Via Distributional Reinforcement Learning | IROS25 | 人形 | 适应、安全/约束 | 未查 |
| 291 | Autotuning Bipedal Locomotion MPC with GRFM-Net for Efficient Sim-To-Real Transfer | IROS25 | 人形 | sim2real/辨识、学习+MPC | 未查 |
| 292 | BeeTLe: Blind Terrain-Aware Learned Locomotion | IROS25 | 足式 | 适应 | 未查 |
| 293 | Biomechanically-Inspired Bipedal Robot Locomotion Via Hybrid Gait Representation and Model-Guided Reinforcement Learning | IROS25 | 双足 | 学习+MPC | 未查 |
| 294 | CROSS-GAiT: Cross-Attention-Based Multimodal Representation Fusion for Parametric Gait Adaptation in Complex Terrains | IROS25 | 四足 | 适应、感知运动、能效/热 | 未查 |
| 295 | Distillation-PPO: A Novel Two-Stage Reinforcement Learning Framework for Humanoid Robot Perceptive Locomotion | IROS25 | 人形 | 感知运动、训练算法 | 未查 |
| 296 | DSE: Denoising State Estimator for RL-Based Bipedal Robot Locomotion | IROS25 | 双足 | 状态估计、能效/热 | 未查 |
| 297 | Efficient Learning of a Unified Policy for Whole-Body Manipulation and Locomotion Skills | IROS25 | 四足 | 技能/模仿、移动操作 | 未查 |
| 298 | Energy-Efficient Motion Planner for Legged Robots | IROS25 | 四足 | 能效/热 | 未查 |
| 299 | Energy-Efficient Omnidirectional Locomotion for Wheeled Quadrupeds Via Predictive Energy-Aware Nominal Gait Selection | IROS25 | 轮足/四足 | 能效/热、学习+MPC | 未查 |
| 300 | Env-Mani: Quadrupedal Robot Loco-Manipulation with Environment-In-The-Loop | IROS25 | 四足 | 移动操作 | 未查 |
| 301 | Explosive Jumping with Rigid and Articulated Soft Quadrupeds Via Example Guided Reinforcement Learning | IROS25 | 四足 | 敏捷动作 | 未查 |
| 302 | Fast Autolearning for Multimodal Walking in Humanoid Robots with Variability of Experience | IROS25/RA-L | 人形 | 适应 | 未查 |
| 303 | FR-Net: Learning Robust Quadrupedal Fall Recovery on Challenging Terrains through Mass-Contact Prediction | IROS25/RA-L | 四足/Go2 | 跌倒/起身、感知运动 | 未查 |
| 304 | Gait in Eight: Efficient On-Robot Learning for Omnidirectional Quadruped Locomotion | IROS25 | 四足 | 训练算法 | 有 |
| 305 | Generalized Locomotion in Out-Of-Distribution Conditions with Robust Transformer | IROS25 | 四足/多足 | 能效/热 | 未查 |
| 306 | HAC-LOCO: Learning Hierarchical Active Compliance Control for Quadruped Locomotion under Continuous External Disturbances | IROS25 | 四足 | 能效/热 | 未查 |
| 307 | Helpful DoggyBot: Open-World Object Fetching Using Legged Robots and Vision-Language Models | IROS25 | 四足 | 感知运动、VLA/大模型、移动操作 | 未查 |
| 308 | HeStIa: Asynchronous Embodied Dynamic Locomotion Learning for Walking Robots through Multimodal Large Language Models | IROS25 | 足式 | VLA/大模型、感知运动 | 未查 |
| 309 | HiFAR: Multi-Stage Curriculum Learning for High-Dynamics Humanoid Fall Recovery | IROS25 | 人形 | 敏捷动作、训练算法、跌倒/起身 | 未查 |
| 310 | Human-Humanoid Robots Cross-Embodiment Behavior-Skill Transfer Using Decomposed Adversarial Learning from Demonstration | IROS25 | 人形 | 技能/模仿、跨形态、人机交互 | 未查 |
| 311 | Humanoid Whole-Body Locomotion on Narrow Terrain Via Dynamic Balance and Reinforcement Learning | IROS25 | 人形 | 感知运动 | 有 |
| 312 | I-CTRL: Imitation to Control Humanoid Robots through Bounded Residual Reinforcement Learning | IROS25 | 人形 | 技能/模仿、学习+MPC | 未查 |
| 313 | Imitation-Enhanced Reinforcement Learning with Privileged Smooth Transition for Hexapod Locomotion | IROS25/RA-L | 四足/多足 | 技能/模仿、训练算法 | 未查 |
| 314 | Impact of Static Friction on Sim2Real in Robotic Reinforcement Learning | IROS25 | 足式 | sim2real/辨识 | 未查 |
| 315 | Integrating Trajectory Optimization and Reinforcement Learning for Quadrupedal Jumping with Terrain-Adaptive Landing | IROS25 | 四足 | 适应、敏捷动作、学习+MPC | 未查 |
| 316 | Interactive Navigation for Legged Manipulators with Learned Arm-Pushing Controller | IROS25 | 足式 | 导航/VLN、移动操作 | 有 |
| 317 | IWalker: Imperative Visual Planning for Walking Humanoid Robot | IROS25 | 人形 | 感知运动 | 未查 |
| 318 | KLEIYN : A Quadruped Robot with an Active Waist for Both Locomotion and Wall Climbing | IROS25 | 四足 | 其他 | 未查 |
| 319 | Learning Accurate Whole-Body Throwing with High-Frequency Residual Policy and Pullback Tube Acceleration | IROS25 | 足式 | 移动操作、学习+MPC | 未查 |
| 320 | Learning Distributed End-To-End Hunting Locomotion for Multiple Quadruped Robots | IROS25 | 四足 | 其他 | 有 |
| 321 | Learning Natural and Robust Hexapod Locomotion Over Complex Terrains Via Motion Priors Based on Deep Reinforcement Learning | IROS25 | 多足 | 技能/模仿 | 未查 |
| 322 | Learning Perceptive Humanoid Locomotion Over Challenging Terrain | IROS25 | 人形 | 感知运动 | 未查 |
| 323 | Learning Robust and Flexible Locomotion of Wheel-Legged Quadruped Robots in Complex Terrains | IROS25 | 轮足/四足 | 导航/VLN | 未查 |
| 324 | Learning Smooth Humanoid Locomotion through Lipschitz-Constrained Policies | IROS25 | 人形 | 安全/约束、训练算法 | 未查 |
| 325 | Learning Symmetric Legged Locomotion Via State Distribution Symmetrization | IROS25 | 人形/四足 | 训练算法 | 未查 |
| 326 | Learning to Exploit Leg Odometry Enables Terrain-Aware Quadrupedal Locomotion | IROS25 | 四足 | 状态估计、感知运动、导航/VLN | 未查 |
| 327 | Learning to Traverse Challenging Terrain Using Vision and Forward Kinematics | IROS25 | 四足 | 感知运动 | 未查 |
| 328 | Learning Whole-Body Control for Small-Sized Quadruped Robots with a Flexible Spine | IROS25 | 四足 | 学习+MPC | 未查 |
| 329 | Learning-Based Quadruped Robot Framework for Locomotion on Dynamic Rigid Platforms | IROS25 | 四足 | 适应 | 未查 |
| 330 | Legged Robot State Estimation Using Invariant Neural-Augmented Kalman Filter with a Neural Compensator | IROS25 | 足式 | 状态估计、世界模型/基于模型 | 有 |
| 331 | Like Playing a Video Game: Spatial-Temporal Optimization of Foot Trajectories for Controlled Football Kicking in Bipedal Robots | IROS25 | 人形/四足 | 敏捷动作、移动操作 | 未查 |
| 332 | Long-Horizon Locomotion and Manipulation on a Quadrupedal Robot with Large Language Models | IROS25 | 四足 | VLA/大模型、移动操作 | 未查 |
| 333 | LoopSR: Looping Sim-And-Real for Lifelong Policy Adaptation of Legged Robots | IROS25 | 足式 | sim2real/辨识、适应 | 未查 |
| 334 | Manipulate-To-Navigate: Reinforcement Learning with Visual Affordances and Manipulability Priors | IROS25 | 四足 | 感知运动、导航/VLN、技能/模仿、移动操作 | 未查 |
| 335 | MoE-Loco: Leveraging Mixture of Experts for Multi-Task Locomotion | IROS25 | 双足/四足 | 训练算法 | 未查 |
| 336 | Mysteric-Net: MIMO Hysteretic Friction-Aware Lagrangian-Based Network for Legged Robot | IROS25 | 足式 | 世界模型/基于模型 | 未查 |
| 337 | Natural Humanoid Robot Locomotion with Generative Motion Prior | IROS25 | 人形 | 技能/模仿、感知运动 | 未查 |
| 338 | Non-Gaited Legged Locomotion with Monte-Carlo Tree Search and Supervised Learning | IROS25/RA-L | 四足 | 学习+MPC | 未查 |
| 339 | Physics-Informed Neural Networks with Unscented Kalman Filter for Sensorless Joint Torque Estimation in Humanoid Robots | IROS25/RA-L | 人形 | 状态估计 | 未查 |
| 340 | Playful DoggyBot: Learning Agile and Precise Quadrupedal Locomotion | IROS25 | 四足 | 敏捷动作、感知运动 | 未查 |
| 341 | Preference Aligned Diffusion Planner for Quadrupedal Locomotion Control | IROS25 | 四足 | 训练算法 | 未查 |
| 342 | Preferenced Oracle Guided Multi-Mode Policies for Dynamic Bipedal Loco-Manipulation | IROS25 | 人形 | 移动操作、训练算法 | 未查 |
| 343 | QuietPaw: Learning Quadrupedal Locomotion with Versatile Noise Preference Alignment | IROS25 | 四足 | 能效/热、训练算法 | 未查 |
| 344 | Reference-Steering Via Data-Driven Predictive Control for Hyper-Accurate Robotic Flying-Hopping Locomotion | IROS25 | 足式 | 世界模型/基于模型 | 未查 |
| 345 | Reinforcement Learning-Based Optimization of Humanoid Joint Motion Control Via Text-Driven Human Motion Mapping | IROS25 | 人形 | VLA/大模型、技能/模仿 | 未查 |
| 346 | RoboDuet: Learning a Cooperative Policy for Whole-Body Legged Loco-Manipulation | IROS25/RA-L | 四足 | 移动操作 | 有 |
| 347 | Robust Ladder Climbing with a Quadrupedal Robot | IROS25 | 四足 | 感知运动 | 未查 |
| 348 | SF-TIM: A Simple Framework for Enhancing Quadrupedal Robot Jumping Agility by Combining Terrain Imagination and Measurement | IROS25 | 四足 | 敏捷动作、感知运动 | 有 |
| 349 | SHIELD: Safety on Humanoids Via CBFs in Expectation on Learned Dynamics | IROS25 | 人形 | 安全/约束、世界模型/基于模型 | 未查 |
| 350 | Stabilizing Humanoid Robot Trajectory Generation Via Physics-Informed Learning and Control-Informed Steering | IROS25 | 人形 | 学习+MPC | 未查 |
| 351 | Stepping Locomotion for a Walking Excavator Robot Using Hierarchical Reinforcement Learning and Action Masking | IROS25 | 足式 | 其他 | 未查 |
| 352 | TAR: Teacher-Aligned Representations Via Contrastive Learning for Quadrupedal Locomotion | IROS25 | 四足 | 训练算法 | 有 |
| 353 | Teacher Motion Priors: Enhancing Robot Locomotion Over Challenging Terrain | IROS25 | 人形 | 技能/模仿、训练算法 | 未查 |
| 354 | The Duke Humanoid: Design and Control for Energy Efficient Bipedal Locomotion Using Passive Dynamics | IROS25 | 人形 | 能效/热 | 未查 |
| 355 | Thruster-Enhanced Locomotion: A Decoupled Model Predictive Control with Learned Contact Residuals | IROS25 | 四足 | 学习+MPC | 未查 |
| 356 | Transferable Latent-To-Latent Locomotion Policy for Efficient and Versatile Motion Control of Diverse Legged Robots | IROS25 | 足式 | 跨形态 | 未查 |
| 357 | Unified Locomotion Transformer with Simultaneous Sim-To-Real Transfer for Quadrupeds | IROS25 | 四足 | sim2real/辨识 | 未查 |
| 358 | UniLegs: Universal Multi-Legged Robot Control through Morphology-Agnostic Policy Distillation | IROS25 | 四足/多足 | 训练算法、跨形态 | 未查 |
| 359 | VMTS: Vision-Assisted Teacher-Student Reinforcement Learning for Multi-Terrain Locomotion in Bipedal Robots | IROS25 | 双足 | 感知运动、训练算法 | 未查 |
| 360 | Whole-Body Impedance Control of a Humanoid Robot Based on Human-Human Demonstration for Human-Robot Collaboration | IROS25 | 人形 | 技能/模仿、人机交互 | 未查 |
| 361 | Adversarial Locomotion and Motion Imitation for Humanoid Policy Learning | NeurIPS25 | 人形 | 技能/模仿 | 有 |
| 362 | From Experts to a Generalist: Toward General Whole-Body Control for Humanoid Robots | NeurIPS25 | 人形 | 跨形态、sim2real/辨识 | 未查 |
| 363 | KungfuBot: Physics-Based Humanoid Whole-Body Control for Learning Highly-Dynamic Skills | NeurIPS25 | 人形 | 技能/模仿、敏捷动作、学习+MPC | 有 |
| 364 | Periodic Skill Discovery | NeurIPS25 | 足式 | 技能/模仿、训练算法 | 有 |
| 365 | Real-DRL: Teach and Learn in Reality | NeurIPS25 | 四足 | 安全/约束 | 未查 |
| 366 | FastDSAC: Unlocking the Potential of Maximum Entropy RL in High-Dimensional Humanoid Control | NeurIPS26 | 人形 | 训练算法 | 未查 |
| 367 | Humanoid Horizon: Extending Task Horizon in Whole-Body Loco-Manipulation via Parallel Training, Dynamic Starting, and Reward Gating | NeurIPS26 | 人形 | 移动操作、训练算法 | 未查 |
| 368 | HumanoidArena: Benchmarking Egocentric Hierarchical Whole-body Learning | NeurIPS26 | 人形 | 感知运动 | 未查 |
| 369 | LessMimic: Versatile Humanoid-Object Interaction with Unified Distance Field Representations | NeurIPS26 | 人形 | 技能/模仿、移动操作 | 未查 |
| 370 | SUGAR: A Scalable Human-Video-Driven Generalizable Humanoid Loco-Manipulation Learning Framework | NeurIPS26 | 人形 | 移动操作 | 未查 |
| 371 | Synthesizing Whole-Body Loco-Manipulation without Human Demonstration | NeurIPS26 | 足式 | 技能/模仿、移动操作 | 未查 |
| 372 | UniT: Toward a Unified Physical Language for Human-to-Humanoid Policy Learning and World Modeling | NeurIPS26 | 人形 | VLA/大模型、世界模型/基于模型 | 未查 |
| 373 | Hierarchical World Models as Visual Whole-Body Humanoid Controllers | ICLR25 | 人形 | 感知运动、世界模型/基于模型 | 未查 |
| 374 | Language Guided Skill Discovery | ICLR25 | 足式 | VLA/大模型、技能/模仿、训练算法 | 未查 |
| 375 | Zero-Shot Whole-Body Humanoid Control via Behavioral Foundation Models | ICLR25 | 人形 | VLA/大模型 | 未查 |
| 376 | BFM-Zero: A Promptable Behavioral Foundation Model for Humanoid Control Using Unsupervised Reinforcement Learning | ICLR26 | 人形 | VLA/大模型 | 未查 |
| 377 | Endowing GPT-4 with a Humanoid Body: Building the Bridge Between Off-the-Shelf VLMs and the Physical World | ICLR26 | 人形 | VLA/大模型 | 未查 |
| 378 | From Language to Locomotion: Retargeting-free Humanoid Control via Motion Latent Guidance | ICLR26 | 人形 | VLA/大模型、技能/模仿 | 未查 |
| 379 | HWC-Loco: A Hierarchical Whole-Body Control Approach to Robust Humanoid Locomotion | ICLR26 | 人形 | 其他 | 未查 |
| 380 | Towards Bridging the Gap between Large-Scale Pretraining and Efficient Finetuning for Humanoid Control | ICLR26 | 人形 | 适应、训练算法 | 未查 |
| 381 | WholeBodyVLA: Towards Unified Latent VLA for Whole-body Loco-manipulation Control | ICLR26 | 足式 | VLA/大模型、移动操作 | 未查 |
| 382 | Diversifying Robot Locomotion Behaviors with Extrinsic Behavioral Curiosity | ICML25 | 人形 | 训练算法 | 有 |
| 383 | Learning to Reconfigure: Configuration-Control Co-optimization of Reconfigurable Robots for Heterogeneous Locomotion | ICML26 | 足式 | 跨形态 | 未查 |
| 384 | Learning Transferable Interaction Primitives from Game Videos for Humanoid Locomotion | ICML26 | 人形 | 移动操作 | 未查 |
| 385 | Scalable and General Whole-Body Control for Cross-Humanoid Locomotion | ICML26 | 人形 | 跨形态 | 未查 |

### 2.2 期刊（初筛，仅标题；以 venue_sweep_journals.md 为准）

| # | 标题 | 出处 | 平台 | 标签 | 代码 |
|---|---|---|---|---|---|
| 386 | Advances, challenges, and opportunities for legged robots | SciRob | 人形/四足 | 综述 | 未查 |
| 387 | Agile perceptive multiskill locomotion for quadrupedal robots in the wild | SciRob | 四足 | 感知运动、技能/模仿、敏捷动作 | 未查 |
| 388 | Attention-based map encoding for learning generalized legged locomotion | SciRob | 人形/四足 | 感知运动、导航/VLN、世界模型/基于模型 | 未查 |
| 389 | BeyondMimic: From motion tracking to versatile humanoid control via guided diffusion | SciRob | 人形 | 技能/模仿 | 未查 |
| 390 | Bridging vision-language reasoning and learned control for legged navigation in the wild | SciRob | 足式 | 感知运动、导航/VLN、VLA/大模型 | 未查 |
| 391 | Evolution of humanoid locomotion control | SciRob | 人形 | 综述 | 未查 |
| 392 | High-speed control and navigation for quadrupedal robots on complex and discrete terrain | SciRob | 四足 | 导航/VLN、敏捷动作 | 未查 |
| 393 | How robot dogs see the unseeable: Improving visual interpretability via peering for exploratory robots | SciRob | 双足/四足/多足 | 感知运动、导航/VLN | 未查 |
| 394 | Humanoid robot learning of complex behaviors with LLMs | SciRob | 人形 | VLA/大模型 | 未查 |
| 395 | Learning coordinated badminton skills for legged manipulators | SciRob | 足式 | 技能/模仿、敏捷动作、移动操作 | 未查 |
| 396 | Learning vision-driven reactive soccer skills for humanoid robots | SciRob | 人形 | 感知运动、技能/模仿、敏捷动作 | 未查 |
| 397 | SONIC: Supersizing motion tracking for natural humanoid whole-body control | SciRob | 人形 | 技能/模仿、感知运动、VLA/大模型 | 未查 |
| 398 | ZEST: Zero-shot embodied skill transfer for athletic robot control | SciRob | 人形/四足 | 技能/模仿、敏捷动作 | 未查 |
| 399 | An eight-neuron network for quadruped locomotion with hip-knee joint control | IJRR | 四足 | 其他 | 未查 |
| 400 | GrandTour: A legged robotics dataset in the wild for multi-modal perception and state estimation | IJRR | 四足 | 感知运动、状态估计 | 未查 |
| 401 | Growable and interpretable neural control with online continual learning for autonomous lifelong locomotion learning machines | IJRR | 多足 | 适应 | 未查 |
| 402 | Learning-based legged locomotion: State of the art and future perspectives | IJRR | 人形/四足 | 综述 | 未查 |
| 403 | Parkour in the wild: Learning a general and extensible agile locomotion policy using multi-expert distillation and RL fine-tuning | IJRR | 四足 | 适应、感知运动、敏捷动作、训练算法 | 未查 |
| 404 | Towards bridging the gap: Systematic sim-to-real transfer for diverse legged robots | IJRR | 四足 | sim2real/辨识、跨形态 | 未查 |
| 405 | Agile and Generalized Legged Locomotion via Attention-Based Neural Map Encoding | T-RO | 足式 | 敏捷动作 | 未查 |
| 406 | ALORE: Autonomous Large-Object Rearrangement with a Legged Manipulator | T-RO | 足式 | 移动操作 | 未查 |
| 407 | DreamWaQ++: Obstacle-Aware Quadrupedal Locomotion With Resilient Multimodal Reinforcement Learning | T-RO | 四足 | 感知运动 | 未查 |
| 408 | Pushing Physical Limits and Uncovering Motion Templates of Spine-Based Quadruped Locomotion via Reinforcement Learning | T-RO | 四足 | 移动操作 | 未查 |
| 409 | SMASH: Mastering Scalable Whole-Body Skills for Humanoid Ping-Pong With Egocentric Vision | T-RO | 人形 | 感知运动、技能/模仿、敏捷动作 | 未查 |
| 410 | A Motion Control Algorithm of Wheel-Legged Robot via Adaptive Dynamic Programming and Data-Driven Value Iteration | RA-L | 轮足 | 适应 | 未查 |
| 411 | Agile Wheel-Bipedal Loco-Manipulation With Active Force Rejection | RA-L | 轮足/双足 | 敏捷动作、移动操作 | 未查 |
| 412 | ALARM: Safe Reinforcement Learning With Reliable Mimicry for Robust Legged Locomotion | RA-L | 足式 | 技能/模仿、安全/约束 | 未查 |
| 413 | Angular Momentum LIP Guided Reinforcement Learning With Step Duration Modulation for Dynamic Locomotion of Bipedal Robots | RA-L | 双足 | 学习+MPC | 未查 |
| 414 | Attention-Based Neural-Augmented Kalman Filter for Legged Robot State Estimation | RA-L | 足式 | 状态估计 | 未查 |
| 415 | CATR: Confidence-Aware Terrain Reconstruction for Vision-Based Quadruped Locomotion | RA-L | 四足 | 感知运动 | 未查 |
| 416 | CodeAct: Codebook-Guided Multi-Skill Integration for Dynamic Humanoid Whole-Body Control | RA-L | 人形 | 技能/模仿 | 未查 |
| 417 | Collision-Free Humanoid Traversal in Cluttered Indoor Scenes | RA-L | 人形 | 导航/VLN | 未查 |
| 418 | Contact-Guided Exploration for Non-Prehensile Locomanipulation With Multi-Critic RL | RA-L | 足式 | 移动操作、训练算法 | 未查 |
| 419 | CReF: Cross-Modal and Recurrent Fusion for Depth-Conditioned Humanoid Locomotion | RA-L | 人形 | 感知运动 | 未查 |
| 420 | CROSSER: Learning Generalizable Humanoid Locomotion Through Inverse Dynamics-Guided Cross-Simulator Adaptation | RA-L | 人形 | sim2real/辨识、适应 | 未查 |
| 421 | CWI: Composite Humanoid Whole-Body Imitation System for Loco-Manipulation | RA-L | 人形 | 技能/模仿、移动操作 | 未查 |
| 422 | DemoHLM: From One Demonstration to Generalizable Humanoid Loco-Manipulation | RA-L | 人形 | 技能/模仿、移动操作 | 未查 |
| 423 | DoublyAware: Dual Planning and Policy Awareness for Temporal Difference Learning in Humanoid Locomotion | RA-L | 人形 | 训练算法 | 未查 |
| 424 | DPL: Depth-Only Perceptive Humanoid Locomotion via Realistic Depth Synthesis and Cross-Attention Terrain Reconstruction | RA-L | 人形 | 感知运动 | 未查 |
| 425 | DSE: A Denoising State Estimator for RL-Based Bipedal Robot Locomotion | RA-L | 双足 | 状态估计 | 未查 |
| 426 | Dynamic Legged Ball Manipulation on Rugged Terrains With Hierarchical Reinforcement Learning | RA-L | 足式 | 移动操作 | 未查 |
| 427 | Dynamic Policy Learning for Legged Robot With Simplified Model Pretraining and Model-Homotopy-Inspired Transfer | RA-L | 足式 | 训练算法 | 未查 |
| 428 | Efficient Exploration for Quadruped Robots Using Graph Neural Networks With Global Attention | RA-L | 四足 | 训练算法 | 未查 |
| 429 | Emerging Locomotion Behavior by Maximizing Entropy-Based Information Metrics | RA-L | 足式 | 训练算法 | 未查 |
| 430 | EMOTION: Expressive Motion Sequence Generation for Humanoid Robots With In-Context Learning | RA-L | 人形 | 适应、技能/模仿 | 未查 |
| 431 | Extending the Speed Limit of Quadrupedal Locomotion via Refined Actuator Modeling and Adaptive Command Scheduling | RA-L | 四足 | sim2real/辨识、适应 | 未查 |
| 432 | FastStair: Learning to Run up Stairs With Humanoid Robots | RA-L | 人形 | 感知运动、敏捷动作 | 未查 |
| 433 | From Policy Actions to Whole-Body Dynamics: A Unified Projection-Based Framework for Versatile Legged Loco-Manipulation | RA-L | 足式 | 移动操作 | 未查 |
| 434 | Gait Optimization for Underwater Legged Robots Using Data-Driven Hydrodynamic Modeling and Reinforcement Learning | RA-L | 足式 | 世界模型/基于模型 | 未查 |
| 435 | Gait-Adaptive Perceptive Humanoid Locomotion With Real-Time Under-Base Terrain Reconstruction | RA-L | 人形 | 适应、感知运动 | 未查 |
| 436 | Gait-Parameterized Reinforcement Learning for a Hydraulic Quadruped Robot | RA-L | 四足 | 其他 | 未查 |
| 437 | Global-Local Attention Decomposition for Terrain Encoding in Humanoid Perceptive Locomotion | RA-L | 人形 | 感知运动 | 未查 |
| 438 | HiPAN: Hierarchical Posture-Adaptive Navigation for Quadruped Robots in Unstructured 3D Environments | RA-L | 四足 | 适应、导航/VLN | 未查 |
| 439 | Human-Inspired Adaptive Gait Learning for Humanoids Locomotion | RA-L | 人形 | 适应 | 未查 |
| 440 | Human2Humanoid: Physics-Aware Cross-Morphology Motion Retargeting for Humanoid Robots | RA-L | 人形 | 技能/模仿、跨形态 | 未查 |
| 441 | Humanoid Goalkeeper: Learning From Position Conditioned Task-Motion Constraints | RA-L | 人形 | 敏捷动作、安全/约束 | 未查 |
| 442 | LA-WBC: Learning-Driven Adaptation of Whole-Body Control for Safe Locomotion on Uncertain Terrain | RA-L | 足式 | 适应、安全/约束、学习+MPC | 未查 |
| 443 | Learning Asynchronous Upper-Body Task-Space Trajectory Tracking Policy for Humanoid Robots | RA-L | 人形 | 技能/模仿 | 未查 |
| 444 | Learning Dynamic Pick-and-Place for a Legged Manipulator | RA-L | 足式 | 移动操作 | 未查 |
| 445 | Learning Humanoid Navigation From Human Data | RA-L | 人形 | 导航/VLN、技能/模仿 | 未查 |
| 446 | Learning Multi-Stage Pick-and-Place With a Legged Mobile Manipulator | RA-L | 足式 | 移动操作 | 未查 |
| 447 | Learning Spine-Assisted Bounding Locomotion for Gap Crossing in a Small-Scale Quadruped Robot | RA-L | 四足 | 敏捷动作 | 未查 |
| 448 | Learning Terrain-Aware Whole-Body Control for Perceptive Legged Loco-Manipulation | RA-L | 足式 | 感知运动、移动操作、学习+MPC | 未查 |
| 449 | Learning Time-Varying Joint-Motor Mapping for Precise Control of Cable-Driven Humanoid Robots Under Transmission Uncertainties | RA-L | 人形 | sim2real/辨识 | 未查 |
| 450 | Learning Whole-Body Humanoid Locomotion via Motion Generation and Motion Tracking | RA-L | 人形 | 技能/模仿 | 未查 |
| 451 | Learning Whole-Body Loco-Manipulation for Omni-Directional Task Space Pose Tracking With a Wheeled-Quadrupedal-Manipulator | RA-L | 轮足/四足 | 移动操作 | 未查 |
| 452 | Learning-Based Kinematic Residual Compensation With Latent Regime Mixture-of-Experts for Quadruped Odometry | RA-L | 四足 | 学习+MPC、训练算法、状态估计 | 未查 |
| 453 | LNP: Liquid Network Policy for Humanoid Whole-Body Motion Tracking | RA-L | 人形 | 技能/模仿 | 未查 |
| 454 | M3imic: Learning a Versatile Whole-Body Controller for Multimodal Motion Mimicking | RA-L | 足式 | 技能/模仿、学习+MPC | 未查 |
| 455 | MLM: Learning Multi-Task Loco-Manipulation Whole-Body Control for Quadruped Robot With Arm | RA-L | 四足 | 移动操作、学习+MPC | 未查 |
| 456 | Mobile Pedipulation for Object Sliding via Hierarchical Control on a Wheeled Bipedal Robot | RA-L | 轮足/双足 | 移动操作 | 未查 |
| 457 | MotionVL: Vision-Language Supervision for Reinforcement Learning of Humanoid Motion | RA-L | 人形 | 感知运动、VLA/大模型 | 未查 |
| 458 | OmniTrack: General Motion Tracking via Physics-Consistent Reference | RA-L | 足式 | 技能/模仿 | 未查 |
| 459 | PAINT: Partner-Agnostic Intent-Aware Cooperative Transport With Legged Robots | RA-L | 足式 | 移动操作、人机交互 | 未查 |
| 460 | PAKE: Learning Whole-Body Loco-Manipulation With Partial Kinematic Embeddings | RA-L | 足式 | 移动操作 | 未查 |
| 461 | Physically-Grounded Learning and Control for Leg-Arm Reuse Robots by Scheduling Physical Primitives | RA-L | 足式 | 其他 | 未查 |
| 462 | PolyMorph: Learning Locomotion Policy for Cross-Embodiment Adaptation | RA-L | 足式 | 适应、跨形态 | 未查 |
| 463 | PPL: Point Cloud Supervised Proprioceptive Locomotion Reinforcement Learning for Legged Robots in Crawl Spaces | RA-L | 足式 | 感知运动 | 未查 |
| 464 | Pretraining in Actor-Critic Reinforcement Learning for Locomotion | RA-L | 足式 | 训练算法 | 未查 |
| 465 | PRVR: Learning Posture Recovery for a Legged Spherical Robot Using Vector Reward | RA-L | 足式 | 训练算法、跌倒/起身 | 未查 |
| 466 | PUMA: Perception-Driven Unified Foothold Prior for Mobility Augmented Quadruped Parkour | RA-L | 四足 | 感知运动、敏捷动作 | 未查 |
| 467 | QLIMB: End-to-End Whole-Body Control for Quadruped Loco-Manipulation and Balance on Complex Terrains | RA-L | 四足 | 移动操作 | 未查 |
| 468 | Quiet Humanoid Walking With NMPC-Informed Reinforcement Learning | RA-L | 人形 | 能效/热 | 未查 |
| 469 | RAIWAY: A Large-Wheeled Bipedal Robot With Contact-Informed Blind Locomotion | RA-L | 轮足/双足 | 其他 | 未查 |
| 470 | Rationality Randomization With Maximum Entropy for Robust Dynamic Obstacle Avoidance on Legged Robots | RA-L | 足式 | 导航/VLN、技能/模仿、训练算法 | 未查 |
| 471 | Real-to-Sim-to-Real: Learning Agile and Robust Recovery Skills With Terrain Imagination via Adversarial Imitation | RA-L | 足式 | sim2real/辨识、技能/模仿、敏捷动作、跌倒/起身 | 未查 |
| 472 | REFINE-DP: Diffusion Policy Fine-Tuning for Humanoid Loco-Manipulation via Reinforcement Learning | RA-L | 人形 | 适应、移动操作 | 未查 |
| 473 | Reinforcement Learning for Robust Climbing Locomotion With Rope-Driven Legged Robot | RA-L | 足式 | 其他 | 未查 |
| 474 | Reinforcement Learning of Contact Preferability in Multi-Contact Locomotion Planning for Humanoids | RA-L | 人形 | 学习+MPC | 未查 |
| 475 | RL-Augmented MPC for Non-Gaited Legged and Hybrid Locomotion | RA-L | 足式 | 学习+MPC | 未查 |
| 476 | RobotDancing: Residual-Action Reinforcement Learning Enables Robust Long-Horizon Humanoid Motion Tracking | RA-L | 人形 | 技能/模仿、学习+MPC | 未查 |
| 477 | Robust Fall Recovery for Armless Bipedal-Wheeled Robots via Force-Guided Learning | RA-L | 轮足/双足 | 跌倒/起身 | 未查 |
| 478 | Robust Locomotion Policy With Adaptive Lipschitz Constraint for Legged Robots | RA-L | 足式 | 适应、安全/约束、训练算法 | 未查 |
| 479 | Scaling Rough Terrain Locomotion With Automatic Curriculum Reinforcement Learning | RA-L | 足式 | 训练算法 | 未查 |
| 480 | SDWM: Learning Bipedal Locomotion via a Smooth Denoising World Model Method | RA-L | 双足 | 世界模型/基于模型 | 未查 |
| 481 | See-Touch-Predict: Active Exploration and Online Perception of Terrain Physics With Legged Robots | RA-L | 足式 | 感知运动、训练算法 | 未查 |
| 482 | SPRINT: Efficient Spectral Priors for Humanoid Athletic Sprints | RA-L | 人形 | 敏捷动作 | 未查 |
| 483 | TACT: Humanoid Whole-Body Contact Manipulation Through Deep Imitation Learning With Tactile Modality | RA-L | 人形 | 技能/模仿、移动操作 | 未查 |
| 484 | TCLL: Temporal-Aware Contrastive Latent Learning for Heterogeneous Legged Robots Locomotion | RA-L | 足式 | 跨形态 | 未查 |
| 485 | Teacher-Guided Terrain-Aware Learning for Recovery of Quadruped Robots | RA-L | 四足 | 训练算法、跌倒/起身 | 未查 |
| 486 | TerAdapt: Proprioceptive Terrain-Adaptive Locomotion via Codebook Aligned Representation Learning | RA-L | 足式 | 适应 | 未查 |
| 487 | Terramechanics-Aware Adaptive Quadrupedal Locomotion via Foot-Terrain Interaction Model | RA-L | 四足 | 适应、移动操作 | 未查 |
| 488 | TNavRL: Cross-Modal Transformer for Humanoid Visual Navigation | RA-L | 人形 | 感知运动、导航/VLN | 未查 |
| 489 | Towards Quadrupedal Jumping and Walking for Dynamic Locomotion Using Reinforcement Learning | RA-L | 四足 | 敏捷动作 | 未查 |
| 490 | Transformer Observer-Based Contact Force Estimation for Quadruped Manipulators With Model Uncertainties | RA-L | 四足 | 移动操作 | 未查 |
| 491 | UniTracker: Learning Universal Whole-Body Motion Tracker for Humanoid Robots | RA-L | 人形 | 跨形态 | 未查 |
| 492 | Unleashing the Agility of Wheeled-Legged Robots for High-Dynamic Reflexive Obstacle Evasion | RA-L | 轮足 | 导航/VLN、敏捷动作 | 未查 |
| 493 | Variable-Frequency Model Learning and Predictive Control for Jumping Maneuvers on Legged Robots | RA-L | 足式 | 敏捷动作 | 未查 |
| 494 | Vision-Assisted Bipedal Locomotion on Challenging Terrains via Terrain-Related Adversarial Motion Priors | RA-L | 双足 | 感知运动、技能/模仿 | 未查 |
| 495 | VPIES: Variational Privileged Information Encoder as Scaffold for Legged Locomotion Learning | RA-L | 足式 | 训练算法 | 未查 |
| 496 | VR-Robo: A Real-to-Sim-to-Real Framework for Visual Robot Navigation and Locomotion | RA-L | 足式 | sim2real/辨识、感知运动、导航/VLN | 未查 |
| 497 | Whole-Body Constrained Learning for Legged Locomotion via Hierarchical Optimization | RA-L | 足式 | 安全/约束 | 未查 |
| 498 | X-IONet: Cross-Platform Inertial Odometry Network for Pedestrian and Legged Robot | RA-L | 足式 | 状态估计 | 未查 |
| 499 | YMSkater: Learning Skating Locomotion via Model-Guided Reinforcement Learning | RA-L | 滑板/轮滑 | 敏捷动作 | 未查 |

## 3. 主题地图

### 3.1 标签计数（会议 385 篇，一篇可有多个标签；括号内为人形/四足/轮足篇数）

| 标签 | 篇数 | 人形 | 四足 | 轮足 | 判断 |
|---|---|---|---|---|---|
| 技能/模仿（动作跟踪、重定向、遥操作数据） | 88 | 59 | 17 | 1 | **最拥挤**，主要是人形 |
| 移动操作 | 79 | 44 | 18 | 1 | 拥挤 |
| 感知运动（深度/高程/跑酷/楼梯） | 71 | 38 | 20 | 1 | 拥挤 |
| 训练算法（课程、蒸馏、MoE、奖励） | 58 | 27 | 16 | 1 | 拥挤 |
| 适应（在线/元学习/微调） | 51 | 22 | 18 | 1 | 拥挤 |
| 敏捷动作（跳跃、足球、球拍类运动） | 47 | 32 | 11 | 1 | 拥挤（人形运动类集中在 CoRL26） |
| 学习+MPC | 34 | 13 | 10 | 2 | 中等 |
| VLA/大模型 | 31 | 22 | 2 | 0 | 中等；四足很少 |
| 世界模型/基于模型 | 31 | 12 | 12 | 0 | 中等 |
| sim2real/辨识 | 28 | 13 | 6 | **0** | 中等；**轮足为 0** |
| 安全/约束 | 27 | 10 | 14 | 0 | 中等 |
| 导航/VLN | 25 | 6 | 11 | 3 | 中等 |
| 能效/热 | 18 | 5 | 9 | 2 | 稀疏 |
| 跨形态 | 17 | 11 | 3 | 1 | 稀疏 |
| 状态估计（学习型） | 12 | 1 | 5 | 0 | **稀疏** |
| 跌倒/起身（新增标签） | 10 | 5 | 1 | 0 | 稀疏 |
| 容错 | 10 | 1 | 8 | 0 | **稀疏** |
| 人机交互 | 9 | 7 | 2 | 0 | **最稀疏** |

（"轮足"一列只计标题或摘要明确写出轮足的论文，不含四足滑板和轮滑类。另有 58 篇平台只写"legged"，未细分。）

**结论**：
- **最拥挤**：人形的技能/模仿、移动操作和感知运动。会议相关论文中人形占 49%（190/385），四足占 29%（112），轮足只占 2%（9 篇）。
- **最稀疏**：人机交互、容错、跌倒/起身、学习型状态估计（各 9–12 篇），其次是能效/热和跨形态（17–18 篇）。
- **对本课题最关键的空白**：**轮足 × sim2real/辨识、轮足 × 学习型状态估计、轮足 × 安全/约束、轮足 × 世界模型，在 2025–26 年会议中都是 0 篇**。最接近的是 MUJICA（ICRA26，Go2-W，训练时加入了直流电机约束模型）和 AJAC（RSS26，轮足四足的执行器电压约束，不是学习方法）。这一结果支持 PACE 主方案"方向较空"的判断。能效方向在轮足上已有 2 篇（IROS25 能耗预测加残差 RL；ICRA26 DeepSkate，四足穿轮滑），不再是空白。

### 3.2 轮足 Go2 / Go2-W 直接相关
- 明确用 **Go2-W**：MUJICA（ICRA26）。只此 1 篇。
- 明确用 **Go2**（会议）：DDAT（RSS25）、RoboGauge/MoE（RSS26）、一阶基于模型 RL（CoRL25）、无冲突能耗最小化（CoRL25）、Risk-Aware Bandit（ICRA26）、Safe WB Loco-Manip（ICRA26）、Knowledge-Based Locomotion（ICRA26）、Triple-Zero 协同导航（ICRA26）、FR-Net（IROS25/RA-L）。摘要只写"quadruped"的论文没有计入。
- 改装 Go1 的轮足：IROS25 两篇（Wheel-Legged Quadruped Robust Locomotion；Energy-Efficient Omnidirectional）。

### 3.3 轮足及相关论文完整清单（含期刊初筛和非学习类；"学习?=否"的仅供参考）

| # | 标题 | 出处 | 平台 | 学习? | 标签 |
|---|---|---|---|---|---|
| 1 | Discrete-Time Hybrid Automata Learning: Legged Locomotion Meets Skateboarding | RSS25 | 滑板/轮滑/四足 | 是 | 敏捷动作 |
| 2 | HUSKY: Humanoid Skateboarding System via Physics-Aware Whole-Body Control | RSS26 | 滑板/轮滑/人形 | 是 | 敏捷动作 |
| 3 | Multi-Loco: Unifying Multi-Embodiment Legged Locomotion via Reinforcement Learning Augmented Diffusion | CoRL25 | 轮足/双足 | 是 | 跨形态、学习+MPC |
| 4 | S2M-Trek: From Single to Multi-Sphere Transport via Per-Frame Deep Sets on a Wheel-Legged Robot | CoRL26 | 轮足 | 是 | 移动操作 |
| 5 | Phase-Aware Policy Learning for Skateboard Riding of Quadruped Robots Via Feature-Wise Linear Modulation | ICRA26 | 滑板/轮滑/四足 | 是 | 敏捷动作 |
| 6 | Reinforcement Learning for Stair Locomotion of a Wheeled Bipedal Robot with Contact-Guided Behavior Cloning | ICRA26 | 轮足/双足 | 是 | 感知运动、导航/VLN |
| 7 | Efficient and Versatile Quadrupedal Skating: Optimal Co-Design Via Reinforcement Learning and Bayesian Optimization | ICRA26 | 滑板/轮滑/四足 | 是 | 敏捷动作、能效/热 |
| 8 | MUJICA: Multi-Skill Unified Joint Integration of Control Architecture for Wheeled-Legged Robots | ICRA26 | 轮足/四足/**Go2-W** | 是 | 技能/模仿 |
| 9 | MemClaw-RAG: Memory-Driven Navigation and Adaptive Locomotion for Wheeled-Legged Robots in Dynamic Environments | ICRA26 | 轮足 | 是 | 适应、导航/VLN |
| 10 | DeepSkate: Reinforcement Learning of a Robust Controller for Energy Efficient Quadruped Skating | ICRA26 | 轮足/四足 | 是 | 敏捷动作、能效/热 |
| 11 | Teaching to Individual Needs: Bidirectional Teacher-Student Learning for Wheeled-Legged Locomotion | ICRA26 | 轮足 | 是 | 训练算法 |
| 12 | Learning Robust and Flexible Locomotion of Wheel-Legged Quadruped Robots in Complex Terrains | IROS25 | 轮足/四足 | 是 | 导航/VLN |
| 13 | Energy-Efficient Omnidirectional Locomotion for Wheeled Quadrupeds Via Predictive Energy-Aware Nominal Gait Selection | IROS25 | 轮足/四足 | 是 | 能效/热、学习+MPC |
| 14 | Learning Whole-Body Loco-Manipulation for Omni-Directional Task Space Pose Tracking With a Wheeled-Quadrupedal-Manipulator | RA-L | 轮足/四足 | 是 | 移动操作 |
| 15 | A Motion Control Algorithm of Wheel-Legged Robot via Adaptive Dynamic Programming and Data-Driven Value Iteration | RA-L | 轮足 | 是 | 适应 |
| 16 | Robust Fall Recovery for Armless Bipedal-Wheeled Robots via Force-Guided Learning | RA-L | 轮足/双足 | 是 | 跌倒/起身 |
| 17 | Mobile Pedipulation for Object Sliding via Hierarchical Control on a Wheeled Bipedal Robot | RA-L | 轮足/双足 | 是 | 移动操作 |
| 18 | Agile Wheel-Bipedal Loco-Manipulation With Active Force Rejection | RA-L | 轮足/双足 | 是 | 敏捷动作、移动操作 |
| 19 | Unleashing the Agility of Wheeled-Legged Robots for High-Dynamic Reflexive Obstacle Evasion | RA-L | 轮足 | 是 | 导航/VLN、敏捷动作 |
| 20 | YMSkater: Learning Skating Locomotion via Model-Guided Reinforcement Learning | RA-L | 滑板/轮滑 | 是 | 敏捷动作 |
| 21 | RAIWAY: A Large-Wheeled Bipedal Robot With Contact-Informed Blind Locomotion | RA-L | 轮足/双足 | 是 | 其他 |
| 22 | Grounding Discrete-Time Joint-Level Acceleration Bounds in Voltage-Constrained Actuation | RSS26 | 轮足/四足 | 否（模型/设计） | — |
| 23 | OTTO: Dynamics and Control of Wheeled Bipedal Jumping Robot | ICRA26 | 轮足/双足 | 否（模型/设计） | — |
| 24 | Path Tracking Control for a Transformable Wheel-Legged Robot Using Model Predictive Control | ICRA26 | 轮足 | 否（模型/设计） | — |
| 25 | Ringbot Quad: A Monocycle Robot with Four Legs for Versatile Wheel-Leg Transformable Locomotion | ICRA26 | 轮足/四足 | 否（模型/设计） | — |
| 26 | WiXus: A Wheeled-Legged Robot with Wire-Driven Environmental Utilizing to Integrate Mobility and Manipulation | ICRA26 | 轮足 | 否（模型/设计） | — |
| 27 | Design and Implementation of an Angle-Bisecting Foot Mechanism for a Leg-Wheel Transformable Robot | ICRA26 | 轮足 | 否（模型/设计） | — |
| 28 | Proprioceptive Contact State and Contact Point Estimation for a Leg-Wheel Transformable Robot | ICRA26 | 轮足 | 否（模型/设计） | — |
| 29 | A Novel Paddling Propulsion Gait for a Wheel-Legged Robot on Sand Terrain | ICRA26 | 轮足 | 否（模型/设计） | — |
| 30 | SPIRA: Small Gas Pipeline Inspection Robot with Spiral Leg-Wheel Mechanism and Single Bending Joint | ICRA26/RA-L | 轮足/四足 | 否（模型/设计） | — |
| 31 | Whole-Body Balance Control of Wheeled-Bipedal Robots for Perception-Less Terrain Adaptation | ICRA26 | 轮足/双足 | 否（模型/设计） | — |
| 32 | Bi-Level Optimization for Closed-Loop Model Reference Adaptive Vibration Control in Wheeled-Legged Multi-Mode Vehicles (I) | IROS25 | 轮足/四足 | 否（模型/设计） | — |
| 33 | Relative Tilt Suppression of a Carried Object Using Base Link Angle Adjustment on a Quadruped-Wheeled Robot | IROS25 | 轮足/四足 | 否（模型/设计） | — |
| 34 | A Wearable Centaur Robot with Wheel-Legged Transformation for Enhanced Load-Carrying Assistance | IROS25 | 轮足 | 否（模型/设计） | — |
| 35 | Somersaulting Jump of Wheeled Bipedal Robot: A Comprehensive Planning and Control Strategy | IROS25/RA-L | 轮足/双足 | 否（模型/设计） | — |
| 36 | Motion Control of a Hybrid Self-Reconfigurable Wheel-Legged Dual-Arm Robot | IROS25 | 轮足/双足 | 否（模型/设计） | — |
| 37 | Lywal-X: A Novel Wheel-Claw Quadruped Robot | IROS25 | 四足 | 否（模型/设计） | — |
| 38 | Design and Control of SKATER: A Wheeled-Bipedal Robot with High-Speed Turning Robustness and Terrain Adaptability (I) | IROS25 | 轮足/双足 | 否（模型/设计） | — |
| 39 | From Concept to Field Trials: Design, Analysis, and Evaluation of a Novel Quadruped Robot with Deformable Wheel-Foot Structure | IROS25/T-RO | 轮足/四足 | 否（模型/设计） | — |
| 40 | Whole-Body Stabilization of Wheeled Bipedal Robots Via Decoupled Control of Wheels and Legs | IROS25 | 轮足/双足 | 否（模型/设计） | — |
| 41 | Probabilistic Path Planning for Wheel-Legged Rover in Dense Environment Based on Extended MDP and Configuration Topology Analysis | T-RO | 轮足 | 否（模型/设计） | — |
| 42 | Whole-Body Bilateral Teleoperation With Multistage Object Parameter Estimation for Wheeled Humanoid Locomanipulation | T-RO | 轮足/人形 | 否（模型/设计） | — |
| 43 | Wheel-Legged SLAM: Indoor LiDAR-Inertial SLAM Integrating Kinematic Model of Wheel-Legged Robots | RA-L | 轮足 | 否（模型/设计） | — |
| 44 | Integrated Modeling and Control Optimization of Biped Wheel-Legged Robot | RA-L | 轮足/双足 | 否（模型/设计） | — |
| 45 | BiTSpoke: A Leg-Wheel Robot With Single-Motor Driven Actively-Transformable Spoke Wheels | RA-L | 轮足 | 否（模型/设计） | — |
| 46 | TWLHex: A Biologically Inspired Multi-Morphology Transformable Wheel-Legged Hexapod | RA-L | 轮足/多足 | 否（模型/设计） | — |
| 47 | Jump Planning and Airborne Attitude Control of Bipedal Wheel-Legged Robots | RA-L | 轮足/双足 | 否（模型/设计） | — |
| 48 | Automatic Adaptation to Step-Climbing in Elastically Coupled Dual Legged-Wheels | RA-L | 足式 | 否（模型/设计） | — |
| 49 | Enhanced Robust Locomotion of Wheeled-Bipedal Robot via Hierarchical Optimization and Online Wheel Position Planning | RA-L | 轮足/双足 | 否（模型/设计） | — |
| 50 | Whole-Body Impedance Coordinative Control for a Wheel-Legged Robot on Uncertain Terrain | RA-L | 轮足 | 否（模型/设计） | — |
| 51 | VectorGlide: Realizing Continuum Drive Paradigm via Integrated Contact Kino-Dynamic MPC for Wheeled Quadruped Robots | RA-L | 轮足/四足 | 否（模型/设计） | — |
| 52 | A Reconfigured Wheel-Legged Robot for Enhanced Steering and Adaptability | RA-L | 轮足 | 否（模型/设计） | — |
| 53 | Longitudinal Dynamics Modeling and Control of a Wheel-Legged Robot With Tilting Rotor Assistance | RA-L | 轮足 | 否（模型/设计） | — |
| 54 | Quadrupedal Robot With Leg-and-Wheel Transformable Origami Mechanism | RA-L | 四足 | 否（模型/设计） | — |
| 55 | X2-N: A Transformable Wheel-Legged Humanoid Robot With Dual-Mode Locomotion and Manipulation | RA-L | 轮足/人形 | 否（模型/设计） | — |

## 4. 此前名单未覆盖、对 Go2-W 本科毕设最有潜力的 7 篇

（已和 options_overview.CN.md 及第四轮名单对照，以下均未出现过。）

| # | 论文 | 出处 | 一句话理由 |
|---|---|---|---|
| 1 | MUJICA: Multi-Skill Unified Joint Integration of Control Architecture for Wheeled-Legged Robots | ICRA26 | 普查中唯一明确在 **Go2-W** 上做实验的论文。用单一本体感知策略加技能选择器完成全向移动、爬高台和摔倒恢复，训练时建模直流电机约束。可直接作为基线或复现底座 |
| 2 | Teaching to Individual Needs: Bidirectional Teacher-Student Learning for Wheeled-Legged Locomotion | ICRA26 | 指出教师—学生框架在轮足上的特有问题：多模态动作被平均、教师动作难以模仿。改动只在训练端（MDN 输出头和可模仿性奖励），实机风险低，适合本科做"复现 + 消融" |
| 3 | Energy-Efficient Omnidirectional Locomotion for Wheeled Quadrupeds via Predictive Energy-Aware Nominal Gait Selection | IROS25 | 改装 Go1 的轮足平台，用功率预测网络选名义步态，再由残差 RL 微调，能耗最多降 34%。属于学习+控制，且是稀疏的能效主题，问题直观 |
| 4 | Non-conflicting Energy Minimization in Reinforcement Learning based Robot Control | CoRL25 | 免调参的梯度投影能耗最小化，已在 Go2 上完成 sim2real，摘要称只需很少代码改动，有代码。可与第 3 篇组合，在 Go2-W 上比较"奖励加权"和"梯度投影"两种做法 |
| 5 | Toward Reliable Sim-to-Real Predictability for MoE-based Robust Quadrupedal Locomotion（RoboGauge） | RSS26 | 在 Go2 上用 sim-to-sim 指标预测策略的实机可迁移性，可减少实机试错。和 PACE 主方案（仿真—真机差距）互补，可作为评估工具 |
| 6 | Risk-Aware Reinforcement Learning with Bandit-Based Adaptation for Quadrupedal Locomotion | ICRA26 | 训练一族 CVaR 风险条件策略，部署时用多臂老虎机在约 2 分钟内选出合适档位，不需要特权信息，Go2 实机。是比在线改权重（TEMPO 类）更安全的"部署时适应"替代 |
| 7 | Grounding Discrete-Time Joint-Level Acceleration Bounds in Voltage-Constrained Actuation（AJAC） | RSS26 | 在轮足四足实机上把关节加速度界限建立在电机电压约束上。本身不是学习方法，但可作为 RL 动作约束或仿真执行器模型的物理依据，连接 sim2real 和过热两个备选方向 |

候补：Unleashing the Agility of Wheeled-Legged Robots for High-Dynamic Reflexive Obstacle Evasion（RA-L）；MemClaw-RAG（ICRA26，轮足导航加 RL 运动）；GRAM（ICRA26，四足鲁棒适应模块）；Learning Robust and Flexible Locomotion of Wheel-Legged Quadruped Robots（IROS25，仅用 IMU 和关节数据的轮足 RL）。
