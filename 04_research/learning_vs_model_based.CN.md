# 学习控制 vs 传统控制：答辩证据整理

日期：2026-11-25。性质：文献与代码只读调研，**未安装或运行任何东西**。用于回应评审的三个质疑：(a) MPC/WBC 已成熟，为何用学习；(b) 黑盒如何保证稳定安全；(c) 对齐不就是系统辨识，辨识后用 MPC 不行吗。
约定：**事实**＝论文或仓库原文及数字；**【评价】**＝本文判断；查不到写"未核实"。

## 0. 阅读范围与证据等级

| 等级 | 含义 | 涉及文献 |
|---|---|---|
| A | 下载 PDF 用 pdftotext 读全文，数字逐条核对 | Hwangbo 2019、Lee 2020、Miki 2022、Bjelonic 2020/2021、ASAP |
| B | arXiv HTML 经网页抽取，只覆盖前约 100k 字符 | Lee 2024（131k 字符，末尾约 31k 未读）、Ha 等综述（222k 字符，已读到约 200k）、SPI-Active（数字为抽取结果，未对 PDF 复核） |
| C | 仅读摘要页或检索摘要 | DTC、CaT、Yang 2022、CBF-RL、Tosun 2023、2501.16590、各开源仓库 README |

- Hwangbo、Lee 2020 的 PDF 正文含补充材料（fig. S1/S2 等）；两栏版面使表格被打乱，Lee 2020 的 Table 1 数值抽不出来，只引文字结论。
- 检索工具返回过若干 arXiv 号形如 26xx 的条目，**本文一律不引用**，以免引到不可核的条目。
- 仓库查询用 GitHub API 与 raw README，日期为 2026-11-25 当天。

## 1. 学习 vs 模型方法的直接比较

### 1.1 逐篇证据

