# 04 GRAM 官方代码精读（总览）

> 本篇是总览，用来建立全局印象。逐文件、逐行、从零讲起的详细版在 [code/](code/) 目录：
> [00 Python 与 PyTorch 基础](code/00_python_pytorch_basics.CN.md) → [01 项目结构与运行流程](code/01_project_structure_and_run_flow.CN.md) → [02 仿真环境](code/02_environment.CN.md) → [03 策略网络与不确定性](code/03_actor_critic.CN.md) → [04 对抗者](code/04_adversary.CN.md) → [05 PPO 与数据存储](code/05_ppo_and_storage.CN.md) → [06 训练主循环与评估](code/06_runner_train_eval.CN.md)。

代码来源：`github.com/merlresearch/gram`（浅克隆，只读）。行号对应原仓库（Isaac Lab v1.0 版本），服务器上的兼容版只改了 import 路径，行号基本一致。

标注约定：
- **【代码事实】**：读代码得出，附 `文件:行号`；
- **【论文】**：论文原文；
- **【推断】**：我们的判断，未运行验证。

---

## 一、目录结构与文件职责

```text
gram/
├── environment.yaml                 # 原环境：Python 3.10，torch 2.2.2+cu118
└── source/
    ├── train.py                     # 训练入口
    ├── eval.py                      # 评估入口
    ├── launcher.py                  # 启动 Isaac Sim（AppLauncher）并解析命令行
    ├── utils/
    │   ├── cli_utils.py             # 所有命令行参数；按算法名切换开关（核心配置中心）
    │   └── torch_utils.py           # 权重初始化
    ├── envs/
    │   ├── __init__.py              # 注册自定义任务
    │   ├── unitree_go2_cfg.py       # ID 上下文集（default / wide）的默认数值
    │   ├── unitree_go2_custom_env.py# 继承 Isaac Lab Go2 粗糙地形配置，改动作、执行器、事件、奖励
    │   ├── envs_utils.py            # 自定义动作项、电机、摩擦随机化、对抗推力、关节重置
    │   └── context_env_wrapper.py   # 把 26 维上下文读成张量，供教师使用
    └── algs/gram/
        ├── gram_actor_critic.py     # 【核心】策略、价值、上下文编码器、历史编码器、epinet、α
        ├── gram_ppo.py              # PPO 更新、历史编码器损失、对抗者更新、微调
        ├── gram_on_policy_runner.py # 训练主循环、鲁棒/自适应分配交替、验证集分位数、评估
        ├── gram_adversary.py        # 对抗者网络
        └── gram_rollout_storage.py  # 经验缓存（多存历史、掩码、对抗者数据）
```

全仓库约 4700 行 Python，算法核心集中在 `algs/gram/` 的 5 个文件里，约 2500 行。

---

## 二、一次训练的完整调用链

命令：`python -m source.train --alg_name gram --id_context default`

| 步骤 | 位置 | 做什么 |
|---|---|---|
| 1 | `train.py:16` | 导入 `launcher`，启动 Isaac Sim，得到 `args_cli` |
| 2 | `train.py:46-47` | `parse_custom_inputs_cfg` 读 default 上下文集，再由 `create_custom_env` 注册自定义 Go2 任务 |
| 3 | `train.py:50-53` | 解析环境配置；`parse_agent_cfg` → `update_agent_cfg_by_alg`（`cli_utils.py:546`）按算法名设开关 |
| 4 | `train.py:56-59` | 设随机种子（默认 `--seed 1`，`cli_utils.py:28`） |
| 5 | `train.py:72,85` | `gym.make` 建环境，用 `ContextRslRlVecEnvWrapper` 包装，构造时读一次上下文（`context_env_wrapper.py:17`） |
| 6 | `train.py:88` | 建 `GRAMOnPolicyRunner`：内部构造 `GRAMActorCritic`、`GRAMPPO`、`GRAMAdversary`（`runner:52-112`） |
| 7 | `train.py:111` | `runner.learn(max_iterations=10000)` |
| 8 | `runner:278-359` | 共 10000 + 5000 次迭代：前 10000 次每次采样后调用 `alg.update()`（PPO + 对抗者）；后 5000 次调用 `alg.finetune()`（只训练历史编码器） |
| 9 | `runner:378` | `collect_validation_data()`：用 ID 环境跑一整回合，统计不确定性的 101 个分位数，存进模型 |
| 10 | `runner:380` | 保存最终 checkpoint |

