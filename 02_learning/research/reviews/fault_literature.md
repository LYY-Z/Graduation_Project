# 容错RL与突发故障恢复：独立文献筛查

> 阶段记录（2026-11-22）：以下论文、分类和建议反映当时已查到的资料，不是最终候选或后续检索边界。可随新文献和核验结果替换、修正。

核查日期：2026-11-21。范围：Go2-W轮足四足 + UR7e固定基座机械臂；允许两个策略独立训练。这里只核查论文/作者项目/作者代码，不把第三方复刻当官方。未安装环境、未跑训练或接触真机，因此“有源码”不等于“已成功复现”。

## 决策摘要

1. 最切题但不满足完整开源的正式论文很多：FT-Net（RA-L2023）、Random Joint Masking（ICRA2024）、DreamFLEX（ICRA2025）、FT-CPG（RA-L2025）、Contrastive Forward Prediction（CoRL2025）。不能据Github按钮认定训练代码已发布。
2. 实际训练链较完整的额外入口：IIT `fault-locomotion-isaaclab`（Go2/ Pegasus，当前对应MoE论文自称arXiv）；RecoveryChaining（IROS2025，机械臂任务失败后的局部恢复）；RMA²（CVPR2024，机械臂对物性和外力适应）。三个方向的动作、故障对象、部署观测差别很大，不能拼成一个现成通用机器人策略。
3. 新文 Joint-Health-Aware RL 确实同时涉及Go2/Panda，但主要是仿真+固定episode退化，没查到作者发布代码和正式录用。其Go2的动作offset缩放尤其不能等同物理电机扭矩失效。
4. UR7e为6自由度，Franka/Panda为7自由度；单关节完全锁死后保留任意6D末端位姿跟踪一般缺少自由度。选题应将UR任务设为可行的3D位置/有限姿态/沿面轨迹，或者用轻度退化、外力、载荷、摩擦作为两平台共同扰动，不承诺任何关节全锁后的任意轨迹。

## 逐篇名单（不以数量掩盖可复现缺口）

