# 证据卡：ASAP（真机轨迹 + delta-action 模型对齐仿真；RSS 2025）

日期：2026-11-25。性质：论文正文（arXiv HTML 经网页抽取）+ 仓库浅克隆只读阅读（`git show HEAD:<path>`，行号取自该提交）+ GitHub issue 页面抽取 + 简要查重。**没有安装或运行任何代码。**
标注约定：**事实**＝论文/代码/issue 原文；**【评价】**＝审查者判断；查不到写"未核实"。

**阅读范围（先说清）**：
- 论文读的是 arXiv HTML（工具抽取文本，**不是逐页读 PDF**），无页码，出处写节/表/图号（取自抽取文本，未与 PDF 逐一对照）。抽取内容只覆盖约前 100k/110k 字符，末尾约 10k 字符（多半是致谢和参考文献）未读。公式在抽取文本里有乱码（如 Sec. III-B 步骤 1 的公式、Sec. V-A 的 "43004300 to 4300043000"），数字按语义还原，标"抽取乱码"处请对 PDF 复核。**RSS 论文集页（rss21/p066）本次没有读**，发表信息仅依据仓库 README 写的 "RSS 2025"，页数、Oral/Poster 未核实。
- 仓库：浅克隆（depth 50）成功，但 Windows 路径过长使 checkout 失败，故改用 `git show HEAD:path` 读文件，没有受影响。读了 README、`delta_a_open_loop.py`、`delta_a_closed_loop.py`、`train_delta_a.py`、`delta_dynamics_model.py`、`listener_deltaa.py`、`motion_tracking.py` 的相关段、`motion_lib_base.py` 的相关段，以及 delta_a 相关 yaml。**没有读** `isaacsim.py` 全文、`isaacgym.py`、`legged_robot_base.py` 全文。

## 1. 基本信息

| 项 | 内容 | 出处 |
|---|---|---|
| 题目 | ASAP: Aligning Simulation and Real-World Physics for Learning Agile Humanoid Whole-Body Skills | 任务给定；README |
| 发表 | RSS 2025（仓库 README 自述）；arXiv 2502.01143 | README 第 7、10 行 |
| 平台 | Unitree G1 人形（23 DoF 用于 delta 模型；README 里是 29dof_anneal_23dof 配置） | Sec. III-A、IV-C；README |
| 代码 | https://github.com/LeCAR-Lab/ASAP，基于 HumanoidVerse | README 第 76 行 |
| 最近提交 | **2026-01-05** "added NO_domain_rand_finetune_with_deltaA.yaml"（df5320c）；此前 2025-09-09 补 `obs/delta_a/train_policy_with_delta_a.yaml`，2025-09-04 "added missing files for delta_a training" | `git log` |
| star/fork | 未核实 | - |
| 代码发布范围 | README TODO 全部打勾，含 "Release ASAP delta action model training pipeline"（第 64–71 行）。**但 delta-action 部分是后补的**：2025-09 才补缺失文件，2026-01 才补域随机化配置，issue #80、#88 就是用户因缺文件而报错 | README；`git log`；issues #80、#88 |

## 2. 【决定性问题 1】真机数据怎么采

### 2.1 记录哪些量（事实）

| 内容 | 出处 |
|---|---|
| 论文：每个时间步记录基座位置、基座线速度、基座姿态（四元数）、基座角速度、关节位置、关节速度（23 DoF） | Sec. III-A |
| 论文：状态由"motion capture device and onboard sensors"记录 | Sec. III-A；Sec. I 写 "proprioceptive states and positions recorded by the motion capture system" |
| 代码：`DataLogger` 订阅 ROS 话题 `/odometry`（`nav_msgs/Odometry`，取 pose 与 twist 作为"mocap"：position、orientation wxyz、linear_velocity、angular_velocity），订阅 `rt/lowstate`（关节 q、dq、tau_est，IMU 四元数/陀螺/加速度计）和 `rt/lowcmd`（q、dq、kp、kd、tau 指令） | `sim2real/rl_policy/listener_deltaa.py` L53–L60、L114–L178 |
| 代码：缓冲 50 Hz（默认 `buffer_rate=50.0`，L20；L49 注释写 200 Hz，与默认值不符），按键 `;` 开始、`'` 停止，每段存一个 `motion_{k}.npz`，字段 `time, joint_pos, joint_vel, tau_est, IMU_*, joint_pos_cmd, joint_vel_cmd, kp, kd, tau_cmd, pos, quat, lin_vel, ang_vel` | 同上 L91–L111、L325–L348 |
| 基座位置/速度/姿态来源：论文只说 MoCap + 机载传感器，**没有区分各量来自哪个**；论文全文没有 "state estimation" 一词（抽取检索结果）。代码里是一个叫 `/odometry` 的话题，**仓库内没有发布该话题的代码**（只读到 `state_publisher.py` 存在，未读内容），README 说 "MoCap setup is hard to transfer across different robots/labs"（README L583） | 论文 Sec. III-A、VIII；README L583 |

