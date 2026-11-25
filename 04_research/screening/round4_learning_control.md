# 第四轮粗筛：跳出“辨识/适应/热/雷达避障”循环的学习与控制新方向

检索日期：2026-11-25。范围：arXiv、RA-L、IROS、ICRA、CoRL（PMLR）、RSS 2026 论文集、AVEC 2026、GitHub API（未登录，按仓库元数据记 `pushed_at`）。
本轮刻意**不推荐** PACE、ASAP、TEMPO、热约束、雷达避障，只在对比时提及。
标注约定：**[事实]** 指本轮直接从 arXiv 页面、论文集或仓库读到的信息；**[评价]** 是我的判断；**未核实**指本轮没能查实的内容。所有数字都取自所列页面，没有凭记忆补充。

---

## 0. 结论先行（评价）

| 方向 | 一句话 | 推荐基础论文 | 综合判断 |
|---|---|---|---|
| A. 轮足**学习型本体里程计**（轮速+IMU+腿运动学，滚动/迈步混合接触） | 用仿真训练的网络加滤波器，估计 Go2-W 在打滑、滚走混合时的速度和位姿，用 LiDAR 里程计当真值 | Legolas（CoRL 2024，PMLR 270, 2025）＋ InNKF（IROS 2025）作为“滤波器＋学习补偿”的结构参照 | **最稳**：实机风险最低，与传统估计正面对话，但没有官方代码，需要自行实现 |
| B. 3DGS **real-to-sim 视觉策略迁移到轮足** | 把 VR-Robo 的高斯泼溅数字孪生流程搬到 Go2-W，让 RGB 策略同时决定“去哪”和“滚还是走” | VR-Robo（RA-L 2025，官方代码，Go2，Isaac Lab） | **论文观感最强、代码基础最好**，但工程量最大，与传统控制对话较弱 |
| C. 轮足高速运动的**学习型安全过滤器**（侧翻/失稳） | 用对抗 RL 学到的 reach-avoid Q 函数做运行时过滤，与 LTR 约束 MPC 正面对比 | Gameplay Filters（CoRL 2024，PMLR 270，Go2，官方代码）＋ Go2-W Racing MPC（AVEC 2026，MPC 代码公开）作为传统对照 | **答辩最好讲**，但实机有侧翻风险，代码栈老，需要移植 |

总体判断（评价）：三者都避开了前几轮的循环。若首要目标是“一定能在 3–4 个月做完并有实机结果”，选 **A**；若首要目标是“论文吸引力和后续可扩展性”，选 **B**；**C** 适合作为 A 或 B 的备选，或缩成其中一章。

---

## 1. 候选论文卡片（12 篇，按方向分组）

### 1.1 视觉策略与 real-to-sim

#### (1) VR-Robo: A Real-to-Sim-to-Real Framework for Visual Robot Navigation and Locomotion
- **发表状态**：[事实] arXiv 2502.01536 v3 页眉写明 RA-L 2025 录用，DOI 10.1109/LRA.2025.3575648；项目页也标为 RA-L 2025。RA-L 正式页码未核实。
- **代码**：[事实] https://github.com/zst1406217/VR-Robo ，最近 push 2025-06-20，约 200 星，MIT 许可。README 说已发布 real2sim 和 RL 训练代码（2025-06-14）；训练用 **Isaac Lab**（`vrrobo_isaaclab`），渲染另起服务（`vrrobo_renderer`），两套 conda 环境。任务名为 `go2_gs`。README 没提到预训练权重和场景数据，CUDA 版本也没写。
- **平台**：[事实] Unitree Go2，机载 Jetson Orin Nano，Insta360 Ace RGB（320×180）。
- **核心想法**：[事实] 用 3DGS 渲染外观，mesh 负责碰撞，组成数字孪生。策略分两层：高层 5 Hz PPO，输入冻结的 ViT-Tiny 特征、目标颜色、上一动作和本体，输出速度指令；底层 50 Hz LSTM+MLP 输出关节位置。任务是在 15 s 内只凭 RGB 到达指定颜色的锥桶，部分锥桶要经斜坡或台阶才能到。
- **结果**：[事实] 实机 Easy/Medium/Hard 成功率 100%/93.33%/100%；CNN 编码器为 73.33%/66.67%/6.67%，纹理 mesh 为 20%/6.67%/0%。训练用一张 4090D，约 3 天。作者自述局限：只有室内静态场景；每个任务约 3 天；仅用 RGB 重建的 mesh 有结构缺陷，需要人工修补。
- **Go2-W 上的创新点**：[评价] ① **轮足模式感知**：高层同时输出速度和“滚/走”倾向，比如平地滚行、遇台阶迈步，原文底层只有腿式行走。② **用 Go2-W 自带 LiDAR 修几何**：直接针对原文“仅 RGB 重建 mesh 有缺陷”这条局限。③ 从室内扩到室内外走廊。
- **复现与实机难点**：[评价] 两套环境加渲染服务器，工程链长；Isaac Lab 在 Blackwell 上应选 Isaac Sim 5.x 系列，具体版本兼容性未核实；底层轮足策略要自己训；Go2-W 前置相机的画质和 FOV 与 Insta360 不同，要重新标定。

