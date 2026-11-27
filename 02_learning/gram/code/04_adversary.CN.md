# 代码精读 04：`gram_adversary.py`——专门"使坏"的对抗者

> 主文件：`source/algs/gram/gram_adversary.py`，共 154 行。
> 相关代码：`gram_ppo.py`（对抗者怎么收集数据、怎么训练）、`gram_on_policy_runner.py`（对抗者在训练流程中何时开关、强度怎么增长）、`gram_rollout_storage.py`（优势怎么归一化）、`envs/envs_utils.py`（推力怎么作用到机器人上）、`envs/unitree_go2_custom_env.py`（推力事件怎么注册）。
>
> 标注约定：**【代码事实】** 直接从代码读出；**【推断】** 根据代码和 Isaac Lab 的一般行为推出，没有在服务器上打印验证；**【论文对照】** 与论文的对应或差异。

---

## 0. 先搞清楚：对抗者是什么、为什么需要它

### 0.1 一句话

**对抗者是另一个小策略网络，它的目标和机器人的策略正好相反：机器人想拿高分，对抗者想让机器人拿低分。** 它的手段是：在机器人走路时，**挑一个最让机器人难受的方向推它一下**。

### 0.2 为什么要它

回忆论文：GRAM 的训练环境一半做"适应训练"（输入真实环境 z），一半做"鲁棒训练"（输入 z=0）。鲁棒训练的目标是让策略在"我不知道环境是什么"时也能稳住。**光是输入 z=0 还不够**，必须让它在这种状态下真的经历"糟糕的情况"，才能学会保守而稳健的走法。对抗者就负责制造这些"糟糕的情况"。

### 0.3 术语

| 术语 | 小白解释 |
|---|---|
| 对抗训练 | 让两个网络"对打"：一个想做好，一个想捣乱。捣乱的越聪明，做好的那个就被逼得越稳 |
| 最坏情况（worst case） | 在所有可能的扰动里，对机器人最不利的那一种。鲁棒控制里的 min-max 设计就是"针对最坏情况设计" |
| 优势（advantage）A | PPO 里的概念："这一步实际的结果比平均预期好多少"。A>0 说明这步做得比预期好 |
| 掩码（mask） | 一个 0/1 数组，1 表示"这个位置生效"，0 表示"不生效" |
| 伯努利分布 Bernoulli(p) | 抛一枚"正面概率 p"的硬币，正面记 1，反面记 0 |
| 均匀分布 U(a, b) | 在 a 到 b 之间等可能地随机取一个数 |

### 0.4 对抗者的"动作"到底是什么（先给结论）

| 问题 | 答案 |
|---|---|
| 对抗者看到什么 | 和机器人策略一样的观测（归一化后的 n_obs 维）【代码事实：`gram_ppo.py:99` 传入的 `obs`】 |
| 对抗者输出什么 | **一个数 θ**：推力的方向角（弧度）【代码事实：`gram_on_policy_runner.py:49` `num_adversary_actions = 1`】 |
| 推多大 | **不由对抗者决定**，是随机的：U(0, 当前上限)，上限随训练从 0 线性增长到 1 |
| 多久推一次 | 每一步以 **5%** 的概率推，而且**只在鲁棒训练环境里推** |
| 怎么"推" | **不是施加力**，而是直接给机身水平速度加一个增量（最多 1 m/s） |
| 对抗者怎么学 | 用 PPO，但优势取**负号**：机器人越吃亏，对抗者越得分 |
| 多久学一次 | 每 **10** 次 PPO 迭代才更新一次对抗者 |

下面逐行讲清楚每一条是怎么在代码里实现的。

---

## 1. 导入（第 1–18 行）

```python
# gram_adversary.py:9-18
from __future__ import annotations

import math

import torch
import torch.nn as nn
from rsl_rl.modules.actor_critic import get_activation
from torch.distributions import Normal

from source.utils.torch_utils import weight_init
```

和 `gram_actor_critic.py` 的导入几乎一样：激活函数工具、正态分布、Xavier 初始化函数。说明对抗者**本质上也是一个 Actor**（只有策略，没有自己的价值网络）。

---

## 2. 构造函数（第 21–86 行）

### 2.1 参数表（第 23–39 行）

```python
# gram_adversary.py:21-39
class GRAMAdversary(nn.Module):

    def __init__(
        self,
        num_actor_obs,
        num_actions,
        adversary_hidden_dims=[512, 256, 128],
        use_log_std=True,
        activation="elu",
        adversary_init_noise_std=1.0,
        init_nn_weights=True,
        adversary_gain=1e-4,
        adversary_prob=0.0,
        adversary_clamp=5.0,
        adversary_random_scale=True,
        adversary_random_angle=False,
        adversary_max_scale_start=0.0,
        **kwargs,
    ):
```

