# 向老师汇报：未选为主线的 26 篇论文，精简论证链

说明
- 英文原话逐字取自论文全文（PDF 文本），已用脚本逐条核对存在；页码为 PDF 页码，节号为论文节号。"未读到"表示全文确无或无法获取。
- 5 列文字较长，按"论文"分块给出；表后附出处核实备注。
- 读取范围：1-23 读全文；24 只读摘要；25、26 读作者版/接受版全文。

## 一、总表

| # | 论文（简称） | 正式出处（核实） | 代码 |
|---|---|---|---|
| 1 | PACE | IJRR 2026，DOI 10.1177/02783649261459628（Crossref；arXiv 2509.06342 v2） | github.com/leggedrobotics/pace-sim2real（不含运动训练环境、奖励与策略权重，见 pace_audit E3） |
| 2 | Random Joint Masking | ICRA 2024，DOI 10.1109/ICRA57147.2024.10610088（Crossref） | 未找到 |
| 3 | DreamFLEX | ICRA 2025，DOI 10.1109/ICRA55743.2025.11127805（Crossref） | 未找到（项目页 "Code (TBU)"） |
| 4 | HIMLoco | ICLR 2024（OpenAlex + 官方仓库 README；OpenReview 未取到） | github.com/Sage-PhysicalAI/HIMLoco（原 OpenRobotLab） |
| 5 | DreamWaQ | ICRA 2023，DOI 10.1109/ICRA48891.2023.10161144（Crossref） | 无官方仓库，仅第三方复现 |
| 6 | RMA | RSS 2021，DOI 10.15607/RSS.2021.XVII.011（Crossref） | 项目页链到 antonilo/rl_locomotion（后续论文仓库，非独立官方 RMA 仓库） |
| 7 | ESCP | AAAI-22，vol.36 no.7 pp.7637-7646，DOI 10.1609/aaai.v36i7.20730（Crossref + OpenAlex）；无 arXiv 版 | github.com/FanmingL/ESCP |
| 8 | SADL | IJRR 2026 在线发表，DOI 10.1177/02783649261431863（Crossref；卷期页码暂无） | github.com/AlejandroMllo/situationally_aware_dynamics_learning |
| 9 | ASID | **ICLR 2024**（PDF 首页；清单写 RSS 有误） | github.com/WEIRDLabUW/asid |
| 10 | FLAIR | **Nature Communications 17:3715（2026）**，DOI 10.1038/s41467-026-70256-y | github.com/adaptive-intelligent-robotics/FLAIR |
| 11 | Diffusion Policy | RSS 2023（DOI 10.15607/RSS.2023.XIX.026）；IJRR 扩展版 Vol.44 No.10-11 pp.1684-1704，DOI 10.1177/02783649241273668 | github.com/real-stanford/diffusion_policy |
| 12 | Ségas 等 | **预印本** arXiv 2611.22231 v1，仅见 "submitted to IEEE"，未录用 | 未找到（仅数据集 Zenodo 10.5281/zenodo.24274994） |
| 13 | TEMPO | arXiv 2610.20318；arXiv comments 与页脚均写 NeurIPS 2026（proceedings 未核实） | 未找到 |
| 14 | Omni-Perception | CoRL 2025，PMLR 305:670-685（PMLR 页标题略异） | github.com/aCodeDog/OmniPerception |
| 15 | Fu 等 | Nature Communications 17:5857（2026），DOI 10.1038/s41467-026-72475-9，题为 *Learning diverse natural behaviors for enhancing the agility of quadrupedal robots* | Code Ocean 10.24433/CO.8261908.v1；Zenodo 10.5281/zenodo.19052497 |
| 16 | VR-Robo | RA-L 10(8):7875-7882, 2025，DOI 10.1109/LRA.2025.3575648 | github.com/zst1406217/VR-Robo |
| 17 | StreamVLN | ICRA 2026（arXiv comments + Crossref DOI 10.1109/ICRA57385.2026.11696190） | github.com/InternRobotics/StreamVLN（现重定向 Sage-PhysicalAI） |
| 18 | CaT | IROS 2024，DOI 10.1109/IROS58592.2024.10802334（Crossref） | github.com/Gepetto/constraints-as-terminations |
| 19 | DIAL-MPC | ICRA 2025，DOI 10.1109/ICRA55743.2025.11127320；ICRA 官网列为 Best Paper（机器人操作与运动类）"Other Finalists"，**非获奖者** | github.com/LeCAR-Lab/dial-mpc |
| 20 | LoComposition | **预印本** arXiv 2606.15896 v2；仅有 CoRL 2026 模板页脚，**录用未核实** | github.com/LouKordos/locomposition |
| 21 | PEGrad | CoRL 2025，PMLR 305:221-237（peri25a） | github.com/pvskand/PEGrad（来自 GitHub 搜索，PMLR 页未列） |
| 22 | FPO++ | arXiv 2602.02481 v2；页脚 CoRL 2026，项目页标 Oral（录用以项目页为准，未见官方目录） | github.com/amazon-far/fpo-control（据项目页链接，未打开仓库核实） |
| 23 | QOED | RSS 2026（roboticsproceedings.org/rss22/p137），题为 *Learning What Matters: Adaptive Information-Theoretic Objectives for Robot Exploration* | github.com/youwyu/QOED（据项目页链接，未核实内容） |
| 24 | Hao 等 | IEEE RICAI 2023，DOI 10.1109/RICAI60863.2023.10489493，pp.149-152，题为 *Skid Steering Control and Wheel-Centred Trajectory Planning for Wheel-Legged Robots* | 未找到 |
| 25 | Lee 等 | Science Robotics 9(89) eadi9641, 2024，DOI 10.1126/scirobotics.adi9641，题为 *Learning robust autonomous navigation and locomotion for wheeled-legged robots*（读 arXiv 2405.01792 接受版） | 未找到 |
| 26 | Heavy metal acrobatics | Science Robotics 11(120)，2026-11-11，DOI 10.1126/scirobotics.aef0894，*Learning dynamic control for skid-steer loaders*（读 arXiv 2611.18365 作者版） | 无训练代码；Dryad 数据与绘图代码 10.5061/dryad.d7wm37qhh |

