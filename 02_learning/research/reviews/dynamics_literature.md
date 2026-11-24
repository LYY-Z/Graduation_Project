# 动力学、自适应模型与突发物理变化：文献及代码审计

> 阶段记录（2026-11-22）：以下论文、分类和建议反映当时已查到的资料，不是最终候选或后续检索边界。可随新文献和核验结果替换、修正。

审计日期：2026-11-21。用途：为 Go2-W 与 UR7e 分别训练控制器，但研究同一种“任务执行中物理变化后的运动恢复”机制。只查阅作者、机构、会议/期刊和官方仓库；未安装环境、运行训练或操作机器人。以下“已发布”只表示文件可读取，并非已经复现。

## 首先给出的判断

1. **可以研究一个跨两类机器人的算法问题，但没有找到同时面向 Go2-W 与 UR7e、可直接复现的官方训练/故障注入/评估/部署闭环。** 更现实的是统一适应与评估协议，保留各机器人自己的状态、动作、奖励和模型尺寸。
2. 若坚持模型驱动路线，**FAMLE 的任务接口最接近“关节效率变化后恢复”**，而 **Situationally-Aware Dynamics Learning 的新代码最接近“运行中发现动力学变化”**。两者都需要增加本项目的双机器人环境。FAMLE 发布代码还有重要的硬编码故障问题，见下文。
3. **不宜把“变化点检测 + 重置历史/贝叶斯末层/模型库”直接当作论文创新。** MOCA（NeurIPS 2020）、MBCD（AAMAS 2021）、MOLe（ICLR 2019）已经覆盖很多核心思想。2026 年 TAM、Learning on the Fly 等又强化了残差适应方向的竞争。
4. 对本科项目，建议先做**可解释的动作效率/闭环响应适应，配合有限幅度恢复策略**。先限定一种任务内突变（效率下降），再比较负载变化、短暂外力作为干扰。全面训练可微接触世界模型、在线重训整套策略、主动双重控制三者同时进行，工作量明显过大。

## 证据等级和问题边界

- **W**：明确关注不断变化/任务内变化，并有相关算法或环境代码；仍须检查默认实验是否在 episode 中途切换。
- **F**：有损伤/执行器故障恢复证据，但多数实验可能先施加损伤，再开始试验。
- **S**：主要是固定参数的 sim-to-real 或新任务适应，不自动算突发恢复。
- **C**：支持模块或通用 MBRL，不是故障恢复方法本身。
- **T/E/D**：训练/环境或数据与评估/实机部署。`有`是文件已观察到，`部分`是缺子系统或硬件桥接；未检查运行结果。

“零扭矩”“锁死关节”“速度目标为零”“扭矩乘 0.5”“动作反号”不应混为一种故障。对 UR 的位置/速度闭环接口，在软件指令上乘数与电机真实效率下降不是等价干预。对 Go2-W，12 个腿关节之外还有轮子；普通 Go2 的资产、动作和接触模型不等于 Go2-W。

## 文献筛选表（16 项主要参考，另列未满足条件的新工作）