**要点**：论文说的"RL 训练 10000 次 + 监督学习 5000 次"，在代码里是**同一个循环的前后两段**（`runner:276-277`）。

---

## 三、网络结构（`gram_actor_critic.py`）

### 3.1 各网络一览

| 网络 | 输入 | 隐藏层 | 输出 | 位置 |
|---|---|---|---|---|
| 策略 actor | 观测 + 8 维 latent | 512-256-128，ELU | 12 维动作均值 | `:91-104` |
| 价值 critic | 特权观测 + 8 维 latent | 512-256-128 | 1 | `:106-116` |
| 上下文编码器（教师用） | 26 维上下文 | 64-64 | 8 维 latent z | `:128-138` |
| 历史编码器（学生用，即论文的 φ_base） | 观测 × 16 步，展平 | 512-256-128 | 8 维 latent | `:169-181` |
| epinet 可训练部分 | 见 3.2 | 16-16 | 8×8 | `:229-245` |
| epinet 先验部分（冻结） | 同上 | 16-16 | 8×8 | `:247-263`，`requires_grad=False` 在 `:263` |
| 对抗者 | 观测 | 512-256-128 | 1 维（角度） | `gram_adversary.py:44-55` |

表中的维度与论文 Table I 一致。

**初始化**（`:346-359`）：各网络最后一层用 `xavier_normal`，gain = 1e-4，初始输出接近 0。所以训练开始时教师 latent z ≈ 0，正好等于 z_rob = 0，与论文 p.4 的说法吻合："begins training near z_rob = 0"。epinet 先验网络最后一层的 gain = 1.0，让它在训练前就有足够的随机性。

**动作噪声**：`log_std` 是可学习参数（`:122-126`），每步训练后夹在 [0.01, 10] 之间（`:664-672`）。

### 3.2 epinet 的输入（`history_epinet_input_type="concat"`）

`encode_history`（`:567-620`）的计算步骤：

1. `latent = history_encoder(历史)`：base 网络的输出，8 维（`:568`）。
2. 拼出 epinet 的特征输入（`:572-575`），由两部分组成：
   - **展平的原始历史**；
   - **历史编码器倒数第二层（128 维）的特征**。
   
   两者都经过 `.detach()`，梯度不回传到 base 网络。这对应论文"h̃_t 是 h_t 与 base 最后隐藏层的拼接，并停止梯度"。
3. 采 **8 个**标准高斯随机向量 ε，每个 8 维（`:581-583`）。同一批数据共用这 8 个 ε（`:584`）。
4. 把 [特征, ε] 分别送进可训练网络和冻结的先验网络，两者相减（`:590-592`）。
5. `mlp_dot` 方式（`:597-601`）：输出被整理成 8×8 矩阵，再与 ε 做点积，得到 8 维的 epinet 项。
6. 得到 8 个样本：`latent_all = latent + epinet 项`（`:603`），形状为（8 个样本，批大小，8 维）。

### 3.3 不确定性与 α（代码中的式 9）

```python
latent_std_l2 = latent_all.var(dim=0).sum(dim=-1)        # :607  8个样本逐维方差，再把8维加起来 → 标量
uncertainty = (latent_std_l2 - shift).clamp(min=0)       # :608  (σ̂² - β)+
alpha = torch.exp(scale * uncertainty * -1)              # :609  α = exp(-λ(σ̂² - β)+)
latent = alpha.unsqueeze(-1) * latent                    # :614  默认 output_type="base"
```

