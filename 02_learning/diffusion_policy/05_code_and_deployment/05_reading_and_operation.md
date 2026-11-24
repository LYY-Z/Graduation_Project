# 05　怎样读代码、准备环境、理解操作和检查记录

[教材目录](README.md) · 上一章：[控制和执行](04_control_and_execution.md)

本章把前四章连成可学习、可检查的顺序。命令分为本机无硬件检查、Linux 环境准备、以后现场操作模板、离线读记录。本文编写与核对时没有运行相机、连接机器人或进行模型推理。真实操作模板必须由负责现场的人在满足条件后使用，不能把整章当作“一键全部执行”的脚本。

## 1. 第一次阅读代码只做一条主线

不要从原 SDK 的几千行 C++ 开始，也不要一看到原仓库的 `eval_real_robot.py` 就直接运行。它们的设备假设和执行路径未必等于当前工程。

建议打开文件后按下面顺序跳转，每个函数只记输入、输出、状态变化、副作用与退出方式：

| 顺序 | 实际位置 | 第一次只回答这些问题 |
|---|---|---|
| 1 | [cli.py](../../../03_code/diffusion_policy_ur7e/src/dp_ur7e/cli.py) | 子命令有哪些？什么时候拒绝？什么时候才导入硬件相关代码？ |
| 2 | [config.py](../../../03_code/diffusion_policy_ur7e/src/dp_ur7e/config.py) | 路径从哪里算？单位、图像尺寸、观察长度怎样校验？ |
| 3 | [pipeline.py](../../../03_code/diffusion_policy_ur7e/src/dp_ur7e/pipeline.py) 的 `run_capture_shadow` | 无推理与有推理相差哪一步？为什么没有控制连接？ |
| 4 | 同文件 `run_execution` | 预演与实机在哪个条件分叉？模型、会话、基线和控制创建顺序怎样？ |
| 5 | [hardware/observations.py](../../../03_code/diffusion_policy_ur7e/src/dp_ur7e/hardware/observations.py) | `SensorSession` 怎么拥有资源？`ObservationHistory.build` 怎样选两帧？ |
| 6 | [inference/policy.py](../../../03_code/diffusion_policy_ur7e/src/dp_ur7e/inference/policy.py) | `load_policy` 与 `predict` 怎样区分？保留了哪个权重与 normalizer？ |
| 7 | 原 [Transformer 策略](../../../03_code/diffusion_policy_ur7e/third_party/diffusion_policy/diffusion_policy/policy/diffusion_transformer_hybrid_image_policy.py) | 只沿 `predict_action` 和 `conditional_sample` 的当前分支读 |
| 8 | `pipeline.prepare_candidate` 和 [control/safety.py](../../../03_code/diffusion_policy_ur7e/src/dp_ur7e/control/safety.py) | 二维输出怎样限幅、平滑、锁定和消耗预算？ |
| 9 | [control/robot.py](../../../03_code/diffusion_policy_ur7e/src/dp_ur7e/control/robot.py) | 哪一行真的发送？前后各有什么检查和记录？ |
| 10 | [recording.py](../../../03_code/diffusion_policy_ur7e/src/dp_ur7e/recording.py) | 文件是什么格式？每条结论能在哪里找到证据？ |

第二遍再读 `camera_bridge.py` 的 ROS 生命周期、`camera.py` 的字节与原子帧、`robot_state.py` 的快照一致性、`geometry.py` 的 TCP 变换。第三遍才深入私有 SDK 和底层发送行为。每一遍都有明确问题，就不容易被细节淹没。

### 给自己做一份函数阅读卡

以 `prepare_candidate` 为例：

```text
输入：模型输出、映射、ActionGuard、当前TCP、来源年龄和模型长度
检查：输出形状/有限性、模型边界、当前状态和执行限幅
处理：取action[0,0] → 逆映射 → guard.propose
输出：原始二维动作、三维候选、六维小目标、年龄和夹爪hold说明
副作用：不发送机器人命令；guard.propose不commit执行预算
失败：抛出异常，由外层流程记录和退出
```

“副作用”是函数除了返回值以外对外部造成的变化，例如写文件、开线程、连设备或修改对象状态。能准确区分这些，比背函数名更有帮助。

## 2. 六个命令各自做到哪一层