## 二、论证链（问题 / 已有局限 / 方法 / 平台与结果 / 自述局限）

### 1. PACE
- 问题：p1 摘要 "Yet controllers trained in simulation often fail to transfer reliably, and most existing approaches neglect actuator-specific energy losses or depend on complex, hand-tuned reward formulations." 意译：仿真控制器迁移不可靠，多数方法忽略执行器能耗或依赖手调奖励。
- 已有局限：p1 §1 "While these methods have demonstrated impressive sim-to-real transfer, they often require specialized sensors, exhaustive parameter identification, or iterative expert tuning of heuristic models and reward functions." 意译：现有方法需专用传感器、穷尽辨识或专家调参。
- 方法核心：固定基座悬空约 20 s 编码器数据，CMA-ES 拟合关节动力学参数。
- 平台与结果：TYTAN/ANYmal/MINIMAL 零样本；Table 5（p18）ANYmal D CoT 1.27，较 ANYmal C 的 1.86 降约 32%（混杂因素见 pace_audit §3）。
- 自述局限：p21 §6 "Current limitations include finite excitation bandwidth on suspended setups and temperature/aging dependencies that shift effective parameters." 意译：悬挂激励带宽有限；温度/老化使有效参数漂移。

### 2. Random Joint Masking
- 问题：p1 摘要 "In this paper, we propose a novel deep reinforcement learning framework to enable a quadrupedal robot to walk with impaired joints." 意译：让四足机器人带着受损关节行走。
- 已有局限：p2 §II-B "However, these methods often relied on a specific robot dynamic model, case-by-case models for various failure cases, and time-consuming model parameter tuning." 意译：依赖特定模型、逐故障建模、调参耗时。
- 方法核心：随机屏蔽关节动作/力矩，加关节状态估计器与渐进课程。
- 平台与结果：Go1；Table II 总平均速度 RMSE 0.5787 -> 0.1951；室外约 0.5 km（p6）。
- 自述局限：p6 §IV-B "Still, there is a lot of room to improve in that the performance of impaired locomotion decreases according to the impaired joint positions"（原句后接 "and front-biased center of gravity"，PDF 缺连字符，截断引用）。意译：性能随受损位置下降，仍有改进空间。

