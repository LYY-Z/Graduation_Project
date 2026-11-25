# 2025–2026 期刊普查：足式 / 轮足 / 人形运动控制 × 学习

日期：2026-11-25。范围：2025-01-01 至今在 Science Robotics、IJRR、IEEE T-RO、IEEE RA-L、Nature、Nature Communications、Nature Machine Intelligence 上发表的论文（含 online-first）。会议部分见 `venue_sweep_2025_2026.md`。

## 0. 方法（可复跑）

1. **全量拉取，不用关键词搜索引擎**。每本期刊都调用 Crossref `GET https://api.crossref.org/journals/{ISSN}/works?filter=from-pub-date:2025-01-01,type:journal-article&rows=1000&cursor=*&select=DOI,title,volume,issue,published,abstract,container-title,page`，翻 cursor 直到取完。每本期刊拿到的条数都等于 Crossref 报告的 `total-results`。所用 ISSN：Sci. Robot. 2470-9476、IJRR 0278-3649、T-RO 1552-3098、RA-L 2377-3766、Nature 0028-0836、Nat. Commun. 2041-1723、NMI 2522-5839。
2. **初筛 R1（平台词）**：对标题做正则 `legged|quadruped|biped|humanoid|locomot|wheel-leg|wheeled-leg|leg-wheel|walking robot|robot dog|hexapod|go2|anymal|unitree|gait`。Sci. Robot. 和 Nature 系期刊再对 Crossref 摘要跑一遍同样的正则。
3. **初筛 R2（补漏）**：
   - IJRR、T-RO、RA-L 再跑一遍标题正则 `wheel|whole-body|parkour|stair|terrain|jump|agil|foothold|footstep|contact-implicit|centroidal|loco-manip|traversab|acrobat|fall|standing`，结果逐条人工看。
   - Nature 系期刊另外人工通读所有标题含 `robot|locomot|legged|humanoid|quadruped|embodied|exoskeleton|prosthe` 的条目，再补跑一遍 `agil|whole-body|sim-to-real|reinforcement learning|terrain|walking|jump|wheel|biped|parkour` 等。
   - Sci. Robot. R1 没有命中的 182 个标题全部人工通读。
4. **摘要**：IEEE 期刊在 Crossref 中没有摘要，OpenAlex 当天返回 429（免费额度用完）。改用 Semantic Scholar `POST /graph/v1/paper/batch`（`fields=title,abstract`）按 DOI 批量取回，303 篇中 289 篇有摘要。
5. **收录口径**：
   - 平台：足式、轮足或人形。运动、移动操作、导航，以及服务于运动的估计都算。
   - 方法：必须有学习成分，包括 RL、模仿、学习的模型或估计器、大模型，以及学习与 MPC/WBC 的组合。
   - 不收：外骨骼和假肢、人体步态、软体/蛇形/游动、纯机构设计。
   - 纯模型方法的轮足论文不进主表，单列在 §3.3。
6. **代码列**："有"表示摘要中明确声明开源，或已有核查报告确认；其余标"未查"。"未查"**不代表没有代码**。
7. **标签**：人工按摘要打标，可多选。

## 1. 覆盖记录

| 期刊 | 检索方式 / 查询式 | 拉取总数（2025-01 起） | R1 命中 | R2 补充人工看 | 最终收录 | 备注 |
|---|---|---|---|---|---|---|
| Science Robotics | Crossref ISSN 2470-9476 全量 | 237（含社论、Focus、书评） | 55（标题+摘要） | 其余 182 个标题全部通读 | 15 | 摘要覆盖 234/237。另有 2 篇轮式相邻工作列在 §3.3 |
| IJRR | Crossref ISSN 0278-3649 全量 | 240 | 14 | 13 | 5 | 摘要覆盖 236/240 |
| IEEE T-RO | Crossref ISSN 1552-3098 全量 | 646 | 36 | 约 30 | 10 | Crossref 无摘要，用 S2 补齐。日期只精确到年 |
| IEEE RA-L | Crossref ISSN 2377-3766 全量 | 3847（含卷 12(1) 的 online-first） | 241 | 约 150 | 116 | Crossref 无摘要，用 S2 补齐 |
| Nature | Crossref ISSN 0028-0836 全量 | 8665（含新闻和评论） | 17 | 57 个 robot 标题 | 1（学习成分待核） | Crossref 摘要只覆盖 942 篇，以标题为主 |
| Nature Communications | Crossref ISSN 2041-1723 全量 | 24325 | 73（多为神经科学） | 148 个 robot 标题 | 3 | 摘要覆盖 8865 篇 |
| Nature Machine Intelligence | Crossref ISSN 2522-5839 全量 | 372 | 4 | 30 个 robot 标题 | 1 | — |
| **合计** | | **38332** | | | **151** | 年份分布：2025 年 42 篇，2026 年 105 篇，2027 年卷期的 online-first 4 篇 |

**无法访问或局限**（如实说明）：
- OpenAlex 当天 429，没用上。
- S2 有 14 篇没返回摘要，只能按标题判定，例如 ALORE、Humanoid-DART、Sci. Robot. 的 UMV。
- 最后一批 S2 请求也被 429，因此 Nature 马拉松四足、FLAIR 只看到了摘要前段。
- Nature 和 Nat. Commun. 只能主要依靠标题，标题里没有 robot、legged 等词的论文可能漏掉。

## 2. 相关论文总表（151 篇；按期刊、时间排序）

平台列中"足式"表示摘要只写了 legged。最后一列是 DOI。

