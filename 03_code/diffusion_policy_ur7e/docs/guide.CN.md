# UR7e Diffusion Policy 部署指南

[English](guide.md) | [简体中文](guide.CN.md)

本指南说明运行环境、模型资源、设备配置与启动接口。系统实现及控制约束见[技术报告](technical_report.CN.md)，验证范围与记录来源见[验证数据](validation.json)。

部署产物包括推理环境、模型文件和控制扩展；运行进程包括相机驱动、图像桥接和策略应用。以下命令均在 Linux 主机的仓库根目录执行。

## 1. 运行环境

| 环境 | 用途 | 依赖 |
|---|---|---|
| 推理环境 | 策略应用、模型及资源校验、控制扩展构建 | Conda；项目环境 `.envs/inference`，Python 3.9 |
| ROS 环境 | 相机驱动与图像桥接 | Ubuntu 22.04、ROS 2 Humble、系统 Python 3.10、`orbbec_camera` |
| 原生构建工具 | 编译项目专用控制扩展 | CMake、G++、Boost |
| 计算设备 | 模型推理 | NVIDIA GPU 及兼容驱动；环境内 CUDA runtime 11.6 |

### 1.1 环境构建

`scripts/prepare_environment.sh` 根据 `environment.yml` 创建推理环境、注册项目源码并执行依赖检查；已有环境进入安装与校验流程。报告保存于 `runs/validation/environment/`。

```bash
bash scripts/prepare_environment.sh
```

检查覆盖依赖导入、CUDA 可用性和受保护环境的元数据一致性，不初始化模型或连接设备。`--verify-only` 用于校验已有环境。

### 1.2 应用终端

应用命令使用 `.envs/inference` 中的解释器。终端初始化如下：

```bash
unset PYTHONPATH PYTHONHOME LD_LIBRARY_PATH
export PYTHONNOUSERSITE=1
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate ./.envs/inference
```

清理环境变量用于隔离 ROS 与推理依赖。ROS 驱动和桥接运行于独立终端，使用第 4 节的启动环境。环境路径由 Conda 显式激活，仓库目录不参与解释器选择。

## 2. 模型与控制资源

### 2.1 模型获取与完整性校验

当前模型为官方仿真 Push-T 图像 Transformer checkpoint。`models/checkpoint_manifest.json` 固定下载地址、文件大小和 SHA-256；下载结果写入 `models/pusht_image_transformer.ckpt`。

```bash
python scripts/fetch_checkpoint.py
python scripts/verify_bundle.py --check-model
```

两项操作的职责与结果如下：

| 工具 | 输入与校验对象 | 成功结果 |
|---|---|---|
| `fetch_checkpoint.py` | 模型清单及官方权重文件 | 大小与 SHA-256 一致，输出 `verified: true`；已有有效文件通过校验后复用 |
| `verify_bundle.py --check-model` | 固定上游源码、ur_rtde 源码与补丁、checkpoint | 输出源码计数及 `patch_verified: true`、`checkpoint_verified: true` |

固定源码基线包含 369 个策略文件和 339 个 SDK 文件。资源校验不反序列化模型、不初始化 CUDA，也不访问设备；模型加载由运行模式触发。

`models/transformer_config.yaml` 是模型配置参考。网络结构由 checkpoint 内嵌配置构建，EMA 权重与归一化状态从 checkpoint 的模型参数加载。运行配置 `config.yaml` 负责硬件、路径与会话设置。

### 2.2 控制扩展构建

`execute` 使用项目专用的 `dp_ur7e_rtde_control` 扩展。构建脚本以 `third_party/ur_rtde_guarded/` 为输入，完成编译、原生回环测试及模块共存检查后，生成 `.runtime/control_backend/manifest.json`。

```bash
python scripts/build_backend.py --jobs 2
```

扩展与推理环境的 Python ABI 绑定，在部署主机编译。`--plan` 可查看构建命令。构建测试不连接机械臂；已激活扩展由清单记录来源和二进制哈希，候选构建失败时保留原激活版本。

