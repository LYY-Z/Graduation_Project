# 复现参考项目与选型依据

## 1. 参考项目如何支撑工作计划

复现需要环境、统一接口、历史策略、序列训练和设备部署五类组件。现有项目各覆盖其中一部分，尚无已核对工程能够直接完成LocoFormer在Go2-W上的多本体训练与部署。因此以Robot Lab为主仿真任务，在同一训练管线内接入历史策略，其余项目按模块参考。

### 1.1 项目介绍与工作计划的对应关系

项目本身及实现程度在第2–4节说明。汇报时先介绍这些已有能力，再按下表解释选用方式。这里将“已经提供的功能”与“本项目准备完成的工作”分开。

| 参考项目 | 已有能力 | 对应工作 | 使用方式 | 验证重点 |
|---|---|---|---|---|
| Robot Lab / Isaac Lab | Go2-W任务、模型、观测、动作和PPO | 阶段1–2 | 保留原配置建立单体基线 | 逐关节检查、保存重载和固定任务评估 |
| MetaMorph / GenLoco | 形态表示、有效位、方向与默认姿态配置 | 阶段3 | 借鉴设计，编写本项目统一槽位与映射 | 单槽位、缺失位及改造前后对比 |
| URMA / Body Transformer | 逐关节编解码与身体结构建模 | 阶段3的后续对照 | 接口路线变化时单独比较 | 匹配身体集合与预算，不混入首版 |
| lucidrains / Baby | TXL核心、Isaac Lab序列训练接入 | 阶段4 | 移植必要模块，补任务边界和更新规则 | 因果、缓存、逐步/分段一致性及历史消融 |
| GenBot-1K | 多本体资产、生成与身体划分 | 阶段5 | 筛选资产，统一任务，补轮足变体 | 逐身体启动、完整身体留出及多种子指标 |
| SDK2 / rl_sar | 消息、通道、模式和部署组织 | 阶段6 | 编写本项目状态转换、动作解码和TXL运行器 | 只读、影子推理与命令/反馈闭环 |

### 1.2 主线与辅助资料

主线项目直接服务阶段交付：Robot Lab建立基线，LocoFormer相关代码提供历史模型参考，GenBot扩展身体，SDK2连接实机。URMA、MetaMorph等提供接口设计依据；其他轮足控制、仿真和训练框架用于局部对照。全部27个仓库保留在第4节逐项说明，汇报中重点讲上述主线。

本地保存的是阅读用源码快照，部分资源已排除，不作为完整运行仓库。以下结论区分源码静态检查、项目README说明和实际运行结果；当前没有本项目训练结果。固定提交链接用于追溯，运行环境按所选版本另行建立。

### 1.3 三类接口参考的采用层级

固定槽位是首版项目设计，参考MetaMorph的模块/形态表示与有效位置处理，以及GenLoco的方向、初态和控制配置；不把两者原架构等同73维平面数组。URMA提供逐关节编码、聚合和共享解码的架构参考。本地locoformer提供按输入类型选编码器、按selector选动作组的示例，主要复用历史核心，不直接照搬为主接口。

