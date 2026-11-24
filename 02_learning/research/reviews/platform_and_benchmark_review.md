# 平台、扰动基准与补充候选审查

> 阶段记录（2026-11-22）：以下论文、分类和建议反映当时已查到的资料，不是最终候选或后续检索边界。可随新文献和核验结果替换、修正。

核查日期：2026-11-21。本文记录公开论文、作者网页与源码的静态证据；未安装依赖、未运行训练或控制硬件。

## 1. Go2-W 的现成工程链与研究方法必须分开

`robot_lab` 提供 Go2-W 训练环境；`rl_sar` 提供对应策略推理和部署配置。这解决平台搭建的一部分，但不能直接证明任何新适应算法已在 Go2-W 复现。

已核版本：

- [robot_lab](https://github.com/fan-ziqi/robot_lab/tree/26acb225aad129e222da7a34ba11f39e29b73e39)，提交 `26acb225aad129e222da7a34ba11f39e29b73e39`。
- [rl_sar](https://github.com/fan-ziqi/rl_sar/tree/376d42c9b128f963ab08579762d5a216a976ce39)，提交 `376d42c9b128f963ab08579762d5a216a976ce39`。

### 1.1 动作不是同一种关节目标

[Go2-W 环境配置](https://github.com/fan-ziqi/robot_lab/blob/26acb225aad129e222da7a34ba11f39e29b73e39/source/robot_lab/robot_lab/tasks/manager_based/locomotion/velocity/config/wheeled/unitree_go2w/rough_env_cfg.py)明确分为：

| 槽位组 | 关节 | 输出语义 |
|---|---|---|
| 前 12 项 | FR、FL、RR、RL，每腿 hip / thigh / calf | 相对默认姿态的关节位置目标 |
| 后 4 项 | FR、FL、RR、RL 的 wheel / foot joint | 轮子角速度目标 |

代码使用腿部 `JointPositionActionCfg` 与轮部 `JointVelocityActionCfg`，髋部动作缩放 0.125，其余腿关节 0.25，轮速度缩放 5.0。以上是**该公开配置值**，不是制造商全部能力或本项目安全执行限值。

对应 [rl_sar 配置](https://github.com/fan-ziqi/rl_sar/blob/376d42c9b128f963ab08579762d5a216a976ce39/policy/go2w/robot_lab/config.yaml)给出 16 个自由度、轮索引 12–15、57 维观察和 `policy.pt`。观察包含角速度、重力方向、目标速度、关节位置/速度及上次动作。部署合同要同时匹配排列、单位、缩放、默认姿态和控制周期。

### 1.2 部署时不能照搬仿真真值

该 Go2-W actor 配置主动移除了 `base_lin_vel` 和地形高度扫描。说明可采用不直接输入车体线速度的部署策略。但把其他方法迁入时，如果方法仍要求真实车体速度或故障标签，必须实现估计器或修改训练合同，不能因为平台底座已有就忽略这项需求。

当前 `robot_lab/main` 对应 Isaac Lab 3.0.0；其版本表另列 `v2.3.2` 对应 Isaac Lab 2.3.2。既有环境使用 2.3.2 时，应审查固定版本，不应直接把本次 main 的路径与命令视为可无缝运行。

## 2. 新轮足论文：实验相关不等于已有完整复现发布

### 2.1 MUJICA

[论文](https://arxiv.org/abs/2605.13058)与[作者项目页](https://hyzenthlayer.github.io/mujica/)描述 Go2-W 上的移动、攀爬及跌倒恢复，采用本体感觉和技能选择器，对轮腿协同、电机约束与恢复任务有直接参考价值。

本次直接读取项目 HTML，真实链接包括论文、视频；还残留另一项目 `extreme-parkour` 的模板链接。未核实到 MUJICA 自身的作者训练仓库。因此，不能把页面中的其他 GitHub 地址当作 MUJICA 官方实现。该结论是发布材料审查，不是对论文质量的否定。

### 2.2 Learning to Recover / Robust Fall Recovery

[作者项目页](https://boyuandeng.github.io/L2R-WheelLegCoordination/)展示 Go2-W 的轮腿协同跌倒恢复、课程训练与动态奖励。页面可点击的主要材料为论文与视频；`Code` 字样在本次 HTML 中未对应实际代码链接。应作为轮足恢复任务与评价协议的参考，目前不能按“已核实完整作者训练发布”列入主底座。

### 2.3 TWiRL

RSS 2023 的 [Learning and Adapting Agile Locomotion Skills by Transferring Experience](https://www.roboticsproceedings.org/rss19/p051.html)研究借用旧控制器的经验训练新技能。其[作者主页](https://sites.google.com/berkeley.edu/twirl)仍显示代码将发布。它是经验迁移的重要相关工作，当前公开证据不足以当作快速完整复现基座。

## 3. QWM：现代跨四足世界模型，但本次发现关键公开依赖缺口

[Toward Hardware-Agnostic Quadrupedal World Models via Morphology Conditioning](https://arxiv.org/abs/2604.08780)通过已知结构描述条件化世界模型；[作者仓库](https://github.com/modanesh/QWM)给出训练脚本与模型代码。它明确研究四足家族内的形态泛化，不应写成已支持机械臂或运行中未知损伤。

静态核对提交 `d65f26776cb6aebd776656687bd7e407751392fd`：

- 仓库约 24 个树条目，存在 `qwm.py`、`envs/hq_isaac.py`、`configs.yaml` 等。
- 配置动作数固定为 12，环境要求注册任务 `Isaac-Velocity-Flat-HeteroQuadruped-v0`。
- README 明确要求专用 `modanesh/IsaacLab-HQ`，声称标准 Isaac Lab 没有此异构环境。本次公开 GitHub API 请求该依赖返回 404，无法验证其公开可获取性；不能据此判断作者是否内部存在该环境。
- 配置引用 `assets/usds`；仓库根 README 描述这些资产，但当前树没有相应完整资产发布。

因此，QWM 是值得阅读的跨本体方法，但本次不能认证为从公开材料即可重建全部环境的主复现项目。普通四足的 12 维关节动作也不覆盖 Go2-W 的 4 个轮速度或 UR7e 的机械臂任务。

## 4. 扰动 Benchmark 的使用原则

[Robust-Gymnasium，ICLR 2025](https://proceedings.iclr.cc/paper_files/paper/2025/hash/fcc22e5b7d5d2155d994da22d045f0a6-Abstract-Conference.html)及[官方代码](https://github.com/SAIL-Research-Lab/Robust-Gymnasium)提供状态、动作、奖励和环境扰动接口。它适合统一评估协议，**不是一个已解决恢复的策略算法**。

官方覆盖表中，MuJoCo locomotion 提供 dynamics 扰动；Robosuite 机械臂表主要列 state / action / reward。不能从“支持机械臂”推导出“所有机械臂任务已提供运行中电机失效和动力学切换”。具体实验要逐任务读扰动实现。

应分开报告：

1. **观测损坏**：传感器丢失、偏置、噪声。
2. **指令扰动**：网络输出被噪声或偏置修改。
3. **执行器变化**：真实力矩权限、响应时间、摩擦、控制增益改变。
4. **外部与接触变化**：外推力、载荷、地面接触参数。

这四类不物理等价；特别是“动作乘零”是否模拟断电，要看动作下面是否还有保持姿态的 PD 控制器。

## 5. 对研究计划的实际含义

较可行的工程分工是：用已公开的 Go2-W 平台环境与 SDK 解决观测、混合动作和部署；用经审查的适应算法解决研究问题；对 UR7e 单独建立同一算法所需的观测与动作合同。两个平台可分别训练，不需要先实现一套跨任意自由度的通用权重。

如果采用需要底层力矩的算法，必须先确认两个平台可用的力矩接口及重力补偿约定；如果采用位置/速度动作，则应把受扰系统定义为包括底层控制器在内的闭环系统，并在该层完成训练和评估。
