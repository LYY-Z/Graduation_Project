# 顶刊四足/轮足论文：作者自述局限与未来工作（信息抽取）

日期：2026-11-25。输入：`venue_sweep_journals.md` §2 总表 151 篇、§3.2–3.3；`cross_domain_sweep.md` 中已正式发表的跨领域来源。**只做信息抽取，不含选题判断。**

## 0. 筛选与读取口径

- **保留 91 篇**：四足、轮足（含双足轮足）及平台只写"足式"的论文；Sci. Robot. 8（含 2 篇综述）、IJRR 5、T-RO 9、RA-L 64、Nature 系 5。
- **排除**：纯人形/纯双足（约 60 篇）；Sci. Robot. 中平台未核的"全身接触操作"和多平台的"Resilient odometry"；RA-L 的六足模仿 RL（标题明确写 hexapod）、绳驱足式、腿式球形机器人；人形加被动轮的 YMSkater 因普查表标"轮足"而**保留**（#81）。
- **平台修正**：#10 GOLLUM、#32 实为六足，因普查表只标"多足/足式"而保留，请注意。#53 实际平台是自研 Jumper，不是 Olympus。
- **读取方式**：由 10 个抽取员并行检索 arXiv、项目页、出版社页，只记录读到的文字。"源"列：全=读到全文（含 arXiv 版）；摘=只读到摘要或项目页；无=没有找到。**arXiv 版与期刊版是否完全一致未逐篇核对。**
- **"读到局限"的判定**：读到作者在结论、局限或未来工作里写出的具体内容才算。仅摘要级表述（#7、#8）、新闻稿（#87）、补充材料一句话（#88）不计入。共 **57 篇**读到，**34 篇未读到**。
- 局限类型代码（只依据作者自述）：A 仿真到真机或执行器建模差距；B 感知依赖或失效；C 泛化范围有限（地形/任务/场景）；D 训练成本或样本效率；E 安全/约束/可靠性无保证；F 跨平台/形态迁移；G 多技能、模式切换、长时程；H 能效/热/续航；I 状态估计误差；J 在线适应/未建模动力学；K 接触交互/操作；X 未读到。
- **Go2-W：91 篇中 0 篇使用。** Go2 系：#14、#15、#28（零样本迁移测试）、#29、#33、#43、#44（基准）、#46、#47（仅仿真）、#52、#57、#62（自采数据，非控制）、#85、#89；#65、#76 仅普查表标 Go2，未读到全文。
- 轮足相关：#26（LimX W1）、#55（含 B2-W、Centauro）、#58、#59（含轮式四足 Kyon 验证）、#64、#70、#79（M20）、#81、#84。

## 1. 论文表

### 1.1 Science Robotics

| # | 标题 | 期刊卷期年 | 平台 | 问题 | 方法核心 | 作者自述局限/未来工作 | 代码 | Go2/Go2-W | 类型 | 源 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | High-speed control and navigation for quadrupedal robots on complex and discrete terrain | Sci. Robot. 10(102) 2025 | Raibo 四足 | 离散地形高速导航 | 落脚点规划+RL 跟踪器 | 仅 2.5D 图，无法规划垂直墙；将做 3D 体素图与遮挡预测，现依赖动捕 | 无（仅数据） | 否 | B C | 全 |
| 2 | Learning coordinated badminton skills for legged manipulators | Sci. Robot. 10(102) 2025 | ANYmal-D+臂 | 腿式机械臂打羽毛球 | 单 RL 策略控制全身，感知噪声模型 | 倒退时球易出视场；挥拍靠规则；将换学习式感知、可动相机 | 无（仅数据） | 否 | B K C | 全 |
| 3 | Attention-based map encoding for learning generalized legged locomotion | Sci. Robot. 10(105) 2025 | ANYmal+人形 | 稀疏地形通用运动 | CNN+注意力编码高度图 | 训练需数天、调参低效；2.5D 图不适用；未做操作；将做 3D 表示 | 无（仅数据） | 否 | D C K | 全 |
| 4 | Agile perceptive multiskill locomotion for quadrupedal robots in the wild | Sci. Robot. 11(116) 2026 | HOUND（Go1 等为初步） | 野外多技能敏捷运动 | 轨迹优化运动库+APT-RL | 以矢状面为主，仅小跑和跳跃；高速时 LiDAR 不可靠；将加转弯、侧移、长时程 | 无（有项目页） | 否 | C B G | 全(部分) |
| 5 | Advances, challenges, and opportunities for legged robots（综述） | Sci. Robot. 11(116) 2026 | 足式综述 | 足式进展与挑战 | 硬件/运动/自主/数据/应用综述 | 策略安全验证仍是开放问题；仿真覆盖不了真实情形需真实数据 | 无 | 否 | E A | 全 |
| 6 | ZEST: Zero-shot embodied skill transfer for athletic robot control | Sci. Robot. 11(117) 2026 | Atlas/G1/Spot | 动作参考零样本上真机 | RL 模仿+自适应采样+执行器模型 | 未评估训练外动作；仅本体感知、假定平坦不打滑；自动系统辨识未解 | 未查 | 否 | C A G | 全(部分) |
| 7 | How robot dogs see the unseeable: peering | Sci. Robot. 11(118) 2026 | ANYmal | 植被遮挡视觉失效 | 侧向 peering 合成孔径 | 未读到明确局限；仅知遮挡约 50% 时最佳、需足够采样 | 未查 | 否 | X | 全(无局限) |
| 8 | Bridging vision-language reasoning and learned control for legged navigation in the wild (ROAM) | Sci. Robot. 11(120) 2026 | 腿式(型号未读到) | 公里级野外导航 | VLM 风险图引导 RL | 未读到（摘要称 VLM 可靠性与空间推理仍是开放挑战） | 有 github.com/leggedrobotics/roam | 未知 | X | 摘 |