- **不确定性是一个标量**：8 维的方差被求和成一个数。这正是我们想改的地方，即"整体退回"。
- `apply_bias` 只在评估时打开（`cli_utils.py:568-570`）。**训练时不使用 α**，与论文所说的"GRAM(h) 只在部署时使用"一致。

### 3.4 shift 与 scale 怎么来（`set_uncertainty_params`，`:706-730`）

训练结束后，验证集给出不确定性的分位数 q(·)，然后：

- **shift（论文中的 β）** = q(0.90)，见 `:709`；
- **scale（论文中的 λ）** 要满足：不确定性等于 q(0.99) 时，α = 0.01。

推导：

```text
exp(-λ·(q99 - q90)) = 0.01
⇒ λ = -ln(0.01) / (q99 - q90) ≈ 4.605 / (q99 - q90)
```

对应代码 `:719-723`：`scale = log(0.01) * -1 / (q99 - shift)`。

**含义**：
- ID 数据里有 90% 的时刻不确定性 ≤ β，此时 α = 1，完全适应；
- 只有 1% 的时刻不确定性超过 q99，此时 α < 0.01，基本退回鲁棒。

另外，`uncertainty_max_threshold = q99`（`:728`），只用在 `gram_modular` 消融里做硬切换（`:735-741`）。

### 3.5 鲁棒分支就是"同一个网络，输入零向量"（`robust_as_zeros=True`）

- `:273-279`：`robust_actor = self.actor`，`robust_critic = self.critic`，`robust_log_std = self.log_std`，三者都是**同一个对象**。
- `update_distribution`（`:449-472`）的计算：

```python
robust_latent = torch.zeros_like(latent.detach())                          # :452  z_rob = 0
mean = robust_masks * robust_mean + (1 - robust_masks) * adapt_mean        # :463
```

`robust_masks` 是每个环境一个 0/1 数：1 表示这条数据按"鲁棒训练"处理，策略看到的 latent 是 0；0 表示按"自适应训练"处理，策略看到的是真实 latent。

- `evaluate` 也一样（`:533-544`），价值函数同样按掩码混合。

---

## 四、训练循环细节（`gram_on_policy_runner.py`、`gram_ppo.py`）

### 4.1 鲁棒/自适应分配的交替

| 内容 | 位置 |
|---|---|
| 初始：前一半环境 mask = 0（自适应），后一半 = 1（鲁棒） | `runner:263-264` |
| 每次迭代开始时 mask = (mask + 1) mod 2，所有环境翻转 | `runner:198-200, 304-308` |
| 更新频率 `robust_mask_update_every = 1`，即每次迭代都翻转 | `cli_utils.py:129` |
| 每次迭代每个环境采 `num_steps_per_env` 步 | `runner:311` |

所以同一个环境的一条长轨迹（1000 步）里，会出现"24 步自适应、24 步鲁棒"交替的情况。这就是论文说的"完整轨迹混合两种数据"。

另外，`num_steps_per_env` 来自 Isaac Lab 的 Go2 PPO 配置，我们记得是 24，但本仓库内没有写出，属于**【推断】**。

`gram_separate` 消融改成"只在回合重置时翻转"（`robust_mask_reset_update=True`，`runner:209-219`），让一整条轨迹只属于一种模式。

### 4.2 对抗者

| 内容 | 位置 |
|---|---|
| 网络输出 1 维角度 θ | `runner:49`；`gram_adversary.py:49` |
| θ 转成方向向量 (cos θ, sin θ)，再乘以 U(0, M_k) 的随机幅值 | `gram_adversary.py:140-149` |
| M_k 随训练进度从 0 线性增长到 1 | `gram_adversary.py:151-154`；调用处 `runner:360` |
| 每步以 5% 概率触发（伯努利采样） | `gram_adversary.py:135-138`；`--adversary_prob 0.05`（`cli_utils.py:146`） |
| 只在鲁棒环境生效：`adversary_masks * robust_masks` | `gram_ppo.py:107` |
| 施加方式：直接把机身 x、y 速度加上 `magnitude × 向量`（magnitude = 1.0 m/s），并不是真的施加力 | `envs_utils.py:270-298`；事件 `custom_env.py:206-211` |
| 对抗者的优化目标：取负的策略优势，只在触发的步上计算，PPO 式裁剪 | `gram_ppo.py:392-416` |
| 每 10 次迭代更新一次 | `gram_ppo.py:361-363`；`--adversary_update_every 10` |