#### (2) GaussGym: An open-source real-to-sim framework for learning locomotion from pixels
- **发表状态**：[事实] arXiv 2510.15352（2025-10-17，v1），comments 字段无录用信息，**会议录用未核实**。作者为 Escontrela、Kerr、Allshire、Frey、Duan、Sferrazza、Abbeel。
- **代码**：[事实] https://github.com/escontra/gauss_gym ，最近 push 2025-10-30，约 393 星。`setup_dev.sh` 会下载 **Isaac Gym Preview 4**；配置覆盖 A1、Go1、T1、ANYmal C 的 vision 版，README 说“只有 a1 和 t1 在硬件上验证过”。预训练策略和部署代码仍列在 TODO 中。场景从 Hugging Face 下载。
- **核心想法**：[事实] 把 3DGS 当作 IsaacGym 的渲染层，论文称单张 4090 上 4096 个环境可超过 10⁵ steps/s；自带 2500 个场景；在实机上演示了视觉爬楼梯。
- **Go2-W 创新点**：[评价] 场景规模适合做“轮足在大量真实外观场景中的视觉地形识别”。
- **难点**：[评价] Isaac Gym Preview 4 能否在 sm_120（Blackwell）上运行**未核实，风险较高**；没有 Go2/Go2-W 配置，也没有部署代码。

#### (3) GS-Playground: A High-Throughput Photorealistic Simulator for Vision-Informed Robot Learning
- **发表状态**：[事实] **RSS 2026**，论文集 PDF 首页写有 “Robotics: Science and Systems 2026”；arXiv 2604.25459。
- **代码**：[事实] https://github.com/discoverse-dev/gs_playground ，最近 push 2026-06-11，约 509 星。README 自称 “preview repository”：目前只有 Go2/G1 导航 demo 和回放 demo；物理引擎 MotrixSim 以 **Python 二进制包**形式提供；批量 3DGS 渲染器和 Real2Sim 在另外的仓库，**PPO/视觉策略训练脚本仍处于计划中**。依赖 CUDA 12.8 的 PyTorch wheel，仅支持 Linux x86_64。
- **平台**：[事实] Go2、G1、Airbot Play，没有 Go2-W。
- **评价**：引擎新、吞吐高，cu128 对 Blackwell 友好（推断）。但训练代码还没放出，**暂不适合作复现基础**，适合作为加速渲染的备选。

#### (4) ReaDy-Go: Real-to-Sim Dynamic 3D Gaussian Splatting Simulation for Environment-Specific Visual Navigation with Moving Obstacles
- **发表状态**：[事实] arXiv 2602.11575，comments 写明 RA-L 录用。
- **代码**：[事实] 只有项目页 https://syeon-yoo.github.io/ready-go-site/ ，没找到代码仓库。
- **核心想法**：[事实] 在静态 3DGS 场景里加入动态人体高斯化身，用 2D 轨迹生成人体运动，训练能避让行人的 RGB 导航策略，并零样本迁移到实机。机器人平台未核实。
- **用途**：[评价] 方向 B 的**查重近邻**，说明“动态障碍”这条扩展已有人做，不宜再选。

> 查重补充（不单列卡片）：**QuadVerse**（arXiv 2606.07118，未见录用信息，未见代码）在 3DGS 场景上同时标定空间变化的摩擦，并用真实轨迹训练残差动力学补偿器，做零样本视觉导航。这说明“视觉 real-to-sim + 动力学对齐”的组合已被占用，方向 B 应避开这一组合，也正好不再回到 PACE/ASAP 一类。