### 1.2 IJRR

| # | 标题 | 期刊卷期年 | 平台 | 问题 | 方法核心 | 作者自述局限/未来工作 | 代码 | Go2/Go2-W | 类型 | 源 |
|---|---|---|---|---|---|---|---|---|---|---|
| 9 | Learning-based legged locomotion: SOTA and future perspectives（综述） | IJRR 44(8) 2025 | 足式综述 | 学习式足式运动现状 | 综述硬件、仿真器、RL、模仿 | 开放问题：轮足混合运动、仅靠足与躯干的操作、安全、技能发现、基础模型 | 无 | 否 | F K E | 全(部分) |
| 10 | GOLLUM: growable neural control with online continual learning | IJRR 44(13) 2025 | 六足 MORF | 终身运动技能学习 | 神经发生增列+在线持续学习 | 无正式局限节；实验受场地所限被叫停；可扩展到示教编程 | 有 github.com/Arthicha/GOLLUM | 否 | C | 全(部分) |
| 11 | Parkour in the wild: multi-expert distillation and RL fine-tuning | IJRR online 2026 | ANYmal-D | 通用可扩展跑酷 | 多专家 DAgger 蒸馏+RL 微调 | 噪声模型过激进；记忆有限需换架构；感知失效靠本体；电机冲击磨损增大 | 未读到 | 否 | B H G | 全 |
| 12 | Towards bridging the gap: systematic sim-to-real for diverse legged robots (PACE) | IJRR online 2026 | 多机型 | 足式执行器 sim2real | 关节空间对齐+PMSM 模型 | 悬挂激励带宽有限；温度老化致参数漂移；假设破坏则失败；未来建模电气约束 | 有（称将发布）github.com/leggedrobotics/pace-sim2real | 否 | A H J | 全 |
| 13 | GrandTour: legged robotics dataset in the wild | IJRR online 2026 | ANYmal-D | 多模态感知与估计数据 | 49 序列+63 种估计方法基准 | 仅瑞士；无重访；缺雷达/事件相机；未来加双足、轮足形态 | 有工具与 HF 数据 | 否 | C I F | 全(部分) |

### 1.3 T-RO

| # | 标题 | 期刊卷期年 | 平台 | 问题 | 方法核心 | 作者自述局限/未来工作 | 代码 | Go2/Go2-W | 类型 | 源 |
|---|---|---|---|---|---|---|---|---|---|---|
| 14 | Spatio-Temporal Motion Retargeting for Quadruped Robots | T-RO 41 2025 | Go1/Go2/AlienGo/B2 | 动物动作重定向 | 空间重定向+时间优化 | 依赖接触估计；贝叶斯优化难扩展到高维；将做更好接触估计、双足、全身操作 | 有（项目页） | Go2 | I D K | 全(部分) |
| 15 | MARG: risky gap terrains with elevation mapping | T-RO 41 2025 | Go2 | 危险缝隙落足 | 高程图+本体 DRL | 依赖 LiDAR 精度；仅 trot；9 cm 窄梁成功率低；将做软滑地形 | 未读到 | Go2 | B C | 全 |
| 16 | One Filter to Deploy Them All | T-RO 42 2026 | Go1 | 未知环境四足安全 | 可达性值网络安全滤波 | 仍有碰撞；扰动超估计界；验证集保证难外推；保守；将做在线标定 | 未读到（有项目页） | 否 | E J | 全(部分) |
| 17 | Traversability-Aware Legged Navigation From Real-World Visual Data | T-RO 42 2026 | Go1 | 视觉可通行性导航 | 价值函数估通行性+分层 RL | 未读到 | 未读到 | 否 | X | 全(无局限) |
| 18 | DreamWaQ++ | T-RO 42 2026 | Go1（另 A1 等） | 感知失效下避障 | 本体+外感知多模态 RL | 将给相机加主动倾斜；潜变量随种子而异；地图缺长期记忆 | 未读到 | 否 | B C G | 全(部分) |
| 19 | Chambolle–Pock Whole-Body Controller | T-RO 42 2026 | 四足(型号未读到) | 全身控制安全与能效 | RL+Chambolle-Pock QP WBC | 未读到 | 有（匿名仓库） | 未知 | X | 摘 |
| 20 | Spine-Based Quadruped Locomotion via RL | T-RO 42 2026 | 仿生脊柱四足 | 脊柱四足极限速度 | RL 提取脊柱运动模板 | 未读到 | 未查 | 否 | X | 摘 |
| 21 | Agile and Generalized Legged Locomotion via Attention-Based Neural Map Encoding | T-RO 42 2026 | ANYmal-D+TRON1 | 复杂地形泛化 | 注意力地图编码+学习建图 | 仅 2.5D；高草/雪等感知退化不适用；动态遮挡失效；将做多层图、体素 | 未查（有项目页） | 否 | B C G | 全 |
| 22 | ALORE: large-object rearrangement with a legged manipulator | T-RO online 2026 | B2+Z1 | 大物体重排 | 分层 RL+速度估计器 | 目标位姿需预知；仅泛化到相近构型；摩擦变化降性能；将做多物体 | 有（项目页） | 否 | C K | 全 |

