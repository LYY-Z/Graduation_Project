# Go2-W MPC 开源现状调研（核查日 2026-11-26）

数据来自 GitHub API / 页面抓取；星数、pushed_at 为当日值（pushed_at 即最近推送，近似最近提交）。Gitee 无法检索，**未核实**。

## 1. 直接面向 Go2-W 的 MPC
| 项目 | 星 | 许可 | 最近推送 | 说明 |
|---|---|---|---|---|
| [meisman-ucb/go2w-roll-control-mpc](https://github.com/meisman-ucb/go2w-roll-control-mpc) | 9 | 无（null） | 2026-09-08 | 即 arXiv 2606.26313（Borrelli 组，AVEC 2026）的配套代码 |
| [RayyanRafikh/wheeled-quadruped-mpc](https://github.com/RayyanRafikh/wheeled-quadruped-mpc) | 0 | 无 | 2026-11-20 | 仅 README+报告，MPC 内容未证实，不可用 |
| [TrackinBIT/Wheel_legged-Robot](https://github.com/TrackinBIT/Wheel_legged-Robot) | 31 | 无 | 2025-08-08 | MATLAB Simscape 仿真，复现论文，非 Go2-W |
| [LYHrmer/wheel-legged-control-lab](https://github.com/LYHrmer/wheel-legged-control-lab) | 0 | MIT | 2026-11-20 | 16 自由度轮足，VMC+LQR+MPC+残差 PPO，仅仿真（平台是否 Go2-W 未核实） |

要点：
- 搜 "go2w mpc"、"go2-w mpc"、"b2w mpc" 在 GitHub 无直接结果；Henry Kou 的 MPPI Wheeled Quadruped（Go2W，MuJoCo）只有项目页，**未找到仓库**。
- **2606.26313 代码**：这是规划层，不是全身控制。mpc.py 基于动态单轨（bicycle）模型，输出 [a_x, M_psi, M_theta]（纵向加速度、横摆/俯仰力矩，用于主动侧倾），IPOPT 求解（README 间接推断），仅含离线赛车线生成 + 闭环仿真（simulate.py）。16 个关节由论文里的全身 RL 策略驱动，**该 RL 策略与实机接口不在仓库内**。结论：不能直接上 Go2-W 实机，也不是腿部 MPC，无许可证，复用有法律风险。
- 另有 [kosuke-satake/go2-w_ws](https://github.com/kosuke-satake/go2-w_ws)（0 星，无许可，2026-07）仅为 Go2-W ROS2/RL 学习工作区，无 MPC。

## 2. Go2（无轮）成熟 MPC 栈
| 项目 | 星 | 许可 | 最近推送 | 实机 / 状态估计 |
|---|---|---|---|---|
| [qiayuanl/legged_control](https://github.com/qiayuanl/legged_control)（OCS2 NMPC+WBC） | 1857 | BSD-3 | 2025-02-13（已归档） | A1 实机；线性卡尔曼估计，用关节+IMU 估计基座位置速度；官方无 Go2 |
| [WeixianLin-cc/leggedcontrol_go2](https://github.com/WeixianLin-cc/leggedcontrol_go2) | 39 | BSD-3 | 2024-05-08 | 声称仿真+实机 Go2（未核实验证） |
| [bb0928/Go2_legged_control](https://github.com/bb0928/Go2_legged_control) | 4 | BSD-3 | 2025-07-15 | Go2 版 legged_control，实机情况未核实 |
| [leggedrobotics/ocs2](https://github.com/leggedrobotics/ocs2) | 1545 | BSD-3 | 2026-09-29 | 示例含 legged_robot、ballbot、mobile_manipulator；**无轮足示例** |
| [LeCAR-Lab/dial-mpc](https://github.com/LeCAR-Lab/dial-mpc)（ICRA 2025） | 1018 | Apache-2.0 | 2025-05-28 | 有 Go2 实机部署（unitree_sdk2_python）；采样式 MPC，需外部定位提供基座位置速度（ROS2 里程计 ≥50 Hz 或 Vicon）；README 无轮式 |
| [robomechanics/quad-sdk](https://github.com/robomechanics/quad-sdk) | 975 | MIT | 2025-11-25 | 原生 Spirit/Go1 类，非 Go2 原生（第三方栈集成见 darshmenon/quadruped-robotics-stack，35 星） |
| [go2-convex-mpc](https://github.com/elijah-waichong-chan/go2-convex-mpc)（CasADi+OSQP） | 138 | MIT | 2026-04-17 | 仅 MuJoCo，实机"准备中" |
| [unitreerobotics/unitree_guide](https://github.com/unitreerobotics/unitree_guide) | 644 | BSD-3 | 2024-07-22 | 官方示例，主要面向 A1/Go1，无 Go2 实机 MPC 证据 |
| [Khaledsweid1/ocs2-perceptive-mpc-go2](https://github.com/Khaledsweid1/ocs2-perceptive-mpc-go2) | 2 | Apache-2.0 | 2026-07-22 | OCS2 感知 MPC，Go2 + unitree_mujoco，仅仿真 |

Cheetah-Software 移植：GitHub 检索无 Go2 结果，**未核实**。

加轮要改什么（对 legged_control / OCS2 类栈）：
1. 模型：URDF 补 4 个轮关节，足端接触点改为轮心加滚动半径；动力学 12→16 自由度。
2. 接触：约束从"零速度站立"改为"无滑动滚动"（非完整约束，速度沿轮向），步态模式增加纯滚动。
3. 代价：加轮速/前进速度跟踪；OCS2 需改 ocs2_legged_robot 的 constraint、reference manager、状态输入维度（工作量大）。
4. 硬件接口：Go2-W 轮电机经 unitree_sdk2 低层指令控制（可行性未核实）；状态估计需融合轮速里程计，足式卡尔曼的"支撑足静止"假设对轮子不成立。

## 3. 轮足 MPC 先例
- **ETH 轮式 ANYmal**：Bjelonic 等的 [Whole-Body MPC and Online Gait Sequence Generation for Wheeled-Legged Robots](https://arxiv.org/abs/2010.06322)，基于 OCS2，**未找到该论文专用开源代码**（OCS2 主仓库无轮足示例）。
- **IIT**：[ADVRHumanoids/horizon](https://github.com/ADVRHumanoids/horizon)（86 星，许可 NOASSERTION，推送 2026-11-23），基于 CasADi 的轨迹优化框架，Centauro/Kyon 用此建模。
- **[AndrePatri/AugMPC](https://github.com/AndrePatri/AugMPC)**：39 星，GPL-2.0，推送 2026-07-18。MPC 后端是 Horizon（README 称 "Horizon-based MPC implementations"），上层 SAC/PPO 选接触序列与速度指令。验证 Centauro（零样本实机），README 称覆盖 30–120 kg 的多种构型，B2W 仅见于演示文件名（未核实），Go2/Go2-W 未提及。移植到 Go2-W 要自己写机器人模型+接口（xbot2/Isaac Sim/硬件）；依赖 ibrido-containers，GPL-2.0 有传染性。
- Diablo/Ascento：未找到开源 MPC，**未核实**。

## 4. 最短路径结论
| 路径 | 工作量粗估 | 风险 |
|---|---|---|
| A 直接可用 | 无 | **不存在**：没有 Go2-W 全身 MPC 开源实现 |
| B 用 2606.26313 代码做规划层 + 自有底层 | 1–2 周（仿真复现），实机另需底层 | 无许可证；只有单轨规划层，需自备 RL/底层控制器；与"腿部 MPC"目标不同 |
| C 改 Go2 栈加轮（legged_control 或 Go2 凸 MPC） | 约 2–4 个月（OCS2 路线）；凸 MPC 改轮约 1–2 个月（仅仿真） | OCS2 学习曲线陡；状态估计需重写；轮约束建模；实机接口未核实 |
| D 改 IIT 栈（AugMPC/Horizon） | 约 2–3 个月 | GPL、依赖重、文档少；Horizon 求解速度需验证 |
| E 从零 | 3 个月以上 | 毕设周期风险高 |

**推荐**：毕设稳妥路线为"2606.26313 单轨 MPC 作规划层 + 现成 Go2-W RL 底层策略"（若有）；若必须腿部 MPC，选 go2-convex-mpc（MIT，已含 Go2 模型）在 MuJoCo 中加轮，先仿真后实机。
