# 策略适应、残差RL、元RL与跨形态控制：文献及开源实质审计

> 阶段记录（2026-11-22）：以下论文、分类和建议反映当时已查到的资料，不是最终候选或后续检索边界。可随新文献和核验结果替换、修正。

核查日期：2026-11-21。目标：同一算法框架分别训练 Unitree Go2-W 与 UR7e；关注运行中突发扰动后的恢复，而非仅测试回合开始时换参数。只检查公开论文、作者/机构页面、GitHub API树和源文件；未安装依赖、下载权重/大资产、训练或运行机器人。以下“可复现”指代码证据，不代表本机已跑通。

## 核心判断

1. **最直接的经典证据是 GrBAL/ReBAL (ICLR2019)**：原文明确在 rollout 中切换失效关节、Ant由正常变为瘸腿；作者仓库还含7自由度机械臂的力/质量/阻尼/失效环境。代价是MuJoCo131与旧TensorFlow，不能把“论文相关”直接写成“本科最容易复现”。
2. **RMA² (CVPR2024)值得作为机械臂适应机制参考，但当前开源有实质断点**：作者认证无疑，基座训练/适配训练/评估入口齐全，却README称依赖两个固定子模块而`.gitmodules`空、树无对应gitlink；无公开基座权重。并非下载即跑。
3. **OSCAR (ICRA2022)发布最实在之一**：训练、预训练、评估、微调脚本和成套checkpoint都存在。但它在动力学/操作空间控制内部补偿，最终依赖关节力矩；对UR7e的实际控制接口要先验证，不可只因Panda也是机械臂就迁移。
4. **CaDM (ICML2020)是干净的历史上下文适应比较对象**，既有model-based也有PPO+context代码；默认损伤参数仅在reset变化，不能宣称已验证运行中突然失效。
5. **ReSkill (CoRL2022)公开训练、演示生成、skill与残差权重**，适合研究“冻结先验+残差”的可训练完整链条；却有4万演示/skill先验训练负担，且主要是任务组合/任务变化，不是突发动力学失效。
6. **MetaMorph/ModuMorph不要作为本任务第一主线**：已知形态描述与未知故障不是同一个问题；同算法、不同权重已经满足双平台目标，不必额外背负一套权重跨Go2-W与UR7e的难题。

以上排序是针对本课题的工程推断，不是论文作者声称已在Go2-W/UR7e完成的结果。未发现本次深审任一代码原生同时支持这两台平台。

## 广筛清单（超过12篇）