### 1.4 RA-L（轮足相关论文标 **W**）

| # | 标题 | 期刊卷期年 | 平台 | 问题 | 方法核心 | 作者自述局限/未来工作 | 代码 | Go2/Go2-W | 类型 | 源 |
|---|---|---|---|---|---|---|---|---|---|---|
| 23 | Robust Locomotion Policy With Adaptive Lipschitz Constraint | RA-L 10(1) 2025 | Go1 | 观测噪声下动作抖动 | 自适应 Lipschitz 约束 | 未读到 | 无 | 否 | X | 摘 |
| 24 | Variable-Frequency Model Learning and Predictive Control for Jumping | RA-L 10(2) 2025 | A1 | 长腾空跳跃精度 | 残差模型学习+变频 MPC | 线性化 MPC 远离参考时精度降；将做非线性 MPC、线足、滚动、软接触 | 有 github.com/DRCL-USC/Learning_MPC_Jumping | 否 | J K | 全 |
| 25 | Non-Gaited Legged Locomotion With MCTS and Supervised Learning | RA-L 10(2) 2025 | Aliengo | 非周期步态实时规划 | MCTS+监督价值函数+MPC | 长腾空需更长规划域；重规划预算限节点数；将融合视觉 | 未查 | 否 | B D | 全 |
| 26 **W** | Whole-Body Loco-Manipulation for Pose Tracking With a Wheeled-Quadrupedal-Manipulator | RA-L 10(2) 2025 | LimX W1+臂（轮足） | 轮足臂 6D 位姿跟踪 | 奖励融合+师生 RL | 策略无感知，狭窄空间或有障碍需更强协调；将加感知 | 无（项目页） | 否（W1） | B C K | 全 |
| 27 | See-Touch-Predict | RA-L 10(4) 2025 | Go1 | 在线感知地形物理 | 主动探测估摩擦+地形分类 | 仅摩擦系数；纯纹理分类随场景增大变差；无恢复机制 | 未查 | 否 | B C J | 全 |
| 28 | RoboDuet | RA-L 10(5) 2025 | Go1+ARX5（Go2 零样本） | 四足带臂全身协同 | 运动与臂策略协作两阶段 | 仅低层控制，需接高层规划与碰撞检测；楼梯等复杂地形未做 | 有（项目页） | Go2 | C K | 全 |
| 29 | FR-Net: fall recovery via mass-contact prediction | RA-L 10(7) 2025 | Go2 | 复杂地形倒地恢复 | 质量-接触预测网络 | 无精确接触位置（如缝隙）；将加触觉传感器 | 无 | Go2 | B K | 全 |
| 30 | ALARM: Safe RL With Reliable Mimicry | RA-L 10(7) 2025 | Go1 等 | 安全鲁棒足式运动 | 一步师生+NP3O 约束 | 未读到 | 有 github.com/SUCRO-Legged/ALARM | 否 | X | 摘 |
| 31 | FT-CPG: CPG for fault-tolerant quadruped locomotion | RA-L 10(7) 2025 | Go1（未核实） | 多关节故障容错 | 学习 CPG | 未读到 | 未查 | 否(未核实) | X | 无 |
| 32 | Whole-Body Constrained Learning via Hierarchical Optimization | RA-L 10(7) 2025 | 六足 Elspider-Air | RL 约束保证 | 层级优化全身跟随器 | 调约束会改变策略风格；将在线辨识更多地形参数 | 无（项目页） | 否 | E J | 全 |
| 33 | VR-Robo: real-to-sim-to-real | RA-L 10(8) 2025 | Go2 | 视觉导航与运动 | 3DGS 重建+仿真训练 | 仅静态室内；每任务从头训约 3 天；RGB 网格需人工修补；将做更大场景 | 项目页，未见代码 | Go2 | C D B | 全 |
| 34 | OmniNet: omnidirectional jumping | RA-L 10(8) 2025 | 四足(型号未读到) | 全向可控高度跳跃 | 训练框架+在线状态估计 | 未读到 | 未查 | 未知 | X | 摘 |
| 35 | Modular Residual Learning for Model-Based Locomotion | RA-L 10(9) 2025 | Go1 | MPC 模型失配鲁棒 | RL 残差调落足+监督修正动力学 | 需更广条件评估；将扩展到地面软度、打滑等不确定性 | 无（项目页） | 否 | C J | 全 |
| 36 | Deep Disturbance Observer for Locomotion Robustness | RA-L 10(9) 2025 | 四足(型号未读到) | 不确定性下鲁棒 | 策略+深度扰动观测器 | 未读到 | 未查 | 未知 | X | 摘 |
| 37 | Safe Quadruped Traversal Using Multi-Layer Elevation Maps | RA-L 10(10) 2025 | 四足(报道称 Go1) | 复杂地形安全通行 | 多层高程图+分层控制 | 未读到 | 未查 | 否 | X | 摘 |
| 38 | Fault Joint Detection and Adaptive Fault-Tolerant Control | RA-L 10(10) 2025 | 四足(普查表 A1) | 关节部分失效容错 | 故障关节检测+自适应容错 | 未读到 | 普查表标有，未核 | 未知 | X | 无 |
| 39 | Multi-Stage Pick-and-Place With a Legged Mobile Manipulator (SLIM) | RA-L 10(11) 2025 | Go1+WidowX | 语言指令长时程拾放 | 纯仿真训练零样本部署 | 将增加场景、视觉语言多样性、物体与任务；失败含抓取时踢飞物块 | 无（项目页） | 否 | C G K | 全 |
| 40 | RENet: Redundant Estimator Networks Under Visual Collapse | RA-L 10(11) 2025 | Go1 | 视觉退化容错 | 双估计器+异常检测切换 | 缺 3D 语义理解；强光下鲁棒有限；将加语义感知、试人形 | 无（项目页） | 否 | B C F | 全 |
| 41 | Heavy Hydraulic Robot Using an Actuator Model | RA-L 10(12) 2025 | 液压四足 >300 kg | 重型液压 sim2real | 解析液压执行器模型 | 未测训练外工况；耐久未评；速度未超 1 m/s；将试更高速、更多平台 | 无 | 否 | A C F | 全 |
| 42 | MULE: Multi-Terrain and Unknown Load Adaptation | RA-L 11(1) 2026 | Go1 | 变载荷+多地形 | 名义策略+自适应修正策略 | 未读到（结论无局限段） | 无（项目页） | 否 | X | 全(无局限) |
| 43 | MLM: Multi-Task Loco-Manipulation WBC | RA-L 11(1) 2026 | Go2+Airbot 臂 | 单策略多任务移操作 | 轨迹库+自适应采样 | 性能受扩散策略推理限制；将经高层决策扩任务；动态任务需更快传感与执行器响应 | 无 | Go2 | G K A | 全 |
| 44 | Primal-Dual iLQR for GPU-Accelerated Learning and Control | RA-L 11(1) 2026 | Go2/Aliengo/Talos | MPC 并行加速 | JAX 并行扫描 PD-iLQR | 将把该 MPC 作运动策略学习先验；完善不等式约束 | 有 github.com/iit-DLSLab/mpx | Go2 | E D | 全 |
| 45 | VOCALoco: viability-optimized cost-aware locomotion | RA-L 11(2) 2026 | ANYmal-D | 选安全节能技能 | 预测技能可行性与运输成本 | 将从离散切换扩展到策略混合，实现连续过渡 | 无（项目页） | 否 | G B | 全 |
| 46 | PPL: Point Cloud Supervised Proprioceptive Locomotion in Crawl Spaces | RA-L 11(2) 2026 | Go2 | 低矮空间爬行 | 点云监督本体估计 | 将在机身加触觉传感器；PPL-Net 可用于 3D 混合运动 | 未读到 | Go2 | C B | 全 |
| 47 | Adaptive Legged Locomotion via Online Learning for MPC | RA-L 11(2) 2026 | Go2（仅仿真） | MPC 未建模扰动 | MPC+在线随机傅里叶特征残差 | 极端条件仍会失败；无未来工作；无真机 | 有 github.com/UM-iRaL/Adaptive-Legged-Locomotion | Go2 | J A | 全 |
| 48 | Transformer Observer-Based Contact Force Estimation | RA-L 11(2) 2026 | A1+臂 | 动量观测器依赖模型 | 超扭曲观测器+Transformer | 未读到（无局限或未来工作） | 未读到 | 否 | X | 全(无局限) |
| 49 | START: Sparse Footholds With Terrain Reconstruction | RA-L 11(2) 2026 | Lite3 | 稀疏落脚点 | TR-Net 重建高程图 | 仅评测四类地形；将加强边缘保持、探索体素 | 未读到 | 否 | C B | 全 |
| 50 | Attention-Based Neural-Augmented Kalman Filter | RA-L 11(4) 2026 | 足式(Go1 模型) | 打滑下状态估计 | InEKF+滑移注意力补偿 | 接触误判持续则滑移失真；室外前向尺度误差；将用于控制并扩展到轮式机器人 | 未读到（项目页） | 否 | I F | 全 |
| 51 | Efficient Exploration Using GNN With Global Attention | RA-L 11(4) 2026 | 四足 | 未知环境探索 | 拓扑图 GNN+注意力 RL | 未读到 | 普查表标有，未核 | 未知 | X | 摘 |
| 52 | VPIES: Variational Privileged Information Encoder | RA-L 11(4) 2026 | Go2+G1 | 特权信息依赖 | 变分特权编码器 | 未读到 | 未读到 | Go2 | X | 摘 |
| 53 | Quadrupedal Jumping and Walking Using RL | RA-L 11(4) 2026 | 自研 Jumper | 跳跃与行走 | 课程学习无参考轨迹 | 全向泛化损峰值跳跃；扭矩极限处性能降；需弥合 sim2real | 未读到 | 否 | C A G | 全 |
| 54 | Gait-Parameterized RL for a Hydraulic Quadruped | RA-L 11(5) 2026 | 液压四足 350 kg | 奖励难调 | 策略输出步态参数 | 未读到 | 未查 | 否 | X | 摘 |
| 55 **W** | RL-Augmented MPC for Non-Gaited Legged and Hybrid Locomotion | RA-L 11(5) 2026 | Centauro、B2-W、50 kg 四足 | 非步态足式/轮足混合 | SAC 定接触+全刚体 MPC | 策略只针对特定 MPC 与机器人；待做通用策略、落足点控制、持续强扰动评估 | 有 github.com/AndrePatri/AugMPC | 否（B2-W） | C F E | 全 |
| 56 | EFGCL: External Force Guided Curriculum Learning | RA-L 11(5) 2026 | KLEIYN 四足 | 稀疏奖励动态动作 | 外力辅助课程 | 辅助力靠启发式；只验证单次动作；连续行为需自动生成辅助力 | 未读到 | 否 | C G | 全 |
| 57 | Dynamic Legged Ball Manipulation With Hierarchical RL | RA-L 11(6) 2026 | Go2 | 崎岖地形运球 | 高层协调+DSF-PO | 将加速收敛；球位置扩到三维；接入更多底层技能 | 无（项目页） | Go2 | D C G | 全 |
| 58 **W** | Wheel-Legged Robot via ADP and Data-Driven Value Iteration | RA-L 11(6) 2026 | 轮足 | 未读到 | 未读到 | 未读到（检索不到） | 未查 | 未知 | X | 无 |
| 59 | Teacher-Guided Terrain-Aware Learning for Recovery | RA-L 11(6) 2026 | 四足，轮式 Kyon 跨平台验证 | 不平地形倒地恢复 | 姿态优化+师生 RL | 未读到 | 有（项目页） | 未知 | X | 摘 |
| 60 | Dynamic Pick-and-Place for a Legged Manipulator | RA-L 11(6) 2026 | 自研四足+Z1 | 动态抓放 | 分层 RL+质量估计 | 将用自我中心视觉替代动捕；泛化更多物体；载荷限 1.3 kg | 无 | 否 | B C K | 全 |
| 61 | HiPAN: Hierarchical Posture-Adaptive Navigation | RA-L 11(7) 2026 | Go1 | 非结构化 3D 导航 | 深度图发速度与姿态 | 玻璃等透明/镜面深度失败；将加语义识别 | 无（项目页） | 否 | B C | 全 |
| 62 | X-IONet: Cross-Platform Inertial Odometry | RA-L 11(7) 2026 | 行人+四足（自采 Go2 数据） | 跨平台惯性里程计 | 规则选专家网络+EKF | 仅评估行人与四足；未见机器人、异构 IMU 待探索 | 未读到 | Go2（数据） | F C I | 全 |
| 63 | Dynamic Policy Learning: Simplified Model Pretraining and Homotopy Transfer | RA-L 11(7) 2026 | Go1 | 动态动作 RL 收敛慢 | 单刚体预训练+模型同伦 | 依赖预定义接触序列与摆动轨迹；将隐式学接触时序 | 无 | 否 | C G | 全 |
| 64 **W** | Robust Fall Recovery for Armless Bipedal-Wheeled Robots (FTSR) | RA-L 11(8) 2026 | 自研无臂双足轮足 | 轮足倒地恢复 | 力引导+师生蒸馏 | 将在更广泛平台测试；无单独局限节 | 无（项目页） | 否 | F | 全 |
| 65 | Real-to-Sim-to-Real: Recovery With Terrain Imagination | RA-L 11(8) 2026 | Go2（普查表） | 未读到 | 未读到 | 未读到 | 未查 | Go2(未核) | X | 无 |
| 66 | Scaling Rough Terrain Locomotion With Automatic Curriculum RL | RA-L 11(8) 2026 | ANYmal-D | 手工课程难扩展 | 学习进度自动课程 | 未读到（结论无局限段） | 无（项目页） | 否 | X | 全(无局限) |
| 67 | TCLL: Temporal-Aware Contrastive Latent Learning | RA-L 11(8) 2026 | 多种足式 | 未读到 | 未读到 | 未读到 | 未查 | 未知 | X | 无 |
| 68 | PUMA: Perception-Driven Unified Foothold Prior | RA-L 11(9) 2026 | Lite3 | 四足跑酷落足 | 深度预测落足先验 | 仅深度几何，无语义/材质；静态训练；将加语义与时序推理 | 无 | 否 | B C | 全 |
| 69 | QLIMB: Whole-Body Control for Loco-Manipulation and Balance | RA-L 11(9) 2026 | 小型四足+臂 | 未读到 | 未读到 | 未读到 | 未查 | 未知 | X | 无 |
| 70 **W** | Agile Wheel-Bipedal Loco-Manipulation With Active Force Rejection | RA-L 11(9) 2026 | 双足轮足+臂 | 接触任务外力扰动 | NN-EKF 估外力+WBC | 未读到（出版页摘要无局限） | 未查 | 否 | X | 摘 |
| 71 | Kinematic Residual Compensation With Latent Regime MoE for Odometry | RA-L 11(10) 2026 | Go1/ANYmal | 未读到 | 未读到 | 未读到 | 未查 | 未知 | X | 无 |
| 72 | Extending the Speed Limit via Refined Actuator Modeling | RA-L 11(11) 2026 | BlackPanther2 | 高速 sim2real 差距 | 含电压耦合/磁饱和执行器模型 | 可加离线轨迹优化与关节负载均衡目标；可加主动腰关节 | 无 | 否 | A H | 全 |
| 73 | Rationality Randomization for Dynamic Obstacle Avoidance | RA-L 11(11) 2026 | 足式（疑 Go1，仅仿真） | 动态避障鲁棒 | 量子响应对抗 RL | 仅处理前方单个障碍；将扩到任意数量；**arXiv 版（题目不同）是否同一篇未确认** | 未查 | 否 | C | 全(疑) |
| 74 | CATR: Confidence-Aware Terrain Reconstruction | RA-L 11(11) 2026 | Go1 | 未读到 | 未读到 | 未读到 | 未查 | 未知 | X | 无 |
| 75 | PAINT: Partner-Agnostic Cooperative Transport | RA-L 11(11) 2026 | ANYmal(±臂) | 无力传感协同搬运 | 本体推断力旋量+师生 | 无主动避障；仅平面力旋量；将扩 6D、语义意图 | 无（项目页） | 否 | C E K | 全 |
| 76 | Terramechanics-Aware Adaptive Locomotion via Foot-Terrain Model | RA-L 11(11) 2026 | Go2（普查表） | 未读到 | 未读到 | 未读到 | 未查 | Go2(未核) | X | 无 |
| 77 | From Policy Actions to Whole-Body Dynamics (PADP) | RA-L 11(11) 2026 | 足式 | 未读到 | 未读到 | 未读到 | 未查 | 未知 | X | 无 |
| 78 | Terrain-Aware WBC for Perceptive Legged Loco-Manipulation | RA-L 11(11) 2026 | B2+Z1 | 腿式操作缺地形感知 | 足接触面采样+双策略蒸馏 | 无独立局限节；将做高层策略与之衔接实现全自主 | 未查到 | 否 | G K | 全 |
| 79 **W** | Wheeled-Legged Robots Reflexive Obstacle Evasion (AWARE) | RA-L 11(11) 2026 | M20 轮足四足 | 轮足高动态避障 | 分层 RL+速度课程 | M20 硬件限制使系统无法完全激活，sim2real 差距降成功率；无未来工作 | 未查到 | 否 | A | 全 |
| 80 | LA-WBC: Learning-Driven Adaptation of WBC | RA-L 11(12) 2026 | 四足 | 未读到 | 未读到 | 未读到 | 未查 | 未知 | X | 无 |
| 81 **W** | YMSkater: Skating Locomotion via Model-Guided RL | RA-L 11(12) 2026 | 人形+被动轮 | 未读到 | 未读到 | 未读到 | 未查 | 未知 | X | 无 |
| 82 | PolyMorph: Cross-Embodiment Adaptation | RA-L 11(12) 2026 | 多形态（Raibo 真机） | 单策略跨形态 | URDF 转关节模块+图 Transformer | 泛化限训练形态范围，强外推退化；将做 URDF 扰动增广 | 无 | 否 | F C | 全 |
| 83 | Spine-Assisted Bounding for Gap Crossing | RA-L 11(12) 2026 | 小型脊柱四足 | 未读到 | 未读到 | 未读到 | 未查 | 未知 | X | 无 |
| 84 **W** | RAIWAY: Large-Wheeled Bipedal Robot Blind Locomotion | RA-L 11(12) 2026 | 大轮双足 28 kg | 大轮盲走不连续地形 | 接触特权蒸馏为潜变量 | 仿真未建模边缘/胎面啮合；将引入外感知、更高速度 | 无 | 否 | A B C | 全 |
| 85 | E2DRL: Differentiable RL for 3D Obstacle Avoidance | RA-L 12(1) 2027 | Go2 | 3D 避障 | 可微 RL+停梯度整形 | 依赖机载深度，反光/透明/噪声下退化；将提升感知鲁棒、扩展场景 | 无 | Go2 | B C | 全 |
| 86 | Pretraining in Actor-Critic RL for Locomotion | RA-L 11(9) 2026 | ANYmal-D/Go1/G1 | 提升样本效率 | 逆动力学预训练 actor/critic | 将缩小网络、引入时序结构 | 无 | 否 | D F | 全 |