【评价】基座位姿显然来自动捕（论文明说限制是"需要 MoCap 设置"，Sec. VIII）；线速度是动捕差分还是 `/odometry` 自带 twist，论文与代码都没说清，未核实。

### 2.2 数据量

| 项 | 数字 | 出处 |
|---|---|---|
| 踝关节 4 DoF delta 模型的真机数据 | **100 条运动片段（motion clips）**，"prove sufficient"；每个跟踪任务真机执行 30 次 | Sec. IV-C |
| 完整 23 DoF delta 模型 | 需要 "over 400 real-world motion clips"（Sec. IV-C），Sec. VIII 写 ">> 400 episodes in simulation"，作者称真机采集不可行 | Sec. IV-C、VIII |
| 另有 10 分钟的行走（locomotion）数据 | 10 minutes | Sec. IV-C |
| 采集代价 | 两台 G1 在采集过程中损坏（Sec. IV-C "two Unitree G1 robots broke"；Sec. VIII 措辞为 "broken to some extent"） | Sec. IV-C、VIII |
| 每条片段的长度、总帧数 | 论文与代码均未给出：未核实 | - |

【评价】100 条是 4 DoF 的数字；全 23 DoF 作者自己说采不了。对 Go2-W 这是核心可迁移性风险：delta 通道越多，所需真机轨迹越多。

### 2.3 delta-action 训练时是否需要在仿真里按真机初始状态重置并回放，因此必须有全局基座状态？

**结论：是，论文和代码都要求。** 证据：

1. 论文 Sec. III-B 步骤 1："The robot is initialized at the real-world state"（每个 RL 步；公式乱码）。训练里仿真用真机记录的动作 a^r 加上 Δa 前进一步，奖励是仿真状态对真机记录状态的跟踪误差（Sec. III-B、Table II）。
2. 代码 `LeggedRobotMotionTracking._reset_root_states`：用动作文件里的 `root_pos`、`root_rot`、`root_vel`、`root_ang_vel` 写入仿真器基座状态（L395–L448）；`_reset_dofs` 用动作文件里的 `dof_pos` 写关节（L464–L481）。重置时刻是 `episode_length_buf * dt + motion_start_times`（L405、L422、L473），`motion_start_times` 在重置回调里重采样（L159–L164、L216–L219）。
3. 回放的真机动作：`DeltaA_OpenLoop._compute_torques` 用 `get_open_loop_action_at_current_timestep()`（取运动文件里的 `action` 字段，`motion_lib_base.py` L103–L112、L384–L405）与 delta 相加，再走 PD：`tau = kp*(delta*scale + motion_action*scale + default - q) - kd*dq`（`delta_a_open_loop.py` L90–L92）。
4. delta 策略的观测包含 `base_pos_z, base_lin_vel, base_ang_vel, projected_gravity, dof_pos, dof_vel, actions, actions_open_loop, feet_contact_force`（`config/obs/delta_a/open_loop.yaml` L6–L20）。奖励是 `teleop_body_position_*`（全局身体位置，含脚）、`body_rotation`、`body_velocity`、`joint_position/velocity` 等对参考（即真机记录）的指数跟踪（`reward_delta_a_openloop.yaml` L11–L18），所以**确实依赖全局位置与朝向**。
5. 运动文件格式要求 `root_trans_offset`、`pose_aa`（含根朝向）、`fps`，再用正向运动学算出各刚体位置，另加 `action` 键（`motion_lib_base.py` L370–L405；README L249）。
6. 训练时长：README 命令里 `max_episode_length_s=1.0`（L267 附近），论文 Sec. V-A 称 1.0 s 的闭环结果最好、1.5 s 开环误差最低。