| 论文与出处 | 平台 | 对比对象与条件 | 指标与关键数字 | 结论 |
|---|---|---|---|---|
| **Hwangbo 等 2019**，Sci. Robot. 4(26) eaau5872，DOI 10.1126/scirobotics.aau5872，arXiv 1901.08652（A） | ANYmal（12 个串联弹性执行器） | 对比"ANYmal 上现有最好的运动控制器"（模型方法，引用 Bellicoso 等 RAL 2018 在线非线性运动优化，参考文献 [12]）；同一硬件、同一飞行小跑步态、同一指令序列 | 线速度误差 0.143 vs 0.231 m/s（模型方法高约 95%）；偏航率误差 0.174 vs 0.278 rad/s（高约 60%）；平均力矩 8.23 vs 11.7 Nm；平均机械功率 78.1 vs 97.3 W（补充材料 fig. S1/S2 与 Results 正文）。最高速度 1.2 m/s，比此前纪录高 25%；推理 <25 µs，"prior controllers often require two orders of magnitude more onboard computation" | 学习策略在跟踪精度、能耗、速度上占优；对手是同组自研控制器 |
| **Lee 等 2020**，Sci. Robot. 5(47) eabc5986，DOI 10.1126/scirobotics.abc5986，arXiv 2010.11251（A） | ANYmal | 对比基线 [1, 26]（Jenelten 2019 滑移地面、Bellicoso 2018 两篇的模型方法，ANYmal 原有控制器）。森林、苔藓、泥地、植被；台阶与 10 kg 负载（占机重 22.7%，训练未见）；湿白板打滑 | 基线最高 0.6 m/s；台阶成功率各 10 次（Fig. 3E）；基线载重后"incapable of traversing any steps under any command speed"；基线侧向航向误差达 30°，指令 0.6 m/s 时失败；湿白板上"quickly loses balance... and falls"。Table 1 证明学习方法速度更高、COT 更低（数值未能抽取）。DARPA SubT 4 次 60 分钟任务 0 次失败 | 在非结构化地形、载荷失配、打滑下学习方法占优；作者承认 Table 1 只统计基线成功行走时的数据，低估了差距 |
| **Miki 等 2022**，Sci. Robot. 7(62) eabk2822，DOI 10.1126/scirobotics.abk2822，arXiv 2201.08117（A） | ANYmal | 基线 [4] 是 Lee 2020 的**纯本体学习控制器**，不是模型方法 | 台阶成功率、障碍赛、转向 3 vs 0.6 rad/s | **不能当作"学习 vs 模型方法"的证据**。只证明外感知提升学习控制器。答辩被问到时应主动说明 |
| **Lee 等 2024**，Sci. Robot. 9(89) adi9641，DOI 10.1126/scirobotics.adi9641，arXiv 2405.01792（B） | 带驱动轮的 ANYmal 类轮足机器人（抽取文本未点名机型，只写"比腿式 ANYmal 重约 12 kg"；动作 16 维：12 腿位置 + 4 轮速度；轮电机为准直驱，无精确力矩测量） | (1) 与同组此前 MPC 控制器 [10]：只有定性一句"lacks robustness and cannot operate in the environments depicted in Fig. 6"，**无数字**；(2) 与传统采样式导航规划器（Wellhausen）在同一底层控制器上比较，10 次重复；(3) 与 ANYmal 纯腿式数据比较 | 平均速度 1.68 m/s、机械 COT 0.16，"三倍速度、COT 低 53%"（对象是腿式 ANYmal，**不是轮足 MPC**）；规划耗时 0.34 ms vs 基线有时超 1 s；跟踪误差 0.24 vs 0.45 m/s（Fig. 7E）。峰值速度 6.3 m/s | 与轮足 MPC 的对比只有定性描述；数字对比对象是腿式机器人和导航规划器。作者列出的自身失败：记忆容量耗尽后困住（Fig. 7D-i）、感知视野仅前方约 3 m、定位丢失需人工恢复 |
| **Bjelonic 等 2021**（模型方法一侧），IROS 2021 pp. 8388–8395，DOI 10.1109/IROS51168.2021.9636371，arXiv 2010.06322（A） | ANYmal 轮足 | 全身 MPC（单刚体动力学 + 运动学，轮视为滚动点接触）对比自己的分解式任务方法 | 质心预测误差 0.061±0.044 m vs 0.214±0.061 m（约 71%，Fig. 4）；在线步态序列使运输成本最多降 85%（摘要）。同组 RAL 2020（arXiv 1909.07193）：2 m/s 混合小跑机械 COT 0.2；比传统小跑低 42%、比被动轮滑行低 9%（Sec. V） | 模型方法在平地、模型假设成立时能自动发现混合步态并节能。局限：依赖单刚体假设（"joint accelerations' momentum is negligible"）；含离散决策的整体优化"currently impractical to run online"；作者把加入外感知地形信息列为"future work"（盲步态生成） |
| **Jenelten 等 2024 DTC**，Sci. Robot. 9(86) eadh5401，DOI 10.1126/scirobotics.adh5401，arXiv 2309.15462（C，仅摘要） | ANYmal | 学习 + 轨迹优化混合：优化器给落脚点，神经网络策略跟踪 | 摘要：稀疏地形（缝隙、踏石）落脚精度更好，纯数据驱动方法在此"tend to fail"；在湿滑、可变形地面比模型方法更稳 | 模型方法的价值在稀疏落脚点和直观调参；作者自己选了混合路线 |
| **Ha 等综述**，Int. J. Robot. Res. 2025，DOI 10.1177/02783649241312698，arXiv 2406.01152（B） | 四足为主，含 Sec. 8.5 轮足 | 综述 | Sec. 1.3：模型方法"solving a high-dimensional non-convex optimization problem in real-time is computationally expensive"、"dealing with uncertainties, especially in contact interaction is difficult"、难以直接融合视觉；Sec. 6 引言：模型方法"can explicitly take constraints into account which makes them suitable for safety-critical cases" | 综述对两类方法的评价是互补，没有"一方全面占优"的结论 |
| **Akki 与 Chen 2025**，arXiv 2501.16590（C） | Go1，**仅 MuJoCo 仿真**，匀速直走 | MPC vs RL | 摘要页：RL 抗扰与能效好但地形泛化差；MPC 大扰动恢复更好、关节出力更均匀。检索摘要却写 RL 恢复更快 | 两处说法互相矛盾，且为非正式发表的仿真工作。**只作弱旁证，引用前须读全文** |