### 1.5 Nature 系

| # | 标题 | 期刊卷期年 | 平台 | 问题 | 方法核心 | 作者自述局限/未来工作 | 代码 | Go2/Go2-W | 类型 | 源 |
|---|---|---|---|---|---|---|---|---|---|---|
| 87 | A quadruped robot designed to complete a marathon on a single battery charge | Nature 658(8135) 2026 | RAIBO2 | 单次充电跑马拉松 | 机电驱控全系统协同降耗 | 论文原文未读到；仅新闻稿称量产需一致性、防水尘、宽温、抗振、EMI | 未查 | 否 | （H E C，新闻稿，不计） | 摘 |
| 88 | FLAIR: reconstituting control with online learning | Nat. Commun. 17(1) 2026 | 多平台(仿真六足、GVR-Bot) | 突发扰动后恢复 | 现有控制器上叠加在线学习 | 未读到有效局限（补充材料一句话，不计） | 有 github.com/adaptive-intelligent-robotics/FLAIR | 否 | J E（不计） | 摘 |
| 89 | Learning diverse natural behaviors for agility of quadrupedal robots | Nat. Commun. 17(1) 2026 | Go2 | 敏捷自然行为 | 犬动捕半监督 GAIL+隐变量 | 将用更大规模犬户外动捕训练更鲁棒基础控制器；融合多模态理解意图（依据预印本） | 项目页，未核代码 | Go2 | C G B | 全(预印本) |
| 90 | Koopman global linearization of contact dynamics | Nat. Commun. 17(1) 2026 | 足式+操作 | 接触切换动力学难控 | Koopman 线性化+凸 MPC | 未读到 | 未查 | 未知 | X | 摘 |
| 91 | Bio-inspired gait strategies for versatile quadruped locomotion | Nat. Mach. Intell. 7(7) 2025 | A1 | 单一步态难适应地形 | 步态切换+程序记忆+自适应 DRL | 真机无法精确测基座线速度；将与无 Froude 数运动工作结合 | 有 github.com/ihcr/learning_to_adapt | 否 | I G C | 全 |