| 参数 | 构造默认 | GRAM 实际值（来源） | 含义 |
|---|---|---|---|
| `num_actor_obs` | — | n_obs（runner 传入） | 输入维度，和策略观测相同 |
| `num_actions` | — | **1**（`runner:49`） | 输出一个角度 θ |
| `adversary_hidden_dims` | [512, 256, 128] | 同左 | 隐藏层，和策略网络一样大。论文 Table I 也写对抗者是 512-256-128 |
| `use_log_std` | True | True | 用 log σ 作参数 |
| `adversary_init_noise_std` | 1.0 | 1.0（`cli_utils.py:148`） | 角度的初始探索噪声 σ=1 弧度（约 57°） |
| `adversary_gain` | 1e-4 | 1e-4（`cli_utils.py:99`） | 最后一层初始化增益 |
| `adversary_prob` | 0.0 | **0.05**（`cli_utils.py:146`，gram 训练时生效） | 每一步发动推力的概率 |
| `adversary_clamp` | 5.0 | 5.0（`cli_utils.py:134`） | 角度均值的限幅 ±5 弧度 |
| `adversary_random_scale` | True | True（除非 `--no_adversary_random_scale`） | 推力大小是否在 [0, 上限] 内随机 |
| `adversary_random_angle` | False | False（除非 `--adversary_random_angle`） | True 时角度完全随机，对抗者不学习 |
| `adversary_max_scale_start` | 0.0 | 0.0（`cli_utils.py:144`） | 推力上限的起始值 |
| `**kwargs` | — | — | 接收 policy 配置里其他用不到的参数（runner 把整个 `policy_cfg` 都传进来，`runner:99`） |

**为什么 `**kwargs` 很重要**：runner 构造对抗者时写的是 `GRAMAdversary(num_obs, num_adversary_actions, **self.policy_cfg)`，`policy_cfg` 里有一大堆给 actor-critic 用的参数（如 `num_latent`），对抗者用不到，就用 `**kwargs` 统统接住、忽略，避免报错。

### 2.2 对抗者网络（第 43–57 行）

```python
# gram_adversary.py:43-57
        # Adversary
        adversary_layers = []
        adversary_layers.append(nn.Linear(num_actor_obs, adversary_hidden_dims[0]))
        adversary_layers.append(activation)
        for layer_index in range(len(adversary_hidden_dims)):
            if layer_index == len(adversary_hidden_dims) - 1:
                adversary_layers.append(nn.Linear(adversary_hidden_dims[layer_index], num_actions))
            else:
                adversary_layers.append(
                    nn.Linear(adversary_hidden_dims[layer_index], adversary_hidden_dims[layer_index + 1])
                )
                adversary_layers.append(activation)
        self.adversary = nn.Sequential(*adversary_layers)
```

和 actor 的写法一模一样（见代码精读 03 的 3.2 节）。层结构（n_obs=45【推断】）：

| 下标 | 层 | 输入维 | 输出维 |
|---|---|---|---|
| adversary[0] | Linear | 45 | 512 |
| adversary[1] | ELU | 512 | 512 |
| adversary[2] | Linear | 512 | 256 |
| adversary[3] | ELU | 256 | 256 |
| adversary[4] | Linear | 256 | 128 |
| adversary[5] | ELU | 128 | 128 |
| adversary[6] | Linear | 128 | **1** |

**注意**：对抗者**看不到上下文 c，也看不到 z**，只看和机器人一样的观测。它要从"机器人当前的姿态、速度、指令"判断"往哪推最难受"。

### 2.3 噪声与基本设置（第 59–76 行）

```python
# gram_adversary.py:59-76
        # Action noise
        self.use_log_std = use_log_std
        if self.use_log_std:
            self.log_std = nn.Parameter(torch.log(adversary_init_noise_std * torch.ones(num_actions)))
        else:
            self.std = nn.Parameter(adversary_init_noise_std * torch.ones(num_actions))
        self.distribution = None
        # disable args validation for speedup
        Normal.set_default_validate_args = False

        self.adversary_prob = adversary_prob
        self.adversary_clamp = adversary_clamp

        self.adversary_random_scale = adversary_random_scale
        self.adversary_random_angle = adversary_random_angle

        self.adversary_max_scale_start = adversary_max_scale_start
        self.adversary_max_scale_cur = adversary_max_scale_start
```

- 角度噪声：1 个参数 log σ，初值 log(1) = 0，即 σ = 1 弧度。
- `adversary_max_scale_cur`：**当前推力上限**，从 `start`（0.0）开始，训练中逐渐增大（见第 8 节）。

### 2.4 要不要训练对抗者（第 78–81 行）

```python
# gram_adversary.py:78-81
        if (self.adversary_prob == 0.0) or self.adversary_random_angle:
            self.train_adversary = False
        else:
            self.train_adversary = True
```

两种情况不训练：
1. **概率为 0**：根本不推，没东西可学（contextual_rl、domain_rand 就是这样，`cli_utils.py:602、610`）；
2. **角度完全随机**：方向不由网络决定，学了也没用。这对应一个"随机推力"的对照实验。

**数值例子**：gram 训练时 `adversary_prob=0.05`，`random_angle=False` → `train_adversary=True`。

**【代码事实】一个细节**：`train_adversary` 只在构造时算一次。之后 runner 在微调开始时把 `adversary_prob` 改成 0（`runner:291`），但 `train_adversary` 仍是 True。这没关系，因为微调阶段调用的是 `finetune()` 而不是 `update()`，不会走对抗者更新的代码。【推断，依据 runner:356-360】

### 2.5 初始化（第 83–86 行）

```python
# gram_adversary.py:83-86
        # Initialize NN weights
        if init_nn_weights:
            self.apply(weight_init)
            nn.init.xavier_normal_(self.adversary[-1].weight, gain=adversary_gain)
```