### 3. DreamFLEX
- 问题：p1 摘要 "In this paper, we propose DreamFLEX, a robust fault-tolerant locomotion controller that enables a quadrupedal robot to traverse complex environments even under joint failure conditions." 意译：关节故障下仍能穿越复杂地形。
- 已有局限：p1 §I "However, these studies had a limited demonstration for overcoming various rough terrains." 意译：已有 DRL 容错研究在崎岖地形上验证有限。
- 方法核心：在 DreamWaQ 上加 FEMNet，显式估计关节故障向量并调制隐变量。
- 平台与结果：Go1，Isaac Gym；Table III（p6）平均 ATE 0.1786 对 FT-Net 0.2848；FEMNet 最多提升 36.49%（p5，对比去掉故障向量的版本）。
- 自述局限：无局限段，取结论未来工作 p6 §IV "In future work, we plan to extend DreamFLEX to leverage an additional hardware such as a manipulator to enhance the robustness of the fault-tolerant controller when the robot is faced with various dynamic environments." 意译：计划借助机械臂等附加硬件增强鲁棒性。

### 4. HIMLoco
- 问题：p1 摘要 "However, the sensors of most legged robots can only provide partial and noisy observations, making the estimation particularly challenging, especially for external states like terrain frictions and elevation maps." 意译：传感器观测部分且含噪，外部状态难估计。
- 已有局限：p2 §1 "This two-phase training paradigm complicates the training process and inevitably induces information loss in the mimicking learning phase" 意译：两阶段（先 oracle 后模仿）复杂且模仿阶段丢信息。
- 方法核心：把外部状态视为扰动，对比学习使响应嵌入逼近后继状态，仅本体感觉。
- 平台与结果：A1/Go1/Aliengo；Table 2（p7）短楼梯成功率 100% 对 RMA 60%（真机 20 次）。
- 自述局限：p9 §5 "However, the lack of external perceptions, e.g., visual information, leaves legged robots with only a primitive skill set." 意译：缺外部感知，技能集仍原始。

### 5. DreamWaQ
- 问题：p1 摘要 "This work proposes a novel quadrupedal locomotion learning framework that allows quadrupedal robots to walk through challenging terrains, even with limited sensing modalities." 意译：有限传感下走过挑战性地形。
- 已有局限：p1 摘要 "Furthermore, prior works that rely only on proprioception have shown a limited demonstration for overcoming challenging terrains, especially for a long distance." 意译：仅本体感觉的工作验证有限，尤其长距离。
- 方法核心：非对称演员-评论家，CENet（β-VAE）联合估计速度与隐变量，加自适应自举。
- 平台与结果：A1，Isaac Gym；Table III（p5）推力存活率 95.23% 对基线 20.51%；真机 Course A/B 共 430/465 m（§III-G）。
- 自述局限：p6 §IV "DreamWaQ's limitation lies in its adaptation mechanism, where it must first hit the obstacles with its legs." 意译：适应机制必须先用腿撞到障碍。

### 6. RMA
- 问题：p1 摘要 "Successful real-world deployment of legged robots would require them to adapt in real-time to unseen scenarios like changing terrains, changing payloads, wear and tear." 意译：真实部署需对未见场景实时适应。
- 已有局限：p4 §II "However, domain randomization trades optimality for robustness leading to an over conservative policy" 意译：域随机化以最优性换鲁棒性，策略过保守。
- 方法核心：基策略条件于环境外参 z；自适应模块用状态-动作历史回归 z。
- 平台与结果：A1，RaiSim；Table II（p8）仿真成功率 73.5%，Robust 62.4%，Expert 76.2%；真机下楼梯 70%（Fig.1）。
- 自述局限：p9 §VI "Larger perturbations such as sudden falls while going downstairs, or due to multiple leg obstructions from rocks, sometimes lead to failures." 意译：较大扰动有时导致失败（前句 "a blind robot has limitations"）。

