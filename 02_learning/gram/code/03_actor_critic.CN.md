# 代码精读 03：`gram_actor_critic.py`——GRAM 的"大脑"

> 文件：`source/algs/gram/gram_actor_critic.py`，共 741 行（官方仓库 merlresearch/gram）。
> 本篇按文件顺序**逐段**讲完全部代码，不跳段。每段的讲法都一样：**这段要干什么 → 原样贴代码（注明行号）→ 逐行解释 → 数值例子 → 小结**。
>
> 标注约定：
> - **【代码事实】**：直接从代码读出来的；
> - **【推断】**：根据代码和 Isaac Lab 默认设置推出来的，没有在服务器上打印验证；
> - **【论文对照】**：和论文写法的对应或差异。

---

## 0. 先搞清楚：这个文件在整个 GRAM 里是什么角色

GRAM 里有好几个网络，**除了对抗者以外，全部都定义在这一个类 `GRAMActorCritic` 里**：

| 网络 | 代码里的名字 | 作用（一句话） | 训练时用不用 | 部署时用不用 |
|---|---|---|---|---|
| 策略网络（Actor） | `self.actor` | 看到"观测 + 环境隐变量 z"，输出 12 个关节的目标角度 | 用 | 用 |
| 价值网络（Critic） | `self.critic` | 估计"从当前状态往后能拿多少分"，只用于训练 | 用 | **不用** |
| 上下文编码器（教师用） | `self.context_encoder` | 把 26 维真实环境参数压成 8 维 z | 用 | **不用**（部署时拿不到真实参数） |
| 历史编码器（学生用） | `self.history_encoder` | 从最近 16 步观测里估计 8 维 z | 只在最后 5000 次微调中训练 | 用 |
| epinet 可训练部分 | `self.history_epinet_trainable` | 给历史编码器加上"随机扰动的修正量"，用来测不确定性 | 只在微调中训练 | 用 |
| epinet 先验部分 | `self.history_epinet_prior` | 一个**永远不训练**的随机网络 | 不训练 | 用 |
| 鲁棒策略/价值（可选） | `self.robust_actor`、`self.robust_critic` | 只有在**不**使用"零向量鲁棒点"时，才单独建一套鲁棒网络 | GRAM 主算法里不单独存在 | — |

**一句话概括这个文件**：它定义了"怎么从观测和历史算出动作"，以及"怎么算出不确定性和 α"。PPO 怎么更新这些网络，在 `gram_ppo.py` 里，不在这里。

### 先认识几个贯穿全文的术语

| 术语 | 小白解释 |
|---|---|
| `nn.Module` | PyTorch 里所有网络的"基类"。继承它之后，网络里的参数会被自动登记，方便保存、加载、放到 GPU |
| `nn.Linear(a, b)` | 全连接层：输入 a 个数，输出 b 个数。内部就是 y = Wx + b，W 是 b×a 的矩阵 |
| MLP | 多层感知机，就是好几个 `Linear` 叠起来，中间夹激活函数 |
| 激活函数 ELU | 一个非线性函数：x>0 时输出 x，x≤0 时输出 eˣ−1。没有它，多层线性叠起来还是线性 |
| 张量（tensor） | 多维数组。`shape` 是它的形状，例如 (4096, 8) 表示 4096 行 8 列 |
| batch（批） | 一次同时处理多少条数据。GRAM 有 4096 个并行环境，所以 batch 常常是 4096 |
| `nn.Parameter` | 会被优化器更新的张量；`requires_grad=False` 时只是"跟着模型保存"，不训练 |
| 梯度、`detach()` | 训练靠梯度更新参数。`x.detach()` 表示"把 x 当常数，梯度不要从这里往回传" |
| 正态分布 `Normal(μ, σ)` | 策略输出的不是一个确定的动作，而是一个以 μ 为中心、σ 为宽度的"钟形分布"，训练时从中采样，带来探索 |

### 本篇用到的维度符号

| 符号 | 含义 | GRAM 默认值 |
|---|---|---|
| `n_obs` | 策略每一步的观测维度 | 【推断】45 = 角速度 3 + 投影重力 3 + 速度指令 3 + 关节角 12 + 关节速度 12 + 上一步动作 12（Isaac Lab Go2 默认观测去掉机身线速度和高度扫描） |
| `n_critic_obs` | 价值网络的观测维度 | 由环境决定，可能比 n_obs 多（含特权观测） |
| `n_act` | 动作维度 | 12 |
| `n_ctx` | 上下文维度 | 26 |
| `d` = `num_latent` | 隐变量维度 | 8 |
| `H` = `obs_history_length` | 历史长度 | 16 |
| `m` = `history_epinet_dim` | epinet 随机输入维度 | 8 |
| `N` = `history_epinet_num_samples` | 每个数据点采样几次 | 8 |
| `B` | batch 大小 | 4096（并行环境数） |

---

## 1. 文件开头：导入（第 1–19 行）

**这段要干什么**：声明版权，导入要用的库。

```python
# gram_actor_critic.py:9-19
from __future__ import annotations

import itertools
import math

import torch
import torch.nn as nn
from rsl_rl.modules.actor_critic import get_activation
from torch.distributions import Normal

from source.utils.torch_utils import weight_init
```

**逐行解释**：
- `itertools`：后面用 `itertools.chain` 把好几组参数"串成一串"，交给优化器。
- `math`：用到 `math.log`（求 ln）。
- `get_activation`：从 rsl_rl 库借来的小函数，输入字符串 `"elu"`，返回 `nn.ELU()` 对象。
- `Normal`：正态分布，用于"策略输出一个分布，再从中采样动作"。
- `weight_init`：GRAM 自己写的初始化函数（`source/utils/torch_utils.py:11`）。【代码事实】它对每个 `nn.Linear` 用 **Xavier 正态初始化**权重、偏置置 0。

**小结**：GRAM 的网络建立在 rsl_rl 库（ETH 的足式机器人 RL 库）的基础上，只借用了它的激活函数工具，网络本身是自己写的。

---

## 2. 构造函数的参数表（第 22–74 行）

**这段要干什么**：定义类 `GRAMActorCritic`，列出所有可调参数和默认值。**这些参数决定了网络长什么样、不确定性怎么算。**

```python
# gram_actor_critic.py:22-74（节选，原样）
class GRAMActorCritic(nn.Module):

    def __init__(
        self,
        num_actor_obs,
        num_critic_obs,
        num_actions,
        num_context,
        num_latent,
        obs_history_length,
        actor_hidden_dims=[512, 256, 128],
        critic_hidden_dims=[512, 256, 128],
        context_hidden_dims=[64, 64],
        use_log_std=True,
        history_epinet=True,
        history_epinet_apply_bias=False,
        history_epinet_output_type="base",
        ...
        robust_use_latent_critic=True,
        **kwargs,
    ):
```

下面把**全部参数**按用途分组列出来。"实际值"一列指运行 `--alg_name gram` 时最终生效的值（会被 `cli_utils.py` 改写的已注明）。

### 2.1 维度类参数（必须给，没有默认值）

| 参数 | 含义 | 实际值 |
|---|---|---|
| `num_actor_obs` | 策略观测维度 n_obs | 【推断】45 |
| `num_critic_obs` | 价值网络观测维度 | 由环境决定 |
| `num_actions` | 动作维度 | 12 |
| `num_context` | 上下文维度 | 26 |
| `num_latent` | 隐变量维度 d | 8（`cli_utils.py:156`） |
| `obs_history_length` | 历史长度 H | 16（`cli_utils.py:161`） |

### 2.2 网络结构参数

| 参数 | 默认值 | 含义 |
|---|---|---|
| `actor_hidden_dims` | [512, 256, 128] | 策略网络隐藏层宽度 |
| `critic_hidden_dims` | [512, 256, 128] | 价值网络隐藏层宽度 |
| `context_hidden_dims` | [64, 64] | 上下文编码器隐藏层 |
| `history_encoder_hidden_dims` | [512, 256, 128] | 历史编码器隐藏层 |
| `history_epinet_hidden_dims` | [16, 16] | epinet 隐藏层（很小） |
| `activation` | "elu" | 激活函数 |

### 2.3 动作噪声参数

| 参数 | 默认值 | 含义 |
|---|---|---|
| `use_log_std` | True | 用 log σ 而不是 σ 作为可训练参数。好处：log σ 可以是任意实数，取 exp 后 σ 永远为正 |
| `init_noise_std` | 1.0 | 动作噪声的初始标准差 |

### 2.4 epinet（不确定性）参数——重点

| 参数 | 默认值 | 含义 |
|---|---|---|
| `history_epinet` | True（构造函数默认）；**`cli_utils` 先置 False，gram 算法再置 True** | 是否启用 epinet |
| `history_epinet_apply_bias` | False；**gram 评估时置 True**（`cli_utils.py:573`） | 是否用 α 把隐变量往 0 收缩。**名字里的 bias 指"往鲁棒点偏"**，不是神经网络的偏置 |
| `history_epinet_output_type` | "base" | α 乘的是 base 网络输出（"base"）还是 8 个样本的均值（"mean"） |
| `history_epinet_finetune_scale` | True | 是否用验证集定标 scale（论文的 λ） |
| `history_epinet_finetune_shift` | True | 是否用验证集定标 shift（论文的 β） |
| `history_epinet_finetune_min_quantile` | 0.90 | shift 取验证集的 0.90 分位数 |
| `history_epinet_finetune_max_quantile` | 0.99 | 在 0.99 分位数处 α 要等于 target |
| `history_epinet_finetune_target` | 0.01 | 上面那个 target |
| `history_epinet_type` | "mlp_dot" | epinet 结构类型（见第 4 节） |
| `history_epinet_input_type` | "concat" | epinet 输入取什么（见第 4 节） |
| `history_epinet_gain` | 1e-4 | 可训练 epinet 最后一层的初始化增益（很小） |
| `history_epinet_prior_gain` | 1.0 | 先验 epinet 最后一层的初始化增益（正常大小） |
| `history_epinet_dim` | 8 | 随机输入 ε 的维度 m |
| `history_epinet_num_samples` | 8 | 每个数据点采样 N 次 |
| `history_epinet_coef` | 1.0 | epinet 修正量的系数 |

### 2.5 上下文编码器选项