### 1.2 模型方法占优或学习方法失败的场景（公平呈现）

1. **稀疏落脚点**（缝隙、踏石）：DTC 摘要称纯学习方法在这类地形上因奖励稀疏而失败。
2. **显式约束与可调参**：Ha 等综述 Sec. 6 与 DTC 摘要都把"约束可显式写入、代价函数直观"列为模型方法优势。
3. **轮足平地混合步态**：Bjelonic 2020/2021 的 MPC 在平地以 2 m/s 混合小跑 COT 0.2，并能自动在驱动、静态步态、小跑间切换。我们**没有找到**同平台上与学习方法的定量对比，因此不能断言学习方法在这一场景更好。
4. **学习方法自身的失败**：Lee 2024 的卡死与视野限制；Ha 等综述 Sec. 8 称 DRL 在踏石、受限空间等安全关键场景"struggle"。
5. **对手偏旧且为自研**：Hwangbo 2019 与 Lee 2020 的基线都是 ETH 同组 2018–2019 年的控制器，比较条件由学习方法作者设定。**【评价】**评审可质疑基线调参是否充分；同期更强的 MPC 与 WBC（含 Bjelonic 2021）未与学习方法做同条件对比。

### 1.3 缺口（如实告知评审）

- 在检索范围内**没有找到**"同一轮足平台上，学习策略与 MPC/WBC 的受控定量对比"的发表工作。Lee 2024 是最接近的，但对比只有定性一句。
- 这既是风险（无现成数字可引），也是机会：本课题在 Go2-W 上做"学习 vs 传统基线"的同条件实验，本身就是一个可写入论文的贡献点，但前提是基线做得公平（见 §4）。

## 2. 学习控制的公认短板与常见回应

| 短板 | 事实依据 | 常见回应（出处） | 对本课题的含义 |
|---|---|---|---|
| **稳定性与安全，无形式化保证** | Ha 等综述 Sec. 3.1.2：安全对腿式机器人"becomes a more important issue"（欠驱动、无可靠复位）；Sec. 8.4：安全滤波（HJ 可达性、CBF、预测式）在运动控制中"limited"。**我们没有找到对已部署高维神经网络策略的形式化稳定性证明** | ① 训练时把约束并入：CaT 把约束违反变为概率终止，只改动 PPO 一小处（arXiv 2403.18765；STATUS 记录为 IROS 2024）（C）。② 学习策略 + 恢复策略切换：Yang 等（arXiv 2203.02638），摘要称仿真跌倒平均减少约 48.6%，真机 115 分钟少于 5 次跌倒（C）。③ CBF 并入训练：CBF-RL，ICRA 2026 录用，称部署时无需运行时滤波器，平台 G1（C，arXiv 2510.14959）。④ 运行时 QP 安全滤波：Tosun 与 Samur（arXiv 2303.02386），文中指出可用于学习控制器的测试部署（C） | 不应声称"保证安全"。可声称"经验鲁棒 + 工程层保护"：关节与轮速限幅、变化率限制、急停、回退出厂模式。这些是工程措施，不是证明 |
| **可解释性差** | 综述抽取文本未讨论该点（B，未覆盖则不下结论） | Miki 2022 提供可检视的内部置信状态：用学习到的置信解码器重建地形，并在感知失效时可视化（正文 "Internal belief state inspection" 图，A）。Lee 2020 用特权信息教师—学生蒸馏（A） | 可解释性确实弱于 MPC 的代价函数与约束。可回应的是"行为可通过奖励项与消融分解"，不要声称策略本身可解释 |
| **数据与仿真依赖** | 综述 Sec. 5：纯仿真训练的策略"can take advantage of some aspects of the simulation that are not present in reality"；Sec. 5.1：bang-bang 策略"sim-to-real is doomed to fail"；Sec. 5.2：执行器动力学是主要建模误差来源 | PD 位置动作空间降低差距：Sec. 5.1 称"a low proportional gain for the joint PD controller... greatly reduces sim-to-real gap"（B）。Hwangbo 2019 的执行器网络（A）。域随机化与真机数据对齐（ASAP、SPI-Active） | 本课题的动作空间（12 腿位置 + 4 轮速度，见 `02_learning/platform/go2w.CN.md`）就属于 PD 层，符合综述推荐做法 |
| **训练成本** | Hwangbo：单 PC 单 GPU，每次训练不超过 11 小时（A）。FLORES 轮足：Isaac Gym 4096 环境约 18 小时，单张 A100（B，arXiv 2507.22345，预印本） | - | 服务器条件充足，算力不是主要风险 |
| **真机数据采集的硬件风险** | ASAP Sec. VIII：采集中两台 G1 受损，依赖动捕，全 23 自由度 delta 模型需 400 多条片段，不可行（A） | 只学 4 自由度踝关节 delta | 对 Go2-W 的含义：真机轨迹采集量与动捕/状态估计是主要风险，见 `candidates/asap.md` |