### 1.2 学习型状态估计（腿式 / 轮足）

#### (5) Legolas: Deep Leg-Inertial Odometry
- **发表状态**：[事实] CoRL 2024，收录于 PMLR 270（2025 年出版）；作者 Wasserman、Agarwal、Jangir、Chowdhary、Pathak、Gupta。
- **代码**：[事实] 项目页 learned-odom.github.io 只链接 OpenReview，**没有找到代码**。
- **平台**：[事实] 两台实机四足，项目页没有写明型号。
- **核心想法**：[事实] 只用腿部关节和 IMU 数据回归里程计，**不需要解析建模，也不需要采集真实数据**，训练数据来自仿真。项目页报告：室内相对位姿误差比解析滤波方法低 73%，比真实数据行为克隆低 87.5%；室外 180 m 漂移很小；地毯上 VIO 丢跟踪时，与 RTABMap 配合仍能建图。
- **Go2-W 创新点**：[评价] 把“仿真训练的腿-惯性里程计”扩展到**轮足混合接触**：轮子滚动时足端不再静止，传统零速假设失效，这正是解析方法难处理、学习方法可能有优势的地方。
- **难点**：[评价] 没有代码，需要自己实现；仿真里的轮胎打滑和气胎形变与实机差距会直接影响泛化，必须靠真实数据微调或在滤波器里融合来兜底。

#### (6) InNKF（IROS 2025）与 AttenNKF（RA-L 2026）
- **发表状态**：[事实] InNKF：arXiv 2503.00344，comments 写 “Accepted to IROS 2025”。AttenNKF：检索摘要称 RA-L 于 2026-01 录用（arXiv 2601.18569），**录用页本轮没有直接打开核实**。
- **代码**：[事实] 只找到 `seokju-lee/innkf_webpage`（项目页）和 `seokju-lee/attennkf`。后者 README 是通用学术主页模板，**没有算法代码**。
- **核心想法**：[事实] 在接触辅助的不变 EKF（InEKF）上加一个尊重李群结构的神经补偿器；AttenNKF 再按足端打滑严重程度做注意力补偿，在 InEKF 更新之后施加。
- **用途**：[评价] 这是“滤波器为主、学习只做残差补偿”的典范结构，**最适合拿来回应传统控制质疑**：滤波器保留可解释性，网络只修正模型误差。可作为方向 A 的方法骨架参照。

#### (7) Learning Wheel Motion Uncertainty for Degeneracy-Aware LiDAR-Inertial Odometry on Quadrupedal Wheel-Legged Robots
- **发表状态**：[事实] arXiv 2610.26550（2026-10-19），无录用信息。
- **代码**：[事实] 作者“计划公开”代码和多模态数据集，目前只有项目页 weihairuo.github.io/wheel-motion-uncertainty/。
- **核心想法**：[事实] 保留解析的轮子滚动预测，用 CovNet 从本体历史学习**逐轮、分方向的过程协方差**；CovNet 通过可微滤波器、用仿真速度监督训练，实机不微调。另用 DAP 抑制几何退化方向上的 LiDAR 约束。结果：退化度最高的 6 个房间序列上，平均位置 RMSE 比 FAST-LIO2 低 66.2%，比固定协方差版本低 31.0%；严重退化走廊的终点误差为 0.198 m，FAST-LIO2 为 7.531 m。
- **用途**：[评价] **方向 A 最近的查重对象**。它做的是 *LiDAR 主导*、学习协方差；方向 A 若定位为 *纯本体*（无 LiDAR 时可用，或作为 LiDAR 退化时的后备），并学习速度或位移本身，就有区分度。需要持续跟踪它的代码和录用情况。