| 参数 | 默认值 | 含义 |
|---|---|---|
| `context_encoder_clamp` | False | 是否把 z 限幅到 ±clamp_value |
| `context_encoder_clamp_value` | 1.0 | 限幅值 |
| `context_encoder_stochastic` | False | 是否给 z 加噪声 |
| `context_encoder_noise_std` | 0.25 | 噪声标准差 |

GRAM 默认都不开。

### 2.6 初始化参数

| 参数 | 默认值 | 含义 |
|---|---|---|
| `init_nn_weights` | True | 是否用 Xavier 初始化 |
| `actor_gain`、`critic_gain`、`context_gain`、`history_gain` | 都是 1e-4 | 各网络**最后一层**的初始化增益 |

**为什么最后一层增益这么小（1e-4）？** Xavier 初始化的权重大小 ∝ gain。gain=1e-4 意味着最后一层权重几乎是 0，所以**训练刚开始时，网络输出几乎全是 0**：
- 策略输出 ≈ 0 → 动作 ≈ 默认站立姿态（动作是相对默认姿态的偏移），机器人一开始不会乱动；
- 上下文编码器输出 z ≈ 0 → 正好落在鲁棒点 z_rob = 0 附近。**论文 Sec. IV 说"z_t begins training near z_rob = 0"，靠的就是这个初始化。**

### 2.7 训练/推理选项

| 参数 | 默认值 | gram 训练时 | gram 评估时 | 含义 |
|---|---|---|---|---|
| `no_context_critic` | False | False | False | True 时价值网络不看 z |
| `latent_detach_actor` | False | False | — | True 时策略的梯度不传回上下文编码器 |
| `latent_detach_critic` | False | False | — | True 时价值网络的梯度不传回上下文编码器 |
| `robust_as_zeros` | True | **True** | **True** | 鲁棒模式 = 同一网络输入 z=0（GRAM 的核心设计） |
| `act_from_context` | True | **True** | **False** | True：z 来自上下文编码器（教师）；False：z 来自历史编码器（学生） |
| `act_inference_adapt` | False | False | **True** | 推理时强制使用"适应分支" |
| `act_inference_robust` | False | False | False | 推理时强制使用"鲁棒分支" |
| `robust_use_latent_actor` | False | — | — | 仅当单独建鲁棒网络时有意义 |
| `robust_use_latent_critic` | True | — | — | 同上 |

（"gram 训练/评估时"一列来自 `cli_utils.py:546-575`。）

**小结**：参数很多，但 GRAM 主算法真正关键的只有五个：`robust_as_zeros=True`、`history_epinet=True`、`act_from_context`（训练 True、评估 False）、`act_inference_adapt`（评估 True）、`history_epinet_apply_bias`（评估 True）。

---

## 3. 构造函数前半：适应部分的网络（第 75–183 行）

### 3.1 价值网络要不要看 z（第 75–85 行）

```python
# gram_actor_critic.py:75-85
        super().__init__()
        activation = get_activation(activation)

        if num_context == 0:
            raise ValueError("Algorithm requires context definition.")

        self.no_context_critic = no_context_critic
        if self.no_context_critic:
            num_latent_critic = 0
        else:
            num_latent_critic = num_latent
```

- `super().__init__()`：调用父类 `nn.Module` 的初始化，**必须写**，否则参数无法登记。
- `activation = get_activation(activation)`：把字符串 "elu" 变成 ELU 对象，后面所有网络共用。
- 没有上下文就报错：GRAM 依赖上下文，没有就无法训练教师。
- `num_latent_critic`：价值网络额外接收多少维 z。默认 8。

### 3.2 策略网络 actor（第 91–104 行）

```python
# gram_actor_critic.py:91-104
        mlp_input_dim_a = num_actor_obs + num_latent
        mlp_input_dim_c = num_critic_obs + num_latent_critic

        # Adaptive policy
        actor_layers = []
        actor_layers.append(nn.Linear(mlp_input_dim_a, actor_hidden_dims[0]))
        actor_layers.append(activation)
        for layer_index in range(len(actor_hidden_dims)):
            if layer_index == len(actor_hidden_dims) - 1:
                actor_layers.append(nn.Linear(actor_hidden_dims[layer_index], num_actions))
            else:
                actor_layers.append(nn.Linear(actor_hidden_dims[layer_index], actor_hidden_dims[layer_index + 1]))
                actor_layers.append(activation)
        self.actor = nn.Sequential(*actor_layers)
```

**逐行解释**：
- 输入维度 = 观测 + 隐变量 = n_obs + 8。**这就是"策略同时看观测和环境估计"的实现方式：直接拼接。**
- 先放一层 `Linear(n_obs+8 → 512)` 和 ELU；
- for 循环：对隐藏层列表 [512, 256, 128] 逐个处理：
  - 不是最后一个：加 `Linear(当前宽度 → 下一个宽度)` + ELU；
  - 是最后一个（128）：加 `Linear(128 → 12)`，**最后一层后面不加激活**，因为动作可以是任意实数。
- `nn.Sequential(*actor_layers)`：把列表里的层按顺序串起来，调用时数据依次流过。

**层结构表（n_obs=45 代入）**：

| 下标 | 层 | 输入维 | 输出维 |
|---|---|---|---|
| actor[0] | Linear | 45+8=53 | 512 |
| actor[1] | ELU | 512 | 512 |
| actor[2] | Linear | 512 | 256 |
| actor[3] | ELU | 256 | 256 |
| actor[4] | Linear | 256 | 128 |
| actor[5] | ELU | 128 | 128 |
| actor[6] | Linear | 128 | 12 |

参数量约：53×512 + 512×256 + 256×128 + 128×12 + 偏置 ≈ 2.0 万 + 13.1 万 + 3.3 万 + 0.15 万 ≈ **19 万**。

> 服务器冒烟测试的 checkpoint 里能看到 `actor.0.weight`、`actor.2.weight`、`actor.4.weight`、`actor.6.weight`，下标正好是 0、2、4、6（奇数下标是 ELU，没有参数），和上表对得上。

### 3.3 价值网络 critic（第 106–116 行）

```python
# gram_actor_critic.py:106-116
        # Adaptive value function
        critic_layers = []
        critic_layers.append(nn.Linear(mlp_input_dim_c, critic_hidden_dims[0]))
        critic_layers.append(activation)
        for layer_index in range(len(critic_hidden_dims)):
            if layer_index == len(critic_hidden_dims) - 1:
                critic_layers.append(nn.Linear(critic_hidden_dims[layer_index], 1))
            else:
                critic_layers.append(nn.Linear(critic_hidden_dims[layer_index], critic_hidden_dims[layer_index + 1]))
                critic_layers.append(activation)
        self.critic = nn.Sequential(*critic_layers)
```

和 actor 完全同构，只有两点不同：
- 输入是 `n_critic_obs + 8`；
- **最后输出 1 个数**：价值 V(s, z)，即"从这里往后大概能拿多少分"。

| 下标 | 层 | 输入维 | 输出维 |
|---|---|---|---|
| critic[0] | Linear | n_critic_obs+8 | 512 |
| critic[2] | Linear | 512 | 256 |
| critic[4] | Linear | 256 | 128 |
| critic[6] | Linear | 128 | **1** |

### 3.4 动作噪声（第 121–126 行）

```python
# gram_actor_critic.py:121-126
        # Action noise
        self.use_log_std = use_log_std
        if self.use_log_std:
            self.log_std = nn.Parameter(torch.log(init_noise_std * torch.ones(num_actions)))
        else:
            self.std = nn.Parameter(init_noise_std * torch.ones(num_actions))
```

- 每个关节一个噪声标准差，共 12 个，**和状态无关**（不是网络输出，是一组独立参数）。
- 初值：log(1.0 × [1,…,1]) = [0,…,0]，即 σ = 1。
- 训练中 PPO 会逐渐把 σ 调小，策略从"随机探索"变成"确定动作"。

**数值例子**：如果某时刻 log_std[0] = −1.2，则第 0 个关节的噪声 σ = e^{−1.2} ≈ 0.30。

### 3.5 上下文编码器 context_encoder（第 128–143 行）

```python
# gram_actor_critic.py:128-143
        # Context encoder
        context_layers = []
        context_layers.append(nn.Linear(num_context, context_hidden_dims[0]))
        context_layers.append(activation)
        for layer_index in range(len(context_hidden_dims)):
            if layer_index == len(context_hidden_dims) - 1:
                context_layers.append(nn.Linear(context_hidden_dims[layer_index], num_latent))
            else:
                context_layers.append(nn.Linear(context_hidden_dims[layer_index], context_hidden_dims[layer_index + 1]))
                context_layers.append(activation)
        self.context_encoder = nn.Sequential(*context_layers)

        print(f"Context Encoder MLP: {self.context_encoder}")

        self.context_encoder_stochastic = context_encoder_stochastic
        self.context_encoder_noise_std = context_encoder_noise_std
```

**这就是论文里的 f：C → Z**，把 26 维真实环境参数压缩成 8 维 z。

| 下标 | 层 | 输入维 | 输出维 |
|---|---|---|---|
| context_encoder[0] | Linear | 26 | 64 |
| context_encoder[1] | ELU | 64 | 64 |
| context_encoder[2] | Linear | 64 | 64 |
| context_encoder[3] | ELU | 64 | 64 |
| context_encoder[4] | Linear | 64 | **8** |

**为什么要压缩？** 26 维里很多维对动作的影响相似（比如 12 个电机强度），压成 8 维既去掉冗余，也让学生（历史编码器）的回归目标更简单。

**【关键】这 8 维没有物理含义**：哪一维对应摩擦、哪一维对应电机，网络自己决定，我们不知道。**这是后面"分组不确定性"必须先改上下文编码器的原因**（见第 13 节）。

### 3.6 历史编码器的配置保存（第 145–167 行）

```python
# gram_actor_critic.py:145-167
        # History encoder
        self.obs_history_length = obs_history_length

        self.history_epinet = history_epinet
        self.history_epinet_apply_bias = history_epinet_apply_bias
        self.history_epinet_output_type = history_epinet_output_type
        self.history_epinet_finetune_scale = history_epinet_finetune_scale
        self.history_epinet_finetune_shift = history_epinet_finetune_shift
        self.history_epinet_finetune_min_quantile = history_epinet_finetune_min_quantile
        self.history_epinet_finetune_max_quantile = history_epinet_finetune_max_quantile
        self.history_epinet_finetune_target = history_epinet_finetune_target

        self.validation_quantiles_q = nn.Parameter(torch.linspace(0, 1, 101), requires_grad=False)
        self.validation_quantiles_value = nn.Parameter(torch.zeros(101), requires_grad=False)
        self.validation_quantiles_saved = nn.Parameter(torch.tensor(False), requires_grad=False)
        self.set_uncertainty_params()

        self.history_epinet_type = history_epinet_type
        self.history_epinet_input_type = history_epinet_input_type
        self.history_epinet_dim = history_epinet_dim
        self.history_epinet_num_samples = history_epinet_num_samples
        self.history_epinet_coef = history_epinet_coef
        self.history_epinet_coef_active = history_epinet_coef
```