**要点**：论文说的"external forces"，在代码里实际上是**瞬时改变速度**，每次最多 1 m/s，方向由对抗者学习得到。

### 4.3 PPO 更新与历史编码器

- PPO 部分是标准的裁剪目标加价值损失（`gram_ppo.py:195-221`）。优化器 `optimizer` 管 actor、critic、log_std 和上下文编码器（`gram_ppo.py:59`；参数组见 `actor_critic.py:369-375`）。
  - **上下文编码器和策略一起，靠 RL 损失端到端训练**，即论文式 3。
- **历史编码器在 RL 阶段默认不训练**：只有加 `--train_and_finetune` 才在 `update()` 里训练（`gram_ppo.py:229`）。冒烟测试日志也印证了这一点：前两次迭代 History loss = 0，第 3 次（微调）才变成 14.57。
- **微调阶段**（`gram_ppo.py:469-600`）只更新 `history_optimizer`，即历史编码器加 epinet 可训练部分（`actor_critic.py:408-412`），学习率为 1e-3（`cli_utils.py:224`）。此时：
  - 采样改用学生自己的 latent，`act_from_context=False`（`runner:287`），相当于 DAgger 式地在学生自己的轨迹上学习；
  - 默认关闭对抗者（`runner:290-294`）；
  - 观测归一化器冻结（`runner:297-299`）。

**历史损失**（`gram_ppo.py:240-257`）：

```text
L = mean_over_8_samples || z_teacher - latent_all ||²
```

这就是论文的式 8，即在 8 个 ε 样本上取平均的 latent 回归。

- 可选 `--history_loss_adapt_only`（默认关闭）：只用自适应数据计算损失；
- 可选 `--history_loss_robust_as_zeros`（默认关闭）：鲁棒数据的目标设为 0。

**为什么这样训练能让 ID 上方差小**：每个 ε 样本都被要求逼近同一个教师 z。在训练分布内，网络学会让 epinet 项趋近于 0，8 个样本就会很接近；在没见过的历史上，冻结的先验网络会产生随机差异，可训练部分没有机会把它抵消，方差就变大。这是 epinet 的工作原理（Osband 2023）。

### 4.4 验证集与分位数（`runner:497-616`）

1. 关闭对抗者（`:507-510`），默认使用学生 latent。
2. 在 ID 环境中跑满一个回合（1000 步），分 mask = 0 和 mask = 1 两轮。默认 `collect_data_mix=True`，所以每轮里仍然一半一半交替（`:543-556`）。
3. 每步计算不确定性标量（`:580-581`），只统计还没摔倒的步（`:583-602`）。
4. 计算 0%、1%、…、100% 共 **101 个分位数**（`:603`），用 `store_validation` 存进模型参数 `validation_quantiles_value`（`actor_critic.py:157-159, 702-704`）。

所以 β 和 λ 是跟着 checkpoint 一起保存的，换一台机器评估时不需要重新校准。

---

## 五、六种算法的开关对照（`cli_utils.py:546-620`）

