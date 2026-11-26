# Go2-W 机载算力：能否实时跑 MPC 与 RL 推理（调研，2026-11-26）

说明：所有数字均带出处；查不到的写"未核实"。本文为精简核查，非实测。

## 1. Go2-W 机载计算

| 项目 | 结论 | 出处 |
|---|---|---|
| 基础算力 | 官方规格页写"Basic Computing Power：8-core High-performance CPU"，扩展项写"Multiple brands and models available, such as Orin NX, etc." | unitree.com/go2-w/ |
| 基础主控芯片型号、主频 | **未核实**。官方未公开。.161 板上 RK3588 的说法仅见于 G1 文档，属于类比，不可当作 Go2-W 事实 | zeulewan G1 笔记 |
| 基础主控是否开放用户程序 | 基本不开放。社区开发手册称用户无法登录 .161 主板，只能登录 .18 的 Jetson。也有非官方指南用默认口令 SSH 到 .161，不建议依赖 | miye-kim YMO develop_manual；mybotshop 论坛；ACRE wiki |
| EDU 扩展 | Go2 EDU 为 Orin 扩展坞，标称 40 TOPS（Orin Nano）至 100 TOPS（Orin NX 16GB）。Go2-W 官方页未给 TOPS，**Go2-W 具体可选模组未核实** | unitree.com/go2/；UMBC testbed；QuakeLogic datasheet |
| 用户程序位置 | 两种：外接电脑（以太网 192.168.123.x，rl_sar 主流程）或扩展坞 Jetson（.18，SSH 后本地编译运行） | rl_sar README |

Orin NX 自身 CPU 为 8 核 Cortex-A78AE（NVIDIA Jetson Orin 页面），具体主频以所配模组为准，未逐项核实。

## 2. MPC 公开案例

| 案例 | MPC 类型 | 频率 | 硬件 | 出处 |
|---|---|---|---|---|
| legged_control（OCS2，A1） | NMPC + WBC | 作者称"接近 200 Hz" | 11 代 NUC，**外接电脑**；README 写明用外接设备如 NUC，仿真版"不要在机载电脑上跑" | github.com/qiayuanl/legged_control（已归档） |
| Go1 + legged_control（arXiv 2505.08574） | NMPC，用于生成专家数据训练多任务策略 | NMPC 100 Hz，WBC 500 Hz | 机载或外接**未说明** | arXiv 2505.08574 |
| Go2 QP 基准（arXiv 2502.01329，"Benchmarking Different QP Formulations and Solvers for Dynamic Quadrupedal Walking"） | SRBD 线性 MPC，N=10/20，acados QP 接口 | MPC 100 Hz，WBC 500 Hz | 在 Jetson Orin NX、LattePanda Alpha、桌面机上测了求解时间。Jetson 与 LattePanda 相近。N=20 时部分稠密形式过慢导致实验失败。具体毫秒数只在图 3，**未核实** | arXiv 2502.01329 |
| 轮足 22 自由度小型机器人（arXiv 2602.21612） | OCS2 SQP 全身 NMPC，horizon 1 s，步长 0.015 s | 50 Hz | 机载 Intel NUC10（i7，16 GB），非 Jetson | arXiv 2602.21612 |
| ReCo（arXiv 2610.01612，Go2 + 机械臂） | 策略感知 MPC | **未核实** | Jetson Orin NX，摘要称全程机载 | arXiv 2610.01612 摘要 |
| RK-MPC（Go1） | Koopman MPC | 估计器与控制器 500 Hz | Jetson Xavier NX 机载（检索摘要，未读全文） | arXiv 2604.04221 |

**轮足对计算量的影响**：Go2-W 为 16 个驱动关节（12 腿 + 4 轮）。2602.21612 中 22 自由度的轮足 NMPC 只做到 50 Hz，且用的是 x86 NUC，而不是 Jetson。说明 4 个轮自由度会让全身 NMPC 的状态与输入维度明显增大。这是依据该案例做的推断，非直接对比实验。