状态采集使用已安装的 `rtde_receive`；运动执行加载私有 Control 模块，两者职责分离。扩展加载规则与控制补丁见[技术报告](technical_report.CN.md#4-动作执行)。

## 3. 设备与运行配置

从[配置模板](../config.example.yaml)建立本地配置：

```bash
cp -n config.example.yaml config.yaml
```

`config.yaml` 使用 schema 2。`project_root` 相对配置文件目录解析，其余项目路径相对 `project_root` 解析。部署配置主要包含以下接口：

| 配置组 | 核对内容 |
|---|---|
| `paths` | 上游源码、权重、图像交换文件与运行记录路径 |
| `robot` | 控制器地址、采集频率、坐标系及激活 TCP |
| `camera` | 图像话题、`frame_id`、裁剪区域和桥接频率 |
| `observation` | 观测窗口长度、采样时间网格、时效与配对阈值 |
| `mapping` | 虚拟动作坐标与 UR 基坐标系的映射 |
| `inference`、`execution` | 设备、随机种子、记录范围及执行后端 |

模板地址 `192.0.2.1` 为文档占位地址，仅允许 `inspect`。硬件模式要求实际控制器地址。相机型号和序列号为描述字段，设备选择由外部驱动的启动参数完成。

当前接口固定为两步 `96×96` RGB 观测与二维位置。工具 TCP 为 `[0,0,0.244,0,0,0]`，单位为米和旋转向量弧度；执行模式同时核对配置声明和控制器激活 TCP。虚拟动作坐标的工程映射不包含相机标定。

完整字段见[附录 B](#附录-b-配置字段)。模型接口、坐标变换及数值限制见[技术报告](technical_report.CN.md)。

## 4. 运行接口

### 4.1 进程与数据流

相机驱动发布 RGB 话题；桥接将图像转换为本地 NPZ 数据；策略应用读取图像并通过 RTDE 获取机器人状态。应用内部自动完成模型初始化、采集线程管理及所选模式的处理流程。

| 进程 | 环境与入口 | 输出 |
|---|---|---|
| 相机驱动 | ROS 环境；[相机启动配置](#附录-a-相机配置) | `/wrist_camera/color/image_raw` |
| 图像桥接 | ROS 环境；`camera-bridge` | `paths.frame_store` 指定的图像交换文件 |
| 策略应用 | 推理环境；`inspect / capture / shadow / preview / execute` | 运行记录；`execute` 另发送运动命令 |

桥接和应用部署于同一主机。应用直接建立 RTDE 接口，不依赖 ROS 机器人驱动。图像流重启后需建立新的应用会话。

### 4.2 图像桥接

在 ROS 终端加载环境并启动桥接。源码安装的相机驱动还需加载其工作区环境。

```bash
source /opt/ros/humble/setup.bash
export PYTHONNOUSERSITE=1
export PYTHONPATH="$PWD/src:$PYTHONPATH"

/usr/bin/python3 -m dp_ur7e camera-bridge --config config.yaml
```

桥接校验话题类型、图像编码和 `frame_id`，按配置写入图像交换文件。策略应用从该文件构建观测窗口。

### 4.3 策略应用

在第 1.2 节的推理环境中，通过 CLI 选择运行模式：

| 模式 | 处理范围 | 运动控制 |
|---|---|---|
| `inspect` | 校验配置、资源路径与模型文件 | 不连接设备 |
| `capture` | 采集并保存一个真实观测窗口 | 仅 Receive |
| `shadow` | 真实观测采集、策略推理与结果记录 | 仅 Receive |
| `preview` | 推理、动作映射、过滤与目标预览 | 仅 Receive，读取控制器状态 |
| `execute` | 推理、目标检查、运动执行与反馈确认 | Receive 与私有 Control |

影子推理入口：

```bash
python -m dp_ur7e shadow --config config.yaml
```

实机执行要求控制器处于 Remote Control、正常安全模式、程序空闲且机械臂静止，并完成激活 TCP 与运动范围核对。`--site-ready` 是该次执行的显式现场条件声明：

```bash
python -m dp_ur7e execute --config config.yaml --site-ready
```

`preview` 和 `execute` 先完成预热，再处理最多三个候选目标。执行模式经过限幅、平滑、控制器检查及反馈确认；完整控制约束见[技术报告](technical_report.CN.md#4-动作执行)。诊断模式与执行模式为独立入口。

应用退出时释放自身线程和连接，外部驱动与桥接保留各自生命周期。运动命令不自动重试，程序不自动返回初始位姿。

## 5. 运行记录与验证

每次应用会话输出运行目录 `runs/<UTC>_<short-id>/`：

| 文件 | 内容 |
|---|---|
| `metadata.json` | 模式、配置、环境与模型来源 |
| `events.jsonl` | 观测、预测、过滤、命令确认、实测反馈和结束状态 |
| `observations/*.npz` | 策略输入窗口；capture/shadow 由保存选项控制 |

`summarize_run.py` 读取指定目录的事件文件，输出命令确认数、完成运动数及位置指标；距离单位为米。`RUN_ID` 对应应用输出的实际会话目录名：

```bash
python scripts/summarize_run.py runs/RUN_ID
```

会话完成、命令确认和实测到位分别统计。运动证据由 `motion_command_acknowledged`、反馈及 `completed=true` 的 `motion` 事件组成。`filtered_prediction.executed=false` 表示候选生成时的状态，后续执行结果独立记录。任务成功率属于单独的评测指标。

### 最小影子推理验证样例

输入条件为有效设备配置、持续更新的 RGB 数据流和 RTDE 状态。设置 `inference.max_predictions=1`、`inference.save_observations=true`，以 `shadow` 运行，验证一条观测—预测—记录链路。

正常结束时，终端输出 `Recorded 1/1; executed=False`，并生成以下数据：

| 数据 | 预期结构 |
|---|---|
| `observations/000000.npz` | `image: [1,2,3,96,96]`、`agent_pos: [1,2,2]`，均为 float32 |
| `prediction` 事件 | `action_pred_px: [10,2]`、`preview.raw_action_px: [8,2]`；事件存储去除 batch 维 |
| 运行摘要 | `run_completed: true`；`acknowledged_motions`、`completed_motions` 和 `feedback_samples` 均为 0 |

样例结构与归档 shadow 记录一致，来源见[验证数据](validation.json)的 `non_motion_example`。该检查覆盖数据接口和推理输出，任务效果与当前版本实机回归另行评估。

## 6. 开发验证与故障定位

开发检查使用独立的 Python 3.11 环境，依赖由 `pyproject.toml` 的 `dev` 分组定义：

```bash
conda create --prefix .envs/dev python=3.11 pip --yes
conda activate ./.envs/dev
python -m pip install -e ".[dev]"
```

离线测试与静态检查入口：

```bash
python -m pytest -q
python -m ruff check src tests scripts
```

离线测试通过替身隔离模型与硬件边界；ROS 生命周期用例在 ROS 环境下执行。实机验收范围见[验证数据](validation.json)。

| 故障范围 | 检查对象 |
|---|---|
| 模块导入 | `sys.executable`、`sys.prefix`、源码注册位置 |
| 图像与观测窗口 | 驱动话题、`frame_id`、交换文件路径、时间戳及 RTDE 更新 |
| 模型或扩展校验 | 来源清单、文件哈希、Python ABI 与本机构建结果 |
| 目标拒绝或超时 | 观测年龄、推理耗时、工作空间限制和控制器状态 |
| 停止或清理异常 | 实际机器人状态、平台停止规程及错误记录；日志不构成停止确认 |

## 附录 A. 相机配置

单路腕部相机使用下列 RGB 配置；`CAMERA_SERIAL` 指定目标设备：

```bash
source /opt/ros/humble/setup.bash
CAMERA_SERIAL="YOUR_WRIST_CAMERA_SERIAL"

ros2 launch orbbec_camera gemini_330_series.launch.py \
  camera_name:=wrist_camera "serial_number:=$CAMERA_SERIAL" device_num:=1 \
  enable_color:=true color_format:=MJPG \
  color_width:=640 color_height:=480 color_fps:=30 \
  enable_depth:=false enable_left_ir:=false enable_right_ir:=false \
  enable_point_cloud:=false enable_colored_point_cloud:=false \
  enable_accel:=false enable_gyro:=false \
  publish_tf:=false enumerate_net_device:=false
```

| 组件 | 记录配置 |
|---|---|
| UR7e 控制器 | CB5 v5.5；PolyScope 5.23.0（平台报告） |
| 工具 TCP | `[0,0,244]` mm，零旋转 |
| 腕部相机 | Gemini 335L；固件 1.4.60；SDK 2.7.6 |
| ROS 驱动 | `orbbec_camera`，`gemini_330_series.launch.py` |
| 彩色流 | 640×480，配置帧率 30 fps，MJPG 设备传输格式 |

记录来源见[验证数据](validation.json)的 `hardware_reference`；ROS Wrapper 精确版本未归档。本机版本与可用参数通过驱动元数据核对：

```bash
ros2 pkg xml orbbec_camera --tag version
ros2 launch orbbec_camera gemini_330_series.launch.py --show-args
```

图像接口要求 `sensor_msgs/msg/Image`、`rgb8` 或 `bgr8` 编码、`wrist_camera_color_optical_frame` 坐标系及持续前进的时间戳。话题检查入口为：

```bash
ros2 topic info /wrist_camera/color/image_raw --verbose
ros2 topic echo /wrist_camera/color/image_raw --once --field header \
  --qos-reliability best_effort
```

30 fps 是请求采集频率，实际观测与推理频率由数据到达和处理耗时决定。参数定义见[官方启动文件](https://github.com/orbbec/OrbbecSDK_ROS2/blob/v2-main/orbbec_camera/launch/gemini_330_series.launch.py)。

## 附录 B. 配置字段

| 字段 | 作用 |
|---|---|
| `schema_version`、`project_root` | 配置版本为 `2`；项目根目录基准为配置文件所在目录 |
| `paths.upstream` | 固定的官方策略源码目录 |
| `paths.checkpoint`、`paths.checkpoint_manifest`、`paths.official_config` | 权重、模型清单、可读模型配置 |
| `paths.frame_store`、`paths.runs` | 图像交换文件和运行记录目录 |
| `robot.model`、`camera.model`、`camera.serial` | 硬件描述；实际相机由外部驱动选择 |
| `robot.ip` | 控制器 IP |
| `robot.state_interface`、`robot.receive_hz` | `rtde_receive_only`；采集请求频率，默认 125 Hz |
| `robot.pose_frame` | `ur_base` 坐标系声明；坐标变换由适配层计算 |
| `robot.declared_active_tcp_offset_m_rad` | 声明的激活 TCP 偏移，单位为米和旋转向量弧度 |
| `robot.report_tcp_offset_m_rad` | 报告 TCP 偏移，当前为 `[0,0,0.244,0,0,0]` |
| `robot.active_tcp_offset_verified_on_pendant` | 核对示教器激活 TCP 后设为 `true`；执行模式要求该确认 |
| `camera.topic`、`camera.expected_frame_id` | RGB 话题与光学坐标系名称，需匹配驱动输出 |
| `camera.image_shape_hw`、`camera.roi_xywh` | 输出固定 `[96,96]`；ROI 为源图像像素 `[x,y,width,height]`，`null` 表示中心正方形裁剪 |
| `camera.publication_hz`、`camera.frame_store_poll_hz` | 桥接写入上限 30 Hz；文件轮询频率 100 Hz，不改变相机曝光频率 |
| `observation.n_obs_steps`、`observation.rate_hz` | 两步观测，标称时间网格为 10 Hz |
| `observation.max_age_s`、`observation.max_acquisition_skew_s` | 样本年龄上限 0.5 s；相机与状态配对时间差上限 0.05 s |
| `observation.startup_timeout_s` | Capture/shadow 的无效观测重试超时，默认 20 s |
| `mapping.mode`、`mapping.calibration_status` | `relative_anchor`，标记为 `engineering_mapping_not_calibrated` |
| `mapping.anchor_px`、`mapping.pixels_per_m` | 初始虚拟坐标 `[256,256]`；比例 `[1000,1000]` 虚拟像素/米 |
| `mapping.axes_in_ur_base`、`mapping.model_bounds_px` | 基坐标系 XY 轴；虚拟坐标范围 `[0,512]` |
| `inference.device`、`inference.seed` | 计算设备，默认 `cuda:0`；随机种子 42 |
| `inference.max_predictions`、`inference.max_duration_s` | Shadow 目标记录数 20；capture/shadow 会话时长上限 120 s |
| `inference.save_observations` | capture/shadow 输入窗口保存开关，默认 `true` |
| `execution.implementation`、`execution.default_mode` | 固定为 `guarded` 和 `preview`；执行由 CLI 模式显式选择 |

`preview` / `execute` 使用独立会话边界：首次观测等待 20 s，后续观测等待 10 s，观测循环截止时间 60 s，最多三个候选；这些约束独立于 `inference.max_predictions` 和 `inference.max_duration_s`。启动、预热、控制器查询与清理时间计入各自流程，60 s 不构成整个进程的硬实时上限。preview/execute 始终保存输入窗口。