| 子命令 | 读本地配置/清单 | 读真实输入 | 加载策略并推理 | 生成过滤后目标 | 创建运动 Control |
|---|---|---|---|---|---|
| `inspect` | 是 | 否 | 否 | 否 | 否 |
| `camera-bridge` | 是 | 相机 ROS 消息 | 否 | 否 | 否 |
| `capture` | 是 | 相机与只读机器人状态 | 否 | 否 | 否 |
| `shadow` | 是 | 是 | 是 | 保存原始动作与工程预览 | 否 |
| `preview` | 是 | 是，并读执行基线/Dashboard | 是 | 是 | 否 |
| `execute` | 是 | 是 | 是 | 是 | 满足显式条件后才创建 |

`shadow` 中的工程预览是输出动作的数值逆映射，不等于 `preview` 中按 `ActionGuard` 生成的受限目标；两者都不发送运动。`preview` 会对真实静止基线和执行条件做更多读取，但不创建运动控制连接。

`--site-ready` 只允许与 `execute` 搭配；`execute` 缺少该参数会在命令解析阶段拒绝。还必须有真实人工核对后的 TCP 声明和其他检查。配置的默认模式是预演，单独修改配置不会授权运动。

`inspect` 在没有权重时仍能报告静态契约，此时 `checkpoint_present=false`、哈希未验证、`ready_for_inference=false`。存在且匹配时可报告文件层准备就绪，但 **`ready_for_inference=true` 只代表该检查对权重文件的判断**，不代表依赖、CUDA、相机、现场或机器人已经全部验收。

新 CLI 会拒绝把 `192.0.2.1` 等文档地址用于硬件模式。复制示例配置后直接运行硬件命令应得到明确拒绝，不能把占位地址超时当作真实机器人故障。

## 3. 在 Windows 本机做不涉及设备的阅读检查

下面是以后在本机建立普通开发环境的示例，不是本轮已经执行的操作记录。若已有合适环境，可以直接使用；创建新 `.venv` 的目的是只给本项目安装小型开发依赖，不安装 ROS、旧策略全部依赖或私有控制扩展。

```powershell
Set-Location 'G:\毕设\03_code\diffusion_policy_ur7e'
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e '.[dev]'
.\.venv\Scripts\python.exe -m dp_ur7e --help
.\.venv\Scripts\python.exe -m pytest -q
```

`-e` 是 editable，即让安装指向当前源代码；`.[dev]` 表示本项目及其 dev 可选依赖。这里的开发环境不是 Linux 上 `.envs/inference` 的替代品，默认不执行权重推理。

帮助输出应列出 `inspect,camera-bridge,capture,shadow,preview,execute` 与 `--config`、`--site-ready`。默认测试使用伪造数据与对象，不连接真实设备；某些 ROS 生命周期测试在缺 ROS 环境中会明确跳过。通过数和跳过数以本次实际输出和验证记录为准，不把它们记成任务成功次数。

如果只想检查公开示例契约，可明确使用模板：

```powershell
.\.venv\Scripts\python.exe -m dp_ur7e inspect --config config.example.yaml
```

预期 JSON 包含：

```json
{
  "input_shapes": {"image": [1, 2, 3, 96, 96], "agent_pos": [1, 2, 2]},
  "model_loaded": false,
  "hardware_connected": false
}
```

这里只列关键字段，真实输出还有根路径、checkpoint 清单、是否存在和是否核验。它可能读取并哈希本地权重文件，但不会反序列化模型或接设备。

## 4. 测试为什么能不接机器人

单元测试用可控的小输入检验一个具体规则。例如用 `[3,4] mm` 检查范数限幅，用假时间检查观察过期，用伪控制对象检查 ready 失败时是否从未调用 `moveL`。

“fake”是有简单行为的替身；“mock”常用于记录调用或指定返回值。测试里能让 `getTCPOffset()` 返回一个不匹配值，再断言执行器抛错且不发送。真实现场不适合为了验证错误分支而故意设错 TCP，这正是离线替身测试的价值。

但替身不能证明网线、控制柜固件、相机驱动、GPU、物理误差和真实急停响应。因此验证应分层理解：

新增加的 [test_pipeline_offline.py](../../../03_code/diffusion_policy_ur7e/tests/test_pipeline_offline.py) 还会把真实主流程连起来检查：用合成 RGB、替代策略和假设备，运行真正的观察历史构造、共享 `predict` 包装、工程映射、ActionGuard、GuardedRobot 到位监测和落盘记录，分别走 preview 与 execute 分支。替代策略直接产生预设数字，假设备按测试约定更新位置；没有真实 Transformer/DDPM、GPU 推理、RTDE 原生传输或物理运动。这里测试中的 `execute=True` 是进入被替身隔离后的代码分支，不能读成实机执行结果。