最后一层 gain=1e-4，**初始输出的角度均值 ≈ 0**（指向 x 正方向，即机身前方）。但因为有 σ=1 的噪声，初始采样的角度大致在 −1 到 +1 弧度（约 ±57°）之间，主要集中在"往前推"附近。训练中网络会学会根据状态选择方向。

**小结**：对抗者 = 一个和策略一样大的 MLP，输入观测，输出 1 个角度均值；外加 1 个可训练的角度噪声。

---

## 3. 辅助函数（第 88–106 行）

```python
# gram_adversary.py:88-106
    def reset(self, dones=None):
        pass

    def forward(self):
        raise NotImplementedError

    @property
    def action_mean(self):
        return self.distribution.mean

    @property
    def action_std(self):
        return self.distribution.stddev

    def get_std(self):
        if self.use_log_std:
            return torch.exp(self.log_std)
        else:
            return self.std
```

和 actor-critic 中的同名函数作用相同：没有记忆所以 `reset` 为空；不实现 `forward` 防误用；提供均值、标准差的访问接口。`get_std` 用于训练日志打印 "mean_adversary_std"（`gram_ppo.py:460`）。

---

## 4. 采样角度：update_distribution 与 act（第 108–122 行）

```python
# gram_adversary.py:108-122
    def update_distribution(self, observations):
        mean = self.adversary(observations)
        mean_clamp = mean.clamp(min=-self.adversary_clamp, max=self.adversary_clamp)
        if self.use_log_std:
            std = self.log_std.exp()
        else:
            std = self.std
        self.distribution = Normal(mean_clamp, mean_clamp * 0.0 + std)

    def act(self, observations, **kwargs):
        self.update_distribution(observations)
        return self.distribution.sample()

    def get_actions_log_prob(self, actions):
        return self.distribution.log_prob(actions).sum(dim=-1)
```

**逐行解释**：

| 行 | 做了什么 | 形状（B=4096） |
|---|---|---|
| 109 | 网络前向，得到角度均值 | (4096, 1) |
| 110 | 均值限幅到 [−5, 5] 弧度 | (4096, 1) |
| 111–114 | 取噪声 σ | (1,) |
| 115 | 建立正态分布 N(均值, σ) | — |
| 119 | 从分布里**采样一个角度** θ | (4096, 1) |
| 122 | 计算某个角度的对数概率（只有 1 维，求和不改变值） | (4096,) |

**为什么限幅 ±5 弧度？** 角度是周期性的（θ 和 θ+2π 是同一个方向），±5 弧度已经超过一整圈（2π ≈ 6.28 的范围是 [−3.14, 3.14] 就够），限幅只是防止网络输出跑到很大的数导致数值问题。所以**这个限幅不会限制对抗者选方向**。

**数值例子**：某环境网络输出 0.8，σ = 0.5。采样可能得到 θ = 1.1 弧度（约 63°），即"往左前方推"。

---

## 5. 一个从未被调用的函数：act_inference（第 124–127 行）

```python
# gram_adversary.py:124-127
    def act_inference(self, observations):
        actions_mean = self.actor(observations)
        actions_mean_clamp = actions_mean.clamp(min=-self.adversary_clamp, max=self.adversary_clamp)
        return actions_mean_clamp
```

**【代码事实】这个函数有 bug**：对抗者类里没有 `self.actor`，网络叫 `self.adversary`。如果调用会报 `AttributeError`。

**为什么没出问题？** 全仓库只有 `gram_on_policy_runner.py:661` 调用了 `act_inference(`，而那是 `self.alg.actor_critic.act_inference`（策略网络的），**不是对抗者的**。评估时对抗者根本不用（推力强度被设为 0）。所以这是一段死代码，大概是从 actor-critic 复制过来没改名。

**读代码的经验**：看到疑似 bug，先查有没有调用者，再判断影响。这里没有影响，复现时不用管；但如果以后自己写"评估时加对抗推力"的实验，就要把它改成 `self.adversary`。

---

## 6. 限制噪声范围：enforce_minimum_std（第 129–133 行）

```python
# gram_adversary.py:129-133
    def enforce_minimum_std(self):
        if self.use_log_std:
            self.log_std.data.clamp_(min=math.log(1e-2), max=math.log(10.0))
        else:
            self.std.data.clamp_(min=1e-2, max=10.0)
```

和策略网络的同名函数一样，每次对抗者更新后（`gram_ppo.py:417-418`）把角度噪声 σ 限制在 [0.01, 10] 弧度之间。

---

## 7. 什么时候推：generate_adversary_masks（第 135–138 行）

```python
# gram_adversary.py:135-138
    def generate_adversary_masks(self, observations):
        mask_shape = observations.shape[:-1] + (1,)
        adversary_mask_probs = torch.ones(mask_shape, device=observations.device) * self.adversary_prob
        return torch.bernoulli(adversary_mask_probs)
```

**逐行解释**：
- 第 136 行：`observations.shape[:-1]` 是去掉最后一维的形状，即 (B,)；再加上 (1,)，得到 (B, 1)。
- 第 137 行：造一个 (B, 1) 的张量，每个元素都是 0.05。
- 第 138 行：对每个元素抛一次"正面概率 0.05"的硬币，得到 0 或 1。

**但这还不是最终的掩码**。在 `gram_ppo.py:106-107`：