## 3. 针对 (c)：为什么"只做参数辨识"不够

### 3.1 先承认的事实

**辨识是有效的，而且是必要的基线。** SPI-Active（CoRL 2025，PMLR v305，arXiv 2505.14266，B）在 Go2（4.7 kg 负载）上做质量、质心、惯量和执行器增益的采样式辨识，摘要称在多个运动任务上比基线好 42–63%；抽取结果对 Table 1(b) 的复算为前跳 52%、偏航跳 63%、速度跟踪 42%，姿态跟踪仅 27%。不辨识参数、直接上 delta 模型，会被评审抓住。

### 3.2 参数辨识不足的证据

| 证据 | 内容 | 出处 |
|---|---|---|
| 解析执行器模型调参仍失败 | Hwangbo 2019 的"解析模型"使用执行器真实控制代码、辨识参数与 CAD，并手工调延迟、阻尼、摩擦；"Both alternative methods could not make a single step without falling"；"We have tuned the analytical model for more than a week without much success"。执行器网络验证集误差 0.740 Nm，理想执行器模型 3.55 Nm；测试集 0.966 vs 5.74 Nm | Hwangbo 2019，Results 消融与 Methods，Fig. 6（A） |
| 辨识后模型类仍有偏差 | ASAP Table IV（sim-to-sim，IsaacGym → IsaacSim/Genesis）。Hard 级别 Eg-mpjpe：Vanilla 148/175，SysID 165/186，ASAP 129/129（单位见论文）。SysID 比不辨识还差 | ASAP Table IV（A） |
| 辨识的参数空间是预设的 | ASAP 自述 SysID 需要"pre-defined parameter space"，未必覆盖真实差距，且常依赖真值力矩；其 SysID 基线只辨识质心偏移、基座质量比例与 PD 增益（Table VII） | ASAP Sec. I、附录（A） |
| 执行器非线性结构选择影响很大 | SPI-Active Table 2：线性增益模型 1.30/1.54，统一 tanh 0.74/1.17，其方法 0.55/0.76（前跳/偏航跳）。同文：基于可微仿真的梯度辨识 GD 在关节角误差上比 Vanilla 更差（Table 1(a)，1.14），归因于接触不可微 | SPI-Active（B，抽取数字） |
| 轮足特有：无力矩测量、打滑 | Lee 2024：轮电机为准直驱，无精确力矩测量，故用学习式执行器处理腿、轮用速度指令；传统状态估计"often result in high errors in case of wheel slippage or discrete height changes" | Lee 2024 Methods、Intro（B） |
| 域随机化过保守 | ASAP 与 SPI-Active 都指出过度随机化导致保守策略 | ASAP Sec. I；SPI-Active Sec. 1（A/B） |