| 算法 | robust_as_zeros | history_epinet | 评估时 apply_bias | 评估动作 | collect_data_mix | 训练时对抗者 | 微调（历史编码器） |
|---|---|---|---|---|---|---|---|
| **gram** | 是 | 是 | 是（用 α） | act_inference_adapt（latent × α） | 是 | 是 | 是 |
| gram_separate | 是 | 是 | 是 | 同上 | **否**（回合级分配） | 是 | 是 |
| gram_modular | **否**（鲁棒、自适应是两个网络） | 是 | 否 | **硬阈值切换**（不确定性 > q99 时用鲁棒网络） | 否 | 是 | 是 |
| robust_rl | 否 | 否 | 否 | act_inference_robust | 只训练鲁棒（robust_train_only） | 是 | 否（`finetune_iterations=0`） |
| contextual_rl | 否 | 否 | 否 | act_inference_adapt（普通学生） | 只训练自适应 | **否**（`adversary_prob=0`） | 是 |
| domain_rand | 否 | 否 | 否 | act_inference_robust | 只训练鲁棒 | **否** | 否 |

**为什么 robust_rl 和 domain_rand 的策略"不看 latent"**：

- 它们的 `robust_as_zeros=False`，并且 `robust_use_latent_actor` 默认关闭，所以鲁棒策略是一个**单独的网络，输入只有观测**（`actor_critic.py:281-302, 455-458`）。
- 两者都只训练鲁棒分支（`runner:202-203`）。
- 区别只在对抗者：robust_rl 开了推力对抗者；domain_rand 不开，只靠 26 维上下文的随机化。
- 也就是说，**域随机化 = 不看环境信息、在随机环境里训练出的普通策略**。

另外，所有算法在**评估时都强制关闭对抗者**（`cli_utils.py:529-530`、`:563-565`）。

---

## 六、环境细节（`envs/`）

### 6.1 26 维上下文（`context_env_wrapper.py:108-199`）

| 顺序 | 量 | 维度 | 来源 | 归一化 |
|---|---|---|---|---|
| 1 | 机身附加质量 | 1 | 物理引擎读质量减去默认值（`:113-130`） | 线性映射到 [-1, 1] |
| 2 | 摩擦倍数 | 1 | 读最后一个形状（脚）的静摩擦，再除以 0.8（`:133-155`） | [-1, 1] |
| — | 动作倍数（冻结关节） | 12 | 默认**不放进上下文**（`action_mult_context_include=False`，`unitree_go2_cfg.py:76`） | — |
| 3 | 关节零偏 | 12 | 动作项的 `action_shift`（`:172-183`） | [-1, 1] |
| 4 | 电机强度倍数 | 12 | 执行器的 `effort_scale`（`:186-197`） | [-1, 1] |

**合计 1 + 1 + 12 + 12 = 26。**

**关键**：上下文在包装器**构造时只读一次**（`:17`）。质量和摩擦随机化都是 startup 事件，即在环境创建时设定一次。所以**一个环境的动力学在整个训练过程中固定不变**，代码里没有"运行中变化"。

### 6.2 动作处理（`envs_utils.py:29-191`，配置在 `custom_env.py:176-189`）

```text
目标关节角 = 原始动作 × 动作倍数 × scale + 默认关节角 + 关节零偏，然后夹到关节限位内
```

- `scale = 0.25`，髋关节再乘 `hip_scale_mult = 0.5`，即髋关节的 scale 是 0.125（`envs_utils.py:42-44`）。注意代码写死了"前 4 个关节是髋"。
- **关节零偏**：作为动作偏移项 `action_shift`，每个环境、每个关节在 [-0.1, 0.1] rad 内均匀采样（`:146-155`）。它模拟的是编码器零点误差：策略以为发出了 X，实际执行的是 X 加偏差。
- **动作倍数，也就是"冻结关节"**：
  - 把被选中关节的倍数设为 0（`:51-90`；`unitree_go2_cfg.py:72-74` 中的 min = max = 0）；
  - 这样目标角恒等于"默认角 + 零偏"，关节被 PD **拉回默认姿态并保持**，并不是物理上卡在当前位置；
  - 评估参数 `--frozen_joint_type hip/thigh/calf/all/custom` 决定从哪些关节里随机选一个（`cli_utils.py:375-384`）。