```python
# gram_ppo.py:106-107
        adversary_masks = self.adversary_policy.generate_adversary_masks(obs).detach()
        self.transition.adversary_masks = adversary_masks * robust_masks
```

**最终掩码 = 伯努利掩码 × 鲁棒掩码**。也就是说：
- **适应训练环境（robust_masks=0）永远不推**；
- 鲁棒训练环境里，每一步有 5% 的概率推。

**数值例子**：4096 个环境，一半（2048 个）是鲁棒环境。每一步平均被推的环境数 ≈ 2048 × 0.05 ≈ **102 个**。对单个鲁棒环境来说，平均每 1/0.05 = 20 步被推一次；策略 50 Hz，即**平均每 0.4 秒被推一次**。

**【论文对照】** 论文说"the adversary applies forward and lateral external forces to the robot's body 5% of the time during data collection"，对应这里的 5%。论文没强调"只推鲁棒环境"，但从方法逻辑看（适应环境要学的是"正常情况下针对性适应"），这样做是合理的。

---

## 8. 推多大、往哪推：angle_to_vector（第 140–149 行）

```python
# gram_adversary.py:140-149
    def angle_to_vector(self, theta):
        if self.adversary_random_angle:
            theta = torch.rand_like(theta) * 2 * torch.pi

        vector = torch.cat([torch.cos(theta), torch.sin(theta)], dim=-1)
        if self.adversary_random_scale:
            scale = torch.rand_like(theta) * self.adversary_max_scale_cur
            vector = scale * vector

        return vector
```

**这段要干什么**：把对抗者输出的角度 θ 变成一个**二维速度增量向量** [Δvx, Δvy]。

**逐行解释**：

| 行 | 做了什么 | 形状 |
|---|---|---|
| 141–142 | 如果开了"随机角度"，直接用 U(0, 2π) 的随机角度替换网络的输出 | (B, 1) |
| 144 | 角度 → 单位方向向量 [cos θ, sin θ] | (B, 2) |
| 145–147 | 如果开了"随机大小"（默认开），乘上一个 U(0, 当前上限) 的随机数 | (B, 1) × (B, 2) → (B, 2) |

**方向的几何意义**：θ=0 → [1, 0]，沿 x 正方向；θ=π/2 → [0, 1]，沿 y 正方向；θ=π → [−1, 0]，沿 x 负方向。**这里的 x、y 是世界坐标系，不是机身坐标系。**【推断：因为下面写入的是 `root_vel_w`，w 表示 world】这意味着对抗者要结合观测（机身朝向等）才能推算出"相对机器人往哪推最难受"。

**数值例子**：θ = 1.1 弧度，当前上限 0.6，随机数 rand = 0.5。
- 方向：[cos 1.1, sin 1.1] = [0.454, 0.891]
- 大小：0.5 × 0.6 = 0.30
- 速度增量：0.30 × [0.454, 0.891] = **[0.136, 0.267] m/s**

**一个重要的认识**：**对抗者只能选方向，不能选大小**。大小在 [0, 上限] 之间随机。所以 GRAM 的对抗者其实是"半对抗、半随机"的：方向是最坏的，大小是随机的。【代码事实】论文说"the direction of the external force is learned by the adversary"，和这里一致。

---

## 9. 推力上限如何增长：update_magnitude（第 151–154 行）

```python
# gram_adversary.py:151-154
    def update_magnitude(self, train_progress):
        self.adversary_max_scale_cur = (
            self.adversary_max_scale_start + (1.0 - self.adversary_max_scale_start) * train_progress
        )
```

公式：**上限 = 起始值 + (1 − 起始值) × 训练进度**。起始值为 0，所以上限 = 训练进度。

**谁调用它、进度怎么算**（`gram_on_policy_runner.py:356-360`）：

```python
# gram_on_policy_runner.py:356-360
            if it >= finetune_start_iter:
                loss_stats, update_stats = self.alg.finetune()
            else:
                loss_stats, update_stats = self.alg.update()
                self.alg.adversary_policy.update_magnitude((it - start_iter + 1) / (finetune_start_iter - start_iter))
```

- 只在 RL 阶段（前 10000 次）每次 PPO 更新后调用；
- 进度 = (已完成迭代数) / 10000。

**数值例子**（从头训练，start_iter=0，finetune_start_iter=10000）：

| 第几次迭代后 | 进度 | 推力上限（m/s） | 一次推力的平均大小（上限的一半） |
|---|---|---|---|
| 1 | 0.0001 | 0.0001 | 几乎为 0 |
| 2500 | 0.25 | 0.25 | 0.125 |
| 5000 | 0.50 | 0.50 | 0.25 |
| 10000 | 1.00 | **1.00** | 0.50 |

**为什么要从 0 慢慢加？** 这叫**课程学习（curriculum）**：一开始机器人连路都不会走，如果马上用 1 m/s 的力推它，它永远学不会走。先轻后重，让它先学会走，再学会抗推。

**【论文对照】** 论文 Sec. VI："the impact of the force on linear velocity increases from 0.0 to 1.0 meters per second over the course of training"。完全对应。

---

## 10. 推力怎么真正作用到机器人上

### 10.1 第一步：把推力参数"塞进"环境事件（`gram_ppo.py:114-117`）