**【评价】**证据的准确说法是："参数辨识降低差距，但模型结构误差（延迟、执行器非线性、接触）留有残差，需要数据驱动的残差项。"不能说"辨识没用"。ASAP 的真机对比只有 Vanilla 与 ASAP（Table V，如 Kick 的 Eg-mpjpe 61.2 → 50.2，LeBron 159 → 112），**没有真机 SysID 对照**；辨识不足的直接数据来自 sim-to-sim，评审可以指出这一点。

### 3.3 "辨识 + MPC"在轮足上的代表做法与局限

- **代表做法**：Bjelonic 2020（RAL，arXiv 1909.07193）用分解的轮/基座轨迹优化，加分层 WBC 输出力矩，同时满足非完整滚动约束、摩擦锥与力矩限制；Bjelonic 2021 改为单任务全身 MPC，采用单刚体 + 运动学模型，轮视为带滚动约束的点接触。
- **局限（事实）**：
  1. 单刚体假设"joint accelerations' momentum is negligible"，辨识不会改变这一模型结构。
  2. 论文把轮建模为固定关节位置的点接触，目的是控制优化规模（"adding a full model of a wheel increases the MPC's number of states"）。
  3. 预测模型不含执行器延迟与摩擦（【评价】由模型描述推断，论文未直接这样说）；论文用"预测误差"（0.061 m）量化模型与真机的偏差。
  4. Bjelonic 2020 的轮子轨迹优化依赖无侧滑（no-lateral-slip）速度约束；Lee 2024 把打滑下的状态估计列为传统方法的短板。
- **【评价】**对 Go2-W，"辨识 + MPC"是合理的公平基线，但需要自己实现轮足 MPC（见 §4），而不是只辨识参数。**不能写成"MPC 不可行"**，只能写成"成本高、且模型类受限"。

### 3.4 对实验设计的含义

建议至少设 4 组：辨识 only、辨识 + MPC 基线（若能实现）、delta-action only、辨识 + delta-action。这样能直接回答 (c)，且不预设结论。ASAP 管线需要全局基座位姿，Go2-W 无动捕时的可行性见 `candidates/asap.md` 第 65 行。

## 4. 传统基线的开源实现与 Go2-W 出厂控制器

### 4.1 开源 MPC/WBC 代码（核对日期 2026-11-25）

| 项目 | 内容 | 支持 Go2-W 轮子？ | 维护 | 结论 |
|---|---|---|---|---|
| **OCS2**，github.com/leggedrobotics/ocs2，BSD-3 | MPC 工具箱，示例含 legged robot、ballbot、mobile manipulator 等；ROS1 主分支，另有 ros2 分支；最近推送 2026-09-29 | README 示例列表**无轮足** | 活跃 | 可作为开发框架，需自行写轮足模型（Bjelonic 所用模型思路见 §3.3），工作量大 |
| **legged_control**，github.com/qiayuanl/legged_control，BSD-3 | 基于 OCS2 + ros-control 的 NMPC-WBC 栈；README 以 A1 为部署例（ROBOT_TYPE=a1）；自定义机器人需仿 `UnitreeHW` 写硬件接口 | 否，未提及 Go1/Go2/轮 | **已归档**（README 写 "not supported anymore"；最近推送 2025-02-13） | 作为参考实现可读，不宜直接作基线 |
| **Go2_legged_control**，bb0928，4 星 | 检索摘要称"基于 MPC 的 Go2 实现"；README 在 main 分支 404 | 未核实 | 最近推送 2025-07-15 | 仅腿式（若可用），可信度未核实 |
| **unitree_guide**，unitreerobotics，BSD-3 | 宇树官方配套教程代码，ROS Melodic/Ubuntu 18.04 + Gazebo | 否；机型 README 抽取未核实 | 最近推送 2024-07-22 | 教学级，不适合作 Go2-W 基线 |
| **Cheetah-Software**，mit-biomimetics，MIT | MIT Mini Cheetah/Cheetah 3 软件，含 MPC；README 以 Mini Cheetah 为主 | 否 | 最近推送 2023-10-18 | 需移植，且无轮 |
| **quad-sdk**，robomechanics，MIT | ROS 四足全栈，含规划、控制、估计；最近推送 2026-11-25 | 否；支持机型列表未从 README 抽到，未核实 | 活跃 | 同上 |
| **go2w-roll-control-mpc**，meisman-ucb，9 星 | 论文《Racing a Wheeled Quadruped: Active Load Transfer Mitigation via MPC》的补充代码 | 针对 Go2-W，但**只是动态自行车模型上的高层 MPC 仿真**，无硬件接口，无许可证显示 | 2026-09 | 说明有人在 Go2-W 上做 MPC，但不是可用的低层运动基线 |
| **Bjelonic 的轮足 MPC** | 论文 arXiv 2010.06322 | 为 ANYmal 轮足 | - | **本次检索未找到公开代码**（未做穷尽查找） |