| 标题 | 期刊 卷(期), 年 | 平台 | 主题标签 | 代码 | 备注 | DOI |
|---|---|---|---|---|---|---|
| Humanoid robot learning of complex behaviors with LLMs | Sci. Robot. 10(98), 2025 | 人形 | VLA/大模型 | 未查 | Focus 短评 | 10.1126/scirobotics.adv4627 |
| High-speed control and navigation for quadrupedal robots on complex and discrete terrain | Sci. Robot. 10(102), 2025 | 四足(ANYmal) | 学习+MPC/WBC、感知运动、敏捷动作、导航/VLN | 未查 | 采样落脚规划+学习跟踪器 | 10.1126/scirobotics.ads6192 |
| Learning coordinated badminton skills for legged manipulators | Sci. Robot. 10(102), 2025 | 四足+臂(ANYmal) | 移动操作、感知运动、安全/约束 | 未查 | 羽毛球；约束RL+感知噪声模型 | 10.1126/scirobotics.adu3922 |
| Learning contact-rich whole-body manipulation with example-guided reinforcement learning | Sci. Robot. 10(105), 2025 | 全身(平台未核) | 移动操作、技能/模仿 | 未查 | 示例引导RL全身接触操作 | 10.1126/scirobotics.ads6790 |
| Attention-based map encoding for learning generalized legged locomotion | Sci. Robot. 10(105), 2025 | 四足(ANYmal) | 感知运动、敏捷动作 | 未查 | 注意力地图编码 | 10.1126/scirobotics.adv3604 |
| Resilient odometry via hierarchical adaptation | Sci. Robot. 10(109), 2025 | 多平台含足式 | 状态估计 | 未查 | Super Odometry，学习惯导 | 10.1126/scirobotics.adv1818 |
| Agile perceptive multiskill locomotion for quadrupedal robots in the wild | Sci. Robot. 11(116), 2026 | 四足 | 感知运动、敏捷动作、技能/模仿、学习+MPC/WBC | 未查 | APT-RL，TO生成数据预训练 | 10.1126/scirobotics.adz7397 |
| Advances, challenges, and opportunities for legged robots | Sci. Robot. 11(116), 2026 | 足式 | 其他 | 未查 | 综述 | 10.1126/scirobotics.aee0787 |
| ZEST: Zero-shot embodied skill transfer for athletic robot control | Sci. Robot. 11(117), 2026 | 人形+四足 | 技能/模仿、敏捷动作 | 未查 | ZEST 零样本动作迁移 | 10.1126/scirobotics.aec7695 |
| SONIC: Supersizing motion tracking for natural humanoid whole-body control | Sci. Robot. 11(117), 2026 | 人形 | 技能/模仿、训练算法 | 未查 | SONIC 规模化动作跟踪 | 10.1126/scirobotics.aed4592 |
| Learning vision-driven reactive soccer skills for humanoid robots | Sci. Robot. 11(117), 2026 | 人形 | 感知运动、技能/模仿 | 未查 | 视觉反应式足球，AMP | 10.1126/scirobotics.aed1152 |
| Evolution of humanoid locomotion control | Sci. Robot. 11(117), 2026 | 人形 | 其他 | 未查 | 综述 | 10.1126/scirobotics.aed3973 |
| BeyondMimic: From motion tracking to versatile humanoid control via guided diffusion | Sci. Robot. 11(117), 2026 | 人形 | 技能/模仿、敏捷动作 | 未查 | BeyondMimic 引导扩散 | 10.1126/scirobotics.adx8924 |
| How robot dogs see the unseeable: Improving visual interpretability via peering for exploratory robots | Sci. Robot. 11(118), 2026 | 四足(机器狗) | VLA/大模型、其他 | 未查 | peering 合成孔径+多模态大模型 | 10.1126/scirobotics.aed8577 |
| Bridging vision-language reasoning and learned control for legged navigation in the wild | Sci. Robot. 11(120), 2026 | 四足(ANYmal) | 导航/VLN、VLA/大模型、感知运动 | 未查 | ROAM：VLM+RL 千米级导航 | 10.1126/scirobotics.aee1549 |
| Learning-based legged locomotion: State of the art and future perspectives | IJRR 44(8), 2025 | 足式 | 其他 | 未查 | 学习型足式运动综述 | 10.1177/02783649241312698 |
| Growable and interpretable neural control with online continual learning for autonomous lifelong locomotion learning machines | IJRR 44(13), 2025 | 多足 | 训练算法、适应 | 未查 | GOLLUM 持续学习 | 10.1177/02783649251336385 |
| Parkour in the wild: Learning a general and extensible agile locomotion policy using multi-expert distillation and RL fine-tuning | IJRR online, 2026 | 四足(ANYmal) | 感知运动、敏捷动作、训练算法 | 未查 | 多专家蒸馏+RL微调跑酷 | 10.1177/02783649261455067 |
| Towards bridging the gap: Systematic sim-to-real transfer for diverse legged robots | IJRR online, 2026 | 多种足式 | sim2real/辨识、能效/热 | 有 | 含执行器能量损耗的系统 sim2real | 10.1177/02783649261459628 |
| GrandTour: A legged robotics dataset in the wild for multi-modal perception and state estimation | IJRR online, 2026 | 四足(ANYmal-D) | 状态估计 | 未查 | GrandTour 数据集 | 10.1177/02783649261480737 |
| Spatio-Temporal Motion Retargeting for Quadruped Robots | T-RO 41, 2025 | 四足 | 技能/模仿 | 未查 | 时空运动重定向 | 10.1109/tro.2025.3600123 |
| MARG: MAstering Risky Gap Terrains for Legged Robots With Elevation Mapping | T-RO 41, 2025 | 四足 | 感知运动、安全/约束 | 未查 | MARG 危险缝隙 | 10.1109/tro.2025.3619041 |
| One Filter to Deploy Them All: Robust Safety for Quadrupedal Navigation in Unknown Environments | T-RO 42, 2026 | 四足(Go1) | 安全/约束、导航/VLN | 未查 | 通用安全滤波 | 10.1109/tro.2025.3644957 |
| Traversability-Aware Legged Navigation by Learning From Real-World Visual Data | T-RO 42, 2026 | 四足 | 导航/VLN、感知运动、能效/热 | 未查 | 真实视觉数据学可通行性+能耗 | 10.1109/tro.2025.3645885 |
| DreamWaQ++: Obstacle-Aware Quadrupedal Locomotion With Resilient Multimodal Reinforcement Learning | T-RO 42, 2026 | 四足 | 感知运动、适应 | 未查 | DreamWaQ++ | 10.1109/tro.2026.3653774 |
| Safe and Efficient Quadrupedal Locomotion With a Chambolle–Pock Whole-Body Controller | T-RO 42, 2026 | 四足 | 学习+MPC/WBC、安全/约束、训练算法 | 未查 | Chambolle-Pock QP WBC 与 RL 结合 | 10.1109/tro.2026.3653775 |
| Pushing Physical Limits and Uncovering Motion Templates of Spine-Based Quadruped Locomotion via Reinforcement Learning | T-RO 42, 2026 | 脊柱四足 | 敏捷动作、其他 | 未查 | RL 推极限速度 | 10.1109/tro.2026.3697171 |
| SMASH: Mastering Scalable Whole-Body Skills for Humanoid Ping-Pong With Egocentric Vision | T-RO 42, 2026 | 人形 | 移动操作、感知运动、敏捷动作 | 未查 | SMASH 乒乓 | 10.1109/tro.2026.3734282 |
| Agile and Generalized Legged Locomotion via Attention-Based Neural Map Encoding | T-RO 42, 2026 | 四足 | 感知运动、敏捷动作 | 未查 | 神经地图编码(期刊版) | 10.1109/tro.2026.3742243 |
| ALORE: Autonomous Large-Object Rearrangement with a Legged Manipulator | T-RO online, 2026 | 四足+臂 | 移动操作 | 未查 | ALORE(仅标题) | 10.1109/tro.2026.3747611 |
| Imitation-Enhanced Reinforcement Learning With Privileged Smooth Transition for Hexapod Locomotion | RA-L 10(1), 2025 | 六足 | 技能/模仿、训练算法 | 未查 |  | 10.1109/lra.2024.3497754 |
| Robust Locomotion Policy With Adaptive Lipschitz Constraint for Legged Robots | RA-L 10(1), 2025 | 足式 | 安全/约束、训练算法 | 未查 | 自适应 Lipschitz | 10.1109/lra.2024.3506278 |
| Variable-Frequency Model Learning and Predictive Control for Jumping Maneuvers on Legged Robots | RA-L 10(2), 2025 | 四足(A1) | 学习+MPC/WBC、世界模型/基于模型、敏捷动作 | 未查 | 变频模型学习+MPC 跳跃 | 10.1109/lra.2024.3519864 |
| Non-Gaited Legged Locomotion With Monte-Carlo Tree Search and Supervised Learning | RA-L 10(2), 2025 | 足式 | 学习+MPC/WBC、训练算法 | 未查 | MCTS+监督学习非周期步态 | 10.1109/lra.2024.3519908 |
| Reinforcement Learning of Contact Preferability in Multi-Contact Locomotion Planning for Humanoids | RA-L 10(2), 2025 | 人形 | 学习+MPC/WBC | 未查 | RL 学接触偏好+优化 | 10.1109/lra.2024.3524890 |
| Learning Whole-Body Loco-Manipulation for Omni-Directional Task Space Pose Tracking With a Wheeled-Quadrupedal-Manipulator | RA-L 10(2), 2025 | 轮足四足+臂，**轮足** | 移动操作 | 未查 | 6D 末端位姿 RL | 10.1109/lra.2024.3519856 |
| See-Touch-Predict: Active Exploration and Online Perception of Terrain Physics With Legged Robots | RA-L 10(4), 2025 | 足式 | 感知运动、适应 | 未查 | 主动探测地面物理 | 10.1109/lra.2025.3541432 |
| Fast Autolearning for Multimodal Walking in Humanoid Robots With Variability of Experience | RA-L 10(4), 2025 | 人形 | 适应、训练算法 | 未查 |  | 10.1109/lra.2025.3546168 |
| RoboDuet: Learning a Cooperative Policy for Whole-Body Legged Loco-Manipulation | RA-L 10(5), 2025 | 四足+臂 | 移动操作 | 未查 | RoboDuet | 10.1109/lra.2025.3551230 |
| Physics-Informed Neural Networks With Unscented Kalman Filter for Sensorless Joint Torque Estimation in Humanoid Robots | RA-L 10(6), 2025 | 人形 | 状态估计、sim2real/辨识 | 未查 | PINN+UKF 估关节力矩 | 10.1109/lra.2025.3562792 |
| FR-Net: Learning Robust Quadrupedal Fall Recovery on Challenging Terrains through Mass-Contact Prediction | RA-L 10(7), 2025 | 四足(Go2) | 容错/恢复 | 未查 | FR-Net 摔倒恢复 | 10.1109/lra.2025.3569117 |
| DSE: A Denoising State Estimator for RL-Based Bipedal Robot Locomotion | RA-L 10(7), 2025 | 双足 | 状态估计 | 未查 | 去噪状态估计 | 10.1109/lra.2025.3569124 |
| ALARM: Safe Reinforcement Learning With Reliable Mimicry for Robust Legged Locomotion | RA-L 10(7), 2025 | 足式 | 安全/约束、技能/模仿 | 未查 | ALARM 安全RL | 10.1109/lra.2025.3572427 |
| FT-CPG: Learning Central Pattern Generators for Fault-Tolerant Quadruped Locomotion Under Multi-Joint Failures | RA-L 10(7), 2025 | 四足(Go1) | 容错/恢复 | 未查 | FT-CPG 多关节故障 | 10.1109/lra.2025.3572772 |
| Whole-Body Constrained Learning for Legged Locomotion via Hierarchical Optimization | RA-L 10(7), 2025 | 足式 | 安全/约束、学习+MPC/WBC | 未查 | 分层优化约束学习 | 10.1109/lra.2025.3577526 |
| VR-Robo: A Real-to-Sim-to-Real Framework for Visual Robot Navigation and Locomotion | RA-L 10(8), 2025 | 四足(Go2) | 感知运动、导航/VLN、sim2real/辨识 | 未查 | VR-Robo 3DGS | 10.1109/lra.2025.3575648 |
| EMOTION: Expressive Motion Sequence Generation for Humanoid Robots With In-Context Learning | RA-L 10(8), 2025 | 人形 | VLA/大模型、人机交互 | 未查 | 表情动作，LLM 上下文学习 | 10.1109/lra.2025.3575983 |
| TACT: Humanoid Whole-Body Contact Manipulation Through Deep Imitation Learning With Tactile Modality | RA-L 10(8), 2025 | 人形 | 移动操作、技能/模仿 | 未查 | TACT 触觉模仿 | 10.1109/lra.2025.3580329 |
| OmniNet: Omnidirectional Jumping Neural Network With Height-Awareness for Quadrupedal Robots | RA-L 10(8), 2025 | 四足 | 敏捷动作 | 未查 | OmniNet 全向跳跃 | 10.1109/lra.2025.3580993 |
| A Modular Residual Learning Framework to Enhance Model-Based Approach for Robust Locomotion | RA-L 10(9), 2025 | 足式 | 学习+MPC/WBC | 未查 | 模块化残差学习 | 10.1109/lra.2025.3592067 |
| Learn to Teach: Sample-Efficient Privileged Learning for Humanoid Locomotion Over Real-World Uneven Terrain | RA-L 10(9), 2025 | 人形(Digit) | 训练算法、适应 | 未查 | Learn to Teach | 10.1109/lra.2025.3592131 |
| Enhancing Robustness of Locomotion Policy for Quadrupedal Robot With Deep Disturbance Observer | RA-L 10(9), 2025 | 四足 | 适应、学习+MPC/WBC | 未查 | 深度扰动观测器 | 10.1109/lra.2025.3595037 |
| Learning Autonomous and Safe Quadruped Traversal of Complex Terrains Using Multi-Layer Elevation Maps | RA-L 10(10), 2025 | 四足 | 感知运动、安全/约束、导航/VLN | 未查 | 多层高程图 | 10.1109/lra.2025.3595814 |
| Fault Joint Detection and Adaptive Fault-Tolerant Control of Legged Robots Under Joint Partial Failures | RA-L 10(10), 2025 | 四足(A1) | 容错/恢复 | 有 | 关节部分故障检测 | 10.1109/lra.2025.3598620 |
| Learning Multi-Stage Pick-and-Place With a Legged Mobile Manipulator | RA-L 10(11), 2025 | 四足+臂 | 移动操作 | 未查 |  | 10.1109/lra.2025.3608425 |
| RENet: Fault-Tolerant Motion Control for Quadruped Robots via Redundant Estimator Networks Under Visual Collapse | RA-L 10(11), 2025 | 四足 | 感知运动、容错/恢复 | 未查 | RENet 视觉失效 | 10.1109/lra.2025.3608633 |
| PPF: Pre-Training and Preservative Fine-Tuning of Humanoid Locomotion via Model-Assumption-Based Regularization | RA-L 10(11), 2025 | 人形(Digit) | 学习+MPC/WBC、技能/模仿、训练算法 | 未查 | PPF 模仿模型控制器 | 10.1109/lra.2025.3608637 |
| Opt2Skill: Imitating Dynamically-Feasible Whole-Body Trajectories for Versatile Humanoid Loco-Manipulation | RA-L 10(11), 2025 | 人形 | 技能/模仿、学习+MPC/WBC、移动操作 | 未查 | Opt2Skill | 10.1109/lra.2025.3620620 |
| Learning Humanoid Arm Motion via Centroidal Momentum Regularized Multi-Agent Reinforcement Learning | RA-L 10(11), 2025 | 人形 | 训练算法、其他 | 未查 | 质心动量正则 MARL 摆臂 | 10.1109/lra.2025.3614078 |
| Learning Quadrupedal Locomotion for a Heavy Hydraulic Robot Using an Actuator Model | RA-L 10(12), 2025 | 液压四足 | sim2real/辨识 | 未查 | 执行器模型 | 10.1109/lra.2025.3623024 |
| CROSSER: Learning Generalizable Humanoid Locomotion Through Inverse Dynamics-Guided Cross-Simulator Adaptation | RA-L 10(12), 2025 | 人形 | sim2real/辨识 | 未查 | CROSSER 跨仿真器 | 10.1109/lra.2025.3630544 |
| MULE - Multi-Terrain and Unknown Load Adaptation for Effective Quadrupedal Locomotion | RA-L 11(1), 2026 | 四足(Go1) | 适应 | 未查 | MULE 负载+地形 | 10.1109/lra.2025.3632081 |
| MLM: Learning Multi-Task Loco-Manipulation Whole-Body Control for Quadruped Robot With Arm | RA-L 11(1), 2026 | 四足+臂(Go2) | 移动操作 | 未查 | MLM | 10.1109/lra.2025.3632087 |
| Primal-Dual iLQR for GPU-Accelerated Learning and Control in Legged Robots | RA-L 11(1), 2026 | 足式 | 学习+MPC/WBC、训练算法 | 未查 | GPU 原对偶 iLQR | 10.1109/lra.2025.3632610 |
| A Lightweight Physics-Informed Neural Network for Sim-to-Real of Biped Robot | RA-L 11(1), 2026 | 双足(BRUCE) | sim2real/辨识 | 未查 | 轻量 PINN sim2real | 10.1109/lra.2025.3632659 |
| VOCALoco: Viability-Optimized Cost-Aware Adaptive Locomotion | RA-L 11(2), 2026 | 足式 | 安全/约束、感知运动 | 未查 | VOCALoco 可行性 | 10.1109/lra.2025.3632604 |
| PPL: Point Cloud Supervised Proprioceptive Locomotion Reinforcement Learning for Legged Robots in Crawl Spaces | RA-L 11(2), 2026 | 足式 | 感知运动 | 未查 | PPL 爬行空间 | 10.1109/lra.2025.3643303 |
| Adaptive Legged Locomotion via Online Learning for Model Predictive Control | RA-L 11(2), 2026 | 四足 | 学习+MPC/WBC、适应、世界模型/基于模型 | 未查 | 在线学习残差动力学+MPC | 10.1109/lra.2025.3644161 |
| MILD: Tractable Terrain Modeling for Learning Improved Bipedal Locomotion on Deformable Surfaces | RA-L 11(2), 2026 | 双足 | sim2real/辨识、适应 | 未查 | MILD 可变形地面 | 10.1109/lra.2025.3645520 |
| Transformer Observer-Based Contact Force Estimation for Quadruped Manipulators With Model Uncertainties | RA-L 11(2), 2026 | 四足+臂 | 状态估计、移动操作 | 未查 | Transformer 接触力观测 | 10.1109/lra.2025.3645652 |
| Unleashing Humanoid Reaching Potential via Real-World-Ready Skill Space | RA-L 11(2), 2026 | 人形 | 移动操作、技能/模仿 | 未查 | 技能空间伸够 | 10.1109/lra.2025.3645662 |
| DoublyAware: Dual Planning and Policy Awareness for Temporal Difference Learning in Humanoid Locomotion | RA-L 11(2), 2026 | 人形(H1) | 世界模型/基于模型、训练算法 | 未查 | DoublyAware MBRL | 10.1109/lra.2025.3648611 |
| STATE-NAV: Stability-Aware Traversability Estimation for Bipedal Navigation on Rough Terrain | RA-L 11(2), 2026 | 双足 | 导航/VLN、安全/约束 | 未查 | STATE-NAV | 10.1109/lra.2025.3648502 |
| START: Traversing Sparse Footholds With Terrain Reconstruction | RA-L 11(2), 2026 | 四足 | 感知运动、敏捷动作 | 未查 | START 稀疏落脚 | 10.1109/lra.2025.3645649 |
| Human-Inspired Adaptive Gait Learning for Humanoids Locomotion | RA-L 11(3), 2026 | 人形 | 技能/模仿、能效/热 | 未查 |  | 10.1109/lra.2026.3653300 |
| Gait-Adaptive Perceptive Humanoid Locomotion With Real-Time Under-Base Terrain Reconstruction | RA-L 11(4), 2026 | 人形 | 感知运动 | 未查 |  | 10.1109/lra.2026.3664167 |
| Attention-Based Neural-Augmented Kalman Filter for Legged Robot State Estimation | RA-L 11(4), 2026 | 足式 | 状态估计 | 未查 | AttenNKF 打滑 | 10.1109/lra.2026.3664311 |
| Efficiently Learning Robust Torque-Based Locomotion Through Reinforcement With Model-Based Supervision | RA-L 11(4), 2026 | 双足 | 学习+MPC/WBC | 未查 | DCM+WBC 残差 RL | 10.1109/lra.2026.3664534 |
| Learning Time-Varying Joint-Motor Mapping for Precise Control of Cable-Driven Humanoid Robots Under Transmission Uncertainties | RA-L 11(4), 2026 | 绳驱人形 | sim2real/辨识 | 未查 |  | 10.1109/lra.2026.3664669 |
| Efficient Exploration for Quadruped Robots Using Graph Neural Networks With Global Attention | RA-L 11(4), 2026 | 四足 | 导航/VLN | 有 | GNN 探索 | 10.1109/lra.2026.3665062 |
| Reinforcement Learning for Robust Climbing Locomotion With Rope-Driven Legged Robot | RA-L 11(4), 2026 | 绳驱足式 | 其他 | 未查 | 攀爬 | 10.1109/lra.2026.3665321 |
| DemoHLM: From One Demonstration to Generalizable Humanoid Loco-Manipulation | RA-L 11(4), 2026 | 人形(G1) | 移动操作、技能/模仿 | 未查 | DemoHLM | 10.1109/lra.2026.3666395 |
| VPIES: Variational Privileged Information Encoder as Scaffold for Legged Locomotion Learning | RA-L 11(4), 2026 | 跨平台(G1/Go2) | 训练算法 | 未查 | VPIES 特权编码 | 10.1109/lra.2026.3666686 |
| Towards Quadrupedal Jumping and Walking for Dynamic Locomotion Using Reinforcement Learning | RA-L 11(4), 2026 | 四足(Olympus) | 敏捷动作 | 未查 |  | 10.1109/lra.2026.3668467 |
| TNavRL: Cross-Modal Transformer for Humanoid Visual Navigation | RA-L 11(5), 2026 | 人形 | 导航/VLN、感知运动 | 未查 | TNavRL | 10.1109/lra.2026.3669788 |
| MotionVL: Vision-Language Supervision for Reinforcement Learning of Humanoid Motion | RA-L 11(5), 2026 | 人形 | VLA/大模型、技能/模仿 | 未查 | MotionVL VLM 奖励 | 10.1109/lra.2026.3669793 |
| Gait-Parameterized Reinforcement Learning for a Hydraulic Quadruped Robot | RA-L 11(5), 2026 | 液压四足 | 训练算法、其他 | 未查 | 步态参数化 RL | 10.1109/lra.2026.3673991 |
| RL-Augmented MPC for Non-Gaited Legged and Hybrid Locomotion | RA-L 11(5), 2026 | 足式+混合(50-120kg)，**轮足** | 学习+MPC/WBC | 未查 | RL 给 MPC 发步态；hybrid 是否轮足待核 | 10.1109/lra.2026.3675839 |
| EFGCL: Learning Dynamic Motion Through Spotting-Inspired External Force Guided Curriculum Learning | RA-L 11(5), 2026 | 足式 | 训练算法、敏捷动作 | 未查 | EFGCL 外力课程 | 10.1109/lra.2026.3675955 |
| TerAdapt: Proprioceptive Terrain-Adaptive Locomotion via Codebook Aligned Representation Learning | RA-L 11(6), 2026 | 人形(G1) | 适应 | 未查 | TerAdapt | 10.1109/lra.2026.3682531 |
| Dynamic Legged Ball Manipulation on Rugged Terrains With Hierarchical Reinforcement Learning | RA-L 11(6), 2026 | 四足 | 移动操作、敏捷动作 | 未查 | 带球 | 10.1109/lra.2026.3682979 |
| A Motion Control Algorithm of Wheel-Legged Robot via Adaptive Dynamic Programming and Data-Driven Value Iteration | RA-L 11(6), 2026 | 轮足，**轮足** | 学习+MPC/WBC | 未查 | ADP 数据驱动值迭代 | 10.1109/lra.2026.3685946 |
| Teacher-Guided Terrain-Aware Learning for Recovery of Quadruped Robots | RA-L 11(6), 2026 | 四足 | 容错/恢复 | 未查 | 地形感知恢复 | 10.1109/lra.2026.3688056 |
| Learning Dynamic Pick-and-Place for a Legged Manipulator | RA-L 11(6), 2026 | 四足+臂 | 移动操作 | 未查 |  | 10.1109/lra.2026.3688092 |
| HiPAN: Hierarchical Posture-Adaptive Navigation for Quadruped Robots in Unstructured 3D Environments | RA-L 11(7), 2026 | 四足 | 导航/VLN、感知运动 | 未查 | HiPAN | 10.1109/lra.2026.3692054 |
| X-IONet: Cross-Platform Inertial Odometry Network for Pedestrian and Legged Robot | RA-L 11(7), 2026 | 四足(Go2) | 状态估计 | 未查 | X-IONet 学习惯导 | 10.1109/lra.2026.3692056 |
| Dynamic Policy Learning for Legged Robot With Simplified Model Pretraining and Model-Homotopy-Inspired Transfer | RA-L 11(7), 2026 | 足式 | 学习+MPC/WBC、敏捷动作、训练算法 | 未查 | 简化模型预训练+同伦迁移 | 10.1109/lra.2026.3692082 |
| UniTracker: Learning Universal Whole-Body Motion Tracker for Humanoid Robots | RA-L 11(7), 2026 | 人形(G1) | 技能/模仿 | 未查 | UniTracker | 10.1109/lra.2026.3692091 |
| CodeAct: Codebook-Guided Multi-Skill Integration for Dynamic Humanoid Whole-Body Control | RA-L 11(7), 2026 | 人形(G1) | 技能/模仿 | 未查 | CodeAct | 10.1109/lra.2026.3698369 |
| FastStair: Learning to Run up Stairs With Humanoid Robots | RA-L 11(7), 2026 | 人形 | 敏捷动作、感知运动 | 未查 | FastStair | 10.1109/lra.2026.3701575 |
| Robust Fall Recovery for Armless Bipedal-Wheeled Robots via Force-Guided Learning | RA-L 11(8), 2026 | 双足轮足，**轮足** | 容错/恢复 | 未查 | FTSR 无臂摔倒恢复 | 10.1109/lra.2026.3701481 |
| SDWM: Learning Bipedal Locomotion via a Smooth Denoising World Model Method | RA-L 11(8), 2026 | 双足 | 世界模型/基于模型、sim2real/辨识 | 未查 | SDWM 去噪世界模型 | 10.1109/lra.2026.3703226 |
| Real-to-Sim-to-Real: Learning Agile and Robust Recovery Skills With Terrain Imagination via Adversarial Imitation | RA-L 11(8), 2026 | 四足(Go2) | 容错/恢复、技能/模仿 | 未查 | 实-仿-实 恢复+地形想象 | 10.1109/lra.2026.3703264 |
| Scaling Rough Terrain Locomotion With Automatic Curriculum Reinforcement Learning | RA-L 11(8), 2026 | 四足(ANYmal) | 训练算法 | 未查 | 自动课程 | 10.1109/lra.2026.3703486 |
| DPL: Depth-Only Perceptive Humanoid Locomotion via Realistic Depth Synthesis and Cross-Attention Terrain Reconstruction | RA-L 11(8), 2026 | 人形 | 感知运动 | 未查 | DPL | 10.1109/lra.2026.3703584 |
| Collision-Free Humanoid Traversal in Cluttered Indoor Scenes | RA-L 11(8), 2026 | 人形 | 感知运动、导航/VLN | 未查 |  | 10.1109/lra.2026.3703590 |
| TCLL: Temporal-Aware Contrastive Latent Learning for Heterogeneous Legged Robots Locomotion | RA-L 11(8), 2026 | 多种足式 | 跨形态、训练算法 | 未查 | TCLL | 10.1109/lra.2026.3706930 |
| M3imic: Learning a Versatile Whole-Body Controller for Multimodal Motion Mimicking | RA-L 11(8), 2026 | 人形 | 技能/模仿 | 未查 | M3imic | 10.1109/lra.2026.3706946 |
| Vision-Assisted Bipedal Locomotion on Challenging Terrains via Terrain-Related Adversarial Motion Priors | RA-L 11(8), 2026 | 双足 | 感知运动、技能/模仿 | 未查 | 地形相关 AMP | 10.1109/lra.2026.3707326 |
| Quiet Humanoid Walking With NMPC-Informed Reinforcement Learning | RA-L 11(9), 2026 | 人形 | 学习+MPC/WBC、其他 | 未查 | NMPC 指导 RL 静音行走 | 10.1109/lra.2026.3707354 |
| Learning Humanoid Navigation From Human Data | RA-L 11(9), 2026 | 人形(G1) | 导航/VLN、技能/模仿 | 未查 | EgoNav 人类数据扩散 | 10.1109/lra.2026.3710346 |
| Learning Whole-Body Humanoid Locomotion via Motion Generation and Motion Tracking | RA-L 11(9), 2026 | 人形(G1) | 技能/模仿、感知运动 | 未查 |  | 10.1109/lra.2026.3710365 |
| CWI: Composite Humanoid Whole-Body Imitation System for Loco-Manipulation | RA-L 11(9), 2026 | 人形 | 移动操作、技能/模仿 | 未查 | CWI | 10.1109/lra.2026.3710366 |
| Pretraining in Actor-Critic Reinforcement Learning for Locomotion | RA-L 11(9), 2026 | 足式 | 训练算法 | 未查 | Actor-Critic 预训练 | 10.1109/lra.2026.3711838 |
| PUMA: Perception-Driven Unified Foothold Prior for Mobility Augmented Quadruped Parkour | RA-L 11(9), 2026 | 四足 | 感知运动、敏捷动作 | 未查 | PUMA | 10.1109/lra.2026.3711844 |
| QLIMB: End-to-End Whole-Body Control for Quadruped Loco-Manipulation and Balance on Complex Terrains | RA-L 11(9), 2026 | 小型四足+臂 | 移动操作 | 未查 | QLIMB | 10.1109/lra.2026.3712638 |
| Agile Wheel-Bipedal Loco-Manipulation With Active Force Rejection | RA-L 11(9), 2026 | 双足轮足+臂，**轮足** | 移动操作、状态估计、学习+MPC/WBC | 未查 | NN-EKF 力估计+WBC | 10.1109/lra.2026.3712640 |
| PRVR: Learning Posture Recovery for a Legged Spherical Robot Using Vector Reward | RA-L 11(9), 2026 | 腿式球形机器人 | 容错/恢复 | 未查 | PRVR | 10.1109/lra.2026.3712643 |
| CReF: Cross-Modal and Recurrent Fusion for Depth-Conditioned Humanoid Locomotion | RA-L 11(10), 2026 | 人形 | 感知运动 | 未查 | CReF | 10.1109/lra.2026.3723339 |
| RobotDancing: Residual-Action Reinforcement Learning Enables Robust Long-Horizon Humanoid Motion Tracking | RA-L 11(10), 2026 | 人形(G1/H1) | 技能/模仿 | 未查 | RobotDancing | 10.1109/lra.2026.3723309 |
| REFINE-DP: Diffusion Policy Fine-Tuning for Humanoid Loco-Manipulation via Reinforcement Learning | RA-L 11(10), 2026 | 人形 | 移动操作、技能/模仿、训练算法 | 未查 | REFINE-DP | 10.1109/lra.2026.3723742 |
| Learning-Based Kinematic Residual Compensation With Latent Regime Mixture-of-Experts for Quadruped Odometry | RA-L 11(10), 2026 | 四足(Go1/ANYmal) | 状态估计 | 未查 | MoE 运动学残差 | 10.1109/lra.2026.3728379 |
| Angular Momentum LIP Guided Reinforcement Learning With Step Duration Modulation for Dynamic Locomotion of Bipedal Robots | RA-L 11(10), 2026 | 点足双足 | 学习+MPC/WBC、敏捷动作 | 未查 | ALIP 引导 RL | 10.1109/lra.2026.3730300 |
| Extending the Speed Limit of Quadrupedal Locomotion via Refined Actuator Modeling and Adaptive Command Scheduling | RA-L 11(11), 2026 | 四足(BP2) | sim2real/辨识、敏捷动作 | 未查 | 精细执行器模型，13.2 m/s | 10.1109/lra.2026.3726387 |
| Rationality Randomization With Maximum Entropy for Robust Dynamic Obstacle Avoidance on Legged Robots | RA-L 11(11), 2026 | 足式 | 导航/VLN、安全/约束 | 未查 | 动态避障 | 10.1109/lra.2026.3728367 |
| CATR: Confidence-Aware Terrain Reconstruction for Vision-Based Quadruped Locomotion | RA-L 11(11), 2026 | 四足(Go1) | 感知运动 | 未查 | CATR | 10.1109/lra.2026.3728309 |
| PAINT: Partner-Agnostic Intent-Aware Cooperative Transport With Legged Robots | RA-L 11(11), 2026 | 四足 | 移动操作、人机交互 | 未查 | PAINT 协作搬运 | 10.1109/lra.2026.3730304 |
| Terramechanics-Aware Adaptive Quadrupedal Locomotion via Foot-Terrain Interaction Model | RA-L 11(11), 2026 | 四足(Go2) | sim2real/辨识、适应、能效/热 | 未查 | 塑性虚拟地面+步态自适应 | 10.1109/lra.2026.3732903 |
| LNP: Liquid Network Policy for Humanoid Whole-Body Motion Tracking | RA-L 11(11), 2026 | 人形 | 技能/模仿、训练算法 | 未查 | 液态网络策略 | 10.1109/lra.2026.3732845 |
| Human2Humanoid: Physics-Aware Cross-Morphology Motion Retargeting for Humanoid Robots | RA-L 11(11), 2026 | 人形(G1/H1) | 技能/模仿 | 未查 | 重定向 | 10.1109/lra.2026.3733563 |
| From Policy Actions to Whole-Body Dynamics: A Unified Projection-Based Framework for Versatile Legged Loco-Manipulation | RA-L 11(11), 2026 | 足式 | 学习+MPC/WBC、移动操作 | 未查 | PADP 策略动作到动力学投影 | 10.1109/lra.2026.3734869 |
| Learning Terrain-Aware Whole-Body Control for Perceptive Legged Loco-Manipulation | RA-L 11(11), 2026 | 四足+臂 | 移动操作、感知运动 | 未查 |  | 10.1109/lra.2026.3732842 |
| Unleashing the Agility of Wheeled-Legged Robots for High-Dynamic Reflexive Obstacle Evasion | RA-L 11(11), 2026 | 轮足四足(M20)，**轮足** | 导航/VLN、敏捷动作 | 未查 | AWARE 反射式闪避 | 10.1109/lra.2026.3741790 |
| SPRINT: Efficient Spectral Priors for Humanoid Athletic Sprints | RA-L 11(12), 2026 | 人形(G1) | 敏捷动作、技能/模仿 | 未查 | SPRINT | 10.1109/lra.2026.3742276 |
| Global-Local Attention Decomposition for Terrain Encoding in Humanoid Perceptive Locomotion | RA-L 11(12), 2026 | 人形(G1) | 感知运动 | 未查 |  | 10.1109/lra.2026.3743710 |
| LA-WBC: Learning-Driven Adaptation of Whole-Body Control for Safe Locomotion on Uncertain Terrain | RA-L 11(12), 2026 | 四足 | 适应、学习+MPC/WBC、安全/约束 | 未查 | 学习驱动 WBC 摩擦自适应 | 10.1109/lra.2026.3745006 |
| Humanoid Goalkeeper: Learning From Position Conditioned Task-Motion Constraints | RA-L 11(12), 2026 | 人形 | 敏捷动作、技能/模仿 | 未查 | 守门员 | 10.1109/lra.2026.3744965 |
| YMSkater: Learning Skating Locomotion via Model-Guided Reinforcement Learning | RA-L 11(12), 2026 | 人形+被动轮，**轮足** | 学习+MPC/WBC、能效/热 | 未查 | YMSkater 模型引导 RL 滑行 | 10.1109/lra.2026.3746864 |
| PolyMorph: Learning Locomotion Policy for Cross-Embodiment Adaptation | RA-L 11(12), 2026 | 多形态 | 跨形态 | 未查 | PolyMorph | 10.1109/lra.2026.3747582 |
| Learning Spine-Assisted Bounding Locomotion for Gap Crossing in a Small-Scale Quadruped Robot | RA-L 11(12), 2026 | 小型四足 | 敏捷动作 | 未查 | 脊柱跳跃过沟 | 10.1109/lra.2026.3746906 |
| Learning Asynchronous Upper-Body Task-Space Trajectory Tracking Policy for Humanoid Robots | RA-L 11(12), 2026 | 人形(G1) | 移动操作 | 未查 |  | 10.1109/lra.2026.3749521 |
| RAIWAY: A Large-Wheeled Bipedal Robot With Contact-Informed Blind Locomotion | RA-L 11(12), 2026 | 大轮双足，**轮足** | 适应、sim2real/辨识、感知运动 | 未查 | RAIWAY 接触特权潜变量 | 10.1109/lra.2026.3749518 |
| GentleHumanoid: Learning Upper-Body Compliance for Contact-Rich Human and Object Interaction | RA-L 12(1), 2027 | 人形 | 人机交互、移动操作 | 未查 | GentleHumanoid | 10.1109/lra.2026.3747618 |
| E2DRL: End-to-End Differentiable Reinforcement Learning for 3D Obstacle Avoidance in Quadruped Robots | RA-L 12(1), 2027 | 四足(Go2) | 导航/VLN、感知运动、训练算法 | 未查 | E2DRL 可微 RL | 10.1109/lra.2026.3747555 |
| Unified Perceptive Fall Safety for Humanoids | RA-L 12(1), 2027 | 人形(G1) | 容错/恢复、感知运动 | 未查 |  | 10.1109/lra.2026.3751978 |
| Humanoid-DART: Humanoid Loco-Manipulation Using D iffusion-Guided A ugmentation Through R elabeling and T racking | RA-L 12(1), 2027 | 人形 | 移动操作、技能/模仿 | 未查 | Humanoid-DART(仅标题) | 10.1109/lra.2026.3752346 |
| A quadruped robot designed to complete a marathon on a single battery charge | Nature 658(8135), 2026 | 四足 | 能效/热 | 未查 | 马拉松续航，软硬协同(学习成分待核) | 10.1038/s41586-026-11102-5 |
| Getting robots back on track by reconstituting control in unexpected situations with online learning | Nat. Commun. 17(1), 2026 | 多平台 | 适应、容错/恢复、学习+MPC/WBC | 未查 | FLAIR 在线学习补偿 | 10.1038/s41467-026-70256-y |
| Learning diverse natural behaviors for enhancing the agility of quadrupedal robots | Nat. Commun. 17(1), 2026 | 四足(Go2) | 技能/模仿、敏捷动作 | 有 | Fu 等，动物动作数据 | 10.1038/s41467-026-72475-9 |
| Koopman global linearization of contact dynamics for robot locomotion and manipulation enables elaborate control | Nat. Commun. 17(1), 2026 | 足式+操作 | 世界模型/基于模型、学习+MPC/WBC | 未查 | Koopman 接触线性化 | 10.1038/s41467-026-72485-7 |
| Learning to adapt through bio-inspired gait strategies for versatile quadruped locomotion | Nat. Mach. Intell. 7(7), 2025 | 四足 | 适应、能效/热、技能/模仿 | 未查 | 仿生步态转换+记忆 | 10.1038/s42256-025-01065-z |