前面几行只是把参数存成成员变量。**中间三行非常重要**：

| 变量 | 形状 | 含义 |
|---|---|---|
| `validation_quantiles_q` | (101,) | [0, 0.01, 0.02, …, 1.00]，101 个分位点 |
| `validation_quantiles_value` | (101,) | 验证集上不确定性的 101 个分位数值，初始全 0 |
| `validation_quantiles_saved` | 标量布尔 | 是否已经算过验证集，初始 False |

**为什么用 `nn.Parameter(..., requires_grad=False)` 而不是普通张量？** 因为 `nn.Parameter` 会被写进 `state_dict`，**随 checkpoint 一起保存和加载**；`requires_grad=False` 保证优化器不会改它。这样训练结束时算好的分位数，部署时加载模型就能直接用。服务器冒烟测试的 checkpoint 变化列表里确实有 `validation_quantiles_value` 和 `validation_quantiles_saved`。

- `self.set_uncertainty_params()`：用当前分位数算 shift、scale（详见第 11 节）。此时还没有验证集，所以 shift=0、scale=1。
- `history_epinet_coef_active`：epinet 修正量的"当前生效系数"，默认 1.0。【代码事实】全仓库只有这个文件里读它，没有别处修改。

### 3.7 历史编码器 history_encoder（第 169–183 行）

```python
# gram_actor_critic.py:169-181
        encode_layers = []
        encode_layers.append(nn.Flatten())
        encode_layers.append(nn.Linear(num_actor_obs * self.obs_history_length, history_encoder_hidden_dims[0]))
        encode_layers.append(activation)
        for layer_index in range(len(history_encoder_hidden_dims)):
            if layer_index == len(history_encoder_hidden_dims) - 1:
                encode_layers.append(nn.Linear(history_encoder_hidden_dims[layer_index], num_latent))
            else:
                encode_layers.append(
                    nn.Linear(history_encoder_hidden_dims[layer_index], history_encoder_hidden_dims[layer_index + 1])
                )
                encode_layers.append(activation)
        self.history_encoder = nn.Sequential(*encode_layers)
```

**这就是论文里的 φ_base**：从历史估计 z。

**历史长什么样？**【代码事实】在 runner 里（`gram_on_policy_runner.py:192-196`），历史是一个形状 (B, 16, n_obs) 的张量，每一步把最老的一帧挤掉、新观测接到末尾；环境重置时清零。也就是说，**历史里只有观测，没有单独存动作**；但观测本身包含"上一步动作"，所以动作信息间接包含在内。

| 下标 | 层 | 输入 | 输出 |
|---|---|---|---|
| history_encoder[0] | Flatten | (B, 16, 45) | (B, 720) |
| history_encoder[1] | Linear | 720 | 512 |
| history_encoder[2] | ELU | 512 | 512 |
| history_encoder[3] | Linear | 512 | 256 |
| history_encoder[4] | ELU | 256 | 256 |
| history_encoder[5] | Linear | 256 | 128 |
| history_encoder[6] | ELU | 128 | 128 |
| history_encoder[7] | Linear | 128 | **8** |

- `nn.Flatten()`：把 (B, 16, 45) 展平成 (B, 720)。它把 16 帧直接首尾拼起来，**不考虑时间顺序结构**，是最简单的做法（RMA 用的是一维卷积，这里用 MLP）。
- **后面会多次用到 `self.history_encoder[:-1]`**：Python 切片"去掉最后一个元素"，即只跑到 history_encoder[6]（ELU 之后），输出 **128 维中间特征**。这就是论文说的"base 网络最后一个隐藏层的输出"。

服务器 checkpoint 的变化列表里有 `history_encoder.1/3/5/7.weight`，下标和上表一致。

**小结**：前半段建了四个普通网络：actor、critic、context_encoder、history_encoder。教师路线是 `context_encoder → actor`，学生路线是 `history_encoder → actor`。

---

## 4. 构造函数：epinet（第 185–263 行）——理解不确定性的关键

### 4.1 epinet 的输入维度：三种 input_type（第 185–195 行）

```python
# gram_actor_critic.py:185-195
        if self.history_epinet:
            self.input_flattener = nn.Flatten()

            if self.history_epinet_input_type == "full":
                epinet_in_dim = num_actor_obs * self.obs_history_length + self.history_epinet_dim
            elif self.history_epinet_input_type == "concat":
                epinet_in_dim = (
                    num_actor_obs * self.obs_history_length + history_encoder_hidden_dims[-1] + self.history_epinet_dim
                )
            else:
                epinet_in_dim = history_encoder_hidden_dims[-1] + self.history_epinet_dim
```

epinet 要知道"当前是什么历史"，还要接收随机向量 ε。输入有三种选法：

| input_type | epinet 输入 = | 维度（n_obs=45） | 含义 |
|---|---|---|---|
| "full" | 展平历史 + ε | 720 + 8 = 728 | 只看原始历史 |
| **"concat"（默认）** | 展平历史 + base 的 128 维特征 + ε | 720 + 128 + 8 = **856** | 原始历史和 base 学到的特征都看 |
| 其它（如 "feature"） | base 的 128 维特征 + ε | 128 + 8 = 136 | 只看 base 的特征 |

**【论文对照】** 论文式 (5) 写 h̃_t 是"h_t 和 φ_base 最后隐藏层输出的拼接，并截断梯度"，正好对应 "concat"。

### 4.2 两种 epinet 结构：mlp 和 mlp_dot（第 197–263 行）

每种类型都建**两个结构完全相同的网络**：`history_epinet_trainable`（可训练）和 `history_epinet_prior`（先验，冻结）。

**类型一："mlp"（第 197–227 行）**

```python
# gram_actor_critic.py:197-227（节选）
            if self.history_epinet_type == "mlp":
                epinet_layers = []
                epinet_layers.append(nn.Linear(epinet_in_dim, history_epinet_hidden_dims[0]))
                epinet_layers.append(activation)
                ...
                        epinet_layers.append(nn.Linear(history_epinet_hidden_dims[layer_index], num_latent))
                ...
                self.history_epinet_trainable = nn.Sequential(*epinet_layers)
                ... (同样结构再建一遍)
                self.history_epinet_prior = nn.Sequential(*epinet_layers)
                self.history_epinet_prior.requires_grad_(requires_grad=False)
```

结构：856 → 16 → 16 → **8**，直接输出 8 维修正量。ε 只作为输入的一部分进入网络。

**类型二："mlp_dot"（默认，第 229–263 行）**

```python
# gram_actor_critic.py:229-263（节选）
            elif self.history_epinet_type == "mlp_dot":
                epinet_layers = []
                epinet_layers.append(nn.Linear(epinet_in_dim, history_epinet_hidden_dims[0]))
                epinet_layers.append(activation)
                for layer_index in range(len(history_epinet_hidden_dims)):
                    if layer_index == len(history_epinet_hidden_dims) - 1:
                        epinet_layers.append(
                            nn.Linear(history_epinet_hidden_dims[layer_index], num_latent * self.history_epinet_dim)
                        )
                    ...
                self.history_epinet_trainable = nn.Sequential(*epinet_layers)
                ... (同样结构再建一遍)
                self.history_epinet_prior = nn.Sequential(*epinet_layers)
                self.history_epinet_prior.requires_grad_(requires_grad=False)
```

结构：856 → 16 → 16 → **64**（= d × m = 8 × 8）。

| 下标 | 层 | 输入维 | 输出维 |
|---|---|---|---|
| [0] | Linear | 856 | 16 |
| [1] | ELU | 16 | 16 |
| [2] | Linear | 16 | 16 |
| [3] | ELU | 16 | 16 |
| [4] | Linear | 16 | **64** |

**64 个数怎么用？** 后面会把它变形成一个 **8×8 矩阵 M**，再和 ε（8 维）做矩阵乘：修正量 = M·ε（8 维）。

**mlp 和 mlp_dot 的区别（小白版）**：
- mlp：ε 只是输入里的 8 个数，网络可能学会"忽略 ε"，那样所有样本的输出都一样，测不出不确定性；
- mlp_dot：输出**显式地乘以 ε**。只要矩阵 M 不为零，不同的 ε 就一定给出不同的结果。M 越大，输出随 ε 摆动越大，不确定性越高。**M 的大小就是"网络对这个输入有多没把握"**。这是 Osband 等人 epinet 论文推荐的形式。

### 4.3 为什么要两个网络、为什么先验要冻结

`self.history_epinet_prior.requires_grad_(requires_grad=False)` 把先验网络的所有参数设为不可训练。最终用的是：

**修正量 = (trainable(输入) − prior(输入)) · ε**

**用打比方来理解**：
- 先验网络是一个随机初始化、永远不变的网络，它对**任何**输入都会输出一个"乱七八糟"的矩阵 M_prior。所以如果只有它，所有输入的不确定性都很高。
- 可训练网络在训练中学会：**在训练见过的历史上，输出 M_train ≈ M_prior**，两者相减接近 0，修正量接近 0，8 个样本几乎一样，方差小。
- 在没见过的历史上，可训练网络没有被训练去"抵消"先验，M_train − M_prior 仍然不小，修正量随 ε 剧烈变化，方差大。

**为什么一定要冻结先验？** 如果先验也能训练，最省事的办法是让两个网络一起变成 0，那么所有输入的方差都是 0，不确定性就失效了。冻结先验，等于给每个输入都预先"埋下"不确定性，只有见过的数据才能把它消掉。

### 4.4 两个 gain 的意义：1e-4 和 1.0

这在第 357–359 行设置（第 7 节会再看到）：

```python
        if self.history_epinet:
            nn.init.xavier_normal_(self.history_epinet_trainable[-1].weight, gain=history_epinet_gain)
            nn.init.xavier_normal_(self.history_epinet_prior[-1].weight, gain=history_epinet_prior_gain)
```