|论文|正式发表证据/原始来源|故障与恢复相关性|官方实现核查与判断|
|---|---|---|---|
|FT-Net: Learning Failure Recovery and Fault-tolerant Locomotion for Quadruped Robots|[IEEE RA-L 2023 DOI](https://doi.org/10.1109/LRA.2023.3329766)，[作者稿](https://dartmouthrobotics.github.io/icra-2025-robots-wild/spotlight-papers/icra-2025-robots-wild-7.pdf)|任意相位电机部分/完全失效，本体历史适配，四足转三足|[作者repo](https://github.com/arclab-hku/FT-Net_Quadruped_Robots)仅图和Supplementary PDF；没有训练器、环境、权重。强related work，不能当完整复现底座|
|Learning Quadrupedal Locomotion with Impaired Joints Using Random Joint Masking|[ICRA2024作者项目](https://sites.google.com/view/learning-impaired-joints-loco)，[论文](https://arxiv.org/abs/2403.00398)|Go1，随机关节失能、历史估计+课程|官页只有论文/视频，未发现代码链接；不是已核验开源|
|Multi-Task Learning of Active Fault-Tolerant Controller for Leg Failures in Quadruped Robots|[ICRA2024 DOI](https://doi.org/10.1109/ICRA57147.2024.10610151)，[作者论文](https://arxiv.org/abs/2402.08996)|SOLO8，同一腿两个关节并发断电/锁死；三任务策略健康/断电/锁死|未找到作者训练repo；8DOF SOLO与Go2-W差异显著|
|DreamFLEX|[ICRA2025作者页](https://dreamflex.github.io/)|故障估计调制latent；复杂地形、弱化/锁死|官页提供论文视频，无Code；不能只因架构吻合就选作可直接复现基座|
|FT-CPG|[IEEE RA-L10(7):6936–6943,2025](https://doi.org/10.1109/LRA.2025.3572772)|Go1，同一腿任意数量关节各自锁死或断电，真正混合故障而非仅单电机；CPG策略推断故障并调整节律|此次未找到作者公开训练仓；值得综述/混合故障设计参考，CPG动作不是任意关节残差|
|Contrastive Forward Prediction RL for Adaptive Fault-Tolerant Legged Robots|[CoRL2025 PMLR305正式proceedings](https://proceedings.mlr.press/v305/fu25b.html)，[全文+附录](https://raw.githubusercontent.com/mlresearch/v305/main/assets/fu25b/fu25b.pdf)|历史预测误差+对比学习；训练mask作为标签；未见锁死场景零样本，四足/六足|作者主页/正式页/PDF未发现官方实现链接；源码缺口。不能把forward-model论文写成现成开源基座|
|Meta Reinforcement Learning of Locomotion Policy for Quadruped Robots With Motor Stuck|[IEEE TASE DOI](https://doi.org/10.1109/TASE.2024.3424328)，[作者仓](https://github.com/chenci107/MetaRL_for_Quadruped)|卡死关节，context元RL；PyBullet/Lite3/JYLite环境|有环境+policy/context ONNX，没训练器；标准演示收集完整rollout后更新posterior并reset再跑，不能作为瞬时within-episode恢复已复现|
|Towards Fault-tolerant Quadruped Locomotion with RL|[IEEE CAI2024会议全文](https://ieeecai.com/2024/wp-content/pdfs/540900b433/540900b433.pdf)，[DOI](https://doi.org/10.1109/CAI59869.2024.00257)|A1单关节机械锁死、teacher/student；仍可承重的locked关节|和Saving the Limping预印本属紧密同一研究线，勿当两篇独立方法计数；没确认官方训练发布|
|AcL: Action Learner for Fault-Tolerant Quadruped Locomotion Control|[作者论文](https://arxiv.org/html/2503.21401v1)，[作者repo](https://github.com/ACT-legmotion/AcL-ActionLearner)|teacher/student、多关节故障；action learner|repo实际只有video&pics/README；论文承诺接受后放代码。此轮没核准正式发表，不能说已开源训练|
|FT-WBC|[作者CoRL2026 accepted声明](https://ft-wbc.github.io/)，[作者仓](https://github.com/hhhappyshow/FT-WBC-Learning-Fault-Tolerant-Whole-Body-Control-for-Legged-Loco-Manipulation)|腿部弱化/锁死下locomanipulation，故障预测+安全姿态映射|repo仍Code is coming soon。不是固定UR7e执行器失效恢复；腿失效下手臂任务保持不是手臂关节失效|
|Mixture-of-Experts RL for Fault-Tolerant Legged Locomotion|[作者论文](https://arxiv.org/html/2606.25965)，[IIT官方代码](https://github.com/iit-DLSLab/fault-locomotion-isaaclab)|估计故障显式选专家；1/2条腿失效，允许严重失效时拖行|训练/仿真部署/ROS2部署和部分权重真实存在。仓自称arXiv，未核准正式venue；不能假称RA-L/ICRA|
|Learning Fault-Tolerant Locomotion with Adaptive Gait Timing|[作者论文](https://arxiv.org/abs/2608.07328)，[IIT作者视频声明IROS2026](https://www.youtube.com/watch?v=x4paP49SKuY)|68kg KYON，partial power loss，critic privileged、actor历史，额外gait frequency action|未找到作者训练发布；不能因同属IIT就认定上一个repo复现本论文|
|RecoveryChaining|[MERL正式IROS2025记录](https://www.merl.com/publications/TR2025-152)，[DOI](https://doi.org/10.1109/IROS60139.2025.11245856)，[作者代码](https://github.com/shivamvats/recovery-chaining)|操作模型控制器执行失败后，学局部恢复并切回某个nominal controller；不是电机失效控制|真实故障采集/训练/eval源码；有failure数据和value_fn，没发现已发布完整recovery policy weights；见深审|
|Rapid Motor Adaptation for Robotic Manipulator Arms (RMA²)|[CVPR2024正式全文](https://openaccess.thecvf.com/content/CVPR2024/papers/Liang_Rapid_Motor_Adaptation_for_Robotic_Manipulator_Arms_CVPR_2024_paper.pdf)，[Oxford官方](https://www.robots.ox.ac.uk/~vgg/publications/2024/Liang24/)，[作者仓](https://github.com/yichao-liang/rma4rma)|Panda/ManiSkill2，未知物体形状/密度/摩擦和外力；深度+状态动作历史|训练/adapter/eval/task代码目前真实存在；无打包模型权重，需定制ManiSkill2/SB3 forks。没有原生UR7e或真机迁移证据|
|Adaptive Compensation for Robotic Joint Failures Using Partially Observable RL|[Algorithms2024正式论文](https://www.mdpi.com/1999-4893/17/10/436)，[作者项目](https://hanhpt23.github.io/franka-IK/)，[作者repo](https://github.com/Hanhpt23/franka-IK)|Franka拉抽屉，永久、随机间歇、前/后半程失效|仅仿真，结论明确真机为future work；repo franka.py实际为DH/IK/轨迹绘图，无PPO训练/IsaacLab故障环境/weights。作者“all code/models”措辞不能代替审计|
|A New RL Fault-Tolerant Tracking Control Method With Application to Baxter Robot|[IEEE/ASME TMECH2024 DOI](https://doi.org/10.1109/TMECH.2023.3309888)|Baxter柔性多关节，RBF估计+actor/critic+事件触发在线补偿|正式控制论文，但未找到官方代码；与PPO端到端sim2real不是一套范式|
|Fault-Aware Robust Control via Adversarial RL|[CYBER2021官方digest](https://ieee-cyber.org/2021/wp-content/uploads/2021/07/Cyber21-Digest-V3_0s.pdf)，[论文](https://arxiv.org/abs/2011.08728)，[DOI](https://doi.org/10.1109/CYBER53097.2021.9588329)|DClaw + DKitty，adversary聚焦差表现joint damage；可跨操作/行走借鉴|未找到作者完整训练/权重入口；并非UR臂，不建议本科作为重构起点|
|Reinforcement Learning with Adaptive Curriculum Dynamics Randomization for Fault-Tolerant Robot Control|[原文](https://arxiv.org/html/2111.10005)|每episode抽腿和输出衰减k；hard-to-easy课程；单策略|没有核准正式venue/官方代码；重点是reset随机化鲁棒性，不足以证明突变恢复|
|Joint-Health-Aware RL for Robust Robot Control Under Actuator Degradation|[原文2026-10-30 v1](https://arxiv.org/html/2610.41348)|Walker/Go2/Cassie/Panda；HealthNet历史估计；多关节连续衰减|未找到作者代码或正式录用；大部分实验episode内固定退化，仅Go2个例t=1.5s；target offset衰减模型有关键物理区别|
|Test-Time Adaptation of Manipulation Policies Under Actuator Degradation (TeAR)|[原文](https://arxiv.org/html/2609.36182)，[作者仓](https://github.com/somsagar07/TeAR-Telemetry-Aware-Action-Rectification)|SO-101/robosuite，实测温度电流电压conditioning，冻结策略外动作矫正，监督训练|真实代码/测试/说明，但base policies/demos不bundled，正式review未核准。与Dongwon-Son的Torque Adaptation Module TAM为不同作者、不同论文，绝不能混淆|
|Meta RL for robust quadruped locomotion under joint failures (ARER-MetaRL)|[PLOS ONE2026正式全文](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0361099)|Isaac Sim多关节锁死0–3训练、最多6测；仅sim|新但非首选；先审数据/源码可得性。不能用PLOS已发替代完整开源证据|

## 深审1：RecoveryChaining（正式已发 + 源码较完整，但恢复对象不同）

作者仓实读路径：`belief_srs/envs/failure_detector_wrapper.py`、`discrete_action_wrapper.py`、`skills/primitive_skill.py`、`recovery_skill.py`、`cfg/ctrl/osc_pose.yaml`、`cfg/rl/rc_pick_place.yaml`、`scripts/learn_recoveries.py`、`run_experiments.sh`、`evaluate_policies.sh`。[仓入口](https://github.com/shivamvats/recovery-chaining)

- 观测配置为`object-state + robot0_proprio-state`，不使用相机原图；故障检测器基于末端力阈值和夹爪开度，不要求关节故障真值标签。但真实物体位姿、夹爪状态和力感知要有部署来源；仿真object-state不可自动等同真实可观测。
- 高层PPO动作为离散motion primitive索引加nominal controller选项；平移分辨率示例0.02，旋转选项开启、夹爪动作默认关闭。primitive根据当前EEF姿态构造目标，再用`OSC_POSE`执行；配置`control_delta: False`，故底层接收绝对目标pose+夹爪。并非每步输出6/7关节力矩。
- `primitive_skill.py`虽以relative eef motion描述，但实际先取MuJoCo site的当前位置/旋转，计算absolute goal后重复执行若干步。迁UR应替换为真实TCP读数+IK/位置伺服或明确的阻抗接口；不可拿其动作直接传UR关节驱动。
- 故障数据采集保存MuJoCo state/XML用于重置训练。`observe_true_state`出现于训练/日志并不意味着政策输入都用了oracle；必须沿wrapper区分。恢复训练从失败状态分布重置，不代表真实故障后也允许reset机器人。
- 仓有Panda默认配置和MELFA资产；实体迁移论文需与released env对应核对。无需同时迁四足，可将它作UR“恢复到可继续任务集合”的对照。
- `run_experiments.sh`提供5 seeds、10 CPU、200k高层步示例；`evaluate_policies.sh`默认某些env/rl配置在仓树中未显式匹配，说明“脚本存在”仍需小规模运行验证路径。仓有failure demos/value_fn.pt，不等于已发布recovery policy checkpoint。未运行，判定“训练基础好，论文全部复现仍缺核验”。

## 深审2：RMA²（机械臂自适应实用入口）

[官方Oxford页面](https://www.robots.ox.ac.uk/~vgg/publications/2024/Liang24/)确认为CVPR2024；[作者repo](https://github.com/yichao-liang/rma4rma)含`src/rma4rma/train.py`、`algo/{ppo,adaptation,policy,models,evaluate_policy}.py`、`tasks/{pick_single,peg_insertion,turn_faucet}.py`和配置。

- 真正两阶段：privileged encoder teacher学隐变量latent；freeze后adapter用深度和状态动作历史估计latent。不是从任务reset后在线梯度调参。
- privileged包括物体尺寸、密度、摩擦、夹爪接触impulse及type/token embedding；部署必须取消真实physics标签。仍假设有带噪物体位置，由感知模块供应。
- 物体物性随episode随机和动态外力要分开讨论。论文外力会按概率重新采样并覆盖旧残留力，属于运行中扰动；物体质量泛化不自动表示途中载荷突变已测。
- 仓明确A100评估、定制ManiSkill2和SB3 fork；有base→adapter→eval命令，但未见论文权重打包。UR7e要换asset、7→6DOF、碰撞/限制、夹爪接口和动作控制器，重新训练。原文任务主要sim benchmark，没有“现成UR真机适配”证据。

## 深审3：IIT fault-locomotion-isaaclab（实际最丰富的故障工程仓）

[官方仓](https://github.com/iit-DLSLab/fault-locomotion-isaaclab)、[训练说明](https://github.com/iit-DLSLab/fault-locomotion-isaaclab/blob/main/README_train.md)、[部署说明](https://github.com/iit-DLSLab/fault-locomotion-isaaclab/blob/main/README_deploy.md)。API递归tree已确认：`scripts/rsl_rl/{train,play}.py`、`scripts/moe_rsl_rl/{train_moe,play_moe}.py`、`tasks/fault_locomotion/fault_locomotion_env.py`、`go2_env_cfg.py`、`tasks/custom_events.py`、`supervised_learning_networks.py`、`deploy/play_mujoco.py`、ROS2 controller以及Go2/Pegasus policy.onnx/model.pt。一个release名v2.3.2；当前main README另推荐IsaacLab3.0/Newton，说明复现必须锁版本，不能混用。

- 有基础速度估计和故障RMA，但配置可关闭。policy wrapper明确known `_per_leg_joint_status`用于MuJoCo schedule/console模拟，policy输入可用真值或RMA估计。只有勾选并实际加载RMA才可称未知故障部署。
- 警惕现成Go2 moe_blind权重的依赖：tree看到policy权重，但未看见同目录rma/concurrent estimator权重；config默认路径不等于文件已存在。部分Pegasus concurrent SE权重真实存在。应在复现清单逐文件核验。
- 主动作12关节目标位置offset，经clip/filter/scale和default pose；MoE可重排healthy-leg输出。不是轮足16自由度。Go2→Go2-W必须加4轮velocity/torque维度及混合动作head，并重新定义foot-wheel接触、滚动滑移、reward和wheel fault。
- 训练源码出现专门onset采样window(3,30)，意在补足走动中突然失败检测样本；比只reset随机化更接近需求。正式paper/代码默认的真值fault、估计fault模式需分别报告结果。
- 部署base velocity可用concurrent estimator；不能假定Unitree运动服务关闭后SportModeState真速度仍可读。要估计或外部定位，并测试故障时估计器是否崩溃。
- 论文MoE是故障分类显式选专家，1条腿到2条腿严重失效可能拖地；不要把“仍前进”宣传为保持正常轮足运动质量。

## 深审4：Chen Motor-Stuck 元RL（有权重，不完整训练发布）

[作者仓](https://github.com/chenci107/MetaRL_for_Quadruped)，实读[推理主文件](https://github.com/chenci107/MetaRL_for_Quadruped/blob/main/infer_policy/sim_policy_onnx.py)。native JYLite/Lite3 PyBullet，树包含TG/IK/Bezier及A1/Lite3 URDF，两个ONNX。

- `update_context`输入明确为obs/action/reward（默认不含next obs）。reward在真机上如何得到需要核实，不能说只需关节编码器。
- `__main__`固定task idx及锁定角，先`rollout(accum_context=True)`最多200步，再`infer_posterior(context)`，再`rollout(accum_context=False)`，第二次rollout内部再次env.reset。这一发布演示是跨rollout适配，不是突变后立即滑窗适配。
- 没发现meta-training/PEARL训练实现或optimizer目录；这不满足用户要求的作者训练代码。虽然可CPU ONNX试跑，但后续自主改进要自己补训练。
- native残差/Bezier+IK语义需沿wrapper确认，不能直接当12D关节力矩输出；迁Go2-W成本大。

## 深审5：Pham Franka容错PPO（正式论文、开源承诺与实际不符）

[正式论文](https://www.mdpi.com/1999-4893/17/10/436)、[官方项目](https://hanhpt23.github.io/franka-IK/)、[实际repo](https://github.com/Hanhpt23/franka-IK)。观察：9个robot joint角/速度（含夹爪）+抽屉位置速度+gripper到drawer距离；没有显式故障label。动作论文为9个关节目标角。永久/间歇失效、上半段正常下半段失效等确比纯reset参数更切题。

但repo根目录仅`franka.py`、媒体和网页。实读franka.py只有DH、Frame、RobotSerial、数值IK、轨迹插值/绘图，`failure_joint`通过轨迹某列归零演示IK失败；没有PPO、IsaacLab task、RL模型、训练/eval。其93.6%为仿真任务成功率，文章明确未来才迁真实机器人。期刊级别与开源缺口均不宜忽略。

## 深审6：Joint-Health-Aware（新、跨形态，但物理语义限制极关键）

[arXiv版本记录](https://arxiv.org/abs/2610.41348)只有2026-10-30 v1，未见venue或code链接；[完整方法](https://arxiv.org/html/2610.41348)说明训练和部署都用预测health，true health仅监督。K=10历史。主要benchmark h在episode内固定；仅Go2图例1.5s后注入5关节衰减，可引用为个例，不可扩写成全部系统atic recovery benchmark。

对torque环境：u_exec=h⊙u。对Go2/Cassie target-position环境：q*=q0+s(h⊙a)。后者h=0使控制目标回默认关节角，仍有PD主动刚度支撑，绝不是零电流/无力矩/自由关节。若把这篇用于UR的servoJ offset缩放，模拟的是命令行程受限，不能报告为真实执行器有效性衰减。原文实验全sim。作为跨机器人论文动机参考很贴题；在“正式已审+作者开源+可复现”筛选中暂不合格。

## 易混淆点与可发表实验设计建议

- 两个TAM：Som Sagar/Ransalu Senanayake的TeAR仓曾自名TAM；Dongwon-Son/Dieter Fox的Torque Adaptation Module是另一论文。自重命名并不表明同一工作。TeAR是telemetry-conditioned动作矫正，监督训练；不能写成必然RL算法。
- 故障种类至少分：扭矩有效性alpha、机械锁角、目标命令offset缩放、关节速度受限、动作延迟、传感器冻结/噪声、轮地摩擦。不能用一行`action*=h`统一后都叫电机故障。
- robust reset baseline 与 sudden-onset adaptation应同训练预算：每episode reset抽故障；episode中随机t0注入；复合外力+alpha；unseen组合（训练只单故障、测试两类组合）；故障解除后再适应。要报告t0后track误差积分、恢复到阈值所需时间、跌倒/任务失败率、峰值力和能耗，不只episode reward。
- 固定UR任务与Go2-W运动任务不同，可共享“同一类型在线残差context估计机制和同一突发扰动协议”，不能声称一个策略泛化双机器人，除非真的做了共享训练与零样本迁移。
- 完整开源判定拆成论文peer-review、author linkage、env、train、eval、weights、部署观测、native robot八列。这个领域很容易在前两列看起来很好、后六列空缺。

## 核验限制

本次执行GitHub REST递归tree时随后遇到未认证rate limit（403），改用官方raw/source页面继续审计；没有绕过访问限制。树核查不是运行核验，未宣称任何复现通过。未大规模clone、未下载数据集/权重、未运行真实机器。

## 源码固定版本与可核查行号（第二轮深审）

通过只读`git ls-remote ... HEAD`获取（2026-11-21）：

- IIT fault-locomotion-isaaclab：`738ae3604a46d99957967602dc7c3a64eb6905bf`。
- RecoveryChaining：`4894acc3768678de4dee6358df14c461a411162e`。
- RMA²：`2f938f6518709ac8cbda05c294b7765c6d16630d`。

### 决定性的IIT默认权重观测审计

[发布Go2权重所附env.yaml L496–500](https://github.com/iit-DLSLab/fault-locomotion-isaaclab/blob/738ae3604a46d99957967602dc7c3a64eb6905bf/tested_policies/go2/moe_blind/params/env.yaml#L496-L500)：history=5，`base_state_source: ground_truth`、`use_rma: false`。

[env.py L477–487](https://github.com/iit-DLSLab/fault-locomotion-isaaclab/blob/738ae3604a46d99957967602dc7c3a64eb6905bf/source/fault_locomotion_isaaclab/fault_locomotion_isaaclab/tasks/fault_locomotion/fault_locomotion_env.py#L477-L487)确认：RMA关时直接将真实joint_status拼入policy observation。[L438–451](https://github.com/iit-DLSLab/fault-locomotion-isaaclab/blob/738ae3604a46d99957967602dc7c3a64eb6905bf/source/fault_locomotion_isaaclab/fault_locomotion_isaaclab/tasks/fault_locomotion/fault_locomotion_env.py#L438-L451)确认ground truth分支读取root_lin_vel_b。

因此，默认发布的Go2模型适合作oracle baseline和仿真可行性验证，**不是未知故障+真实速度估计已配套的开箱即用模型**。仓具有RMA/SE训练能力，与该特定weight已具备能力是不同事实。

[custom_events.py L722–744](https://github.com/iit-DLSLab/fault-locomotion-isaaclab/blob/738ae3604a46d99957967602dc7c3a64eb6905bf/source/fault_locomotion_isaaclab/fault_locomotion_isaaclab/tasks/custom_events.py#L722-L744)：中途故障为固定`max_episode_length-100`时刻，仅原健康env转坏，原坏env不恢复。故“已有onset训练”是真的；“随机未知时刻/突发解除/一再切换全都支持”不成立。自己研究需要改成随机t0+t1和保持足够故障后时长。

[custom_events.py L172–195](https://github.com/iit-DLSLab/fault-locomotion-isaaclab/blob/738ae3604a46d99957967602dc7c3a64eb6905bf/source/fault_locomotion_isaaclab/fault_locomotion_isaaclab/tasks/custom_events.py#L172-L195)：坏腿PD stiffness+damping置零。[env.py L370–384](https://github.com/iit-DLSLab/fault-locomotion-isaaclab/blob/738ae3604a46d99957967602dc7c3a64eb6905bf/source/fault_locomotion_isaaclab/fault_locomotion_isaaclab/tasks/fault_locomotion/fault_locomotion_env.py#L370-L384)：policy只设置position target。这比“offset乘零仍有PD”更接近无力矩关节，但需保留passive摩擦和限制、验证求解器实际motor torque，而不是仅看mask。

[go2_env_cfg.py L52–120](https://github.com/iit-DLSLab/fault-locomotion-isaaclab/blob/738ae3604a46d99957967602dc7c3a64eb6905bf/source/fault_locomotion_isaaclab/fault_locomotion_isaaclab/tasks/fault_locomotion/go2_env_cfg.py#L52-L120)：COM和mass随机为startup，外力/力矩和joint friction/armature/gains/delay为reset。不能把这些全写成runtime突变。interval push另设，和质量突变不是同事。

### RMA²实际动作和UR迁移中的硬编码

[config.py L287–311](https://github.com/yichao-liang/rma4rma/blob/2f938f6518709ac8cbda05c294b7765c6d16630d/src/rma4rma/config.py#L287-L311)明确`control_mode = pd_ee_delta_pose`，sim_freq=120。它是末端delta pose，不是7D关节扭矩。需要UR末端增量→IK/伺服适配和速度/频率匹配。

[models.py L248–291](https://github.com/yichao-liang/rma4rma/blob/2f938f6518709ac8cbda05c294b7765c6d16630d/src/rma4rma/algo/models.py#L248-L291)的ProprioCNN硬编码39个输入channel（32D Panda agent_state+7D EEF/gripper action），[policy.py L137–151](https://github.com/yichao-liang/rma4rma/blob/2f938f6518709ac8cbda05c294b7765c6d16630d/src/rma4rma/algo/policy.py#L137-L151)确认拼接。UR从7DOF换6DOF会改变q/qdot维度，因此修改asset绝不够，需同时改encoder维度、buffer、normalization、camera几何和重新训练。

[pick_single.py L131–161](https://github.com/yichao-liang/rma4rma/blob/2f938f6518709ac8cbda05c294b7765c6d16630d/src/rma4rma/tasks/pick_single.py#L131-L161)：force每次observation getter先衰减0.8、以0.1概率重采样，按object.mass缩放，仅grasp时施加于物体center。因此是持物外力扰动，不能默认等同UR腕部推力或任意连杆外力。

[pick_single.py L188–218](https://github.com/yichao-liang/rma4rma/blob/2f938f6518709ac8cbda05c294b7765c6d16630d/src/rma4rma/tasks/pick_single.py#L188-L218)显示外力只在可选inc_obs_noise_in_priv时进入priv info；[models.py L103–125](https://github.com/yichao-liang/rma4rma/blob/2f938f6518709ac8cbda05c294b7765c6d16630d/src/rma4rma/algo/models.py#L103-L125)部署pred_e替换teacher编码，但仍有object1_state和goal_info，真实物体位置来源不可省略。

[tests/test_smoke.py](https://github.com/yichao-liang/rma4rma/blob/2f938f6518709ac8cbda05c294b7765c6d16630d/tests/test_smoke.py)明确测试仅包结构/import、不跑仿真/RL。因此CI绿不等于训练链已验证。environment.yml为Python3.11而README标3.10+，重现实验应使用仓实际环境并锁fork gitlink。

### RecoveryChaining硬件证据与边界

[论文§VI-E](https://arxiv.org/html/2410.13979v2#S6.SS5)：实际6DOF Mitsubishi Assista + WSG-32 + Mitsubishi wrist F/T，sim内对应Assista训练后转真机；错误shelf pose注入碰撞/滑移；真实Box5/5、Mustard5/5、Can4/5。对6DOF UR迁移比仅Panda7DOF更有参考价值，但每物体5次仅证明可行性，不能当大样本可靠性。

[primitive_skill.py](https://github.com/shivamvats/recovery-chaining/blob/4894acc3768678de4dee6358df14c461a411162e/belief_srs/skills/primitive_skill.py)、[OSC配置](https://github.com/shivamvats/recovery-chaining/blob/4894acc3768678de4dee6358df14c461a411162e/cfg/ctrl/osc_pose.yaml)：相对primitive先取当前EEF pose后形成absolute目标；`control_delta=False`。UR上直接复制7元素到关节命令属于接口错误。


## 后续深审：正向可用路线与实际补齐范围

会话中断不属于研究或实验时间。下列未执行训练，作者未测量的训练耗时不猜成小时数。

### DyWA：ICCV2025，真实训练链和权重；适合物性适应机制

[ICCV2025正式CVF全文](https://www.openaccess.thecvf.com/content/ICCV2025/papers/Lyu_DyWA_Dynamics-adaptive_World_Action_Model_for_Generalizable_Non-prehensile_Manipulation_ICCV_2025_paper.pdf)、[作者项目](https://pku-epic.github.io/DyWA/)、[作者仓](https://github.com/jiangranlv/DyWA)，审查commit 52eeee070c873f1c65ed62989ba4169551ab3106。它补上“正式发表+author training+环境+推理+公开权重”的正向候选缺口。

原生Panda非抓取桌面操控，student以单视点物体点云、末端状态、关节状态、previous action和目标信息为输入；历史编码通过FiLM调制动作/状态预测。teacher物性与完整点云用于训练监督，值得作为跨平台历史适应的算法参考。作者报告真实物体/桌面摩擦泛化，不是未知电机断电/锁死恢复；质量、摩擦DR也不能写成已有中途突变训练。

发布范围：[README](https://github.com/jiangranlv/DyWA/blob/52eeee070c873f1c65ed62989ba4169551ab3106/README.md#L131-L153)、[训练说明](https://github.com/jiangranlv/DyWA/blob/52eeee070c873f1c65ed62989ba4169551ab3106/dywa/exp/train/README.md)给出teacher PPO、stage2动作空间微调、student DAgger及eval。dywa/exp/scripts有独立脚本，任务/robot/controller真实存在。官方链接的[HF发布](https://huggingface.co/Steve3zz/Dywa_abs_1view/tree/main)只读元数据核实：student last.ckpt 750,633,289bytes，teacher-last.ckpt 5,576,846bytes，env normalizer 12,656bytes及teacher normalizer、test_set.json均在；未下载权重。另需CORN encoder权重、DexGraspNet预处理assets、CUDA11.3/PyTorch3D0.7.2/IsaacGym环境。

动作：[franka.py L574–604](https://github.com/jiangranlv/DyWA/blob/52eeee070c873f1c65ed62989ba4169551ab3106/dywa/src/env/robot/franka.py#L574-L604)给Cartesian relative pose 6D，加7关节刚度与7阻尼参数，总20D；[L1140–1164](https://github.com/jiangranlv/DyWA/blob/52eeee070c873f1c65ed62989ba4169551ab3106/dywa/src/env/robot/franka.py#L1140-L1164)明确Cartesian pose→IK target→joint impedance。不是20个关节位置。UR6DOF通常改为6+6+6=18D，必须改previous_action、robot_state、teacher/student输出、normalization、控制器并重训。若简化成固定阻抗+UR末端伺服，是可行算法变体，要做消融，不能沿用权重称完整论文复现。

teacher_state是否泄漏：eval脚本有add_teacher_state=1，但[student指定输入keys](https://github.com/jiangranlv/DyWA/blob/52eeee070c873f1c65ed62989ba4169551ab3106/dywa/src/data/cfg/student/rma_gru_student_base_v3.yaml#L10-L23)不含teacher_state；[前向L234–269](https://github.com/jiangranlv/DyWA/blob/52eeee070c873f1c65ed62989ba4169551ab3106/dywa/exp/train/distill.py#L234-L269)用点云、指定state keys及history。teacher_state在[loss L380–417](https://github.com/jiangranlv/DyWA/blob/52eeee070c873f1c65ed62989ba4169551ab3106/dywa/exp/train/distill.py#L380-L417)作监督。max_delay_steps=0关闭前向teacher fallback。然而发布eval仍构建teacher作loss/log；[DAgger选择L193–211](https://github.com/jiangranlv/DyWA/blob/52eeee070c873f1c65ed62989ba4169551ab3106/dywa/exp/train/train_rma.py#L193-L211)在anneal_step=1时整段eval第0步alpha=0选teacher、第1步起选student，计数不随episode reset。不能笼统称全程oracle，也不是严格每一步纯student。严格纯student评估应固定student选择、移除teacher loss wrapper并验证差异；这是推理入口整理，非缺训练算法。student.eval()使update_policy中self.training分支不更新权重。

预算：论文§3.6 teacher200K、student500K iterations；仓stage1配置4096env、[stage2脚本8192env](https://github.com/jiangranlv/DyWA/blob/52eeee070c873f1c65ed62989ba4169551ab3106/dywa/exp/scripts/train_teacher_stage2.sh)、[student脚本1024env](https://github.com/jiangranlv/DyWA/blob/52eeee070c873f1c65ed62989ba4169551ab3106/dywa/exp/scripts/train_distill_abs_goal_1view.sh)。iteration与环境step不可随意等同。降低env数/物体集/训练长度可做算法复现，但不代表论文全分布结果。发布权重使小批量eval可优先尝试；若本科主问题是退化与突发恢复，RMA²类小型本体历史框架比DyWA全视觉泛化通常更省工程，这是推断，非实测速度排名。


### IIT：缺估计器权重可补训，默认schedule有具体陷阱

发布Go2权重吃oracle不意味着仓整体应排除。源码已实现历史数据集、BCE fault estimator、并发velocity estimator，属于校准训练配置并重训，不是缺整套算法。

[Flat PPO配置](https://github.com/iit-DLSLab/fault-locomotion-isaaclab/blob/738ae3604a46d99957967602dc7c3a64eb6905bf/source/fault_locomotion_isaaclab/fault_locomotion_isaaclab/tasks/fault_locomotion/agents/rsl_rl_ppo_cfg.py#L31-L34)默认max_iterations=2500、num_steps_per_env=24；[Go2配置](https://github.com/iit-DLSLab/fault-locomotion-isaaclab/blob/738ae3604a46d99957967602dc7c3a64eb6905bf/source/fault_locomotion_isaaclab/fault_locomotion_isaaclab/tasks/fault_locomotion/go2_env_cfg.py)的RMA/SE start=12000、end=16000、interval=1000。直接打开use_rma配默认Flat训练，到2500结束仍没有训练估计器。要同步改schedule或明确训练超过12000。按4096env×24steps×12000iterations，启用前约11.8亿转移；这是仿真样本预算，不等于GPU耗时。

[custom_observations.py](https://github.com/iit-DLSLab/fault-locomotion-isaaclab/blob/738ae3604a46d99957967602dc7c3a64eb6905bf/source/fault_locomotion_isaaclab/fault_locomotion_isaaclab/tasks/custom_observations.py)中RMA对角速度/重力/command/q/qdot/prev_action历史做bitmask分类，真实mask是监督标签；buffer优先采故障后3–30step。源码step_counter/24换算iteration，改num_steps_per_env需一起检查。SE初期真值、随后混合估计，最终部署必须另测纯估计。监督训练有CPU buffer和验证早停，不能因网络小就假设没有内存/课程成本。

Go2-W迁移：保留PPO和监督估计器逻辑可行；12DOF Go2→16DOF轮足的asset/contact/observation/action map是实质移植。需4个wheel velocity action、轮半径/转动惯量/滚动接触、joint ordering/轮速单位及healthy reward；descriptor扩到轮执行器并区分轮堵转、失驱、腿退化。速度输入可并发估计或LIO，不能默认证实机SportModeState线速度可读。没有Go2-W或UR发布权重，属于算法模块移植。

### Learning on the Fly：RA-L2026，轻量原生复现链；跨两平台需重构动力学

[作者正式稿](https://rpg.ifi.uzh.ch/docs/RAL26_Pan.pdf)明确2025-12-17accepted；[官方项目](https://rpg.ifi.uzh.ch/lotf/)、[作者仓](https://github.com/uzh-rpg/learning_on_the_fly)，commit cba6e5370773ace8a08107f02810eecabf16c793，DOI10.1109/LRA.2026.3655300。提供JAX/Flax BPTT、residual dynamics学习、full/LoRA finetune、三任务环境、约1MB policy checkpoints和residual模型，以及约416KiB示例数据。原生quadrotor仿真训练和残差拟合可作为真实正向备选。

动作是总推力+三轴bodyrate；残差模型19D(position3+R9+velocity3+command4)→linear acceleration3。在线真实数据更新残差，再在可微模型更新policy，不需部署真实故障标签。但残差监督要由实测状态/加速度构建；“视觉actor不吃状态”不等于整个学习循环无需状态估计。

[quadrotor_obj.py L297–401](https://github.com/uzh-rpg/learning_on_the_fly/blob/cba6e5370773ace8a08107f02810eecabf16c793/lotf/objects/quadrotor_obj.py#L297-L401)前向用residual，custom JVP backward仅用解析模型，与论文设计一致。不能直接宣传完整微分穿透接触。[finetune示例](https://github.com/uzh-rpg/learning_on_the_fly/blob/cba6e5370773ace8a08107f02810eecabf16c793/examples/state_hovering/3_finetune_policy_full.ipynb)仍设use_forward_residual=False，即加载residual权重后默认也不使用；需明确改True并核查前向差异。这是示例配置缺口，不缺训练器。全树未见论文真机异步ROS控制/采样nodes，仿真复现与真实完整闭环需分开。

作者称RTX4060也测试过，原生学习预算轻；Go2-W接触切换/轮滑需新模型，UR需可微6DOF动力学/控制模式/残差标签，均非asset替换。宜作在线更新机制对照或高级备选，不是两个平台的省事主底座。