## 3. 主题统计

### 3.1 标签频次（151 篇，一篇可多标签）

| 主题 | 篇数 | 备注 |
|---|---|---|
| 感知运动 | 35 | **最拥挤**。人形深度/高程图（DPL、CReF、Global-Local 等）和四足跑酷（PUMA、START、MARG）最密集 |
| 技能/模仿 | 33 | **次拥挤**。几乎全是人形动作跟踪（UniTracker、CodeAct、RobotDancing、LNP、M3imic、SONIC、BeyondMimic） |
| 学习+MPC/WBC | 25 | 方法分散：残差 RL、RL 给 MPC 发步态、策略动作投影进 QP、学习修正 WBC 参数 |
| 敏捷动作 | 25 | 跳跃、冲刺、跑楼梯 |
| 移动操作 | 25 | 四足+臂、人形 loco-manipulation |
| 训练算法 | 23 | 课程、预训练、特权信息编码 |
| 导航/VLN | 15 | |
| 适应 | 15 | |
| 安全/约束 | 12 | |
| sim2real/辨识 | 12 | 以执行器模型为主（液压、BP2 高速、IJRR 能量损耗） |
| 容错/恢复 | 10 | 以摔倒恢复为主（FR-Net、Real-to-Sim-to-Real、FTSR、Unified Fall Safety） |
| 状态估计 | 9 | |
| 其他 | 9 | 综述 4 篇 |
| 能效/热 | 7 | **稀疏**，且没有一篇讲热 |
| VLA/大模型 | 5 | **稀疏**，期刊上只有 ROAM 一篇是"大模型+运动"的完整系统 |
| 世界模型/基于模型 RL | 5 | **稀疏**（DoublyAware、SDWM、Koopman、变频模型学习+MPC、在线残差+MPC） |
| 人机交互 | 3 | 最稀疏之一 |
| 跨形态 | 2 | 最稀疏（PolyMorph、TCLL） |