| 网络 | 最后一层 gain | 初始输出 | 意图 |
|---|---|---|---|
| trainable | 1e-4 | 几乎为 0 | 训练开始时不干扰，从"什么都没学"出发 |
| prior | 1.0 | 正常大小 | 一开始就给所有输入"埋下"明显的不确定性 |

所以训练开始时：差值 ≈ −prior，不确定性在所有输入上都很高；训练后，见过的输入不确定性降低。

**小结**：epinet = "固定的乱说者（prior）"+"学会在见过的地方纠正它的纠正者（trainable）"，输出再乘以随机向量 ε。8 个 ε 结果的分散程度就是不确定性。

---

## 5. 构造函数：鲁棒部分（第 265–325 行）

### 5.1 两条路径：robust_as_zeros = True / False

```python
# gram_actor_critic.py:269-279
        self.robust_as_zeros = robust_as_zeros
        self.robust_use_latent_actor = robust_use_latent_actor
        self.robust_use_latent_critic = robust_use_latent_critic

        if self.robust_as_zeros:
            self.robust_actor = self.actor
            self.robust_critic = self.critic
            if self.use_log_std:
                self.robust_log_std = self.log_std
            else:
                self.robust_std = self.std
```

**路径 A：`robust_as_zeros=True`（GRAM 主算法）**
- `self.robust_actor = self.actor`：**不是复制，是起了个别名**，两个名字指向同一个网络。
- 噪声参数也共用。
- 所以"鲁棒策略"就是**同一个策略网络输入 z=0**。这对应论文 Sec. IV 的核心设计：**鲁棒模式只是隐空间里的一个点 z_rob=0**。

**路径 B：`robust_as_zeros=False`（Modular 消融、robust_rl、domain_rand）**

```python
# gram_actor_critic.py:280-325（节选）
        else:
            if self.robust_use_latent_actor:
                mlp_input_dim_a_robust = num_actor_obs + num_latent
            else:
                mlp_input_dim_a_robust = num_actor_obs
            ...
            # Robust policy
            robust_actor_layers = []
            robust_actor_layers.append(nn.Linear(mlp_input_dim_a_robust, actor_hidden_dims[0]))
            ...
            self.robust_actor = nn.Sequential(*robust_actor_layers)
            # Robust value function
            ...
            self.robust_critic = nn.Sequential(*robust_critic_layers)
            # Action noise
            if self.use_log_std:
                self.robust_log_std = nn.Parameter(torch.log(init_noise_std * torch.ones(num_actions)))
```

- 单独建一套**结构相同、参数独立**的鲁棒策略和价值网络，以及独立的噪声参数。
- 默认 `robust_use_latent_actor=False`：鲁棒策略**只看观测，不看 z**，输入维度是 n_obs。
- 默认 `robust_use_latent_critic=True`：鲁棒价值网络看 z（价值网络只在训练时用，看特权信息有助于估值）。

**这对理解基线很重要**：

| 算法 | 用哪条路径 | 部署时实际用的策略 |
|---|---|---|
| gram | A | `actor(obs, α·ẑ)` |
| gram_separate | A | 同上，只是训练数据不混合 |
| gram_modular | B | 不确定性超过阈值 → `robust_actor(obs)`，否则 `actor(obs, ẑ)`，**硬切换两个独立网络** |
| robust_rl | B | `robust_actor(obs)`，加对抗者训练 |
| domain_rand | B | `robust_actor(obs)`，不加对抗者 |
| contextual_rl | B（但只训练适应分支） | `actor(obs, ẑ)` |

**有个小知识**：服务器冒烟测试的 checkpoint 里出现了 `robust_actor.*` 和 `robust_critic.*` 两组键。因为路径 A 里它们只是别名，PyTorch 的 `state_dict` 会把同一组参数**以两个名字各存一份**。这不代表 GRAM 真有两套网络。【推断，依据 PyTorch 的别名行为】

**小结**：GRAM 的"一个网络两种模式"在代码里就是一行 `self.robust_actor = self.actor`。

---

## 6. 构造函数：其他设置（第 327–343 行）

```python
# gram_actor_critic.py:327-343
        # Distribution
        self.distribution = None
        # disable args validation for speedup
        Normal.set_default_validate_args = False

        # Action options
        self.act_from_context = act_from_context
        self.act_inference_adapt = act_inference_adapt
        self.act_inference_robust = act_inference_robust

        # Context training arguments
        self.latent_detach_actor = latent_detach_actor
        self.latent_detach_critic = latent_detach_critic
        self.context_encoder_clamp = context_encoder_clamp
        self.context_encoder_clamp_value = context_encoder_clamp_value
```

- `self.distribution`：存放"当前这批数据的动作分布"，每次调用 `update_distribution` 时更新。
- `Normal.set_default_validate_args = False`：关闭参数合法性检查以提速（每步对 4096 个样本建分布，检查开销不小）。
- 其余都是保存选项。

---

## 7. 构造函数：初始化与参数分组（第 345–414 行）

### 7.1 初始化（第 345–359 行）

```python
# gram_actor_critic.py:345-359
        # Initialize NN weights
        if init_nn_weights:
            self.apply(weight_init)
            nn.init.xavier_normal_(self.actor[-1].weight, gain=actor_gain)
            nn.init.xavier_normal_(self.critic[-1].weight, gain=critic_gain)
            nn.init.xavier_normal_(self.context_encoder[-1].weight, gain=context_gain)
            nn.init.xavier_normal_(self.history_encoder[-1].weight, gain=history_gain)

            if not self.robust_as_zeros:
                nn.init.xavier_normal_(self.robust_actor[-1].weight, gain=actor_gain)
                nn.init.xavier_normal_(self.robust_critic[-1].weight, gain=critic_gain)

        if self.history_epinet:
            nn.init.xavier_normal_(self.history_epinet_trainable[-1].weight, gain=history_epinet_gain)
            nn.init.xavier_normal_(self.history_epinet_prior[-1].weight, gain=history_epinet_prior_gain)
```

- `self.apply(weight_init)`：对类里**每一个子模块**都调用一次 `weight_init`，所有 Linear 层先用 gain=1 的 Xavier 初始化、偏置置 0。
- 然后**单独重设每个网络最后一层**的权重，用很小的 gain（1e-4），原因见 2.6 节。
- epinet 的两个 gain 见 4.4 节。注意它**不在** `if init_nn_weights` 里面，无论如何都会执行。

**Xavier 初始化（小白版）**：一种按层宽度自动决定初始权重大小的方法，权重从均值 0、标准差 gain × √(2/(输入宽+输出宽)) 的正态分布中抽取。目的是让信号在层间传递时不至于越来越大或越来越小。

**数值例子**：actor 最后一层是 128→12，标准差 = gain × √(2/140) ≈ gain × 0.12。gain=1e-4 时标准差约 1.2×10⁻⁵，所以初始动作输出在 10⁻⁵ 量级，几乎为 0。

### 7.2 参数分组（第 361–414 行）

```python
# gram_actor_critic.py:369-375（robust_as_zeros=True 的分支）
        if self.robust_as_zeros:
            self.ac_params = itertools.chain(
                self.actor.parameters(),
                std_params,
                self.critic.parameters(),
                self.context_encoder.parameters(),
            )
            ...
        self.context_params = self.context_encoder.parameters()
        self.opt_params = self.ac_params

        if self.history_epinet:
            self.history_params = itertools.chain(
                self.history_encoder.parameters(),
                self.history_epinet_trainable.parameters(),
            )
        else:
            self.history_params = self.history_encoder.parameters()
```

**为什么要分组？** 因为 GRAM 的不同阶段训练不同的网络：

| 参数组 | 包含 | 谁用（在 gram_ppo.py 中） | 什么时候训练 |
|---|---|---|---|
| `ac_params` / `opt_params` | actor、噪声、critic、context_encoder（路径 B 再加鲁棒网络） | PPO 主优化器 | RL 阶段（前 10000 次） |
| `ac_adapt_params` | actor、噪声、critic | 适应分支专用 | — |
| `ac_robust_params` | 鲁棒网络（仅路径 B） | 鲁棒分支专用 | — |
| `context_params` | context_encoder | — | — |
| `history_params` | history_encoder + epinet_trainable | 历史优化器 | 微调阶段（最后 5000 次） |

**注意两点**：
1. `history_params` 里**没有** `history_epinet_prior`：先验不训练，和 4.3 节一致。
2. `itertools.chain` 生成的是一个**只能遍历一次**的迭代器。【推断】它们应该在构造优化器时只用一次；如果在别处再遍历，会发现是空的。这是读代码时容易踩的坑。

**小结**：构造函数到这里结束。它建好了所有网络、设好了初始化，并把参数按"RL 阶段训练"和"微调阶段训练"分成两组。

---

## 8. 简单的辅助函数（第 416–447 行）

```python
# gram_actor_critic.py:416-447
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

    @property
    def entropy(self):
        return self.distribution.entropy().sum(dim=-1)

    def get_std(self):
        if self.use_log_std:
            return torch.exp(self.log_std)
        else:
            return self.std

    def get_robust_std(self):
        ...

    def get_actions_log_prob(self, actions):
        return self.distribution.log_prob(actions).sum(dim=-1)
```

| 函数 | 作用 |
|---|---|
| `reset` | 环境重置时调用。网络没有内部记忆（不是 RNN），所以什么都不做 |
| `forward` | 故意不实现。必须明确调用 `act`、`evaluate` 等，避免误用 |
| `action_mean` | 当前分布的均值 μ（12 维），即"确定性动作" |
| `action_std` | 当前分布的标准差 σ |
| `entropy` | 分布的熵，12 个关节求和。PPO 用它鼓励探索 |
| `get_std` | 返回噪声标准差（log_std 取 exp） |
| `get_actions_log_prob` | 计算"某个动作在当前分布下的对数概率"，12 维求和。PPO 的比值 r = exp(新 log p − 旧 log p) 就靠它 |

**@property 是什么**：让函数可以像变量一样访问，写 `self.action_mean` 而不是 `self.action_mean()`。

**为什么 log_prob 要求和**：12 个关节的噪声相互独立，联合概率 = 各自概率相乘，取 log 后就是相加。

---

## 9. 动作与价值的计算（第 449–546 行）

### 9.1 update_distribution：两种模式怎么混合（第 449–472 行）