**两个与论文不一致/未解决之处（事实）**：
- 论文说每个 RL 步都用真机状态初始化；代码是在每个 episode 开头（约 1 s 一段）从随机运动时刻重置，之后由仿真自行滚动。issue #84（2025-09-16，无人回复）问的正是"在哪里实现每步重置为真机状态"。【评价】更像代码是"按段重置"，论文描述是简化，但这是我对代码的推断，作者未确认。
- **仓库里没有把 `.npz`（上面 logger 的输出）转成 delta 训练所需 `.pkl`（含 `action` 键）的脚本**（`git grep` 未找到；`scripts/` 下只有 SMPL 拟合与可视化）。issue #90（6 条评论）和 #104 的用户都在问这个文件怎么生成，无维护者回复；一位用户猜是"真机 rollout 的输出"，另一位问是否需要动捕，均未得到确认。

### 2.4 能否去掉全局基座状态？

【评价】代码层面不能直接去掉：重置需要 root_pos/rot/vel，奖励需要全局身体位置。若改成只用机体系量（关节、IMU 重力投影、机体系线速度），需要自己改重置与奖励；论文也把"MoCap-free alignment"列为未来工作（Sec. VIII）。这一点对你的方案是最大障碍：Go2-W 没有动捕时，基座线速度只有腿式里程计/状态估计，轮地打滑正是这种估计最不准的地方。这条属于对方案的推断，非论文结论。

## 3. 【问题 2】delta-action 模型如何训练、如何用于微调

| 阶段 | 内容 | 出处 |
|---|---|---|
| 0 预训练 | 在仿真里用 PPO 训练运动跟踪策略，全域随机化（论文设定）。README 示例 4096 环境，G1 29dof_anneal_23dof | README L214–L234 |
| 1 真机采集 | 部署策略，记录状态与动作（见 §2） | Sec. III-A |
| 2 训练 delta 策略（**用 RL，不是监督回归**） | PPO。输入：仿真当前状态与基座/关节观测、真机记录的动作；输出：Δa（与动作同维度，加到真机记录的动作上）。仿真 `s_{t+1} = f_sim(s_t, a_r + Δa)`。奖励：仿真状态对真机记录状态的跟踪（Table II：关节位置 0.5、关节速度 0.5、身体位置 1.0、脚位置 1.0、身体旋转 0.5 等），加动作变化率惩罚 -0.01、动作范数惩罚（Table II 写 -0.2，Sec. V-A 称 0.1 最好，README 命令用 -0.1，三处不一致）。网络 MLP [512,256,128]，ELU；README 5000 环境、episode 1.0 s | Sec. III-B、V-A，Table II；`ppo_train_delta_a.yaml`；README L254–L272 |
| 3 冻结 delta，在"带 delta 的仿真"里微调原策略 | `PPODeltaA` 冻结加载的 delta 策略，每步用 delta 策略观测出 `actions_closed_loop`，与新策略的动作一起进 `_compute_torques`（`train_delta_a.py` L76–L78、L111–L116；`delta_a_closed_loop.py` L65–L79、L162–L164）。奖励用 `reward_motion_tracking_dm_simfinetuning`，README 微调 1000 次迭代、4096 环境 | README L277–L300 |
| 4 部署 | 微调后的策略直接上真机，**不带 delta 模型** | Sec. III-D |
| 算力/时间 | 论文未报告 GPU 型号与训练小时（抽取检索未命中）：未核实。仿真数据：Fig. 13 提到"4300 episode 数据集"，Sec. V-A 把数据从 4300 扩到 43000 样本，闭环误差只改善 0.65%（抽取乱码，数字待复核） | Fig. 13、Sec. V-A |
| 另一条分支 | `delta_dynamics_model.py` 是监督学习的 delta-dynamics 基线（MLP 256×2，MSE 预测状态差），**但仓库里没有对应的环境实现**（`get_input_dim` 等函数全库搜不到），README 也没有它的命令，实际不可运行（issue #77 "Delta dynamics training" 已关闭，内容未读） | `git grep`；L19–L35、L156–L161 |

补充事实：作者发现 delta 动作大多集中在踝关节（Fig. 13），所以真机只训 4 DoF 踝关节版本（Sec. IV-C、V-C）。闭环时 delta 动作会有"自洽"问题：代码里留了梯度搜索和不动点迭代两种试验性实现（`delta_a_closed_loop.py` L89–L151），README 未提，属于实验代码。

