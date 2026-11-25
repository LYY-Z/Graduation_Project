# 服务器只读盘点

盘点时间：2026-11-24 14:34（服务器时间，UTC+8）。方式：SSH 只读命令（`nvidia-smi`、`lscpu`、`free`、`df`、`ps`、目录与包列表）。未安装、未修改、未启动任何任务。连接信息见[平台连接资料](../../02_learning/platform/vnc.md)；密码不写入仓库。

## 1. 用户提供 vs 实际核验

| 项目 | 用户提供 | 实际核验 |
|---|---|---|
| 设备 | 服务器3，RTXPro5000x2 | 主机名 `RTXPro5000x2` |
| GPU | RTX PRO 5000 × 2 | **NVIDIA RTX PRO 5000 Blackwell × 2**，单卡 48,935 MiB（约 48 GB），compute capability **12.0（sm_120）** |

## 2. 硬件与系统

| 项目 | 核验结果 |
|---|---|
| GPU 驱动 / CUDA | 驱动 580.178.04；系统 CUDA toolkit 13.0（`/usr/local/cuda-13.0`） |
| GPU 当前占用 | 两卡各约 6.3–6.7 GB、10–15% 利用率，来自另一位用户的 VLA 进程；属于他人任务，不得干预 |
| CPU | 2 × Intel Xeon Gold 6248R，共 96 线程 |
| 内存 | 251 GiB（可用约 228 GiB） |
| 系统 | Ubuntu 22.04.5 LTS，内核 6.8.0；系统 Python 3.10.12；ROS 2 Humble（`/opt/ros/humble`） |
| Conda | `/opt/miniconda3`（conda 26.1.1，不在默认 PATH） |

## 3. 磁盘：根分区接近满

| 挂载点 | 容量 | 已用 | 可用 | 说明 |
|---|---|---|---|---|
| `/`（含 `/home`） | 938 G | 860 G（97%） | **30 G** | 个人目录 `~` 已占 54 G |
| `/data` | 3.6 T | 250 G | 3.2 T | 他人数据，可写 |
| `/data2` | 3.6 T | 2.0 T | 1.5 T | 他人数据 |
| `/data3` | 3.6 T | 28 K | **3.4 T** | 空，可写 |
| `/data_backup` | 3.6 T | 1.9 T | 1.6 T | 备份盘 |

**影响**：Isaac Sim 环境、着色器缓存、训练日志和 checkpoint 不能继续放在 `~`。建议实施时在 `/data3/robotic_dog/`（个人子目录）建立工作空间与 Conda 环境目录（`CONDA_ENVS_PATH`、`CONDA_PKGS_DIRS`、缓存目录都指向这里）。待用户确认后再建。

## 4. 已有可复用环境（属于本项目历史工作）

| 环境 / 目录 | 内容 | 可复用判断 |
|---|---|---|
| `~/.conda/envs/lyy_locoformer_go2w_py311` | Python 3.11，**Isaac Sim 5.1.0（pip）**，PyTorch 2.7.0+cu128 | 软件栈支持 Blackwell（cu128 构建）；可作为 Isaac Lab / robot_lab 起点，是否已通过训练验证需查 `logs/stage1/` |
| `~/lyy_ws/locoformer_go2w/` | `third_party/IsaacLab`、`third_party/robot_lab` 源码快照，安装与验证日志 | Isaac Lab 与 robot_lab 的具体提交待核对；`runs/` 为空，尚无训练记录 |
| `~/lyy_ws/flair_reproduction/` | FLAIR CPU 复现环境（JAX 0.4.22）与运行结果 | 只用于已完成的 FLAIR 复现 |
| `~/RL_L/`（独立 miniconda，PyTorch 2.11.0+cu128） | 另一项目 | 非本项目，不改动 |
| `~/dog_projects/fzw/` | 机器狗数据记录 | 非本项目，不改动 |

## 5. 发现的问题

- 本账户有一个 Firefox 进程已运行约 8 天 19 小时，持续占用约 15 个 CPU 核（打开的是 FLAIR 复现的 HTML 结果页）。建议用户在远程桌面中关闭；本次未处理任何进程。

## 6. 对研究方案的约束

- **单卡 48 GB，不能按 96 GB 计算。** 多卡加速取决于具体代码是否支持分布式训练。另需扣除他人任务常驻的约 6–7 GB。
- **只能用支持 sm_120 的软件栈**：PyTorch ≥ 2.7（cu128）、Isaac Sim ≥ 5.x 一类版本。固定在 Isaac Sim 4.x / CUDA 11.x 的旧代码（如 GRAM 官方环境）需要移植，不能直接照搬。是否能用 PTX 兼容运行，需逐项实测。
- 已有 Isaac Sim 5.1 环境可节省搭建时间，但要先确认 Isaac Lab 与 robot_lab 的版本是否匹配候选论文的代码。