> 状态估计的其他近邻（只核对了摘要页）：
> - **KING**（arXiv 2608.01015，comments 写 IROS 2026 录用；只有项目页）：用图神经网络统一表示轮式与腿式机器人的运动学，约 1 分钟数据即可适应新构型。是否覆盖**同一台轮足混合机器人**未核实，必须读全文。
> - **AutoOdom**（arXiv 2511.18857，未见录用信息，Booster T1 人形）：先用仿真预训练，再用少量真实数据做自回归训练；相对 Legolas，ATE 改善 57.2%。
> - **TRACE**（arXiv 2608.05975，投稿 RA-L，未录用）：用足端感知的交叉注意力，不设接触/打滑阈值。
> - **Okawara et al.**（RA-L 2025，arXiv 2506.09548）：在因子图里在线学习腿部运动学，融合 LiDAR 和 IMU。
> - **Go2-W 长距离导航**（arXiv 2606.21387，Tsukuba Challenge 2025，无代码）：[事实] 作者认为气胎让接触检测困难，轮速与腿运动学融合难以使用，于是用 MLP 从速度指令和短时 IMU 偏航估计每步位移，完成约 2.8 km 自主行驶。这直接说明 **Go2-W 上本体里程计是真实痛点**，而且现有做法很粗糙。

### 1.3 学习与控制结合：安全过滤、MPC + RL

#### (8) Gameplay Filters: Robust Zero-Shot Safety through Adversarial Imagination
- **发表状态**：[事实] CoRL 2024，PMLR 270（2025 年出版）；作者 Nguyen、Hsu、Yu、Tan、Fisac。
- **代码**：[事实] https://github.com/SafeRoboticsLab/Gameplay-Filters ，最近 push 2025-08-20，3 星。有训练脚本（`train/train_isaacs.py`，产出安全回退策略、对抗策略和 critic）和评估脚本；依赖 **PyBullet、Python 3.8、CUDA 11.8、JAX 0.4.8**；没有提到 Go2 部署代码和预训练权重；有配置文件 `isaacs_spirit.yaml`。
- **平台**：[事实] 论文称在两台物理参数和传感不同的四足上测试，项目页致谢中提到 Go2。
- **核心想法**：[事实] 先在仿真里让安全策略与对抗环境智能体博弈预训练；运行时对每个候选动作“想象”一局博弈，判断是否需要接管。这是面向 36 维全阶四足动力学的预测式安全过滤器。
- **Go2-W 创新点**：[评价] 失效集改为**轮足高速转弯侧翻或单侧轮离地**（以 LTR 为度量），对抗方施加侧向扰动和摩擦变化。
- **难点**：[评价] JAX 0.4.8 加 CUDA 11.8 **不能直接在 Blackwell 上跑**（推断：sm_120 需要 CUDA 12.8 及以上），需要移植到 Isaac Lab 和 PyTorch；PyBullet 里没有 Go2-W 模型。

#### (9) Winning a Won Game: Strict Reach-Avoid-Stay CBFs for High-Dimensional Black-Box Systems（sRAS）
- **发表状态**：[事实] arXiv 2609.19449（2026-09-16），“Submitted to the IEEE”，未录用；同为 Fisac 组。
- **代码**：[事实] 没有链接。
- **平台**：[事实] Go2 跳 25 cm 沟（MuJoCo 和实机），另有 F1TENTH 仿真。
- **核心想法**：[事实] 把“到达-避开-保持”拆成两个值函数，合成离散时间 CBF，再提升为 Q 函数做运行时干预；值函数用**只需黑箱交互的对抗 RL** 近似，不需要动力学、仿射结构或手工设计的屏障函数。
- **用途**：[评价] 方向 C 的理论骨架和查重近邻，说明该组在 Go2 上的工作很活跃。

#### (10) Racing a Wheeled Quadruped: Active Load Transfer Mitigation via MPC（附 RACER）
- **发表状态**：[事实] arXiv 2606.26313，comments 写 AVEC 2026 录用；作者 Eisman、Lam、Sonnino、Borrelli（UC Berkeley MPC Lab）。
- **代码**：[事实] https://github.com/meisman-ucb/go2w-roll-control-mpc ，创建于 2026-06-15，最近 push 2026-09-08，9 星。只有**高层主动侧倾 MPC**（CasADi/IPOPT、动态自行车模型）和闭环仿真，**不含底层 RL 策略**。
- **平台**：[事实] **Unitree Go2-W 实机**。
- **核心想法与结果**：[事实] 离线生成最短时间赛车线；在线 MPC 用自行车模型最小化横向载荷转移率 LTR，输出 [a_x, M_psi, M_theta]；底层全身 RL 策略执行，膝关节当主动悬架产生抗侧倾力矩。结果：平均 LTR 最多降低 44%，最快圈快 8.7%，峰值侧向加速度提高 21.3%，达到 1.98 m/s²。
- **RACER**：[事实] arXiv 2610.07409，无录用信息，无代码，只有仿真；同组用学习型神经残差刻画 RL 速度跟踪器的闭环误差，嵌入 MPPI，并用低秩适应（LoRRA）做少量真实数据微调。
- **用途**：[评价] **Go2-W 上现成的“传统控制强基线”**，方向 C 可直接拿来对照。RACER 已占住“MPC + 学习残差”这一组合，所以方向 C 不应再做残差动力学（何况这又接近前几轮的辨识路线）。