```python
# gram_ppo.py:114-117
    def adversary_update_sim(self, adversary_actions, adversary_masks):
        adversary_cfg = self.env.unwrapped.event_manager.get_term_cfg("adversary_push")
        adversary_cfg.params["adversary_actions"] = self.adversary_policy.angle_to_vector(adversary_actions)
        adversary_cfg.params["adversary_masks"] = adversary_masks
```

- Isaac Lab 的环境有一个**事件管理器**（event manager），负责在特定时机执行"事件函数"（如重置、随机化、推机器人）。
- 这里找到名叫 `"adversary_push"` 的事件，把它的参数字典里的两项**直接改掉**：
  - `adversary_actions` ← 角度转成的速度增量向量 (B, 2)；
  - `adversary_masks` ← 最终掩码 (B, 1)。
- 这是一种"不改环境代码、从外部给事件传参"的技巧。

### 10.2 第二步：事件注册（`unitree_go2_custom_env.py:205-211`）

```python
        # adversary
        self.events.adversary_push = EventTerm(
            func=adversarial_push_by_setting_velocity,
            mode="interval",
            interval_range_s=(0.0, 0.0),
            params={"magnitude": adversary_magnitude},
        )
```

- `mode="interval"`：按时间间隔触发的事件；
- `interval_range_s=(0.0, 0.0)`：间隔为 0 秒，【推断】即**每个环境步都触发一次**；是否真的推，由掩码决定；
- `magnitude`：总幅值系数。gram 训练时 = 1.0；**评估时被强制设为 0**（`cli_utils.py:529-537`），所以评估时永远不推。

### 10.3 第三步：执行推力（`envs_utils.py:270-296`）

```python
# envs_utils.py:270-296（节选）
def adversarial_push_by_setting_velocity(
    env, env_ids, magnitude=0.0, adversary_actions=None, adversary_masks=None, asset_cfg=SceneEntityCfg("robot"),
):
    asset = env.scene[asset_cfg.name]

    if (adversary_actions is not None) and (adversary_masks is not None) and (magnitude > 0):
        # velocities
        vel_w = asset.data.root_vel_w[env_ids]
        # push x,y velocity
        processed_adversary_actions = adversary_actions.clamp(min=-1, max=1)
        vel_xy_push_all = magnitude * processed_adversary_actions
        vel_xy_push = vel_xy_push_all[env_ids]

        # additive
        vel_w[:, :2] += adversary_masks[env_ids] * vel_xy_push

        # set the velocities into the physics simulation
        asset.write_root_velocity_to_sim(vel_w, env_ids=env_ids)
```

**逐行解释**：
- 三个条件都满足才推：有方向、有掩码、幅值大于 0；
- `root_vel_w`：机身在**世界坐标系**下的速度（线速度 3 维 + 角速度 3 维）；
- `.clamp(min=-1, max=1)`：每个分量限制在 ±1。因为 |cos|、|sin| ≤ 1 且大小 ≤ 1，正常情况下这一步不起作用；
- `vel_w[:, :2] += 掩码 × 推力`：**只改水平的 x、y 线速度**，掩码为 0 的环境加 0；
- `write_root_velocity_to_sim`：把改后的速度**直接写进物理引擎**。

**这就是为什么说"不是施加力，而是改速度"**：
- 施加力：F 持续作用一段时间，速度逐渐变化，需要经过动力学积分；
- 改速度：**瞬间**让机身多出一个速度，相当于被一个**极短的冲击**撞了一下。
- 这是足式机器人 RL 里很常见的做法（Isaac Lab 自带的 `push_by_setting_velocity` 也是这样），好处是简单、不受质量影响（同样的速度增量对轻的和重的机器人效果一样）。

**数值例子**：某鲁棒环境的机器人正以 [0.8, 0.0] m/s 前进，这一步被推中（掩码 1），速度增量 [0.136, 0.267]：
- 推后速度 = [0.936, 0.267] m/s，机器人突然被往左前方"弹"了一下；
- 策略必须马上调整步态，否则会摔倒或跑偏，拿到低分。

---

## 11. 对抗者怎么学习（`gram_ppo.py:359-418`）——"负优势"

### 11.1 先回顾 PPO 的优势

PPO 训练策略时，对每一步算一个**优势 A**："这一步之后实际拿到的分，比价值网络预期的多多少"。A>0 的动作要多做，A<0 的少做。

**在 GRAM 里，优势在存储时还要分组归一化**（`gram_rollout_storage.py:100-115`）：鲁棒环境的优势单独减均值、除标准差，适应环境也单独做。【代码事实】所以对抗者用到的优势，是**鲁棒环境内部归一化过的**。

### 11.2 对抗者的目标：让机器人的优势越小越好

如果某一步对抗者推了机器人，之后机器人的优势 A 很低（摔了、跑偏了），说明**这次推得好**。所以对抗者的"优势"应该是 **−A**。

### 11.3 代码逐段

**(a) 多久更新一次（第 359–363 行）**

```python
# gram_ppo.py:359-363
            # Adversary update
            if (
                self.since_adversary_update % self.adversary_update_every == 0
            ) and self.adversary_policy.train_adversary:
```

- `since_adversary_update` 在每次 `update()` 结束时加 1 并对 10 取余（`gram_ppo.py:442-443`）；
- 所以**每 10 次 PPO 迭代，只有 1 次会更新对抗者**；在那一次里，每个小批次（mini-batch）、每个训练轮次（epoch）都更新。
- 为什么不每次都更新？【推断】防止对抗者进步太快、把策略压垮；让策略有时间适应当前的对抗者。