## 2. 跨领域来源表（仅已正式发表；预印本已忽略）

| 来源论文 | 出处 | 领域 | 核心技术 | 能迁移到轮足的具体技术点 |
|---|---|---|---|---|
| X1 Deep Dynamics | RA-L 9(6):5292, 2024 | 车辆动力学 | 物理约束网络+Physics Guard 限幅 | 估计轮地摩擦与滑移系数，限幅后作滑移转向代理模型 |
| X2 One Model to Drift Them All（正式标题含 Physics-Informed Conditional Diffusion） | CoRL 2024, PMLR 270 | 车辆漂移 | 条件扩散生成物理参数+MPC | 按在线测量生成地面/滑移参数分布，供 MPC 或策略条件化 |
| X3 Shafiee, Bellegarda, Ijspeert | Nat. Commun. 15:3073, 2024 | 生物力学 | CPG+DRL，可行性驱动步态转换 | 以防跌倒可行性设计腿/轮模式切换触发信号 |
| X4 Lee 等（轮足导航与运动，本身即轮足） | Sci. Robot. 9(89), 2024 | 轮足 | 特权学习 RL，走-驶自发切换+分层导航 | 直接对照：特权学习训练运动控制器与分层导航 |
| X5 Han 等（Tencent MAX） | Nat. Mach. Intell., 2024（卷号 6(7) 与 arXiv 页标 7 不一致，未核实） | 图形学 | 动物动作生成式预训练+分层 | 以生成式运动先验给轮足提供步态原语 |
| X6 Flow Matching Policy Gradients (FPO) | ICLR 2026 | 生成式 RL | 流匹配替代对数似然，兼容 PPO | 在 PPO 流程里用流策略表示滚/迈二选一的多模态动作 |
| X7 Su 等 Leveraging Symmetry | IROS 2024 | 对称性 RL | 等变网络或数据增广 | 利用左右对称做等变网络/增广，改善滑移转向样本效率 |
| X8 Mittal 等 Symmetry Considerations | ICRA 2024 | 对称性 RL | 数据增广/镜像损失 | 镜像增广解决前后、左右转行为不一致 |
| X9 Shi 等 Rethinking Robustness Assessment | RSS 2024 | 鲁棒性评估 | 序贯对抗攻击找失效点 | 对轮足策略做对抗扰动测试并回训加固 |
| X10 LCP（正式标题 Learning Smooth Humanoid Locomotion through Lipschitz-Constrained Policies） | IROS 2025 | 平滑控制 | 可微 Lipschitz 梯度惩罚 | 用 Lipschitz 惩罚替代平滑奖励与低通，使轮速指令更平滑 |
| X11 FIPER | NeurIPS 2025 | 策略安全 | RND 分布外分数+动作熵+共形校准 | 给生成式轮足策略加运行时失效预警，触发模式切换 |
| X12 Song 等 Reaching the limit in autonomous racing | Sci. Robot. 8(82), 2023 | 无人机竞速 | RL 对比最优控制并归因 | 轮足上比较 RL 与最优控制，按目标/分解/模型误差归因 |
| X13 Zhang 等 Extreme Adaptation | T-RO 2025 | 四旋翼 | 模仿+RL，历史估系统参数潜变量 | 从历史观测估潜在参数，适应负载与地面变化 |
| X14 Song 等 Differentiable Simulation for Quadruped | CoRL 2024, PMLR 270:258 | 四足可微仿真 | 浮动基/关节空间分离+代理模型校正 | 可微仿真提升样本效率，可作 PPO 对照（仅读到摘要级） |
| X15 Cheng 等 L1 Adaptive Control for RL | RA-L 7(3), 2022 | 自适应控制 | 预训练 RL 策略外挂 L1 环 | 不重训即外挂 L1，补偿轮足参数偏移与扰动 |
| X16 Heavy metal acrobatics（滑移转向装载机） | Sci. Robot. 11(120), 2026（原文 403 未读到，细节依据新闻稿与检索摘要） | 滑移转向重型机械 | 仿真 RL+sim2real，两轮平衡/原地旋转 | 滑移转向 RL sim2real 方法与评价动作（细节未读到） |
| X17 Learning Without Critics? | NeurIPS 2025（**未能确认是主会**，arXiv 页未标会议） | RLVR/GRPO | 无 critic 的 GRPO | 结论偏负面：长时程连续控制仍需 critic |
| X18 MaskedMimic | ACM TOG（SIGGRAPH Asia 2024） | 图形学 | 掩码运动补全统一多种输入 | 用掩码约束统一速度指令与腿姿指令，平滑切换 |
| X19 Swift（Kaufmann 等） | Nature 620:982, 2023 | 无人机竞速 | 仿真 RL+真实数据残差动力学 | 真实数据拟合轮-地残差，修正仿真 |