## 4. 【问题 3】关键数字与论文自述局限

### 4.1 sim-to-sim（IsaacGym → IsaacSim / Genesis；均为论文自己的对照，Sec. IV-B 一带）

| 设置 | 结果（E_g-mpjpe，越小越好） | 出处 |
|---|---|---|
| 开环，1.0 s horizon | IsaacSim：OpenLoop 80.8，SysID 77.6，DeltaDynamics 68.1，**ASAP 37.9**；Genesis：82.5 / 76.5 / 50.2 / **36.9** | Table III |
| 闭环，Hard 级 | IsaacSim：Vanilla 148，SysID 165，DeltaDynamics 137，**ASAP 129**，ASAP 成功率 100%，DeltaDynamics 66.7%；Genesis：ASAP 129，SysID 186，DeltaDynamics 190，DeltaDynamics 成功率 60.0% | Table IV |
| 小问题 | 文中称 IsaacSim Easy 上 ASAP 最低，但 Table IV 显示 SysID 105、ASAP 106 | Table IV（抽取内容，待复核） |

### 4.2 sim-to-real（G1）

| 动作 | 方法 | E_g-mpjpe | E_mpjpe | E_acc | E_vel | 出处 |
|---|---|---|---|---|---|---|
| Kick | Vanilla → ASAP | 61.2 → 50.2 | 43.5 → 40.1 | 2.96 → 2.46 | 2.91 → 2.70 | Table V |
| LeBron（分布外） | Vanilla → ASAP | 159 → 112 | 55.3 → 47.5 | 3.43 → 2.84 | 6.43 → 5.94 | Table V |

- 摘要/结论称真机误差最多降 52.7%（Sec. VII），但 Table V 只能算出约 18%（Kick）和约 30%（LeBron）。【评价】52.7% 在抽取内容里找不到对应表项，引用时应用 Table V 的数字，不用 52.7%。
- 真机上 SysID、DeltaDynamics 的闭环数字没有报告（Table V 只有 Vanilla 与 ASAP）。【评价】真机上"ASAP 优于 SysID"没有直接证据，只有仿真对仿真的证据。
- 真机对照只有两个动作（Kick、LeBron），样本很小；每个任务 30 次真机执行（Sec. IV-C）。

### 4.3 作者自述的局限（Sec. VIII，原文意思）

1. 硬件：敏捷动作使电机过热、硬件故障，采集规模与多样性受限；两台 G1 受损。
2. 依赖动捕：流程需要 MoCap 记录真机轨迹，在无动捕环境难用。
3. 数据量大：全 23 DoF 的 delta 训练需要 >> 400 条片段，真机不现实；降到 4 DoF 踝关节才可行。
4. 未来方向：防损伤策略、MoCap-free 对齐、delta 模型的少样本自适应。

## 5. 【问题 4】代码

### 5.1 目录与 delta-action 文件

仓库顶层：`humanoidverse/`、`isaac_utils/`、`scripts/`、`sim2real/`、`imgs/`。`humanoidverse/simulator/` 下有 `base_simulator`、`genesis`、`isaacgym`、`isaacsim` 四个后端目录。

delta-action 相关文件（均已读）：

| 文件 | 作用 |
|---|---|
| `humanoidverse/envs/delta_a/delta_a_open_loop.py`（165 行） | 开环训练环境：把运动文件里的真机动作加 delta 后走 PD |
| `humanoidverse/envs/delta_a/delta_a_closed_loop.py`（252 行） | 微调环境：叠加冻结 delta 策略的输出 |
| `humanoidverse/agents/delta_a/train_delta_a.py`（170 行） | `PPODeltaA`：加载并冻结 delta 策略，在 rollout 里调用 |
| `humanoidverse/envs/motion_tracking/motion_tracking.py` | 基类：按运动文件重置基座与关节（L395–L481）、各种跟踪奖励 |
| `humanoidverse/utils/motion_lib/motion_lib_base.py` | 运动库：读 `action` 键（L103–L112、L384–L405），正向运动学 |
| `config/{env,exp,obs/delta_a,rewards/motion_tracking/delta_a,algo/ppo_train_delta_a,domain_rand/NO_domain_rand_finetune_with_deltaA}` | Hydra 配置 |
| `sim2real/rl_policy/listener_deltaa.py`（396 行） | 真机数据记录（§2.1） |
| `humanoidverse/agents/delta_dynamics/delta_dynamics_model.py` | 监督式基线，**未接通**（§3） |

