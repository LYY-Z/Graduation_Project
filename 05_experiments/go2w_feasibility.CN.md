# Go2-W 实机与软件链可行性核查

核查日期：2026-11-25。方式：只读文档、公开仓库与网页；未连接服务器和机器人，未安装任何东西。
行号说明：raw 文件经网页抓取工具读取，**行号为工具估计值（"约"）**，引用时应以文件内的函数/字段名为准，落实前请本地 `grep` 复核。

## 0. 结论摘要

| 条件 | 状态 |
|---|---|
| 官方 SDK 提供 Go2-W 的 lowcmd/lowstate（16 路：12 腿 + 4 轮），有官方例程 | 已核实 |
| 轮电机用"kp=0 + dq 目标 + kd"的速度模式，与 robot_lab 仿真轮执行器（stiffness=0, damping=0.5）形式一致 | 已核实 |
| robot_lab 有 Go2-W 任务，v2.3.2 兼容 Isaac Sim 5.1（与服务器环境一致） | 已核实 |
| rl_sar 有 Go2-W 实机部署（`rl_real_go2 <网卡> wheel`），可跑外部 PC，也可跑机载 Jetson | 已核实 |
| lowstate 含 q/dq/tau_est/temperature 与 IMU | 字段已核实；**轮电机 temperature 是否有效未核实** |
| Go2-W 非 EDU 版本是否开放 lowcmd | **未核实**（官方无明确表述） |
| 激光雷达型号、机载 Orin 型号 | **未核实**（官方页不写型号，来源互相矛盾） |
| 底层模式下基座速度来源 | 官方 SportModeState 不可用；需 LIO 或自建估计，Go2-W 上无现成验证案例 |

## 1. 已核实

### 1.1 底层控制接口（问题 1）