**(b) 重新算一遍对抗者的分布（第 364–367 行）**

```python
                self.adversary_policy.act(obs_batch)
                adversary_log_prob_batch = self.adversary_policy.get_actions_log_prob(adversary_actions_batch)
                adversary_mu_batch = self.adversary_policy.action_mean
                adversary_sigma_batch = self.adversary_policy.action_std
```

用**当前**的对抗者参数，对收集数据时用过的观测重新前向，算出"当时那个角度在新参数下的概率"。PPO 需要新旧概率的比值。

**(c) 自适应学习率（第 369–390 行）**

```python
                if self.desired_kl is not None and self.schedule == "adaptive":
                    with torch.inference_mode():
                        kl = torch.sum(
                            torch.log(adversary_sigma_batch / old_adversary_sigma_batch + 1.0e-5)
                            + (torch.square(old_adversary_sigma_batch) + torch.square(old_adversary_mu_batch - adversary_mu_batch))
                            / (2.0 * torch.square(adversary_sigma_batch))
                            - 0.5,
                            axis=-1,
                        )
                        kl_mean = torch.mean(kl)

                        if kl_mean > self.desired_kl * 2.0:
                            self.adversary_lr = max(1e-5, self.adversary_lr / 1.5)
                        elif kl_mean < self.desired_kl / 2.0 and kl_mean > 0.0:
                            self.adversary_lr = min(1e-2, self.adversary_lr * 1.5)
```

- **KL 散度**：衡量"新分布和旧分布差多少"。这里是两个一维正态分布 KL 的解析公式。
- 规则：变化太大（KL > 2 倍目标）→ 学习率除以 1.5；变化太小（KL < 目标的一半）→ 学习率乘以 1.5；限制在 [1e-5, 1e-2]。
- 这和 rsl_rl 对策略网络用的自适应学习率规则相同，只是对抗者有**自己独立的学习率和优化器**（`gram_ppo.py:57-60`，初值等于策略的学习率）。

**(d) 计算对抗者的优势（第 393–401 行）——核心**

```python
# gram_ppo.py:393-401
                adversary_batch_size = max(adversary_masks_batch.sum().item(), 1.0)

                # center adversary advantages
                adversary_advantages_batch_mean = (
                    advantages_batch * adversary_masks_batch
                ).sum() / adversary_batch_size
                adversary_advantages_batch = (
                    (advantages_batch - adversary_advantages_batch_mean) * adversary_masks_batch * -1
                )
```

逐行：
1. `adversary_batch_size`：这个小批次里**真正被推过**的样本数（掩码为 1 的个数），至少为 1 防止除零；
2. `adversary_advantages_batch_mean`：**只在被推过的样本上**求策略优势的平均值；
3. `(A − 平均) × 掩码 × (−1)`：
   - 减平均：中心化，让对抗者比较的是"这次推得比平均好还是差"；
   - × 掩码：**没推的样本优势为 0**，不参与对抗者学习（没推，对抗者的角度对结果没有影响）；
   - × (−1)：**取负号**，机器人吃亏 = 对抗者得分。

**(e) PPO 裁剪损失（第 403–410 行）**

```python
# gram_ppo.py:403-410
                adversary_ratio = torch.exp(adversary_log_prob_batch - torch.squeeze(old_adversary_log_prob_batch))
                adversary_surrogate = -torch.squeeze(adversary_advantages_batch) * adversary_ratio
                adversary_surrogate_clipped = -torch.squeeze(adversary_advantages_batch) * torch.clamp(
                    adversary_ratio, 1.0 - self.clip_param, 1.0 + self.clip_param
                )
                adversary_loss = (
                    torch.max(adversary_surrogate, adversary_surrogate_clipped).sum() / adversary_batch_size
                )
```

- `ratio = exp(新 log p − 旧 log p)`：新参数下选这个角度的概率，是旧参数下的几倍；
- 标准 PPO 损失：max(−A_adv × r, −A_adv × clip(r, 1−ε, 1+ε))，ε 是 `clip_param`（rsl_rl 默认 0.2【推断】）；
- `.sum() / adversary_batch_size`：只对被推过的样本平均（没推的样本优势已为 0）。

**(f) 梯度更新（第 413–418 行）**

```python
                self.adversary_optimizer.zero_grad()
                adversary_loss.backward()
                nn.utils.clip_grad_norm_(self.adversary_policy.parameters(), self.max_grad_norm)
                self.adversary_optimizer.step()
                with torch.no_grad():
                    self.adversary_policy.enforce_minimum_std()
```

标准的四步：清梯度 → 反向传播 → 梯度裁剪（防止梯度爆炸）→ 优化器更新；最后限制噪声范围。

### 11.4 用数值例子把符号走一遍

某小批次里有 4 个被推过的样本，策略的（归一化后）优势 A 为：

| 样本 | A | A − 平均 | 对抗者优势 = −(A − 平均) | 含义 |
|---|---|---|---|---|
| 1 | −1.0 | −1.0 − 0 = −1.0 | **+1.0** | 推完机器人表现很差 → 好角度，对抗者要多用 |
| 2 | +0.5 | +0.5 | −0.5 | 推完机器人反而表现好 → 坏角度 |
| 3 | +0.8 | +0.8 | −0.8 | 坏角度 |
| 4 | −0.3 | −0.3 | +0.3 | 较好角度 |