### 1.4 真实世界 RL / 实机微调

#### (11) LoopSR: Looping Sim-and-Real for Lifelong Policy Adaptation of Legged Robots
- **发表状态**：[事实] arXiv 2409.17992，comments 写 IROS 2025（会议论文集页面未直接核实）；作者来自上海交大。
- **代码**：[事实] https://github.com/aldeW64/LoopSR ，最近 push 2025-12-17，13 星。基于 **Isaac Gym + legged_gym + rsl_rl**，任务有 `go2_amp` 和 `a1_amp`，提供 `refine_real.py`，没有给出权重链接。
- **核心想法**：[事实] 用 Transformer 编码器把真实轨迹映射到隐空间，重建仿真参数（数字孪生）后继续在仿真里训练。作者明确写了“不含视觉感知”。
- **评价**：本质仍是“真实数据→仿真参数→再训练”，**与前几轮的辨识/对齐路线同族**，只作对比，不推荐。

#### (12) SLowRL: Safe Low-Rank Adaptation RL for Locomotion
- **发表状态**：[事实] arXiv 2603.17092（2026-03），无录用信息；无代码。
- **平台**：[事实] Unitree Go2。
- **核心想法**：[事实] 用 LoRA 低秩微调仿真预训练策略，配合恢复策略保证实机训练安全；摘要称微调时间比 PPO 基线少 46.5%，安全违例接近零。
- **评价**：真机 RL 是被前几轮忽略的方向，但对本科生而言实机训练的时间和硬件风险都高，SLowRL 又没有代码；**只作为方向 C 的一个可选子实验**（例如安全过滤器保护下的实机微调），不单独成方向。

> 任务层与人机交互（只作记录，不推荐）：**Obstacle-Avoidant Leader Following with a Quadruped Robot**（arXiv 2410.00572，ICRA 2025，ANYmal，用信标识别领队）；**Monocular Person Localization under Camera Ego-Motion**（arXiv 2503.02916，Go1，作者称代码和数据公开）。[评价] 系统集成为主，学习与控制上的贡献偏薄，且容易滑回“避障”。

---

## 2. 研究方向提炼

### 方向 A：Go2-W 轮足混合运动的学习型本体里程计（首推的稳妥方案）

- **要解决的问题**：Go2-W 在滚行、迈步和混合运动中，轮子和地面的接触点在滚动，足端零速假设失效，气胎还会形变和打滑，导致基于腿运动学的 InEKF 类估计器失效。[事实] Go2-W 长距离导航论文因此放弃了运动学融合，改用粗糙的指令回归 MLP。
- **为什么有价值**：
  - 速度和位姿估计是速度跟踪、导航、建图退化时后备定位的基础，是一个“小而硬”的真实问题。
  - LiDAR 在走廊、空旷场地等环境会退化（2610.26550 的动机）。
  - 结构可以采用“滤波器 + 学习补偿”，**传统估计方法本身就是基线，答辩最容易回应质疑**。
- **推荐基础论文**：
  - 方法主线：**Legolas**（CoRL 2024 / PMLR 2025），仿真训练、无需真实数据。
  - 结构参照：**InNKF**（IROS 2025），InEKF 加神经补偿。
  - 两篇都没有官方代码，复现形式是“按论文重实现，并在 Go2 腿式模式上先对齐趋势”。传统基线可用开源 InEKF 实现（具体仓库待选）和 Go2-W 自带的状态估计。