- **平台分布**：人形或双足 60 篇，四足 61 篇，明确写 Go2 的 9 篇，**明确用 Go2-W 的 0 篇**，轮足 8 篇。
- 期刊和会议的对比：期刊同样以人形模仿和感知运动为主。对 Go2-W 有用的世界模型、能效/热、跨形态方向在期刊上都只有个位数。热管理在 7 本期刊中 **0 篇**。

### 3.2 全部轮足论文（含学习，进入主表的 8 篇）

| # | 论文 | 期刊 | 平台 | 学习方式 | 主题 |
|---|---|---|---|---|---|
| 1 | Learning Whole-Body Loco-Manipulation for Omni-Directional Task Space Pose Tracking With a Wheeled-Quadrupedal-Manipulator | RA-L 10(2) 2025 | 轮足四足+臂 | 师生 RL，奖励融合模块 | 移动操作 |
| 2 | RL-Augmented MPC for Non-Gaited Legged and Hybrid Locomotion | RA-L 11(5) 2026 | 50–120 kg 足式/"hybrid" | 高层 RL 决定接触时序，底层 MPC | 学习+MPC。**"hybrid"是否指轮足待核** |
| 3 | A Motion Control Algorithm of Wheel-Legged Robot via ADP and Data-Driven Value Iteration | RA-L 11(6) 2026 | 轮足 | 数据驱动值迭代（ADP），近似最优控制 | 学习+控制 |
| 4 | Robust Fall Recovery for Armless Bipedal-Wheeled Robots via Force-Guided Learning (FTSR) | RA-L 11(8) 2026 | 双足轮足 | 约束 RL，外力引导课程 | 容错/恢复 |
| 5 | Agile Wheel-Bipedal Loco-Manipulation With Active Force Rejection | RA-L 11(9) 2026 | 双足轮足+臂 | 神经网络+EKF 估外力，送入 WBC | 移动操作、估计 |
| 6 | Unleashing the Agility of Wheeled-Legged Robots for High-Dynamic Reflexive Obstacle Evasion (AWARE) | RA-L 11(11) 2026 | 轮足四足 DEEP Robotics M20 | 分层 RL，滚/走/混合专家 | 敏捷、避障 |
| 7 | YMSkater: Learning Skating Locomotion via Model-Guided RL | RA-L 11(12) 2026 | 人形穿被动轮 | 简化平面模型先验注入 RL | 学习+模型、能效 |
| 8 | RAIWAY: A Large-Wheeled Bipedal Robot With Contact-Informed Blind Locomotion | RA-L 11(12) 2026 | 自研 20 英寸大轮双足 | 接触特权信息蒸馏为潜变量，部署时在线推断 | 适应、sim2real |