结论：**没有找到现成的、支持 Go2-W 轮子的开源 MPC/WBC 实现。** 要有"传统控制基线"，只能：(i) 自行在 OCS2 或自写 QP 上实现带滚动约束的轮足模型，成本大，毕设 3–4 个月不现实；(ii) 采用更简单的"经典"基线，见 §4.3。

### 4.2 Go2-W 出厂运动控制器作基线

**事实**（unitree_sdk2 `example/go2w`，unitree_sdk2_python `example/go2w`，仓库 API 核对）：

- 官方有 Go2-W 专用示例：C++ 的 `go2w_sport_client.cpp`、`go2w_stand_example.cpp`，Python 有 `high_level` 与 `low_level`。
- 高层接口 `SportClient` 提供 `Move(vx, vy, vyaw)`、`StopMove`、`SpeedLevel`、`SwitchGait`（示例中注释）、`BalanceStand`、`RecoveryStand` 等；`Move` 一次调用移动 1 s，持续调用才持续运动，1 s 内无请求自动停下。状态话题 `rt/lf/sportmodestate`。
- 低层示例对腿设位置目标和 kp、kd，对轮设 kp=0 并发送 dq 目标。
- 低层控制前须用手机 App（或 MotionSwitcher）关闭内置 sport_mode，以免指令冲突（unitree_sdk2_python README）。本仓库 `02_learning/platform/interfaces.CN.md` 第 31 行记录：真机关闭内置运动服务后 SportModeState 不可读。
- `unitree_mujoco` 的 `unitree_robots` 目录含 `go2w`。`robot_lab` 与 `rl_sar` 均列有 Go2W 的 RL 流程。
- 出厂控制器的算法**未公开**，不能写成"出厂是 MPC"。

**可行性与限制【评价】**：
1. **可行**：在出厂模式下，用 `Move` 发相同的速度指令序列，同时订阅 `rt/lowstate`（关节与轮的 q、dq、估计力矩、IMU）和 `sportmodestate`（其速度与位置估计）记录数据；再切到低层模式运行学习策略，用同一指令序列和同一场地做对比。
2. **限制**：(a) 两种控制器不能同时运行，只能分时对比；(b) 出厂控制器是黑盒，只能作"厂商产品基线"，不能说明"传统控制理论方法"；(c) 出厂 `sportmodestate` 的估计量在低层模式下消失，需统一用外部量（动捕或雷达里程计）作真值；(d) `Move` 的速度上限、轮式驱动模式切换方式（`SwitchGait` 取值含义）文档未核对，**需现场确认**；(e) 本次未接触实机，以上均为代码层判断。

### 4.3 建议的基线组合【评价】

| 基线 | 性质 | 工作量 | 可回答 |
|---|---|---|---|
| 出厂 `Move` | 黑盒产品基线 | 小（SDK 示例已有） | 学习策略与厂商控制器在同指令下的差别 |
| 固定站姿 + 轮速 PD（含车体速度与偏航 PI） | 经典控制基线，平地驱动模式 | 小到中 | "简单传统控制够不够"；是评审常见反问 |
| 辨识后仿真中的 MPC | 模型基线 | 大，可能做不完 | 仅在时间允许时做，否则如实说明 |