- **本科可做的创新点草案**：
  1. **轮足感知的输入与输出**：加入逐轮角速度、轮电机电流，以及“滚动接触点速度 = 轮半径 × 轮速”的物理先验特征；网络输出机体速度和不确定性，作为 InEKF 的观测（而非端到端替代）。
  2. **仿真训练加少量真实标注**：真值来自 Go2-W 自带 LiDAR 跑 FAST-LIO2 离线得到的轨迹，室内退化场景可外加动捕。对比三种设置：纯仿真、仿真加 LoRA 少量微调（参考 AutoOdom/TRACE 的做法）、纯真实数据。
  3. **实验对比**：
     - 基线：Go2-W 原厂估计、纯运动学 InEKF、轮速里程计加 IMU、Legolas 式纯网络、本文“InEKF + 轮足网络”。
     - 场景：平地滚行、草地或湿滑地面打滑、上下台阶迈步、滚走切换。
     - 指标：ATE、RPE、速度 RMSE、每 100 m 漂移。
     - 消融：去掉轮速特征、去掉物理先验、去掉不确定性输出、去掉真实微调。
     - 加分项：把估计速度接入 RL 速度跟踪闭环，看跟踪误差是否改善。
- **查重初判**：[评价] 腿式学习里程计已很拥挤（Legolas、AutoOdom、TRACE、InNKF、AttenNKF、Okawara、KING）。**轮足混合 + 纯本体 + 仿真训练**这一组合，本轮没有查到完全相同的工作。最近邻是 2610.26550（学的是 LiDAR 融合中的轮运动协方差）和 KING（轮式与腿式统一，是否覆盖混合构型未核实）。**这两篇必须读全文后再定题**。
- **风险**：
  - 没有官方代码，重实现有偏差风险。
  - 仿真中的轮地接触和气胎建模失真，可能让纯仿真模型在实机上表现差，缓解办法是真实微调或依靠滤波器兜底。
  - 2610.26550 若很快开源并录用，可能压缩创新空间。
  - 贡献偏“估计”而非“控制”，需要接入控制闭环实验来补强。
- **与前几轮方向相比**：
  - 优：几乎不伤机器（主要是采数据），实验周期可控，可用 LiDAR 自动生成真值；与传统滤波直接对话；不需要大规模视觉渲染。
  - 劣：“炫”的程度不如视觉策略；顶会故事需要讲清“为什么学习能处理解析模型处理不了的东西”。

### 方向 B：用 3DGS real-to-sim 训练 Go2-W 的 RGB 视觉策略，同时决定去哪、滚还是走

- **要解决的问题**：仿真渲染与真实外观不一致，使得纯 RGB 策略难以零样本迁移；VR-Robo 已在腿式 Go2 上解决了这一点，但**轮足的核心决策（何时滚行、何时迈步）依赖对地形的视觉理解**，现有 3DGS 工作都只针对腿式。本轮没有检索到轮足 + 3DGS 的工作（[事实]，检索覆盖有限）。
- **为什么有价值**：视觉策略和 real-to-sim 是 2025–2026 的热点（RSS 2026 收录 GS-Playground，RA-L 收录 VR-Robo、ReaDy-Go）；轮足能效优势只有在“看得懂路面”时才能发挥，故事自然。
- **推荐基础论文**：**VR-Robo**（RA-L 2025）。有官方代码，基于 Isaac Lab，平台为 Go2，与 Go2-W 最接近；GaussGym 可作为场景规模的参照。
- **本科可做的创新点草案**：
  1. **模式感知的高层动作**：在 VR-Robo 的高层速度指令上增加一个离散或连续的“滚/走”变量，底层换成 Go2-W 的轮足策略；奖励中加入能耗或机械功项，让策略学会平地滚、台阶走。
  2. **LiDAR 辅助的几何重建**：针对 VR-Robo 自述局限，用 Go2-W 的 LiDAR 点云约束 mesh，对比纯 RGB 重建的碰撞几何误差和策略成功率。
  3. **实验对比**：
     - 方法组：VR-Robo 原设定（只有腿式模式）、本文（模式感知）、深度相机或高程图输入的策略、纯 LiDAR 几何加 RGB 纹理的消融。
     - 指标：成功率、到达时间、能耗（电流积分）、模式切换次数，并统计误切换（在台阶前仍在滚行）。
     - 场景：实验室内重建 2–3 个含台阶和斜坡的场景，参照 VR-Robo 的 Easy/Medium/Hard 设置。