**这段要干什么**：给定观测、隐变量 z 和鲁棒掩码，算出动作分布。**这是"一个网络两种模式"在前向计算中的实现。**

```python
# gram_actor_critic.py:449-472
    def update_distribution(self, observations, latent, robust_masks):
        actor_input = torch.cat([observations, latent], dim=-1)
        if self.robust_as_zeros:
            robust_latent = torch.zeros_like(latent.detach())
            robust_actor_input = torch.cat([observations, robust_latent], dim=-1)
        else:
            if self.robust_use_latent_actor:
                robust_actor_input = actor_input
            else:
                robust_actor_input = observations

        robust_mean = self.robust_actor(robust_actor_input)
        adapt_mean = self.actor(actor_input)

        mean = robust_masks * robust_mean + (1 - robust_masks) * adapt_mean
        mean_clamp = mean.clamp(min=-20.0, max=20.0)

        if self.use_log_std:
            log_std = robust_masks * self.robust_log_std + (1 - robust_masks) * self.log_std
            std = torch.exp(log_std)
        else:
            std = robust_masks * self.robust_std + (1 - robust_masks) * self.std

        self.distribution = Normal(mean_clamp, mean_clamp * 0.0 + std)
```

**逐行解释**：

| 行 | 做了什么 | 形状（B=4096） |
|---|---|---|
| 450 | 观测和 z 拼起来，作为"适应分支"输入 | (4096, 45) + (4096, 8) → (4096, 53) |
| 452 | 造一个和 z 同形状的全 0 张量。`detach()` 保证不传梯度 | (4096, 8) |
| 453 | 观测和 0 拼起来，作为"鲁棒分支"输入 | (4096, 53) |
| 455–458 | 路径 B：鲁棒分支输入要么带 z，要么只有观测 | — |
| 460 | 鲁棒分支前向 | (4096, 12) |
| 461 | 适应分支前向 | (4096, 12) |
| 463 | **按掩码选择**：mask=1 用鲁棒结果，mask=0 用适应结果 | (4096, 12) |
| 464 | 限幅到 [−20, 20]，防止数值爆炸 | (4096, 12) |
| 466–470 | 噪声也按掩码选 | (12,) 广播到 (4096, 12) |
| 472 | 建立正态分布。`mean_clamp * 0.0 + std` 是一个小技巧：把 (12,) 的 std 广播成 (4096, 12) | — |

**`robust_masks` 是什么？** 形状 (B, 1)，每个环境一个 0 或 1。1 表示"这个环境本轮做鲁棒训练"，0 表示"做适应训练"。它在 runner 里每次迭代翻转一次（见 runner 的精读）。

**数值例子**：两个环境，掩码 [[1], [0]]。
- 环境 0：mean = 1×robust_mean + 0×adapt_mean = robust_mean，**用 z=0 的输出**；
- 环境 1：mean = adapt_mean，**用真实 z 的输出**。

**一个值得注意的细节**：每次都对**所有**环境同时算两个分支，再用掩码挑一个。算力上浪费了一半，但代码简单、可以整批并行。在路径 A 里，两个分支用的是同一个网络，只是输入的 z 不同。

### 9.2 act：训练时采样动作（第 474–482 行）

```python
# gram_actor_critic.py:474-482
    def act(self, observations, context, observations_history, robust_masks, **kwargs):
        latent = self.calculate_latent(context, observations_history, from_context=self.act_from_context)

        if self.latent_detach_actor:
            self.update_distribution(observations, latent.detach(), robust_masks)
        else:
            self.update_distribution(observations, latent, robust_masks)

        return self.distribution.sample()
```

- 第 475 行：算 z。**训练时 `act_from_context=True`**，所以 z = context_encoder(真实上下文)，也就是**教师模式**。历史编码器在 RL 阶段收集数据时**不参与**。
- 第 477–480 行：默认不 detach，于是 PPO 的梯度可以一路传回 context_encoder，**上下文编码器和策略一起训练**（论文式 3 的"f、π、V 一起训练"）。
- 第 482 行：从分布中**随机采样**动作，带来探索。

### 9.3 act_inference_from_mask：按指定掩码推理（第 484–501 行）

```python
# gram_actor_critic.py:484-501
    def act_inference_from_mask(
        self, observations, context, observations_history, robust_masks=None, deterministic=False
    ):
        latent = self.calculate_latent(context, observations_history, from_context=self.act_from_context)

        if self.act_inference_robust:
            robust_masks = torch.ones((observations.shape[0], 1), device=observations.device)
        elif self.act_inference_adapt or (robust_masks is None):
            robust_masks = torch.zeros((observations.shape[0], 1), device=observations.device)

        self.update_distribution(observations, latent, robust_masks)

        if deterministic:
            actions = self.action_mean
        else:
            actions = self.distribution.sample()

        return actions
```

- 用于**收集验证数据或微调数据**这类"由外部指定用哪个分支"的场合。
- 优先级：强制鲁棒 > 强制适应或没给掩码 > 使用传入的掩码。
- `deterministic=True` 时直接用均值动作，不加噪声。

### 9.4 act_inference：部署时推理（第 503–520 行）

```python
# gram_actor_critic.py:503-520
    def act_inference(self, observations, context, observations_history, uncertainty_metric, deterministic=False):
        latent = self.calculate_latent(context, observations_history, from_context=self.act_from_context)

        robust_masks = self.calculate_uncertainty_mask(uncertainty_metric)

        if self.act_inference_robust:
            robust_masks = torch.ones_like(robust_masks)
        elif self.act_inference_adapt:
            robust_masks = torch.zeros_like(robust_masks)

        self.update_distribution(observations, latent, robust_masks)
        ...
```

**这是评估时（`runner.evaluate`，`gram_on_policy_runner.py:661`）真正调用的函数。** 按算法走一遍：

| 算法 | 第 504 行 latent | 第 506 行掩码 | 第 508–511 行覆盖后 | 实际动作 |
|---|---|---|---|---|
| **gram** | 评估时 `act_from_context=False` → 历史编码器 + **α 收缩**（因为 `apply_bias=True`） | 硬阈值算出 | `act_inference_adapt=True` → **全 0** | `actor(obs, α·ẑ)` |
| gram_modular | 历史编码器，**不收缩**（apply_bias=False） | 硬阈值：不确定性 > q99 → 1 | 不覆盖 | 超阈值用 `robust_actor(obs)`，否则 `actor(obs, ẑ)` |
| robust_rl / domain_rand | 历史编码器 | — | `act_inference_robust=True` → 全 1 | `robust_actor(obs)` |
| contextual_rl | 历史编码器，不收缩 | — | 全 0 | `actor(obs, ẑ)` |

**关键理解**：GRAM 部署时**永远走"适应分支"**，靠 α 把 z 往 0 拉来实现"变保守"；Modular 则是在两个网络之间**硬切换**。这就是论文 Table III 中 GRAM 与 Modular 的区别。

### 9.5 evaluate：计算价值（第 522–546 行）

```python
# gram_actor_critic.py:522-546
    def evaluate(self, critic_observations, context, observations_history, robust_masks, **kwargs):
        if self.no_context_critic:
            critic_input = critic_observations
            robust_critic_input = critic_input
        else:
            latent = self.calculate_latent(context, observations_history, from_context=self.act_from_context)
            if self.latent_detach_critic:
                critic_input = torch.cat([critic_observations, latent.detach()], dim=-1)
            else:
                critic_input = torch.cat([critic_observations, latent], dim=-1)

            if self.robust_as_zeros:
                robust_latent = torch.zeros_like(latent.detach())
                robust_critic_input = torch.cat([critic_observations, robust_latent], dim=-1)
            else:
                ...

        robust_value = self.robust_critic(robust_critic_input)
        adapt_value = self.critic(critic_input)
        value = robust_masks * robust_value + (1 - robust_masks) * adapt_value

        return value
```

和 `update_distribution` 完全同理，只是网络换成 critic，输出 (B, 1) 的价值。**鲁棒环境的价值也用 z=0 来估**，保证鲁棒模式下"策略看到的"和"价值网络看到的"一致。

**小结**：第 9 节五个函数的关系：

```
训练收集数据：  act()  ──→ calculate_latent(用上下文) ──→ update_distribution(按 robust_masks 混合) ──→ 采样
训练估值：      evaluate() ──→ 同上，网络换成 critic
部署：          act_inference() ──→ calculate_latent(用历史 + α 收缩) ──→ update_distribution(掩码全 0) ──→ 动作
```

---

## 10. 隐变量的计算（第 548–662 行）——全文核心

### 10.1 calculate_latent：选教师还是学生（第 548–554 行）

```python
# gram_actor_critic.py:548-554
    def calculate_latent(self, context, observations_history, from_context=True):
        if from_context:
            latent = self.encode_context(context)
        else:
            latent = self.encode_history(observations_history)

        return latent
```

一个开关：`from_context=True` 走教师（真实上下文），False 走学生（历史）。

### 10.2 encode_context：教师编码（第 556–565 行）

```python
# gram_actor_critic.py:556-565
    def encode_context(self, context):
        latent = self.context_encoder(context)
        if self.context_encoder_clamp:
            latent = latent.clamp(min=self.context_encoder_clamp_value * -1, max=self.context_encoder_clamp_value)

        if self.context_encoder_stochastic:
            latent_noise = torch.randn_like(latent.detach()) * self.context_encoder_noise_std
            latent = latent + latent_noise

        return latent
```

- 主体就一行：(B, 26) → context_encoder → (B, 8)。
- 两个可选项默认都关：限幅、加噪声。（加噪声可以让教师对 z 的小误差更鲁棒，有些 RMA 变体这样做；GRAM 没用。）

### 10.3 encode_history：学生编码 + 不确定性 + α（第 567–620 行）——最重要的函数

**这段要干什么**：从 16 步历史估计 z；如果开了 epinet，就采样 8 次算不确定性；如果开了 apply_bias（GRAM 评估时），就用 α 把 z 往 0 收缩。