| 检查层 | 能支持的结论 | 仍缺的内容 |
|---|---|---|
| 语法/静态检查 | 文件可解析，明显导入或变量问题被发现 | 实际运行行为 |
| 无硬件单元测试 | 数值、时间和异常路径符合测试条件 | 真实驱动与设备 |
| 文件与来源清单 | 源码/补丁/权重匹配记录 | 模型输出与物理行为 |
| 依赖导入/原生回环 | 指定环境可导入；本机通信逻辑可测 | 现场机械臂 |
| 真实 capture/shadow | 实际输入和模型推理能接通 | 实际运动 |
| 真实受限 execute | 本次小目标下发及反馈链路通过 | 长时稳定、碰撞规划、任务性能 |
| 任务评测 | 给定任务与成功判据下的统计表现 | 超出测量条件的泛化 |

每层失败都应先解释原因，不能用上一层通过代替。新版当前有无硬件验证，原版曾有实机短测，两者必须分别写清。

## 5. Linux 模型环境：准备与启动是不同操作

实际部署面向 Linux；当前 Windows 阅读环境不能照搬 `/usr/bin/python3` 等路径。以下 `DP_ROOT` 用通用占位路径，请由操作者替换为准备好的新工程绝对路径，不照抄旧工程服务器目录。

```bash
export DP_ROOT=/absolute/path/to/diffusion_policy_ur7e
cd "$DP_ROOT"
cp -n config.example.yaml config.yaml
```

`cp -n` 不覆盖已存在本地配置；已有 `config.yaml` 时先阅读，不把模板强行覆盖上去。模板只提供默认字段，真实设备 IP、相机选择、环境和现场核对需由操作者补齐。配置的 `project_root: .` 指配置文件所在根目录；移动配置到子目录时要重新明确根目录关系。

[prepare_environment.sh](../../../03_code/diffusion_policy_ur7e/scripts/prepare_environment.sh) 只准备/检查工程自己的 `.envs/inference`。Conda 可执行文件从 `CONDA_EXE` 或 PATH 寻找，依赖规格在 `environment.yml`。它使用工程缓存与环境目录，并保存原有环境元数据和设置的前后对比。

```bash
bash scripts/prepare_environment.sh --help
```

准备新环境或核查已有环境时，实际模板分别为：

```bash
bash scripts/prepare_environment.sh
bash scripts/prepare_environment.sh --verify-only
```

这两行是两种选择，不是要求每次都连续运行。准备过程可能下载并安装依赖，需要时间和磁盘；`--verify-only` 用于环境已经存在时。`--allow-cpu` 只允许在依赖核查中没有可用 CUDA，不把 CPU 检查等同于真实 GPU 推理性能验证。

脚本不启动相机、桥接、模型推理或机器人。它也不是删除并重建所有 Conda 环境的工具；发现已有前缀不完整时会拒绝，需要检查该工程目录，而不是盲删他人环境。

在 ROS 系统终端中可单独验证桥接依赖导入：

```bash
source /opt/ros/humble/setup.bash
/usr/bin/python3 "$DP_ROOT/scripts/check_environment.py" ros
```

该检查不创建 ROS 节点。记录位于 `runs/validation/environment/`，例如 `protected_before.json`、`protected_after.json`、`verification.json`、`ros_imports.json`、Conda/Pip 版本清单。准备脚本保存的输出与检查脚本保存的结构化文件用途互补。

## 6. 权重和私有后端怎样准备

下载文件、编译控制扩展与连接设备是三件事。先看工具帮助和计划，再在已确认环境中使用相应准备工具；这里没有任何“下载后顺便试一下机器人”的隐含步骤。

```bash
python scripts/fetch_checkpoint.py --help
python scripts/verify_bundle.py --help
python scripts/build_backend.py --help
```

权重下载按清单校验，不使用随手复制的 URL 当成位置参数。明确参数形式为：

```bash
python scripts/fetch_checkpoint.py \
  --manifest models/checkpoint_manifest.json \
  --output models/pusht_image_transformer.ckpt
python scripts/verify_bundle.py --check-model
```