注意：delta 相关代码里写死了关节索引与维度，例如 `anklePR` 只留索引 [4,5,10,11]（`delta_a_open_loop.py` L62–L64、L150–L161），梯度搜索里写死 23 维（`delta_a_closed_loop.py` L99–L101）。

### 5.2 对 Isaac Gym 的依赖集中在哪里

- 主要集中：`simulator/isaacgym/isaacgym.py`（65 处 isaacgym/gymapi/gymtorch 命中）和 `isaacgym_hoi.py`（86 处）。
- 零星：`train_agent.py` L44、`eval_agent.py` L125（`import isaacgym`，且要求先于 torch 导入）；`envs/env_utils/terrain.py`、`utils/terrain.py` 顶部 `from isaacgym import terrain_utils`；`agents/modules/world_models.py` L9–L10。
- `motion_tracking.py` 在 L410、L438、L515 按 `simulator.config.name` 分支处理四元数顺序；Genesis 分支直接 `raise NotImplementedError`（L414–L415）。
- delta_a 的两个环境文件里 isaacgym 导入已被注释，**delta-action 核心逻辑本身不依赖 Isaac Gym**，依赖的是上层 HumanoidVerse 的模拟器抽象（`simulator.dof_pos`、`robot_root_states`、`set_actor_root_state_tensor` 等）。

### 5.3 有没有 Isaac Sim / Isaac Lab 后端

- 有：`humanoidverse/simulator/isaacsim/`（`isaacsim.py` 719 行、`isaaclab_cfg.py`、`events.py` 等）；README 写 IsaacSim 4.2.0 + IsaacLab 安装步骤；`train_agent.py` L26 在 isaacsim 模式下用 `omni.isaac.lab.app.AppLauncher`。HumanoidVerse 的设计是"模拟器、任务、算法分离"（README L78）。
- 但：PR #86（2025-09-27，已关闭）把 `omni.isaac.lab` 改名为 `isaaclab` 并降 PPO 迭代数，说明主线代码仍是旧命名；issue #107（2026-01-30，4 条评论，未关闭）有人装了 Isaac Sim 却 `import omni` 失败，求 Isaac Lab 版；issue #79 有人在 RTX 5060 Ti 上遇到 PyTorch 兼容错误（已关闭，内容未读）。
- **delta-action 在 isaacsim 后端是否真能跑通：未核实**。README 的 delta 命令全部用 `+simulator=isaacgym`；`isaacsim.py` 里有 TODO（L651 "only consider the robot root state"）。
- Isaac Sim 5.1 兼容性：未核实，很可能需要改名/改 API。
- 这是 HumanoidVerse 自己的框架，**不是 Isaac Lab 的 manager-based 任务**，与 robot_lab 不是同一套结构。

### 5.4 提交与 issue

- 最近提交 2026-01-05（见 §1）。issue 页面抽取到 #77–#110，其中 #105–#110 创建于 2025-12 至 2026-10，**均无维护者回复**（评论数 0–1，#107 有 4 条用户评论）。
- 与 delta-action 相关的 issue：#77（已关）、#80（已关，缺文件）、#84（每步重置，无回复）、#88（缺 domain_rand 文件，其后 2026-01 才补）、#89/#90（运动文件内容，6 条评论全是用户）、#98（怎么判断 delta 好坏，无回复）、#104（求运动文件示例，1 条评论）。
- **issue 里没有任何人报告在真机上成功复现 delta-action**：已读到的列表中没有这样的条目；#85（真机 sim2real 无响应，7 条评论）说的是普通部署。编号小于 #77 的更早 issue 因抽取长度限制没读到：未核实。

### 5.5 把 delta-action 核心移植到 robot_lab Go2-W 的工作量（【评价】）

需要自己写的模块：