## 5. 答辩"三问三答"草稿

**问 1：MPC/WBC 已经很成熟，为什么要用学习？**

答：我不认为学习方法全面优于 MPC，成熟的模型方法在约束明确、模型准确的场景很强。比如 Bjelonic 等的轮足全身 MPC 在平地以 2 m/s 混合小跑，机械 COT 为 0.2，并能在线生成步态，这一点我们不否认。但在同一台 ANYmal 上，Hwangbo 等 2019 报告学习策略的速度跟踪误差为 0.143 m/s，对比当时最好的模型控制器的 0.231 m/s，平均功率 78.1 W 对 97.3 W，推理不到 25 微秒。Lee 等 2020 在泥地、植被、10 公斤负载和湿滑白板上发现模型基线会失败，而学习控制器在 4 次 60 分钟的比赛中零失败。需要说明的是，这些基线都是同组 2018–2019 年的自研控制器，并非今天最强的 MPC。同时，我没有找到轮足平台上学习与 MPC 的定量同条件对比，所以我们在 Go2-W 上设置传统基线，只对我们的实验条件下的结论负责。

**问 2：黑盒策略怎么保证稳定和安全？**

答：目前没有对高维神经网络策略的形式化稳定性证明，我不会声称"保证"。Ha 等 2025 的综述也指出，安全滤波在运动控制中应用有限，是开放问题。现有的做法分三层：训练时把约束写进学习，如 CaT 把约束违反变成概率终止；运行时加恢复策略，Yang 等的方法在真机 115 分钟内少于 5 次跌倒；以及用 CBF 做训练内或运行时的安全滤波，如 CBF-RL 与 Tosun 等的滤波器。本课题采用关节位置加轮速这一层 PD 接口，这正是综述推荐的降低 sim-to-real 差距的做法，再叠加限幅、变化率约束、急停和回退到出厂模式。这些是工程保护，不是数学证明，实验中的安全性以统计数据（跌倒次数、违反约束次数）报告。

**问 3：你的对齐不就是系统辨识吗？辨识好参数再用 MPC 不行吗？**

答：对齐里确实包含系统辨识，我们先做参数辨识，这是必要基线：SPI-Active 在 Go2 上通过辨识质量、质心和执行器增益，比基线好 42–63%。但参数辨识只能在预设模型类里调参。Hwangbo 等手工调了一周多的解析执行器模型，训练出的策略一步都走不了，而执行器网络的力矩误差为 0.740 Nm，理想模型为 3.55 Nm。ASAP 的 sim-to-sim 实验里，最难一档辨识参数的位置误差 165 反而高于不辨识的 148，delta-action 为 129。至于"辨识 + MPC"，它是合理的做法，Bjelonic 等已在 ANYmal 轮足上实现；但单刚体模型假设关节动量可忽略，辨识改变不了这个结构，打滑和执行器延迟也不在预测模型里。因此我们的实验设辨识、辨识 + MPC（若时间允许）、delta-action、辨识 + delta-action 四组对照，由数据判断残差项是否有额外收益；ASAP 的真机验证没有 SysID 对照，这一点我们如实说明。

## 6. 未核实与需要继续做的事

1. Lee 2024 的对比细节：补充材料中的与 MPC 的比较，本次未读；Table 1（Lee 2020）数值待从 PDF 图像核对。
2. SPI-Active、DTC、CaT、Yang 2022、CBF-RL 的数字与结论为摘要或抽取结果，写论文前须读全文并核对表号。
3. 2501.16590 的结论互相矛盾，需读全文再决定是否引用。
4. Go2-W 的 `SwitchGait` 取值、`Move` 速度上限、驱动模式切换：需现场或官方文档确认。
5. 轮足 MPC 的公开代码、Go2_legged_control 的实际可用性、quad-sdk 与 unitree_guide 的支持机型：本次只做了 README 级检查。
6. 出厂控制器与 MPC 的关系：宇树未公开，不得在答辩中断言。