### 6.3 执行器（`envs_utils.py:345-389`，配置在 `custom_env.py:192-203`）

- 使用 `ScaledDCMotor`，基于 Isaac Lab 的 DC 电机模型：Kp = 25，Kd = 0.5，力矩上限 23.5 N·m，速度上限 30 rad/s。只匹配 hip、thigh、calf 三类关节。
- **电机强度**：每个环境、每个电机在 [0.8, 1.2] 内采样一个倍数 `_effort_scale`（`:356-358`），在力矩裁剪前相乘（`:376-379`）。
- **`motor_fault_indices`**（`:360-371`）：把选中电机的倍数直接设为 0，即"力矩为零"的故障。注意：
  - 只在**执行器构造时设定一次**，不是在运行中途发生；
  - 论文没有使用它（论文的"冻结关节"用的是动作倍数）；
  - 但它是我们后续做"轮/腿失效"时**可以直接利用的现成接口**。

### 6.4 摩擦（`envs_utils.py:195-264`，事件在 `custom_env.py:215-226`）

- 在 [0.05, 4.5] 区间划分 **64 档**，每个环境随机选一档；静摩擦和动摩擦用同一个倍数（默认值分别为 0.8 和 0.6）。
- 只作用于 `.*foot` 的碰撞形状。迁移到 Go2-W 时要改成轮子。

### 6.5 奖励、观测与终止（`custom_env.py:243-292`）

- **观测**：去掉了机身线速度 `base_lin_vel`（`:247`）。保留的是 Isaac Lab Go2 配置自带的项：角速度、投影重力、速度指令、关节位置、关节速度、上一步动作，并带噪声。
  - 论文 p.5 列的观测是"关节角、关节速度、投影重力、机身角速度"。代码里还有指令和上一步动作，这些属于继承来的默认项，论文没写全。
- **奖励权重**（注释写的是"coefficients updated to match Margolis 2024"）：

| 项 | 权重 |
|---|---|
| 线速度跟踪 track_lin_vel_xy_exp | 1.0 |
| 角速度跟踪 track_ang_vel_z_exp | 0.5 |
| 竖直速度 lin_vel_z_l2 | -2.0 |
| 横滚俯仰角速度 ang_vel_xy_l2 | -0.05 |
| 姿态 flat_orientation_l2 | -0.1 |
| 力矩 dof_torques_l2 | -1e-5 |
| 关节加速度 dof_acc_l2 | -2.5e-7 |
| 动作变化率 action_rate_l2 | -0.01 |
| 腾空时间 feet_air_time | 1.0 |
| 关节限位 dof_pos_limits | -10.0 |
| 机身高度 base_height_l2（目标 0.34 m） | -30.0 |
| 非脚部接触 undesired_contacts（thigh/calf/hip） | -1.0 |

  其余项和参数，例如 feet_air_time 的阈值，继承自 Isaac Lab 的 `UnitreeGo2RoughEnvCfg`。
- **评估模式**（`:279-292`）：只保留以 `track` 开头的两项奖励，并且机身、髋、大腿、头部一旦触地就终止。所以 Table III 的"归一化任务回报"只衡量**速度跟踪**，摔倒提前终止会导致得分偏低。【推断】
- **训练重置**：从"趴下"到"站立"之间随机插值的姿态开始，再加 ±0.1 rad 的扰动（`envs_utils.py:301-342`）。
- **地形**：训练时是平地；评估时可以设粗糙度和坡度（`custom_env.py:106-150`）。关闭了地形课程（`:103-104`）。
- **指令**：vx、vy ~ U(-1, 1)，按目标朝向生成角速度，10 s 重采样一次；2% 的环境站立不动（`unitree_go2_cfg.py:94-106`）。评估时指令永不重采样（`cli_utils.py:502-508`）。

---

## 七、论文与代码的不一致和注意点