### 7. ESCP
- 问题：p1 引言 "In this paper, we aim at improving the fast adaptation ability of the agents in the changing environment." 意译：提升变化环境中的快速适应能力。
- 已有局限：p1 摘要 "However, previous methods show lagged and unstable context extraction, which are hard to handle sudden changes well." 意译：已有上下文提取滞后且不稳定，难应对突变。
- 方法核心：上下文编码器加方差最小化、关系矩阵行列式最大化、截断历史 RNN。
- 平台与结果：纯仿真（grid-world + 5 个运动任务）；Table 1（p7）HalfCheetah 突变回报 7237 对 SAC-RNN 5997；格子世界适应快 10 倍。
- 自述局限：未读到（结论段只总结贡献，全文无 limitation/future 命中）。

### 8. SADL
- 问题：p1 §1 "Such ambiguity is undesirable because it increases uncertainty during decision-making, often producing suboptimal plans or, in extreme cases, unsafe behavior." 意译：状态歧义增加决策不确定性，导致次优或不安全。
- 已有局限：p2 §1 "However, these methods are data-intensive and often rely on multi-stage procedures that require privileged information, such as ground-truth data that is difficult to obtain or is only available in simulation." 意译：数据量大、多阶段且需特权信息。
- 方法核心：多变量 BOCD 在线估计转移分布，符号化情境输入动力学模型。
- 平台与结果：Jackal 地面车（仿真+实机）、四旋翼仿真；Table 3 难度 4 成功率 0.86 对 Dubins 0.82、PE-RPY 0.56、PE-Y 0.22。
- 自述局限：p25 §7.1 "A more fundamental limitation relates to the model's generalization capabilities, particularly when encountering dynamics that are out-of-distribution (OOD) with respect to the situations learned during training, which is a common restriction of most learning-based methods." 意译：对训练未见的分布外动力学泛化有限。

### 9. ASID
- 问题：p2 §1 "However, directly deploying policies trained in simulation in the real world is often ineffective due to the discrepancy between the simulation and the real world, the so-called sim2real gap." 意译：仿真策略直接上真机常因 sim2real gap 失效。
- 已有局限：p1 摘要 "The challenge with such model-based techniques is the requirement for an extremely accurate simulation, requiring both the specification of appropriate simulation assets and physical parameters." 意译：需要极精确的仿真资产与物理参数。
- 方法核心：仿真中学最大化 Fisher 信息的探索策略，真机采数据辨识参数后重训。
- 平台与结果：Franka Panda 真机；Table 2 平衡杆 ASID 6/9 次成功，DR 0/9；Table 3 台球推冰壶 4/5（近）、3/5（远），DR 2/5、1/5。
- 自述局限：无局限段。最接近 p9 §5.5 "we find that a center of mass close to the middle of the rod causes ambiguities that hurt our system identification process" 意译：质心靠近杆中部时存在歧义，损害辨识（非专门局限段）。

### 10. FLAIR
- 问题：p1 摘要 "Everyday scenarios are a challenge for robot controllers due to disturbances that can be caused by unforeseen conditions (e.g., damage, flat tires, or wind gusts) or unexpected usage." 意译：意外条件造成的扰动使控制器失效。
- 已有局限：p1 引言 "such approaches quickly increase in complexity when more sources of perturbation are considered, and their performance can degrade if the robot encounters scenarios not pre-specified" 意译：扰动源增多则复杂度剧增，遇未预设场景性能下降。
- 方法核心：高层在线拟合扰动模型（泰勒展开），反向修正操作指令。
- 平台与结果：履带移动机器人实机（另有六足仿真）；Table 1 中位数跟踪误差降 74.4%，更新约 218 ms。
- 自述局限：p8 Discussion "More generally, FLAIR cannot fully recover operability when the force required to counteract a perturbation exceeds the maximal strength of the actuators." 意译：所需力超过执行器上限时无法完全恢复。

### 11. Diffusion Policy
- 问题：p1 §1 "In practice however, the unique nature of predicting robot actions" ... "makes this task distinct and challenging compared to other supervised learning problems"（省略的插入语为 "such as the existence of multimodal distributions, sequential correlation, and the requirement of high precision"）。意译：多模态、时序相关、高精度使动作预测不同于一般监督学习。
- 已有局限：p2 §1 "Training energy-based policies often requires negative sampling to estimate an intractable normalization constant, which is known to cause training instability" 意译：能量式策略需负采样，训练不稳。
- 方法核心：视觉运动策略建模为动作空间条件去噪扩散，滚动时域输出动作序列。
- 平台与结果：4 个基准 15 任务，摘要称平均提升 46.9%；真机 Push-T Table 6 成功率 0.95，最佳基线 LSTM-GMM 0.20。
- 自述局限：p15 §9 "Second, diffusion policy has higher computational costs and inference latency compared to simpler methods like LSTM-GMM." 意译：计算开销与推理延迟更高。