**已按"预印本"忽略**：SkateNav、SKooP、MS-PPO、RAPT、Learning to Drift with Individual Wheel Drive、FPO++、FLORES、Racing a Wheeled Quadruped（AVEC 2026 仅录用）、pulse-and-glide 一类。Hoyt & Taylor 1981、Fu CoRL 2021、Mandow IROS 2007、Jalalnezhad JVET 2026、MoE-Loco 等未抽取（会议或出处待核，且不在范围内的部分未读）。

## 3. 按局限类型聚类（仅 57 篇读到局限者；一篇可多类）

| 类型 | 篇数 | 编号 |
|---|---|---|
| C 泛化范围有限 | 37 | 1 2 3 4 6 10 13 15 18 21 22 26 27 28 33 35 39 40 41 46 49 53 55 56 57 60 61 62 63 68 73 75 82 84 85 89 91 |
| B 感知依赖或失效 | 22 | 1 2 4 11 15 18 21 25 26 27 29 33 40 45 46 49 60 61 68 84 85 89 |
| G 多技能、模式切换、长时程 | 15 | 4 6 11 18 21 39 43 45 53 56 57 63 78 89 91 |
| K 接触交互/操作 | 14 | 2 3 9 14 22 24 26 28 29 39 43 60 75 78 |
| A 仿真到真机/执行器差距 | 10 | 5 6 12 41 43 47 53 72 79 84 |
| F 跨平台/形态迁移 | 10 | 9 13 40 41 50 55 62 64 82 86 |
| D 训练成本/样本效率 | 7 | 3 14 25 33 44 57 86 |
| E 安全/约束/可靠性 | 7 | 5 9 16 32 44 55 75 |
| J 在线适应/未建模动力学 | 7 | 12 16 24 27 32 35 47 |
| I 状态估计误差 | 5 | 13 14 50 62 91 |
| H 能效/热/续航 | 3 | 11 12 72 |
| X 未读到局限 | 34 | 7 8 17 19 20 23 30 31 34 36 37 38 42 48 51 52 54 58 59 65 66 67 69 70 71 74 76 77 80 81 83 87 88 90 |