- **消息与主题**：Go2-W 使用 `unitree_go` IDL（`LowCmd_`/`LowState_`），主题 `rt/lowcmd`、`rt/lowstate`。依据：Python 例程 `unitree_sdk2_python/example/go2w/low_level/go2w_stand_example.py` 约第 62、66 行 [链接](https://github.com/unitreerobotics/unitree_sdk2_python/blob/master/example/go2w/low_level/go2w_stand_example.py)；unitree_mujoco README 明写 "Go2, B2, H1, B2w, Go2w robots use unitree_go idl for low-level communication" [链接](https://github.com/unitreerobotics/unitree_mujoco/blob/main/readme.md)。
- **电机数量与顺序**：消息数组为 20 槽（`motor_state[20]`，见 [`_LowState_.py`](https://github.com/unitreerobotics/unitree_sdk2_python/blob/master/unitree_sdk2py/idl/unitree_go/msg/dds_/_LowState_.py)），Go2-W 用 0–15：0–11 为腿（FR、FL、RR、RL 各 hip/thigh/calf），12–15 为轮（FR、FL、RR、RL）。依据：rl_sar `policy/go2w/base.yaml` 的 `joint_names`/`wheel_indices: 12–15` [链接](https://github.com/fan-ziqi/rl_sar/blob/main/policy/go2w/base.yaml)；官方 C++ 例程 `unitree_sdk2/example/go2w/go2w_stand_example.cpp` 对 0–11 与 12–15 分开处理 [链接](https://github.com/unitreerobotics/unitree_sdk2/blob/main/example/go2w/go2w_stand_example.cpp)。仓库内 [go2w.CN.md §1.2](../02_learning/platform/go2w.CN.md) 的映射表与此一致。
- **轮控制方式**：官方 C++ 例程中，腿 `kp=70, kd=5`；轮 `kp=0`、`kd=5`（同一 Kd 变量）、`q=0`、`dq=±3`（约第 40–41 行 Kp/Kd，轮相位在 `LowCmdWrite`）。Python 例程轮 `kp=0`、`kd=Kd`、`dq=3/-3`（约第 146–155 行）。即轮为"速度目标 + 阻尼"，按 PD 形式 `tau = kd*(dq_des - dq) + tau_ff` 解释；`MotorCmd_` 另含 `tau` 前馈字段，**轮是否接受 kp≠0 的位置控制、tau 前馈是否被执行，官方未写，未核实**。所有电机 `mode=0x01`（例程注释 "servo (PMSM) mode"）。
- **进入底层模式**：必须先释放高层运动服务。官方例程用 `MotionSwitcherClient`：循环 `CheckMode()`，非空则 `ReleaseMode()`，直至模式名为空（C++ 例程 `queryMotionStatus()` 循环，间隔 5 s；Python 例程约第 81 行）。rl_sar 同样在 `rl_real_go2.cpp` 开头循环 `ReleaseMode()`（约 L56–73）[链接](https://github.com/fan-ziqi/rl_sar/blob/main/src/rl_sar/src/rl_real_go2.cpp)。
- **发送频率**：官方例程 2 ms 周期（500 Hz），发送前计算 CRC；约 1 s 延迟（`motiontime>=500`）后才开始发布。

### 1.2 lowstate 字段（问题 2）

依据 IDL：[`_MotorState_.py`](https://github.com/unitreerobotics/unitree_sdk2_python/blob/master/unitree_sdk2py/idl/unitree_go/msg/dds_/_MotorState_.py)、[`_IMUState_.py`](https://github.com/unitreerobotics/unitree_sdk2_python/blob/master/unitree_sdk2py/idl/unitree_go/msg/dds_/_IMUState_.py)、[`_LowState_.py`](https://github.com/unitreerobotics/unitree_sdk2_python/blob/master/unitree_sdk2py/idl/unitree_go/msg/dds_/_LowState_.py)。

| 消息 | 字段 |
|---|---|
| `MotorState_` | `mode`(u8)、`q`、`dq`、`ddq`、`tau_est`、`q_raw`、`dq_raw`、`ddq_raw`（均 f32）、`temperature`(u8)、`lost`(u32)、`reserve[2]` |
| `IMUState_` | `quaternion[4]`、`gyroscope[3]`、`accelerometer[3]`、`rpy[3]`、`temperature`(u8) |
| `LowState_` | `imu_state`、`motor_state[20]`、`bms_state`、`foot_force[4]`、`foot_force_est[4]`、`tick`、`wireless_remote[40]`、`power_v`、`power_a`、`temperature_ntc1/2`、`fan_frequency[4]` 等 |

- `tau_est` 是估计力矩，`temperature` 是 u8 整数度数；`q_raw/dq_raw` 的含义（是否为转子侧）官方无说明，未核实。
- **采样频率**：官方例程以 500 Hz 发 lowcmd；`rt/lowstate` 的实际发布频率官方文档抓取失败（support.unitree.com 为动态页），**未核实**。unitree_ros2 README 说明 `lf/lowstate` 的 "lf" 表示低频版本 [链接](https://raw.githubusercontent.com/unitreerobotics/unitree_ros2/master/README.md)，记录时应用 `rt/lowstate`，并在实机上用 `tick` 字段实测周期。
- rl_sar 的 `GetState` 只读 IMU 的 `quaternion`、`gyroscope` 与电机的 `q`、`dq`、`tau_est`，**不读 temperature**（`rl_real_go2.cpp` 约 L149–166），做温度记录需自己加。

### 1.3 robot_lab（问题 3）

- **任务存在**：任务 ID `RobotLab-Isaac-Velocity-Rough-Unitree-Go2W-v0`（README 只列 rough）[链接](https://github.com/fan-ziqi/robot_lab)。目录 `source/robot_lab/robot_lab/tasks/manager_based/locomotion/velocity/config/wheeled/unitree_go2w/` 下有 `rough_env_cfg.py`、`flat_env_cfg.py`、`agents/`。
- **版本**：README 兼容表：`v2.3.2` → Isaac Lab v2.3.2 / Isaac Sim 4.5、5.0、5.1；`main` → Isaac Lab v3.0.0 / Isaac Sim 6.2。**Isaac Sim 5.1 应选 v2.3.2 标签，不要用 main**。服务器已有 Isaac Sim 5.1.0 + PyTorch 2.7 cu128 环境（见 [inventory.CN.md §4](server/inventory.CN.md)），其中的 robot_lab 快照是否为 v2.3.2 待核（inventory 已标"待核对"）。
- **轮执行器模型**（`assets/unitree.py` v2.3.2 约第 121–175 行 [链接](https://github.com/fan-ziqi/robot_lab/blob/v2.3.2/source/robot_lab/robot_lab/assets/unitree.py)）：腿和轮都是 `ImplicitActuatorCfg`；腿 `stiffness=25, damping=0.5, effort_limit_sim=23.5, velocity_limit_sim=30`；轮 `stiffness=0, damping=0.5`，同样限幅。资产是 URDF `go2w_description.urdf`。没有 DC 电机模型（Go2/A1/B2 用 `DCMotorCfg`，Go2-W 不是），也没有执行器延迟或摩擦。
- **动作与观测**（`rough_env_cfg.py` 约第 28–29、81–105 行）：腿用位置动作，轮用 `JointVelocityActionCfg`（scale=5.0，clip ±100）；策略观测中 **`base_lin_vel = None`（已删除）**、`height_scan = None`；轮的关节位置观测用 `joint_pos_rel_without_wheel`。观测共 57 维（3+3+3+16+16+16）。**这意味着 Go2-W 基线策略部署不需要基座速度**；若本课题的 sim-to-real 对齐需要基座速度，那是评估/记录需求，不是部署需求。
- 仿真步长 `sim.dt=0.005`、`decimation=4`（50 Hz 策略；`velocity_env_cfg.py` 约第 716–719 行）。随机化：摩擦静 0.3–1.0 / 动 0.3–0.8、基座质量 −1～+3 kg、其他刚体 ×0.7–1.3、PD 增益 ×0.5–2.0、10–15 s 推力（约第 260–368 行）。**没有轮胎变形、电机延迟、温度/热模型**。

### 1.4 rl_sar（问题 4）

- **Go2-W 支持**：README 支持表 "Unitree-Go2W (go2w) | robot_lab (IsaacSim)"，Gazebo/Mujoco/Real 均 ✅ [链接](https://github.com/fan-ziqi/rl_sar)。文件：`policy/go2w/base.yaml`、`policy/go2w/robot_lab/config.yaml`、`policy/go2w/robot_lab/policy.pt`、`src/rl_sar/fsm_robot/fsm_go2w.hpp`、`src/rl_sar/src/rl_real_go2.cpp`、`src/rl_sar/include/rl_real_go2.hpp`。
- **通信**：以太网直连，命令 `./cmake_build/bin/rl_real_go2 <网卡> wheel`（README）。代码里订阅 `TOPIC_LOWSTATE`、发布 `TOPIC_LOWCMD`（Cyclone DDS，基于 unitree_sdk2；致谢里写 unitree_sdk2-2.0.0）。
- **运行位置**：README 两种都有——外部电脑经网线，或在机载 Jetson 上 `./build.sh -m` 编译后运行同一二进制。
- **频率**：`policy/go2w/base.yaml`：`dt=0.005`、`decimation=4`，即控制循环 200 Hz、策略 50 Hz，与 robot_lab 训练一致。
- **参数**（`config.yaml`）：观测与 robot_lab 一致（57 维）；轮 `action_scale=5.0`，`rl_kp=0`、`rl_kd=0.5`；腿 `rl_kp=20`、`rl_kd=0.5`；`torque_limits=23.5`。**注意：仿真腿 stiffness=25，rl_sar 部署腿 kp=20，两者不一致**，对齐实验时必须统一并记录。
- 不用 SportModeState，没有基座线速度输入；轮位置观测是否清零在 `ComputeObservation`（未读到该函数，未核实）。
- 已知问题：[#178](https://github.com/fan-ziqi/rl_sar/issues/178)（Go2W 实机剧烈抖动，开放无回复）、[#175](https://github.com/fan-ziqi/rl_sar/issues/175)（编译链接失败）、[#134](https://github.com/fan-ziqi/rl_sar/issues/134)（Jetson 无 ROS 时 core dump，已关闭）。

### 1.5 基座状态与雷达（问题 5，已核实部分）

- **SportModeState 在底层模式下不可用**：unitree_mujoco README："the `SportModeState` message is not readable after the built-in motion control service is turned off"，仿真保留该消息仅用于分析 [链接](https://github.com/unitreerobotics/unitree_mujoco/blob/main/readme.md)。故释放运动服务后，不能用官方速度估计作为实机基座速度真值。（此条是对 Go2 通用的官方表述，Go2-W 无单独声明。）
- **Go2-W 的官方 odometry 话题不可用**：MYBOTSHOP 论坛报告 Go2-W 上 `/utlidar/robot_odom`、`/utlidar/robot_pose` 零消息，厂商回复"尚未实现"，建议用 FastLIO2/MOLA [链接](https://forum.mybotshop.de/t/unitree-go2-w-ros2-odometry-and-topic-availability-issues/1831)。该帖的 Go2-W 有 `/utlidar/cloud`、`/utlidar/imu`，帖中称雷达为 Unitree L1 / UTLiDAR（用户陈述，非官方）。
- **开源 LIO**：Unitree 官方 [`point_lio_unilidar`](https://github.com/unitreerobotics/point_lio_unilidar)（适配 L1/L2，输出位姿与速度）；ROS2 社区移植 Point-LIO-ROS2；社区 Go2 EDU 自主栈用 Go2 内置 L1 + Point-LIO（搜索结果，未逐一核对仓库）。**未找到 Go2-W 上跑 Point-LIO/FAST-LIO 的公开验证案例**；FAST-LIO 系列需要按雷达驱动改接口。
- 注意 [unilidar_sdk#34](https://github.com/unitreerobotics/unilidar_sdk/issues/34)：L1 内置 IMU 数据异常（姿态/加速度不合理），开放未解决，选 LIO 时要先检查雷达 IMU。

### 1.6 社区报告的 Go2-W 问题（问题 6）

1. **长时间运行发热**：[rl_sar#70](https://github.com/fan-ziqi/rl_sar/issues/70)，维护者回复"go2w 的 policy 未经调优，长时间运行会发热，后续放出调优版"；后转为 Discussion #92（内容未读到）。帖中没有写明哪个电机、多少度。
2. **实机剧烈抖动**：[rl_sar#178](https://github.com/fan-ziqi/rl_sar/issues/178)，robot_lab 训练的 Go2W 策略部署后剧烈抖动，另一用户确认同样问题，无人回复。
3. **训练后不动**：[unitree_rl_lab#122](https://github.com/unitreerobotics/unitree_rl_lab/issues/122)，把 Go2 配置换成 `UNITREE_GO2W_CFG` 训练 50K 迭代后机器人不动，无诊断（该仓库官方并不支持 Go2W 训练，README 列 Go2/H1/G1）。
4. **轮响应与轮胎**：博客 [Go2-W Sim-to-Real](https://isprout.com/posts/2025-12-18-isaac-workshop-part4)（非同行评议，作者经验）：轮电机响应比腿快，轮指令滞后会打滑；充气轮胎形变与刚体仿真不同，建议随机化轮胎摩擦；滚动/行走切换时机是差距来源；总循环 50 Hz。
5. **资产/模型差异**：[unitree_ros#157](https://github.com/unitreerobotics/unitree_ros/issues/157)（URDF 与 MJCF 的 Go2W 总质量与轮惯量不一致）、[unitree_ros#115](https://github.com/unitreerobotics/unitree_ros/issues/115)（URDF 导入 Isaac Sim 后轮碰撞体朝向错位）、[#131](https://github.com/unitreerobotics/unitree_ros/issues/131)（Isaac Sim 4.5 材质导入问题）。对 sim-to-real 对齐是直接相关的风险。
6. 相关但非 Go2-W：[unitree_sdk2_python#174](https://github.com/unitreerobotics/unitree_sdk2_python/issues/174) "cannot use StandDown for go2w"（高层服务，已关闭）。

## 2. 未核实 / 存在冲突

| 项目 | 现状 | 建议核实方式 |
|---|---|---|
| 非 EDU Go2-W 是否开放 lowcmd | 官方 Go2-W 页只写 "Secondary development ●，见二次开发手册"，不分版本 [链接](https://www.unitree.com/go2-w)。第三方销售/论坛称 Go2 系列仅 EDU 开放二次开发（[Go2 Pro 论坛帖](https://forum.mybotshop.de/t/unitree-go2-pro-unitree-sdk2-can-not-run-example-code/1090)），未见针对 Go2-W 的结论 | 看实机 App 内版本标识，向 Unitree/经销商书面确认；以只读 `rt/lowstate` 订阅能否收到数据作第一步测试 |
| 轮电机 `temperature` 是否有效 | 未找到任何 issue 讨论；IDL 字段存在，rl_sar 不读取 | 实机只读订阅 `rt/lowstate`，静止与轮转后打印 `motor_state[12:16].temperature`，看是否为 0/恒定/随负载变化 |
| `rt/lowstate` 实际频率 | 官方文档页抓取失败 | 实机用 `tick` 字段实测 |
| 雷达型号 | 官方 Go2-W 页只写 "Super-wide-angle 3D LIDAR"，无型号。第三方：销售页写 4D LiDAR L2；论坛用户写 L1/UTLiDAR；个别销售页列 Hesai XT16 为升级配置 | 看实机雷达铭牌；`ros2 topic list` 是否有 `/utlidar/*`；用 L1 或 L2 的 `unilidar_sdk`/`unilidar_sdk2` 对应驱动 |
| 机载计算 | 官方页：基础算力 "8-core CPU"，扩展模块 "Multiple brands and models available, such as Orin NX"，无 TOPS 和内存信息。销售页称 Orin Nano 或 Orin NX（100 TOPS），互相矛盾；学习博客也把 Orin Nano vs NX 列为未决 | 在实机扩展坞上 `cat /etc/nv_tegra_release`、`jetson_release` 或查标签 |
| 轮电机对 kp≠0 / tau 前馈的响应、轮的最大转速/电流限制 | 官方例程只展示 kp=0 + dq；URDF 为 30.1 rad/s、23.7 N·m，robot_lab 为 30、23.5，rl_sar 为 23.5，三者不一致，且产品页称各电机最大扭矩不同 | 不控制硬件前不可测；先用只读记录观察 `tau_est` 范围 |
| `q_raw/dq_raw` 含义、`tau_est` 的标定与符号 | 无官方说明 | 对照仿真，用已知载荷做静态/动态检查 |
| Go2-W 上的 LIO 实际效果（轮式振动、IMU 质量、外参） | 无公开案例 | 实机采 rosbag 后离线验证 |
| robot_lab Go2-W 策略在服务器能否训练到收敛 | 未运行（按要求不启动仿真） | 之后在服务器测试；`unitree_rl_lab#122` 提示配置不当会训练出不动的策略 |
| rl_sar 的 `ComputeObservation` 对轮位置的处理、rl_sar #92 讨论的发热调优内容 | 未读到 | 阅读源码与 Discussion #92 |

## 3. 对课题的含义（我们的评价，非事实）

- **部署链路可行性较高**：robot_lab → rl_sar 是已发布并含 Go2-W 预训练策略的完整链路，仿真与部署的 dt、decimation、观测维度、轮动作缩放一致。风险集中在实机效果（抖动、发热）而非"能否对接"。
- **sim-to-real 对齐的可测量项**：关节 `q/dq/tau_est`、轮速、IMU 均可由 `rt/lowstate` 直接获取；`temperature` 需先验证。
- **基座速度需要外部来源**：底层模式下无官方速度估计，需雷达 LIO（Point-LIO，须先确认雷达型号与其 IMU 质量）或动捕。对实验设计：若对齐只用关节和 IMU 信号，可避开该风险。
- **仿真侧简化**：隐式 PD、无延迟、无轮胎模型、无热模型，正是 sim-to-real 差距的来源，与 [STATUS.CN.md](../STATUS.CN.md) 中的热与轮速方向一致。
- 执行器参数在 URDF / robot_lab / rl_sar / 官方例程间存在多处不一致（见 1.4 和 §2），做对齐实验前应建立单一参数表。


## 补充：能否读到轮电机的电流或功率（2026-11-25 主模型核实）

依据：unitree_ros2 的消息定义 `unitree_go/msg/MotorState.msg`、`LowState.msg`、`BmsState.msg`（[GitHub](https://github.com/unitreerobotics/unitree_ros2/tree/master/cyclonedds_ws/src/unitree/unitree_go/msg)）。Go2-W 与 Go2 共用 `unitree_go` 消息，`motor_state[20]` 中使用 16 路。

| 量 | 字段 | 结论 |
|---|---|---|
| 单个电机电流 | `MotorState` 只有 `mode、q、dq、ddq、tau_est、q_raw、dq_raw、ddq_raw、temperature、lost、reserve` | **读不到单个电机（含轮电机）的电流** |
| 单个电机机械功率 | `tau_est × dq` | 可估算（估计力矩的精度未标定） |
| 整机电功率 | `LowState.power_v × LowState.power_a`（母线电压、电流） | 可读，整机总量 |
| 电池电流 | `BmsState.current` | 可读，整机总量 |

**含义**：转弯能耗可用两种方式测量：① 整机电功率（母线电压 × 电流）随时间积分，这是最可靠的总能耗；② 各轮 `tau_est × dq` 作为分轮的机械功率估计。分轮的电功率无法直接测得。