**未查到**：Go2/Go2-W 上由 Jetson 机载运行全身 NMPC（OCS2、Crocoddyl 等）并给出 Hz 的公开报告。unitree_guide、quad-sdk、Cheetah-Software 移植、Hybrid DIAL-MPC 的具体硬件与频率本次**未核实**。

## 3. RL 推理

- rl_sar：支持 go2 与 go2w（robot_lab 策略），可在 Gazebo、MuJoCo、实机运行。实机运行 `rl_real_go2 <网卡> [wheel]`。README 同时给出外接电脑流程与"Deploying on the Onboard Jetson"流程（Jetson 上 `./build.sh -m` 后运行，并可配 systemd 自启）。README 未写控制或推理频率（**频率未核实**）。出处：github.com/fan-ziqi/rl_sar。
- Go2-W 教程（isprout.com，Isaac workshop part4）：策略转 TensorRT FP16 在 Jetson 上运行，循环 50 Hz（20 ms），腿 20 ms、轮 10 ms 预算，观测 53 维、动作 16 维（12 腿 + 4 轮）。文中未实测推理时延，且观测分项与 53 维对不上，使用前需自行核对。Jetson 具体型号文中未写。
- unitree_rl_lab 文档（经 deepwiki 摘要）：策略频率 50 Hz，ONNX CPU 推理约 0.3–0.5 ms，Go2W 16 关节。二手来源，标记为部分核实。
- Go2 + Orin NX 的学习控制器稳定 50 Hz 并同时跑深度图像处理（arXiv 2505.09979 摘要级）。

## 4. 结论

| 方案 | 机载可行性 | 依据 |
|---|---|---|
| (a) 凸/质心 MPC | **可行，需 Orin NX 级模组**。基础主控不开放，不可用 | Go2 上 SRBD 线性 MPC 100 Hz，并在 Orin NX 上做过求解基准（2502.01329）。N 取 10 且选合适 QP 形式。N=20 稠密形式有失败 |
| (b) 全身 NMPC | **机载不推荐**，需先实测 | 公开案例均用 x86 NUC 或外接 PC（legged_control 约 200 Hz；轮足 50 Hz）。无 Jetson 机载全身 NMPC 的 Hz 报告 |
| (c) RL 推理 | **可行** | 50 Hz，ONNX/TensorRT 毫秒级，Jetson 机载有 rl_sar 与教程案例；亦可外接电脑 |
| (d) RL + MPC 混合 | **有条件可行** | RL 部分轻量，MPC 部分取决于类型：质心/SRBD MPC 可机载，全身 NMPC 走外接。ReCo 称 Go2 + Orin NX 全程机载策略感知 MPC，但频率未核实 |

**外接电脑方案**：通过网线接 192.168.123.x，由 rl_sar、unitree_sdk2 发布低层指令。legged_control 即采用外接 NUC。**以太网链路的实测延迟，本次未查到公开数值（未核实）**，需在本项目中自行测量。外接方案另需注意链路抖动对 500 Hz 级 WBC 的影响，因此 WBC 宜靠近机体运行。

## 建议的后续核实项
1. 确认所购 Go2-W 是否带 Orin 模组及型号（Nano 或 NX）。
2. 在目标 Jetson 上用 acados 或 OCS2 对 Go2-W 模型实测求解时间。
3. 实测外接以太网往返延迟。

## 出处清单
- https://www.unitree.com/go2-w/ ；https://www.unitree.com/go2/
- https://github.com/fan-ziqi/rl_sar ；https://github.com/qiayuanl/legged_control
- https://arxiv.org/abs/2502.01329 ；2505.08574 ；2602.21612 ；2610.01612 ；2604.04221 ；2505.09979
- https://isprout.com/posts/2025-12-18-isaac-workshop-part4
- https://cypress.umbc.edu/testbed/trace/trace-testbed-design/unitree-go2-edu-plus-qugv ；https://quakelogic.net/datasheets/QL-Unitree-Go2-EDU+.pdf
- https://miye-kim.github.io/YMO-support/go2/develop_manual ；https://forum.mybotshop.de/t/unitree-go2-network-setting/1153
