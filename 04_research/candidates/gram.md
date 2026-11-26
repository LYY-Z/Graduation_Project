# GRAM 精读与代码审查

说明：页码为论文印刷页码（PDF 第 8 页即印刷 p.6）。代码路径相对 `gram/`（浅克隆，只读，未安装未运行）。带"【推断】"的是读代码或凭记忆得出、未实机核实的内容。

## A. 论证链抽取

| 项 | 内容 |
|---|---|
| 出处/单位 | IEEE RA-L 2026, vol.11 no.2, pp.2218-2225, DOI 10.1109/LRA.2025.3641155（README 引用块）；MERL TR2026-057。作者 Queeney, Cai, Schperberg, Corcodel, Benosman, How。单位：MERL、MIT、Amazon Robotics（p.1）。2025-11-20 录用。 |
| 问题与目标 | 动力学泛化，建模为 CMDP（p.2 式1）。奖励不变、转移随上下文 c 变。训练时 c 为特权信息，部署时不可得。目标 max J(π,c)，c∈C_ID∪C_OOD（式2）。适用对象：仿真训练、零样本部署的足式机器人。 |
| 已有方法局限（原文） | 情境 RL/teacher-student："adaptation is only reliable for the range of ID scenarios seen during training"（p.1），且对 ID 分布敏感（p.2）。鲁棒 RL/对抗训练："at the cost of conservative performance in ID environments"（p.1）。作者原话："making it challenging to achieve both with a single policy"（p.2）。 |
| 方法设计 | 基础：RMA/Margolis 式 teacher-student + PPO + 对抗 RL。新增三项。①鲁棒适应模块（Sec.IV, p.3-4）：适应网络换成 epistemic NN（式5，base+epinet），用 N=8 个随机输入采样得到均值 μ̂ 和方差 σ̂²。②GRAM(h)=(1-α)z_rob+α·μ̂，α=exp(-(σ̂²-β)+)（式9），z_rob=0。③联合训练（Sec.V, p.4）：并行环境按迭代交替分配到"自适应训练"（z=f(c)，普通 PPO）和"鲁棒训练"（z=z_rob，加对抗者）。 |
| 适应与鲁棒如何结合 | 同一个策略网络，鲁棒模式就是 z=0 的一个输入点。适应分支靠特权 z 训练，鲁棒分支靠对抗数据训练 z=0 时的行为（p.4）。完整轨迹混合两种数据，作者称有额外鲁棒性收益（p.4）。 |
| 不确定性估计 | epinet 在 N=8 个高斯随机输入下的输出方差，对 8 维 latent 先逐维算方差，再求和得到**一个标量**（式6-7）。训练用式8，使 ID 历史方差小。部署前在验证集（ID 上的 σ̂²）上定标：β 取 0.90 分位，α 在 0.99 分位处等于 0.01（p.5）。 |
| 何时/如何退向鲁棒 | **整体回退，不分因素。** α 是标量，对整个 8 维 latent 统一缩放，高方差时整体趋近 z_rob。α 随时间步变化，所以同一条轨迹里可以时而适应时而保守（p.6，Fig.4：均值中等、25%-CVaR 低）。论文没有按物理因素（质量/摩擦/电机）拆分。 |
| Task 与训练 | Go2，跟踪速度指令 [vx,vy]~U(-1,1) m/s，航向目标生成 ωz（p.5）。观测：关节角、关节速度、投影重力、基座角速度（带噪，p.5）。动作 a∈R^12 目标关节角，PD 200 Hz，Kp=25，Kd=0.5，策略 50 Hz，每回合 20 s=1000 步。历史 H=16，latent d=8，epinet 输入维 8、N=8（Table I, p.5）。RL 10,000 次更新+适应模块监督 5,000 次（p.5）。奖励沿用 Margolis 2024，细节见该文。部署只用本体历史，不需特权信息（p.2）。 |
| 训练上下文（Table II） | 摩擦倍数 [0.05,4.5]；附加质量 [-1,3] kg；电机强度 ×12 维 [0.8,1.2]；关节零偏 12 维 [-0.1,0.1] rad；上下文共 26 维。对抗者：对机体施加前向/侧向推力，5% 时间，对线速度的影响随训练从 0 升到 1 m/s（p.4-5）。 |
| Benchmark | Isaac Lab 仿真 + 真机 Go2。训练全部在平地上，用 C_ID。测试：近 OOD（6 kg、5° 坡、5 cm 粗糙地、冻结后髋）；远 OOD（9 kg、10° 坡、10 cm 粗糙、随机冻结关节）（p.5）。运行中变化：仿真有"10 s 时加 9 kg"（Fig.4 右，p.6）；真机有走上泡沫、湿滑白板的地面切换（p.7-8）。真机 7 个场景，每场景每算法 5 次，共 105 次（p.7）。 |
| Baseline 与理由 | 鲁棒 RL（对抗训练）、情境 RL（teacher-student）、域随机化，都是足式泛化的常用方案（p.5）。消融：No Φ_GRAM、Separate Data、Modular（p.6）。 |
| 指标与关键数字 | 归一化平均任务回报（Table III, p.6），ID/近 OOD/远 OOD：GRAM 0.92/0.79/0.58；鲁棒 RL 0.87/0.74/0.59；情境 RL 0.94/0.75/0.42；DR 0.93/0.74/0.43。消融：No Φ_GRAM 0.93/0.80/0.55；Separate 0.92/0.74/0.46；Modular 0.94/0.74/0.41。注意近 OOD 上 No Φ_GRAM（0.80）高于 GRAM（0.79），但正文只称 GRAM 优于"其他方法"。Fig.5（p.6）：加宽质量训练范围后 9 kg 回报 GRAM 约 0.92，对照默认训练下 GRAM 约 0.50。真机 Table IV：平均到达时间 GRAM 8.17 s，鲁棒 RL 8.71 s，情境 RL 9.38 s。Table V：难场景成功 GRAM 15/15，鲁棒 RL 12/15，情境 RL 2/15。**仿真重复次数/种子数及"±"含义：未读到。** |
| 贡献 | 鲁棒适应模块；联合训练；Go2 仿真+真机验证（p.1）。 |
| 作者自述局限 | OOD 泛化取决于对抗者对最坏动力学的覆盖，极端 OOD 可能失败；只试了标准对抗者和四足（p.8）。 |