**8 篇全部发表在 RA-L**；Sci. Robot.、IJRR、T-RO 和 Nature 系期刊中，**学习型轮足论文为 0 篇**。四轮轮足四足（Go2-W 这一构型）只有 #1 和 #6 两篇。

### 3.3 轮足和轮式相邻论文（纯模型或机构类，不进主表，供对照）

- **RA-L**：
  - 轮足 SLAM（10(2) 2025）
  - 双足轮足一体化建模与控制优化（10(2) 2025）
  - 轮式双足空翻（10(5) 2025）
  - BiTSpoke（10(5) 2025）
  - TWLHex（10(7) 2025）
  - 双足轮足跳跃规划与空中姿态控制（10(9) 2025）
  - 弹性耦合双腿轮爬台阶（10(9) 2025）
  - 轮式双足分层优化+在线轮位规划（10(10) 2025）
  - 轮足人形全身阻抗控制（11(2) 2026）
  - **VectorGlide**：轮足四足的一体化接触运动学-动力学 MPC，靠姿态实现"无硬件转向"（11(6) 2026）。它和 Go2-W 的滑移转向问题直接相关
  - FLORES 可重构轮足（11(6) 2026）
  - 倾转旋翼辅助的轮足纵向控制（11(7) 2026）
  - 轮式双足用腿推物（NMPC，11(8) 2026）
  - 折纸式腿轮变换四足（11(10) 2026）
  - X2-N 轮足人形（11(12) 2026）
  - Circleg（11(11) 2026）
  - SPIRA 管道腿轮（10(12) 2025）