### 12. Ségas 等（预印本）
- 问题：p1 §I "In this paper, we address the problem of making learned locomotion policies thermally aware, so that sustained locomotion is limited by the battery rather than by motor temperatures." 意译：让策略具备热感知，使续航受电池而非电机温度限制。
- 已有局限：p2 §I "Over a reinforcement learning (RL) episode of a few seconds, temperatures barely change, making credit assignment of temperature-based rewards exceedingly challenging." 意译：回合仅数秒，温度几乎不变，温度奖励难做信用分配。
- 方法核心：辨识 RC 热网络，惩罚预测稳态温度作奖励。
- 平台与结果：Unitree Go2 实机；Fig.1 5 kg 载荷 1 m/s 续航 19 -> 174 分钟；Table I 热模型留出集 RMSE < 1 摄氏度。（论文内部摘要写 26 度、引言写 22 度，未引用温度。）
- 自述局限：无局限段，取 p7 §IV 未来工作 "In future work, we plan to (1) close the sim-to-real gap we observed at large payloads, (2) build an electrical power reward on the identified power balance to turn thermal headroom into range, and (3) add a governor that adjusts the commanded velocity from the model's real-time predictions." 意译：大载荷下仍有 sim-to-real 差距，未把热余量转为航程。

### 13. TEMPO
- 问题：p1 §1 "Robots deployed in the real world must contend with operating conditions that can diverge sharply from those encountered during training" 意译：部署条件可能与训练严重偏离。
- 已有局限：p1 §1 "While effective in some cases, this approach is fundamentally constrained by what can be specified in advance"（指域随机化）。意译：受限于事先能枚举的变化。
- 方法核心：冻结 critic 只更新 actor，加熵正则与高难度分数记忆。
- 平台与结果：MuJoCo Playground 的 Go1/Go2/G1，摘要称最高提升 80%；Go2 实机 Table 1 平均奖励 89.8 -> 98.7。
- 自述局限：p17 附录 C "First, while TEMPO is designed to be lightweight and on-device friendly, it still relies on access to a pretrained critic that is reasonably informative under shift" 意译：仍依赖偏移下仍有信息量的预训练 critic。

### 14. Omni-Perception
- 问题：p2 §1 "Enabling such agile, collision-free movement in unstructured 3D environments remains a fundamental challenge" 意译：非结构化三维环境中的敏捷无碰撞运动仍是根本挑战。
- 已有局限：p1 摘要 "Depth-based perception approaches often struggle with sensor noise, lighting variability, computational overhead from intermediate representations." 意译：深度感知受噪声、光照影响且中间表示开销大。
- 方法核心：PD-RiskNet 分层处理原始 LiDAR 点云，端到端 RL 避障。
- 平台与结果：Unitree 实机（图注为 Go2+Livox，机型由图注推断）；Table 4 空中障碍 21/30 对原生 0/30，动态行人 27/30 对 0/30。
- 自述局限：p9 §6 "Performance can degrade in environments dominated by highly unstructured vegetation, such as dense grass, where LiDAR struggles to extract reliable geometric features essential for locomotion." 意译：茂密草丛中 LiDAR 难提取几何特征。

### 15. Fu 等（Nature Commun. 17:5857）
- 问题：p1 摘要 "While recent studies have successfully demonstrated imitation of specific behaviors, enabling robots to replicate a broader range of natural behaviors in real-world environments remains an open challenge." 意译：复现更广泛自然行为仍是开放难题。
- 已有局限：p2 §Introduction "However, designing suitable reward functions in DRL is complex and often leads to unnatural behaviors." 意译：奖励设计复杂，常致不自然行为。
- 方法核心：狗动捕半监督对抗模仿，深度 TSC 调度，EASI 校准仿真。
- 平台与结果：Go2 + RealSense D435i；Fig.2f 完整敏捷赛道平均 1.1 m/s、24 s；Fig.3 跨栏峰值 3.2 m/s。狗动捕数据来自 AI4Animation。
- 自述局限：p7 Discussion "While the TSC is robust to noise, its adaptation to environmental shifts is limited"（后接 "for example, changing obstacle geometry slightly reduces success due to train-test distribution shift"）。意译：对环境变化适应有限。