```python
# gram_actor_critic.py:567-620
    def encode_history(self, observations_history):
        latent = self.history_encoder(observations_history)
        if self.history_epinet:
            if self.history_epinet_input_type == "full":
                encoder_feature = self.input_flattener(observations_history).detach()
            elif self.history_epinet_input_type == "concat":
                full_feature = self.input_flattener(observations_history).detach()
                encoder_feature = self.history_encoder[:-1](observations_history).detach()
                encoder_feature = torch.cat([full_feature, encoder_feature], dim=-1)
            else:
                encoder_feature = self.history_encoder[:-1](observations_history).detach()

            encoder_feature_repeat = encoder_feature.unsqueeze(dim=0).repeat((self.history_epinet_num_samples, 1, 1))

            epinet_samples = torch.randn(
                (self.history_epinet_num_samples, self.history_epinet_dim), device=encoder_feature.device
            )
            epinet_samples_repeat = epinet_samples.unsqueeze(dim=1).repeat((1, encoder_feature.shape[0], 1))

            # shape: (epinet_samples, batch_size, total_epinet_input_size)  # noqa: E800
            epinet_input = torch.cat([encoder_feature_repeat, epinet_samples_repeat], dim=-1)

            # shape: (epinet_samples, batch_size, total_epinet_output_size)  # noqa: E800
            epinet_output_trainable = self.history_epinet_trainable(epinet_input)
            epinet_output_prior = self.history_epinet_prior(epinet_input)
            epinet_output_difference = epinet_output_trainable - epinet_output_prior

            # shape: (epinet_samples, batch_size, latent_size)  # noqa: E800
            if self.history_epinet_type == "mlp":
                epinet_term_all = epinet_output_difference
            elif self.history_epinet_type == "mlp_dot":
                epinet_output_difference = epinet_output_difference.reshape(
                    (epinet_output_difference.shape[0], epinet_output_difference.shape[1], -1, self.history_epinet_dim)
                )
                epinet_term_all = (epinet_output_difference * epinet_samples_repeat.unsqueeze(dim=-2)).sum(dim=-1)

            latent_all = latent + self.history_epinet_coef_active * epinet_term_all
            latent_mean = latent_all.mean(dim=0)

            if self.history_epinet_apply_bias:
                latent_std_l2 = latent_all.var(dim=0).sum(dim=-1)
                uncertainty = (latent_std_l2 - self.history_epinet_shift_param).clamp(min=0)
                alpha = torch.exp(self.history_epinet_scale_param * uncertainty * -1)

                if self.history_epinet_output_type == "mean":
                    latent = alpha.unsqueeze(dim=-1) * latent_mean
                else:
                    latent = alpha.unsqueeze(dim=-1) * latent

            else:
                if self.history_epinet_output_type == "mean":
                    latent = latent_mean

        return latent
```

#### (1) 张量形状逐行变化表

代入 B=4096，N=8（num_samples），m=8（epinet_dim），d=8（latent），n_obs=45【推断】，H=16，input_type="concat"，type="mlp_dot"。

| 行 | 代码 | 结果形状 | 说明 |
|---|---|---|---|
| — | 输入 `observations_history` | (4096, 16, 45) | 每个环境最近 16 帧观测 |
| 568 | `latent = self.history_encoder(...)` | (4096, 8) | **base 估计 φ_base(h)** |
| 573 | `full_feature = flatten(...).detach()` | (4096, 720) | 原始历史展平，截断梯度 |
| 574 | `history_encoder[:-1](...).detach()` | (4096, 128) | base 最后隐藏层特征，截断梯度 |
| 575 | `torch.cat([...], dim=-1)` | (4096, 848) | 论文的 h̃（不含 ε） |
| 579 | `.unsqueeze(0)` | (1, 4096, 848) | 在最前面加一维 |
| 579 | `.repeat((8, 1, 1))` | (8, 4096, 848) | **复制 8 份**，每份对应一个 ε 样本 |
| 581–583 | `epinet_samples = torch.randn((8, 8))` | (8, 8) | **8 个 ε，每个 8 维** |
| 584 | `.unsqueeze(1).repeat((1, 4096, 1))` | (8, 4096, 8) | 同一个 ε 复制给所有 4096 个环境 |
| 587 | `epinet_input = cat(...)` | (8, 4096, 856) | 每份特征后面接上对应的 ε |
| 590 | `trainable(epinet_input)` | (8, 4096, 64) | Linear 对最后一维运算，前两维照搬 |
| 591 | `prior(epinet_input)` | (8, 4096, 64) | 同上 |
| 592 | 相减 | (8, 4096, 64) | trainable − prior |
| 598–600 | `.reshape((8, 4096, -1, 8))` | (8, 4096, 8, 8) | 64 个数变成 **8×8 矩阵 M**（−1 表示自动算出 8） |
| 601 | `epinet_samples_repeat.unsqueeze(-2)` | (8, 4096, 1, 8) | ε 变成"一行" |
| 601 | 逐元素相乘 | (8, 4096, 8, 8) | 广播：M 的每一行都乘以 ε |
| 601 | `.sum(dim=-1)` | (8, 4096, 8) | 每行求和 = **M·ε**（矩阵乘向量） |
| 603 | `latent + coef * epinet_term_all` | (8, 4096, 8) | (4096, 8) 广播成 (8, 4096, 8)；**8 个样本的 z 估计** |
| 604 | `latent_all.mean(dim=0)` | (4096, 8) | **μ̂**：8 个样本逐维取平均 |
| 607 | `latent_all.var(dim=0)` | (4096, 8) | **σ̂²**：8 个样本逐维求方差 |
| 607 | `.sum(dim=-1)` | (4096,) | **8 维方差加成一个数**：‖σ̂‖² |
| 608 | `(… − shift).clamp(min=0)` | (4096,) | (‖σ̂‖² − β)⁺ |
| 609 | `exp(−scale × …)` | (4096,) | **α** |
| 612/614 | `alpha.unsqueeze(-1) * …` | (4096, 1) × (4096, 8) → (4096, 8) | 收缩后的 z |

**几个要点**：
1. **第 573、574 行的 `.detach()`**：epinet 的输入特征截断梯度，所以训练 epinet 时梯度**不会**回传到历史编码器。对应论文"with gradients stopped as in [8]"。
2. **第 581 行的 ε 是 8 个，全 batch 共享**：所有 4096 个环境用同一组 8 个 ε。【代码事实】这不影响"每个环境各自的方差"，只是省了随机数。
3. **第 601 行的"乘再求和"就是矩阵乘法**：对每一行 i，修正量第 i 维 = Σⱼ M[i, j] × ε[j]。
4. **第 607 行 `var` 默认用无偏估计**（除以 N−1 = 7），和论文式 (7) 的 1/(N−1) 一致。
5. **第 607 行的 `.sum(dim=-1)` 就是 GRAM"整体退回"的根源**：8 维方差加成一个数后，就分不清是哪一维不确定了。

#### (2) 手算一个小例子

为了能手算，把维度缩小：**batch=1，d=2，m=2，N=3**（原代码 d=8、m=8、N=8，道理完全一样）。

**已知**：
- base 估计 `latent` = [0.50, −0.20]；
- 3 个随机样本 ε 和对应的 M（= trainable − prior，2×2）如下（M 依赖 ε，因为 ε 也是 epinet 的输入，所以每个样本的 M 略有不同）：

| 样本 | ε | M |
|---|---|---|
| 1 | [1.0, 0.0] | [[0.10, 0.30], [−0.20, 0.05]] |
| 2 | [−0.5, 1.0] | [[0.12, 0.28], [−0.18, 0.06]] |
| 3 | [0.0, −1.0] | [[0.11, 0.31], [−0.21, 0.04]] |

**第一步：修正量 M·ε（第 601 行）**
- 样本 1：第 1 维 0.10×1.0 + 0.30×0.0 = **0.10**；第 2 维 −0.20×1.0 + 0.05×0.0 = **−0.20** → [0.10, −0.20]
- 样本 2：第 1 维 0.12×(−0.5) + 0.28×1.0 = −0.06 + 0.28 = **0.22**；第 2 维 −0.18×(−0.5) + 0.06×1.0 = 0.09 + 0.06 = **0.15** → [0.22, 0.15]
- 样本 3：第 1 维 0.11×0 + 0.31×(−1.0) = **−0.31**；第 2 维 −0.21×0 + 0.04×(−1.0) = **−0.04** → [−0.31, −0.04]

**第二步：latent_all = latent + 修正量（第 603 行，coef=1）**

| 样本 | 第 1 维 | 第 2 维 |
|---|---|---|
| 1 | 0.50+0.10 = 0.60 | −0.20−0.20 = −0.40 |
| 2 | 0.50+0.22 = 0.72 | −0.20+0.15 = −0.05 |
| 3 | 0.50−0.31 = 0.19 | −0.20−0.04 = −0.24 |

**第三步：均值 μ̂（第 604 行）**
- 第 1 维：(0.60 + 0.72 + 0.19) / 3 = 1.51 / 3 ≈ **0.503**
- 第 2 维：(−0.40 − 0.05 − 0.24) / 3 = −0.69 / 3 = **−0.230**

**第四步：逐维方差（第 607 行，除以 N−1=2）**
- 第 1 维：偏差 0.097、0.217、−0.313；平方 0.0094、0.0470、0.0982；和 0.1546；÷2 ≈ **0.0773**
- 第 2 维：偏差 −0.17、0.18、−0.01；平方 0.0289、0.0324、0.0001；和 0.0614；÷2 = **0.0307**

**第五步：求和成标量（第 607 行 `.sum(dim=-1)`）**
- ‖σ̂‖² = 0.0773 + 0.0307 = **0.108**

**第六步：α（第 608–609 行）**，假设已定标 shift = 0.05，scale = 20：
- uncertainty = max(0.108 − 0.05, 0) = 0.058
- α = exp(−20 × 0.058) = exp(−1.16) ≈ **0.314**

**第七步：输出（第 614 行，output_type="base"）**
- 收缩后 z = 0.314 × [0.50, −0.20] = **[0.157, −0.063]**
- 如果 output_type="mean"：0.314 × [0.503, −0.230] = [0.158, −0.072]

**看懂这个例子的关键**：
- 第 1 维方差（0.077）明显大于第 2 维（0.031），说明网络对第 1 维更没把握；
- 但第五步一相加，就只剩一个 0.108，然后**两维被同一个 α=0.314 一起缩小**；
- 如果第 2 维代表"摩擦"、第 1 维代表"电机"，那摩擦估计本来更可信，也被一起丢掉了 69%。**这就是我们要改的地方。**

#### (3) 第 616–618 行：不收缩时

如果没开 apply_bias（训练阶段、contextual_rl、modular），就直接返回 base 估计（"base"），或 8 个样本的均值（"mean"）。

### 10.4 encode_history_epinet：训练和统计用（第 622–662 行）