`verify_bundle` 核对第三方源码和补丁；`--check-model` 进一步核对权重，不反序列化模型。使用 `--output` 可将报告保存到指定验证目录，保留实际输出，不能把本章示例当作已生成报告。

私有后端先查看构建计划：

```bash
python scripts/build_backend.py --plan
```

计划应显示 CMake 构建命令、原生回环测试等事项，并表明不安装到全局环境、不连接机器人。真正构建仅在 Linux 且依赖已准备时使用：

```bash
python scripts/build_backend.py \
  --python "$DP_ROOT/.envs/inference/bin/python" --jobs 2
```

源码 `third_party/ur_rtde_guarded/source/` 已是固定的、应用过受限修改的审计树。`guarded.patch` 保存修改来源，**不要再对该树应用一次补丁**。构建工具会先核对来源，复制到工程缓存构建，运行原生回环，生成 `.runtime/control_backend/manifest.json` 并校验私有模块可与 Receive 共存。它不替换系统安装的普通 `ur_rtde`，也不向机器人发送控制命令。

本轮不进行目标服务器构建或实机复验。工具“已编写”和后端“已在目标服务器可用”是不同结论，需要分别有验证记录。

## 7. 以后现场操作时为什么分三个终端

三个终端各有明确责任：A 运行相机驱动；B 用系统 ROS Python 做桥接；C 用隔离 Python 做采集、推理或受限执行。它们引用同一份本地配置和帧路径。终端不是三个模型，也不是三个运动控制程序。

以下命令是**已经准备好 Linux 环境后的现场模板**。先由现场人员确认设备和空间条件；相机驱动已经运行时，不启动第二份。命令中的相机序列号由本地信息选择，不在教材内固化某台设备标识。

### 终端 A：相机驱动

干净的 ROS 终端，不激活模型环境：

```bash
source /opt/ros/humble/setup.bash
ros2 topic info /wrist_camera/color/image_raw
```

如果已有正确话题和驱动，保留现有实例即可。只有确实需要本次启动新驱动时，按当前安装驱动支持的参数使用单相机模板；本工程本身不安装或启动该驱动：

```bash
export CAMERA_SERIAL='填写现场确认的相机序列号'
ros2 launch orbbec_camera gemini_330_series.launch.py \
  camera_name:=wrist_camera serial_number:="$CAMERA_SERIAL" device_num:=1 \
  enable_color:=true color_width:=640 color_height:=480 \
  color_fps:=30 color_format:=MJPG \
  enable_depth:=false enable_left_ir:=false enable_right_ir:=false \
  enable_point_cloud:=false enable_colored_point_cloud:=false \
  enable_accel:=false enable_gyro:=false publish_tf:=false enumerate_net_device:=false
```

预期是单路 RGB 话题，来源 frame 与配置一致，时间不断推进。本模板明确不把深度、点云和 IMU 输入策略；若本机驱动版本不识别参数，先检查本机已安装的 launch 参数，不凭教材绕过错误。

### 终端 B：相机桥接

```bash
export DP_ROOT=/absolute/path/to/diffusion_policy_ur7e
source /opt/ros/humble/setup.bash
export PYTHONNOUSERSITE=1
export PYTHONPATH="$DP_ROOT/src${PYTHONPATH:+:$PYTHONPATH}"
cd "$DP_ROOT"
/usr/bin/python3 -m dp_ur7e camera-bridge --config "$DP_ROOT/config.yaml"
```

预期日志说明 topic、帧文件位置和本次 stream ID；`.runtime/wrist_rgb.npz` 持续更新。桥接启动不等于驱动启动，旧 NPZ 存在也不等于当前有新图。把历史 `runs/` 中某个配置复制过来，可能让桥接向历史路径写数据，应使用本次自己的本地配置。

桥接也经过统一 CLI 配置检查；即使当前不发送机器人命令，文档地址占位仍需按本地设备配置完成后才能进入硬件模式。

### 终端 C：模型或采集流程

该终端不 source ROS，显式使用隔离解释器：

```bash
export DP_ROOT=/absolute/path/to/diffusion_policy_ur7e
cd "$DP_ROOT"
unset PYTHONPATH PYTHONHOME LD_LIBRARY_PATH
export PYTHONNOUSERSITE=1
export OMP_NUM_THREADS=4
export MKL_NUM_THREADS=4
export XDG_CACHE_HOME="$DP_ROOT/.cache/xdg"
export TORCH_HOME="$DP_ROOT/.cache/torch"
export HF_HOME="$DP_ROOT/.cache/huggingface"
nvidia-smi
```