【评价】
- 强项：一个策略同时覆盖 ID 与 OOD，有真机证据；退回机制可用验证集分位数定标；对 ID 范围的敏感性有 Fig.5 的专项实验。
- 弱项一：回退是单标量，若只有一个因素 OOD，整个 latent 一起失效，其余可信因素的适应信息也被丢掉。这正是"选择性鲁棒适应"的切入空间。
- 弱项二：鲁棒分支只靠"推力对抗者"训练，没有针对质量/摩擦/电机等因素的 OOD 训练，鲁棒覆盖的是推力而非各类动力学。
- 弱项三：论文没有给种子数，仿真 ±0.00~0.03 的统计口径不清。

## B. 代码审查

**版本**：`README.md` 写明 Isaac Lab v1.0.0 + rsl_rl v2.0.0，测试于 Isaac Sim 4.1.0.0（pip 安装）。`environment.yaml`：Python 3.10、PyTorch 2.2.2 + CUDA 11.8、gymnasium 0.29.1。无 requirements.txt。仓库本身不含 Isaac Lab。

**目录与关键文件（共约 2150 行 Python）**

| 文件 | 作用 |
|---|---|
| `source/train.py`、`source/eval.py`、`source/launcher.py` | 训练/评估入口（`python -m source.train --alg_name gram --id_context default`） |
| `source/algs/gram/gram_actor_critic.py` | **GRAM 核心**：context_encoder、history_encoder、epinet、α 计算、鲁棒/自适应混合 |
| `source/algs/gram/gram_ppo.py` | PPO 更新、对抗者更新、历史编码器监督损失 |
| `source/algs/gram/gram_on_policy_runner.py` | 训练主循环、robust_masks 交替、验证分位数采集（`collect_validation_data`）、评估 |
| `source/algs/gram/gram_adversary.py` | 对抗者网络（输出 1 维角度，转为 2D 推力） |
| `source/envs/unitree_go2_custom_env.py` / `unitree_go2_cfg.py` | 任务与奖励配置、ID 上下文集（default/wide） |
| `source/envs/envs_utils.py` | 自定义动作项、DC 电机、摩擦随机化、对抗推力事件 |
| `source/envs/context_env_wrapper.py` | 把 26 维上下文读成张量 |
| `source/utils/cli_utils.py` | 各算法开关（`update_agent_cfg_by_alg`，L525-620） |