- **T-RO**：
  - 轮式平衡机器人的非光滑轨迹优化（41, 2025）
  - 两轮机器人复合全身控制（41, 2025）
  - TerraAdapt 轮足一体四足（41, 2025）
  - 轮足星球车概率路径规划（41, 2025）
  - 轮式人形双边遥操作（42, 2026）
- **轮式但含学习（相邻领域，可借鉴）**：
  - **Sci. Robot. 11(120) 2026 "Heavy metal acrobatics"**：在仿真中用 RL 训练，零样本迁移到 5 吨滑移转向装载机，实现两轮平衡行驶和旋转
  - Sci. Robot. 11(119) 2026：Ultra Mobility Vehicle，能跳的自行车机器人（系统论文，只看到标题）
  - RA-L：Learning to Drift With Individual Wheel Drive（2025）
  - RA-L：Learning to Model and Plan for Wheeled Mobility on Vertically Challenging Terrain（10(2) 2025）
  - RA-L：柔性轮机器人 RL 盲爬楼梯（11(4) 2026）

## 4. 此前名单未出现、对 Go2-W 本科毕设最有潜力的论文

核对范围：`04_research/`（不含同日并行生成的 `venue_sweep_2025_2026.md`）和 `06_reports/`，全文 grep 标题关键词。以下 5 篇均未命中。