| # | 论文 | 代码 | 影响 |
|---|---|---|---|
| 1 | 式 9：GRAM = (1-α)·z_rob + α·μ̂，μ̂ 是 8 个 epinet 样本的均值 | `α × latent`（`:614`），默认 `output_type="base"`，即乘的是 **base 网络输出**，不是 μ̂ | 因为 z_rob = 0，(1-α)·0 + α·x = α·x，形式等价；但 x 用的是 base 输出，与论文写法不同。训练使 epinet 项趋近 0，所以两者在 ID 上应该很接近。【推断】 |
| 2 | 不确定性"per-dimension"计算 | 逐维方差**再求和**成一个标量（`:607`） | 论文式 7 是逐维的，式 9 里的 σ̂² 实际上是总和，读者容易误解 |
| 3 | 正文有"10 s 时加 9 kg"（Fig.4 右） | 全仓库**没有**运行中改变质量的代码，上下文只在构造时读取一次 | 复现 Fig.4 右要自己补事件 |
| 4 | 有真机实验 | 没有真机部署代码，也**没有预训练权重** | 必须自己从头训练 |
| 5 | 鲁棒训练用对抗"外力" | 实际是瞬时**加速度变化**（改写速度，≤1 m/s） | 物理含义不完全等同于施加外力 |
| 6 | 冻结关节（frozen joint） | 动作倍数为 0，关节被**拉回默认角**，不是锁在当前角度 | 与真机的"卡死"不同 |
| 7 | 评估 | 对抗者强制为 0；奖励只保留跟踪项 | 正常 |
| 8 | 奖励"参考 [4]" | 继承 Isaac Lab Go2 rough 配置，再按 Margolis 调整权重 | 换 Isaac Lab 版本后，继承来的默认值可能变化（见 07 文档的风险 1） |
| 9 | 种子数未报告 | 默认 `--seed 1` | 我们复现时需要自己定种子数 |

---

## 八、选择性鲁棒适应要改的代码点

详细版见 `04_research/candidates/gram.md` 的 C 节，这里只列要点。

**现在"整体退回"的五个位置**：

| # | 内容 | 位置 |
|---|---|---|
| ① | 标量不确定性 | `calculate_uncertainty_metric`，`actor_critic.py:674-682`；`encode_history:607` |
| ② | 标量的 shift/scale，以及 α 整体乘到 latent 上 | `:706-725`、`:608-614` |
| ③ | 训练时每个环境一个标量掩码 `robust_masks (N,1)` | `runner:263-264, 198-207`；`actor_critic.py:463` |
| ④ | 鲁棒分支把**整个** latent 置零 | `:452, :534` |
| ⑤ | 历史损失按标量掩码选样本 | `gram_ppo.py:252-257` |

**改成按组（例如"环境组：质量 + 摩擦"和"执行器组：电机强度 + 零偏"）的步骤**：

1. **latent 分块**：上下文编码器改成分组结构，每组只看本组的上下文，各输出 4 维，拼成 8 维（`actor_critic.py:128-138`）。上下文的拼接顺序在 `context_env_wrapper.py:108-199` 里已经按"质量、摩擦、零偏、电机"排好，正好可以切开。
2. **分组不确定性**：`latent_all` 按组切片，各自计算 `var(dim=0).sum(-1)`；每组单独保存一套验证分位数和 β_g、λ_g；得到的 α_g 只乘对应的 z_g。
3. **掩码向量化**：`robust_masks` 从 (N,1) 改成 (N,G)，在 `update_distribution`、`evaluate` 里按组置零；`_update_robust_masks` 改成随机挑选不可信的组。
4. **部分可信时的训练信号**：被标为不可信的组，把它的参数采样范围推到 ID 之外，例如某个电机的强度设为 0 到 0.5，或利用现成的 `motor_fault_indices`；其他组保持 ID 采样。这一步需要把上下文和事件改成**按组、可在运行中重新采样**（目前只在构造时读一次）。
5. **历史损失**：按组加权，只对可信组做回归。
6. **评估**：记录每组的 α_g，画出"是哪一组触发了退回"。