### 16. VR-Robo
- 问题：p1 摘要 "However, these policies often encounter challenges when deployed in real-world environments due to sim-to-real gaps, as simulators typically fail to replicate visual realism and complex real-world geometry." 意译：仿真器缺视觉真实感与复杂几何导致迁移差距。
- 已有局限：p1 §I "Nonetheless, most existing approaches [13]–[17] focus on enhancing photorealism, offering limited support for physical interaction with complex terrains." 意译：多只追求照片级真实，物理交互支持有限。
- 方法核心：3DGS-网格混合重建数字孪生，仿真中训练纯 RGB 策略。
- 平台与结果：Go2（Jetson Orin Nano 板载）；Table I 真机到红锥成功率 Ours 100%/93.33%/100%（易/中/难），IL 均 0%；Table II 仿真 100% 对 IL 8.67%。
- 自述局限：p7 §VI-A "The current environment is limited to indoor scenes with static terrains, which constrains the diversity of scenarios." 意译：仅限静态地形的室内场景。

### 17. StreamVLN
- 问题：p1 §I "However, achieving robust VLN remains challenging due to the need for fine-grained multimodal alignment, long-term sequence reasoning, and generalization to unseen environments." 意译：稳健 VLN 需细粒度对齐、长程推理与未见环境泛化。
- 已有局限：p1 摘要 "While Video-based Large Language Models (Video-LLMs) have driven recent progress, current VLN methods based on Video-LLM often face trade-offs among fine-grained visual understanding, long-term context modeling and computational efficiency." 意译：三者之间被迫取舍。
- 方法核心：慢快上下文，滑窗 KV 复用加 3D 体素剪枝记忆。
- 平台与结果：VLN-CE R2R/RxR val-unseen，Table I（p4）R2R SR 56.9% / SPL 51.9%，RxR SR 52.9% / SPL 46.0%；真机 Go2 + RealSense D455（Fig.5/6）。
- 自述局限：未读到（全文无 Limitations 段，结论无未来工作句）。

### 18. CaT
- 问题：p1 摘要 "Yet, current solvers fail to produce efficient policies respecting hard constraints." 意译：现有求解器难产出满足硬约束的高效策略。
- 已有局限：p1 §I "Although some recent constrained RL methods have been applied to locomotion [20], [21], they often simplify reward engineering at the cost of algorithmic complexity, as additional critic networks and terms in the policy loss function have to be implemented." 意译：约束 RL 增加了算法复杂度。
- 方法核心：约束违反转为随机终止，缩放未来回报，PPO 改几行。
- 平台与结果：真机 Solo-12（非 Go2）；Table III 障碍赛道成功率 CaT(Tracking Constraints) 90.6%、CaT(Tracking Rewards) 79.4%、Style always active 34.4%。
- 自述局限：无局限段，取 p6 §VI "Future work could explore more principled ways to define the termination conditions based on the constraints." 意译：终止条件的定义仍不够有原则。

### 19. DIAL-MPC
- 问题：p1 摘要 "Due to high dimensionality and non-convexity, real-time optimal control using full-order dynamics models for legged robots is challenging." 意译：全阶动力学实时最优控制因高维非凸而困难。
- 已有局限：p1 §I "Nonetheless, these algorithms are sensitive to hyperparameters in high-dimensional and non-convex optimization problems, particularly the sampling kernel, leading to high variance and suboptimal performance." 意译：采样式 MPC 对采样核敏感，方差大、次优。
- 方法核心：扩散式退火的采样 MPC，全阶力矩级实时控制。
- 平台与结果：Go2 力矩级控制（Fig.7，7 kg 负载行走与连续跳跃）；Table I 行走跟踪误差 DIAL-MPC 0.024、NMPC 0.055、GCRL 0.119、MPPI-explore 0.190。需外部定位（仓库 README，见 go2w_rerank）。
- 自述局限：p7 §V "One limitation is that DIAL-MPC requires fast simulation to generate samples, which limits the application of DIAL-MPC in longer planning horizon tasks." 意译：需快速仿真生成采样，限制长时域任务。