先看 GPU 占用，选择现场允许使用的设备，不终止别人的任务。`CUDA_VISIBLE_DEVICES=0` 是示例选择，设定后程序中的 `cuda:0` 指当前可见的第一块卡，不必等于物理全局编号 0。

```bash
export CUDA_VISIBLE_DEVICES=0
"$DP_ROOT/.envs/inference/bin/python" -m dp_ur7e inspect --config config.yaml
```

这一条仍不连硬件。只有环境与配置检查完成后，才按下一节逐级选择对应现场步骤。

## 8. 采集、影子、预演到执行的分级模板

这四步不是必须在一个 shell 中自动连续完成的脚本。每一步都检查输出和记录，前一层未理解的失败不应靠直接跳到执行解决。

### 8.1 真实观察采集：capture

```bash
"$DP_ROOT/.envs/inference/bin/python" -m dp_ur7e capture --config config.yaml
```

它读取真实相机和状态，构造一组合法两帧观察并保存，不加载策略。预期打印独立 Run directory 和 `Recorded 1/1; executed=False`；事件有 observation 和 completed。若最初显示 waiting，允许在启动期限内等待历史填满；持续 stale/skew 需要排查。

### 8.2 原模型影子推理：shadow

```bash
"$DP_ROOT/.envs/inference/bin/python" -m dp_ur7e shadow --config config.yaml
```

它读真实输入并做原模型推理，记录原始动作和工程预览，不创建运动控制客户端。记录次数来自 `inference.max_predictions`，模板当前为 20；不要把 20 当成命令条数。每次记录 `executed=False` 表示这条流程没有下发。

### 8.3 受限候选预演：preview

```bash
"$DP_ROOT/.envs/inference/bin/python" -m dp_ur7e preview --config config.yaml
```

它先预热并丢弃输出，再以真实静止状态为基线，生成最多三轮过滤目标，不创建 Control。预期出现类似 `FILTERED 1 live= False completed_moves= 0` 的打印。具体空格以真实输出为准，重要的是 mode 和事件含义。

预演不保存可直接发送的“批准计划”。后续执行会重新采集和预测，不回放预演结果；现场状态变化后，旧候选也不应被拿来发送。

### 8.4 受监督实体短测：execute

仅在现场有人看护、急停可用、相关连杆/工具/相机/线缆空间清楚、设备模式和 TCP 真正核对、没有其他控制程序占用时，才由负责现场的人使用这个模板。还要先在本地配置把 `active_tcp_offset_verified_on_pendant` 设为真实核对结果，不能因为想消除报错就写 true。

```bash
"$DP_ROOT/.envs/inference/bin/python" -m dp_ur7e execute \
  --config config.yaml --site-ready
```

这条命令会创建真实控制通道并允许受限运动。最多三条，单步 1 mm、累计命令路径 3 mm、速度 2 mm/s，当前 Z/姿态锁定、夹爪保持。若候选低于死区可能只保持；若检查失败可能退出；只有实际反馈满足到位规则才增加完成数。不会自动回起点。

**新版尚未进行的实机复验不能由本章命令模板补成“已完成”。** 现场使用后要保存本次自己的记录、版本和结果，不能沿用旧版成功记录当作本次证据。

## 9. 停止与资源清理的实际边界

正常情况下等待 C 完成本轮，再在 B 按 Ctrl+C 停桥接，最后退出本次在 A 启动的驱动。若 A 中使用的是别人管理的共享驱动，不应把它当成本次拥有的进程结束。

运行中出现危险或未知运动时按现场预案使用急停；Ctrl+C 和 SIGTERM 会尝试软件退出与清理，但不是物理急停的替代品。软件关闭只处理自己的控制脚本、连接、线程和文件。不要用 `pkill python`、`killall` 或“清理所有 ROS”之类无范围命令来结束本次作业。

失败后先确认现场状态，保留日志，确认是否已经发生部分运动。不要连续重启旧命令，也不要为了恢复把保护检查关闭。网络中断时软件停止尝试可能无确认，文档必须把“尝试停止”和“反馈确认停止”分开。

## 10. 当前 RunWriter 真实保存什么