```python
# gram_actor_critic.py:622-662（与 encode_history 的差别部分）
    def encode_history_epinet(self, observations_history):
        latent = self.history_encoder(observations_history)
        if self.history_epinet:
            ...（第 625–656 行与 encode_history 的 570–601 行完全相同）
            latent_all = latent + self.history_epinet_coef_active * epinet_term_all
        else:
            latent_all = latent

        return latent_all, latent, epinet_term_all
```

- 前半部分和 `encode_history` 一字不差；
- 区别是**不算 α、不收缩**，而是把三样中间结果都返回：
  - `latent_all` (8, B, 8)：8 个样本的估计；
  - `latent` (B, 8)：base 估计；
  - `epinet_term_all` (8, B, 8)：修正量本身。
- 谁用它：
  - `gram_ppo.py` 的微调损失：让 `latent_all` 的每个样本都去回归教师的 z（论文式 8）；
  - 本文件的 `calculate_uncertainty_metric` 和 `calculate_epinet_metrics`。

**一个小隐患**【代码事实】：如果 `history_epinet=False`，变量 `epinet_term_all` 没有被定义，第 662 行 return 会报错。实际上只有 epinet 开启时才会调用这个函数，所以不会触发。

---

## 11. 不确定性相关的工具函数（第 664–741 行）

### 11.1 enforce_minimum_std：限制噪声范围（第 664–672 行）

```python
# gram_actor_critic.py:664-672
    def enforce_minimum_std(self):
        if self.use_log_std:
            self.log_std.data.clamp_(min=math.log(1e-2), max=math.log(10.0))
            if not self.robust_as_zeros:
                self.robust_log_std.data.clamp_(min=math.log(1e-2), max=math.log(10.0))
        else:
            ...
```

每次优化器更新后调用，把噪声 σ 限制在 [0.01, 10]：
- 下限 0.01：防止探索完全消失、log_prob 数值爆炸；
- 上限 10：防止动作完全随机。
- `.data.clamp_()`：直接原地修改参数值，不经过梯度。

### 11.2 calculate_uncertainty_metric：算 ‖σ̂‖²（第 674–682 行）

```python
# gram_actor_critic.py:674-682
    def calculate_uncertainty_metric(self, obs_history):
        if self.history_epinet:
            latent_all, _, _ = self.encode_history_epinet(obs_history)
            metric = latent_all.var(dim=0).sum(dim=-1)

        else:
            metric = torch.zeros((obs_history.shape[0]), dtype=torch.float32, device=obs_history.device)

        return metric
```

- 返回每个环境的总方差 ‖σ̂‖²，形状 (B,)。
- 用途：
  1. 收集验证集时记录它，算分位数（runner 的 `collect_validation_data`）；
  2. 评估时传给 `act_inference`，供 Modular 的硬阈值使用；
  3. 训练日志里记录平均不确定性（`gram_ppo.py:356`）。
- **注意**：它和 `encode_history` 是**分开调用**的，各自重新采样 ε。所以同一时刻，评估用的不确定性和 α 里用的不确定性**数值不完全相同**（随机采样不同），但统计上一致。【代码事实】

### 11.3 calculate_epinet_metrics：评估统计（第 684–700 行）

```python
# gram_actor_critic.py:684-700
    def calculate_epinet_metrics(self, obs_history):
        if self.history_epinet:
            latent_all, latent_base, _ = self.encode_history_epinet(obs_history)
            latent_mean = latent_all.mean(dim=0)

            latent_base_l2 = latent_base.pow(2).sum(dim=-1)
            latent_mean_l2 = latent_mean.pow(2).sum(dim=-1)
            latent_std_l2 = latent_all.var(dim=0).sum(dim=-1)

            latent_std_l2 = latent_all.var(dim=0).sum(dim=-1)
            uncertainty = (latent_std_l2 - self.history_epinet_shift_param).clamp(min=0)
            alpha = torch.exp(self.history_epinet_scale_param * uncertainty * -1)
        ...
        return latent_base_l2, latent_mean_l2, latent_std_l2, alpha
```

返回四个量，用于评估时打印和画图：

| 返回值 | 含义 | 用途 |
|---|---|---|
| `latent_base_l2` | ‖base 估计‖² | 看 z 离原点多远 |
| `latent_mean_l2` | ‖μ̂‖² | 同上，用均值 |
| `latent_std_l2` | ‖σ̂‖²（总方差） | 不确定性 |
| `alpha` | α | **论文 Fig. 4 的 α 就来自这里** |

- 第 691 行和第 693 行一模一样，重复计算了一次，无害。【代码事实】
- 服务器冒烟测试评估日志里打印的 "Uncertainty Metric" 分位数和 α 分位数，就是这里算出来的。

### 11.4 store_validation：保存验证集分位数（第 702–704 行）

```python
# gram_actor_critic.py:702-704
    def store_validation(self, validation_quantiles_value):
        self.validation_quantiles_value.data = validation_quantiles_value
        self.validation_quantiles_saved.data = torch.tensor(True, device=self.validation_quantiles_saved.device)
```

- 训练结束后，runner 在 ID 环境里跑一段，收集所有 ‖σ̂‖²，算出 101 个分位数，调用这里存进模型（`gram_on_policy_runner.py:606`）。
- 同时把 `saved` 标记为 True。之后保存 checkpoint，分位数就跟着模型走了。

### 11.5 set_uncertainty_params：算 β 和 λ（第 706–730 行）

**这段要干什么**：用验证集分位数自动定出 shift（β）和 scale（λ）。

```python
# gram_actor_critic.py:706-730
    def set_uncertainty_params(self):
        # shift / scale parameters for GRAM alpha calculation
        if self.history_epinet_finetune_shift and self.validation_quantiles_saved:
            self.history_epinet_shift_param = self.validation_quantiles_value.quantile(
                q=self.history_epinet_finetune_min_quantile
            )
        else:
            self.history_epinet_shift_param = torch.tensor(0.0, device=self.validation_quantiles_value.device)

        if self.history_epinet_finetune_scale and self.validation_quantiles_saved:
            latent_std_l2_quantile = self.validation_quantiles_value.quantile(
                q=self.history_epinet_finetune_max_quantile
            )
            self.history_epinet_scale_param = (
                math.log(self.history_epinet_finetune_target)
                * -1
                / (latent_std_l2_quantile - self.history_epinet_shift_param)
            )
        else:
            self.history_epinet_scale_param = torch.tensor(1.0, device=self.validation_quantiles_value.device)

        # Threshold for GRAM modular ablation
        self.uncertainty_max_threshold = self.validation_quantiles_value.quantile(
            q=self.history_epinet_finetune_max_quantile
        )
```

**逐行解释**：
- 第 708–711 行：**shift = 验证集的 0.90 分位数**。注意这里是"对 101 个分位数值再求 0.90 分位"，因为 101 个点是 0%、1%、…、100% 均匀排列的，所以结果就是原始数据的 0.90 分位数（再做一次线性插值）。
- 第 712–713 行：还没有验证集时，shift = 0。
- 第 715–723 行：**scale = −ln(target) / (q99 − shift)**，target=0.01。
- 第 724–725 行：还没有验证集时，scale = 1。
- 第 728–730 行：**Modular 消融的硬阈值 = 0.99 分位数**。

**推导**（为什么 scale 这样算）：要求不确定性等于 q99 时 α = target：

exp(−scale × (q99 − q90)) = 0.01
⇒ scale × (q99 − q90) = −ln 0.01 = 4.605
⇒ scale = 4.605 / (q99 − q90)

**数值例子**：假设验证集算出 q90 = 2.0，q99 = 6.0。
- shift = **2.0**
- scale = 4.605 / (6.0 − 2.0) = **1.151**
- Modular 阈值 = **6.0**

再看不同不确定性下的 α：

| 不确定性 ‖σ̂‖² | uncertainty = (‖σ̂‖² − 2)⁺ | α = exp(−1.151 × uncertainty) | Modular 掩码（>6 才切） | 含义 |
|---|---|---|---|---|
| 1.0 | 0 | exp(0) = **1.000** | 0 | 很有把握，完全相信估计 |
| 3.0 | 1.0 | exp(−1.151) ≈ **0.316** | 0 | 有点陌生，z 缩到原来的 1/3 |
| 6.0 | 4.0 | exp(−4.605) = **0.010** | 0（等于阈值，不大于） | 训练分布里最极端的 1%，几乎完全退回 |
| 10.0 | 8.0 | exp(−9.21) ≈ **0.0001** | 1 | 完全陌生，等于 z_rob = 0 |

**这个表说明了 GRAM 和 Modular 的本质区别**：GRAM 的 α 从 1 平滑下降；Modular 在 6.0 处从"完全适应"突然跳到"完全鲁棒"。

**什么时候被调用？**【代码事实】
1. 构造函数里（第 160 行）：此时没有验证集，shift=0、scale=1；
2. runner 加载 checkpoint 时（`gram_on_policy_runner.py:147`）：此时分位数已随模型加载，算出正确的 shift、scale。

所以**评估流程是"加载模型 → 自动重算 shift/scale"**。【推断】训练结束后在同一个进程里，`store_validation` 只存不算，要等重新加载时才会更新参数。官方流程是训练和评估分两次运行，所以没问题。

### 11.6 get_uncertainty_params（第 732–733 行）

```python
    def get_uncertainty_params(self):
        return self.history_epinet_shift_param, self.history_epinet_scale_param, self.uncertainty_max_threshold
```

把三个参数一起返回，供日志打印。

### 11.7 calculate_uncertainty_mask：Modular 的硬阈值（第 735–741 行）

```python
# gram_actor_critic.py:735-741
    def calculate_uncertainty_mask(self, uncertainty_metric):
        uncertainty_mask_bool = uncertainty_metric > self.uncertainty_max_threshold
        uncertainty_mask_bool[torch.isnan(uncertainty_metric)] = False

        uncertainty_mask = uncertainty_mask_bool.to(dtype=torch.float32).unsqueeze(dim=-1)

        return uncertainty_mask
```

- 不确定性 > q99 → 掩码 1（用鲁棒策略），否则 0；
- NaN（例如没开 epinet 时算出的异常值）一律当 0 处理；
- 转成 float 并变成 (B, 1)，可以直接传给 `update_distribution`。
- 对 GRAM 主算法来说，这个掩码会在 `act_inference` 里被 `act_inference_adapt=True` **覆盖成全 0**，所以没有实际作用。