**风险**：epinet 只有一个输出头，各组的方差能否真正分开，必须先做"直接告诉策略哪组不可信"的上限实验来确认。

---

## 九、读代码顺序建议

1. `README.md`：看清 6 种算法和训练、评估命令。
2. `source/train.py`：看清整体流程，约 120 行。
3. `utils/cli_utils.py:546-620`：看清 6 种算法分别打开哪些开关。
4. `algs/gram/gram_actor_critic.py`：
   - 先读 `update_distribution`、`act`、`evaluate`（`:449-546`）；
   - 再读 `encode_history`（`:567-620`）；
   - 最后读 `set_uncertainty_params`（`:706-730`）。
5. `algs/gram/gram_on_policy_runner.py`：`learn`（`:221-380`）和 `collect_validation_data`（`:497-616`）。
6. `algs/gram/gram_ppo.py`：`act`（`:85-112`）、`update` 中的历史损失与对抗者部分（`:228-418`）、`finetune`（`:469-600`）。
7. `envs/context_env_wrapper.py`：看 26 维上下文怎么拼成。
8. `envs/unitree_go2_custom_env.py` 和 `envs_utils.py`：看动作、电机、摩擦、推力、奖励。

**建议做法**：每读完一个函数，用一句话写下"输入是什么、输出是什么、对应论文哪个公式"。

---

## 十、自测题（附答案）

**1. 代码里的 α 在训练时用了吗？**
没有。`history_epinet_apply_bias` 只在评估时设为 True（`cli_utils.py:568-570`）。训练时，鲁棒和自适应完全由 0/1 掩码决定。

**2. 鲁棒策略和自适应策略是两个网络吗？**
GRAM 里不是。`robust_as_zeros=True` 时是同一个 actor：鲁棒模式输入 latent = 0，自适应模式输入真实 latent（`actor_critic.py:273-279, 452`）。

**3. β 和 λ 是怎么确定的？**
训练结束后，在 ID 验证数据上统计不确定性分位数。β = q90；λ = -ln(0.01)/(q99 - q90)，使得 q99 处 α = 0.01（`:706-725`）。

**4. 为什么 latent 维度 8 的不确定性只是一个数？**
`latent_all.var(dim=0).sum(dim=-1)`：先对 8 个 ε 样本逐维求方差，再把 8 维加起来（`:607`）。

**5. 对抗者"施加外力"在代码里是怎么做的？**
把机身水平速度直接加上 U(0, M_k) × (cos θ, sin θ) × 1 m/s，每步 5% 概率触发，只在鲁棒环境生效（`envs_utils.py:270-298`；`gram_ppo.py:107`）。

**6. 历史编码器在什么时候训练？用什么损失？**
默认只在最后 5000 次微调迭代中训练，用学生自己的轨迹。损失是 8 个 epinet 样本与教师 z 的平方误差取平均（`gram_ppo.py:240-257`、`:469-600`）。

**7. "冻结关节"真的把关节锁死了吗？**
没有。它把该关节的动作倍数设为 0，目标角恒等于默认角加零偏，PD 把关节拉回并保持在默认位置（`envs_utils.py:96-100`）。

**8. 训练中一个环境的摩擦、质量会变吗？**
不会。它们都是 startup 事件，上下文也只在包装器构造时读一次（`context_env_wrapper.py:17`）。

**9. domain_rand 和 robust_rl 的区别是什么？**
两者都只训练一个"只看观测"的策略。robust_rl 加了推力对抗者，domain_rand 没有；它们都不做微调（`cli_utils.py:589-617`）。

**10. 如果要做"运行中某个轮子突然失效"，现有代码缺什么？**
缺两样：
- 中途触发的事件：现在电机倍数和 `motor_fault_indices` 只在构造时设定；
- 上下文的同步刷新：`_set_context` 只调用一次。

另外，执行器只匹配腿部的三类关节，要为轮子单独写速度控制执行器。