- **查重初判**：[评价] “3DGS + 动态行人”（ReaDy-Go）和“3DGS + 摩擦与残差动力学”（QuadVerse）已被占用。“3DGS + 轮足模式选择”本轮未见，但该领域发展很快，定题前需再做一轮针对性检索（wheel-legged / hybrid locomotion + vision / RGB）。
- **风险**：
  - 工程链最长：重建、两套环境、渲染服务器、高低两层策略、Go2-W 相机标定和机载推理。
  - VR-Robo 训练约 3 天/任务（4090D），2 卡 Blackwell 应能承受，但迭代次数有限。
  - Isaac Lab / Isaac Sim 版本在 Blackwell 上的组合需要先验证。
  - 与传统控制的对话较弱，只能把“传统规划 + 高程图”当基线来回应。
- **与前几轮方向相比**：
  - 优：最新颖、最有展示度，后续可扩展（语言目标、长程导航）。
  - 劣：复现成本最高，3–4 个月里实机部分容易被压缩；失败时更难给出“部分成果”。

### 方向 C：轮足高速运动的学习型安全过滤器（对抗 RL 学 reach-avoid Q 函数），对照 LTR 约束 MPC

- **要解决的问题**：Go2-W 高速滚行转弯时容易出现单侧轮离地或侧翻（Racing 论文用 LTR 刻画）。传统做法是基于简化模型（自行车模型）的 MPC 约束；学习型 RL 策略缺少安全保证。
- **为什么有价值**：它正面回答“学习方法安全吗”，**与传统控制的对话最直接**：同一个失效集，一边是基于模型的 MPC 约束，一边是从黑箱交互学到的安全值函数，可以公平对比保守性、干预率和速度上限。
- **推荐基础论文**：
  - **Gameplay Filters**（CoRL 2024 / PMLR 2025，Go2，有训练代码）作为方法与复现基础。
  - **Racing a Wheeled Quadruped**（AVEC 2026，Go2-W 实机，有 MPC 代码）作为传统强基线。
  - sRAS（arXiv 2609）作为理论参照。
- **本科可做的创新点草案**：
  1. 把 Gameplay Filter 的失效集换成“LTR 超过阈值或机身侧倾超限”，对抗方施加侧向推力、摩擦突变或指令突变；名义策略是普通的 Go2-W 速度跟踪 RL。
  2. **实验对比**：
     - 方法组：无过滤 RL、RL + LTR 约束 MPC（Racing 论文高层）、RL + 解析 CBF（基于静态稳定裕度）、RL + 学习过滤器（本文）。
     - 指标：侧翻或轮离地次数、干预率、可达到的最大侧向加速度、圈速或跟踪误差。
     - 消融：去掉对抗训练、去掉想象 rollout（只用值函数阈值）。
  3. 可选：在过滤器保护下做 SLowRL 式实机 LoRA 微调，把安全过滤器变成“安全实机学习”的使能器。
- **查重初判**：[评价] 学习型安全过滤器用于四足已有 Gameplay Filters、sRAS、One Filter（Go1，未见录用信息）、CBF-RL（ICRA 2026，G1）；用于**轮足侧翻**的学习型过滤器本轮未见。但 Fisac 组（Go2）和 Borrelli/Ames 组（Go2-W，RACER）都很活跃，存在被抢先的风险。
- **风险**：
  - **实机侧翻会损坏机器**，需要吊架、软地面和低速开始，实验强度受限。
  - 基础代码栈（JAX 0.4.8、CUDA 11.8、PyBullet）在 Blackwell 上不能直接用，要移植到 Isaac Lab，相当于半重写。
  - Racing 论文的 RL 底层没有开源，传统基线只能复用其 MPC 部分并自行接到底层。
  - 安全理论部分对本科生门槛较高。
- **与前几轮方向相比**：
  - 优：答辩说服力最强，Go2-W 有现成的同平台强基线（这是之前各方向没有的）。
  - 劣：实机风险和移植工作量大；“安全过滤 + 高速”的实验场地要求高。

---

## 3. 三个方向的横向比较（评价）