---

## 12. 论文与代码的对应和差异

| 论文 | 代码 | 关系 |
|---|---|---|
| 式 (5) φ(h, ε) = φ_base(h) + φ_epi(h̃, ε) | `latent_all = latent + coef × epinet_term_all`（第 603 行） | 一致；φ_epi 具体为 (trainable − prior)·ε |
| h̃ = h 拼接 base 最后隐藏层，梯度截断 | `input_type="concat"` + 两处 `.detach()`（第 573–575 行） | 一致 |
| 式 (6) μ̂ = 样本均值 | `latent_all.mean(dim=0)`（第 604 行） | 一致 |
| 式 (7) σ̂² 逐维、除以 N−1 | `latent_all.var(dim=0)`（第 607 行），默认无偏 | 一致 |
| ‖σ̂‖² 为各维方差之和 | `.sum(dim=-1)` | 一致 |
| 式 (9) 输出 (1−α)z_rob + α**μ̂** | 默认 `output_type="base"`：输出 α × **base 估计** | **不完全一致**：乘的是 base 估计而不是 μ̂ |
| z_rob = 0 | (1−α)×0 + α×z = α×z，所以代码直接写 `alpha * latent` | **数学上等价** |
| α = exp(−λ(‖σ̂‖² − β)⁺) | 第 608–609 行 | 一致；λ=`scale_param`，β=`shift_param` |
| β = 0.90 分位数，λ 使 0.99 分位数处 α=0.01 | `set_uncertainty_params` | 一致 |
| "鲁棒模式是隐空间的一个点" | `robust_as_zeros=True`：`robust_actor` 就是 `actor`，输入全 0 | 一致 |
| φ_GRAM 只在部署时用 | 训练时 `act_from_context=True`，不经过 `encode_history`；评估时才开 `apply_bias` | 一致 |

**关于 base 和 μ̂ 的差异，怎么理解**：训练后，在见过的输入上修正量很小，base ≈ μ̂；在没见过的输入上两者可能有差别，但此时 α 已经很小，乘出来都接近 0。所以实际影响不大。复现时如果想严格按论文，可以加 `--history_epinet_output_type mean`。【推断】

---

## 13. 改成"分组不确定性 / 分组 α"要改哪里

目标：把 8 维 z 拆成若干组（例如 G=2 组：环境组 4 维 = 摩擦 + 负载；执行器组 4 维 = 电机强度 + 关节零偏），每组单独算不确定性和 α_g，只缩小不可信的那一组。

### 13.1 需要改的位置

| # | 位置 | 现在 | 要改成 |
|---|---|---|---|
| 1 | 构造函数第 128–138 行：`context_encoder` | 26 → 64 → 64 → 8，一个整体 | **分块编码器**：每组上下文单独一个小 MLP，例如 [摩擦, 质量] (2 维) → 4 维，[电机 12, 零偏 12] (24 维) → 4 维，再拼接。这样 z 的前 4 维只来自环境、后 4 维只来自执行器 |
| 2 | 第 157–160 行：验证分位数 | (101,) 一组 | (G, 101)，每组一套 |
| 3 | 第 607 行（`encode_history`）、第 677 行、第 693 行 | `var(dim=0).sum(dim=-1)` → (B,) | 按组切片后分别求和 → (B, G) |
| 4 | 第 608–609 行 | 标量 shift、scale | 每组一个 shift_g、scale_g → α 形状 (B, G) |
| 5 | 第 612/614 行 | `alpha.unsqueeze(-1) * latent` | 把 α (B, G) 按组展开成 (B, 8)（每组 4 维复制同一个 α_g），再逐元素相乘 |
| 6 | 第 706–730 行 `set_uncertainty_params` | 标量 | 对每组分别算 |
| 7 | 第 449–472 行 `update_distribution` 与第 522–546 行 `evaluate` | `robust_masks` (B, 1)，鲁棒分支整个 z 置 0 | `robust_masks` (B, G)：**只把被标记的组置 0**，其他组保留真实 z。这是"训练时练习部分可信"的关键 |
| 8 | 第 735–741 行 | 标量硬阈值 | 分组硬阈值（作为分组版 Modular 消融） |
| 9 | 第 684–700 行 | 返回一个 α | 返回每组 α_g，用于画"哪一组触发了退回"的图 |

另外需要改 `gram_ppo.py`（历史损失按组加权）和 runner（掩码按组抽样、验证集按组统计）、环境（不可信组的参数推出训练范围），这些在其他分篇讲。

### 13.2 改后的伪代码

```python
# 分组定义（例子）：组 0 = z[0:4]（环境），组 1 = z[4:8]（执行器）
GROUPS = [slice(0, 4), slice(4, 8)]

def encode_context_grouped(context):
    z_env = env_encoder(context[:, ENV_IDX])        # (B, 4)，只看摩擦、质量
    z_act = act_encoder(context[:, ACT_IDX])        # (B, 4)，只看电机强度、零偏
    return torch.cat([z_env, z_act], dim=-1)        # (B, 8)

def encode_history_grouped(obs_history):
    latent = history_encoder(obs_history)                       # (B, 8)
    latent_all = latent + epinet_term(obs_history)              # (N, B, 8)，与原来相同
    var = latent_all.var(dim=0)                                 # (B, 8)
    unc = torch.stack([var[:, g].sum(-1) for g in GROUPS], -1)  # (B, G)  ← 原来是 (B,)
    u = (unc - shift_g).clamp(min=0)                            # shift_g: (G,)
    alpha_g = torch.exp(-scale_g * u)                           # (B, G)
    alpha_full = torch.cat([alpha_g[:, i:i+1].expand(-1, 4)     # (B, 8)：每组 4 维共用一个 α_g
                            for i in range(len(GROUPS))], -1)
    return alpha_full * latent                                  # 只缩小不可信组

def update_distribution_grouped(obs, latent, robust_masks_g):   # robust_masks_g: (B, G)
    keep = 1 - expand_to_latent(robust_masks_g)                 # (B, 8)，被标记的组为 0
    z_partial = keep * latent                                   # 只把不可信组置 0
    mean = actor(torch.cat([obs, z_partial], -1))
    ...
```

**和原版的对比**：原版 `robust_masks` 只有"全置 0"和"全不置 0"两种情况；改后有 2^G 种组合（G=2 时 4 种：都可信、只环境不可信、只执行器不可信、都不可信），训练时随机抽，策略才能学会"部分可信时怎么走"。

**风险提醒**：
1. epinet 只有一个输出头，各组的方差是否真能区分不同来源的变化，需要实验验证（先做"直接告诉策略哪组不可信"的上限实验）；
2. 分块编码器限制了 z 的表达能力，可能让 ID 性能略降，要和原版比较。

---

## 14. 读这个文件的顺序建议

1. 先看第 449 行 `update_distribution`，理解"一个网络、掩码选择两种模式"；
2. 再看第 273 行 `robust_as_zeros`，理解为什么鲁棒分支就是同一个网络；
3. 再看第 567 行 `encode_history`，对照第 10.3 节的形状表和手算例子；
4. 再看第 706 行 `set_uncertainty_params`，对照数值例子；
5. 最后回头看构造函数，搞清楚每个网络的结构和初始化。

---

## 自测题

1. GRAM 训练收集数据时，策略用的 z 来自哪个网络？部署时呢？分别由哪个开关控制？
2. 为什么各网络最后一层的初始化 gain 设为 1e-4？这和论文"z 从 z_rob=0 附近开始训练"有什么关系？
3. `self.robust_actor = self.actor` 这一行意味着什么？checkpoint 里为什么还会出现 `robust_actor.*`？
4. epinet 为什么要有一个冻结的 prior 网络？如果 prior 也能训练，会发生什么？
5. mlp_dot 类型中，64 维输出是怎么变成 8 维修正量的？写出公式。
6. 在 `encode_history` 里，哪一行把"哪一维不确定"的信息丢掉了？
7. 假设 q90 = 1.0，q99 = 3.0，不确定性为 2.0 时 α 是多少？Modular 掩码是多少？
8. 默认 `output_type="base"` 和论文式 (9) 有什么不同？实际影响大吗？
9. 部署时 GRAM 的 `robust_masks` 是什么？GRAM 是怎样"变保守"的？
10. 要实现"分组退回"，最先要改的是哪个网络？为什么？

<details>
<summary>参考答案</summary>

1. 训练时来自 `context_encoder`（真实上下文，`act_from_context=True`）；部署时来自 `history_encoder` 加 α 收缩（`act_from_context=False`、`history_epinet_apply_bias=True`）。
2. 让各网络初始输出几乎为 0：动作 ≈ 默认姿态，机器人不会乱动；上下文编码器输出 z ≈ 0，正好在鲁棒点附近。训练中 z 只在需要适应时才离开 0。
3. 鲁棒策略和适应策略是同一个网络，鲁棒模式就是输入 z=0。PyTorch 保存 state_dict 时，同一组参数会以两个名字各存一份，不代表有两套网络。
4. 先验给每个输入预先"埋下"随 ε 变化的输出，可训练部分只在见过的输入上把它抵消，所以没见过的输入方差大。如果先验也能训练，两个网络可以一起变成 0，所有输入方差都为 0，不确定性失效。
5. 64 维重排成 8×8 矩阵 M（trainable − prior），修正量 = M·ε，第 i 维 = Σⱼ M[i, j]·ε[j]。
6. 第 607 行 `latent_all.var(dim=0).sum(dim=-1)` 中的 `.sum(dim=-1)`，把 8 维方差加成一个标量。
7. scale = 4.605 / (3.0 − 1.0) = 2.303；uncertainty = 2.0 − 1.0 = 1.0；α = exp(−2.303) ≈ 0.10。Modular 阈值是 3.0，2.0 不大于 3.0，掩码为 0。
8. 论文乘的是 8 个样本的均值 μ̂，代码默认乘 base 估计。见过的输入上两者接近；没见过的输入上 α 已经很小，所以影响不大。可用 `--history_epinet_output_type mean` 对齐论文。
9. 全 0（`act_inference_adapt=True` 覆盖）。GRAM 永远走适应分支，通过 α 把 z 往 0 收缩来变保守，而不是切换网络。
10. 上下文编码器。现在它把 26 维混在一起压成 8 维，z 的每一维没有物理含义，无法按组切分；要先改成分块编码器，让每组 z 只来自对应的物理量。
</details>