平均 = (−1.0 + 0.5 + 0.8 − 0.3) / 4 = 0。

PPO 更新后：样本 1、4 用的角度概率上升，样本 2、3 的下降。**对抗者渐渐学会"在这种状态下往这个方向推最伤"**。

### 11.5 一个容易误解的点：对抗者没有自己的价值网络

【代码事实】对抗者**直接借用策略的优势**（`advantages_batch`），没有单独训练一个"对抗者价值网络"。因为这是一个零和博弈：机器人的得分就是对抗者的失分，所以机器人的优势取负号就是对抗者的优势。这样省掉了一个网络。

但要注意一个微妙之处【推断】：策略的优势 A 衡量的是"这一步**策略的动作**比预期好多少"，它同时受策略动作和对抗者推力影响。对抗者把它当作"推力的效果"来学，是一种近似。

---

## 12. 对抗者在整个训练流程中的开关

| 阶段 | 对抗者是否推 | 对抗者是否学习 | 依据 |
|---|---|---|---|
| RL 阶段（第 1–10000 次） | 推（鲁棒环境，5%，上限 0→1） | 每 10 次迭代学一次 | `gram_ppo.py:99-110`、`359-418` |
| 微调阶段（第 10001–15000 次） | **不推**（除非 `--finetune_w_adversary`） | 不学 | `runner:289-294`：概率改 0，并把事件掩码写成全 0 |
| 收集验证集 | **不推** | 不学 | `runner:504-510`：同样关掉 |
| 评估 | **不推** | 不用 | `cli_utils.py:529-532`：评估时事件幅值设为 0 |

**为什么微调和验证阶段要关掉推力？** 【论文对照】论文 Sec. V："We do not apply an adversary during the supervised learning phase, as the goal is to train the epinet in (5) to output estimates with low variance in ID contexts." 如果微调时也被推，epinet 会把"被推"当成见过的情况，部署时遇到类似扰动就不会提高不确定性。验证集同理：β、λ 要按"纯 ID"的不确定性分布来定标。

**runner:289-294 的写法值得注意**：

```python
                    if not self.finetune_w_adversary:
                        self.alg.adversary_policy.adversary_prob = 0.0
                        adversary_actions = self.alg.adversary_policy.act(obs).detach()
                        adversary_masks = self.alg.adversary_policy.generate_adversary_masks(obs).detach()
                        self.alg.adversary_update_sim(adversary_actions, torch.zeros_like(adversary_masks))
```

光把概率改成 0 不够：事件的参数字典里还存着上一步的掩码，如果不覆盖，环境事件会继续用旧掩码推。所以这里显式写入一次**全零掩码**。

### 不同算法下的对抗者

| 算法 | 环境幅值 magnitude | adversary_prob | 推哪些环境 | 对抗者是否训练 |
|---|---|---|---|---|
| gram / gram_separate / gram_modular | 1.0 | 0.05 | 鲁棒环境（约一半） | 是 |
| robust_rl | 1.0 | 0.05 | **所有环境**（`robust_train_only`，掩码全 1【推断】） | 是 |
| contextual_rl | 0 | 0 | 不推 | 否 |
| domain_rand | 0 | 0 | 不推 | 否 |

（来源：`cli_utils.py:529-537`、`546-620`。）

---

## 13. 全流程数据流图

```
 每个环境步（50 Hz），runner.learn 循环（runner:310-326）
 ─────────────────────────────────────────────────────────────
  obs (B, n_obs)，已归一化
     │
     ├──► actor_critic.act(...)  ──► 机器人动作 (B, 12)
     │
     └──► adversary.act(obs)                      gram_ppo.py:99
             │  MLP 512-256-128 → 均值，限幅 ±5
             │  N(均值, σ) 采样
             ▼
          θ (B, 1)  ──► 存入 storage（角度、log_prob、均值、σ）
             │
          generate_adversary_masks:  Bernoulli(0.05)  (B, 1)
             │  × robust_masks (B, 1)                  gram_ppo.py:107
             ▼
          最终掩码 (B, 1)  ──► 存入 storage
             │
          adversary_update_sim                         gram_ppo.py:114
             │  angle_to_vector(θ):
             │     [cos θ, sin θ] × U(0, 当前上限)
             ▼
          事件 "adversary_push" 的参数被改写
             │
 env.step(动作)                                        runner:316
     │   事件管理器触发 interval 事件（每步）
     ▼
 adversarial_push_by_setting_velocity                 envs_utils.py:270
     │   vel_w[:, :2] += 掩码 × magnitude(1.0) × clamp(向量, ±1)
     │   write_root_velocity_to_sim
     ▼
 机器人机身速度被瞬间改变 → 之后的奖励变化
     │
 ═══ 一次迭代（24 步）结束 ═══
     │
 storage.compute_returns：算策略优势 A，按鲁棒/适应分组归一化
     │
 ppo.update():
     ├─ 策略 PPO 更新（所有样本）
     └─ 若 (第 10 的倍数次) 且 train_adversary：
          对抗者优势 = −(A − 被推样本的平均A) × 掩码
          PPO 裁剪损失 → Adam 更新 → 限制 σ
     │
 update_magnitude((it+1)/10000)：推力上限增大     runner:360
```