## 4. 作者明确写出、且可与轮足或 Go2/Go2-W 衔接的未来工作（15 条）

| 序 | 论文 | 作者原文要点 | 衔接点 |
|---|---|---|---|
| 1 | #9 IJRR 综述 | 轮足混合运动是值得研究的方向，其步态生成并不直观 | 轮足 |
| 2 | #13 GrandTour | 数据集将增加双足、轮足等形态 | 轮足 |
| 3 | #26 轮足四足臂 | 为策略加入感知信息以应对障碍与狭窄空间 | 轮足 |
| 4 | #50 AttenNKF | 将框架扩展到空中、轮式机器人 | 轮式 |
| 5 | #55 RL-Augmented MPC | 扩展通用策略、控制落足点、评估强持续扰动鲁棒性（含 B2-W 平台） | 轮足 |
| 6 | #64 FTSR | 在更广泛平台上测试轮足倒地恢复 | 轮足 |
| 7 | #84 RAIWAY | 引入外感知、更高速度、更复杂不连续地形 | 轮足 |
| 8 | #85 E2DRL | 提升机载深度感知鲁棒性、扩展到复杂场景 | Go2 |
| 9 | #44 PD-iLQR | 把 GPU 并行 MPC 作为运动策略学习先验，完善不等式约束 | Go2 |
| 10 | #28 RoboDuet | 接入高层规划与碰撞检测（已在 Go2 零样本迁移） | Go2 |
| 11 | #33 VR-Robo | 扩展到更大场景并引入生成模型 | Go2 |
| 12 | #46 PPL | 机身加触觉传感器，PPL-Net 用于 3D 混合运动 | Go2 |
| 13 | #62 X-IONet | 扩展到更多平台、未见机器人、异构 IMU | Go2 数据 |
| 14 | #14 STMR | 更好的接触估计、双足、全身操作（已在 Go2 真机验证） | Go2 |
| 15 | #43 MLM | 经高层决策扩展任务；动态任务需更快传感与执行器响应 | Go2 |

**说明**：#79 AWARE（M20 轮足）只写了硬件与 sim2real 的局限，没有未来工作，故未入表。91 篇中没有任何一篇在原文里提到 Go2-W。