| 工作及正式出处 | 官方证据/代码 | 变化类型 | 实际可复用内容 | 双机器人适合程度及限制 |
|---|---|---|---|---|
| Learning to Adapt in Dynamic, Real-World Environments / GrBAL, ReBAL，ICLR 2019 | [论文](https://people.eecs.berkeley.edu/~ronf/PAPERS/anagabandi-iclr19.pdf)；[代码](https://github.com/iclavera/learning_to_adapt) | W/F | 元训练动力学、近期数据梯度/循环适应、MPC；源码同时有四足式 Ant 与 7DoF arm | 原理通用、基线价值高；TF1/MuJoCo131 很旧，移植成本高 |
| Deep Online Learning via Meta-Learning / MOLe，ICLR 2019 | [作者论文](https://arxiv.org/abs/1812.07671)；[ICLR 正式目录](https://iclr.cc/Downloads/2019) | W | 非平稳模型混合、旧情况召回、新情况创建 | 强相关先例；本轮未证实独立、完整、可运行的官方代码，不能当现成基座 |
| FAMLE，IROS 2020 | [论文](https://arxiv.org/html/2003.04663v2)；[代码](https://github.com/resibots/kaushik_2020_famle) | F/W（可配置连续执行） | 多个元学习 embedding、动力学适应、随机射击 MPC、5DoF reacher 与 Ant | 最直接的模型驱动故障基线；实机 Minitaur 演示不是 Go2-W；发布 reacher 随机故障标志实际被忽略 |
| Context-aware Dynamics Model / CaDM，ICML 2020 | [PMLR 论文](https://proceedings.mlr.press/v119/lee20g/lee20g.pdf)；[代码](https://github.com/younggyoseo/CaDM) | S/W（模型可持续推断） | 历史 context encoder、前向/后向预测损失、PETS/CEM、PPO 对照 | 适合 context 方法对照；TF1.15/Gym0.16；新机器人的环境仍需实现 |
| MOCA / Continuous Meta-Learning without Tasks，NeurIPS 2020 | [正式论文](https://proceedings.neurips.cc/paper/2020/hash/cc3f5463bc4d26bc38eadc8bcffbc654-Abstract.html)；[代码](https://github.com/StanfordASL/moca) | W（序列任务） | 可微 BOCPD、PyTorch ALPaCA、无分段元学习训练与测试 | 算法模块优秀，代码不是机器人闭环；避免把同类拼接称新算法 |
| ALPaCA，WAFR 2018 | [作者论文](https://arxiv.org/abs/1807.08912)；[代码](https://github.com/StanfordASL/ALPaCA)；[作者正式发表记录](https://web.stanford.edu/~jh2/CV.pdf) | C/S | 学习特征和贝叶斯线性回归先验，在线末层更新 | 轻量 residual 学习候选；原版不是专门处理反复突变，且无完整故障控制系统 |
| MBCD，AAMAS 2021 | [正式论文](https://aamas.csc.liv.ac.uk/Proceedings/aamas2021/pdfs/p97.pdf)；[代码](https://github.com/LucasAlegre/mbcd) | W | 概率动力学、CUSUM 型变化检测、SAC/模型库、非平稳 HalfCheetah | 变化检测与模型召回必要对照；默认 40000 steps 一换，不能推成亚秒级恢复 |
| PETS，NeurIPS 2018 | [正式论文](https://proceedings.neurips.cc/paper/2018/file/3de568f8597b94bda53149c7d7f5958c-Paper.pdf)；[代码](https://github.com/kchua/handful-of-trials) | C | 概率 ensemble、轨迹采样、MPC | 通用模型驱动基线，原版不含突然故障识别；模型误差与规划耗时需测 |
| MC-PILCO / Model-Based Policy Search Using Monte Carlo Gradient Estimation with Real Systems Application，T-RO 2022 | [机构论文与软件说明](https://shadow.merl.com/research/downloads/MC-PILCO)；[代码](https://github.com/merlresearch/MC-PILCO) | C/S | GP 动力学、Monte Carlo policy gradient、部分可测系统；公开 UR5 仿真跟踪 | UR 类机械臂参考价值高；Go2-W 高维接触迁移重，不是故障专用 |
| Plan2Explore，ICML 2020 | [正式论文](https://proceedings.mlr.press/v119/sekar20a.html)；[代码](https://github.com/ramanans1/plan2explore) | C | 无奖励世界模型探索、ensemble disagreement | 主动辨识/探索的先例；不是任务中故障恢复的现成实现 |
| Curious Replay，ICML 2023 | [正式论文](https://proceedings.mlr.press/v202/kauvar23a.html)；[官方入口](https://github.com/AutonomousAgentsLab/curiousreplay) | W/C | DreamerV2/V3 的兴趣/预测误差优先回放 | 处理新旧数据冲突的强基线；没有双机器人故障环境 |
| Learning to Walk from Three Minutes of Real-World Data / SSRL，CoRL 2024 | [官方代码](https://github.com/CLeARoboticsLab/ssrl) | S/C | 半结构动力学、策略训练；Go1 硬件代码另仓库 | 接触动力学相关；不是本轮优先深审（主线程已有审查） |
| SPI-Active，CoRL 2025 Oral | [正式论文](https://proceedings.mlr.press/v305/sobanbabu25a.html)；[项目](https://lecar-lab.github.io/spi-active_/)；[代码](https://github.com/LeCAR-Lab/SPI-Active) | S | Go2 物理参数采样辨识、Fisher Information 主动指令、下游 PPO | 有腿式实际系统；离线两阶段辨识，不是突然故障在线恢复；sim2real 尚在 TODO |
| Situationally-Aware Dynamics Learning，IJRR 2026 | [期刊](https://journals.sagepub.com/doi/abs/10.1177/02783649261431863)；[论文](https://arxiv.org/html/2505.19574v2)；[代码](https://github.com/AlejandroMllo/situationally_aware_dynamics_learning) | W | 多元 BOCD、情况聚类、条件概率 ensemble、MPPI；QuadX 数据、训练、评估 | 新且相关；论文 UGV 是车体速度指令，不是关节恢复；发布复现实例集中 QuadX |
| Learning on the Fly，RA-L 2026（2025-12 接收） | [正式接收版](https://rpg.ifi.uzh.ch/docs/RAL26_Pan.pdf)；[项目](https://rpg.ifi.uzh.ch/lotf/)；[代码](https://github.com/uzh-rpg/learning_on_the_fly) | W/S | 在线残差加速度学习、可微仿真 BPTT 更新策略、四旋翼 checkpoint | 在线优化方向的重要近期对照；可微刚体飞行换成轮腿接触并非简单改维数 |
| TAM / Torque Adaptation Module，CoRL 2026 Spotlight（作者项目确认） | [项目](https://dongwon-son.github.io/tam-project-page/)；[论文](https://arxiv.org/html/2606.06218v1)；[代码](https://github.com/Dongwon-Son/TAM) | S/W（历史适应） | 策略下方 torque residual、跨机械臂训练、未知负载、单机器人 finetune | 七类机械臂公开 preset，无 UR7e/Go2-W；低层桥接不公开；必须确认 torque 接口 |

### 未作为主基座的相关工作

- [Continual Robot Policy Learning via Variational Neural Dynamics](https://arxiv.org/abs/2606.27353)，2026：物理先验 + 条件残差、循环历史识别、反复风场恢复。作者 [发表列表](https://rudolfreiter.github.io/) 仍列 arXiv；不能仅因搜索结果出现 CoRL workshop 就写成正式 CoRL 主会。对“记忆已见变化比重新辨识快”的创新主张构成直接先例。
- [Efficient Domain-Adaptive Policy Learning via Kernel Representation](https://arxiv.org/abs/2606.13842)，2026：RFF 表达扰动、在线最小二乘、可微策略训练，quadrotor。当前只确认作者 arXiv；未确认官方完整代码，不选主基座。
- [Residual Model Learning for Microrobot Control](https://arxiv.org/abs/2104.00631)，ICRA 2021（[作者发表列表](https://taochenshh.github.io/)）：极少数据拟合残差作代理仿真器；不等于任务中突发故障恢复，本轮未确认完整官方训练环境。
- [PrivilegedDreamer](https://arxiv.org/abs/2502.11377)：有隐参数估计思想，但 [ICLR 2024 条目](https://openreview.net/forum?id=Y0wAim2F8A) 不能据“Under review”写成接收。未证实符合本次正式发表与代码门槛。

## 六项重点代码审计

### 1. GrBAL / ReBAL：真正可用的老基线，但升级旧栈会占时间

所读仓库树 SHA：`bd7d99ba402521c96631e7d09714128f549db0f1`。

- [run_grbal.py](https://github.com/iclavera/learning_to_adapt/blob/bd7d99ba402521c96631e7d09714128f549db0f1/run_scripts/run_grbal.py)：动力学元训练、采样器、MPC 串在一起；默认 `adapt_batch_size=16`，horizon=10，500 candidates，模型 512×3。删除 adapt_batch_size 可关闭 rollout 适应，便于消融。
- [arm_7dof_env.py](https://github.com/iclavera/learning_to_adapt/blob/bd7d99ba402521c96631e7d09714128f549db0f1/learning_to_adapt/envs/arm_7dof_env.py)：观测包含完整 qpos、qvel 与末端相对目标向量；`cripple_mask * action` 后进入动力学。`reset_task` 提供 cripple、damping、mass、force；不是视觉策略，也不需要文字指令。
- [HalfCheetah 环境](https://github.com/iclavera/learning_to_adapt/blob/bd7d99ba402521c96631e7d09714128f549db0f1/learning_to_adapt/envs/half_cheetah_env.py)：明确有执行器 mask，但默认 reset_task 在 episode reset 时调用。要做任务内突变需自己调度 `reset_task`，不能只跑默认训练脚本便称已经测过。
- [MPC](https://github.com/iclavera/learning_to_adapt/blob/bd7d99ba402521c96631e7d09714128f549db0f1/learning_to_adapt/policies/mpc_controller.py) 要求环境提供 `reward(obs, action, next_obs)`；换机器人需要可从预测状态计算的 reward。此处没有通用的黑箱奖励获取器。

迁移判断（推断）：算法与动作数无关，训练与规划成本会随 Go2-W 动作数和接触复杂度上升。UR7e 需要替换模型、状态及实际控制命令定义。论文已有真实 legged millirobot 适应，不代表完整硬件栈已在该仓库公开。

### 2. FAMLE：最贴近损伤，但是 README 的随机损伤标志不可信

所读树 SHA：`bbedd22a1eb6bba3cc0728fba5025b91186b6628`。

- T/E 有：`offline_data_collection/{reacher,ant}_env_adaptation.py`、`online_adaptation/{reacher_env_meta,ant_env_meta_v2}.py`、embedding 模型、随机射击规划器；有 reacher 的 `.pt`、轨迹和 mismatch 数据。树中未发现 Minitaur 实机部署栈。
- [Reacher 源码](https://github.com/resibots/kaushik_2020_famle/blob/bbedd22a1eb6bba3cc0728fba5025b91186b6628/fast_adaptation_embedding/env/reacher_env.py) 是 **12 维状态**：5 关节角（degree）、5 关节速度（radian/s）、EE xy；**5 维归一化速度命令**，乘 mismatch 后作为 PyBullet `VELOCITY_CONTROL` 目标，幅值限 0.7。末端二维目标不是 UR 三维任务。
- [适应脚本](https://github.com/resibots/kaushik_2020_famle/blob/bbedd22a1eb6bba3cc0728fba5025b91186b6628/online_adaptation/reacher_env_meta.py) 学 `[s,a] -> Δs`；根据近期预测误差选 embedding，并从该 prior 再拟合。默认50步一段，模型更新在整段执行之后。`--online` 才不 reset 物理状态；`--control_steps` 改段长，`--adapt_steps` 限历史。
- **关键发布缺口**：同脚本493–505行 `sample_mismatch` 硬编码 `[-1,1,1,0,1,0,0,0,0,0]`，`--rand_motor_damage` 打印“fault NOT used. Fixed damage for better comparision.”。所谓 online_damage_probability 即便触发，也再次赋同一个固定 mismatch；要实现健全→损伤→修复序列必须改调度代码。

论文的真实实验采用低维步态参数化，不应把其分钟量级 sample efficiency 等同于高维轮腿关节级亚秒恢复。作为**可复现 baseline**有价值；作为最新版完整双机器人基座则不够。

### 3. MBCD：应作为非平稳检测对照，不能借用名义上的“最小延迟”证明机器人恢复速度

所读树 SHA：`fc824b3eca720f8198ff2034c61f197521c29d70`。

- [mbcd_run.py](https://github.com/LucasAlegre/mbcd/blob/fc824b3eca720f8198ff2034c61f197521c29d70/experiments/mbcd_run.py) 提供训练入口；仓库还有 weights、logs、results。核心 [mbcd.py](https://github.com/LucasAlegre/mbcd/blob/fc824b3eca720f8198ff2034c61f197521c29d70/mbcd/mbcd.py) 用 `(obs,action,reward,next_obs,done)`，联合预测 next-state 与 reward 的分布，更新 context 指标；需要现有 SAC 学习器。
- [NonStationaryEnv](https://github.com/LucasAlegre/mbcd/blob/fc824b3eca720f8198ff2034c61f197521c29d70/mbcd/envs/non_stationary_wrapper.py) 默认 `change_freq=40000`。依次 normal、joint-malfunction、wind、velocity；joint-malfunction 是**前两个 action 反号**，不是锁死或扭矩失效。velocity 改 reward 目标，wind 对 body 施力；其检测问题既有动力学变化也有目标变化。
- wrapper counter 在 reset 中不归零，故有跨 episode 非平稳序列，但40000步恰可能落在固定 episode 边界；需要本项目随机时间点注入来证明 within-episode 性质。不要把其他 workshop 文本中的100步切换直接套到该正式发布默认配置。

迁移判断：可复用 detector/model bank，但 Go2-W 与 UR7e 的控制和仿真全部自己接。SAC 在线重新优化需要较多样本；检测快与恢复快是两个不同指标。作为完整本科主系统，风险高于固定策略加小适应模块。

### 4. Situationally-Aware Dynamics Learning：最近、模块清晰，但完整 UGV 论文复现仍有差距

所读树 SHA：`ee89506232d39629f02973e2109855866ff1c45e`。

- [核心 API](https://github.com/AlejandroMllo/situationally_aware_dynamics_learning/blob/ee89506232d39629f02973e2109855866ff1c45e/DOCS.md) 输入维数可配置，数据要求 `obs/actions/next_obs`；有 ensemble、situation identifier、训练、评估。代码内 `get_situation` 拼接旧状态、动作、状态差，产生 situation symbol；没有要求直接观测物理参数。
- [公开配置](https://github.com/AlejandroMllo/situationally_aware_dynamics_learning/blob/ee89506232d39629f02973e2109855866ff1c45e/src/config.yaml)：5模型、MPPI horizon16、population1024、2轮；4维 quadrotor action 范围为前三轴 ±3.14、第四轴0–0.8。数据路径仍是作者绝对路径，需修改。
- [环境](https://github.com/AlejandroMllo/situationally_aware_dynamics_learning/blob/ee89506232d39629f02973e2109855866ff1c45e/src/envs/windy_quadx_gates_env.py) 中确有 `SwitchingWindField`，按随机停留时间切换风况。发布树有3组 `.npz` buffer、prior CSV、QuadX 环境和 `train_quadx.py/evaluate_quadx_models.py`；没有观察到论文所有 UGV 训练场景、ROS 驱动和全部比较算法的完整复现脚本。
- [BOCD 实现](https://github.com/AlejandroMllo/situationally_aware_dynamics_learning/blob/ee89506232d39629f02973e2109855866ff1c45e/src/situationally_aware_dynamics/mbocd.py) 保留 run-length 历史、多元均值/精度及数据；不能未经 profiling 就宣称适合高频、长时间、几十维关节状态。

论文 UGV 使用车体姿态速度信息和2维线/角速度命令，其成功导航不证明底层关节失效恢复。可作为 change-aware forward model 的近期主对照；移植低维闭环响应比关节级世界模型更适合本科。

### 5. TAM：公开训练链丰富，但控制接口和接触归因是硬条件

所读树 SHA：`0cc882865c5509f7ba88690f792ea1368713cf7b`。

- [README](https://github.com/Dongwon-Son/TAM) 列出 data generation、多/单机器人训练、DAgger、mapping server、source-to-OSC 仿真评估，能观察到对应源码路径；不能把 shell 示例中的 checkpoint 路径视为模型已下载。树中未观察到 checkpoint 文件，应单独确认权重获取。
- [preset](https://github.com/Dongwon-Son/TAM/blob/0cc882865c5509f7ba88690f792ea1368713cf7b/src/simadaptor/tam/presets.py) 有 Panda、Piper、RBY-1、iiwa14、Google arm、Z1、Flexiv，**无 UR7e/Go2-W**。
- [部署契约](https://github.com/Dongwon-Son/TAM/blob/0cc882865c5509f7ba88690f792ea1368713cf7b/docs/deployment.md) 明说低层 robot controller bridge 不在仓库。fused history 需要 applied/base/residual 三路 torque，显式 `tau_base/tau_adaptor_delta`，4s attention 对应更大的 history buffer。其输出插入 nominal controller 之后、robot torque 之前。
- DAgger fine-tuning 在仿真中使用解析 teacher torque，**不是实机在线监督更新**。执行时历史 encoder 更新隐状态，不等于模型权重持续学习。

论文局限明确要求可用的理想 inverse torque-command map、匹配运动学和 actuator 顺序；新接触/外力可能被误判为机器人自身 mismatch；无长时稳定性保证。Go2-W 的浮动基座与轮地接触需扩展。UR7e 能否访问所需 torque 接口必须由实际控制版本核实，不能从 Panda torque 部署反推。

### 6. Learning on the Fly：有在线模型和策略更新，难点是两种目标机器人缺少同等简单的可微模型

- 正式 [接收版](https://rpg.ifi.uzh.ch/docs/RAL26_Pan.pdf) 标明 accepted December 2025，RA-L 2026，不应仅按早期 CoRL2025 workshop 版本分类。
- [仓库](https://github.com/uzh-rpg/learning_on_the_fly) 有 JAX/Flax 模型、BPTT、hovering/tracking state/features 环境、高保真 rotor augmentation、pretrained policy/residual checkpoint。所读压缩包文件清单含 examples，但完整硬件 ROS 节点是否全部发布本轮未证实。
- [ResidualDynamics 源码](https://github.com/uzh-rpg/learning_on_the_fly/blob/master/lotf/utils/residual_dynamics.py) 硬编码 MLP `[19,128,128,3]`，输出3维残差。不是现成任意DoF机器人模型。环境 [README](https://github.com/uzh-rpg/learning_on_the_fly/blob/master/lotf/envs/README.md) 的 state-based observation 是 `p,R,v`，features模式用视觉历史与过去动作。
- [项目](https://rpg.ifi.uzh.ch/lotf/) 说明 residual acceleration 来自实测与解析预测之差，再对 hybrid simulator 反传更新策略；其更新5s和完整初期恢复所需时长应分别统计，不可直接宣称故障5s内恢复。

迁移判断（推断）：UR 的闭环 servo 响应可拟合或构造简化模型，但要验证求导模型与真实接口一致。Go2-W 可微接触、轮胎摩擦和失效关节带来的非光滑性是大工程，不能简单换XML。若本科周期有限，把它留作算法启发或离线 baseline，而非首选主基座。

## 补充：SPI-Active 的“主动”与任务中双重控制并不等价

作者 [项目](https://lecar-lab.github.io/spi-active_/) 是两阶段：收集轨迹辨识参数，再优化 informative command、重新收集、再辨识与训练下游策略。它有主动辨识思想，但不是在遭遇故障的那一秒边完成任务边辨识并恢复。

[active_sysid.md](https://github.com/LeCAR-Lab/SPI-Active/blob/main/active_sysid.md) 写明先训练 omni 控制器10000 iterations；优化25s指令序列、5s分段，用 CMA-ES/FIM，1024并行环境。文档第三、四步（用优化指令采集与后续流程）仍有“Stay tuned”。[README](https://github.com/LeCAR-Lab/SPI-Active) 的 Sim2real、Dataset Replay/Visualize TODO 未勾选。已发布 sampling SysID、active exploration、downstream task training 有实质代码，但闭环硬件复现不完整。UR7e 没有对应资产和 controller。

## 建议课题收敛（研究建议，非已验证创新）

### 优先候选：具有变化归因和动作权限约束的运行中适应

**问题**：仅依靠历史误差，执行器效率下降、突然负载、正常接触/短暂外力可能难区分。把它们都压进一个 residual，可能使控制器对无法恢复的执行器持续增大命令，或错误抵消任务需要的接触。

**最小系统**：每个机器人分别训练 nominal/recovery policy；使用统一小型历史 encoder + 低维效率/外力（或闭环响应）隐变量；带 confidence 的变化检测选择保留、缩短或清空历史；输出有限幅度 action correction，或为已有策略提供 context。既不要求共享一套权重，也不要求机器人具有相同关节数。

**可作为论文贡献的必要增量**：不是简单 BOCPD reset，而是控制相关的故障/扰动辨识与可恢复性估计，展示在相同 detection delay 下，避免错误归因如何改善恢复时间和约束违反。若没有方法上的增量，双平台评测可作为本科完整成果，但不承诺主会论文。

**关键可辨识性检查**：若整个动作历史中某关节命令始终接近零，不能从被动观测可信地区分其效率0.3与1.0；先检验激励/coverage，而不是只画 latent 聚类。低维无接触 arm 与轮腿接触条件下分别建立 matched disturbance，使“效率改变”和“外力改变”的短窗预测误差相近，再看归因是否仍成立。

### 降一级工作量的备选：变化感知的闭环响应模型 + 固定策略

在不修改名义低层控制器的前提下，学习“命令→可测下一状态”的小残差模型。优先用 FAMLE / CaDM / SADL 思想做短窗 context，冻结控制策略，比较固定历史、可变历史、oracle boundary。可实现且便于找出真正痛点；但检测/重置本身创新有限，需要诚实定位为基准或工程研究。

### 本科阶段不建议作为主线的组合

- 同时做通用 contact world model、在线 BPTT 更新策略、未知故障诊断和双机器人实机；
- 用未知是否可用的 torque API 作为 UR7e 项目前提；
- 把 Go2 普通四足 checkpoint 直接当作 Go2-W；
- 只在 reset 前采样参数，然后声称是突发故障恢复；
- 把 model adaptation time、训练用交互时间、恢复到任务阈值时间混为一项。

## 可审阅的实验协议

1. **明确硬件/模拟动作契约**：Go2-W 的腿关节目标和轮速度分别是什么，UR7e 是关节位置/速度/torque；故障插在哪个层级。为每种干预写出数学映射。
2. **训练只在一部分范围和组合**，保留未见效率幅度、故障关节、负载、切换时间及两次反复切换作为测试。任务/命令变化和物理变化分别报告。
3. **故障时间在中段随机**，不 reset，仿真状态连续；至少含 healthy→fault、fault→repair、faultA→faultB。严重到不可恢复的情况单列，不应通过提前终止剔除。
4. **对照**：robust DR policy、history recurrent policy、oracle fault/context、固定窗适应、无变化检测、MOCA/MBCD式检测或 SADL、相同算力的 residual adaptation。若用模型规划，保持模型容量、候选数、更新频率和数据量可比。
5. **度量**：变化后0–1/1–3/3–10s累计跟踪误差；任务成功率；进入并持续满足误差阈值的恢复时间；跌倒/限幅/保护停止；误报率、检测延迟；在线计算时间和最坏值。机械臂不能只看 EE误差，轮腿不能只看速度均值。
6. **消融**：oracle变化点、固定/自适应历史、仅效率/仅外力、无confidence gating、无动作约束；明确参数适应或 latent inference 是否在测试时更新。

## 后续重点增补：OCCAM、NeuralActuator 与两项排除

以下为主线程系统扫描正式论文集后提出的补充候选，逐项检查后加入，不与前面16项混算成同等完成度。

### 7. OCCAM：层级控制参数适应是双平台较现实的备选，但不是关节故障恢复现成系统

正式出处：[CoRL 2024 Oral 项目](https://hersh500.github.io/occam/)，[PMLR 卷270记录](https://proceedings.mlr.press/v270/sanghvi25a.html)的出版年份2025是论文集年份。仓库 SHA `f0d3afb3b9369d19b3ed3cd20408c88628296b02`。

其模型预测未来一段时间的**性能指标**而非逐步状态转移。输入是近期传感器/控制历史、任务编码、拟尝试的控制参数；元学习 basis 的最后线性层用 Kalman regression 在线更新，随后采样优化下一组参数。[论文](https://arxiv.org/html/2406.17620v2) §5.1/附录D.4：四足冻结 Walk These Ways 策略以50Hz输出关节角，上层每3s选择8维行为参数（步频、身高、摆腿高度、站宽、步态相关变量），典型适应10–20s；不是直接输出车体差速命令。附录I明确有 Crazyflie **实验中途**加5g质量的实机试验，但未找到同等四足中途关节失效证据。

静态源码证据：

- [mob_locomotion.py](https://github.com/Hersh500/occam/blob/f0d3afb3b9369d19b3ed3cd20408c88628296b02/learned_ctrlr_opt/systems/mob_locomotion.py#L117) `Go1BehaviorParams` 类定义10个总候选行为参数，再按 `gains_to_optimize` 取子集；因此源码总空间10维与论文所选8维并不冲突。`evaluate_x` 把参数写入底层策略 commands；训练历史记录18维 base velocity + joint torque 信息。
- [mob_kf_runner.py](https://github.com/Hersh500/occam/blob/f0d3afb3b9369d19b3ed3cd20408c88628296b02/learned_ctrlr_opt/eval/mob_kf_runner.py#L26) 加载网络/scaler/test set，按 `eval_length_s * 50` 取连续轨迹；逐段 random search、执行、得到 performance、再 Kalman step。在线只有最后线性权重更新，不重训整个低层 locomotion policy。
- [basis_kf.py](https://github.com/Hersh500/occam/blob/f0d3afb3b9369d19b3ed3cd20408c88628296b02/learned_ctrlr_opt/meta_learning/basis_kf.py) 有递推和可微元训练；[train_basis_net.py](https://github.com/Hersh500/occam/blob/f0d3afb3b9369d19b3ed3cd20408c88628296b02/model_training/train_basis_net.py)、[data generator](https://github.com/Hersh500/occam/blob/f0d3afb3b9369d19b3ed3cd20408c88628296b02/dataset_generation/generate_mob_loco_data.py) 与 eval runner 均存在。
- [README](https://github.com/Hersh500/occam) 承认API清理和文档仍在进行；requirements 混合了不少开发依赖并指定外部 rotorpy git版本。底层四足策略依赖外部 Walk These Ways，不能把仓库存在视为一个命令即可复现。
- [mob_locomotion.py](https://github.com/Hersh500/occam/blob/f0d3afb3b9369d19b3ed3cd20408c88628296b02/learned_ctrlr_opt/systems/mob_locomotion.py#L219) 关闭多项额外随机化，其中 `randomize_rigids_after_start=False`。默认公开四足流程仍须核实/增加任务内物理切换。

**Go2-W迁移（推断）**：需要具有可调步态/轮腿协调/身高/轮速分配的 Go2-W 低层控制器；普通 Go1 policy 没有轮子，不能沿用其行为空间。轮腿接触模式切换速度可能快于3s性能窗，需要可变短窗或快速事件响应层。不能把它降成2D差速小车来声称完成轮足故障恢复。

**UR7e迁移（推断）**：算法可调轨迹速度缩放、servo增益、前馈/残差参数或恢复策略context；UR接口未必开放内部PID增益，不应直接照搬quadrotor PD tuning。先选择实际可控的外层参数。若全部只调3–8个轨迹参数，和Go2-W关节级缺损恢复的难度不对等，须在结论中限制范围。

结论：OCCAM比通用可微世界模型更适合本科实现；但严重关节失效会改变可控性，单靠改变名义控制器参数未必覆盖新的恢复动作，必须加入可恢复性/策略权限实验。

### 8. NeuralActuator：发布资料完整，但“前向模型”与在线控制的适用范围非常重要

正式出处：[RSS2026 p159](https://roboticsproceedings.org/rss22/p159.html)；[作者项目](https://people.csail.mit.edu/frankzydou/projects/NeuralActuator/index.html)。官方代码路径是 [Frank-ZY-Dou/Dynamics-Modeling/NeuralActuator](https://github.com/Frank-ZY-Dou/Dynamics-Modeling/tree/main/NeuralActuator)，不是猜测的 frankzydou/NeuralActuator（该GitHub地址404；同名Hugging Face地址确实存在）。本次 SHA：`541a93aac4368e73883e86a51f31a7add6bde059`。

论文/项目明确：历史含命令、q/qdot、跟踪误差和 current/effort、voltage、temperature，Transformer输出 simulator-equivalent torque surrogate、3D末端外力、contact gate及condition score。torque surrogate通过pose rollout监督；**force/gate/condition使用直接标签**。condition实验只监督 OpenManipulator-X 的 Joint3，用橡皮筋施加受限工况，不能扩大为所有关节、未知故障类型或真实电机损伤诊断。Franka只做离线payload-force估计。

必须保留的适用范围区分：

1. **多步记录回放不等于候选动作预测**。未来时间步的current/effort来自记录轨迹；网络没有预测“若换成未执行过的命令，电流会怎样”的 effort-response 子模型。论文 §III-D 与结论明确这样定义，合法用于 recorded-telemetry-conditioned rollout / 当前外力估计，但不能直接放入 MPC 比较候选动作序列。见 [infer_actuator.py](https://github.com/Frank-ZY-Dou/Dynamics-Modeling/blob/541a93aac4368e73883e86a51f31a7add6bde059/NeuralActuator/infer_actuator.py#L455)：455–472行逐时刻从记录取 currents/volts/temps；[同文件](https://github.com/Frank-ZY-Dou/Dynamics-Modeling/blob/541a93aac4368e73883e86a51f31a7add6bde059/NeuralActuator/infer_actuator.py#L56) 56–63行在rollout中只替换模拟q、qdot与误差，保留其余CSV telemetry。
2. **Franka有更明确的offline command proxy**。[evaluate_actuator_franka.py](https://github.com/Frank-ZY-Dou/Dynamics-Modeling/blob/541a93aac4368e73883e86a51f31a7add6bde059/NeuralActuator/evaluate_actuator_franka.py#L121) 121–134行、[train_actuator_diffsim_franka.py](https://github.com/Frank-ZY-Dou/Dynamics-Modeling/blob/541a93aac4368e73883e86a51f31a7add6bde059/NeuralActuator/train_actuator_diffsim_franka.py#L64) 64–71和117–124行，用 `pos[t+5] * 1.03` 构造平滑命令代理。作者清楚标明是 future-state-conditioned offline benchmark。在线需要用当时真正可得的命令替换；不能直接把其离线精度移用于UR7e在线部署。这里是实验协议的适用范围，**不是对研究不当行为的指控**。
3. **surrogate不是可辨识物理电机转矩**。默认implicit force coupling只把surrogate作用于模拟body，外力头独立监督不进入状态更新，故surrogate可吸收接触/负载和模型偏差。显式外力路径也有，但更易受惯量、坐标/标定误差影响。不能从surrogate直接推断“效率参数”而不加辨识约束。

发布核验：有 [train/eval/infer及11权重说明](https://raw.githubusercontent.com/Frank-ZY-Dou/Dynamics-Modeling/541a93aac4368e73883e86a51f31a7add6bde059/NeuralActuator/README.md)、OMX/SO101 teleop与硬件数据采集、MJX/Newton等backend、[数据格式](https://github.com/Frank-ZY-Dou/Dynamics-Modeling/blob/541a93aac4368e73883e86a51f31a7add6bde059/NeuralActuator/docs/dataset.md)。权重分开在作者HF/Release下载，不在代码树内。训练力传感标签或已知砝码仍需要收集，部署无F/T传感器不等于训练无力标签。

评估限制：dataset.md 15–16行写明val/test多为相同commanded trajectory的重复执行；README说明发布numbers多数选择`best_test` checkpoint，condition选择`best_train`。这要求本项目另外保留未用于选择的独立任务/故障测试集，不把其发布指标视为严格跨任务或未触碰测试集结果。没有运行重现，不判断指标是否偏移了多少。

**双平台结论**：UR7e可考虑复用current/effort history→当前外力/context估计模块，但需重采数据、真实命令、标签和机器人闭环模型；Go2-W浮动基座/多个轮地接触不由单一EE 3D合力描述，需要扩展结构和标签。它是模型/感知模块，不是现成RL运动恢复控制器。

### Feedforward Compensation：正式发表，但发布代码不是机器人恢复闭环

[CoRL2023正式记录](https://proceedings.mlr.press/v229/abuduweili23a.html) 的理论针对慢时变系统，用memory buffer关键样本改善预测。官方 [intelligent-control-lab/Feedforward_Adaptation](https://github.com/intelligent-control-lab/Feedforward_Adaptation) 的 [adapt.py](https://github.com/intelligent-control-lab/Feedforward_Adaptation/blob/main/adapt.py) / train.py入口是ETTh1电力、illness、exchange时序预测；看到了预测训练与适应，未看到Go2/UR环境、动作控制或恢复评估。可作为“如何选择历史样本”的参考，不能为了大会标签而推荐为机器人主基座。

### RL2AC：正确的适应控制强基线，但本轮未确认完整官方代码

[RSS2024正式记录](https://roboticsproceedings.org/rss20/p060.html) 是RL策略叠加解析在线torque补偿，1000Hz运行、无须与RL同步训练；重载、单腿扰动、侧向力矩等实验对“冻结策略+适应层”的路线很 relevant。定向搜索未确认完整官方 train/env/deploy 仓库，不能与已逐文件检查的FAMLE/OCCAM同级推荐。也没有证据其在UR位置接口直接成立；torque compensation仍有接口前提。

### 参考链补充：T-MCL / PDML 不能只看名称便当非平稳故障方法

- [T-MCL官方代码](https://github.com/younggyoseo/trajectory_mcl)，NeurIPS2020：multi-headed动力学，在测试按近期预测误差选择head，含 cripple_ant训练入口，是FAMLE/MOLe之间有价值的模型选择对照；TF旧栈。下一步应检查任务内head切换与参数采样时刻，而不从“cripple”名字推断已覆盖突然损伤。
- [PDML正式论文](https://proceedings.mlr.press/v202/wang23an/wang23an.pdf)，ICML2023：[作者代码](https://github.com/si0wang/PDML)。它处理的是**策略演化导致的state-action visitation shift**，并重加权历史策略数据；不是直接处理物理动力学突然变更。可作为replay分布偏移对照或启发，但不能替代故障适应方法。

## 第二轮细审：SADL 的最小修复范围与方法价值

2026-11-21 12:09 UTC 后恢复研究。此前中断时间未计为研究用时。本节优先级高于早先“代码结构清楚”的初步印象。固定仓库SHA仍为`ee89506232d39629f02973e2109855866ff1c45e`。

### 确定的发布版程序/评估接口问题（与论文贡献分开）

| 定位及证据 | 严重性与最小修复 | 对可复现性结论的影响 |
|---|---|---|
| [trainer.py L17](https://github.com/AlejandroMllo/situationally_aware_dynamics_learning/blob/ee89506232d39629f02973e2109855866ff1c45e/src/trainer.py#L17)调用`agent.eval()`，L49调用`agent.train()`；[Agent L10](https://github.com/AlejandroMllo/situationally_aware_dynamics_learning/blob/ee89506232d39629f02973e2109855866ff1c45e/src/situationally_aware_agent.py#L10)是plain class，完整AST方法表无这两方法，QuadX子类也没有 | 小补丁：加入两个模式切换代理方法，设置is_training，并遍历ensemble和sa切换train/eval | 当前版无法保证原样跑完首次评估；不等于缺失trainer或需要重写算法 |
| [Agent L37–39、L146–153](https://github.com/AlejandroMllo/situationally_aware_dynamics_learning/blob/ee89506232d39629f02973e2109855866ff1c45e/src/situationally_aware_agent.py#L146)初始化val buffer但从未向它add，learn回退用training buffer作val；[gaussian_mlp.py L245–262](https://github.com/AlejandroMllo/situationally_aware_dynamics_learning/blob/ee89506232d39629f02973e2109855866ff1c45e/src/situationally_aware_dynamics/gaussian_mlp.py#L245)按该MSE做earlystop和bestepoch | 评估协议补丁：按独立轨迹切分train/validation并真正填充val buffer；不改变模型目标 | 发布版所称`valloss`实际可能是训练buffer重复误差，不能直接当held-out prediction泛化；不能据此推断原文所有单独评测都不存在 |
| [evaluate_quadx_models.py](https://github.com/AlejandroMllo/situationally_aware_dynamics_learning/blob/ee89506232d39629f02973e2109855866ff1c45e/src/evaluate_quadx_models.py)硬编码只评估d3，默认config训练d2 | 小配置补丁：从cfg.task取任务或显式参数化 | 不足以否定算法；须校准训练与评估路径 |
| [trainer.py L27](https://github.com/AlejandroMllo/situationally_aware_dynamics_learning/blob/ee89506232d39629f02973e2109855866ff1c45e/src/trainer.py#L27)只reset env，没有reset agent历史；Agent的_previous_obs、previous_action、BOCD等持续保留 | 协议选择：明确是否评估跨episode记忆；若独立episode，增加reset hooks且保留/清除situation库要分开 | 不能把episode边界的人为状态跳变误当物理变化；在线多episode基线必须公平 |
| environment.yml虽有PyFlyt、mbrl等，却没有显式Torch安装项；多个`.to('cuda')`硬编码，包括situation identification、controller | 安装/设备配置小修复；GPU路线先固定Torch/CUDA版本；CPU不是只改`device=cpu`即可 | 当前Windows工作区不意味着可直接安装运行，建议隔离Linux GPU环境；本轮未安装或尝试训练 |

### 需要先解决的动作契约不一致（静态链推断，不冒充运行结果）

本轮在内存读取作者公开`d1_wind_quadx.npz`（20,119,169 bytes），确认键为obs/actions/next_obs/rewards/dones；100000条，obs和next_obs为15维，actions为4维，**四维actions的实际范围都约为[-1,1]**。prior CSV为256×28、所有元素有限、协方差rank28，未发现零方差输入这一类简单问题。

[QuadXSAAgent](https://github.com/AlejandroMllo/situationally_aware_dynamics_learning/blob/ee89506232d39629f02973e2109855866ff1c45e/src/quadx_sa_agent.py#L86)把MPPI normalized候选直接送给模型，学习也直接使用NPZ动作，因此这两端在normalized空间是一致的。但是[执行端L137–142](https://github.com/AlejandroMllo/situationally_aware_dynamics_learning/blob/ee89506232d39629f02973e2109855866ff1c45e/src/quadx_sa_agent.py#L137)先unnormalize，再交env，并把unnormalized动作写入previous_action。这样 **SA训练历史中的动作与执行时SA历史中的动作单位不同**。normalized模型候选与physical env动作经过明确边界映射，本身属于正常adapter设计，不能单独据此判错；可疑点是SA上下文的编码在离线数据与在线历史之间不一致。

应选择一种明确契约：A) 模型和SA始终保存normalized动作，仅env adapter反归一化；B) 数据加载、模型、SA、规划都用physical动作。改动是动作编码/边界映射的一致性补丁，不需要改BOCD、模型结构或MPPI核心。发布数据的原始采集器未见于仓库，需额外确认NPZ动作究竟在哪层生成。这里不推断论文原始实验是否使用同一版代码。

### 任务内风突变的默认配置不成立

作者 [env_factory.py L20–53](https://github.com/AlejandroMllo/situationally_aware_dynamics_learning/blob/ee89506232d39629f02973e2109855866ff1c45e/src/utils/env_factory.py#L20)设d1/d2风况停留15–45s，d3为10–50s，未传`max_duration_seconds`。本轮直接读取**配置指定PyFlyt0.29.0的官方source distribution**并与tag核对：tag SHA `0ac436c5eb9537dafe8f78b8556fa9996b5ffdc9` 的 [QuadXGatesEnv L53](https://github.com/jjshoots/PyFlyt/blob/0ac436c5eb9537dafe8f78b8556fa9996b5ffdc9/PyFlyt/gym_envs/quadx_envs/quadx_gates_env.py#L53)默认episode10s、40Hz；[BaseEnv L121](https://github.com/jjshoots/PyFlyt/blob/0ac436c5eb9537dafe8f78b8556fa9996b5ffdc9/PyFlyt/gym_envs/quadx_envs/quadx_base_env.py#L121)据此设置max_steps。初始化只预热10个内部step，无法补足d1/d2的15s切换。

因此发布默认d1/d2评估基本在第一次风切换前结束；不能仅看有`SwitchingWindField`类就称默认评估测了任务内风突变。最小修复是延长episode并设置明确的切换计划/随机切换时间日志，增加足够的变化后恢复观察窗。这是**新评测协议**，不等于重写SADL原算法。

补充原文交叉核验：[IJRR作者最终稿v3 §6.1 Table4](https://arxiv.org/html/2505.19574v3)标明15–45、10–50的单位是**steps**；发布[SwitchingWindField L318–319](https://github.com/AlejandroMllo/situationally_aware_dynamics_learning/blob/ee89506232d39629f02973e2109855866ff1c45e/src/envs/windy_quadx_gates_env.py#L318)却明确`min/max_duration`为seconds，L354–375与simulator time比较。因而更贴近原文的最小修复是明确step指agent还是physics step并统一时间单位，而不是直接随意延长episode。代码与原文时间单位差异应作为复现待确认项，不外推论文指标不成立。

另一个方法边界：[最终稿§4.1.1](https://arxiv.org/html/2505.19574v3)明确测试固定situation library，只对新transition找best-match；[situation_identification.py L240](https://github.com/AlejandroMllo/situationally_aware_dynamics_learning/blob/ee89506232d39629f02973e2109855866ff1c45e/src/situationally_aware_dynamics/situation_identification.py#L240)也只有`is_training`时建新簇。因此SADL测试“适应”主要是**在线context推断，非在线学习全新故障动力学**。未知故障可近似匹配已有簇，但若需要真正新簇+模型更新，应明确是额外扩展。默认support40、每2动作更新，在40Hz下建立新簇至少约2s的采样预算（仅针对新簇支持量，不能将其等同已知簇识别延迟）；需为更快故障反应设计单独通道。

### 方法仍可保留，但双机器人迁移比修上述小问题大

SADL的变化识别核心不要求机器人形态，若输入可测的关节/车体状态与已执行动作，它可以在Go2-W与UR7e分别学习。可是原文UGV的2维速度命令与QuadX的4维角速度/推力，都没有解决Go2-W的腿关节+轮速度协同及接触切换，更没有机械臂失效后任务可达性的改变。新增两个环境、奖励、动作映射与故障时间调度属于机器人适配，而非文档补丁。建议把它作为**变化感知模块/对照**，保留现成PPO闭环，而非直接把公开QuadX MPPI改成16维轮腿动作搜索。

## 第三轮新增正向候选：FADA 与完整任务推断方法

2026-11-21 14:48 UTC续查；12:24左右至14:47的中断不计研究时间。以下补充针对“确实能拿来做什么”，而非仅列缺点。

### FADA：现代、实际完整的执行适配基座，已经有机械臂原理验证

[论文全文v2](https://arxiv.org/html/2606.28476v2)；[官方仓库](https://github.com/LeCAR-Lab/FADA)，README标CoRL2026；固定SHA `290b3a9c5c0ebe2e9851b61350617544be05e9bc`。这是本轮新增最值得保留的**完整现代训练工程**。流程确有：privileged PPO oracle、Planner–IDM DAgger、目标域H5数据收集、只更新IDM的LoRA、评估与ONNX部署。实际查询[作者Hugging Face模型树](https://huggingface.co/AngchenXie/fada-checkpoints/tree/main)，可见G1与T1逐100迭代的oracle `.pt`文件，每个约8 MB；不是只有空下载占位。尚未核验所有文件下载及加载。未见Go2-W、UR或论文固定臂诊断任务的专属配置/资产。

I/O及闭环证据：

- [compact_obs.py L8](https://github.com/LeCAR-Lab/FADA/blob/290b3a9c5c0ebe2e9851b61350617544be05e9bc/src/holosoma/holosoma/fada/common/compact_obs.py#L8)：发布主线token为base angular velocity、joint position、joint velocity、projected gravity。planner另接task command；IDM接observation/action history。关节力矩、电流、真实损伤标签均不是部署输入前提。
- [config.py L79](https://github.com/LeCAR-Lab/FADA/blob/290b3a9c5c0ebe2e9851b61350617544be05e9bc/src/holosoma/holosoma/fada/planner_idm/config.py#L79)：history30步、预测6步；主线128维、4头、planner/IDM encoder各3层、IDM decoder2层。planner预测未来自身感觉intent，IDM输出动作chunk，每步仅执行第一动作并重新查询。
- [locomotion_fada.py L883](https://github.com/LeCAR-Lab/FADA/blob/290b3a9c5c0ebe2e9851b61350617544be05e9bc/src/holosoma_inference/holosoma_inference/policies/locomotion_fada.py#L883)取chunk第一动作，L901–904保存raw历史并乘scale；[locomotion.py L918](https://github.com/LeCAR-Lab/FADA/blob/290b3a9c5c0ebe2e9851b61350617544be05e9bc/src/holosoma_inference/holosoma_inference/policies/locomotion.py#L918)形成`q_target=scaled_action+default_q`，L994送低层。因而是关节位置目标上的闭环执行适配，不是直接电机转矩策略。
- [locomotion_fada.py L163–174](https://github.com/LeCAR-Lab/FADA/blob/290b3a9c5c0ebe2e9851b61350617544be05e9bc/src/holosoma_inference/holosoma_inference/policies/locomotion_fada.py#L163)明确ONNX中`teacher_future_obs`仅为teacher指标分支，部署零占位；实际policy使用planner预测future。不要因名称含teacher/future就误判有部署未来信息。

**最有用的正向证据**：论文§5.7额外用7DoF固定臂追踪Cartesian目标，腕负载0/2.5/5 kg；训练只随机0–1.5 kg，用以分离目标运动学与执行动力学。它说明Planner–IDM原理不只适用于腿式身体。这不是UR7e实机结果，也不是突然关节失效实验。

**边界精确限定**：论文§3明定固定target condition；Appendix B.3明确全部数据收完后**一次离线800步、batch4096**微调，无在线迭代更新。2分钟指数据预算，不是故障后恢复延迟或总微调耗时。论文也明确要求非灾难性的zero-shot能力，IDM仍可能含任务结构。

**双平台适配工作（推断）**：UR7e可把planner command换成目标/轨迹，将固定base项去除或常量化，以真实servo position command为动作重训oracle与student；外部关节位置命令是较合适的共同接口，不要求开放内部torque。Go2-W必须把leg position与wheel velocity作为不同动作通道，轮角周期状态应使用sin/cos或省去无意义绝对角，重新定义预测intent和action scaler。现成代码默认`q_target`全位置偏置，因此轮速adapter是**机器人接口扩展**，不只是改维数。两者仍需自己的任务、oracle、domain randomization与数据集；模型本体可复用。

**有边界的创新方向**：从固定目标域一次校准，扩展到任务内突变时的快速执行适配，比较短窗context、变化触发LoRA和固定域LoRA；在严重损伤下增加intent可实现性约束。这不是“加LoRA”即可，既有FADA已经做LoRA；关键问题是漂移/突变时数据窗口污染、稳定性与恢复后的记忆。若本科工期紧，先将它作为固定域执行适配基线，不把三阶段全工程同时迁移两身体当低风险主线。

### TIGR / MoSS / MELTS：任务推断类必须区分奖励变化与物理故障

[TIGR作者正式稿](https://mediatum.ub.tum.de/doc/1710825/document.pdf)，TNNLS DOI 10.1109/TNNLS.2023.3270298（online2023，卷期2024）：recent transition sequence含state/action/**reward**/next-state，经GMM VAE和GRU推断context，再条件化SAC。论文具任务内切换，但主要是速度、方向、站立、跳跃等任务/目标切换。全文只发现ProMP基线GitHub链接，未定位独立官方完整TIGR仓库；不能当已核验完整代码。

[MoSS AAAI2023正式论文](https://ojs.aaai.org/index.php/AAAI/article/download/26210/25982)与[作者全文](https://arxiv.org/html/2305.00286)：明确每100步、概率0.5改变goal velocity/direction，episode延长至500/600步；GRU逐步更新，GMM与对比学习训练latent。**这些非平稳实验改变奖励目标，并非电机效率突然下降。**其对比学习在非平稳任务关闭，以免同episode不同task的样本关系错配；这已经是“变化时避免历史样本污染”的已有处理，不能把该概念本身当创新。定向搜索未定位作者完整代码，不混淆同名ICLR2025视觉语言MoSS仓库。

[MELTS官方仓库](https://github.com/Ghiara/MELTS)确为[TPAMI2024论文](https://doi.org/10.1109/TPAMI.2024.3386780)官方实现；SHA `2703810b730cecc34d2d56a6f414a573ad656617`。主程序、SAC、DPMM-VAE、replay、train/showcase、环境源码与作者Drive权重链接存在。DPMM以任务自发现避免预先固定类别数，故“动态增加故障簇”也已有近邻。旧栈为Ubuntu18.04、MuJoCo200/131、Torch1.7/CUDA11，需要兼容性迁移。

实际源码核验：

- [rollout_worker.py L142](https://github.com/Ghiara/MELTS/blob/2703810b730cecc34d2d56a6f414a573ad656617/tigr/rollout_worker.py#L142)context形状为`T×(obs+action+1+next_obs)`，L175每步更新，L291–305滑窗；c8配置T=16。`true_task`存日志，但policy接context，不意味着部署可知真实task。
- [NonStationaryMetaEnv L65](https://github.com/Ghiara/MELTS/blob/2703810b730cecc34d2d56a6f414a573ad656617/submodules/meta_rand_envs/meta_rand_envs/base.py#L65)支持time/location触发；[HalfCheetah任务类L25](https://github.com/Ghiara/MELTS/blob/2703810b730cecc34d2d56a6f414a573ad656617/submodules/meta_rand_envs/meta_rand_envs/half_cheetah_non_stationary_multi_task.py#L25)先check再step，change_active_task主要换reward objective，不是改变身体。
- 发布树还含[AntCrippleEnv L22–30](https://github.com/Ghiara/MELTS/blob/2703810b730cecc34d2d56a6f414a573ad656617/submodules/meta_rand_envs/meta_rand_envs/ant_cripple.py#L22)：100步后每步0.01概率禁用一腿两action，并在`cripple()`同时缩小/移动几何。这是**确实存在的任务内物理变化代码**；但不能冒称论文主表已评测。该旧wrapper的reset_task签名没有worker调用的keep_buffered参数，返回info也没有worker需要的true_task，需接口适配；且未见该任务的现成主训练配置。这是“环境存在、与主线未完整接通”，和完全没有trainer不同。

**可用定位**：MELTS比TIGR/MoSS更适合作完整context-SAC对照；将故障参数保持为训练监督/日志而不输入policy，采集可在线计算的reward与状态历史，重新连接两robot Gym环境即可。对Go2-W高吞吐PPO基座，直接移植全套旧SAC栈未必划算；优先复用DPMM/短窗推断思想，保留各机器人PPO闭环。UR位置跟踪reward可由当前目标与q/FK计算，因此reward作为部署输入原理上可得，但必须明确时序，不能用真实隐含故障类别算reward。

## 本轮审计限制

这是网页、静态源代码与发布数据schema审查；没有训练复现、算力测量、真实控制接口检查。GitHub API 曾限流，后续直接读取作者raw文件或内存中的仓库zip；未安装任何包，也未把仓库克隆到工作区。没有证据的权重、硬件节点与特定任务脚本均未视作已发布。研究难度与发表可能性属于基于以上约束的判断，不能当成可保证的工期/录用预测。
