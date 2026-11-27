# 代码精读 05：PPO 原理与 `gram_rollout_storage.py`、`gram_ppo.py` 逐行讲解

> 读者：零基础本科生。这一篇讲 GRAM "怎么从数据里学"。
> 涉及文件：
> - `source/algs/gram/gram_rollout_storage.py`（197 行）：经验缓冲区，把采到的数据存起来
> - `source/algs/gram/gram_ppo.py`（646 行）：PPO 更新、对抗者更新、历史编码器的监督训练
>
> 标注约定：
> - **【代码事实】**：直接读代码能确认的；
> - **【推断】**：依赖父类 `rsl_rl` 2.0 或 Isaac Lab 默认配置，这两部分不在 GRAM 仓库里。服务器上有源码，路径 `upstream/rsl_rl` 和 `work/IsaacLab`，需对照确认。

---

## 目录

- [第一部分　零基础讲 PPO](#第一部分零基础讲-ppo)
  - 1.1 轨迹、回报
  - 1.2 价值函数
  - 1.3 优势
  - 1.4 GAE（附手算例子）
  - 1.5 重要性比率与裁剪目标（附数值例子）
  - 1.6 价值损失
  - 1.7 熵
  - 1.8 自适应学习率（desired_kl）
  - 1.9 mini-batch 与 epoch
  - 1.10 一次 PPO 迭代的全景
- [第二部分　`gram_rollout_storage.py` 逐行](#第二部分gram_rollout_storagepy-逐行)
- [第三部分　`gram_ppo.py` 逐行](#第三部分gram_ppopy-逐行)
  - 3.1 `init_extras`：优化器
  - 3.2 `init_storage`
  - 3.3 `act`
  - 3.4 `adversary_update_sim`
  - 3.5 `compute_returns`
  - 3.6 `update`：PPO 主更新
  - 3.7 `update`：历史编码器分支
  - 3.8 `update`：对抗者更新
  - 3.9 `update`：统计量
  - 3.10 `finetune`
- [第四部分　超参数总表](#第四部分超参数总表)
- [第五部分　读代码时发现的值得注意之处](#第五部分读代码时发现的值得注意之处)
- [自测题](#自测题)

---

# 第一部分　零基础讲 PPO

GRAM 的策略是用 **PPO（Proximal Policy Optimization，近端策略优化）** 训练的。不懂 PPO，就看不懂 `gram_ppo.py`。下面从最基础讲起。

## 1.1 轨迹与回报

**这段要讲什么**：强化学习的数据长什么样。

机器狗每 0.02 秒（50 Hz）做一次决策：
1. 看一眼自己的状态 s_t（关节角、角速度、速度指令……）；
2. 策略网络给出一个动作 a_t（12 个关节的目标角度）；
3. 仿真器往前推一步，得到奖励 r_t（跟上速度指令就加分，动作抖就扣分）和新状态 s_{t+1}。

把这一串记下来，就是一条**轨迹（trajectory）**：

```
s_0, a_0, r_0, s_1, a_1, r_1, s_2, a_2, r_2, ...
```

**回报（return）**：从某一时刻起，后面所有奖励"打折后"加起来：

$$G_t = r_t + \gamma r_{t+1} + \gamma^2 r_{t+2} + \cdots$$

- γ（gamma，折扣因子）通常取 0.99。意思是"越远的奖励越不重要"。
- 例：r = [1, 1, 1]，γ = 0.99，则 G_0 = 1 + 0.99 + 0.9801 = 2.9701。

**强化学习的目标**：让回报的期望尽量大。

## 1.2 价值函数 V(s)

**这段要讲什么**：为什么要有一个"评委"网络。

**价值函数 V(s)**：从状态 s 出发，按当前策略走下去，**平均**能拿到多少回报。

- 它是一个神经网络（代码里叫 **critic**，评论家），输入状态，输出一个数。
- 作用：给每一步提供一个"基准线"。

> 打个比方：考试平均分是 75 分。你考了 80，说明比平均好 5 分；考了 70，说明差 5 分。V(s) 就是"平均分"。

## 1.3 优势 A(s, a)

**优势（advantage）**：这一步实际做得比"平均水平"好多少。

$$A_t = (\text{实际拿到的回报}) - V(s_t)$$

- A > 0：这个动作比平均好 → **以后多做**；
- A < 0：这个动作比平均差 → **以后少做**。

PPO 的核心就是：**按优势的正负和大小，调整每个动作的概率。**

## 1.4 GAE：广义优势估计

**这段要讲什么**：实际回报要等到回合结束才知道，但我们每 24 步就要更新一次，所以要"估计"优势。GAE 是一种折中好的估计方法。

### 第一步：单步 TD 误差 δ

$$\delta_t = r_t + \gamma\, V(s_{t+1}) - V(s_t)$$

含义：这一步拿到的奖励 r_t，加上"下一个状态的估值"，比"这一步原来的估值"多了多少。如果 δ > 0，说明这一步比预期好。

### 第二步：把多步的 δ 加权加起来

$$A_t = \delta_t + (\gamma\lambda)\,\delta_{t+1} + (\gamma\lambda)^2\,\delta_{t+2} + \cdots$$

写成递推形式（代码就是这么算的，**从后往前**算）：

$$A_t = \delta_t + \gamma\lambda\, A_{t+1}$$

- λ（lambda，GAE 系数）通常取 0.95。
- λ = 0：只看一步，A_t = δ_t（偏差大，方差小）；
- λ = 1：看到底，相当于用真实回报（偏差小，方差大）；
- 0.95 是常用的折中。

### 第三步：回合结束的处理

如果第 t 步之后回合结束了（摔倒或超时），那么"下一个状态"不属于这条轨迹，不能用它的估值：

$$\delta_t = r_t + \gamma\,(1-\text{done}_t)\,V(s_{t+1}) - V(s_t),\qquad A_t = \delta_t + \gamma\lambda\,(1-\text{done}_t)\,A_{t+1}$$

### 第四步：回报目标

$$\text{Return}_t = A_t + V(s_t)$$

这个 Return_t 会作为价值网络的训练目标。

### 手算例子（3 步）

设 γ = 0.99，λ = 0.95，所以 γλ = 0.9405。

| t | r_t | V(s_t) | done_t |
|---|---|---|---|
| 0 | 1.0 | 2.0 | 0 |
| 1 | 0.5 | 1.5 | 0 |
| 2 | 2.0 | 1.0 | 0 |

最后一步之后的状态估值（代码里叫 `last_values`）V(s_3) = 1.2。

**从后往前算：**

**t = 2**：
- δ_2 = 2.0 + 0.99 × 1.2 − 1.0 = 2.0 + 1.188 − 1.0 = **2.188**
- A_2 = δ_2 + 0.9405 × 0（后面没有了）= **2.188**
- Return_2 = 2.188 + 1.0 = **3.188**

**t = 1**：
- δ_1 = 0.5 + 0.99 × 1.0 − 1.5 = 0.5 + 0.99 − 1.5 = **−0.01**
- A_1 = −0.01 + 0.9405 × 2.188 = −0.01 + 2.0578 = **2.0478**
- Return_1 = 2.0478 + 1.5 = **3.5478**

**t = 0**：
- δ_0 = 1.0 + 0.99 × 1.5 − 2.0 = 1.0 + 1.485 − 2.0 = **0.485**
- A_0 = 0.485 + 0.9405 × 2.0478 = 0.485 + 1.9260 = **2.4110**
- Return_0 = 2.4110 + 2.0 = **4.4110**

**观察**：t = 1 这一步自己的 δ 几乎是 0（−0.01），但因为后面 t = 2 很好，它的优势仍然是 2.05。这就是 GAE"把后面的好处分一部分给前面"。

**如果 t = 1 之后回合结束（done_1 = 1）**：
- t = 1：δ_1 = 0.5 + 0.99 × **0** × 1.0 − 1.5 = **−1.0**；A_1 = −1.0 + 0.9405 × **0** × A_2 = **−1.0**
- 回合结束后，t = 2 是新回合的第一步，它的好处不会传回 t = 1。

## 1.5 重要性比率与裁剪目标

**这段要讲什么**：PPO 名字里"近端"的意思是：每次更新，新策略不能离旧策略太远。

### 策略是一个概率分布

GRAM 的策略输出的不是一个确定的动作，而是一个**高斯分布**：
- 均值 μ（由 actor 网络算出，12 维）；
- 标准差 σ（一个可学习的参数，12 维，代码里存的是 log σ）。

采样动作 a ~ N(μ, σ²)。σ 大，探索多；σ 小，动作更确定。

### 重要性比率

数据是用**旧策略** π_old 采的，但我们要更新成**新策略** π_new。比较同一个动作在新旧策略下的概率：

$$\text{ratio} = \frac{\pi_{new}(a\mid s)}{\pi_{old}(a\mid s)} = \exp\big(\log\pi_{new}(a\mid s) - \log\pi_{old}(a\mid s)\big)$$

- ratio > 1：新策略更倾向这个动作；
- ratio < 1：新策略更不倾向这个动作。

代码里存的是对数概率，所以用 `exp(新 - 旧)` 计算。

### 不裁剪的目标

想让好动作（A > 0）的 ratio 变大，坏动作（A < 0）的 ratio 变小，于是最大化 ratio × A。代码里写成"最小化损失"，所以取负号：

$$L = -A \times \text{ratio}$$

### 为什么要裁剪

如果某个动作 A 很大，网络会拼命把 ratio 拉得很大，一次更新改太多，策略可能崩溃。PPO 的办法是把 ratio 限制在 [1−ε, 1+ε]（ε 叫 `clip_param`，通常 0.2），并且取"更悲观"的那个：

$$L^{CLIP} = \max\big(-A\cdot\text{ratio},\ -A\cdot\text{clip}(\text{ratio}, 1-\varepsilon, 1+\varepsilon)\big)$$

### 数值例子（ε = 0.2）

| 情况 | A | ratio | 不裁剪项 −A·ratio | 裁剪项 −A·clip(ratio) | max（实际损失） | 含义 |
|---|---|---|---|---|---|---|
| ① 好动作，已经涨很多 | +2 | 1.5 | −3.0 | −2 × 1.2 = −2.4 | **−2.4** | 取裁剪项，ratio 再涨也没有好处，**梯度为 0**，停止继续推 |
| ② 好动作，还没涨够 | +2 | 1.1 | −2.2 | −2 × 1.1 = −2.2 | **−2.2** | 没有触到边界，正常推 |
| ③ 坏动作，已经降很多 | −1 | 0.5 | 0.5 | 1 × 0.8 = 0.8 | **0.8** | 取裁剪项，**梯度为 0**，不再继续压 |
| ④ 坏动作，反而涨了 | −1 | 1.5 | 1.5 | 1 × 1.2 = 1.2 | **1.5** | 取不裁剪项，**有梯度**，要把它压回来 |

**一句话**：裁剪只"刹车"，不"放过"。往好的方向走太多就停，往坏的方向走多少都要纠正。

## 1.6 价值损失

价值网络 V 要尽量预测准 Return：

$$L_V = (V(s) - \text{Return})^2$$

**带裁剪的版本**（rsl_rl 默认开启 `use_clipped_value_loss`【推断】）：新的价值估计不能离旧的太远：

$$V_{clip} = V_{old} + \text{clip}(V - V_{old}, -\varepsilon, \varepsilon),\qquad L_V = \max\big((V-\text{Return})^2,\ (V_{clip}-\text{Return})^2\big)$$

数值例子：V_old = 1.0，新 V = 1.5，Return = 2.0，ε = 0.2：
- 不裁剪：(1.5 − 2.0)² = 0.25；
- 裁剪：V_clip = 1.0 + clip(0.5, −0.2, 0.2) = 1.2，(1.2 − 2.0)² = 0.64；
- 取 max = 0.64。效果是让价值网络也"慢慢改"。

## 1.7 熵

**熵（entropy）**：衡量分布有多"散"。高斯分布 σ 越大，熵越大。

总损失里减去熵（乘系数 `entropy_coef`，通常 0.01），鼓励策略保持一定随机性，防止过早地只做一种动作（探索不足）。

## 1.8 自适应学习率（desired_kl）

**这段要讲什么**：学习率太大，策略一次变太多；太小，学得慢。rsl_rl 用"新旧策略之间的 KL 散度"来自动调学习率。

**KL 散度**：衡量两个分布差多少。两个高斯分布 N(μ_old, σ_old²) 和 N(μ, σ²) 的 KL（每一维）：

$$KL = \log\frac{\sigma}{\sigma_{old}} + \frac{\sigma_{old}^2 + (\mu_{old}-\mu)^2}{2\sigma^2} - \frac12$$

对 12 个动作维度求和，再对 batch 取平均，得到 kl_mean。

**调节规则**（`gram_ppo.py:185-188`）：
- kl_mean > 2 × desired_kl：变化太大 → 学习率 ÷ 1.5（下限 1e-5）；
- kl_mean < desired_kl / 2：变化太小 → 学习率 × 1.5（上限 1e-2）；
- 否则不变。

**数值例子**：desired_kl = 0.01（rsl_rl Go2 默认值【推断】），当前学习率 1e-3：
- 算出 kl_mean = 0.03 > 0.02 → 学习率变为 6.67e-4；
- 算出 kl_mean = 0.003 < 0.005 → 学习率变为 1.5e-3。

服务器冒烟测试日志里 `Loss/learning_rate` 从 0.00225 变到 0.003375，正好是 × 1.5，说明这个机制在起作用。

## 1.9 mini-batch 与 epoch

一次迭代采到的数据量是 环境数 × 步数 = 4096 × 24 = **98,304 条**。

PPO 不是一次性用全部数据算一个梯度，而是：
1. **打乱**这 98,304 条数据；
2. 切成 `num_mini_batches` 份（默认 4【推断】），每份 24,576 条，叫一个 **mini-batch**；
3. 每个 mini-batch 算一次损失、更新一次参数；
4. 4 个 mini-batch 都用完，叫一个 **epoch**；
5. 重复 `num_learning_epochs` 次（默认 5【推断】）。

所以每次迭代一共做 **4 × 5 = 20 次梯度更新**。同一批数据被反复用 5 次，这就是为什么需要"裁剪"来防止改过头。

## 1.10 一次 PPO 迭代的全景

```
┌─────────────────────────── 一次迭代（iteration）───────────────────────────┐
│ ① 采样（rollout）：4096 个环境并行，每个走 24 步                              │
│    每一步：策略给动作 → 仿真器走一步 → 存 (s, a, r, done, V, logπ, μ, σ ...)    │
│ ② 计算回报和优势：用 GAE 从后往前算 A 和 Return，再标准化 A                     │
│ ③ 学习（update）：5 个 epoch × 4 个 mini-batch = 20 次梯度更新                  │
│    损失 = 裁剪策略损失 + 1.0 × 价值损失 − 0.01 × 熵                            │
│ ④ 清空缓冲区，进入下一次迭代                                                  │
└───────────────────────────────────────────────────────────────────────────┘
```

GRAM 在这个标准流程上加了三样东西：
1. 存更多数据：观测历史、上下文、`robust_masks`、对抗者的动作；
2. 一个对抗者，也用 PPO 风格的损失训练，但目标是**让机器狗表现变差**；
3. 历史编码器的监督训练（默认只在最后 5000 次迭代做）。

下面逐行看代码。

---

# 第二部分　`gram_rollout_storage.py` 逐行

**这个文件要干什么**：提供一个"大表格"，把 24 步 × 4096 个环境的数据都存下来，供 PPO 更新时取用。它继承 rsl_rl 的 `RolloutStorage`，**额外**存 GRAM 需要的东西。

## 2.1 `Transition`：一步的数据（第 16–27 行）

```python
# gram_rollout_storage.py:15-27
class GRAMRolloutStorage(RolloutStorage):
    class Transition(RolloutStorage.Transition):
        def __init__(self):
            super().__init__()
            self.observations_history = None

            self.adversary_masks = None
            self.adversary_actions = None
            self.adversary_log_prob = None
            self.adversary_mean = None
            self.adversary_sigma = None

            self.robust_masks = None
```

**逐行解释**：
- `Transition`：一个"小盒子"，装**一步**的数据。PPO 每走一步填一次，然后放进大表格。
- `super().__init__()`：先继承父类的字段。【推断】rsl_rl 2.0 父类里有 `observations`、`critic_observations`、`actions`、`rewards`、`dones`、`values`、`actions_log_prob`、`action_mean`、`action_sigma`。
- `observations_history`：**新增**。过去 16 步的观测，历史编码器要用。
- `adversary_*` 五项：**新增**。对抗者这一步的情况：
  - `adversary_masks`：这一步**有没有被推**（0 或 1）；
  - `adversary_actions`：对抗者选的推力方向（一个角度）；
  - `adversary_log_prob`、`adversary_mean`、`adversary_sigma`：对抗者策略的对数概率、均值、标准差。和主策略一样，对抗者也是高斯策略，也要用 PPO 更新，所以要存这些"旧策略"信息。
- `robust_masks`：**新增**。这一步这个环境是"鲁棒训练"（1）还是"自适应训练"（0）。

## 2.2 构造函数：开辟存储空间（第 29–58 行）

```python
# gram_rollout_storage.py:29-58
    def __init__(self, num_envs, num_transitions_per_env, obs_history_length,
                 obs_shape, privileged_obs_shape, actions_shape, adversary_action_shape, device="cpu"):
        super().__init__(num_envs, num_transitions_per_env, obs_shape, privileged_obs_shape, actions_shape, device)

        self.obs_history_length = obs_history_length

        self.observations_history = torch.zeros(
            num_transitions_per_env, num_envs, obs_history_length, *obs_shape, device=self.device
        )

        self.adversary_masks = torch.zeros(num_transitions_per_env, num_envs, 1, device=self.device)
        self.adversary_actions = torch.zeros(num_transitions_per_env, num_envs, *adversary_action_shape, device=self.device)
        self.adversary_log_prob = torch.zeros(num_transitions_per_env, num_envs, 1, device=self.device)
        self.adversary_mu = torch.zeros(num_transitions_per_env, num_envs, *adversary_action_shape, device=self.device)
        self.adversary_sigma = torch.zeros(num_transitions_per_env, num_envs, *adversary_action_shape, device=self.device)

        self.robust_masks = torch.zeros(num_transitions_per_env, num_envs, 1, device=self.device)
```

（原文第 49–56 行有换行，此处合并显示，内容一致。）

**逐行解释**：
- 所有张量的前两维都是 **[步数, 环境数]**，也就是"第几步、第几个环境"。
- `torch.zeros(...)`：先全部填 0，占好显存。
- `*obs_shape`：Python 的"解包"写法。`obs_shape = [45]` 时，`*obs_shape` 就是 `45`。

### 每个张量的形状（代入数值）

设 num_envs = 4096，num_steps_per_env = 24，H = 16。观测维度按 Isaac Lab Go2 速度任务推算为 45（角速度 3 + 投影重力 3 + 速度指令 3 + 关节角 12 + 关节速度 12 + 上一步动作 12；机身线速度和高度扫描被 GRAM 去掉了）【推断，需在服务器上打印 `num_obs` 确认】。

| 张量 | 来源 | 形状 | 代入后 | 含义 |
|---|---|---|---|---|
| `observations` | 父类【推断】 | [T, N, obs] | [24, 4096, 45] | 策略看到的观测 |
| `privileged_observations` | 父类【推断】 | [T, N, critic_obs] | [24, 4096, 45] | critic 的观测；Go2 任务没有单独的 critic 观测组，与策略观测相同 |
| `actions` | 父类【推断】 | [T, N, 12] | [24, 4096, 12] | 采样出的动作 |
| `rewards` | 父类【推断】 | [T, N, 1] | [24, 4096, 1] | 奖励 |
| `dones` | 父类【推断】 | [T, N, 1] | [24, 4096, 1] | 这一步之后回合是否结束 |
| `values` | 父类【推断】 | [T, N, 1] | [24, 4096, 1] | 采样时 critic 的估值 V_old |
| `actions_log_prob` | 父类【推断】 | [T, N, 1] | [24, 4096, 1] | 旧策略的 log π_old(a∣s) |
| `mu`、`sigma` | 父类【推断】 | [T, N, 12] | [24, 4096, 12] | 旧策略的均值和标准差（算 KL 用） |
| `returns`、`advantages` | 父类【推断】 | [T, N, 1] | [24, 4096, 1] | GAE 算出来的 |
| **`observations_history`** | GRAM | [T, N, H, obs] | **[24, 4096, 16, 45]** | 每一步对应的过去 16 帧观测 |
| **`adversary_masks`** | GRAM | [T, N, 1] | [24, 4096, 1] | 这一步是否被推 |
| **`adversary_actions`** | GRAM | [T, N, 1] | [24, 4096, 1] | 推力方向（角度） |
| **`adversary_log_prob`** | GRAM | [T, N, 1] | [24, 4096, 1] | |
| **`adversary_mu`、`adversary_sigma`** | GRAM | [T, N, 1] | [24, 4096, 1] | |
| **`robust_masks`** | GRAM | [T, N, 1] | [24, 4096, 1] | 鲁棒 / 自适应分配 |
| **`context`** | GRAM（`init_extras`） | [T, N, 26] | [24, 4096, 26] | 真实环境参数（特权信息） |

**显存估算**：最大的是 `observations_history`：24 × 4096 × 16 × 45 = 70,778,880 个 float32，约 **283 MB**。其余张量加起来不到 50 MB。所以缓冲区本身不大，显存主要花在仿真上。

> **注意一个细节**：每一步都存了一份完整的 16 帧历史，相邻两步的历史有 15 帧是重复的。这是用空间换简单：取 mini-batch 时可以直接按下标拿，不用再拼。

## 2.3 `init_extras`：存上下文（第 60–61 行）

```python
# gram_rollout_storage.py:60-61
    def init_extras(self, context):
        self.context = context.unsqueeze(dim=0).repeat(self.num_transitions_per_env, 1, 1)
```

**逐行解释**：
- `context`：形状 [4096, 26]，每个环境的 26 维真实参数（摩擦 1 + 附加质量 1 + 电机强度 12 + 关节零偏 12）。
- `unsqueeze(dim=0)`：在最前面加一维 → [1, 4096, 26]。
- `repeat(24, 1, 1)`：第 0 维复制 24 次 → [24, 4096, 26]。

**为什么只存一次，不在每步更新？**【代码事实】`init_extras` 只在构造时调用一次（经 `gram_ppo.py:37`），之后不再修改。这说明 **GRAM 训练时每个环境的上下文从头到尾是固定的**：环境 0 的摩擦是 2.3，就一直是 2.3。这和 Isaac Lab 里质量、摩擦随机化用的是 `mode="startup"`（只在启动时执行一次）是一致的。

**对我们的意义**：如果要做"运行中途电机变弱"，上下文会随时间变化。这里就必须改成**每一步都存一份上下文**，和 `observations` 一样放进 `add_transitions`。

## 2.4 `add_transitions`：存一步数据（第 63–86 行）

```python
# gram_rollout_storage.py:63-86
    def add_transitions(self, transition: Transition):
        if self.step >= self.num_transitions_per_env:
            raise AssertionError("Rollout buffer overflow")
        self.observations[self.step].copy_(transition.observations)
        self.observations_history[self.step].copy_(transition.observations_history)
        if self.privileged_observations is not None:
            self.privileged_observations[self.step].copy_(transition.critic_observations)
        self.actions[self.step].copy_(transition.actions)
        self.rewards[self.step].copy_(transition.rewards.view(-1, 1))
        self.dones[self.step].copy_(transition.dones.view(-1, 1))
        self.values[self.step].copy_(transition.values)
        self.actions_log_prob[self.step].copy_(transition.actions_log_prob.view(-1, 1))
        self.mu[self.step].copy_(transition.action_mean)
        self.sigma[self.step].copy_(transition.action_sigma)

        self.adversary_masks[self.step].copy_(transition.adversary_masks)
        self.adversary_actions[self.step].copy_(transition.adversary_actions)
        self.adversary_log_prob[self.step].copy_(transition.adversary_log_prob.view(-1, 1))
        self.adversary_mu[self.step].copy_(transition.adversary_mean)
        self.adversary_sigma[self.step].copy_(transition.adversary_sigma)

        self.robust_masks[self.step].copy_(transition.robust_masks)

        self.step += 1
```

**逐行解释**：
- `self.step`：当前写到第几步（0 到 23）。
- 第 64–65 行：写满 24 步还想写，就报错"缓冲区溢出"。
- `self.observations[self.step].copy_(...)`：把这一步的数据**复制**进第 `step` 行。`copy_` 带下划线，表示"原地修改"，不新开内存。
- `.view(-1, 1)`：把形状 [4096] 变成 [4096, 1]，和存储张量对齐。
- 第 66–76 行：父类原有字段。
- 第 78–84 行：GRAM 新增字段。
- `self.step += 1`：写完，指针后移。

**它被谁调用？**【推断】父类 `PPO.process_env_step`（rsl_rl 2.0）在环境走完一步后，把奖励和 done 填进 `self.transition`，再调用 `self.storage.add_transitions(self.transition)`，然后清空 transition。GRAM 没有重写 `process_env_step`，用的是父类版本。

## 2.5 `compute_returns`：GAE + 分组标准化（第 88–115 行）

这是本文件**最重要**的函数，有一个 GRAM 特有的改动。

```python
# gram_rollout_storage.py:88-98
    def compute_returns(self, last_values, gamma, lam):
        advantage = 0
        for step in reversed(range(self.num_transitions_per_env)):
            if step == self.num_transitions_per_env - 1:
                next_values = last_values
            else:
                next_values = self.values[step + 1]
            next_is_not_terminal = 1.0 - self.dones[step].float()
            delta = self.rewards[step] + next_is_not_terminal * gamma * next_values - self.values[step]
            advantage = delta + next_is_not_terminal * gamma * lam * advantage
            self.returns[step] = advantage + self.values[step]
```

**逐行解释**（对照 1.4 节的公式）：
- `advantage = 0`：最后一步之后没有"后面的优势"，初值为 0。
- `reversed(range(24))`：step = 23, 22, …, 0，**从后往前**。
- 第 91–94 行：下一个状态的估值。最后一步（step = 23）用 `last_values`，也就是走完 24 步之后那个状态的 V；其他步用 `values[step+1]`。
- `next_is_not_terminal = 1 - done`：回合结束则为 0，切断。
- `delta = r + (1−done)·γ·V_next − V`：TD 误差 δ_t。
- `advantage = delta + (1−done)·γ·λ·advantage`：递推公式 A_t = δ_t + γλ(1−done)A_{t+1}。
- `returns[step] = advantage + values[step]`：Return_t = A_t + V(s_t)。

1.4 节的手算例子就是这段代码在单个环境上的计算过程。这里所有运算都是**4096 个环境同时**做的（张量运算）。

```python
# gram_rollout_storage.py:100-115
        # Compute and normalize the advantages
        self.advantages = self.returns - self.values

        if torch.sum(self.robust_masks == 1) > 0:
            robust_mean = self.advantages[self.robust_masks == 1].mean()
            robust_std = self.advantages[self.robust_masks == 1].std()
            self.advantages[self.robust_masks == 1] = (self.advantages[self.robust_masks == 1] - robust_mean) / (
                robust_std + 1e-8
            )

        if torch.sum(self.robust_masks == 0) > 0:
            adapt_mean = self.advantages[self.robust_masks == 0].mean()
            adapt_std = self.advantages[self.robust_masks == 0].std()
            self.advantages[self.robust_masks == 0] = (self.advantages[self.robust_masks == 0] - adapt_mean) / (
                adapt_std + 1e-8
            )
```

**这段要干什么**：把优势**标准化**（减均值、除以标准差），让数值保持在 0 附近、尺度约为 1，训练更稳定。

**GRAM 的特殊之处**：**鲁棒组和自适应组分开标准化。**【代码事实】rsl_rl 原版是对所有数据一起标准化【推断】。

**为什么要分开？** 用一个例子说明：
- 鲁棒组被对抗者推，表现普遍差，优势可能都在 −3 附近；
- 自适应组表现好，优势在 +1 附近。

如果一起标准化，整体均值约 −1：
- 鲁棒组的动作大多是负优势 → 网络学到"鲁棒模式下做什么都不好"；
- 自适应组大多是正优势 → 网络学到"自适应模式下做什么都好"。

这不是我们想要的。我们想要的是：**在每种模式内部**，比平均好的动作被加强，比平均差的被削弱。分开标准化后，两组各自均值为 0，各自都有"好动作"和"坏动作"，学习信号是公平的。

**数值例子**：

| 环境 | 组 | 原始优势 | 一起标准化（均值 −1，标准差 约 2） | 分开标准化 |
|---|---|---|---|---|
| A | 鲁棒 | −2.5 | −0.75 | (−2.5 − (−3)) / 0.5 = **+1.0** |
| B | 鲁棒 | −3.5 | −1.25 | (−3.5 − (−3)) / 0.5 = **−1.0** |
| C | 自适应 | 1.5 | +1.25 | (1.5 − 1) / 0.5 = **+1.0** |
| D | 自适应 | 0.5 | +0.75 | (0.5 − 1) / 0.5 = **−1.0** |

分开标准化后，鲁棒组里相对好的 A 得到正优势，自适应组里相对差的 D 得到负优势，这才合理。

**`+ 1e-8`**：防止除以 0。

**对我们的意义**：如果改成"分组退回"，`robust_masks` 从 1 列变成多列（每组一列），这里的"按组标准化"需要重新设计。可以按"掩码组合"分组标准化（例如 00、01、10、11 四类各自标准化）。

## 2.6 `mini_batch_generator`：切小批（第 117–197 行）

```python
# gram_rollout_storage.py:117-147
    def mini_batch_generator(self, num_mini_batches, num_epochs=8):
        batch_size = self.num_envs * self.num_transitions_per_env
        mini_batch_size = batch_size // num_mini_batches
        indices = torch.randperm(num_mini_batches * mini_batch_size, requires_grad=False, device=self.device)

        observations = self.observations.flatten(0, 1)
        observations_history = self.observations_history.flatten(0, 1)
        if self.privileged_observations is not None:
            critic_observations = self.privileged_observations.flatten(0, 1)
        else:
            critic_observations = observations
        ...
        context = self.context.flatten(0, 1)

        robust_masks = self.robust_masks.flatten(0, 1)
```

**逐行解释**：
- `batch_size = 4096 × 24 = 98,304`。
- `mini_batch_size = 98,304 // 4 = 24,576`（`//` 是整除）。
- `torch.randperm(n)`：生成 0 到 n−1 的**随机排列**，用来打乱数据。注意：**只打乱一次**，5 个 epoch 用的是同一个顺序。
- `flatten(0, 1)`：把前两维 [24, 4096] 合并成 [98,304]。例如 `observations_history` 从 [24, 4096, 16, 45] 变成 [98,304, 16, 45]。合并后，"第几步、第几个环境"的信息就丢了，每条数据都是独立的一条。
- 第 124–127 行：没有单独的 critic 观测时，critic 用策略观测。

```python
# gram_rollout_storage.py:149-197（节选）
        for epoch in range(num_epochs):
            for i in range(num_mini_batches):
                start = i * mini_batch_size
                end = (i + 1) * mini_batch_size
                batch_idx = indices[start:end]

                obs_batch = observations[batch_idx]
                obs_history_batch = observations_history[batch_idx]
                ...
                context_batch = context[batch_idx]
                robust_masks_batch = robust_masks[batch_idx]

                yield (obs_batch, obs_history_batch, critic_observations_batch, rewards_batch, dones_batch,
                       actions_batch, target_values_batch, advantages_batch, returns_batch,
                       old_actions_log_prob_batch, old_mu_batch, old_sigma_batch,
                       adversary_masks_batch, adversary_actions_batch, old_adversary_log_prob_batch,
                       old_adversary_mu_batch, old_adversary_sigma_batch,
                       context_batch, robust_masks_batch)
```

**逐行解释**：
- 两层循环：外层 epoch（5 次），内层 mini-batch（4 次），共 20 次。
- `batch_idx = indices[start:end]`：第 i 份的下标，例如第 0 份是 `indices[0:24576]`。
- `observations[batch_idx]`：按下标取出这一份数据。
- `yield`：Python 的**生成器**语法。函数不会一次性返回所有数据，而是每次被 `for` 循环要数据时，"吐"出一份，然后暂停，等下一次再继续。好处是省内存、写法简洁。
- 一共吐出 **19 项**，顺序非常重要，`gram_ppo.py` 里的 `for (...) in generator` 必须按同样的顺序接收。
- `target_values_batch` 就是采样时存的 `values`，也就是 V_old，用于价值裁剪。

**小结**：
- 这个文件 = "表格 + GAE + 切小批"；
- GRAM 相对 rsl_rl 的改动：多存了历史、上下文、对抗者数据、鲁棒掩码；**优势按鲁棒 / 自适应两组分别标准化**；
- 上下文只在开头存一次，说明训练时每个环境的参数固定不变。

---

# 第三部分　`gram_ppo.py` 逐行

**这个文件要干什么**：继承 rsl_rl 的 `PPO` 类，做 GRAM 需要的几件事：
1. 采样时同时让对抗者出手（`act`）；
2. PPO 主更新（`update` 前半部分）；
3. 可选地同时训练历史编码器（`update` 中间，**默认关闭**）；
4. 训练对抗者（`update` 后半部分）；
5. 最后 5000 次迭代只训练历史编码器（`finetune`）。

## 3.1 `init_extras`：额外初始化与三个优化器（第 21–61 行）

```python
# gram_ppo.py:21-61
    def init_extras(self, context, adversary_policy, env, train_and_finetune, num_learning_epochs_finetune,
                    history_loss_actions, history_loss_robust_as_zeros, history_loss_adapt_only,
                    history_loss_epinet_separate, history_lr, adversary_update_every):

        self.context = context
        self.storage.init_extras(context)

        self.train_and_finetune = train_and_finetune
        if num_learning_epochs_finetune is not None:
            self.num_learning_epochs_finetune = num_learning_epochs_finetune
        else:
            self.num_learning_epochs_finetune = self.num_learning_epochs

        self.history_loss_actions = history_loss_actions
        self.history_loss_robust_as_zeros = history_loss_robust_as_zeros
        self.history_loss_adapt_only = history_loss_adapt_only
        self.history_loss_epinet_separate = history_loss_epinet_separate
        self.history_lr = history_lr

        self.adversary_policy = adversary_policy
        self.env = env

        self.since_adversary_update = 0
        self.adversary_update_every = adversary_update_every
        self.adversary_lr = self.learning_rate

        self.optimizer = optim.Adam(self.actor_critic.opt_params, lr=self.learning_rate)
        self.adversary_optimizer = optim.Adam(self.adversary_policy.parameters(), lr=self.adversary_lr)
        self.history_optimizer = optim.Adam(self.actor_critic.history_params, lr=self.history_lr)
```

**逐行解释**：
- `self.context`：[4096, 26]，保存一份，采样时策略要用（教师用真实上下文）。
- `self.storage.init_extras(context)`：见 2.3 节。
- `train_and_finetune`：**是否在 RL 阶段同时训练历史编码器**。命令行 `--train_and_finetune` 才打开，**默认 False**（`cli_utils.py:70`，`store_true` 类型参数默认就是 False）。
- `num_learning_epochs_finetune`：finetune 阶段每次迭代的 epoch 数；没指定就和 RL 阶段一样。
- 四个 `history_loss_*` 开关，3.7 节专门讲。
- `history_lr`：历史编码器学习率，默认 **1e-3**（`cli_utils.py:224`），**固定不变**（不参与 KL 自适应调节）。
- `adversary_update_every`：对抗者多少次迭代更新一次，默认 **10**（`cli_utils.py:147`）。
- `since_adversary_update = 0`：计数器。
- `adversary_lr = self.learning_rate`：对抗者学习率起始值等于主策略学习率，之后各自独立调节。

**三个优化器**：

| 优化器 | 负责的参数 | 学习率 | 何时使用 |
|---|---|---|---|
| `optimizer` | `opt_params`：actor、std、critic、上下文编码器（若 `robust_as_zeros=False` 还有独立的鲁棒 actor/critic） | 初始 `learning_rate`，KL 自适应 | RL 阶段每次迭代 |
| `adversary_optimizer` | 对抗者网络和它的 std | 初始同上，KL 自适应 | 每 10 次迭代 |
| `history_optimizer` | `history_params`：历史编码器 + epinet 可训练部分 | 固定 1e-3 | finetune 阶段（或开了 `train_and_finetune` 时的 RL 阶段） |

**Adam**：一种常用的梯度下降优化器，会为每个参数自动调节步长。这里不需要懂细节，记住"根据梯度更新参数"即可。

**注意**：epinet 的**先验网络**不在任何优化器里（`gram_actor_critic.py:227` 设置了 `requires_grad_(False)`），它永远不训练。这是 epinet 能判断"见没见过"的关键。

**注意**：上下文编码器 f 的参数在主 `optimizer` 里，所以 **f 是和策略一起用 PPO 训练的**（论文式 3），不是单独训练。

## 3.2 `init_storage`（第 63–83 行）

```python
# gram_ppo.py:63-83
    def init_storage(self, num_envs, num_transitions_per_env, obs_history_length,
                     actor_obs_shape, critic_obs_shape, action_shape, adversary_action_shape):
        self.storage = GRAMRolloutStorage(num_envs, num_transitions_per_env, obs_history_length,
                                          actor_obs_shape, critic_obs_shape, action_shape,
                                          adversary_action_shape, self.device)
        self.transition = GRAMRolloutStorage.Transition()
```

**解释**：用 GRAM 版本的存储代替父类的。`adversary_action_shape = [1]`（对抗者只输出一个角度，见 runner 第 49 行）。`self.transition` 是那个"装一步数据的小盒子"。

## 3.3 `act`：采样一步（第 85–112 行）

**这段要干什么**：环境每走一步之前调用一次，算出动作，同时把这一步需要的所有信息存进 `transition`。

```python
# gram_ppo.py:85-97
    def act(self, obs, critic_obs, obs_history, robust_masks):
        # Compute the actions and values
        self.transition.actions = self.actor_critic.act(obs, self.context, obs_history, robust_masks).detach()
        self.transition.values = self.actor_critic.evaluate(
            critic_obs, self.context, obs_history, robust_masks
        ).detach()
        self.transition.actions_log_prob = self.actor_critic.get_actions_log_prob(self.transition.actions).detach()
        self.transition.action_mean = self.actor_critic.action_mean.detach()
        self.transition.action_sigma = self.actor_critic.action_std.detach()
        # need to record obs and critic_obs before env.step()
        self.transition.observations = obs
        self.transition.critic_observations = critic_obs
        self.transition.observations_history = obs_history
```

**逐行解释**：
- 第 87 行：`actor_critic.act(...)` 算出动作。内部流程（见 `gram_actor_critic.py:474-482`）：
  1. 算隐变量 latent：RL 阶段 `act_from_context=True`，所以 **latent = f(context)**，用真实上下文（教师模式）；
  2. `update_distribution`：鲁棒组的环境把 latent 换成 0 向量，自适应组用 f(c)，算出高斯分布；
  3. 从分布里采样一个动作。
- `.detach()`：把结果从"计算图"上摘下来。意思是：这些数只是记录，以后不要通过它们反向传播梯度。采样阶段不训练，所以全部 detach。
- 第 88–90 行：critic 估值 V_old。同样，鲁棒组用 `[obs, 0]`，自适应组用 `[obs, f(c)]`。
- 第 91 行：这个动作在当前（旧）策略下的对数概率 log π_old(a∣s)。
- 第 92–93 行：旧策略的均值、标准差（算 KL 用）。
- 第 95–97 行：记下观测、critic 观测、历史。注释说"要在 env.step() 之前记录"，因为 step 之后 obs 就变成下一步的了。

```python
# gram_ppo.py:98-112
        # Compute adversary stats
        self.transition.adversary_actions = self.adversary_policy.act(obs).detach()
        self.transition.adversary_log_prob = self.adversary_policy.get_actions_log_prob(
            self.transition.adversary_actions
        ).detach()
        self.transition.adversary_mean = self.adversary_policy.action_mean.detach()
        self.transition.adversary_sigma = self.adversary_policy.action_std.detach()

        adversary_masks = self.adversary_policy.generate_adversary_masks(obs).detach()
        self.transition.adversary_masks = adversary_masks * robust_masks
        self.transition.robust_masks = robust_masks

        self.adversary_update_sim(self.transition.adversary_actions, self.transition.adversary_masks)

        return self.transition.actions
```

**逐行解释**：
- 第 99 行：对抗者看同样的观测 obs，输出一个**角度** θ（从高斯分布采样）。对抗者网络是 MLP 512-256-128，输出 1 维（`gram_adversary.py:44-55`）。
- 第 100–104 行：对抗者的对数概率、均值、标准差，和主策略一样，为以后的 PPO 更新做准备。
- 第 106 行：`generate_adversary_masks`：对每个环境**抛一次硬币**，以概率 `adversary_prob`（默认 **0.05**）得到 1，否则 0（`gram_adversary.py:135-138`，`torch.bernoulli` 就是按概率抛硬币）。
- 第 107 行：**`adversary_masks * robust_masks`**：只有**鲁棒组**的环境才可能被推。自适应组的 robust_masks = 0，乘完一定是 0。
- 第 108 行：记下这一步的分配。
- 第 110 行：把对抗者的决定"告诉"仿真环境（见 3.4 节）。
- 返回动作，交给 runner 去执行 `env.step(actions)`。

**数值例子**：4096 个环境里，鲁棒组 2048 个。每步约 2048 × 0.05 ≈ **102 个**环境被推一下。

## 3.4 `adversary_update_sim`：把推力交给仿真器（第 114–117 行）

```python
# gram_ppo.py:114-117
    def adversary_update_sim(self, adversary_actions, adversary_masks):
        adversary_cfg = self.env.unwrapped.event_manager.get_term_cfg("adversary_push")
        adversary_cfg.params["adversary_actions"] = self.adversary_policy.angle_to_vector(adversary_actions)
        adversary_cfg.params["adversary_masks"] = adversary_masks
```

**逐行解释**：
- Isaac Lab 用"事件管理器（event manager）"管理各种事件，例如复位、随机化、推力。GRAM 在环境配置里注册了一个叫 `adversary_push` 的事件（`unitree_go2_custom_env.py:206-211`）。
- 第 115 行：拿到这个事件的配置对象。
- 第 116 行：把角度转换成二维向量，写进事件参数。`angle_to_vector`（`gram_adversary.py:140-149`）做两件事：
  1. θ → (cos θ, sin θ)，一个单位方向；
  2. 默认 `adversary_random_scale=True`，再乘一个 **[0, 当前最大强度] 之间的随机数**。当前最大强度随训练从 0 增到 1（3.8 节、runner 第 360 行）。
- 第 117 行：把"谁被推"写进去。

**之后发生什么**：仿真器在执行 `env.step` 时会调用事件函数 `adversarial_push_by_setting_velocity`（`envs_utils.py:270-298`），对被选中的环境：

```
机身水平速度 += 1.0（adversary_magnitude）× 掩码 × 方向向量 × 随机强度
```

**注意**：这是**直接改速度**，相当于一瞬间被踢了一脚，而不是持续施加一个力。论文写的是 "external forces"，代码实现是速度冲量。

【推断】这个事件配置成 `mode="interval"`，`interval_range_s=(0.0, 0.0)`，应该是每个环境步都触发一次；但只有掩码为 1 的环境会被改速度，所以等效于"每步 5% 的鲁棒环境被踢"。需在服务器上确认 Isaac Lab interval 事件在间隔为 0 时的行为。

## 3.5 `compute_returns`（第 119–121 行）

```python
# gram_ppo.py:119-121
    def compute_returns(self, last_critic_obs, obs_history, robust_masks):
        last_values = self.actor_critic.evaluate(last_critic_obs, self.context, obs_history, robust_masks).detach()
        self.storage.compute_returns(last_values, self.gamma, self.lam)
```

**解释**：
- 24 步走完后，用 critic 给"第 25 步的状态"估个值，作为 `last_values`（1.4 节例子里的 V(s_3) = 1.2）。
- 注意传入的是**当前的** `robust_masks`，所以 `last_values` 按当前分配计算。
- 然后调用存储的 GAE（2.5 节）。
- γ、λ 来自 rsl_rl 配置，Go2 默认 0.99、0.95【推断】。

## 3.6 `update`：PPO 主更新（第 123–226 行）

### 3.6.1 统计量初始化（第 124–140 行）

```python
# gram_ppo.py:124-140
        mean_value_loss = 0
        mean_surrogate_loss = 0
        mean_history_loss = 0
        mean_latent_error_l2 = 0
        mean_latent_error_kl = 0
        mean_latent_l2 = 0
        mean_latent_abs = 0
        mean_latent_max = 0
        mean_latent_std = 0
        mean_adversary_l2 = 0
        mean_adversary_abs = 0
        mean_adversary_max = 0
        mean_uncertainty_metric = 0
```

这些只是**记录用**的累加器，不影响训练。每个 mini-batch 加一次，最后除以 20 得到平均值，打印到日志和 TensorBoard。

### 3.6.2 取数据（第 142–163 行）

```python
# gram_ppo.py:142-163
        generator = self.storage.mini_batch_generator(self.num_mini_batches, self.num_learning_epochs)
        for (obs_batch, obs_history_batch, critic_obs_batch, rewards_batch, dones_batch, actions_batch,
             target_values_batch, advantages_batch, returns_batch, old_actions_log_prob_batch,
             old_mu_batch, old_sigma_batch, adversary_masks_batch, adversary_actions_batch,
             old_adversary_log_prob_batch, old_adversary_mu_batch, old_adversary_sigma_batch,
             context_batch, robust_masks_batch) in generator:
```

**解释**：从 2.6 节的生成器里，一次取一份 mini-batch（24,576 条）。19 项和 `yield` 的顺序一一对应。循环共执行 20 次。

### 3.6.3 用新参数重新算一遍（第 164–171 行）

```python
# gram_ppo.py:164-171
            self.actor_critic.act(obs_batch, context_batch, obs_history_batch, robust_masks_batch)
            actions_log_prob_batch = self.actor_critic.get_actions_log_prob(actions_batch)
            value_batch = self.actor_critic.evaluate(
                critic_obs_batch, context_batch, obs_history_batch, robust_masks_batch
            )
            mu_batch = self.actor_critic.action_mean
            sigma_batch = self.actor_critic.action_std
            entropy_batch = self.actor_critic.entropy
```

**逐行解释**：
- 第 164 行：用**当前参数**重新算一遍分布。返回值（采样的动作）没用，目的是更新 `self.distribution`。这次**不 detach**，因为要反向传播。
- 第 165 行：**采样时那个动作** `actions_batch` 在**新分布**下的对数概率 log π_new(a∣s)。
- 第 166–168 行：新的 V(s)。
- 第 169–171 行：新的均值、标准差、熵。

**`robust_masks_batch` 在这里如何起作用**（`gram_actor_critic.py:449-472`）：

```python
# gram_actor_critic.py:449-472（GRAM 默认 robust_as_zeros=True 时）
robust_latent = torch.zeros_like(latent.detach())
robust_actor_input = torch.cat([observations, robust_latent], dim=-1)
robust_mean = self.robust_actor(robust_actor_input)   # robust_actor 就是 actor 本身
adapt_mean = self.actor(actor_input)                   # actor_input = [obs, f(c)]
mean = robust_masks * robust_mean + (1 - robust_masks) * adapt_mean
log_std = robust_masks * self.robust_log_std + (1 - robust_masks) * self.log_std
```

- `robust_as_zeros=True` 时，`self.robust_actor = self.actor`，`self.robust_log_std = self.log_std`（`gram_actor_critic.py:273-279`），**同一个网络、同一个 std**；
- 鲁棒组（mask = 1）：均值 = actor([obs, **0**])；
- 自适应组（mask = 0）：均值 = actor([obs, **f(c)**])；
- 标准差两组相同；
- critic 同理：鲁棒组 critic([obs, 0])，自适应组 critic([obs, f(c)])。

**梯度怎么流**：
- 鲁棒组的数据：梯度流向 actor、critic、std，**不流向上下文编码器 f**（输入是 0，而且 `zeros_like(latent.detach())` 断开了）；
- 自适应组的数据：梯度流向 actor、critic、std，**也流向 f**。所以 f 学会"怎样编码上下文，才能让策略表现更好"。

**一句话**：同一个 actor 网络，同时被"有环境信息"和"没有环境信息 + 被推"两类数据训练，这就是论文式 (10) $L^{GRAM}_{RL} = L^{ID}_{RL} + L^{OOD}_{RL}$ 在代码里的样子：**不是两个损失分别计算再相加，而是两类数据混在同一个 mini-batch 里，一起算一个损失。**

### 3.6.4 KL 与自适应学习率（第 173–191 行）

```python
# gram_ppo.py:173-191
            if self.desired_kl is not None and self.schedule == "adaptive":
                with torch.inference_mode():
                    kl = torch.sum(
                        torch.log(sigma_batch / old_sigma_batch + 1.0e-5)
                        + (torch.square(old_sigma_batch) + torch.square(old_mu_batch - mu_batch))
                        / (2.0 * torch.square(sigma_batch))
                        - 0.5,
                        axis=-1,
                    )
                    kl_mean = torch.mean(kl)

                    if kl_mean > self.desired_kl * 2.0:
                        self.learning_rate = max(1e-5, self.learning_rate / 1.5)
                    elif kl_mean < self.desired_kl / 2.0 and kl_mean > 0.0:
                        self.learning_rate = min(1e-2, self.learning_rate * 1.5)

                    for param_group in self.optimizer.param_groups:
                        param_group["lr"] = self.learning_rate
```

**解释**：就是 1.8 节的公式和规则。
- `torch.inference_mode()`：这段只是计算 KL、调学习率，不需要梯度，关掉梯度追踪更省资源。
- `+ 1.0e-5`：防止 log(0)。
- `axis=-1`：对 12 个动作维度求和。
- 学习率是**每个 mini-batch 都可能调整一次**，所以一次迭代里最多变 20 次。
- 最后把新学习率写进优化器。

**注意**：KL 是对**所有数据**（鲁棒组和自适应组一起）算的平均值，两组共用一个学习率。

### 3.6.5 裁剪策略损失（第 193–199 行）

```python
# gram_ppo.py:193-199
            ratio = torch.exp(actions_log_prob_batch - torch.squeeze(old_actions_log_prob_batch))
            surrogate = -torch.squeeze(advantages_batch) * ratio
            surrogate_clipped = -torch.squeeze(advantages_batch) * torch.clamp(
                ratio, 1.0 - self.clip_param, 1.0 + self.clip_param
            )
            surrogate_loss = torch.max(surrogate, surrogate_clipped).mean()
```

**逐行解释**（对照 1.5 节）：
- 第 194 行：ratio = exp(log π_new − log π_old)。`torch.squeeze` 把 [N, 1] 变成 [N]，对齐形状。
- 第 195 行：不裁剪项 −A × ratio。
- 第 196–198 行：裁剪项 −A × clip(ratio, 0.8, 1.2)（`clip_param` 默认 0.2【推断】）。
- 第 199 行：逐条取 max，再对 24,576 条取平均。

这里的优势 A 已经按组标准化过（2.5 节）。

### 3.6.6 价值损失（第 201–210 行）

```python
# gram_ppo.py:201-210
            if self.use_clipped_value_loss:
                value_clipped = target_values_batch + (value_batch - target_values_batch).clamp(
                    -self.clip_param, self.clip_param
                )
                value_losses = (value_batch - returns_batch).pow(2)
                value_losses_clipped = (value_clipped - returns_batch).pow(2)
                value_loss = torch.max(value_losses, value_losses_clipped).mean()
            else:
                value_loss = (returns_batch - value_batch).pow(2).mean()
```

**解释**：1.6 节的公式。`target_values_batch` 是 V_old。价值裁剪和策略裁剪**共用同一个 `clip_param`**。

### 3.6.7 总损失与梯度更新（第 212–226 行）

```python
# gram_ppo.py:212-226
            loss = surrogate_loss + self.value_loss_coef * value_loss - self.entropy_coef * entropy_batch.mean()

            # Gradient step
            self.optimizer.zero_grad()
            loss.backward()
            nn.utils.clip_grad_norm_(self.actor_critic.ac_adapt_params, self.max_grad_norm)
            if not self.actor_critic.robust_as_zeros:
                nn.utils.clip_grad_norm_(self.actor_critic.ac_robust_params, self.max_grad_norm)
            nn.utils.clip_grad_norm_(self.actor_critic.context_params, self.max_grad_norm)
            self.optimizer.step()
            with torch.no_grad():
                self.actor_critic.enforce_minimum_std()

            mean_value_loss += value_loss.item()
            mean_surrogate_loss += surrogate_loss.item()
```

**逐行解释**：
- 第 212 行：**总损失 = 策略损失 + c₁ × 价值损失 − c₂ × 熵**。Go2 默认 c₁ = `value_loss_coef` = 1.0，c₂ = `entropy_coef` = 0.01【推断】。
- 第 215 行：`zero_grad()`：把上一次的梯度清零（PyTorch 的梯度默认会累加）。
- 第 216 行：`backward()`：**反向传播**，自动算出每个参数的梯度。
- 第 217–220 行：**梯度裁剪**：如果梯度的总长度（范数）超过 `max_grad_norm`（默认 1.0【推断】），就按比例缩小，防止一步走太远。GRAM 把参数分成几组**分别**裁剪：
  - `ac_adapt_params`：actor、std、critic；
  - `ac_robust_params`：独立的鲁棒 actor/critic（只有 `robust_as_zeros=False` 的算法才有，例如 robust_rl、domain_rand、gram_modular）；
  - `context_params`：上下文编码器。
  - **这里有一个代码层面的问题，见第五部分第 1 条。**
- 第 221 行：`optimizer.step()`：按梯度更新参数。
- 第 222–223 行：`enforce_minimum_std`：把动作标准差限制在 [0.01, 10]（`gram_actor_critic.py:664-672`），防止 σ 变成 0（不再探索）或爆炸。
- 第 225–226 行：记录损失。`.item()` 把单元素张量转成 Python 数字。

## 3.7 `update`：历史编码器分支（第 228–342 行）

### 3.7.1 默认情况：不训练历史编码器

```python
# gram_ppo.py:229
            if self.train_and_finetune:
                ...（第 230–334 行：训练历史编码器）
            else:
                with torch.no_grad():
                    latent_context = self.actor_critic.encode_context(context_batch)

                history_loss = torch.zeros_like(value_loss)

            mean_history_loss += history_loss.item()
```

（第 336–342 行）

**【代码事实】默认只在 finetune 阶段训练历史编码器的依据**：
1. `train_and_finetune` 来自命令行 `--train_and_finetune`（`cli_utils.py:70`，`store_true`，**默认 False**），由 `cli_utils.py:667` 写入配置；
2. 所以 `update()` 里 **第 229 行的 if 不成立**，走第 336–340 行的 else 分支：只算一下 f(c) 用于统计，`history_loss` 设为 0；
3. 历史编码器只在 `finetune()`（第 469 行起）里训练，而 `finetune()` 只在 runner 的最后 `finetune_iterations`（默认 5000）次迭代里调用（`gram_on_policy_runner.py:356-357`）。

**服务器日志印证**：冒烟测试 `train_v5.log` 中，第 0、1 次迭代 `History loss: 0.0000`（RL 阶段），第 2 次迭代 `History loss: 14.5718` 且 `Value function loss: 0.0000`（finetune 阶段，不做 PPO，所以价值损失记为 0）。

**这和论文一致**：论文说"RL training is followed by a supervised learning phase"，先 RL 后监督。

如果打开 `--train_and_finetune`，RL 阶段每个 mini-batch 也会训练历史编码器，代码逻辑和 `finetune()` 基本相同，所以下面只在 3.10 节详细讲 `finetune()` 的版本，这里列出两者的**差别**：

| 差别 | `update()` 里的版本（第 229–334 行） | `finetune()` 里的版本（第 508–594 行） |
|---|---|---|
| 是否支持 `history_loss_adapt_only` | 支持 | **不支持**（这个开关在 finetune 里被忽略） |
| `history_action_loss` 加进损失的位置 | 第 272 行缩进在 `else` 里，见第五部分第 3 条 | 正常 |
| 数据 | RL 阶段的数据（latent 来自 f(c)，有对抗者） | finetune 阶段的数据（latent 来自历史编码器，无对抗者） |

### 3.7.2 四个 `history_loss_*` 开关

| 开关 | 命令行 | 默认值 | 打开后的含义 |
|---|---|---|---|
| `history_loss_epinet_separate` | `--history_loss_include_epinet` 取反（`cli_utils.py:742`） | **True** | 损失拆成两项：base 网络回归 f(c) + epinet 修正项压向 0 |
| `history_loss_actions` | `--history_loss_actions` | False | 额外加一项"动作模仿"损失：用估计 latent 算出的动作，要和用真实 f(c) 算出的动作一致 |
| `history_loss_robust_as_zeros` | `--history_loss_robust_as_zeros` | False | 鲁棒组数据的回归目标改成 0 向量（而不是 f(c)） |
| `history_loss_adapt_only` | `--history_loss_adapt_only` | False | 只用自适应组的数据计算损失（只在 `update()` 里有效） |

**GRAM 默认配置下实际生效的损失**（finetune 阶段）：

$$L_{hist} = \underbrace{\|f(c) - \phi_{base}(h)\|^2}_{\text{base 回归}} + \underbrace{\frac{1}{8}\sum_{i=1}^{8}\|\phi_{epi}(\tilde h, \varepsilon_i)\|^2}_{\text{epinet 修正项压向 0}}$$

对所有数据（鲁棒组和自适应组）取平均。

## 3.8 `update`：对抗者更新（第 360–418 行）

**这段要干什么**：训练对抗者"更会捣乱"，即学会往哪个方向推最能让机器狗表现变差。

### 3.8.1 什么时候更新

```python
# gram_ppo.py:361-363
            if (
                self.since_adversary_update % self.adversary_update_every == 0
            ) and self.adversary_policy.train_adversary:
```

以及迭代结束时（第 442–443 行）：

```python
        self.since_adversary_update += 1
        self.since_adversary_update = self.since_adversary_update % self.adversary_update_every
```

**解释**：
- `since_adversary_update` 在**每次 `update()` 结束时 +1**，并对 10 取余，所以它在 0, 1, …, 9 之间循环；
- 只有它等于 0 的那次迭代，对抗者才更新，而且在那次迭代的 **20 个 mini-batch 里每个都更新一次**；
- 所以：**每 10 次迭代里，有 1 次迭代更新对抗者（共 20 步梯度）**。
- `train_adversary`：在对抗者构造时决定（`gram_adversary.py:78-81`）：`adversary_prob == 0` 或"随机角度"模式时为 False，不训练。GRAM 默认 `adversary_prob = 0.05`，所以训练。情境 RL 和域随机化的 `adversary_prob` 被设为 0（`cli_utils.py:602、610`），对抗者不训练也不推。

**为什么对抗者更新得这么少？** 代码没有说明。常见的理由是：对抗训练容易不稳定，让主策略多学几次，对抗者少学几次，避免对抗者太强把主策略"压垮"。

### 3.8.2 对抗者的"奖励"从哪里来

对抗者没有自己的奖励函数。它的学习信号是**主策略优势的相反数**：

```python
# gram_ppo.py:392-401
                adversary_batch_size = max(adversary_masks_batch.sum().item(), 1.0)

                # center adversary advantages
                adversary_advantages_batch_mean = (
                    advantages_batch * adversary_masks_batch
                ).sum() / adversary_batch_size
                adversary_advantages_batch = (
                    (advantages_batch - adversary_advantages_batch_mean) * adversary_masks_batch * -1
                )
```

**逐行解释**：
- 第 393 行：这个 mini-batch 里**真正被推过**的数据有多少条（掩码为 1 的数量）。至少取 1，防止除 0。
- 第 396–398 行：被推的那些步，主策略优势的**平均值**。
- 第 399–401 行：对抗者的优势 = −（主策略优势 − 平均值）× 掩码。
  - **减平均值**（居中）：只比较"被推的这些步之间谁更好"；
  - **乘 −1**：主策略表现越差，对抗者优势越大 → 对抗者学会做让主策略变差的事；
  - **乘掩码**：没被推的步，对抗者的选择没有产生影响，优势设为 0，不参与学习。

**数值例子**：一个 mini-batch 里有 3 步被推，主策略优势分别是 +0.5、−1.0、−2.0：
- 平均值 = (0.5 − 1.0 − 2.0) / 3 = −0.833；
- 对抗者优势 = −(0.5 + 0.833) = **−1.33**，−(−1.0 + 0.833) = **+0.17**，−(−2.0 + 0.833) = **+1.17**；
- 结论：第 3 步的推法让机器狗最难受，对抗者以后多用这个方向。

**一个值得注意的地方**：主策略的优势反映的是**整条后续轨迹**的好坏（GAE），不只是被推那一瞬间。所以对抗者学的是"推了之后，接下来机器狗整体表现变差"。

### 3.8.3 对抗者的 PPO 损失（第 364–418 行）

```python
# gram_ppo.py:364-367
                self.adversary_policy.act(obs_batch)
                adversary_log_prob_batch = self.adversary_policy.get_actions_log_prob(adversary_actions_batch)
                adversary_mu_batch = self.adversary_policy.action_mean
                adversary_sigma_batch = self.adversary_policy.action_std
```

**解释**：和主策略一样，用新参数重算对抗者分布，取"当时采样的角度"的新对数概率。

第 369–390 行：对抗者自己的 KL 和学习率调节，规则与主策略完全相同，但用的是 `adversary_lr` 和 `adversary_optimizer`。

```python
# gram_ppo.py:403-418
                adversary_ratio = torch.exp(adversary_log_prob_batch - torch.squeeze(old_adversary_log_prob_batch))
                adversary_surrogate = -torch.squeeze(adversary_advantages_batch) * adversary_ratio
                adversary_surrogate_clipped = -torch.squeeze(adversary_advantages_batch) * torch.clamp(
                    adversary_ratio, 1.0 - self.clip_param, 1.0 + self.clip_param
                )
                adversary_loss = (
                    torch.max(adversary_surrogate, adversary_surrogate_clipped).sum() / adversary_batch_size
                )

                self.adversary_optimizer.zero_grad()
                adversary_loss.backward()
                nn.utils.clip_grad_norm_(self.adversary_policy.parameters(), self.max_grad_norm)
                self.adversary_optimizer.step()
                with torch.no_grad():
                    self.adversary_policy.enforce_minimum_std()
```

**解释**：
- 和主策略一样的裁剪损失；
- 区别：**`.sum() / adversary_batch_size`**，只对被推的那些步取平均（没被推的步优势为 0，对求和没有贡献），而不是对 24,576 条全部取平均。否则只有 5% × 一半 ≈ 2.5% 的数据有信号，平均后信号会非常弱；
- **对抗者没有价值网络和价值损失**，它直接借用主策略的优势；
- 对抗者的梯度裁剪这里用的是 `self.adversary_policy.parameters()`，每次调用都会重新生成，所以**裁剪有效**（对比第五部分第 1 条）。

### 3.8.4 对抗者强度的课程

对抗者能推多狠，由 `adversary_max_scale_cur` 决定。它在 runner 里每次 RL 迭代后更新（`gram_on_policy_runner.py:360`）：

```python
self.alg.adversary_policy.update_magnitude((it - start_iter + 1) / (finetune_start_iter - start_iter))
```

`update_magnitude`（`gram_adversary.py:151-154`）：

$$\text{scale}_{cur} = \text{start} + (1 - \text{start}) \times \text{progress}$$

默认 start = 0（`cli_utils.py:143`），所以**最大强度从 0 线性增长到 1**。第 1 次迭代后为 1/10000，第 5000 次为 0.5，第 10000 次为 1.0。每次推的实际强度再在 [0, 当前最大强度] 里随机取。乘上 `adversary_magnitude = 1.0`，单位是 m/s。

这就是论文说的"the impact of the force on linear velocity increases from 0.0 to 1.0 meters per second over the course of training"。

## 3.9 `update`：统计量与收尾（第 344–467 行）

```python
# gram_ppo.py:344-358
            if self.train_and_finetune:
                mean_latent_error_l2 += latent_squared_error.mean().item()
                mean_latent_error_kl += history_action_loss.mean().item()

            mean_latent_l2 += torch.norm(latent_context, dim=-1).mean().item()
            mean_latent_abs += torch.abs(latent_context).mean().item()
            mean_latent_max += torch.abs(latent_context).amax(dim=-1).mean().item()
            mean_latent_std += torch.std(latent_context, dim=0).mean().item()

            mean_adversary_l2 += torch.norm(adversary_actions_batch, dim=-1).mean().item()
            mean_adversary_abs += torch.abs(adversary_actions_batch).mean().item()
            mean_adversary_max += torch.abs(adversary_actions_batch).amax().item()

            uncertainty_metric = self.actor_critic.calculate_uncertainty_metric(obs_history_batch)
            mean_uncertainty_metric += uncertainty_metric.mean().item()
```

**每个统计量的含义**（会出现在 TensorBoard 的 `Update/` 下）：

| 统计量 | 含义 | 怎么看 |
|---|---|---|
| `mean_latent_l2` | f(c) 的平均长度 ‖z‖ | 训练初期接近 0（初始化增益 1e-4），之后变大，说明 f 学会了"离开 0" |
| `mean_latent_abs` | f(c) 各维绝对值的平均 | 同上 |
| `mean_latent_max` | f(c) 最大那一维的绝对值 | 看是否有某一维特别大 |
| `mean_latent_std` | 不同环境之间 f(c) 的差异 | 越大说明 f 越能区分不同环境；接近 0 说明 f 没学到东西 |
| `mean_latent_error_l2` | ‖f(c) − 估计‖² | 只在开了 `train_and_finetune` 时有值 |
| `mean_latent_error_kl` | 动作模仿误差 ‖μ_context − μ_history‖²（名字叫 kl，但实际算的是均值的平方误差） | 同上 |
| `mean_adversary_l2/abs/max` | 对抗者角度的大小 | 角度本身的大小意义不大，主要用于调试 |
| `uncertainty_metric_ave` | epinet 方差总和的平均值 | RL 阶段历史编码器没训练，这个数没有意义；finetune 阶段应逐渐下降 |
| `mean_adapt_std` | 自适应模式的动作标准差 | 训练中逐渐下降，表示策略越来越确定 |
| `mean_robust_std` | 鲁棒模式的动作标准差 | GRAM 默认和上一项是同一个参数 |
| `mean_adversary_std` | 对抗者的标准差 | |

第 420–438 行：所有累加值除以 `num_updates = 5 × 4 = 20`，得到平均值。

第 440 行：`self.storage.clear()`：【推断】父类方法，把 `step` 指针归零，准备下一次迭代写入（不清空内容，直接覆盖）。

第 442–443 行：对抗者计数器 +1 并取余（3.8.1 节）。

第 445–467 行：打包成两个字典 `loss_stats`、`update_stats` 返回给 runner，runner 的 `log()` 把它们写进日志。

## 3.10 `finetune`：只训练历史编码器（第 469–646 行）

**这段要干什么**：论文 Section V-b 的"监督学习阶段"：让历史编码器 + epinet 从 16 帧历史里估计出 f(c)，并且让 epinet 在训练见过的历史上输出稳定（方差小）。

**和 `update()` 的根本区别**：**完全不做 PPO**。策略、critic、上下文编码器、对抗者全部不动，只更新 `history_params`。

### 3.10.1 取数据（第 485–506 行）

```python
# gram_ppo.py:485
        generator = self.storage.mini_batch_generator(self.num_mini_batches, self.num_learning_epochs_finetune)
```

和 `update()` 一样从缓冲区取数据，但 epoch 数用 `num_learning_epochs_finetune`（默认等于 RL 阶段的 epoch 数）。

**这些数据是怎么采的？** 见 runner 篇。简单说：finetune 阶段 `act_from_context = False`，所以采样时策略用的是**历史编码器的估计**（学生模式），并且对抗者关闭。这对应论文"Data collection uses the student policy"以及"We do not apply an adversary during the supervised learning phase"。

### 3.10.2 回归目标（第 508–518 行）

```python
# gram_ppo.py:508-518
            # History encoder loss
            with torch.no_grad():
                latent_context = self.actor_critic.encode_context(context_batch)
                if self.history_loss_robust_as_zeros and self.actor_critic.robust_as_zeros:
                    robust_latent_context = torch.zeros_like(latent_context.detach())
                    latent_context = (
                        robust_masks_batch * robust_latent_context + (1 - robust_masks_batch) * latent_context
                    )

                self.actor_critic.update_distribution(obs_batch, latent_context, robust_masks_batch)
                mu_context = self.actor_critic.action_mean
```

**逐行解释**：
- `torch.no_grad()`：这一段只是算目标，不需要梯度。上下文编码器 f 在这个阶段**冻结**。
- 第 510 行：**目标 = f(c)**，也就是教师的隐变量。
- 第 511–515 行：只有打开 `history_loss_robust_as_zeros` 才执行（默认关闭）：鲁棒组的目标改成 0。默认情况下，**鲁棒组的数据也回归 f(c)**。
- 第 517–518 行：算出"用真实 f(c) 时策略会输出的动作均值" `mu_context`，后面动作模仿损失要用（默认只用来记录）。

### 3.10.3 epinet 的前向（第 520–521 行）

```python
# gram_ppo.py:520-521
            if self.actor_critic.history_epinet:
                latent_history_all, latent_base, epinet_all = self.actor_critic.encode_history_epinet(obs_history_batch)
```

调用 `gram_actor_critic.py:622-662` 的 `encode_history_epinet`，返回三样东西：

| 返回值 | 形状（mini-batch 24,576） | 含义 |
|---|---|---|
| `latent_base` | [24576, 8] | base 网络的输出 φ_base(h) |
| `epinet_all` | [8, 24576, 8] | 8 个随机样本下 epinet 的修正项 φ_epi(h̃, ε_i) |
| `latent_history_all` | [8, 24576, 8] | 8 个样本的完整输出 = base + 修正项 |

第一维的 8 是随机样本数 N，最后一维的 8 是隐变量维度 d。

### 3.10.4 回归损失（第 522–531 行）

```python
# gram_ppo.py:522-531
                if self.history_loss_epinet_separate:
                    epi_squared_error = epinet_all.pow(2).sum(dim=-1).mean(dim=0)
                    latent_squared_error = (latent_context - latent_base).pow(2).sum(dim=-1)
                    history_squared_error = latent_squared_error + epi_squared_error
                else:
                    latent_squared_error = (latent_context - latent_history_all).pow(2).sum(dim=-1).mean(dim=0)
                    epi_squared_error = torch.zeros_like(latent_squared_error)
                    history_squared_error = latent_squared_error

                history_loss = history_squared_error.mean()
```

**默认走第一个分支（`history_loss_epinet_separate=True`）**：
- 第 523 行：epinet 修正项的平方长度，对 8 维求和（`sum(dim=-1)`），再对 8 个样本平均（`mean(dim=0)`）。→ 形状 [24576]。
- 第 524 行：base 输出和目标的平方误差，对 8 维求和。→ 形状 [24576]。
- 第 525 行：两项相加。
- 第 531 行：对 24,576 条取平均，得到一个标量损失。

**这两项分别在干什么**：
1. **base 回归项**：让 base 网络学会从历史估计 f(c)，这就是普通 RMA 的学生训练（论文式 4）。
2. **epinet 压零项**：让 epinet 的修正项在训练数据上**接近 0**。回忆 epinet 的结构：修正项 = 可训练网络输出 − 固定先验网络输出，再和随机向量 ε 做点积（`mlp_dot`）。要让它接近 0，可训练网络就必须学会**在训练见过的历史上抵消先验网络**。没见过的历史上没有被训练抵消，修正项会随 ε 变化 → 8 个样本分散 → 方差大 → 不确定性高。

**另一个分支（`--history_loss_include_epinet`）**：直接让 8 个完整输出都去回归 f(c)，再对样本平均，这和论文式 (8) 的写法字面一致。

**两种写法的关系**（数学推导，属于我们的分析）：设 b = base 输出，e_i = 第 i 个修正项，y = 目标。

$$\frac1N\sum_i\|y - (b + e_i)\|^2 = \|y-b\|^2 - 2(y-b)^\top\bar e + \frac1N\sum_i\|e_i\|^2,\qquad \bar e = \frac1N\sum_i e_i$$

默认的"分开"写法就是去掉了中间的交叉项。在 `mlp_dot` 结构下，修正项对 ε 是线性的，ε 的均值为 0，所以 ē 在样本足够多时接近 0，两种写法近似等价。分开写的好处是：base 和 epinet 的训练互不干扰，base 专心回归，epinet 专心压零。论文式 (8) 与默认代码在写法上不完全相同，但目标一致。

**梯度流向**：
- base 回归项 → 历史编码器（`history_encoder`）的全部参数；
- epinet 压零项 → 只流向 `history_epinet_trainable`。因为 epinet 的输入特征在 `encode_history_epinet` 里做了 `.detach()`（`gram_actor_critic.py:626-632`），梯度不会传回历史编码器。这就是论文说的 "with gradients stopped as in [8]"。

### 3.10.5 动作模仿项（第 533–569 行）

```python
# gram_ppo.py:533-545（默认分支）
                if self.history_loss_epinet_separate:
                    if self.history_loss_actions:
                        self.actor_critic.update_distribution(obs_batch, latent_base, robust_masks_batch)
                        mu_history = self.actor_critic.action_mean
                        history_action_loss = (mu_context - mu_history).pow(2).sum(dim=-1)

                        history_action_loss_ave = history_action_loss.mean()
                        history_loss += history_action_loss_ave
                    else:
                        with torch.no_grad():
                            self.actor_critic.update_distribution(obs_batch, latent_base, robust_masks_batch)
                            mu_history = self.actor_critic.action_mean
                            history_action_loss = (mu_context - mu_history).pow(2).sum(dim=-1)
```

**解释**：
- **动作模仿**：比较"用估计的 latent 时策略的动作均值"和"用真实 f(c) 时的动作均值"。这个想法是：latent 估计得不完全准没关系，只要算出来的**动作**一样就行。
- 默认 `history_loss_actions=False`，走 `else`：只在 `no_grad` 下算一下，**不加进损失**，仅用于记录（日志里的 `mean_latent_error_kl`）。
- 打开时加进损失，梯度会穿过 actor 流到历史编码器（actor 本身不在 `history_optimizer` 里，所以 actor 参数不会被更新）。

第 546–569 行是 `history_loss_epinet_separate=False` 时的对应版本：把观测复制 8 份（对应 8 个样本），用 8 个完整输出各算一次动作，再平均。

第 571–588 行：`history_epinet=False` 的算法（如情境 RL）走这里：没有 epinet，只有普通的历史编码器回归。

### 3.10.6 梯度更新（第 590–594 行）

```python
# gram_ppo.py:590-594
            self.history_optimizer.zero_grad()
            history_loss.backward()
            nn.utils.clip_grad_norm_(self.actor_critic.history_params, self.max_grad_norm)
            self.history_optimizer.step()
```

只更新 `history_params`（历史编码器 + epinet 可训练部分），学习率固定 1e-3。

第 596–646 行：统计量累加、求平均、清空缓冲区、返回，和 `update()` 相同。新增 `mean_epi_error_l2`：epinet 修正项的平均平方长度，**这个数应该随 finetune 逐渐下降**，表示 epinet 在训练数据上越来越"安静"。`mean_value_loss`、`mean_surrogate_loss` 在 finetune 里从未累加，所以日志里永远是 0（第 611–612 行）。

### 3.10.7 默认配置下，finetune 一次 mini-batch 的完整计算

```
输入：obs_history_batch [24576, 16, 45]，context_batch [24576, 26]

① 目标：  z* = f(context)                                [24576, 8]    不求梯度
② base：  b  = history_encoder(history)                   [24576, 8]
③ 特征：  feat = [展平历史 720 维, base 倒数第二层 128 维]    [24576, 848]  detach
④ 采样：  ε_1..ε_8 ~ N(0, I_8)                            [8, 8]        所有数据共用这 8 个
⑤ epinet：对每个 ε_i：
          d_i = trainable([feat, ε_i]) − prior([feat, ε_i])   [24576, 64] → reshape [24576, 8, 8]
          e_i = d_i · ε_i（最后一维点积）                    [24576, 8]
⑥ 损失：  L = mean( ‖z* − b‖² + mean_i ‖e_i‖² )
⑦ 更新：  history_encoder + history_epinet_trainable，Adam，lr = 1e-3
```

（第 ③ 步 720 = 16 × 45，按观测维度 45 推算【推断】。）

---

# 第四部分　超参数总表

| 参数 | 值 | 来源 | 确定程度 |
|---|---|---|---|
| 环境数 | 4096 | `cli_utils.py:27` | 代码事实 |
| 每次迭代步数 `num_steps_per_env` | 24 | 继承 Isaac Lab `UnitreeGo2RoughPPORunnerCfg` | 【推断】 |
| RL 迭代 | 10,000 | `cli_utils.py:29`；`unitree_go2_custom_env.py:87` | 代码事实 |
| finetune 迭代 | 5,000 | `cli_utils.py:68` | 代码事实 |
| 保存间隔 | 5,000 | `unitree_go2_custom_env.py:88` | 代码事实 |
| 观测标准化 | 开启 | `cli_utils.py:696`（除非 `--no_empirical_normalization`） | 代码事实 |
| γ、λ | 0.99、0.95 | Isaac Lab Go2 默认 | 【推断】 |
| clip ε | 0.2 | 同上 | 【推断】 |
| epoch × mini-batch | 5 × 4 | 同上 | 【推断】 |
| 初始学习率 | 1e-3 | 同上 | 【推断】 |
| 学习率调度 | adaptive，desired_kl = 0.01 | 同上 | 【推断】 |
| 价值损失系数 | 1.0 | 同上 | 【推断】 |
| 熵系数 | 0.01 | 同上 | 【推断】 |
| 梯度裁剪 `max_grad_norm` | 1.0 | 同上 | 【推断】 |
| 价值裁剪 | 开启 | 同上 | 【推断】 |
| 历史编码器学习率 | 1e-3，固定 | `cli_utils.py:224` | 代码事实 |
| 对抗者概率 | 0.05 | `cli_utils.py:146` | 代码事实 |
| 对抗者更新间隔 | 10 次迭代 | `cli_utils.py:147` | 代码事实 |
| 对抗者强度 | 0 → 1 m/s 线性，每次再乘 [0,1] 随机数 | `cli_utils.py:133、143`；`gram_adversary.py:140-154` | 代码事实 |
| `train_and_finetune` | False | `cli_utils.py:70` | 代码事实 |
| `history_loss_epinet_separate` | True | `cli_utils.py:742` | 代码事实 |
| 其他三个 `history_loss_*` | False | `cli_utils.py:214-220` | 代码事实 |

标【推断】的项：服务器上的 Isaac Lab 是 0.54.2，原论文是 1.0.0，**两版的默认值可能不同**，复现前应打印配置对照。

---

# 第五部分　读代码时发现的值得注意之处

这些是我们读代码的观察，不影响"跑通"，但影响"理解"和"改代码"。

### 1. 部分梯度裁剪可能没有生效【代码观察，需在服务器上验证】

`ac_adapt_params`、`context_params`、`history_params` 在 `gram_actor_critic.py:377-414` 里是用 `itertools.chain(...)` 或 `.parameters()` 创建的，这两者都是**只能遍历一次的迭代器**：
- `history_params` 在 `gram_ppo.py:61` 创建 `history_optimizer` 时就已经被遍历完；
- `ac_adapt_params`、`context_params` 在第一次 `clip_grad_norm_` 时被遍历完。

之后再传给 `clip_grad_norm_`，得到的是空列表，**不会裁剪任何梯度**。主策略的 `opt_params` 也是迭代器，但它只在创建优化器时用一次，优化器内部已经保存了参数列表，所以**优化器本身不受影响**。

**验证方法**：在服务器上 `python -c` 构造一个 `GRAMActorCritic`，连续两次执行 `list(ac.ac_adapt_params)`，第二次如果是空列表就确认了。

**影响**：论文结果就是在这个代码下跑出来的，复现时**不要"修好"它**，否则可能和论文对不上。如果以后自己改代码，要知道这一点。

### 2. 上下文只存一次

见 2.3 节。训练中每个环境的上下文固定。要做"运行中途变化"，需要把上下文改成逐步存储。

### 3. `update()` 第 272 行的缩进

```python
# gram_ppo.py:265-272
                            if self.history_loss_adapt_only:
                                history_action_loss_ave = (...)
                            else:
                                history_action_loss_ave = history_action_loss.mean()

                                history_loss += history_action_loss_ave
```

`history_loss += ...` 缩进在 `else` 里面，所以同时打开 `train_and_finetune`、`history_loss_actions`、`history_loss_adapt_only` 时，动作模仿项会被算出来但**不加进损失**。对比第 292–299 行的同类代码，`+=` 是在 if/else 之外的。默认配置不会走到这里，只在改代码时需要注意。

### 4. 统计量的名字

`mean_latent_error_kl` 实际是动作均值的平方误差，不是 KL 散度。看 TensorBoard 时不要被名字误导。

### 5. ETA 不含 finetune

runner 打印的 ETA 用的是 `num_learning_iterations`（10,000），不包括 5,000 次 finetune，所以训练进行到后期时 ETA 会偏小，见 runner 篇。

### 6. 对改代码（分组退回）的提示

| 要改的地方 | 本文件位置 | 怎么改 |
|---|---|---|
| 掩码从 1 列变多列 | `act` 第 107–108 行；存储 `robust_masks` 形状 | [T, N, 1] → [T, N, G] |
| 对抗者只推鲁棒组 | 第 107 行 | 按需要改成"任意一组不可信就推"或按组设置不同扰动 |
| 优势分组标准化 | 存储第 103–115 行 | 按掩码组合分别标准化 |
| 上下文逐步存储 | 存储 `init_extras`、`add_transitions` | 改成 [T, N, 26] 逐步写入 |
| 历史损失按组 | `finetune` 第 524 行 | 分组回归，或只对"可信组"回归 |

---

# 自测题

1. GAE 递推公式是什么？用 1.4 节的数据，如果 λ = 0，A_0 等于多少？
2. 在 PPO 裁剪损失中，A = +1、ratio = 1.3、ε = 0.2 时，实际损失是多少？梯度是否为 0？
3. `observations_history` 的形状是什么？代入默认参数后大约占多少显存？
4. GRAM 的优势标准化和 rsl_rl 原版有什么不同？为什么要这样做？
5. 采样时，哪些环境可能被对抗者推？每步大约多少个？
6. 对抗者的学习信号从哪里来？为什么要减去平均值、乘以 −1、乘以掩码？
7. 对抗者多久更新一次？推力强度如何随训练变化？
8. 默认配置下，历史编码器在哪个阶段训练？依据是哪几行代码？服务器日志里有什么证据？
9. 默认的历史损失由哪两项组成？各自让哪个网络学什么？
10. 鲁棒组的数据在 PPO 更新时，梯度会流向上下文编码器 f 吗？为什么？

<details>
<summary>参考答案</summary>

1. A_t = δ_t + γλ(1−done_t)A_{t+1}。λ = 0 时 A_0 = δ_0 = 0.485。
2. 不裁剪项 −1 × 1.3 = −1.3，裁剪项 −1 × 1.2 = −1.2，max = −1.2，取裁剪项，对 ratio 的梯度为 0。
3. [24, 4096, 16, 45]（观测维度 45 为推算值），约 7078 万个 float32，约 283 MB。
4. GRAM 把鲁棒组和自适应组分开标准化（`gram_rollout_storage.py:103-115`）。因为两组的整体表现差别大，一起标准化会让鲁棒组几乎全是负优势、自适应组几乎全是正优势，学习信号失真；分开后每组内部都有好动作和坏动作。
5. 只有鲁棒组（`robust_masks = 1`）的环境，而且要再通过概率 0.05 的抽签（`gram_ppo.py:106-107`）。约 2048 × 0.05 ≈ 102 个。
6. 来自主策略的优势（GAE）。减平均值是为了只比较被推的步之间的相对好坏；乘 −1 是因为对抗者要让主策略变差；乘掩码是因为没被推的步与对抗者的选择无关（`gram_ppo.py:393-401`）。
7. 每 10 次迭代更新一次，那次迭代里每个 mini-batch 都更新（`gram_ppo.py:361-363, 442-443`）。最大强度从 0 线性增长到 1 m/s（runner 第 360 行、`gram_adversary.py:151-154`），每次推的实际强度在 [0, 最大强度] 中随机。
8. 只在最后 5000 次 finetune 中训练。依据：`train_and_finetune` 默认 False（`cli_utils.py:70`），`update()` 第 229 行条件不成立，走第 336–340 行把 history_loss 设为 0；runner 第 356–357 行在 finetune 阶段才调用 `finetune()`。服务器日志：前两次迭代 History loss 为 0，第三次（finetune）为 14.57 且 Value loss 为 0。
9. ‖f(c) − φ_base(h)‖²：让历史编码器从历史估计教师隐变量；mean_i ‖φ_epi(h̃, ε_i)‖²：让 epinet 可训练部分在训练数据上抵消固定先验，使修正项接近 0（`gram_ppo.py:522-531`）。
10. 不会。鲁棒组的 latent 输入是 `torch.zeros_like(latent.detach())`（`gram_actor_critic.py:452`），既是常数 0，又断开了计算图，f 收不到鲁棒组的梯度。
</details>