---

## 14. 和论文描述的对照

| 论文写法 | 代码实际 | 是否一致 |
|---|---|---|
| "applies forward and lateral external forces to the robot's body" | 直接改世界坐标系下的水平速度（瞬时冲击） | **方式不同**：不是"力"，是速度增量 |
| "5% of the time" | 每步 Bernoulli(0.05)，且只在鲁棒环境 | 一致，代码多了"只推鲁棒环境" |
| "the direction of the external force is learned by the adversary" | 对抗者输出角度 θ | 一致 |
| "impact ... increases from 0.0 to 1.0 meters per second over the course of training" | 上限从 0 线性增到 1；每次实际大小 U(0, 上限) | 一致，代码多了"大小随机" |
| 对抗者"trained with RL to minimize the returns" | PPO + 负优势，借用策略的优势，每 10 次迭代更新一次 | 一致，"每 10 次"论文没写 |
| 监督阶段不加对抗者 | 微调开始时关闭 | 一致 |
| Table I：对抗者 MLP 512-256-128 | 同 | 一致 |

---

## 15. 对我们方向的启示

1. **对抗者只覆盖"机身推力"一种扰动**。我们关心的执行器类变化（电机变弱、轮子卡死），在 GRAM 的鲁棒训练里**完全没有**。这是论文作者自己承认的局限（"only a standard choice of adversary"）。
2. **要加执行器类扰动，可以照这个模式写**：
   - 改的不是机身速度，而是某个电机的力矩倍数（可以从环境里已有的 `motor_fault_indices` / `_effort_scale` 改起）；
   - "对抗者"可以选**哪个电机**变弱（离散选择），而不是选推力方向；
   - 同样用"只在鲁棒环境 / 只在被标为不可信的组"生效的掩码。
3. **"只推鲁棒环境"的掩码设计，正好可以推广到"分组"**：把 `robust_masks` (B, 1) 换成 (B, G)，对"执行器组不可信"的环境注入电机扰动，对"环境组不可信"的环境注入摩擦、负载扰动。
4. **评估时要能加扰动**：现在评估时强制幅值为 0。做"运行中突然变化"的实验，需要自己写评估期的扰动事件；如果复用对抗者，要先修好第 5 节的 `act_inference` bug。

---

## 自测题

1. 对抗者的输出有几维？代表什么？推力的大小由谁决定？
2. 在 4096 个环境、一半是鲁棒环境的情况下，平均每一步有多少个环境被推？单个鲁棒环境平均多久被推一次？
3. 为什么说 GRAM 的"推力"其实不是力？这样做有什么好处？
4. 第 5000 次迭代后，推力上限是多少？一次推力的平均大小大约是多少？
5. 对抗者的优势是怎么算出来的？为什么要乘以掩码？为什么要乘以 −1？
6. 对抗者多久更新一次参数？
7. 微调阶段为什么要关掉推力？代码里除了把概率设为 0，还做了什么？为什么？
8. `act_inference` 有什么问题？为什么没有导致程序出错？
9. robust_rl 和 gram 在对抗者的使用上有什么区别？
10. 如果要加入"轮子突然变弱"的扰动，可以借鉴对抗者代码的哪些设计？

<details>
<summary>参考答案</summary>

1. 1 维，是推力在世界坐标系中的方向角 θ。大小不由对抗者决定，而是在 [0, 当前上限] 之间均匀随机。
2. 约 2048 × 0.05 ≈ 102 个。单个鲁棒环境平均每 20 步被推一次，50 Hz 下约 0.4 秒一次。
3. 代码直接修改机身的水平速度并写回物理引擎，相当于瞬时冲击，不是持续施加的力。好处是实现简单，且同样的速度增量对不同质量的机器人效果一致。
4. 上限 = 5000/10000 = 0.5 m/s；每次大小在 U(0, 0.5) 中取，平均约 0.25 m/s。
5. 取策略在被推样本上的优势 A，减去这些样本的平均值，乘以掩码，再乘以 −1。乘掩码是因为没被推的样本与对抗者的角度无关，不该参与学习；乘 −1 是因为对抗者的目标与策略相反，机器人吃亏就是对抗者得分。
6. 每 10 次 PPO 迭代更新一次（在那一次中对所有小批次和轮次更新）。
7. 为了让 epinet 只在纯 ID 数据上训练，部署时遇到扰动才会提高不确定性；验证集同理。代码还向事件参数写入一次全零掩码，因为事件参数里残留着上一步的掩码，不覆盖的话环境还会继续推。
8. 它调用了不存在的 `self.actor`（应为 `self.adversary`），一旦调用就会报错。全仓库没有任何地方调用对抗者的 `act_inference`，评估时推力也被关闭，所以没出错。
9. gram 只推鲁棒训练环境（约一半），robust_rl 只做鲁棒训练，所有环境都被推；而且 robust_rl 的部署策略是不看 z 的独立鲁棒网络。
10. 借鉴"掩码决定在哪些环境生效"、"强度随训练从小到大的课程"、"通过事件参数从外部注入扰动"、"用负优势训练一个选择扰动的策略"（例如选择哪个电机变弱），以及"微调与验证阶段关闭扰动"。
</details>