1. **真机日志器**：Go2-W 的 `rt/lowstate`、`rt/lowcmd`（含 4 个轮子的 dq）、IMU、雷达里程计或动捕；对齐时间戳、重采样到控制频率。`listener_deltaa.py` 可作参考，但要去掉其人形假设。**约 2–3 天**，另需动捕或其他全局状态方案。
2. **数据到轨迹格式的转换**：把日志变成 (root pos/quat/vel/ang_vel, joint pos/vel, 动作)；ASAP 的 `.pkl` 转换脚本仓库里没有，要自己写。
3. **仿真中"按真机状态重置 + 回放动作"**：在 Isaac Lab 环境中支持把基座与关节（含轮速）写成给定状态，并在一个短 episode（约 1 s）内回放记录的动作；Isaac Lab 有 `write_root_state_to_sim` 与 `write_joint_state_to_sim`，但需要在 robot_lab 的事件/重置管理里加一类"来自轨迹的重置"。**约 1 周**。
4. **残差动作叠加与执行器路径**：ASAP 是在环境里自己算 PD 力矩（`tau = kp*(...)−kd*dq`），Isaac Lab 里通常是执行器模型（隐式或显式）处理位置目标；delta 要加在"位置目标"（腿）和"速度目标"（轮）上。需要核对 robot_lab Go2-W 的执行器配置。**约 3–5 天**。
5. **delta 策略的 PPO 训练**：观测（机体系速度、重力投影、关节/轮速、历史、真机动作）、奖励（对真机轨迹的跟踪：关节位置、关节速度、基座速度，脚/轮位置，动作范数惩罚）。ASAP 的奖励是全局身体位置跟踪，Go2-W 要改成适合轮足的项，奖励设计本身要摸索。可用 robot_lab 已有的 PPO（RSL-RL）。**约 1–2 周**。
6. **冻结 delta 并微调**：把冻结网络放进环境 step，用于策略微调；腿/轮通道分开、轮通道以轮速为条件是你自己的设计，ASAP 没有。**约 1 周**。
7. **评估与 sim-to-sim 验证平台**：被改动的仿真或 MuJoCo 当"真机"，用来按 ASAP 的开环/闭环指标做对照。**约 1–2 周**。

合计粗估 **5–8 周**到可用状态（含调试），不含真机实验。还要加上：Isaac Gym 部分可以全丢，motion-lib 与人形 SMPL 重定向全不需要。

【评价】**可移植的是思想与约 300 行的核心逻辑，不是代码本身**。代码与 HumanoidVerse 的 Isaac Gym 抽象和 G1 的 23/29 DoF 硬编码耦合，直接复用意义不大。注意真机迁移比论文更难的两点：(a) 论文里 delta 只在踝关节有效，是因为 G1 的踝是并联小连杆、PD 增益不匹配；轮地接触的差距是否也能被"关节/轮速目标上的加性残差"吸收，论文没有证据，属于待验证的猜想；(b) 全局基座状态没有动捕时较难拿到（§2.4）。

## 6. 【问题 5】后续与引用工作（简要，另有人专门查重）

- arXiv 2604.11090（Dao & Fern，2026-04-13，cs.RO）*Simulator Adaptation for Sim-to-Real Learning of Legged Locomotion via Proprioceptive Distribution Matching*：Go2 四足，摘要提到比较 parameter identification、action-delta models 和 residual actuator models，并称不需要时间对齐或外部传感（即不依赖动捕）；评估为 sim-to-sim 消融加真机。**只读到摘要**，是否为 ASAP 风格的 delta action、是否含 PACE 类参数辨识、是否是轮足：未核实（搜索结果称其引用了 ASAP，未亲眼核对参考文献）。【评价】这篇与你的设想邻近，需要专门精读。
- 轮足上用 delta action、或"参数辨识 + delta action"组合：本次两次搜索**没有找到**。结论仅限本次搜索，不代表不存在。

## 7. 对选题的判断（【评价】）

- 优点：思想清晰，delta 通道可分、训练只需 PPO；sim-to-sim 对照在论文里做得充分，易复现；代码里 delta 核心逻辑短。
- 风险：(1) 仓库的 delta 部分可复现性差：缺转换脚本、运动文件格式无文档、issue 无人答复、每步重置与代码不一致；(2) 真机证据弱：两个动作、只有 Vanilla 对 ASAP；(3) 全局基座状态要求与 Go2-W 无动捕的条件冲突；(4) Isaac Lab 后端不确定；(5) 论文数字有内部不一致（52.7%、Table II 与 Sec. V-A 的动作范数权重）。
- 如果选它：核心工作必然是自己重写，不是复现；创新点（腿轮分离、轮速条件化、先参数辨识）不被 ASAP 占据，但与 2604.11090 的关系要先厘清。