### 20. LoComposition（预印本）
- 问题：p1 摘要 "Learning-based quadrupedal locomotion typically relies on complex reward formulations that entangle task specification, operational limits, gait preference, and terrain adaptation within a single optimization objective." 意译：复杂奖励把多目标缠在一起。
- 已有局限：p2 §1 "These gait-style priors can be effective engineering shortcuts, but they also encode assumptions about a particular robot and desired motion pattern that require reward engineering, and we show that this can lead to suboptimal learning outcomes." 意译：步态先验编码特定假设，可能次优。
- 方法核心：奖励管任务、CaT 约束管极限、能耗最小化选步态、感知适应地形。
- 平台与结果：Go2 零样本（Livox MID-360 高程图）；Table 2 COT 0.28、极限违反率 0.50%，对复杂奖励基线 RP 的 0.64、13.3%；Table 4 真机 1 m/s 各障碍成功率。
- 自述局限：p9 §5 "The evaluation covers the tested simulation terrains and controlled hardware obstacles; hardware validation on other embodiments, broader terrain distributions, degraded sensing, and fully onboard state estimation remain future work." 意译：评估范围有限，其他机型、更广地形、传感退化、板载状态估计留待未来。

### 21. PEGrad（Non-conflicting Energy Minimization）
- 问题：p1 摘要 "In this work, we propose a hyperparameter-free gradient optimization method to minimize energy expenditure without conflicting with task performance." 意译：无超参的梯度方法，在不损害任务性能下降低能耗。
- 已有局限：p1 摘要 "This requires carefully tuning weight terms to avoid undesirable trade-offs where energy minimization harms task success." 意译：需精细调权重。
- 方法核心：能耗梯度投影到任务梯度正交方向，免调权重。
- 平台与结果：DMControl、HumanoidBench 仿真能耗最多降 64%；Go2 真机 Table 1（p8）行走较最佳调参 AMP+PPO(lambda=0.0002) 电流低 19.74%、力矩低 15.8%。
- 自述局限：p9 §6 "Throughout this project, we found it challenging to combine the energy minimization objective with style rewards." 意译：与风格奖励难以结合。

### 22. FPO++
- 问题：p1 摘要 "Likelihood-based policy gradient methods are the dominant approach for training robot control policies from rewards."（后句 "These methods rely on differentiable action likelihoods, which constrain policy outputs to simple distributions like Gaussians." 为摘要原文，未逐字脚本核验）。意译：主流策略梯度依赖可微似然，限制策略输出为简单分布。
- 已有局限：p1 §1 "This is effective for simple action distributions, but challenging for more expressive policy representations" 意译：对流策略等表达力更强的表示很难。
- 方法核心：流匹配绕开似然；逐样本比率裁剪加非对称信任域。
- 平台与结果：Go2/Spot/H1/G1 仿真多数收敛回报高于高斯 PPO（图 A.5）；T1 运动、G1 动作跟踪真机（图 3）；无统一数值表。
- 自述局限：p9 §4 "FPO++ also takes more wall-clock time than Gaussian PPO, limiting its appeal where Gaussian policies already suffice" 意译：墙钟时间更长（G1 运动 L40S 上 23 对 19 分钟）。

### 23. QOED
- 问题：p1 摘要 "Designing learnable information-theoretic objectives for robot exploration remains challenging." 意译：难以设计"可学习"的信息论探索目标。
- 已有局限：p2 §II-B "Nonetheless, identifying nuisance parameters and accounting for their influence remains a significant gap." 意译：识别并处理干扰参数仍是空白。
- 方法核心：Fisher 信息矩阵特征空间选可辨识方向，抑制干扰参数。
- 平台与结果：仿真与 Jackal/Franka 真机；表 I（p7）动力学预测 RMSE 较 QOED-Agnostic 降 21.98%、较 BOED 降 35.23%；Franka 真机成功率 89%（图 4）。
- 自述局限：p9 §VI "In the real world, limited training time also leads to less refined behavior than in simulation" 意译：真机训练时间有限，行为不如仿真精细（同节另称需要物理参数化来定义探索目标，该句未逐字核验）。