每次采集、影子、预演或执行会建立独立目录，打印位置，以 UTC 时间和随机后缀区分：

```text
runs/<UTC时间_随机ID>/
├─ metadata.json
├─ events.jsonl
└─ observations/
   ├─ 000000.npz
   ├─ 000001.npz
   └─ ...
```

编号文件在调用 `writer.observation(index, arrays)` 时生成；capture/shadow 可受 `save_observations` 控制，预演/执行会记录对应观察。`000000` 是六位补零编号，不代表六张图，一个 NPZ 就包含这一轮的两帧张量和两帧位置。

当前没有默认生成聚合 `feedback.npz`、`predictions.npz`、`observations.npz` 或 `result.json`。旧规整计划列过这些目标格式，不能把规划中的文件名写成已经实现。真实反馈在 `events.jsonl` 的 `motion_feedback` 中，原始预测和过滤目标也保存在事件里。

### metadata.json：这次运行的背景

它是一个完整 JSON 对象，保存模式、配置、环境版本、模型详情、执行限制及在对应模式可用的初始状态和映射原点。运行推进时可以完整替换元数据文件，创建时间保留。某些字段只在执行路径出现，不应要求 capture 也有初始力和私有控制信息。

`environment_versions()` 查询安装包版本，不调用策略。`None` 表示没有查到相关包，不等于版本号零。元数据可能含真实本机配置和主机名，因此公开报告前应检查内容；教材不需要复制这些个人机器信息。

### events.jsonl：一行一件事

JSONL 是 JSON Lines，每行是一个独立 JSON 对象，整文件不是带外层方括号的 JSON 数组。可以逐行读取，不要直接 `json.load` 整个多行事件文件。

```json
{"utc":"示例UTC时间","event":"filtered_prediction","index":0,"executed":false}
{"utc":"示例UTC时间","event":"motion_command_acknowledged","target":[0.25,0.42,0.70,0,3.14,0]}
{"utc":"示例UTC时间","event":"motion","completed":true}
```

这是删减字段后的格式教学例子，不是新的实机运行记录。实际日志包含完整目标、来源年龄、反馈等；不能从这个三行例子计算任何实验结果。

### observations/000000.npz：实际给模型的数组

可以在无硬件环境离线查看指定记录，路径必须替换为真正存在的本次文件：

```bash
python - <<'PY'
from pathlib import Path
import numpy as np

path = Path('runs/填写已有运行ID/observations/000000.npz')
with np.load(path, allow_pickle=False) as data:
    for name in data.files:
        array = data[name]
        print(name, array.shape, array.dtype)
    print('image range:', data['image'].min(), data['image'].max())
    print('positions:', data['agent_pos'])
PY
```

预期主要键为 `image` 和 `agent_pos`，shape 分别是 `(1,2,3,96,96)`、`(1,2,2)`，类型为 `float32`；图像一般在 0–1。数值全部为零或画面错误时即使 shape 正确也要继续检查来源。NPZ 是实际输入，不是相机原始 480×640 全幅录像。

## 11. 用汇总工具核查证据，而不是只看终端最后一句

[summarize_run.py](../../../03_code/diffusion_policy_ur7e/scripts/summarize_run.py) 读取已有事件，可以离线运行，不连接设备：

```bash
python scripts/summarize_run.py 'runs/填写已有运行ID'
```

需要保存汇总时指定新的输出文件：

```bash
python scripts/summarize_run.py 'runs/填写已有运行ID' \
  --output 'runs/validation/填写独立汇总名.json'
```

它给出事件计数、ACK 数、已完成 motion 数、反馈条数，以及已完成运动的命令距离、实测起止距离、终点误差。`task_success_evaluated=false` 明确说明没有评估任务成功。

这些汇总来自事件，不替代原始事件、元数据和观察数组。若文件缺失、最后一行损坏或执行中断，应该保留原始状态并查明原因，不手工补一个 completed 来让汇总变好看。

手动检查至少回答：模式是什么；权重和配置是什么；两帧是否真实不同且有效；是否只有过滤预测；是否有 intent、ACK、反馈及 completed motion；是否出现 failed/stop_failed/control_cleanup_failed；最终程序完成不等于所有候选都移动；本次是否有独立任务成功判据。

## 12. 按报错阶段找原因