**不确定性与回退（关键行）**
- `gram_actor_critic.py` L688-696：`metric = latent_all.var(dim=0).sum(dim=-1)`，标量。
- L720-739：`history_epinet_shift_param`/`scale_param` 来自验证分位数，标量。
- L620-628：`alpha = exp(-scale*(var-shift)+)`，`latent = alpha*latent`，整体缩放。
- 默认 `history_epinet_output_type="base"`（L52，cli_utils L172-177），所以代码在 α 缩放时用的是 base 网络输出而不是 epinet 采样均值，和论文式9写的 μ̂ 不完全一致。
- L463-486：训练时 `robust_masks`（每环境一个标量）混合 robust/adapt；`robust_as_zeros=True` 时鲁棒分支就是同一网络喂 `zeros_like(latent)`。
- 评估：`cli_utils.py` L569-575，GRAM 用 `act_inference_adapt=True` + `apply_bias=True`。`calculate_uncertainty_mask`（L749-755）的硬阈值只用于 gram_modular 消融。

**复现性**：README 列出 6 种算法（gram、robust_rl、contextual_rl、domain_rand、gram_separate、gram_modular）和 default/wide 两个 ID 集，Table III、Fig.5 的训练命令齐全，评估参数（质量、摩擦、坡度、粗糙度、冻结关节）都能命令行设置。缺口：
1. **无预训练权重**（仓库仅源码和 LICENSE）。
2. **运行中变化**（Fig.4 右、10 s 时加 9 kg）：全仓库没有对应代码，grep 未发现任何中途改质量的逻辑。上下文只在环境构造时读取一次（`_set_context`），质量事件为 Isaac Lab 默认的启动期随机化【推断】。
3. **真机**部署代码、Fig.4/5 绘图脚本、种子汇总脚本未提供。
4. 评估时对抗推力强制为 0（`adversary_magnitude=0`，cli_utils L525 附近）。
5. 冻结关节的实现是把该关节动作倍数置 0（`action_mult_min/max=0`，`unitree_go2_cfg.py` L73-74），即关节被拉回默认位姿，不是物理锁死，和真机"冻结"不完全等价。

**迁移到 Isaac Lab 2.3.x / Isaac Sim 5.1（Blackwell）**：仓库整体绑定 v1.0.0，不能原样运行。需要改：
- 命名空间：`omni.isaac.lab*` → `isaaclab*`，`omni.isaac.lab_tasks` → `isaaclab_tasks`，rsl_rl 封装 → `isaaclab_rl.rsl_rl`（涉及 train.py、eval.py、context_env_wrapper.py、unitree_go2_custom_env.py、envs_utils.py 全部 import）。
- rsl_rl：Isaac Lab 2.3 使用的 rsl_rl 版本与 2.0.0 差异较大（我印象中是 3.x，观测改为字典/TensorDict，`get_observations()` 不再返回 `(obs, extras)`）【未核实】。GRAM 的 runner、PPO、storage 都继承 rsl_rl 2.0 类，且 `get_observations()` 的元组解包、`extras["observations"]["critic"]`、`store_code_state`、`EmpiricalNormalization` 都要按新接口重写。这是最大工作量。
- 内置 Go2 配置的导入路径和字段（`unitree_go2` 目录名、`rough_env_cfg`、`add_base_mass` 参数）、`parse_env_cfg(use_gpu=...)` 参数、`asset.root_physx_view.get_masses()`、`write_root_velocity_to_sim`、DCMotor 的 `_clip_effort` 等，可能有改名或弃用【未核实，需对照 2.3 源码】。
- 环境依赖：Python 3.10 → Isaac Sim 5.x 要求 3.11；Blackwell（sm_120）需要 CUDA 12.8 以上的 PyTorch，`environment.yaml` 的 torch 2.2.2+cu118 不可用。
- **粗估**：GRAM 的 Go2 版迁到 2.3 并跑通训练，约 1-2 周（接口迁移为主），再加 1 周对齐 Table III 趋势；另需自行补"中途加载荷"事件。