1. **Terramechanics-Aware Adaptive Quadrupedal Locomotion via Foot-Terrain Interaction Model**（RA-L 2026，Go2，10.1109/lra.2026.3732903）。在刚体仿真器里注入塑性"虚拟地面"力，再根据接触历史估计地面并切换步态，已在 Go2 沙滩上实测。把足–地模型换成轮–沙/草的地面力学模型，并据此决定滚还是走，就能和 PACE 的轮–地差异线衔接，仿真改动量小。
2. **LA-WBC: Learning-Driven Adaptation of Whole-Body Control**（RA-L 2026，10.1109/lra.2026.3745006）。不用端到端 RL：从本体感知推断摩擦，同时改写 WBC 的摩擦约束和指令速度；训练时间约为 RL 基线的 12%。这是典型的"学习+控制"，适合在答辩中正面回应传统控制。对 Go2-W 可改成推断轮–地摩擦和打滑。
3. **Heavy metal acrobatics: Learning dynamic control for skid-steer loaders**（Sci. Robot. 2026，10.1126/scirobotics.aef0894）。Go2-W 轮式模式本身就是四轮滑移转向。这篇证明 RL+sim2real 可以做滑移转向车辆的极限动作（两轮平衡、原地旋转），可作为"滑移转向擦地/腿辅助转向"（cross_domain 1b）的顶刊依据。
4. **YMSkater: Learning Skating Locomotion via Model-Guided RL**（RA-L 2026，10.1109/lra.2026.3746864）。用简化模型给出滑行步态先验，再注入 RL，速度和能效都优于对称滑行和跑步。可迁移为 Go2-W 的"轮+蹬地"混合推进或能效步态，切入点小，仿真即可出结果。
5. **Learning to adapt through bio-inspired gait strategies for versatile quadruped locomotion**（Nat. Mach. Intell. 7:1141, 2025，10.1038/s42256-025-01065-z）。用效率、稳定性、系统极限三类生物力学指标统一决定步态转换，并加入步态记忆，盲走零样本部署。可以直接改造成 Go2-W"何时滚、何时走"的模式选择准则。代码未查。
6. 备选：**Real-to-Sim-to-Real: Learning Agile and Robust Recovery Skills With Terrain Imagination via Adversarial Imitation**（RA-L 2026，Go2，10.1109/lra.2026.3703264）。用真机示范做对抗模仿，加地形想象模块，学会复杂地形上的摔倒恢复。FTSR 已覆盖轮足恢复，但四轮轮足的复杂地形恢复仍空缺；实机有摔机风险。

## 5. 复现材料

- 原始数据和脚本放在会话 scratchpad 中（`cr/*.jsonl` 为 Crossref 全量记录，`s2.json` 为 S2 摘要，`filt.py` 为 R1 初筛，`build.py` 生成主表，其中包含逐篇的标签和平台判定）。scratchpad 会被清理；如需长期保存，请复制到 `04_research/evidence/`。
- 已知偏差：
  - 平台和标签由一人按摘要判定，没有逐篇读全文。
  - 马拉松四足（Nature）的学习成分待核。
  - RL-Augmented MPC 中的"hybrid"是否指轮足待核。