### 24. Hao 等 RICAI 2023（仅摘要）
- 问题（摘要）："Wheel-legged robots use skid steering due to space constraints." 意译：受空间限制轮足机器人采用滑移转向。
- 已有局限（摘要）："During the steering process, the tire longitudinal and lateral force are large, and the wheel motor performance requirements are high." 意译：转向时轮胎纵侧向力大，对轮毂电机要求高。
- 方法核心：缩小轴距的滑移转向框架加轮心轨迹规划，PID/滑模控制。
- 平台与结果：摘要仅定性称提升效率与转向稳定性、降低电机要求；无数字、无图表号。
- 自述局限：未读到（仅摘要）。

### 25. Lee 等 Science Robotics 2024
- 问题：p1 摘要 "Navigating urban environments, however, poses unique challenges for robots, necessitating innovative solutions for locomotion and navigation." 意译：城市导航需要运动与导航两方面的创新。
- 已有局限：p1 Introduction "Existing approaches for hybrid locomotion build upon simple heuristics to decide when to step and when to drive [10] or rely on pre-defined gait sequences [11, 12]." 意译：现有混合运动依赖简单启发式或预定义步态序列。
- 方法核心：无模型 RL 加特权学习做混合运动，分层 RL 导航，城市级集成。
- 平台与结果：ANYmal 轮足；Zurich Glattpark 任务总行程 8.3 km、少量人工干预（图 3）；平均 1.68 m/s、机械 COT 0.16（对腿式 ANYmal 速度约 3 倍、COT 低 53%，图 3B-iii）。
- 自述局限：p11 Discussion "Our system's perception capabilities, although effective for the demonstrated scenarios, may present limitations for faster missions or in environments with high uncertainty." 意译：感知在更快任务或高不确定环境下可能受限。

### 26. Heavy metal acrobatics
- 问题：p1 摘要 "Yet, automation of such machines is challenged by their complex dynamics, in part because of hydraulic actuation that involves fluids, flexible elements, and nonlinear delays." 意译：液压带来流体、柔性和非线性延迟，自动化困难。
- 已有局限：p1 Introduction（针对 MPC）"However, highly dynamic behaviors involving underactuated balancing and frequent contact changes introduce additional challenges related to model accuracy, contact handling, and real-time optimization." 意译：欠驱动平衡与频繁接触切换使模型精度、接触处理、实时优化更难。
- 方法核心：仿真 RL 加执行器辨识与域随机化，分技能训练并直接迁移真机。
- 平台与结果：5 吨 John Deere 332G 滑移装载机；表 1 抬升到两轮，臂角 28/31 度成功率 100%，34 度 78.6%（11/14）；真机跨 75 cm 起伏地形（图 4C）。
- 自述局限：p6 Discussion "For simplicity, we composed the overall behavior using hand-crafted switching conditions." 意译：各技能由手工切换条件拼接。

## 三、未核实与未读到汇总
- 出处未核实：LoComposition 是否被 CoRL 2026 录用；Ségas 未录用（仅投稿声明）；TEMPO 的 NeurIPS 2026 proceedings 页；FPO++ 的 CoRL 2026 仅据 PDF 页脚与项目页；HIMLoco 的 OpenReview/DBLP 未取到；SADL 卷期页码暂无。
- 与清单不一致处：ASID 为 ICLR 2024（非 RSS）；FLAIR 为 Nature Communications 17:3715。
- 代码：RJM、DreamFLEX、DreamWaQ、Ségas、TEMPO、Hao、Lee 未找到官方代码；FPO++、QOED 仅据项目页链接未打开仓库；PEGrad 仓库来自 GitHub 搜索。
- 原话未读到：ESCP、StreamVLN、Hao 的作者自述局限。
- 用邻近句代替自述局限：DreamFLEX、Ségas、CaT（未来工作句）；ASID（实验段）。
- 引文瑕疵：RJM 局限句因 PDF 缺连字符而截断；FPO++ 摘要第二句与 QOED "需物理参数化"一句未逐字核验；Diffusion Policy 问题句为两段引文拼接，已标注省略。