**迁到 Go2-W（12 腿位置 + 4 轮速度）**
- 动作：`ShiftScaleClampJointPositionAction` 假设全是位置动作，`scale_vec[:, :4] *= hip_scale_mult` 写死前 4 个是髋关节。要拆成腿（位置）+轮（速度）两个动作项，轮子不加 `joint_bias`、不 clamp 到关节限位。
- 资产与执行器：需要 Go2-W 的 USD/URDF 和 ArticulationCfg；`ScaledDCMotorCfg` 的 `joint_names_expr` 只匹配 hip/thigh/calf，要为轮子单独写速度控制执行器，并决定电机强度上下文是 12 维还是 16 维。
- 观测：关节位置/速度改为 16 维，轮子位置建议去掉或取相对量；历史编码器输入维度随之变化（`num_actor_obs*16`）。上下文 26 维要重定义。
- 奖励与终止：`feet_air_time`（轮足不适用）、`undesired_contacts` 的身体名、`base_height_l2` 目标高度 0.34（Go2 数值）、`.*foot` 摩擦随机化目标改为轮子，都要改。
- 工作量粗估：在 2.3 版本基础上再加 1-2 周（资产、动作项、奖励调试）。

## C. "选择性鲁棒适应"的代码切入点

**整体回退的位置**：①标量不确定性 `calculate_uncertainty_metric`（L688-696）；②标量 α 与标量 shift/scale（L620-628、L720-739）；③标量 `robust_masks`（runner L198-219、actor_critic L463-486、L558）；④鲁棒分支输入整向量置零（`robust_as_zeros`，L465-467）；⑤历史损失的 `history_loss_adapt_only` 也按标量 mask 选样本（gram_ppo L252-257）。

**改成 2-3 组的步骤**
1. **分组与潜变量分块**：在 `context_env_wrapper._set_context` 里把 26 维按组排序（例如：质量+摩擦为"接触/负载"组；电机强度+关节零偏为"执行器"组），并把 `context_encoder` 改成块结构，使 `z=[z_1,z_2]`，每组独立 latent（总维度 8 可拆为 4+4）。否则无法分组置零。
2. **分组不确定性**：`encode_history_epinet` 返回的 `latent_all`（样本×批×8）按组切片，各自 `var(dim=0).sum(-1)` 得到每组 σ_g²；`set_uncertainty_params` 对每组各存一套验证分位数（β_g、scale_g）。算出 α_g 后只乘对应 z_g。风险：epinet 只有一个输出头，各组方差是否真能区分，需要实验验证。
3. **训练 mask 向量化**：`robust_masks` 从 (N,1) 改成 (N,G)；在 runner 的 `_update_robust_masks` 里按组抽样（例如每环境随机选一个不可信子集），`update_distribution`/`evaluate` 里按组把 z_g 置零。critic 同样用掩码后的 latent。
4. **关键难点——部分可信下的鲁棒训练信号**：现在鲁棒环境用的是 ID 上下文 + 推力对抗者，对"哪一组 OOD"没有针对性。需要为每组加组内扰动：在被判为不可信的组上，把上下文采样范围扩到 ID 之外（类似 wide 配置，`unitree_go2_cfg.py` L127-133），或为每组增加专属对抗事件（质量/摩擦/电机强度），并让可信组保持 ID 采样。
5. **监督阶段**：`history_loss` 里的 `history_loss_adapt_only` 需按组加权，只对被标为"可信"的组计算 latent 回归损失。
6. **评估**：`act_inference` 里 α 改为向量；`calculate_epinet_metrics` 增加每组 α_g 的记录，用来画"哪个因素触发回退"的图，这也是汇报时最直观的证据。

**风险提示**：Table II 中 26 维上下文的因素在 latent 里是否可分、历史 16 帧能否分辨质量与摩擦同时变化，论文没有分析，需要先做小实验再决定分组方式。