| 看到的现象 | 先理解它拒绝了什么 | 优先核对 |
|---|---|---|
| config 不存在或语法错误 | 没有合法的本地运行设置 | 文件位置、YAML 缩进和类型、是否复制模板 |
| documentation-only robot address | 仍在使用教材占位地址 | 在本机配置真实设备，别改掉占位保护 |
| ModuleNotFoundError | 当前解释器找不到依赖或包 | 系统 ROS 与隔离模型 Python 是否混用 |
| checkpoint 哈希不符 | 文件不等于固定来源 | 大小、完整下载和清单；不关闭校验 |
| waiting/历史不足 | 暂时凑不出合法两帧 | 驱动、桥接、状态是否推进，是否处于启动等待期 |
| stale/skew/clock reset | 样本年龄、时差或时钟连续性不合格 | 帧路径、负载、ROS 延迟、控制柜重置；不直接放宽年龄 |
| optical frame 不符 | 图像来源标签不等于预期 | topic、camera_name、实际驱动输出 |
| 私有后端清单/哈希不符 | 构建产物与审计来源不能对应 | 使用本工程构建工具，保存日志，不回退普通 Control |
| Dashboard/TCP/IK 拒绝 | 执行现场或目标条件不合格 | 模式、现场激活 TCP、当前姿态和近邻解 |
| ready/ACK/到位超时 | 下游状态或运动没有按约定完成 | 保留原错误、反馈和停止情况，先确认实际现场 |
| 输出形状正确但任务方向错误 | 接口连通，任务语义可能未适配 | 视角、坐标、任务定义、数据与模型适配 |

排错时先保存“第一条明确错误”。末尾的清理失败可能是后果；也可能需要独立处理，但不应覆盖最初原因。缺什么就补相应证据，不把所有问题都归咎于“Python 不会用”。

## 13. 给报告留下怎样的记录

原版成功短测是具体历史事实：3 条到位、132 条反馈、命令累计约 2.119 mm、净实测约 2.022 mm，推理约 0.60 s 一次。推理耗时不含采集、控制检查和实体运动，不能写成完整闭环频率或端到端总延迟。

新版整理后的功能需要按新版本重新验证，不能直接沿用旧运行的结果。无硬件测试的结论写“此版本通过这些数值和异常路径检查”；真实链路复验后再写“该版本在这些现场条件下完成受限目标”；真实任务实验则另外给 episode、成功标准、重复次数、失败类型和统计量。

公开代码文档告诉其他人怎样使用项目，个人学习教材帮助你理解为什么，原始日志支撑已发生事实。任务报告可以提炼三者，但不应把聊天过程或没有执行的命令粘贴成实验步骤已经发生。

## 练习与答案

1. `inspect` 显示 `ready_for_inference=true`，能否跳过环境和相机检查？
2. capture 成功后缺少 `feedback.npz`，这是否意味着记录工具坏了？
3. 测试报告全部通过但 ROS 测试跳过，可以说相机实测没问题吗？
4. 终端最后显示 completed，怎样确认究竟移动了几条？
5. 为什么执行之前不把预演保存的三个目标直接回放？
6. 一次受限运行结束后想分析原始 RGB 全幅视频，`observations/000000.npz` 是否足够？

答案：

1. 不能。这是 inspect 对权重文件的静态判断，尚未加载策略或检查所有运行条件。
2. 不是。当前格式本来就是 metadata、events 和逐轮 observations；capture 本身不运动，实际反馈事件属于执行路径。
3. 不可以。无 ROS 测试环境没有覆盖真实驱动；跳过是验证范围说明，不是假装通过。
4. 查看 `motion completed=true` 的数量，再核对 ACK、feedback、failed 和保持事件。循环次数、候选数、完成数不能混用。
5. 现场与观察已经变化，而且预测来源有年龄限制。真实执行重新采集和推理，避免发送陈旧目标。
6. 不够。保存的是缩放、排轴后的模型输入，两帧窗口可能重叠，也不等于原始连续录像；需要单独规划视频记录并说明其时间关系。

建议最后在不连接设备的情况下完成一个口头复述：从统一命令说到 `cli.main`，从配置说到 `SensorSession.observation`，从 `policy.predict_action` 说到 `prepare_candidate`，再解释只有执行路径才到 `GuardedRobot.move`，并指出每一层应留下什么证据。能讲清这条路线，就已经从“知道论文想法”走到了“能负责地阅读部署工程”。

[返回目录](README.md) · [回看第 1 章：工程和 Python](01_project_and_python.md)