工作计划先以Go2与Go2-W候选验证16槽位原型，再在正式身体集合上决定接口覆盖。具体输入数组、输出选择、三种方案与验证顺序见[核心实现第2节](interfaces.CN.md#2-三种统一接口及本项目选择)。

### 1.4 按工作计划区分复现、试验、复用与改造

| 采用层级 | 项目 | 准备开展的工作 | 需要改造或优化 | 是否作为前置条件 |
|---|---|---|---|---|
| 优先复现 | Robot Lab Go2-W平地PPO | 运行原任务，训练并重载评估；再扩展地形 | 先核对模型/配置，不急于改算法 | 是，形成后续对照 |
| 专项复验 | BabyLocoFormer | 在独立环境中小规模检查序列采集与更新，必要时短训练 | 任务重置、缓存清理与实际PPO多轮执行 | 主线需要同类机制验证，不要求复现其全部工程 |
| 模块移植 | lucidrains/locoformer | 参考TXL与mask实现，接入选定主训练管线 | 对齐张量、动作分布与缓存生命周期，筛选额外扩展 | 历史策略的实现来源之一 |
| 设计借鉴 | MetaMorph / GenLoco | 阅读表示、有效位、方向和初始化设计 | 本项目自行定义槽位及轮速语义 | 不安装完整原工程作为依赖 |
| 条件对照 | URMA | 固定槽位难覆盖目标拓扑时，比较逐关节方案 | 接入相同身体、任务、预算和历史模块 | 不阻塞首版 |
| 资产复用 | GenBot-1K | 筛选少量身体，导入并建立同一控制任务 | 轮足变体、映射、惯量/碰撞与执行器检查 | 多本体阶段需要合格资产，不要求全量数据 |
| 协议与部署参考 | SDK2 / rl_sar | 复用消息定义，参考动作/模式配置与部署组织 | 自建观测/动作适配、TXL运行、周期及异常处理 | 实机闭环前完成 |

当前优先的是工程正确性与机制复验，包括接口、缓存、更新和部署。奖励改进、网络结构优化等算法工作在基线与核心机制验收后再独立提出，避免把多个变化合并后无法归因。

Baby专项复验不以作者自述的弱结果为复现目标。若旧依赖或运行成本过高，保留源码审查与最小序列样例验证，在主管线中实现同类机制并报告差异。对URMA等备选项目，也不要求先完整复现全部论文再推进主线。

## 2. LocoFormer已有资源与复现缺口

作者论文与项目页是方法和实验目标依据。已核对公开入口尚未找到完整官方训练仓库、checkpoint、逐机器人槽位映射和全部部署配置。本项目可以实现公开机制，但不能宣称复原了作者所有训练细节。官方论文的CC许可也不自动覆盖第三方代码、模型资产或未公开权重。

主线选择是Robot Lab任务 + 一套RSL-RL/PPO训练 + 统一关节超集 + TXL历史模型；Baby参考集成、lucidrains参考核心、GenBot参考资产、SDK2负责设备通信。其余项目用于局部工程或研究对照。

## 3. 两个LocoFormer相关实现的复用判断

### 3.1 本地lucidrains实现

`StateEmbedder`为不同dim_state建立MLP，state_id由调用方选择；动作selector同样是调用者提供的信息。它解决若干已知输入宽度共享后续网络的程序组织，不等于论文针对未见身体的统一槽位方案。

代码包含TXL、因果与episode-id mask、Actor/Critic、PPO、经验采集、stateful forward与reset_cache等。Microduck示例提供单个双足环境的训练入口，不能据此认定已经有多身体轮足训练成果。默认扩展可能含Beta动作分布、HLGauss Critic和辅助动态模型，复现时应筛选功能，不把所有扩展都视作论文要求。

可复用程度：算法模块参考价值高，作为Go2-W整套工程的直接复用程度低。需审查实际mask标识语义、动作概率维度、采集器与自定义环境API，以及缓存更新后的处理。

### 3.2 BabyLocoFormer的已有工程

生成脚本使用身体长度、宽度、腿长参数网格调用xacro生成四足URDF，另有USD转换、MultiUsdFile资产加载、有限随机化、Isaac Lab任务、自定义rsl_rl和TXL Actor/Critic。它主要扩展四足几何，不能据此认为已覆盖论文所有拓扑、双足和轮足变化。

最值得参考的是环境到序列训练的集成位置：ActorCriticTransformerXL、PPO分支、RolloutStorage和runner。它包含RoPE、Flash Attention、SwiLU等改动；不应将其架构和论文逐项等同。

### 3.3 已发现的实现风险

以下是本地快照的静态审查结果，不是运行测试结论：

| 位置 | 可看到的行为 | 对本项目的影响 |
|---|---|---|
| ActorCriticTransformerXL.reset | 函数为pass，按done清缓存代码被注释 | 可以保留历史，但缺显式任务切换规则；需区分Trial与任务结束 |
| transformerxl_batch_generator | 返回整段rollout，一次yield，没有epoch/minibatch参数 | 配置中的多轮优化/多minibatch不应假定在TXL分支生效 |
| PPO.update的TXL分支 | 直接使用上述生成器 | 需记录实际optimizer.step次数，补序列优化循环 |
| PPO日志计数 | enumerate计数与num_updates统计方式需核查 | 可能影响多个update时日志均值，不能仅看日志判断训练质量 |
| 形态生成 | 长、宽、腿长网格；多USD加载 | 有几何变化，但不是完整多拓扑生成器 |

作者README自述结果较弱、主要供学习，这是性能自述；上述边界和循环问题则是具体可检查的源码证据。它们不足以推出“整个项目完全不能用”，也不能忽略后直接用于论文复现。

改造建议：保持主训练库单一；移植历史模型与必要序列支持；用task_id、重置与有效位小样例验证，再验证PPO epoch和缓存生命周期。

## 4. 全部参考项目详解

### P01｜locoformer

**项目本身：** 第三方LocoFormer灵感实现。

**已有内容：** PyTorch的TXL、Actor/Critic、PPO、多输入编码器与动作selector，还有Microduck示例。

**可以参考和复用：** 阅读缓存、掩码、概率和更新核心；不能直接替代Go2-W环境。

**不能直接覆盖的工作：** 有算法模块，未获得作者完整身体生成、统一槽位和实机工程。

**审查依据：** 本地阅读快照；关键模块检查见第3节，其他模块未逐项运行验证。

**来源与版本：** [仓库](https://github.com/lucidrains/locoformer)；[固定提交](https://github.com/lucidrains/locoformer/tree/79ce9d72d1137015e0212284f06656c83bb414e7)。

### P02｜metamorph

**项目本身：** ICLR2022形态条件化通用控制。

**已有内容：** Transformer共享控制、模块化身体环境、PPO预训练和Unimal-100基准。

**可以参考和复用：** 身体结构条件、padding/mask、输出有效关节筛选。

**不能直接覆盖的工作：** 不是轮足或跨Trial实现；旧依赖和历史MuJoCo许可说明不能直接照装。

**审查依据：** 本地阅读快照；关键模块检查见第3节，其他模块未逐项运行验证。

**来源与版本：** [仓库](https://github.com/agrimgupta92/metamorph)；[固定提交](https://github.com/agrimgupta92/metamorph/tree/d49826475d4d22d8e63df694785833dc127c4e8d)。

### P03｜BabyLocoFormer

**项目本身：** 非官方Isaac Lab学习实现。

**已有内容：** 生成四足、有限随机化、改造TXL、自定义rsl_rl训练与评估。

**可以参考和复用：** 优先参考从环境到历史模型的集成；需在主训练管线内审查移植。

**不能直接覆盖的工作：** 形态范围和随机化有限，作者自述结果较弱；reset和优化轮次需独立审查。

**审查依据：** 本地阅读快照；关键模块检查见第3节，其他模块未逐项运行验证。

**来源与版本：** [仓库](https://github.com/linden713/BabyLocoFormer)；[固定提交](https://github.com/linden713/BabyLocoFormer/tree/f2dadf8eb13826f449387ecc9970593a9af141bc)。

### P04｜embodiment-scaling-laws

**项目本身：** CoRL2025具身数量规模研究与GenBot-1K。

**已有内容：** 约千种身体、生成/转换、RL专家、数据采集、URMA学生蒸馏及部分权重。

**可以参考和复用：** 选少量资产和生成/划分方法，继续采用LocoFormer在线PPO。

**不能直接覆盖的工作：** 共享蒸馏策略不是TXL跨Trial策略；下载资产不等于完成控制适配。

**审查依据：** 本地阅读快照；关键模块检查见第3节，其他模块未逐项运行验证。

**来源与版本：** [仓库](https://github.com/BoAi01/embodiment-scaling-laws)；[固定提交](https://github.com/BoAi01/embodiment-scaling-laws/tree/62e43ce01b07487f83a108122de66e56c428549e)。

### P05｜one_policy_to_run_them_all

**项目本身：** CoRL2024 URMA多本体运动控制。

**已有内容：** MuJoCo/RL-X、机器人环境、共享形态表示、训练与测试、新机器人接入说明。

**可以参考和复用：** 关节描述、共享编解码、初始化/增益/随机化配置清单。

**不能直接覆盖的工作：** 方法和仿真后端不同；作为表示对照，不替换整套主训练栈。

**审查依据：** 本地阅读快照；关键模块检查见第3节，其他模块未逐项运行验证。

**来源与版本：** [仓库](https://github.com/nico-bohlinger/one_policy_to_run_them_all)；[固定提交](https://github.com/nico-bohlinger/one_policy_to_run_them_all/tree/7c1819444028c529b0a964fe3f32878333b1310a)。

### P06｜GenLoco

**项目本身：** 程序化四足形态训练与参考动作模仿。

**已有内容：** 形态随机化、不同四足环境、策略权重、仿真/实机接入说明。

**可以参考和复用：** MOTOR_NAMES、JOINT_DIRECTIONS、初态、PD和动作范围的配置方式。

**不能直接覆盖的工作：** 主要12关节四足及参考步态，缺4轮独立动作和TXL任务组。

**审查依据：** 本地阅读快照；关键模块检查见第3节，其他模块未逐项运行验证。

**来源与版本：** [仓库](https://github.com/HybridRobotics/GenLoco)；[固定提交](https://github.com/HybridRobotics/GenLoco/tree/98b2dd77bb53ac32f04a15806ff4c6d0e7a1b70e)。

### P07｜BodyTransformer

**项目本身：** 利用身体拓扑学习策略的结构架构。

**已有内容：** 模仿学习、强化学习与Unitree A1 sim-to-real子项目。

**可以参考和复用：** 按身体连接组织特征和注意力、关节输出映射。

**不能直接覆盖的工作：** 结构注意力不是LocoFormer的时间历史；需区分关节轴和时间轴。

**审查依据：** 本地阅读快照；关键模块检查见第3节，其他模块未逐项运行验证。

**来源与版本：** [仓库](https://github.com/carlosferrazza/BodyTransformer)；[固定提交](https://github.com/carlosferrazza/BodyTransformer/tree/008d8cd514322252b53f4d5e3dd5c2fc47c7b9cd)。

### P08｜modular-rl

**项目本身：** ICML2020共享模块化策略。

**已有内容：** 不同agent形态、共享模块/消息传递与MuJoCo训练。

**可以参考和复用：** 每肢体共享计算和身体接入组织。

**不能直接覆盖的工作：** Python3.6/PyTorch1.1等旧栈，只做结构参考。

**审查范围：** 本次读取固定提交的README；未在服务器运行，尚未完成全部内部模块审计。

**来源与版本：** [仓库](https://github.com/huangwl18/modular-rl)；[固定提交](https://github.com/huangwl18/modular-rl/tree/1e617d099198f9a2c1b49fb96255080c708522ca)。

### P09｜AnyMorph

**项目本身：** ICML2022通过推断形态实现策略迁移。

**已有内容：** 基于modular-rl的Transformer与形态泛化实验、Docker和实验管理。

**可以参考和复用：** 可变输入输出与形态推断的设计对照。

**不能直接覆盖的工作：** 不是Go2-W控制与TXL实现；旧容器/许可依赖不纳入主环境。

**审查范围：** 本次读取固定提交的README；未在服务器运行，尚未完成全部内部模块审计。

**来源与版本：** [仓库](https://github.com/montrealrobotics/AnyMorph)；[固定提交](https://github.com/montrealrobotics/AnyMorph/tree/b1e8457c9dc619cda5a2d544383c4fb036d2f184)。

### P10｜legged_gym

**项目本身：** Isaac Gym四足强化学习基线。

**已有内容：** 并行地形、腿式奖励、随机化、PPO接口和部署背景。

**可以参考和复用：** 理解奖励、课程和随机化的来源。

**不能直接覆盖的工作：** Isaac Gym不是Isaac Lab；不在Blackwell主环境混装旧栈。

**审查范围：** 本次读取固定提交的README；未在服务器运行，尚未完成全部内部模块审计。

**来源与版本：** [仓库](https://github.com/leggedrobotics/legged_gym)；[固定提交](https://github.com/leggedrobotics/legged_gym/tree/8fa29acc6fd1910c3d9659eef6310bdd301cde0a)。

### P11｜LocoWheeledLegged

**项目本身：** Isaac Lab轮足训练与Go2-W部署。

**已有内容：** 轮足奖励、动作低通、状态估计/训练稳定性、实机配置。

**可以参考和复用：** Go2-W动作类型、训练与部署映射、滤波状态。

**不能直接覆盖的工作：** README版本表述与命令存在不一致需核对；无LocoFormer跨Trial共享训练。

**审查范围：** 本次读取固定提交的README；未在服务器运行，尚未完成全部内部模块审计。

**来源与版本：** [仓库](https://github.com/zhaozijie2022/LocoWheeledLegged)；[固定提交](https://github.com/zhaozijie2022/LocoWheeledLegged/tree/015b8230b1a21331ab6d2b054a2ef8f1e435db84)。

### P12｜walk-these-ways

**项目本身：** Go1行为多样性与泛化控制。

**已有内容：** Isaac Gym训练、历史/适应组件、实机部署和日志工具。

**可以参考和复用：** 指令、历史输入和部署记录组织。

**不能直接覆盖的工作：** 主要Go1四足；历史适应结构不等同TXL跨Trial。

**审查范围：** 本次读取固定提交的README；未在服务器运行，尚未完成全部内部模块审计。

**来源与版本：** [仓库](https://github.com/Improbable-AI/walk-these-ways)；[固定提交](https://github.com/Improbable-AI/walk-these-ways/tree/0e7236bdc81ce855cbe3d70345a7899452bdeb1c)。

### P13｜RoboGauge

**项目本身：** MuJoCo自动化运动策略评估。

**已有内容：** 地形/摩擦评测、稳定性与速度/目标跟踪、异步评估服务。

**可以参考和复用：** 评估场景设计、压力测试和统一指标。

**不能直接覆盖的工作：** 核对README支持对象为Go2，不能视为已支持Go2-W及TXL隐状态。

**审查范围：** 本次读取固定提交的README；未在服务器运行，尚未完成全部内部模块审计。

**来源与版本：** [仓库](https://github.com/wty-yy/RoboGauge)；[固定提交](https://github.com/wty-yy/RoboGauge/tree/add2c7ee0185ea8fd93d242f86e1c8cac6e9913b)。

### P14｜go2_rl_lab

**项目本身：** Go2高速运动训练与sim-to-real。

**已有内容：** 较新的Isaac Lab3/IsaacSim6.2/Newton MJWarp路线及评估部署。

**可以参考和复用：** 训练日志、观测处理和迁移经验。

**不能直接覆盖的工作：** 普通Go2与新主栈不同；不直接替代2.3.2轮足主路线。

**审查范围：** 本次读取固定提交的README；未在服务器运行，尚未完成全部内部模块审计。

**来源与版本：** [仓库](https://github.com/wty-yy/go2_rl_lab)；[固定提交](https://github.com/wty-yy/go2_rl_lab/tree/6c95d9feef4814c25eb6536e61bb38e1d1d718d4)。

### P15｜DreamWaQ_Go2W

**项目本身：** Isaac Gym版Go2-W地形适应运动学习。

**已有内容：** 速度估计、非对称Actor/Critic、轮足奖励和部署接口。

**可以参考和复用：** 真机配置中的关节顺序转换、状态估计及轮足奖励。

**不能直接覆盖的工作：** Python3.8/Isaac Gym旧栈，不能直接并入拟用Lab2.3.2环境。

**审查范围：** 本次读取固定提交的README；未在服务器运行，尚未完成全部内部模块审计。

**来源与版本：** [仓库](https://github.com/ShengqianChen/DreamWaQ_Go2W)；[固定提交](https://github.com/ShengqianChen/DreamWaQ_Go2W/tree/b64f7b90856fc71595870cb283ce29dd0f4d6f0f)。

### P16｜IsaacLab

**项目本身：** Isaac Sim上的机器人学习框架。

**已有内容：** 环境、资产、传感器、执行器、RL包装器和多GPU接口。

**可以参考和复用：** 主环境与任务接口；使用锁定2.3.2版本。

**不能直接覆盖的工作：** 提供平台，不提供完整LocoFormer策略和Go2-W论文配置。

**审查范围：** 本次读取固定提交的README；未在服务器运行，尚未完成全部内部模块审计。

**来源与版本：** [仓库](https://github.com/isaac-sim/IsaacLab)；[固定提交](https://github.com/isaac-sim/IsaacLab/tree/37ddf626871758333d6ed89cf64ad702aef127d0)。

### P17｜unitree_mujoco

**项目本身：** 官方MuJoCo模型与SDK交互仿真。

**已有内容：** 包含Go2-W等模型、仿真程序和消息交互。

**可以参考和复用：** 可选模型核对与sim-to-sim。

**不能直接覆盖的工作：** 物理参数、接触、执行器与Isaac不自动等价。

**审查范围：** 本次读取固定提交的README；未在服务器运行，尚未完成全部内部模块审计。

**来源与版本：** [仓库](https://github.com/unitreerobotics/unitree_mujoco)；[固定提交](https://github.com/unitreerobotics/unitree_mujoco/tree/1eb6642e3f3fdfb7fb13a9794fd6a2dd93ea0e7d)。

### P18｜unitree_ros2

**项目本身：** Unitree ROS2与SDK2桥接生态。

**已有内容：** DDS/ROS2配置和机器人消息示例。

**可以参考和复用：** 现有ROS2系统需要桥接时参考。

**不能直接覆盖的工作：** 首版SDK2直连不强制添加ROS2层，以免扩大依赖。

**审查范围：** 本次读取固定提交的README；未在服务器运行，尚未完成全部内部模块审计。

**来源与版本：** [仓库](https://github.com/unitreerobotics/unitree_ros2)；[固定提交](https://github.com/unitreerobotics/unitree_ros2/tree/668d1ec5a05d1c38d3306bdca7d59f2ba3581a88)。

### P19｜unitree_sdk2

**项目本身：** Unitree官方C++通信SDK。

**已有内容：** DDS状态/服务和控制消息接口。

**可以参考和复用：** 低层消息、模式和生产部署接口。

**不能直接覆盖的工作：** 不训练策略，不统一关节语义，不自动处理限幅。

**审查范围：** 本次读取固定提交的README；未在服务器运行，尚未完成全部内部模块审计。

**来源与版本：** [仓库](https://github.com/unitreerobotics/unitree_sdk2)；[固定提交](https://github.com/unitreerobotics/unitree_sdk2/tree/8e1b927586712edd6a4c29d50dd52dff1e163439)。

### P20｜unitree_ros

**项目本身：** 官方ROS机器人描述与模型。

**已有内容：** Go2-W URDF/mesh、链接、轴、惯量与限位。

**可以参考和复用：** 结构核查与仿真资产来源。

**不能直接覆盖的工作：** URDF不是电机传动剖面，也不是硬件软限制。

**审查范围：** 本次读取固定提交的README；未在服务器运行，尚未完成全部内部模块审计。

**来源与版本：** [仓库](https://github.com/unitreerobotics/unitree_ros)；[固定提交](https://github.com/unitreerobotics/unitree_ros/tree/41dec58c7a3ccb3050243ef16ac2ca74b2b0f9ca)。

### P21｜unitree_sdk2_python

**项目本身：** 官方SDK的Python接口。

**已有内容：** CycloneDDS、状态/命令、Go2-W编号和控制例子。

**可以参考和复用：** 首版只读、影子推理及混合动作适配。

**不能直接覆盖的工作：** 示例会产生动作，不能当只读程序直接运行；不含LocoFormer推理。

**审查范围：** 本次读取固定提交的README；未在服务器运行，尚未完成全部内部模块审计。

**来源与版本：** [仓库](https://github.com/unitreerobotics/unitree_sdk2_python)；[固定提交](https://github.com/unitreerobotics/unitree_sdk2_python/tree/814556d15970dd2ecf1c9984e845ca02ab07e206)。

### P22｜unitree_rl_lab

**项目本身：** 厂商机器人强化学习及部署。

**已有内容：** Isaac Lab任务、训练、sim-to-sim和真机配置。

**可以参考和复用：** 观测/动作缩放、PD和厂商部署规范。

**不能直接覆盖的工作：** 普通Go2示例不能自动变成16路Go2-W，需查具体任务。

**审查范围：** 本次读取固定提交的README；未在服务器运行，尚未完成全部内部模块审计。

**来源与版本：** [仓库](https://github.com/unitreerobotics/unitree_rl_lab)；[固定提交](https://github.com/unitreerobotics/unitree_rl_lab/tree/4960b84732b0c2ec593dccbfe963fda1bcd7b1e3)。

### P23｜robot_lab

**项目本身：** Isaac Lab多机器人任务扩展。

**已有内容：** Go2-W资产、flat/rough任务、混合动作、奖励与RSL-RL配置。

**可以参考和复用：** 首选Go2-W基线和任务底座。

**不能直接覆盖的工作：** 没有完整LocoFormer外层任务组与作者统一空间。

**审查范围：** 本次读取固定提交的README；未在服务器运行，尚未完成全部内部模块审计。

**来源与版本：** [仓库](https://github.com/fan-ziqi/robot_lab)；[固定提交](https://github.com/fan-ziqi/robot_lab/tree/09f6a9dfdf48f32f38bb851dfa3a7d44db32b270)。

### P24｜rsl_rl

**项目本身：** 机器人强化学习训练库。

**已有内容：** PPO、Actor/Critic、rollout storage、runner等。

**可以参考和复用：** 保留一套可追溯主PPO管线，再接历史策略。

**不能直接覆盖的工作：** 不同版本Tensor/TensorDict接口和自定义fork不能假定兼容。

**审查范围：** 本次读取固定提交的README；未在服务器运行，尚未完成全部内部模块审计。

**来源与版本：** [仓库](https://github.com/leggedrobotics/rsl_rl)；[固定提交](https://github.com/leggedrobotics/rsl_rl/tree/11563319134f987f70fb034410496fe3cc7327a9)。

### P25｜transformer-xl

**项目本身：** 原始Transformer-XL长上下文建模。

**已有内容：** 段间递归、相对位置与stop-gradient设计。

**可以参考和复用：** 复核原始记忆语义和段缓存。

**不能直接覆盖的工作：** 原项目主要语言建模，不含机器人动作、PPO与接管。

**审查范围：** 本次读取固定提交的README；未在服务器运行，尚未完成全部内部模块审计。

**来源与版本：** [仓库](https://github.com/kimiyoung/transformer-xl)；[固定提交](https://github.com/kimiyoung/transformer-xl/tree/44781ed21dbaec88b280f74d9ae2877f52b492a5)。

### P26｜unitree_rl_mjlab

**项目本身：** 厂商基于mjlab/MuJoCo的学习与部署。

**已有内容：** MuJoCo/MJWarp训练、速度跟踪和动作模仿任务。

**可以参考和复用：** 模型映射和新后端部署设计。

**不能直接覆盖的工作：** README列出的平台不等于已支持Go2-W；后端不同，保留备选。

**审查范围：** 本次读取固定提交的README；未在服务器运行，尚未完成全部内部模块审计。

**来源与版本：** [仓库](https://github.com/unitreerobotics/unitree_rl_mjlab)；[固定提交](https://github.com/unitreerobotics/unitree_rl_mjlab/tree/1425b15f73bd4095f0df53709d7c389c3eb9e790)。

### P27｜rl_sar

**项目本身：** 跨仿真与实机的策略部署框架。

**已有内容：** Gazebo/MuJoCo、推理后端、多个机器人和Go2-W支持表。

**可以参考和复用：** RobotLab-Go2W配置、joint顺序、动作与模式管理。

**不能直接覆盖的工作：** README的MLP支持不保证TXL缓存导出可用；Python维护状态与版本要核对。

**审查范围：** 本次读取固定提交的README；未在服务器运行，尚未完成全部内部模块审计。

**来源与版本：** [仓库](https://github.com/fan-ziqi/rl_sar)；[固定提交](https://github.com/fan-ziqi/rl_sar/tree/376d42c9b128f963ab08579762d5a216a976ce39)。

## 5. 重要的兼容性和资源判断

Robot Lab与Isaac Lab的v2.3.2已核对为匹配路线。GenBot、Baby、RL-X、旧Isaac Gym项目和新Isaac Lab3项目不共享一套依赖。尤其不能依次pip安装不同项目的rsl_rl，然后认为实际导入的就是期望版本；应记录`module.__file__`及包版本。

GenBot公开README说明完整蒸馏数据可达约4TB，专家权重和URMA学生另有下载。这不是本项目必须获取的数据量。当前优先少量资产在线PPO，不复制全量蒸馏数据。

LocoWheeledLegged快照的README文字版本与安装命令存在不一致，应核对实际依赖，而不是照抄。RoboGauge的支持对象主要Go2；rl_sar声明支持RobotLab-Go2W，但TXL状态化推理仍需新增接口；unitree_rl_mjlab支持名单不能等同已支持轮足。

## 6. 选型结论与开发分工

| 工作 | 优先采用 | 辅助参考 | 需要自己完成 |
|---|---|---|---|
| 单体任务 | Robot Lab v2.3.2 | Unitree RL Lab、Go2-W专项项目 | 资产/动作核对、基线和测量 |
| PPO训练 | 一套主RSL-RL派生实现 | Baby、lucidrains | 序列、任务边界、epoch和cache |
| 统一输入 | 论文关节超集 | MetaMorph、GenLoco | 槽位、方向、有效位、归一化 |
| 架构对照 | URMA逐关节方案 | BoT、AnyMorph、modular-rl | 可变拓扑实验，明确方法偏离 |
| 身体生成 | GenBot选取/生成 | Baby四足几何生成 | 轮足扩展、资产筛选与留出 |
| 实机通信 | SDK2 Python首版 | rl_sar、专项部署 | TXL状态与混合动作适配 |
| 评测 | 项目统一评估脚本 | RoboGauge场景设计 | Go2-W与跨Trial指标协议 |

对未选为主线的项目，保留来源和设计要点，不在服务器全部安装。引用项目的思想、代码、资产和权重时分别检查许可并保留修改记录。