|工作/发表核验|主要适应对象|作者发布证据|对本题取舍|
|---|---|---|---|
|RMA，RSS2021|地形/载荷/电机强度的隐变量|[作者项目](https://ashish-kmr.github.io/rma-legged-robots/)，[论文](https://arxiv.org/abs/2107.04034)|关键思想，不能把第三方RMA重现当原作者完整代码|
|A-RMA，IROS2022|修正适配器估计误差|[作者项目](https://ashish-kmr.github.io/a-rma/)，[论文](https://arxiv.org/abs/2205.15299)|训练后再用非理想adapter微调基座很实用，但项目页本身不是训练仓库|
|HORA，CoRL2022（PMLR2023）|手内物体属性|[正式发表](https://proceedings.mlr.press/v205/qi23a.html)，[作者代码](https://github.com/HaozhiQi/Hora)|强开源RMA模板，但Allegro手并非UR机械臂|
|RMA²，CVPR2024|物体属性、视觉、外力|[CVF](https://openaccess.thecvf.com/content/CVPR2024/html/Liang_Rapid_Motor_Adaptation_for_Robotic_Manipulator_Arms_CVPR_2024_paper.html)，[作者代码](https://github.com/yichao-liang/rma4rma)|机械臂最相关之一；依赖缺口见下|
|GrBAL/ReBAL，ICLR2019|在线动力学模型适应、突发关节失效|[正式版PDF](https://people.eecs.berkeley.edu/~ronf/PAPERS/anagabandi-iclr19.pdf)，[作者代码](https://github.com/iclavera/learning_to_adapt)|突发恢复必读经典；旧栈不宜盲选为第一复现|
|CaDM，ICML2020|从历史推断动力学context|[PMLR](https://proceedings.mlr.press/v119/lee20g.html)，[作者代码](https://github.com/younggyoseo/CaDM)|统一算法跨任务容易解释；原公开基准非mid-episode|
|Residual RL for Robot Control，ICRA2019|传统反馈控制器残差|[作者项目](https://residualrl.github.io/)，[论文](https://arxiv.org/abs/1812.03201)|经典机械臂真机证据；作者项目未提供训练代码链接|
|Residual Policy Learning，2018预印本|脚本/MPC控制器修正|[作者项目](https://k-r-allen.github.io/residual-policy-learning/)，[作者代码](https://github.com/k-r-allen/residual-policy-learning)|完整老代码有价值，勿与Johannink论文混为同一代码或擅自标ICRA|
|OSCAR，ICRA2022|结构化动力学残差与操作空间控制|[作者项目](https://cremebrule.github.io/oscar-web/)，[机构代码](https://github.com/NVlabs/oscar)|发布完整，力矩接口/动力学模型假设重要|
|ReSkill，CoRL2022|冻结skill先验+动作残差|[作者项目](https://krishanrana.github.io/reskill/)，[官方代码](https://github.com/krishanrana/reskill)|本科可借其残差链条，不建议先做skill全家桶|
|AdaptSim，CoRL2023|根据目标试验调sim参数后再训策略|[PMLR](https://proceedings.mlr.press/v229/ren23b.html)，[项目](https://irom-lab.github.io/AdaptSim/)|适应需多次试验与仿真重训，非一次运行内快速恢复|
|RARL，ICML2017|对抗外力下鲁棒策略|[PMLR](https://proceedings.mlr.press/v70/pinto17a.html)，[作者代码](https://github.com/lerrel/rllab-adv)|鲁棒RL基线，只有鲁棒训练不等于在线识别/适应|
|MetaMorph，ICLR2022|已知模块形态通用控制|[作者项目](https://metamorph-iclr.github.io/site/)，[官方代码](https://github.com/agrimgupta92/metamorph)|非本任务必需；同名视觉语言项目很多，注意URL|
|ModuMorph，ICML2023|形态context调制控制器|[PMLR](https://proceedings.mlr.press/v202/xiong23a.html)，[作者代码](https://github.com/MasterXiong/ModuMorph)|跨体强参考，但不是未知故障恢复|
|Recovery RL，ICRA2021|学到安全区及恢复策略|[作者项目](https://sites.google.com/berkeley.edu/recovery-rl/)，[作者代码](https://github.com/abalakrishna123/recovery-rl)|可做后续安全扩展；主要碰撞风险，不等于电机故障适应|
|MESA，2021预印本（本轮未认证主会）|离线元学习安全critic，在新动力学适应|[论文](https://arxiv.org/abs/2112.03575)，[作者项目](https://sites.google.com/view/safe-meta-rl/home)|适应风险模型，需目标环境小数据；不能直接当免数据故障恢复基线|
|Reflexive World Models，NeurIPS2025主会|奖励无关latent快速纠偏|[正式proceedings](https://proceedings.neurips.cc/paper_files/paper/2025/hash/c8afe13ccbadd3f0f8b0fb690a77e1d6-Abstract-Conference.html)，[论文](https://arxiv.org/abs/2505.15589)|相关新工作，但论文checklist说未发完整代码，仅补充核心Python实现；不满足完整训练/环境复现门槛|
|Residual Control for Fast Recovery from Dynamics Shifts，2026预印本|冻结nominal+有界残差/SAG|[论文](https://arxiv.org/abs/2603.07775)|题目极贴合；未认证同行评议与完整作者训练仓库，不能仅凭摘要推荐|

本表不重复主任务已审的Policy Decorator、DSRL、DPPO、AMAGO；它们可以加入最终总表，但不可把“通用RL”自动等价于“已测物理故障恢复”。

## 深审1：GrBAL/ReBAL

### 论文实验证据

[正式ICLR2019 PDF](https://people.eecs.berkeley.edu/~ronf/PAPERS/anagabandi-iclr19.pdf)第7–9页明确区分OOD disabled joint与回合中失效；HalfCheetah在rollout中更换disabled关节，Ant由正常进入crippled腿。GrBAL用最近转移更新元学习动力学先验，ReBAL更新循环隐状态，再由MPC选动作；不是在机器人上持续PPO重训整网。

### 代码可追溯性

作者仓库HEAD `bd7d99ba402521c96631e7d09714128f549db0f1`。具备：

- [run_grbal.py](https://github.com/iclavera/learning_to_adapt/blob/master/run_scripts/run_grbal.py)、[run_rebal.py](https://github.com/iclavera/learning_to_adapt/blob/master/run_scripts/run_rebal.py)、非适应MB baseline。
- [meta_mlp_dynamics.py](https://github.com/iclavera/learning_to_adapt/blob/master/learning_to_adapt/dynamics/meta_mlp_dynamics.py)、rnn dynamics、MPC controller。
- [arm_7dof_env.py](https://github.com/iclavera/learning_to_adapt/blob/master/learning_to_adapt/envs/arm_7dof_env.py)在`reset_task`支持cripple、damping、mass、force；动作是底层仿真control而非统一末端增量。观测是q/qdot与目标误差，不输入失效关节标签。
- [half_cheetah_env.py](https://github.com/iclavera/learning_to_adapt/blob/master/learning_to_adapt/envs/half_cheetah_env.py)通过`cripple_mask*action`模拟失效，mask不包含在`get_current_obs`。
- [rollout工具](https://github.com/iclavera/learning_to_adapt/blob/master/learning_to_adapt/samplers/utils.py)在每步取近期observations/actions/next_obs，先`switch_to_pre_adapt()`再adapt；这是推理时在线更新证据。

### 限制

README指定MuJoCo131，Python3/TensorFlow；无公开预训练checkpoint树、无顶层LICENSE。`sim_policy.py`使用本地训练产物`params.pkl/params.json`。公开rollout工具本身没有论文失效时刻调度器，默认环境在reset_task换故障。因此：**论文确实测mid-episode，发布库有适应核心/环境，但重现该测试还需补调度与指标**，不能说原脚本一条命令复现全部故障曲线。

对UR7e若只开放位置/速度接口，需要重新学习该外层动作到状态的动力学；Go2-W有轮足接触高维模型和实时规划负担。适合作经典比较或机制借鉴，不是最低风险第一实现。

## 深审2：RMA²

### 作者与开源真实性

[作者主页](https://yichao-liang.github.io/)CVPR2024条目直接链接到rma4rma，排除了仅凭用户名猜官方。核查HEAD `2f938f6518709ac8cbda05c294b7765c6d16630d`。

### 真正的I/O与扰动

[config.py:296](https://github.com/yichao-liang/rma4rma/blob/main/src/rma4rma/config.py#L296)固定`control_mode="pd_ee_delta_pose"`，输出末端增量经PD执行；不是关节力矩。默认机器人Panda，选项只有panda/xarm7/xmate3_robotiq，没有UR7e或Go2-W。

[pick_single.py](https://github.com/yichao-liang/rma4rma/blob/main/src/rma4rma/tasks/pick_single.py)把50×39的proprio-action历史放进obs，priv_info含物体参数和disturb_force。外力不是只reset抽样：每步0.1概率重采样、逐步衰减，仅在物体被抓住时对物体质心施力。故可引用为持续执行中外力扰动；不能扩写成电机突然衰减/锁死恢复。

[models.py](https://github.com/yichao-liang/rma4rma/blob/main/src/rma4rma/algo/models.py)及[policy.py](https://github.com/yichao-liang/rma4rma/blob/main/src/rma4rma/algo/policy.py)包含privileged encoder与history/depth adapter分支。必须区分oracle的真参数输入与部署adapter；公平比较应禁用`--expert_adapt`等oracle开关。

### 发布断点（比“有GitHub”重要）

[README](https://github.com/yichao-liang/rma4rma/blob/main/README.md)称ManiSkill2与SB3定制fork作为pinned submodules，然而[.gitmodules](https://github.com/yichao-liang/rma4rma/blob/main/.gitmodules)为0字节，Git tree无这两个gitlink。[environment.yml](https://github.com/yichao-liang/rma4rma/blob/main/environment.yml)直接pip安装`./ManiSkill2`、`./stable-baselines3`；干净checkout缺这两个目录。[pyproject.toml](https://github.com/yichao-liang/rma4rma/blob/main/pyproject.toml)也未替代声明所有训练依赖。[CI测试](https://github.com/yichao-liang/rma4rma/blob/main/tests/test_smoke.py)只检查顶层包版本导入，不能证明GPU训练路径可跑。

存在base training、adapter training、eval入口，但adapter依赖自行训练`best_model.zip`，未找到发布weights/license。判定：**论文对题、核心源码在、当前完整依赖闭环失败**。本科可借方法，不应把它排为无障碍原版复现第一名。

## 深审3：CaDM

正式ICML2020论文：[PMLR](https://proceedings.mlr.press/v119/lee20g.html)。历史context由前后向动力学预测训练，再给MPC或PPO使用；无须故障类别标签。作者HEAD `38c11a58d959bfd597f9323e58f28b17f6bf4fd9`。

[README](https://github.com/younggyoseo/CaDM/blob/master/README.md)含Vanilla+CaDM、PETS+CaDM、PPO+CaDM命令；TF1.15、Gym0.16、mujoco-py2.0.2.9和baselines0.1.5。模型自由PPO分支明确需要先训练动力学checkpoint的`--load_path`，不是没有先验训练负担的单阶段PPO。

[cripple环境](https://github.com/younggyoseo/CaDM/blob/master/cadm/envs/half_cheetah_cripple_env.py)的`reset_model()`调用`change_env()`，step仅将action乘mask；当前源码不在step中切换故障。`_get_obs`不返回mask，`get_sim_parameters()`虽然暴露参数，不能因此认定实际策略用了真标签，需追调用处。

[context_rollout_multi](https://github.com/younggyoseo/CaDM/blob/master/cadm/samplers/utils.py)维护滚动state/action历史，并在done清零，推理无需显式故障身份。动作继承各MuJoCo任务的actuator control；换成PD位置外环可保留框架，但必须重训。

当前无顶层LICENSE/权重发布。是“旧栈可训练代码完整、评测还需改”的比较法。优点是上下文窗口、预测损失、是否加历史的消融容易解释；缺点是机械臂与Go2-W环境未给、突发评估未给、在线MPC计算开销明显。

## 深审4：OSCAR

[ICRA2022作者项目](https://cremebrule.github.io/oscar-web/)，[官方NVlabs库](https://github.com/NVlabs/oscar)，HEAD `5a2ede63de9b0ca5f578ce0c3457123ad544d831`。仓库已于2026-08-12归档，README明确deprecated/no updates。许可为NVIDIA研究/非商业source license，不是MIT。

### 可复现材料真实存在

[examples](https://github.com/NVlabs/oscar/tree/main/examples)有train/eval/finetune/pretrain_oscar四个脚本；[trained_models](https://github.com/NVlabs/oscar/tree/main/trained_models)分pretrain、train、finetune，含Trace/Push/Pour、多个控制器、多个seed模型。无需先假定某个未给出的名义策略可用。代码主栈Linux、CUDA、IsaacGym preview3+、旧Python3.7。

### 控制假设

[oscar.yaml](https://github.com/NVlabs/oscar/blob/main/oscar/cfg/train/controller/oscar.yaml)设history_length25，6D位姿增量输入范围，extrinsics latent8维，`use_extrinsics=False`与`use_ground_truth_mm=False`。不能看到模型函数有extrinsics参数就断言部署用真实动力学。

[control_models.py](https://github.com/NVlabs/oscar/blob/main/oscar/models/control_models.py)与[franka.py](https://github.com/NVlabs/oscar/blob/main/oscar/agents/franka.py)使用q/qdot/qddot、低层控制/torque历史、末端Jacobian、学习的动力学模型，生成动力学补偿并输出关节torques。这是“高层动作是EE位姿，底层实现仍需torque”的典型，UR7e如只能servoJ/servoL，不能直接替换。

### 对突发恢复的边界

[finetune.sh](https://github.com/NVlabs/oscar/blob/main/examples/finetune.sh)载入train checkpoint，切换`*_adapt.yaml`后继续训练；这不是证明未重置的一次rollout内故障瞬时恢复。默认适应配置改变质量、阻尼、摩擦等domain。可做动力学残差思想比较，较重，不建议作为轮足+工业臂统一策略第一工程底座。

## 深审5：ReSkill

[CoRL2022作者实现](https://github.com/krishanrana/reskill)，HEAD `d50092f364b155c8a49cd658a647b5fba90af2d3`。README有MIT badge，但本次完整文件树没有独立LICENSE，需区分徽章与实际许可文本。

### 训练与基座可得

[collect_demos.py](https://github.com/krishanrana/reskill/blob/main/reskill/data/collect_demos.py)及[脚本controller目录](https://github.com/krishanrana/reskill/tree/main/reskill/utils/controllers)可自己生成演示，README示例4万轨迹、skill子序列10步。也提供外部预收集数据链接。本次不下载大数据，不保证链接资产仍完整。

[results/saved_skill_models](https://github.com/krishanrana/reskill/tree/main/reskill/results/saved_skill_models)有skill_vae/skill_prior权重；[saved_rl_models](https://github.com/krishanrana/reskill/tree/main/reskill/results/saved_rl_models)有ppo_agent与ppo_residual_agent；训练skill及下游agent入口和评估工具都在。这比仅有演示视频的项目扎实。

[train_reskill_agent.py](https://github.com/krishanrana/reskill/blob/main/reskill/train_reskill_agent.py)的残差obs包含当前状态、skill特征与基座动作，并用logistic schedule调残差权重；策略不是通过外界给定故障标签选择动作。动作继承Fetch manipulation的末端移动/夹爪接口，不是关节torque。

### 适用范围

主要是SlipperyPush、PyramidStack、TableCleanup、ComplexHook这些技能迁移/组合环境。没有就此认证Go2-W locomotion或UR7e突然负载恢复。4万演示、VAE、skill prior、高层PPO、残差PPO及旧MuJoCo2.1环境叠加，对本科首阶段偏复杂。更适合借鉴残差actor初始化、基座动作作为输入、残差幅值schedule等局部机制。

## 深审6：ModuMorph与跨形态边界

[ICML2023正式论文](https://proceedings.mlr.press/v202/xiong23a.html)，[作者代码](https://github.com/MasterXiong/ModuMorph)，HEAD `80e1ba4c2a4f2b302d52613713b60e73c9994dd2`。训练工具`tools/train_ppo.py`、单体训练`train_single_robot.py`、跨体评估`evaluate.py`真实存在；UNIMAL benchmark需外部下载；PyTorch/Docker旧MuJoCo栈。未找到独立LICENSE/发布权重。

关键源码[agent.py](https://github.com/MasterXiong/ModuMorph/blob/main/metamorph/envs/modules/agent.py)的`get_context()`直接读取MuJoCo `body_mass`、形状、摩擦、joint轴/范围、actuator gear、armature、damping，再作为context参与Transformer/超网络。它解决的是**已知形态条件下的控制泛化**；未知电机衰减不能在部署时从sim.model读到。

论文跨形态泛化不意味着部署UR7e与Go2-W时自动理解两种任务。其观测/动作token、关节mask、图拓扑、奖励都需重新设计，且原训练为模块化locomotion为主。若课题准许两机分别训练权重，直接统一“历史encoder+残差actor+故障调度评测协议”更现实。

## 其他值得保留的发布细节

### HORA：比原始RMA更完整的公开适应模板

[官方README](https://github.com/HaozhiQi/Hora/blob/main/README.md)明确要复现原论文数值请用v0.0.1，main已修改reset顺序并转IsaacGym Preview4，因此main数值与论文不一致。提供两阶段训练、两阶段eval、checkpoint下载、109MB稳定初始抓取缓存、部署说明。部署stage2仅用proprio history；teacher stage1用privileged object物理属性。初始稳定抓取不是算法自己从任意状态恢复，不能把“会旋转不同物体”写成全机械臂通用恢复。

### RARL：真正的鲁棒策略基线

[作者rllab-adv](https://github.com/lerrel/rllab-adv)确有adversarial训练代码，README示例InvertedPendulumAdv；仓库自标Under Development，旧rllab/MuJoCo栈。本任务可用现代PPO重新实现同类对抗外力训练作为思想基线，必须标为自己的实现，不能用学生的SB3重现库充当原作者维护库。固定鲁棒策略没有在线隐状态辨识，不应归入已证明的快速自适应。

### Recovery RL / MESA

[Recovery RL作者仓库](https://github.com/abalakrishna123/recovery-rl)有MIT、SAC、risk critic、MPC/visual MPC、环境和全套脚本；安装脚本还会下载离线数据和视觉动力学模型，当前任务未执行。它通过安全critic在task和recovery行为间切换，风险恢复不自动等于任务误差快速消失。

[MESA作者项目](https://sites.google.com/view/safe-meta-rl/home)由论文tinyurl跳转确认。MESA需要新环境少量离线数据先适配critic，再在线任务学习；安全违规成本标签必须定义。若首阶段尚无故障恢复任务跑通，不宜先引入安全critic元训练。

## 对本科基线和后续论文的落地建议（工程推断）

### 最低必要比较，而非最高复杂度算法

先统一两平台的外层连续动作接口，在各自任务训练权重：Go2-W要明确腿关节位置+轮速度，UR7e要明确关节位置/速度或EE增量。不要只在论文中写一个a向量而隐藏接口不同。随后做：

1. nominal PPO；
2. PPO+domain randomization；
3. 同预算PPO+短历史（TCN/GRU，作为隐式适应）；
4. frozen nominal+有界residual PPO/SAC；
5. 如果资源足够，history-conditioned residual，并与无history、无残差幅值约束做消融。

这属于方法组合的可行工程路线，创新性尚需实验判断。不能因为两平台都有效就声称跨形态零样本；“统一算法、分别训练、跨任务故障恢复评测”应准确表述。

### 新论文应补足的证据

- 失效时刻t*随机且隐藏；actor不输入故障类型、severity、发生时间。oracle单独列为上界。
- 区分推力脉冲、持续外力、载荷突变、电机输出衰减、PD增益偏差、通信延迟；锁死关节可能改变可达性，需与可恢复扰动分开报告。
- 每条轨迹先稳定运行，再注入扰动，继续原任务；无reset、不清历史、不人工重启。训练若只reset randomization，明确报告训练-测试非平稳差异。
- 除success/return，报告恢复时间、扰动后积分误差、峰值偏差、动作/残差平滑度、失败比例、非恢复右删失，并给扰动前后轨迹。
- 与DR和history-only等预算比较；未知幅度/未知组合/再次发生扰动分开测试。
- nominal基座须公开训练配方或checkpoint，不能依赖不可取得厂家黑盒权重；如果使用厂家高层运动控制，方法贡献边界要说清。

这些要求直接针对本次审计暴露的普遍缺口：reset-OOD冒充突发适应、oracle参数泄漏、只有微调没有连续恢复、只给训练源码却缺基座或fork依赖。

## 新增正式候选复审：RL2AC (RSS2024)

[正式proceedings](https://www.roboticsproceedings.org/rss20/p060.html)，[完整PDF](https://www.roboticsproceedings.org/rss20/p060.pdf)，DOI 10.15607/RSS.2024.XX.060。作者为Shangke Lyu等，西湖大学MiLAB。已阅读全文核心方法/实验部分，并搜索作者代码；本轮**未找到完整公开作者训练/环境仓库**，PDF也无GitHub或project URL，不能将第三方SATA复现库当RL2AC官方代码。

- 算法：50Hz RL策略输出关节目标a，并新增历史encoder估计名义下一步关节位置qr；1000Hz复合自适应控制器估计Ku，补偿项为Ku_hat(a-qr)，叠加PD。无需与RL同步训练在线补偿器，但qr预测器确实属于新增训练模块，不能说完全包住任意冻结策略即用。
- 真实观测：q、qdot、qr与实际关节torque反馈。论文Eq11明确实际torque由torque sensor测得，用于复合自适应预测误差；不是只要q/qdot即可。没有输入故障类型标签。
- 硬件：Unitree A1；策略50Hz、低层1000Hz，训练IsaacGym/legged_gym、PPO、8000iteration×3000env；不能照搬成UR7e位置伺服调用，必须有可用torque控制及测量。
- 证据：外部腿部力矩、偏心载荷、重载和地形；腿部扰动在stance才启用补偿。没有把论文展示的时间曲线自动归为“随机隐藏时刻电机失效恢复”；其推导假设未知torque可被Ku(a-qr)近似，突发锁死或大滑移不一定符合。
- 对课题：控制+RL结合有启发，但不满足“官方完整训练开源”硬门槛；且对两平台最难统一的是低层接口，优先级低于动作外环残差。

## 新增深审：QOED (RSS2026)，主动试探创新必须查重

[正式proceedings](https://www.roboticsproceedings.org/rss22/p137.html)，[PDF](https://www.roboticsproceedings.org/rss22/p137.pdf)，[作者项目](https://www.youwei-yu.com/qoed/)，[官方代码](https://github.com/youwyu/QOED)。作者主页与项目页均链接仓库。核查HEAD `41025ebed6d17de10b673bbc3f16d3655bc0ebbc`；[LICENSE](https://github.com/youwyu/QOED/blob/main/LICENSE)为MIT。

### 已做过什么（对创新的直接约束）

它将Fisher信息的可辨识方向选择与nuisance方向抑制结合，优化Schur补目标而非简单全参数信息增益；[objectives.py](https://github.com/youwyu/QOED/blob/main/boed/objectives.py)真实实现`Fkk-Fkb@pinv(Fbb+1e-3I)@Fbk`。因此“出现异常后主动采样有信息的动作”“只识别重要物理参数”“通过Fisher选择探测方向”都不能笼统宣称为全新。若后续做主动探测，需明确区别：突发事件的何时探测、任务代价/恢复期限约束、短期非平稳参数、历史遗忘与安全边界，而不只是改信息奖励。

### 代码比搜索摘要更完整，也比名字更有限

[README](https://github.com/youwyu/QOED/blob/main/README.md)提供两个层次：轻量Jackal/Franka quick demo，以及MBPO预训练/finetune。当前raw README路线已勾选RSS实验、优化和更多机器人，网页搜索缓存还显示未勾选；应以此次读取raw源码为准。

- [pyproject](https://github.com/youwyu/QOED/blob/main/pyproject.toml)设torch2.11.0/torchvision0.26.0、mjlab1.6.0 optional，uv覆盖到作者引用的`leggedrobotics/rsl_rl_rwm` git依赖（未固定commit）。这是较现代栈，但可复现时需固定该浮动依赖。
- [train.py](https://github.com/youwyu/QOED/blob/main/mbpo/rsl_rl/train.py)有go1/g1/jackal/leap及rough版本，pretrain与finetune不同环境，finetune以直接MuJoCo作为真实系统proxy；源码不是硬件驱动全家桶。
- [play.py](https://github.com/youwyu/QOED/blob/main/mbpo/rsl_rl/play.py)有checkpoint加载与MuJoCo观测维度检查。[logs目录](https://github.com/youwyu/QOED/tree/main/logs/rsl_rl)真实含7种任务checkpoint目录；已目视目录证实`go1_velocity/2000-01-01_00-00-00_pretrain/model_1000.pt`存在，未下载/执行权重。
- [mbpo_tasks.py](https://github.com/youwyu/QOED/blob/main/mbpo/rsl_rl/mbpo_tasks.py)为通用robot配置与dynamics装配，finetune自动找policy/system_dynamics checkpoint，缺产物会明确报错；定制task需要定义物理参数范围、prior mean/variance、状态索引。可解释物理参数化不是免建模。
- [mujoco_backend.py](https://github.com/youwyu/QOED/blob/main/mbpo/envs/mujoco_backend.py)中Go1动作映射为default joint position+scale×action，即关节位置目标；不能因为MBPO内部学习动力学就误报成torque接口。

### Franka demo的真实粒度

[demos/franka.py](https://github.com/youwyu/QOED/blob/main/demos/franka.py)是6D物体状态、3D加速度命令的cube-slide模型，参数mass/mu/drag，测量为合力在速度方向投影，MPPI规划并优化信息；`SimulatedFrankaInterface`内部直接调用解析cube step。它不加载Franka URDF、不求机械臂IK、不执行7轴关节或位置/力矩控制。因此这是可信、可学习的小型算法demo，**不是原封不动的UR7e运动自适应环境**。

Franka demo中真theta用于产生仿真测量及累计Fisher统计，在线controller用当前dist.mean；不能只因文件出现theta_true就笼统指控actor使用oracle，但迁移时要沿数据流验证。更全面的MBPO模型中privileged dynamics参数用于仿真监督/系统模型，部署估计分支须单独核查。

### 适应与恢复边界

该项目比“只有信息增益论文、无训练代码”强得多，适合后续科研方向参考，也有跨腿/轮/手的同框架证据。但当前未确认随机时刻故障、不中断回合恢复时间测试；finetune明确在线RL/动力学学习，不应与纯冻结历史encoder推理适应混淆。Franka quick demo与真实Franka实验之间仍缺可直接对应的完整硬件控制发布证据；Go2-W轮足与UR7e均需新环境实现与训练。

## RWM全代码复审与缩写混淆

[NeurIPS2025最终PDF](https://proceedings.neurips.cc/paper_files/paper/2025/file/c8afe13ccbadd3f0f8b0fb690a77e1d6-Paper-Conference.pdf)第12页写完整codebase未来发布，第19页checklist对完整开放代码回答No。本轮又以精确论文题目、作者Carlos Stein Brito、Reflexive World Models+GitHub复查，仍未找到可认证完整训练仓库；这应表述为“本轮未找到”，不能从旧PDF推导永远未发布。

实验协议也需要降温：基于TD-MPC2预训练1M steps的encoder、base policy、world model，冻结后训练残差controller；400step一episode，而actuator gain扰动每次ON持续10000–15000step再OFF同样时长。故它是跨多episode持续在线适应，不能用其曲线证明几百毫秒单次执行恢复。p_j∈[-0.5,0.5]为每actuator乘法增益变化，不是质量/地形/传感噪声或形态改变都验证过。

**QOED引用的RWM依赖是leggedrobotics/robotic_world_model，不是Brito的Reflexive World Models。** 两者缩写相同；不能以QOED依赖开源的Robotic World Model仓库来宣布Reflexive World Models已完整开源。

## 最强候选的主张—证据对照

|主张|证据|不能扩大的边界|
|---|---|---|
|GrBAL测过突发失效|ICLR2019正文p7–9 mid-rollout Ant/HC失效|当前发布eval工具缺论文切换调度器；UR7e/Go2-W未测|
|RMA²测过回合中外力|pick_single step中0.1概率更新外力，抓取时对物体施力|不是电机失效；仓库fork依赖断点、无权重|
|OSCAR已给基座产物|trained_models pretrain/train/finetune目录真实存在|仍是Franka模型与torque底层，需要q/qdot/qddot/Jacobian等|
|ReSkill残差可重训且有先验|演示controller、skill/agent训练及weights目录|skills基座需大量演示/预训练；任务迁移不等于故障恢复|
|QOED主动探索已有正式先例|RSS2026+objectives.py Fisher/Schur实现+跨体MBPO train/play|Franka quick demo是解析物体模型；不直接具备UR关节环境|
|RL2AC快速低层适应|RSS2024 p7公式与A1 1000Hz补偿|需torque测量/控制与qr学习；未认证官方完整源码|
|RWM是奖励无关快速纠偏|最终论文冻结base/encoder/model、训练residual controller|扰动ON持续远超400步episode；完整作者train代码未认证|

# 额度恢复后的第二轮实质研究（2026-11-21 12:09 UTC起）

此前额度中断的墙钟时长不计为研究。以下继续补足连续无任务边界适应和代码级接口检查。

## GRAM：新增优先级较高的现代正式候选（RA-L2026，非已认证ICLR2025）

**发表纠正**：[MERL正式条目](https://www.merl.com/publications/TR2026-057)及[作者最终PDF](https://www.merl.com/publications/docs/TR2026-057.pdf)认证为RA-L2026，DOI 10.1109/LRA.2025.3641155。GitHub给出卷11期2页2218–2225。早期匿名OpenReview是ICLR2025投稿版，不能把搜索聚合的“ICLR2025”当录用证据。

[官方代码](https://github.com/merlresearch/gram)，HEAD `ea3f26ce898d7fdae4cc51497b22e8361a1c3f02`；BSD-3-Clause。版本要求IsaacLab **v1.0.0**、rsl_rlv2.0.0、IsaacSim4.1.0.0、Ubuntu22.04（不是猜测的新版本，也不是之前消息中未核实的Lab1.2）。具备`source.train`、`source.eval`、environment、GRAM/robust_rl/contextual_rl/domain_rand及两种消融，所有阶段都可从头训练，无需非公开nominal策略。树中没有发布checkpoint，eval未给load_run会提示评估未训练模型，不能默认为会下载预训练。

### 双平台迁移的真实输入输出

- Go2 12个关节目标，50Hz策略、200Hz PD，Kp25/Kd0.5。历史H=16（约0.32秒），latent8维；这些数字来自最终PDF TableI及实施段落。不是长历史Transformer或在线更新整网。
- [unitree_go2_custom_env.py](https://github.com/merlresearch/gram/blob/main/source/envs/unitree_go2_custom_env.py#L175)动作scale0.25+default offset、hip另有幅值缩放；无轮电机动作。Go2-W需要补4轮速度/力矩通道及接触动力学，不能直接用现有Go2权重。
- [context wrapper](https://github.com/merlresearch/gram/blob/main/source/envs/context_env_wrapper.py)在训练取mass/friction/motor strength/joint bias真参数作为teacher context。**部署并不因此泄漏**：[cli_utils.py:562](https://github.com/merlresearch/gram/blob/main/source/utils/cli_utils.py#L562)明确eval时`act_from_context=False`；[actor](https://github.com/merlresearch/gram/blob/main/source/algs/gram/gram_actor_critic.py#L548)此时只从history encoder取latent。虽然函数仍传context实参，计算分支不使用其编码。
- 训练同时收集ID与adversarial rollout，最后单独训练history/epinet适配器。Epinet uncertainty将latent拉向robust latent；不是突然故障发生后再请求任务标签。
- 机械臂可保留算法类，但必须重定义context（载荷/阻尼/外力/动作滞后）、任务观测（q/qdot/目标误差等）和机械臂reward。论文未做UR/其他机械臂，属于合理方法迁移推断。

### 连续突变证据与代码限制

最终PDF Fig4右图明确展示**执行10秒时加入9kg基座质量**；硬件困难任务包括Slippery与Ramp→Foam，文字明确多数baseline失败发生在trial内动力学改变。因而GRAM比只reset换域的工作更相关。

当前公开[eval runner](https://github.com/merlresearch/gram/blob/main/source/algs/gram/gram_on_policy_runner.py#L635)执行20秒单episode，正常维护观测历史；通用CLI主要静态设置mass/friction/frozen joint，环境事件中friction为startup、motor scale在构造时抽样，**没有找到Fig4随机/指定时刻加质量的专用开箱即用调度入口**。论文有连续突变证据不等于公开eval默认即可生成同一曲线。需要自己添加t*事件、统计恢复指标。

### “Frozen joint”的具体含义不能写错

[envs_utils.py:51](https://github.com/merlresearch/gram/blob/main/source/envs/envs_utils.py#L51)把选中关节action_scale置0，[process_actions](https://github.com/merlresearch/gram/blob/main/source/envs/envs_utils.py#L160)仍加default offset/joint bias，再送PD。这等于**该关节目标固定，PD仍施力保持**，不是无力矩自由摆动，也不是任意当前角度机械锁死。另有`ScaledDCMotor`的motor_fault_indices把effort_scale置0，那才是输出力矩丢失；两者在仓库中是不同通道。

结论：GRAM为本轮新增很值得认真复现的正式现代算法，尤其可从其domain_rand/contextual/robust同库比较开始，再尝试Go2-W和UR7e共享算法。难点是较旧IsaacLab版本迁移、训练阶段数和未给checkpoint；不能承诺原仓库直接支持两台目标平台。

## ESCP：比只做任务切换的元RL更贴近突发动力学（AAAI2022）

[正式论文](https://cdn.aaai.org/ojs/20730/20730-13-24743-1-2-20220628.pdf)，DOI 10.1609/aaai.v36i7.20730；[作者仓库](https://github.com/FanmingL/ESCP)，MIT，HEAD `518f13f8b002d142f670f52d9ef34778e2c2d59f`。论文原文给出该GitHub，官方性明确。

### 方法与真实任务

环境敏感context policy：SAC主干+短期GRU context encoder；窗口示例16；用同环境表征方差最小/不同环境表征分散及历史截断，降低context对过时历史的惯性。论文模拟Hopper/HalfCheetah/Walker2d/Ant/Humanoid及grid，MuJoCo物理参数为dof_damping与gravity，测试每100步切换。虽论文以“机械臂端盘突然加物体”作动机，但没有机械臂真实验证，不能误报为机械臂实验。

### 训练/评估链条与故障标签

- [main.py](https://github.com/FanmingL/ESCP/blob/master/main.py)启动SAC训练，[algorithms/sac.py](https://github.com/FanmingL/ESCP/blob/master/algorithms/sac.py)内置ID/OOD和nonstationary评估agent，训练日志会分别输出Test/OOD/NS指标；不是独立下载模型的demo。
- [nonstationary_env.py:113](https://github.com/FanmingL/ESCP/blob/master/envs/nonstationary_env.py#L113)的step按counter调用set_task改变物理属性，未reset环境状态；因此发布代码也有连续突变机制。
- [Agent.py](https://github.com/FanmingL/ESCP/blob/master/agent/Agent.py)只有`use_true_parameter=True`才把env_param拼接状态；默认ESCP false。task identity/env_param存入replay用于训练表征和上界/UPOSI比较，不能只看replay有label就说部署必须标签。实际policy输入当前状态、前一动作和短时隐状态，无故障类型/切换时刻输入。
- 动作继承各Gym MuJoCo任务的actuator控制；没有显式环境维数绑定在GRU算法。移植到Go2-W leg-position+wheel-velocity或UR7e servo外环需新wrapper/reward和重训，不能搬同一权重。

### 复现边界

无公开checkpoint；可以从随机初始化训练，不缺外部行为先验。requirements只有torch/mujoco_py/ray/gym等未pin，且含`inspect`（标准库，不应pip依赖）和旧的`sklearn`包名；现代pip直接照抄可能失败。Gym-v2+旧mujoco_py/Ray是维护成本；发布训练核心仍比仅“will upload”强。

对课题的价值：**若统一两平台的环境框架已就绪，ESCP可作为通用短历史物理适应基线，优先级应高于只换目标速度的元RL。** 它没有冻结nominal+residual模块，因此也是检验“残差是否必要”的好对照。方法本身较老，后续创新需和其快慢历史/表征稳定性思路区分。

## 已知项目二次纠偏：RMA²观测、OSCAR配置、SafeDPA开源深度

- RMA² [models.py:120](https://github.com/yichao-liang/rma4rma/blob/main/src/rma4rma/algo/models.py#L120)即便`use_pred_e=True`，actor仍拼接`agent_state`、`object1_state`、估计latent、`goal_info`。depth/history adapter只替换privileged embedding，不代表全策略不用物体位姿。UR7e真机需要为object1_state准备视觉/外部位姿估计；“只需关节历史就能部署”不成立。
- OSCAR应检查最终叠加配置：[train.sh](https://github.com/NVlabs/oscar/blob/main/examples/train.sh)追加[delan_residual.yaml](https://github.com/NVlabs/oscar/blob/main/oscar/cfg/train/controller/oscar_settings/delan_residual.yaml)，有效配置`use_extrinsics=True,learn_residual=True,freeze_base=True`，结合bootstrap_extrinsics让latent来自q/qdot/control历史。前文对基础oscar.yaml的False只是文件默认，不能据此推断正式训练无适配。
- OSCAR pretrain [delan_bootstrap.yaml](https://github.com/NVlabs/oscar/blob/main/oscar/cfg/train/controller/oscar_settings/delan_bootstrap.yaml)启用true mass matrix与传统gravity compensation，训练后正式oscar输出torque；[robot_policy.py](https://github.com/NVlabs/oscar/blob/main/oscar/policies/robot_policy.py)明确DOF_MODE_EFFORT并加学习的Coriolis/gravity torque。论文非力矩baseline禁重力，是其比较设置而非真实UR条件。复现时应解释重力差别。
- SafeDPA [ICRA2024作者项目](https://sites.google.com/view/safe-deep-policy-adaptation)的四阶段需要离线模型、策略/adapter、目标环境少量动力学fine-tune、CBF安全过滤。[官方仓库](https://github.com/LeCAR-Lab/SafeDPA)SHA `414f57303bcc0681e0301e17422cbbe04b4e6424`确有MIT和带wind的SafetyGym，但pendulum experiment、SafetyGym experiment、real-world experiment仍为TODO。完整tree只有环境和随机agent/测试，未见实现全方法的train入口。因此**论文值得引用、不能当完整可复现安全适应基线**。

## ESCP 追加实现审计：窗口、训练标签和无边界切换

以下均针对上述 SHA，而非推断现代复现版的行为。

1. [policy.py](https://github.com/FanmingL/ESCP/blob/master/models/policy.py)的环境探测器输入为当前 observation 与上一 action 的拼接，主策略接 observation 与探测 latent。默认没有 reward 或真实物理参数输入；`use_gt_env_feature`才切换到oracle参数。训练RMDM利用任务分组标签构造同域方差与跨域分散损失，**需要训练时知道属于哪个模拟域，但部署不需要故障标签**。把这两个阶段混称“需要已知故障类别”会误导。
2. `inference_rnn_fix_one_action`维护多个不同起点的GRU隐状态分支，窗口满后丢弃最老分支，并加入一个初始化分支；同一新观测输入各分支，取最老有效分支输出。H=16是有界短历史，不是无限累计GRU。直接用一个永不清空的GRU或仅加Transformer缓存不等价。固定窗口模式的`inference_reset_one_hidden`还明确未实现并行采样分支；移植向量环境时需保留语义。
3. [sac.py](https://github.com/FanmingL/ESCP/blob/master/algorithms/sac.py)的训练agent为stationary，不在训练episode内切换；NS/OODNS agent负责测试切换。因此它证明“从固定域训练分布学到可在突变中重新推断”的能力，不是原默认就用连续变化域训练。
4. [nonstationary_env.py](https://github.com/FanmingL/ESCP/blob/master/envs/nonstationary_env.py)的`period=100, interval=10`：每10步检查，但`int(step/period)`索引到每100步才切换的参数列表。插值代码被注释，实际是分段常值突变。gravity写入`model.opt.gravity`，damping写入`model.dof_damping`，friction写入geom参数； setter不重置q/qdot。
5. [Agent.py](https://github.com/FanmingL/ESCP/blob/master/agent/Agent.py)只在真正episode done时reset环境和历史，不因为物理参数切换reset；env_param用于记录/训练标签及oracle分支，没有切换时刻的输入信号。故默认NS测试满足连续状态、无故障边界提示。

**可控复现代价**：修requirements中的inspect/sklearn、Gym reset/step返回值、mujoco_py→mujoco与Ray兼容性，属于依赖/API维护；保留SAC、RMDM和固定历史GRU后可称ESCP移植。换成PPO+TCN、去掉RMDM换预测误差、改变采样窗口则应称受ESCP启发的新实现，不能把运行成功等同原法复现。Go2-W/UR7e均可使用参数化连续Box，但必须逐通道定义归一化，不能把腿关节角、轮速度和机械臂关节角都当相同物理单位。论文整机1D damping变化比单独电机降效简单，应新增独立执行器效率/延迟等物理任务库。

## OMPO：ICML2024发布代码与NSR2026扩展必须分开

[ICML2024正式论文](https://proceedings.mlr.press/v235/luo24d.html)为《OMPO: A Unified Framework for Policy Learning under Policy and Dynamics Shifts》，[正式PDF](https://raw.githubusercontent.com/mlresearch/v235/main/assets/luo24d/luo24d.pdf)。作者链接[官方仓库](https://github.com/Roythuly/OMPO)，本次HEAD `94f3b16bfcf44f8fcda356c68fdcde28f5e90e16`。它以local/global replay的transition occupancy匹配修正旧数据，算法无需部署故障类别，但需要新交互reward与在线优化；不等于只做一次history encoder推理的瞬时适应。

### 当前代码实际覆盖

- 递归tree仅20个文件，包含三个main、模型、ReplayBuffer、Gym locomotion和Panda helper。README声称MIT，但tree无LICENSE文件；没有requirements/environment锁和公开checkpoint。README命令还残留“OBAC”名称。核心训练实现确实存在，不能简单归为占位repo。
- [main_non_stationary.py](https://github.com/Roythuly/OMPO/blob/main/main_non_stationary.py)在每episode计算sin域参数并`env.reset(...)`，随后内层只调用`env.step(action)`；[Ant环境](https://github.com/Roythuly/OMPO/blob/main/Non_stationary_env/ant_random.py)虽有`step_with_random`，main没有调用。论文Appendix E的Hopper/Walker几何是episode变化，与发布代码相符；Ant/Humanoid另外描述每步随机gravity/wind，当前main没有该逐步项。故不能宣称默认发布训练已复现连续运行的突发故障。
- local buffer满1000条后进行批量discriminator更新并整体clear，global为100万；这与始终滑动保留最近1000条不同。在线采样默认先随机5000步，不能据此保证第一次突然故障后毫秒级适应。
- [panda_env.py](https://github.com/Roythuly/OMPO/blob/main/Non_stationary_env/panda_env.py)默认`control_type='joints'`，flatten Dict observation，包装Gymnasium→旧Gym返回格式；NoiseWrapper实际加噪行被注释。三个main未接入这一helper，初始化注册也主要为locomotion。**有臂接口草稿，不等于已发布完整Panda/MetaWorld实验脚本和数据**。
- [main_transfer.py](https://github.com/Roythuly/OMPO/blob/main/main_transfer.py)调用`update_parameters`少传必需`writer`参数，和[algo.py](https://github.com/Roythuly/OMPO/blob/main/model/algo.py)签名不一致，静态可确定会报TypeError。transfer的real_env仍是模拟环境，并非真实机器人驱动。
- 模型为tanh Gaussian actor、scalar twin Q、正reward裁剪/偏移；无ODE flow actor、101 quantile critic、ResNet共享视觉编码器。

### NSR2026新论文覆盖的范围

[《Embodied learning under policy and dynamics shifts》正式版](https://academic.oup.com/nsr/article/13/21/nwag506/8766030)，DOI10.1093/nsr/nwag506，2026-08-19发布、11-10排版修正。新版本增加signed-reward asinh surrogate、flow actor、distributional critic与视觉实验，却仍把data availability指向同一旧仓库。**新结构不能视作已由此仓库开源**。

真实机器人新增实验是TianJi的抓取前物体被外杆移位，机器人重新接近并完成放置；Panda-Gym是模拟动作噪声。文章把真机限定为support-preserving的proof of concept，非执行器损坏或不可逆故障；未在可读正文中找到UR式底层驱动/控制Hz合同。不可将其称为“真实Franka在失效电机下自恢复”。

### 对本课题的正面使用方式

OMPO仍值得作为**持续在线学习、旧replay污染**方向的强相关基线，而不是快速历史适应的首个本科baseline。可从ICML旧版本修复入口，在统一Gymnasium模拟wrapper上新增显式t*参数调度与完整Panda/UR任务；两平台分别训练同一off-policy算法。代价是局部/全局采样与discriminator稳定性、在线交互预算、旧replay标签及奖励定义，且需要明确这是ICML算法移植。若采用NSR flow/quantile/asinh，则当前证据下属于重实现，不应声称官方全法开箱复现。

## UARL：正式、可训练的现代通用残差候选

《Accelerating Residual Reinforcement Learning With Uncertainty Estimation》，[IEEE正式页](https://ieeexplore.ieee.org/document/11267054)，DOI10.1109/LRA.2025.3636808，**RA-L 2026,11(1):970–977**；不是仅有2025 arXiv。开放[作者论文PDF](https://rai-inst.com/wp-content/uploads/2026/05/2506.17564v2.pdf)、[作者项目页](https://lakshitadodeja.github.io/uncertainty-aware-residual-rl/)、[官方代码](https://github.com/lakshitadodeja/uncertainty_aware_residual_rl)，MIT，SHA `8125f33dcf490d4cf93d57a27d3e1963a47f52ea`。

### 算法与已有相似研究

它用base policy uncertainty（到训练数据的距离、ensemble方差）只在不确定区域探索残差；critic评价最终执行的base+residual action，actor输出残差，以处理随机base。**“冻结基策略+不确定性门控残差”已有正式近邻，不能直接作为新论文创新。** 论文含Robosuite/GMM与diffusion base、D4RL Kitchen，真机为训练后zero-shot Can sim2real，并非硬件突发故障后的在线更新。

### 发布训练与部署合同

- README给Py3.10、外部DPPO与内置SERL launcher安装；requirements锁定torch2.4、JAX0.4.33、robosuite1.4.1、robomimic0.3.0等，但混入大量设备/视觉/TF依赖，不能视为精简CPU demo。
- [train脚本](https://github.com/lakshitadodeja/uncertainty_aware_residual_rl/blob/main/examples/residual_sim/scripts/can/distance_to_data.sh)确实启动1M步SAC residual，10000步base burn-in，5种seed，eval每50000步、20条轨迹；当前方便复现的脚本为Can/Square。外部[官方Drive base/data](https://drive.google.com/drive/folders/1lQXcmddQQ4ZVAbDoNdeZMdXJ-WFvQL-Q?usp=sharing)提供所需diffusion权重、归一化与训练状态；不需用户自备私有nominal，但下载可达性/文件内容本次未下载验证。
- [主循环](https://github.com/lakshitadodeja/uncertainty_aware_residual_rl/blob/main/examples/residual_sim/sync_residual_diffusion.py)确实训练和评估，base模型通过配置`network_path`加载；Hydra实例化后无需在main显式torch.load，不能误判为随机base。tanh残差与base相加，环境wrapper在[-1,1]clip。
- [Can配置](https://github.com/lakshitadodeja/uncertainty_aware_residual_rl/blob/main/examples/cfg/can_robomimic.yaml)obs23、action7、cond_steps1/horizon_steps1；[wrapper](https://github.com/lakshitadodeja/uncertainty_aware_residual_rl/blob/main/serl_launcher/serl_launcher/wrappers/robosuite_state.py)观测eef pos/quat、gripper qpos、object-state，动作shape硬编码7。实际底层controller元数据来自robomimic checkpoint，不应仅凭action7猜成7轴关节力矩；通常Robosuite7D可为6D EE+gripper，须读下载checkpoint元信息后确认。
- [asymmetric SAC](https://github.com/lakshitadodeja/uncertainty_aware_residual_rl/blob/main/serl_launcher/serl_launcher/agents/continuous/assymetric_sac.py)明确critic target与actor loss均以完整动作求Q并clip；不是只在README描述。训练API `sample_actions`有`**kwargs`，main的`deterministic=False`会被接受，不能据此报TypeError。

### 两平台可行路线与边界

可把UARL当**残差组合/不确定性对照的算法来源**，不把Robosuite wrapper直接套Go2-W：先为两平台各训练一个nominal continuous base，收集各自state dataset，逐通道归一化动作，再用同一uncertainty+SAC算法训练residual。其距离度量原代码是原始state欧氏距离，换机器人必须考虑各特征单位与规模；没有天然的故障latent/history，在完全相同可见状态而隐动力学不同的POMDP中，feed-forward residual不能充分辨别变化原因。加入短历史可行，但要报告为扩展，并与ESCP/GRAM的历史适应对照。原论文未证明轮腿/UR7e或统一权重。