| 维度 | A 学习型本体里程计 | B 3DGS 视觉轮足策略 | C 学习型安全过滤器 |
|---|---|---|---|
| 复现基础 | 弱（无官方代码，需重实现） | **强**（VR-Robo 官方代码，Isaac Lab，Go2） | 中（有代码，但栈老，需移植） |
| 实机风险 | **低** | 中 | 高（侧翻） |
| 与传统控制对话 | 强（InEKF 就是基线） | 弱 | **最强**（同平台 MPC 基线） |
| 论文新颖度和展示度 | 中 | **高** | 中高 |
| 查重压力 | 中（2610.26550、KING 待读全文） | 中（领域快） | 中（两个活跃组） |
| 3–4 个月可完成性 | **高** | 中低 | 中 |
| 后续创新空间 | 接入控制闭环、多模态退化 | 语言目标、长程导航、动态场景 | 安全实机 RL、多失效模式 |

## 4. 未核实与下一步

- **未核实**：
  - GaussGym、QuadVerse、AutoOdom、SLowRL、sRAS、RACER、One Filter 的录用情况。
  - LoopSR 在 IROS 2025 论文集中的页面。
  - AttenNKF 的 RA-L 录用页。
  - VR-Robo 的 RA-L 页码。
  - Isaac Gym Preview 4 和 Isaac Lab 各版本在 sm_120 上的实测兼容性。
  - KING 是否覆盖轮足混合构型。
  - Legolas 是否有非公开代码。
  - Gameplay Filters 实机所用的第二台四足型号（配置文件名暗示是 Ghost Spirit，未核实）。
- **建议下一步**：
  1. 精读 2610.26550 和 KING 全文，判断方向 A 的空间。
  2. 在服务器上试装 VR-Robo（Isaac Lab）跑通 `go2_gs`，判断方向 B 的工程成本。
  3. 选定方向后再做一轮针对性的近邻检索与引文追踪。

## 5. 来源
- VR-Robo：https://arxiv.org/abs/2502.01536 ；https://vr-robo.github.io/ ；https://github.com/zst1406217/VR-Robo
- GaussGym：https://arxiv.org/abs/2510.15352 ；https://github.com/escontra/gauss_gym
- GS-Playground：https://www.roboticsproceedings.org/rss22/p093.pdf ；https://gsplayground.github.io ；https://github.com/discoverse-dev/gs_playground
- ReaDy-Go：https://arxiv.org/abs/2602.11575
- QuadVerse：https://arxiv.org/abs/2606.07118
- Legolas：https://proceedings.mlr.press/v270/wasserman25a.html ；https://learned-odom.github.io
- InNKF：https://arxiv.org/abs/2503.00344 ；AttenNKF：https://arxiv.org/abs/2601.18569
- Wheel Motion Uncertainty LIO：https://arxiv.org/abs/2610.26550
- KING：https://arxiv.org/abs/2608.01015 ；AutoOdom：https://arxiv.org/abs/2511.18857 ；TRACE：https://arxiv.org/abs/2608.05975 ；Okawara RA-L 2025：https://arxiv.org/abs/2506.09548
- Go2-W 长距离导航：https://arxiv.org/abs/2606.21387
- Contact-Anchored Proprioceptive Odometry：https://arxiv.org/abs/2602.17393 （无代码，未见录用信息，对比用）
- Tartan IMU（CVPR 2025）：https://openaccess.thecvf.com/content/CVPR2025/html/Zhao_Tartan_IMU_A_Light_Foundation_Model_for_Inertial_Positioning_in_CVPR_2025_paper.html ；https://huggingface.co/Tartan-IMU/TartanIMU
- Gameplay Filters：https://proceedings.mlr.press/v270/nguyen25a.html ；https://github.com/SafeRoboticsLab/Gameplay-Filters
- sRAS：https://arxiv.org/abs/2609.19449
- One Filter to Deploy Them All：https://arxiv.org/abs/2412.09989
- CBF-RL：https://arxiv.org/abs/2510.14959
- Racing a Wheeled Quadruped：https://arxiv.org/abs/2606.26313 ；https://github.com/meisman-ucb/go2w-roll-control-mpc
- RACER：https://arxiv.org/abs/2610.07409
- LoopSR：https://arxiv.org/abs/2409.17992 ；https://github.com/aldeW64/LoopSR
- SLowRL：https://arxiv.org/abs/2603.17092
- ABS（RSS 2024，对比提及）：https://github.com/LeCAR-Lab/ABS
- Leader Following（ICRA 2025）：https://arxiv.org/abs/2410.00572
