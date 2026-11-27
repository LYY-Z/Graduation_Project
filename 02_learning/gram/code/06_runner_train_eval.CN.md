# 代码精读 06：`gram_on_policy_runner.py` 逐行讲解：训练主循环、验证集与评估

> 读者：零基础本科生。上一篇（[05 PPO 与存储](05_ppo_and_storage.CN.md)）讲了"每次迭代内部怎么学"，这一篇讲"**谁在指挥**"：一共跑多少次迭代、每次迭代怎么采样、什么时候切到 finetune、训练完怎么定标 α、评估时怎么统计。
>
> 文件：`source/algs/gram/gram_on_policy_runner.py`（776 行）。
>
> 标注：**【代码事实】** 直接读代码可确认；**【推断】** 依赖 rsl_rl 2.0 父类或 Isaac Lab，需对照服务器上 `upstream/rsl_rl`、`work/IsaacLab` 的源码确认。

---

## 目录

1. [先看全貌：runner 是什么](#1-先看全貌runner-是什么)
2. [`__init__`：构造（第 32–132 行）](#2-__init__构造第-32132-行)
3. [`load` / `save`（第 134–178 行）](#3-load--save第-134178-行)
4. [`train_mode` / `eval_mode`（第 180–190 行）](#4-train_mode--eval_mode第-180190-行)
5. [三个小工具：观测历史与掩码（第 192–219 行）](#5-三个小工具观测历史与掩码第-192219-行)
6. [`learn`：训练主循环（第 221–380 行）](#6-learn训练主循环第-221380-行)
7. [`log`：日志里每个数的含义（第 382–469 行）](#7-log日志里每个数的含义第-382469-行)
8. [`collect_validation_data`：定标 α 的验证集（第 497–616 行）](#8-collect_validation_data定标-α-的验证集第-497616-行)
9. [`evaluate`：评估（第 618–776 行）](#9-evaluate评估第-618776-行)
10. [一次完整训练的时间线](#10-一次完整训练的时间线)
11. [六种算法在 runner 里走哪些分支](#11-六种算法在-runner-里走哪些分支)
12. [读完 runner 后对改代码的提示](#12-读完-runner-后对改代码的提示)
13. [自测题](#13-自测题)

---

## 1. 先看全貌：runner 是什么

**runner（运行器）**：训练的"总指挥"。它不负责具体的数学（那是 `GRAMPPO` 和 `GRAMActorCritic` 的事），只负责安排流程。

GRAM 的 runner 被三个入口调用：

| 入口 | 调用 | 作用 |
|---|---|---|
| `python -m source.train` | `runner.learn(...)`（`train.py:111`） | 训练：10,000 次 RL + 5,000 次 finetune + 收集验证集 |
| `python -m source.train --calculate_validation_metrics_only` | `runner.calculate_and_save_validation_metrics()`（`train.py:109`） | 只对已有模型重新收集验证集、重新定标 |
| `python -m source.eval` | `runner.evaluate(...)`（`eval.py:115`） | 加载模型，在指定场景下跑一个回合，统计回报和 α |

runner 继承自 rsl_rl 2.0 的 `OnPolicyRunner`，但**几乎所有方法都重写了**，所以读这一个文件就能看懂流程。

**名词**：
- **迭代（iteration）**：采样 24 步 + 学习一次。
- **回合（episode）**：一只机器狗从出生到摔倒或超时（最长 1000 步 = 20 秒）。
- 一个回合会跨越约 42 次迭代（1000 ÷ 24）。迭代和回合是两套独立的计时：迭代结束时，环境**不会**被重置，机器狗继续走。

---

## 2. `__init__`：构造（第 32–132 行）

**这段要干什么**：把网络、算法、缓冲区、对抗者都搭起来，并读入各种开关。

### 2.1 读配置、建网络（第 32–56 行）

```python
# gram_on_policy_runner.py:32-56
    def __init__(self, env: VecEnv, train_cfg, log_dir=None, device="cpu"):
        self.cfg = train_cfg
        self.alg_cfg = train_cfg["algorithm"]
        self.policy_cfg = train_cfg["policy"]
        self.device = device
        self.env = env

        # context
        context = self.env.get_context()
        num_context = context.shape[1]

        obs, extras = self.env.get_observations()
        num_obs = obs.shape[1]
        if "critic" in extras["observations"]:
            num_critic_obs = extras["observations"]["critic"].shape[1]
        else:
            num_critic_obs = num_obs
        num_adversary_actions = 1
        self.obs_history_length = self.policy_cfg["obs_history_length"]
        actor_critic_class = eval(self.policy_cfg.pop("class_name"))  # GRAMActorCritic
        actor_critic: GRAMActorCritic = actor_critic_class(
            num_obs, num_critic_obs, self.env.num_actions, num_context, **self.policy_cfg
        ).to(self.device)
        alg_class = eval(self.alg_cfg.pop("class_name"))  # GRAMPPO
        self.alg: GRAMPPO = alg_class(actor_critic, device=self.device, **self.alg_cfg)
```

**逐行解释**：
- `train_cfg`：一个大字典，由 `cli_utils.py` 的 `parse_agent_cfg` 生成，里面有 `algorithm`（PPO 参数）和 `policy`（网络参数）两个子字典，以及大量 GRAM 自己的开关。
- 第 40 行：`env.get_context()`：GRAM 的环境包装器（`context_env_wrapper.py`）提供的方法，返回 [4096, 26] 的真实上下文。
- 第 41 行：`num_context = 26`。
- 第 43–48 行：拿一次观测，确定维度。Go2 任务里没有单独的 `critic` 观测组【推断】，所以 critic 和 actor 看一样的观测。
- 第 49 行：对抗者输出 1 维（一个角度）。
- 第 51 行：`eval("GRAMActorCritic")`：`eval` 把字符串当代码执行，得到类本身。`pop` 把 `class_name` 从字典里拿掉，免得它被当成网络参数传进去。
- 第 52–54 行：建 actor-critic 网络，放到 GPU。`**self.policy_cfg` 把字典展开成关键字参数（例如 `num_latent=8, obs_history_length=16, ...`）。
- 第 55–56 行：建 `GRAMPPO` 算法对象。父类 `PPO.__init__` 会读 `clip_param`、`gamma` 等【推断】。

### 2.2 步数、保存间隔、观测标准化（第 57–65 行）

```python
# gram_on_policy_runner.py:57-65
        self.num_steps_per_env = self.cfg["num_steps_per_env"]
        self.save_interval = self.cfg["save_interval"]
        self.empirical_normalization = self.cfg["empirical_normalization"]
        if self.empirical_normalization:
            self.obs_normalizer = EmpiricalNormalization(shape=[num_obs], until=None).to(self.device)
            self.critic_obs_normalizer = EmpiricalNormalization(shape=[num_critic_obs], until=None).to(self.device)
        else:
            self.obs_normalizer = torch.nn.Identity()  # no normalization
            self.critic_obs_normalizer = torch.nn.Identity()  # no normalization
```

**逐行解释**：
- `num_steps_per_env`：每次迭代每个环境走几步，默认 24【推断，继承 Isaac Lab Go2 配置】。
- `save_interval`：每多少次迭代存一次模型，GRAM 设为 5000（`unitree_go2_custom_env.py:88`）。
- **观测标准化（empirical normalization）**：GRAM 默认**开启**（`cli_utils.py:696`）。
  - 作用：观测各维度的尺度差别很大（关节速度可能到 ±20 rad/s，投影重力在 ±1 之间）。标准化器会**一边训练一边统计**每一维的均值和标准差，然后输出 (x − 均值) / 标准差，让网络输入都在 0 附近、尺度约 1。
  - `until=None`：一直统计，不停止【推断】。
  - 关闭时用 `Identity()`，原样输出。
- **注意**：标准化后的观测才是网络真正看到的，**观测历史里存的也是标准化后的观测**。部署到实机时，必须用训练时保存的均值和标准差。

### 2.3 GRAM 自己的开关（第 67–85 行）

```python
# gram_on_policy_runner.py:67-85
        self.robust_mask_update_every = self.cfg["robust_mask_update_every"]
        self.robust_mask_reset_update = self.cfg["robust_mask_reset_update"]

        self.collect_data_from_context = self.cfg["collect_data_from_context"]
        self.collect_data_deterministic = self.cfg["collect_data_deterministic"]
        self.collect_data_mix = self.cfg["collect_data_mix"]
        self.uncertainty_metric_full_only = self.cfg["uncertainty_metric_full_only"]
        self.uncertainty_metric_adapt_only = self.cfg["uncertainty_metric_adapt_only"]

        self.robust_train_only = self.cfg["robust_train_only"]
        self.adapt_train_only = self.cfg["adapt_train_only"]

        self.finetune_iterations = self.cfg["finetune_iterations"]
        self.finetune_fresh_start = self.cfg["finetune_fresh_start"]
        self.finetune_w_adversary = self.cfg["finetune_w_adversary"]

        self.print_stats = self.cfg["print_stats"]
        self.save_eval_detailed = self.cfg["save_eval_detailed"]
```

**每个开关的含义和 GRAM 默认值**：

| 开关 | GRAM 默认 | 含义 | 在哪里用 |
|---|---|---|---|
| `robust_mask_update_every` | 1 | 每几次迭代翻转一次鲁棒/自适应分配 | `learn` 第 304 行 |
| `robust_mask_reset_update` | False | True 时改成"回合重置时才翻转"（Separate、Modular 消融用） | `learn` 第 304、312 行 |
| `collect_data_from_context` | False | 验证集采样时 latent 用 f(c)（True）还是历史编码器（False） | 第 512 行 |
| `collect_data_deterministic` | True | 验证集采样用分布均值（不加噪声） | 第 559 行 |
| `collect_data_mix` | True | 验证集也用一半一半、每 24 步交替的分配 | 第 543、554 行 |
| `uncertainty_metric_full_only` | False | 只用"活到超时"的完整轨迹算分位数 | 第 598 行 |
| `uncertainty_metric_adapt_only` | False | 只用第一轮（robust_mask_value=0）的数据算分位数 | 第 589 行 |
| `robust_train_only` | False | 所有环境都做鲁棒训练（鲁棒 RL、域随机化用） | 第 202、214 行 |
| `adapt_train_only` | False | 所有环境都做自适应训练（情境 RL 用） | 第 204、216 行 |
| `finetune_iterations` | 5000 | finetune 迭代数 | 第 276 行 |
| `finetune_fresh_start` | False | 加载模型时丢掉已有的历史编码器，从头训练 | 第 137 行 |
| `finetune_w_adversary` | False | finetune 时是否保留对抗者 | 第 290 行 |
| `print_stats` | False | 评估/验证时打印详细统计 | 第 608、709 行 |
| `save_eval_detailed` | False | 评估时保存逐步的 α、方差等 | 第 691 行 |

开关的设置位置：`cli_utils.py:546-620`（按算法）和 `cli_utils.py:640-760`（按命令行）。

### 2.4 建缓冲区、对抗者（第 87–112 行）

```python
# gram_on_policy_runner.py:87-112
        self.alg.init_storage(
            self.env.num_envs, self.num_steps_per_env, self.obs_history_length,
            [num_obs], [num_critic_obs], [self.env.num_actions], [num_adversary_actions],
        )

        adversary_policy = GRAMAdversary(num_obs, num_adversary_actions, **self.policy_cfg).to(self.device)
        self.alg.init_extras(
            context, adversary_policy, env,
            self.cfg["train_and_finetune"], self.cfg["num_learning_epochs_finetune"],
            self.cfg["history_loss_actions"], self.cfg["history_loss_robust_as_zeros"],
            self.cfg["history_loss_adapt_only"], self.cfg["history_loss_epinet_separate"],
            self.cfg["history_lr"], self.cfg["adversary_update_every"],
        )
```

（原文第 88–112 行逐个参数换行，此处合并显示。）

**解释**：
- 第 88–96 行：建缓冲区，详见 05 篇第二部分。
- 第 99 行：建对抗者。它和 actor-critic 共用 `policy_cfg`，从中取 `adversary_hidden_dims`、`adversary_prob`、`adversary_clamp` 等，用不到的参数被 `**kwargs` 吸收。
- 第 100–112 行：把上下文、对抗者、环境和各开关交给 PPO 算法，创建三个优化器（05 篇 3.1 节）。

### 2.5 日志与保存用的配置（第 114–132 行）

```python
# gram_on_policy_runner.py:114-132
        self.log_dir = log_dir
        self.writer = None
        self.tot_timesteps = 0
        self.tot_time = 0
        self.current_learning_iteration = 0
        self.git_status_repos = list()

        self.actor_critic_cfg = copy.deepcopy(self.policy_cfg)
        self.actor_critic_cfg["num_actor_obs"] = num_obs
        self.actor_critic_cfg["num_critic_obs"] = num_critic_obs
        self.actor_critic_cfg["num_actions"] = self.env.num_actions
        self.actor_critic_cfg["num_context"] = num_context

        self.hardware_cfg = dict()
        self.hardware_cfg["joint_pos_clamp"] = self.cfg["joint_pos_clamp"]
        self.hardware_cfg["hip_scale_mult"] = self.cfg["hip_scale_mult"]
```

**解释**：
- `writer`：日志写入器（TensorBoard 等），在 `learn()` 开始时才创建。
- `actor_critic_cfg`：把网络结构参数完整地复制一份，**连同输入输出维度**一起存进模型文件。这样以后在别的程序（例如实机部署）里，不需要再跑环境就能把网络原样重建出来。
- `hardware_cfg`：实机部署需要的两个动作处理参数：
  - `joint_pos_clamp`：目标关节角是否限制在关节限位内；
  - `hip_scale_mult`：髋关节动作缩放倍数（0.5）。
  这说明作者的实机部署代码会读这两个参数，复现动作处理链时要一致。

---

## 3. `load` / `save`（第 134–178 行）

### 3.1 `save`：模型文件里存了什么（第 159–178 行）

```python
# gram_on_policy_runner.py:159-174
    def save(self, path, infos=None):
        saved_dict = {
            "model_state_dict": self.alg.actor_critic.state_dict(),
            "optimizer_state_dict": self.alg.optimizer.state_dict(),
            "iter": self.current_learning_iteration,
            "infos": infos,
            "alg_name": self.cfg["alg_name"],
            "hardware_cfg": self.hardware_cfg,
            "actor_critic_cfg": self.actor_critic_cfg,
            "empirical_normalization": self.empirical_normalization,
        }
        if self.empirical_normalization:
            saved_dict["obs_norm_state_dict"] = self.obs_normalizer.state_dict()
            saved_dict["critic_obs_norm_state_dict"] = self.critic_obs_normalizer.state_dict()

        torch.save(saved_dict, path)
```

**`model_N.pt` 文件内容一览**：

| 键 | 内容 | 用途 |
|---|---|---|
| `model_state_dict` | actor、critic、上下文编码器、历史编码器、epinet（可训练 + 先验）、std，**以及验证集的 101 个分位数** | 网络参数 |
| `optimizer_state_dict` | 主 PPO 优化器（Adam）的状态 | 继续训练用 |
| `iter` | 当前迭代号 | |
| `infos` | 附加信息（GRAM 里一般为 None） | |
| `alg_name` | 例如 `"gram"` | |
| `hardware_cfg` | `joint_pos_clamp`、`hip_scale_mult` | 实机部署 |
| `actor_critic_cfg` | 网络结构 + 维度 | 重建网络 |
| `empirical_normalization` | True | |
| `obs_norm_state_dict` | 观测标准化的均值、方差、计数【推断】 | **部署必需** |
| `critic_obs_norm_state_dict` | 同上，critic 用 | |

**关键点**：验证集分位数是 actor-critic 的 `nn.Parameter`（`requires_grad=False`，见 `gram_actor_critic.py:157-159`），所以**跟着 `model_state_dict` 一起存**。加载模型后就能直接算出 α 的 β 和 λ，不用重新收集验证集。

**注意**：对抗者网络和历史编码器的优化器**没有保存**。从 checkpoint 继续训练时，对抗者会从头开始。

服务器冒烟测试保存的 `model_2.pt`：7.0 MB、134 万个参数，56 个张量在训练后发生了变化，其中包括 `validation_quantiles_value` 和 `validation_quantiles_saved`。这说明验证集确实被写进了模型。

### 3.2 `load`（第 134–157 行）

```python
# gram_on_policy_runner.py:134-157
    def load(self, path, load_optimizer=True):
        loaded_dict = torch.load(path)

        if self.finetune_fresh_start:
            pop_keys = []
            for key in loaded_dict["model_state_dict"].keys():
                if key.startswith("history_encoder") or key.startswith("history_epinet"):
                    pop_keys.append(key)

            for key in pop_keys:
                loaded_dict["model_state_dict"].pop(key)

        self.alg.actor_critic.load_state_dict(loaded_dict["model_state_dict"], strict=False)
        self.alg.actor_critic.set_uncertainty_params()

        if self.empirical_normalization:
            self.obs_normalizer.load_state_dict(loaded_dict["obs_norm_state_dict"])
            self.critic_obs_normalizer.load_state_dict(loaded_dict["critic_obs_norm_state_dict"])
            self.obs_normalizer.eval()
            self.critic_obs_normalizer.eval()
        if load_optimizer:
            self.alg.optimizer.load_state_dict(loaded_dict["optimizer_state_dict"])
        self.current_learning_iteration = loaded_dict["iter"]
        return loaded_dict["infos"]
```

**逐行解释**：
- 第 137–144 行：`finetune_fresh_start` 时，把历史编码器和 epinet 的参数从字典里删掉，这样它们保持随机初始化。用途：拿一个训练好的策略，**重新做一遍 finetune**（例如换一种历史损失做实验），不用重训 RL。
- 第 146 行：`strict=False`：允许字典里缺键（被删掉的那些）或多键。
- 第 147 行：**`set_uncertainty_params()`**：根据刚加载的分位数，重新算 β（shift）和 λ（scale）。这一行很重要：网络构造时分位数还是全 0，算出来的 β、λ 没有意义；加载后必须重算（见 `gram_actor_critic.py:706-730`）。
- 第 149–153 行：恢复标准化器的统计量，并设为 eval 模式（**冻结**，不再更新均值方差）。
- 第 154–155 行：恢复优化器（评估时 `eval.py` 一般不需要）。
- 第 156 行：恢复迭代号，继续训练时从这里接着数。

---

## 4. `train_mode` / `eval_mode`（第 180–190 行）

```python
# gram_on_policy_runner.py:180-190
    def train_mode(self):
        self.alg.actor_critic.train()
        if self.empirical_normalization:
            self.obs_normalizer.train()
            self.critic_obs_normalizer.train()

    def eval_mode(self):
        self.alg.actor_critic.eval()
        if self.empirical_normalization:
            self.obs_normalizer.eval()
            self.critic_obs_normalizer.eval()
```

**解释**：PyTorch 的 `.train()` / `.eval()` 切换模式。GRAM 网络里没有 Dropout、BatchNorm 这类会受模式影响的层，所以对网络本身没影响；**真正有影响的是标准化器**：train 模式下每次调用都会更新均值和方差，eval 模式下冻结【推断】。

---

## 5. 三个小工具：观测历史与掩码（第 192–219 行）

### 5.1 `_update_observation_history`：滚动更新历史（第 192–196 行）

```python
# gram_on_policy_runner.py:192-196
    def _update_observation_history(self, obs_history, obs, reset_env_ids):
        if len(reset_env_ids) > 0:
            obs_history[reset_env_ids] = 0.0

        return torch.cat((obs_history[:, 1:], obs.unsqueeze(dim=1)), dim=1)
```

**这段要干什么**：维护一个"最近 16 帧观测"的窗口，每走一步，窗口往前滑一格。

**逐行解释**：
- `obs_history`：形状 [4096, 16, 45]。第 1 维是时间，**下标 0 最旧，下标 15 最新**。
- 第 193–194 行：刚重置（摔倒或超时后重新开始）的环境，把历史**全部清零**。旧回合的历史不能带进新回合。
- 第 196 行：
  - `obs_history[:, 1:]`：去掉最旧的一帧，剩 15 帧；
  - `obs.unsqueeze(dim=1)`：新观测 [4096, 45] → [4096, 1, 45]；
  - `torch.cat(..., dim=1)`：拼起来，又是 16 帧。

**4 帧窗口的演示**（假设 H = 4，o_t 表示第 t 步的观测）：

| 时刻 | 窗口内容（旧 → 新） | 说明 |
|---|---|---|
| 开始 | [0, 0, 0, o_0] | 全部清零后放入第一帧 |
| 走 1 步 | [0, 0, o_0, o_1] | |
| 走 2 步 | [0, o_0, o_1, o_2] | |
| 走 3 步 | [o_0, o_1, o_2, o_3] | 窗口填满 |
| 走 4 步 | [o_1, o_2, o_3, o_4] | 最旧的 o_0 被挤出 |
| 第 5 步摔倒重置 | [0, 0, 0, o'_0] | 清零后放入新回合第一帧 |

**两个值得注意的地方**：
1. **回合开头的 15 步，历史里有一部分是 0**。历史编码器训练时见过这种"补零"的历史，所以没问题；但部署时也必须同样补零，否则会出现训练没见过的输入。
2. **历史里只有观测，没有动作**。论文式 (4) 写的是 h_t = (s_{t−H}, a_{t−H}, …, s_t)，但观测里本身包含"上一步动作"这一项【推断，Isaac Lab Go2 观测含 `actions`】，所以动作信息是通过观测间接进入历史的。

### 5.2 `_update_robust_masks`：每次迭代翻转（第 198–207 行）

```python
# gram_on_policy_runner.py:198-207
    def _update_robust_masks(self, robust_masks):
        robust_masks += 1.0
        robust_masks %= 2

        if self.robust_train_only:
            robust_masks[:] = 1.0
        elif self.adapt_train_only:
            robust_masks[:] = 0.0

        return robust_masks
```

**逐行解释**：
- `robust_masks`：[4096, 1]，每个环境一个数，0 = 自适应训练，1 = 鲁棒训练。
- `+= 1` 再 `%= 2`（对 2 取余）：0 → 1，1 → 0，就是**翻转**。
- 第 202–205 行：鲁棒 RL / 域随机化强制全 1；情境 RL 强制全 0。

### 5.3 `_update_robust_masks_on_reset`：只在重置时翻转（第 209–219 行）

```python
# gram_on_policy_runner.py:209-219
    def _update_robust_masks_on_reset(self, robust_masks, reset_env_ids):
        if len(reset_env_ids) > 0:
            robust_masks[reset_env_ids] += 1.0
            robust_masks %= 2
        ...
```

**解释**：只翻转刚重置的那些环境。效果：**一个回合从头到尾只用一种分配**，下一个回合换另一种。这就是消融 **Separate Data**（`gram_separate`）和 **Modular**（`gram_modular`）用的方式（`cli_utils.py` 中这两个算法设置 `robust_mask_reset_update = True`）。

---

## 6. `learn`：训练主循环（第 221–380 行）

这是整个文件最重要的函数。分几段讲。

### 6.1 准备日志写入器（第 222–241 行）

```python
# gram_on_policy_runner.py:223-241（节选）
        if self.log_dir is not None and self.writer is None:
            self.logger_type = self.cfg.get("logger", "tensorboard")
            ...
            elif self.logger_type == "tensorboard":
                self.writer = TensorboardSummaryWriter(log_dir=self.log_dir, flush_secs=10)
```

**解释**：按配置选日志工具：TensorBoard（默认）、Neptune、Weights & Biases。服务器冒烟测试用的是 TensorBoard（`--logger tensorboard`）。`flush_secs=10`：每 10 秒写一次磁盘。

### 6.2 随机回合起点（第 243–246 行）

```python
# gram_on_policy_runner.py:243-246
        if init_at_random_ep_len:
            self.env.episode_length_buf = torch.randint_like(
                self.env.episode_length_buf, high=int(self.env.max_episode_length)
            )
```

**解释**：`train.py:111` 调用时传 `init_at_random_ep_len=True`。把每个环境的"回合已进行步数"随机设成 0–999 之间。

**为什么**：如果 4096 个环境同时开始，它们会在第 1000 步**同时超时、同时重置**，数据会周期性地出现"全是回合开头"或"全是回合末尾"的情况。随机错开后，任何时刻都有处在各个阶段的环境，数据分布更均匀。

### 6.3 初始观测与历史（第 247–260 行）

```python
# gram_on_policy_runner.py:247-260
        obs, extras = self.env.get_observations()
        obs = self.obs_normalizer(obs)
        if "critic" in extras["observations"]:
            critic_obs = self.critic_obs_normalizer(extras["observations"]["critic"])
        else:
            critic_obs = obs
        obs, critic_obs = obs.to(self.device), critic_obs.to(self.device)

        obs_history = torch.zeros(
            (self.env.num_envs, self.obs_history_length, obs.shape[1]), dtype=torch.float32, device=self.device
        )
        reset_env_ids = torch.arange(self.env.num_envs, dtype=torch.int64, device=self.device)
        obs_history = self._update_observation_history(obs_history, obs, reset_env_ids)
        obs_history = obs_history.to(self.device)
```

**解释**：
- 拿到第一帧观测，**经过标准化器**；
- 建一个全 0 的历史 [4096, 16, 45]；
- `reset_env_ids = [0, 1, ..., 4095]`：把所有环境都当作"刚重置"，于是历史 = 15 帧 0 + 第一帧。

**一个细节**：这里的 `reset_env_ids` 包含全部环境，它会被带进主循环。对于 Separate 消融，第一次迭代第一步时，`_update_robust_masks_on_reset` 会用它把**所有**环境的掩码翻转一次（见 6.5 节）。

### 6.4 掩码初始化：一半一半（第 262–264 行）

```python
# gram_on_policy_runner.py:262-264
        robust_mask_update_counter = 0
        robust_masks = torch.zeros((self.env.num_envs, 1), dtype=torch.float32, device=self.device)
        robust_masks[int(self.env.num_envs / 2) :] = 1
```

**解释**：前一半环境（0–2047）初始为 0（自适应），后一半（2048–4095）初始为 1（鲁棒）。

### 6.5 掩码如何交替：4 个环境 × 4 次迭代演示

用 4 个环境说明（环境 0、1 是前一半，环境 2、3 是后一半）。

**GRAM（每次迭代开始时翻转，`robust_mask_update_every = 1`）**：

循环里第 304–309 行，在**每次迭代采样之前**执行：

```python
# gram_on_policy_runner.py:304-309
                if (robust_mask_update_counter % self.robust_mask_update_every == 0) and (
                    not self.robust_mask_reset_update
                ):
                    robust_masks = self._update_robust_masks(robust_masks)
                    robust_masks = robust_masks.to(self.device)
                robust_mask_update_counter += 1
```

| | 环境 0 | 环境 1 | 环境 2 | 环境 3 |
|---|---|---|---|---|
| 初始化（第 264 行） | 0 | 0 | 1 | 1 |
| **迭代 0**（先翻转再采样） | **1 鲁棒** | **1 鲁棒** | **0 自适应** | **0 自适应** |
| **迭代 1** | 0 自适应 | 0 自适应 | 1 鲁棒 | 1 鲁棒 |
| **迭代 2** | 1 鲁棒 | 1 鲁棒 | 0 自适应 | 0 自适应 |
| **迭代 3** | 0 自适应 | 0 自适应 | 1 鲁棒 | 1 鲁棒 |

**要点**：
1. 第一次迭代**之前就翻转了一次**，所以实际第 0 次迭代是前一半鲁棒、后一半自适应，和初始化相反。这只是个细节，不影响结果。
2. **任何时刻都恰好一半环境在做鲁棒训练、一半在做自适应训练**，每个 mini-batch 里两类数据大约各占一半。
3. **对同一个环境来说，每 24 步（约 0.48 秒）就换一次模式**。一个 1000 步的回合里大约换 42 次。所以一条轨迹是"自适应 24 步 → 鲁棒 24 步 → 自适应 24 步……"交替的。这就是论文说的 "allows full trajectories to contain a mixture of both forms of data"。

**这对策略意味着什么**：策略经常遇到这样的情况：上一段在 z = f(c) 下走，状态还不错；突然 latent 变成 0，还可能被推一下，要稳住；过一会儿又切回 f(c)。所以策略被迫学会"**从任意状态无缝接手**"。部署时 α 在 0 和 1 之间连续变化，这种训练正好匹配。消融里 Separate Data（一个回合只用一种模式）远 OOD 只有 0.46，说明这种交替很关键。

**Separate 消融（`robust_mask_reset_update = True`）**：主循环第 304 行条件不成立，不按迭代翻转；改为在**每一步**调用第 312–314 行：

```python
# gram_on_policy_runner.py:311-314
                for i in range(self.num_steps_per_env):
                    if self.robust_mask_reset_update:
                        robust_masks = self._update_robust_masks_on_reset(robust_masks, reset_env_ids)
                        robust_masks = robust_masks.to(self.device)
```

`reset_env_ids` 是上一步结束时刚重置的环境（第 324 行）。效果：

| | 环境 0 | 环境 1 | 环境 2 | 环境 3 |
|---|---|---|---|---|
| 初始化 | 0 | 0 | 1 | 1 |
| 第一步（reset_env_ids = 全部，见 6.3 节） | 1 | 1 | 0 | 0 |
| 之后直到环境 1 摔倒前 | 1 | 1 | 0 | 0 |
| 环境 1 摔倒重置后 | 1 | **0** | 0 | 0 |
| 环境 3 超时重置后 | 1 | 0 | 0 | **1** |

**要点**：一个回合内模式不变，回合结束后翻转。鲁棒组和自适应组的比例不再严格一半一半，会随机波动。

### 6.6 统计缓冲（第 266–273 行）

```python
# gram_on_policy_runner.py:267-273
        self.train_mode()

        ep_infos = []
        rewbuffer = deque(maxlen=100)
        lenbuffer = deque(maxlen=100)
        cur_reward_sum = torch.zeros(self.env.num_envs, dtype=torch.float, device=self.device)
        cur_episode_length = torch.zeros(self.env.num_envs, dtype=torch.float, device=self.device)
```

**解释**：
- `deque(maxlen=100)`：一个最多存 100 个数的队列，满了就把最旧的挤掉。`rewbuffer` 存**最近结束的 100 个回合**的总奖励，`lenbuffer` 存它们的长度。日志里的 "Mean reward" 就是这 100 个的平均。
- `cur_reward_sum`：每个环境**当前回合**到目前为止的累计奖励。

### 6.7 迭代总数与 finetune 起点（第 275–278 行）

```python
# gram_on_policy_runner.py:275-278
        start_iter = self.current_learning_iteration
        tot_iter = start_iter + num_learning_iterations + self.finetune_iterations
        finetune_start_iter = tot_iter - self.finetune_iterations
        for it in range(start_iter, tot_iter):
```

**代入默认值**：start_iter = 0，num_learning_iterations = 10,000，finetune_iterations = 5,000：
- `tot_iter = 15,000`；
- `finetune_start_iter = 10,000`；
- 循环 `it = 0, 1, …, 14,999`；
- **it = 0–9,999 是 RL 阶段，it = 10,000–14,999 是 finetune 阶段**。

对于没有 finetune 的算法（鲁棒 RL、域随机化，且未开 `robust_use_latent_actor`），`cli_utils.py` 把 `finetune_iterations` 设为 0，于是 `finetune_start_iter = tot_iter = 10,000`，循环里永远不会进入 finetune。

### 6.8 进入 finetune 阶段时的切换（第 282–302 行）

```python
# gram_on_policy_runner.py:279-302
            start = time.time()
            # Rollout
            with torch.inference_mode():
                if it == finetune_start_iter:
                    title_string = "BEGIN FINETUNE PHASE"
                    ...
                    print(log_string)

                    self.alg.actor_critic.act_from_context = False

                    # turn off adversary
                    if not self.finetune_w_adversary:
                        self.alg.adversary_policy.adversary_prob = 0.0
                        adversary_actions = self.alg.adversary_policy.act(obs).detach()
                        adversary_masks = self.alg.adversary_policy.generate_adversary_masks(obs).detach()
                        self.alg.adversary_update_sim(adversary_actions, torch.zeros_like(adversary_masks))

                    # switch normalizers to eval mode
                    if self.empirical_normalization:
                        self.obs_normalizer.eval()
                        self.critic_obs_normalizer.eval()

                    # save pre-finetune checkpoint
                    self.save(os.path.join(self.log_dir, f"model_{it}.pt"))
```

**`torch.inference_mode()`**：整个采样阶段关闭梯度追踪，节省显存和时间。

**在 it = 10,000 这一次迭代开始时，做了四件事**：

| # | 代码 | 含义 |
|---|---|---|
| 1 | `act_from_context = False` | **教师 → 学生**：从此以后采样时 latent 不再用 f(c)，而用历史编码器的估计。对应论文"Data collection uses the student policy" |
| 2 | `adversary_prob = 0.0` 并把掩码清零 | **关闭对抗者**。对应论文"We do not apply an adversary during the supervised learning phase"。改概率为 0 只影响以后的抽签；当前事件参数里可能还留着上一步的掩码，所以再显式写一次全 0 掩码 |
| 3 | 标准化器 `.eval()` | **冻结观测标准化的均值和方差**。之后不再变化，保证 finetune 和部署时的输入尺度与这时一致 |
| 4 | `save(model_10000.pt)` | 保存 finetune 前的模型。之后如果想换一种历史损失重做 finetune，可以从这里加载并加 `--finetune_fresh_start` |

**finetune 阶段采样时 latent 具体是什么？** `act_from_context=False` → `calculate_latent` 调用 `encode_history`（`gram_actor_critic.py:567-620`）。训练时 `history_epinet_apply_bias=False`（只在评估时打开，`cli_utils.py` 中 gram 的 eval 分支），默认 `output_type="base"`，所以 latent = **base 网络的输出**，没有 α 缩放。鲁棒组仍然用 0 向量（掩码照常交替）。

**注意**：finetune 刚开始时历史编码器还是随机的（RL 阶段没训练过它，见 05 篇 3.7 节），所以前几次迭代学生策略的动作质量会很差，机器狗可能频繁摔倒。随着 finetune 进行，估计越来越准，学生采到的数据也越来越接近部署时的情况。这正是"用学生自己采数据"（DAgger 思路）的意义：**训练分布 = 部署分布**。

### 6.9 采样 24 步（第 311–347 行）

```python
# gram_on_policy_runner.py:311-334
                for i in range(self.num_steps_per_env):
                    if self.robust_mask_reset_update:
                        robust_masks = self._update_robust_masks_on_reset(robust_masks, reset_env_ids)
                        robust_masks = robust_masks.to(self.device)

                    actions = self.alg.act(obs, critic_obs, obs_history, robust_masks)
                    obs, rewards, dones, infos = self.env.step(actions)
                    obs = self.obs_normalizer(obs)
                    if "critic" in infos["observations"]:
                        critic_obs = self.critic_obs_normalizer(infos["observations"]["critic"])
                    else:
                        critic_obs = obs

                    reset_env_ids = self.env.unwrapped.reset_buf.nonzero(as_tuple=False).squeeze(-1)
                    obs_history = self._update_observation_history(obs_history, obs, reset_env_ids)
                    obs_history = obs_history.to(self.device)

                    obs, critic_obs, rewards, dones = (
                        obs.to(self.device), critic_obs.to(self.device),
                        rewards.to(self.device), dones.to(self.device),
                    )
                    self.alg.process_env_step(rewards, dones, infos)
```

**一步之内的顺序**（非常重要，改代码时容易出错）：

| 顺序 | 代码 | 做了什么 |
|---|---|---|
| ① | `self.alg.act(...)`（第 316 行） | 用**当前**观测和历史算动作和价值；对抗者抽签、选方向，并写进仿真事件；把这些都记进 `transition`（05 篇 3.3 节） |
| ② | `self.env.step(actions)`（第 317 行） | 仿真器执行动作（50 Hz 策略，内部 PD 200 Hz，所以一个策略步跑 4 个物理步【推断】）；被选中的环境被对抗者踢一下；返回新观测、奖励、done；**摔倒或超时的环境会被自动重置**，返回的 obs 是新回合的第一帧【推断，Isaac Lab 自动重置行为】 |
| ③ | `obs_normalizer(obs)`（第 318 行） | 标准化新观测（train 模式下同时更新统计量） |
| ④ | 第 324 行 | 找出刚重置的环境。`reset_buf` 是 Isaac Lab 记录"这一步谁重置了"的布尔数组，`.nonzero()` 取出为 True 的下标 |
| ⑤ | 第 325 行 | 更新历史：重置的环境先清零，然后所有环境滑动一格放入新观测 |
| ⑥ | `process_env_step`（第 334 行） | 【推断，rsl_rl 2.0 父类】把奖励、done 填进 transition；对"超时"（而非摔倒）结束的回合做价值自举修正（`rewards += γ × V × time_outs`）；调用 `storage.add_transitions` 存入缓冲区；清空 transition |

**关于"超时修正"的补充**【推断，需对照 rsl_rl 2.0】：回合超时结束时，机器狗其实还好好的，只是时间到了。如果直接当作"结束"，GAE 会认为以后没有奖励了，低估了这个状态的价值。rsl_rl 的做法是把 γ × V(s) 加到最后一步的奖励上，相当于"假装还能继续走"。

### 6.10 统计回合奖励（第 336–347 行）

```python
# gram_on_policy_runner.py:336-347
                    if self.log_dir is not None:
                        if "episode" in infos:
                            ep_infos.append(infos["episode"])
                        elif "log" in infos:
                            ep_infos.append(infos["log"])
                        cur_reward_sum += rewards
                        cur_episode_length += 1
                        new_ids = (dones > 0).nonzero(as_tuple=False)
                        rewbuffer.extend(cur_reward_sum[new_ids][:, 0].cpu().numpy().tolist())
                        lenbuffer.extend(cur_episode_length[new_ids][:, 0].cpu().numpy().tolist())
                        cur_reward_sum[new_ids] = 0
                        cur_episode_length[new_ids] = 0
```

**解释**：
- `infos["log"]`：Isaac Lab 在回合结束时汇报的分项统计，例如各奖励项的平均值、终止原因、速度误差（日志里的 `Metrics/base_velocity/error_vel_xy` 等）。
- 每步把奖励累加到 `cur_reward_sum`；
- 回合结束（`dones > 0`）的环境：把它的总奖励和长度放进 100 长度的队列，然后清零重新累计。

**注意**：这里的 `rewards` 是**训练奖励**，包含所有惩罚项（力矩、动作变化率等），和论文 Table III 的"归一化任务回报"**不是同一个东西**。后者只算速度跟踪奖励，见第 9 节。

### 6.11 计算回报（第 349–354 行）

```python
# gram_on_policy_runner.py:349-354
                stop = time.time()
                collection_time = stop - start

                # Learning step
                start = stop
                self.alg.compute_returns(critic_obs, obs_history, robust_masks)
```

**解释**：
- 记录采样耗时；
- 用**第 25 步的观测**（最后一次 step 之后的 obs）算 `last_values`，再做 GAE（05 篇 3.5 节、2.5 节）。
- 注意它仍然在 `torch.inference_mode()` 里面（第 281 行的 with 块到这里结束）。

### 6.12 学习：RL 还是 finetune（第 356–362 行）

```python
# gram_on_policy_runner.py:356-362
            if it >= finetune_start_iter:
                loss_stats, update_stats = self.alg.finetune()
            else:
                loss_stats, update_stats = self.alg.update()
                self.alg.adversary_policy.update_magnitude((it - start_iter + 1) / (finetune_start_iter - start_iter))
            stop = time.time()
            learn_time = stop - start
```

**逐行解释**：
- it ≥ 10,000：`finetune()`，只训练历史编码器（05 篇 3.10 节）；
- it < 10,000：`update()`，PPO 主更新 + 对抗者更新（05 篇 3.6–3.8 节）；然后**更新对抗者强度**：

$$\text{progress} = \frac{it - 0 + 1}{10000 - 0} = \frac{it + 1}{10000}$$

| it | progress | 对抗者最大强度 |
|---|---|---|
| 0 | 0.0001 | 0.0001 m/s |
| 999 | 0.1 | 0.1 m/s |
| 4,999 | 0.5 | 0.5 m/s |
| 9,999 | 1.0 | 1.0 m/s |

这就是对抗者的**课程（curriculum）**：开始时策略还不会走路，推得太狠会学不会；随着策略变强，推力逐渐加大。

**注意**：强度在 `update()` **之后**更新，所以第 it 次迭代采样时用的是第 it−1 次更新后的强度。第 0 次迭代采样时强度为 0（初始值 `adversary_max_scale_start = 0`），即第一次迭代实际上没有推力。

### 6.13 日志、保存、记录代码状态（第 363–375 行）

```python
# gram_on_policy_runner.py:363-375
            self.current_learning_iteration = it
            if self.log_dir is not None:
                self.log(locals())
            if it % self.save_interval == 0:
                self.save(os.path.join(self.log_dir, f"model_{it}.pt"))
            ep_infos.clear()
            if it == start_iter:
                git_file_paths = store_code_state(self.log_dir, self.git_status_repos)
                ...
```

**解释**：
- `self.log(locals())`：`locals()` 把当前函数里**所有局部变量**打包成字典传给 `log`，所以 `log` 能读到 `collection_time`、`loss_stats`、`rewbuffer` 等。
- 第 366–367 行：每 5000 次迭代存一次。默认会在 it = 0、5,000、10,000 存（10,000 还会在 finetune 切换时存一次，同名覆盖）。
- 第 369–375 行：第一次迭代时把代码的 git 状态（diff）存进日志目录，方便以后追溯"这个模型是用哪版代码训练的"。【推断】`git_status_repos` 为空列表时，rsl_rl 可能只记录 rsl_rl 自己的仓库状态。

### 6.14 训练结束：收集验证集、最终保存（第 377–380 行）

```python
# gram_on_policy_runner.py:377-380
        # Calculate and save validation metrics
        self.collect_validation_data()

        self.save(os.path.join(self.log_dir, f"model_{self.current_learning_iteration}.pt"))
```

**解释**：15,000 次迭代全部完成后：
1. 收集验证集，算出不确定性的 101 个分位数，存进网络（第 8 节）；
2. 保存最终模型 `model_14999.pt`。**只有这个文件里有有效的验证集分位数**，评估时应该加载它。

---

## 7. `log`：日志里每个数的含义（第 382–469 行）

**这段要干什么**：每次迭代结束，把统计量写进 TensorBoard，并在终端打印一段文字。

### 7.1 终端打印的每一行

服务器冒烟测试的日志就是这个格式：

```
                        Learning iteration 1/3
                       Computation: 2850 steps/s (collection: 0.400s, learning 0.150s)
               Value function loss: 0.0302
                    Surrogate loss: 0.0076
                      History loss: 0.0000
             Mean action noise std: 1.00
                       Mean reward: ...
               Mean episode length: ...
Metrics/base_velocity/error_vel_xy: 0.0000
...
--------------------------------------------------------------------------------
                   Total timesteps: ...
                    Iteration time: 0.55s
                        Total time: ...
                               ETA: ...
```

| 行 | 含义 | 正常训练时应该怎样变化 |
|---|---|---|
| `Learning iteration i/N` | 当前迭代号 / 总数（N = 15,000） | |
| `Computation: X steps/s` | 每秒处理多少个环境步 = 24 × 4096 ÷ 本次迭代耗时 | 衡量速度，用来估算总时长 |
| `collection` | 采样耗时（主要是仿真） | |
| `learning` | 学习耗时（反向传播） | |
| `Value function loss` | 价值损失（20 个 mini-batch 平均） | 先升后降；finetune 阶段恒为 0 |
| `Surrogate loss` | 裁剪策略损失 | 在 0 附近小幅波动，没有明显趋势是正常的 |
| `History loss` | 历史编码器损失 | **RL 阶段恒为 0**，finetune 阶段从较大值下降 |
| `Mean action noise std` | 动作标准差 σ 的平均 | 从 1.0 逐渐下降 |
| `Mean reward` | 最近 100 个结束回合的总训练奖励 | 上升 |
| `Mean episode length` | 最近 100 个回合的长度 | 上升到接近 1000（不摔倒） |
| `Episode_Reward/...`、`Metrics/...` 等 | Isaac Lab 回合结束时汇报的分项 | 跟踪奖励上升、速度误差下降 |
| `Total timesteps` | 累计环境步数 | 每次迭代 + 98,304 |
| `Iteration time` | 本次迭代总耗时 | |
| `Total time` | 累计耗时 | |
| `ETA` | 预计剩余时间 | **注意**：公式用的是 `num_learning_iterations`（10,000），不含 finetune，所以后期会偏小，到 it > 10,000 时甚至会变成负数 |

### 7.2 TensorBoard 里的曲线（第 411–431 行）

| 分组 | 曲线 | 含义 |
|---|---|---|
| `Loss/` | `value_function`、`surrogate`、`history`、`learning_rate` | 损失和当前学习率（可看到 KL 自适应调节） |
| `Update/` | `mean_adapt_std`、`mean_latent_l2`、`mean_latent_std`、`uncertainty_metric_ave`、`mean_epi_error_l2`（finetune）、对抗者相关 | 见 05 篇 3.9 节 |
| `Policy/` | `mean_noise_std` | 动作标准差 |
| `Perf/` | `total_fps`、`collection time`、`learning_time` | 速度 |
| `Train/` | `mean_reward`、`mean_episode_length`（按迭代和按时间两种横轴） | 训练效果 |
| `Episode/` 或带 `/` 的键 | Isaac Lab 分项 | |

**复现时重点盯的 5 条曲线**：`Train/mean_reward`、`Train/mean_episode_length`、`Loss/history`（finetune 阶段）、`Update/mean_latent_std`（f(c) 是否学到区分环境）、`Update/uncertainty_metric_ave`（finetune 阶段应下降）。

---

## 8. `collect_validation_data`：定标 α 的验证集（第 497–616 行）

**这段要干什么**：训练结束后，在**训练分布（ID）**下跑一遍，记录每一步的不确定性 ‖σ̂‖²，统计它的分布，存下 101 个分位数。部署时用其中的 0.90 和 0.99 分位数算 β 和 λ（论文 Sec. VI）。

### 8.1 准备：关对抗者、选 latent 来源（第 502–515 行）

```python
# gram_on_policy_runner.py:502-515
        self.eval_mode()

        # turn off adversary
        obs, _ = self.env.get_observations()
        obs = self.obs_normalizer(obs)
        self.alg.adversary_policy.adversary_prob = 0.0
        adversary_actions = self.alg.adversary_policy.act(obs).detach()
        adversary_masks = self.alg.adversary_policy.generate_adversary_masks(obs).detach()
        self.alg.adversary_update_sim(adversary_actions, torch.zeros_like(adversary_masks))

        if self.collect_data_from_context:
            self.alg.actor_critic.act_from_context = True
        else:
            self.alg.actor_critic.act_from_context = False
```

**解释**：
- `eval_mode()`：冻结标准化器；
- 关闭对抗者（和 finetune 切换时一样）。**验证集必须是"干净的 ID 数据"**，不能有推力，否则推力引起的异常会被当成"正常"，β 会被定得过高；
- 默认 `collect_data_from_context = False`：用**学生**（历史编码器）驱动策略，和部署时一致。

**注意**：这里用的是**训练环境本身**（同样的 4096 个环境、同样的上下文范围），所以确实是 ID。

### 8.2 两轮采集（第 517–584 行）

```python
# gram_on_policy_runner.py:519-524
            uncertainty_metrics = torch.zeros(
                (2, self.env.num_envs, self.env.unwrapped.max_episode_length), device=self.device
            )
            alive_mask = torch.zeros((2, self.env.num_envs, self.env.unwrapped.max_episode_length), device=self.device)

            for robust_mask_value in [0, 1]:
```

**解释**：
- `uncertainty_metrics`：[2, 4096, 1000]，第 0 维是"第几轮"，记录每轮、每个环境、每一步的不确定性；
- `alive_mask`：同样形状，记录这一步机器狗是否还"活着"（回合没结束）；
- 共两轮：`robust_mask_value = 0` 和 `1`。

**每一轮做什么**（第 526–584 行）：

```python
# gram_on_policy_runner.py:526-550（节选）
                alive = torch.ones(self.env.num_envs, device=self.device)

                obs, extras = self.env.reset()
                obs = self.obs_normalizer(obs)
                ...
                obs_history = torch.zeros(...)
                reset_env_ids = torch.arange(self.env.num_envs, ...)
                obs_history = self._update_observation_history(obs_history, obs, reset_env_ids)

                if self.collect_data_mix:
                    robust_masks = torch.zeros((self.env.num_envs, 1), ...)
                    robust_masks[int(self.env.num_envs / 2) :] = 1
                else:
                    robust_masks = (torch.ones((self.env.num_envs, 1), ...) * robust_mask_value)
```

1. 所有环境标记为活着；
2. **重置所有环境**，历史清零；
3. 设置掩码：
   - **GRAM 默认 `collect_data_mix = True`**：一半一半，并在第 554–556 行每 24 步翻转一次，**和训练时完全一样**。此时 `robust_mask_value` 只用来区分存在第几轮，**两轮的做法相同**，相当于重复采两次；
   - `collect_data_mix = False`（Separate、Modular 消融）：第 0 轮全部自适应，第 1 轮全部鲁棒。

```python
# gram_on_policy_runner.py:553-584（节选）
                for t in range(self.env.unwrapped.max_episode_length):
                    if self.collect_data_mix and (t % self.num_steps_per_env == 0):
                        robust_masks = self._update_robust_masks(robust_masks)

                    actions = self.alg.actor_critic.act_inference_from_mask(
                        obs, self.alg.context, obs_history, robust_masks, deterministic=self.collect_data_deterministic
                    )
                    obs, rewards, dones, infos = self.env.step(actions)
                    obs = self.obs_normalizer(obs)
                    ...
                    reset_env_ids = self.env.unwrapped.reset_buf.nonzero(as_tuple=False).squeeze(-1)
                    obs_history = self._update_observation_history(obs_history, obs, reset_env_ids)
                    ...
                    uncertainty_metric_step = self.alg.actor_critic.calculate_uncertainty_metric(obs_history)
                    uncertainty_metrics[robust_mask_value, :, t] = uncertainty_metric_step

                    alive *= 1 - dones
                    alive_mask[robust_mask_value, :, t] = alive
```

4. 走满 1000 步（一个最长回合）：
   - `act_inference_from_mask`（`gram_actor_critic.py:484-501`）：按给定掩码算动作；`deterministic=True` 时直接用均值，不加噪声；
   - 走一步，更新历史；
   - **算这一步的不确定性**：`calculate_uncertainty_metric`（`gram_actor_critic.py:674-682`）= epinet 8 个样本在 8 维上的方差之和，也就是 ‖σ̂(h)‖²；
   - **`alive *= 1 - dones`**：一旦某个环境结束过一次，`alive` 就永远变成 0。环境会自动重置并继续走，但之后的数据**不计入**。这样只统计"每个环境的第一个回合"。

**为什么要用 alive 掩码？** 如果机器狗摔倒了，摔倒过程中的历史很"奇怪"，不确定性会很高，这些不代表"正常 ID 情况"。另外重置后历史里有很多 0，也不典型。只取第一个回合的存活部分更干净。

### 8.3 计算分位数（第 586–606 行）

```python
# gram_on_policy_runner.py:586-606
            alive_traj_mask = alive_mask.sum(dim=-1) == (self.env.unwrapped.max_episode_length - 1)

        if self.uncertainty_metric_adapt_only:
            alive_mask = alive_mask[0]
            alive_mask_traj = alive_traj_mask[0]
            uncertainty_metrics = uncertainty_metrics[0]
        else:
            alive_mask = alive_mask.flatten(start_dim=0, end_dim=1)
            alive_mask_traj = alive_traj_mask.flatten(start_dim=0, end_dim=1)
            uncertainty_metrics = uncertainty_metrics.flatten(start_dim=0, end_dim=1)

        if self.uncertainty_metric_full_only:
            uncertainty_metrics = uncertainty_metrics[alive_mask_traj]
            alive_mask = alive_mask[alive_mask_traj]

        uncertainty_metrics = uncertainty_metrics[alive_mask == 1]
        validation_quantiles_value = uncertainty_metrics.quantile(q=self.alg.actor_critic.validation_quantiles_q)

        self.alg.actor_critic.store_validation(validation_quantiles_value)
```

**逐行解释**：
- 第 586 行：**"完整轨迹"的判断**。如果一个环境一直没摔倒，到第 1000 步时因**超时**结束，`dones` 在最后一步为 1，所以 `alive` 在最后一步变成 0，存活步数之和 = 999 = max_episode_length − 1。所以这一行的意思是"**活到超时的环境**"。
- 第 589–596 行：默认把两轮合并：[2, 4096, 1000] → [8192, 1000]。
- 第 598–600 行：默认不只取完整轨迹。
- 第 602 行：只取存活时刻的不确定性，展平成一维。最多 2 × 4096 × 1000 ≈ **819 万个数**。
- 第 603 行：**计算 101 个分位数**。`validation_quantiles_q = linspace(0, 1, 101)` = [0, 0.01, 0.02, …, 1.00]（`gram_actor_critic.py:157`）。
  - 例：0.90 分位数 = 把这 819 万个数从小到大排序，排在 90% 位置的那个数。
- 第 606 行：`store_validation`：把 101 个数写进网络参数，并把 `validation_quantiles_saved` 设为 True（`gram_actor_critic.py:702-704`）。

**之后怎么用**：`set_uncertainty_params()`（`gram_actor_critic.py:706-730`）在**加载模型时**被调用（第 147 行）：
- β = 分位数表在 0.90 处的值；
- λ = −ln(0.01) ÷ (q₀.₉₉ − q₀.₉₀)。

**注意**：`store_validation` 之后，runner **没有**立即调用 `set_uncertainty_params()`。所以同一次运行里如果紧接着评估，β 和 λ 还是旧的；必须通过 `load` 加载最终模型，才会用上新的分位数。GRAM 的流程中，训练和评估是两个独立的命令，所以没问题。

**数值例子**：假设 819 万个不确定性值中，q₀.₉₀ = 3.0，q₀.₉₉ = 6.0：
- β = 3.0；
- λ = 4.605 ÷ (6.0 − 3.0) = 1.535；
- 某时刻不确定性 = 2.5 → (2.5 − 3.0)⁺ = 0 → α = 1.00；
- 不确定性 = 4.0 → α = exp(−1.535 × 1.0) = 0.215；
- 不确定性 = 6.0 → α = exp(−1.535 × 3.0) = 0.010。

### 8.4 打印（第 608–616 行）

`--print_stats` 时打印全部 101 个分位数，格式为 `Q  90:    3.0000`。复现时建议打开，记录下来，便于和别的训练对比。

### 8.5 一个值得思考的设计

默认配置下，验证集里**一半是鲁棒模式（latent = 0）驱动的轨迹**。也就是说，"ID 的历史"包括了"策略在不知道环境时走出来的历史"。这样定出来的 β 会把"鲁棒模式下的正常走法"也算作见过。部署时 GRAM 退回鲁棒模式后，历史会变成鲁棒模式的走法，不确定性会下降，α 又回升。这可能形成一种"退回 → 稳住 → 恢复适应"的自然循环。论文没有讨论这一点，是我们的分析。

---

## 9. `evaluate`：评估（第 618–776 行）

**这段要干什么**：加载训练好的模型，在指定的测试场景（例如 9 kg 负载、10° 坡）下，让每个环境走**一个回合**，统计回报、存活步数和 α。

**被谁调用**：`eval.py:115`：`runner.evaluate(eval_inputs_dict, deterministic=(not args_cli.stochastic_eval))`。默认 `deterministic=True`。

**评估环境和训练环境的区别**（由 `cli_utils.py` 和环境配置在 eval_mode 下设置）：
- 只保留**跟踪奖励**（线速度、角速度跟踪），去掉所有惩罚项（`unitree_go2_custom_env.py:279-283`）；
- 速度指令不重新采样（`resample_time = 1e6`），一个回合一个指令；
- 身体（除脚外）着地就终止（`terminate_contacts`）；
- 对抗者强度为 0；
- `act_from_context = False`（学生模式）；
- GRAM：`act_inference_adapt = True`、`history_epinet_apply_bias = True`（`cli_utils.py:569-575`）。

### 9.1 初始化（第 619–645 行）

```python
# gram_on_policy_runner.py:619-645（节选）
        self.eval_mode()

        alive = torch.ones(self.env.num_envs, device=self.device)
        total_rewards = torch.zeros(self.env.num_envs, device=self.device)
        total_steps = torch.zeros(self.env.num_envs, device=self.device)
        alive_mask = torch.zeros((self.env.num_envs, self.env.unwrapped.max_episode_length), device=self.device)

        if self.alg.actor_critic.history_epinet:
            epinet_base_l2 = torch.zeros((self.env.num_envs, self.env.unwrapped.max_episode_length), ...)
            epinet_mean_l2 = ...
            epinet_std_l2 = ...
            alpha = ...

        obs, extras = self.env.reset()
        obs = self.obs_normalizer(obs)
        ...
        obs_history = self._update_observation_history(obs_history, obs, reset_env_ids)

        uncertainty_metric_step = self.alg.actor_critic.calculate_uncertainty_metric(obs_history)
```

**解释**：准备累加器：每个环境的总回报、存活步数；每步的 α 和三个 epinet 统计量（[环境数, 1000]）。重置环境，初始化历史，算第一步的不确定性。

### 9.2 主循环（第 647–678 行）

```python
# gram_on_policy_runner.py:647-678
        for t in range(self.env.unwrapped.max_episode_length):
            with torch.inference_mode():
                alive_mask[:, t] = alive
                if self.alg.actor_critic.history_epinet:
                    epinet_base_l2_step, epinet_mean_l2_step, epinet_std_l2_step, alpha_step = (
                        self.alg.actor_critic.calculate_epinet_metrics(obs_history)
                    )
                    epinet_base_l2[:, t] = epinet_base_l2_step
                    epinet_mean_l2[:, t] = epinet_mean_l2_step
                    epinet_std_l2[:, t] = epinet_std_l2_step
                    alpha[:, t] = alpha_step

                actions = self.alg.actor_critic.act_inference(
                    obs, self.alg.context, obs_history, uncertainty_metric_step, deterministic=deterministic
                )
                obs, rewards, dones, infos = self.env.step(actions)
                obs = self.obs_normalizer(obs)
                obs = obs.to(self.device)

                reset_env_ids = self.env.unwrapped.reset_buf.nonzero(as_tuple=False).squeeze(-1)
                obs_history = self._update_observation_history(obs_history, obs, reset_env_ids)
                uncertainty_metric_step = self.alg.actor_critic.calculate_uncertainty_metric(obs_history)

                total_rewards += rewards * alive
                total_steps += alive
                alive *= 1 - dones
```

**每一步做的事**：

| 顺序 | 代码 | 做了什么 |
|---|---|---|
| ① | 第 650 行 | 记录这一步之前是否活着 |
| ② | `calculate_epinet_metrics`（第 652–658 行） | 算四个量（`gram_actor_critic.py:684-700`）：`base_l2` = ‖φ_base(h)‖²；`mean_l2` = ‖μ̂(h)‖²；`std_l2` = ‖σ̂(h)‖²（不确定性）；`alpha` = exp(−λ(std_l2 − β)⁺) |
| ③ | `act_inference`（第 661–663 行） | 算动作。GRAM 下内部流程：`calculate_latent` → `encode_history`，因为 `apply_bias=True`，**latent = α × base 输出**（式 9，z_rob = 0）；`robust_masks` 由 `calculate_uncertainty_mask` 算出，但随后被 `act_inference_adapt=True` 覆盖为全 0，所以**α 是唯一的退回机制**。`uncertainty_metric_step` 参数只对 Modular 消融有用（硬阈值切换） |
| ④ | `env.step` | 走一步 |
| ⑤ | 第 669–673 行 | 更新历史，算下一步的不确定性 |
| ⑥ | 第 676–678 行 | **只累加活着时的奖励和步数**；一旦结束，`alive` 永远为 0 |

**注意**：第 ② 步和第 ③ 步各自独立调用了一次 epinet，**两次的随机样本 ε 不同**，所以记录的 α 和实际用来算动作的 α 有细微差别。差别来自 8 个随机样本的抽样误差，影响很小。

### 9.3 整理结果（第 680–707 行）

```python
# gram_on_policy_runner.py:681-689
        eval_log = {
            "params": eval_inputs_dict,
            "returns": total_rewards.numpy(force=True),
            "episode_length": total_steps.numpy(force=True),
        }

        if self.alg.actor_critic.history_epinet:
            alpha_ave = torch.sum(alpha * alive_mask, dim=-1) / torch.sum(alive_mask, dim=-1)
            eval_log["alpha"] = alpha_ave.numpy(force=True)
```

**`eval_log` 的内容**：

| 键 | 形状 | 含义 |
|---|---|---|
| `params` | 字典 | 这次评估的场景参数（质量、摩擦、坡度、冻结关节等） |
| `returns` | [环境数] | 每个环境一个回合的**跟踪奖励总和** |
| `episode_length` | [环境数] | 每个环境活了多少步（最多 1000） |
| `alpha` | [环境数] | 每个环境存活期间 α 的平均值 |
| `alive/alive_mask` 等（仅 `--save_eval_detailed`） | [环境数, 1000] | 逐步的存活、base_l2、mean_l2、std_l2、α；**结束后的步填 NaN** |
| `epinet/alpha_shift`、`alpha_scale`、`alpha_max_threshold`（同上） | 标量 | β、λ、Modular 用的硬阈值（q₀.₉₉） |

`eval.py:121` 用 `dump_pickle` 把 `eval_log` 存成 pickle 文件。

**论文里的"归一化任务回报"怎么来的？** 【代码事实】仓库里**没有**归一化和画图的脚本。【推断】大概是把 `returns` 除以"理论最大跟踪奖励"（每步满分 × 1000 步），得到 [0, 1] 的数；再对多个场景、多个种子取平均。复现时需要自己写这一步，并在报告里写清楚口径。

**论文 Fig. 4 的"平均 α"和"25%-CVaR α"**：可以从 `epinet/alpha`（逐步）算出：平均 α = 所有存活步的均值；25%-CVaR α = 所有存活步中最小的 25% 的均值。

### 9.4 打印统计（第 709–774 行）

`--print_stats` 时打印：
- 场景参数；
- 总回报的均值、标准差、最小、最大；
- 存活步数的同样四个统计；
- **α 的分布**：均值、最小值、1%–99% 的若干分位数、最大值；
- **不确定性（std_l2）的分布**：同上。

服务器冒烟测试 `evaluate_v2.log` 的结尾就是这一段。那次用的是只训练了 2 次迭代的模型，α 的 Q95、Q99 都是 1.0，不确定性 Q50 约 4.1，这些数**没有意义**，只证明流程能跑通。

---

## 10. 一次完整训练的时间线

默认 GRAM 配置，`python -m source.train --alg_name gram --id_context default`：

```
构造 runner（__init__）
 ├─ 建 actor-critic、PPO、缓冲区、对抗者、三个优化器
 └─ 上下文固定：每个环境 26 维参数，整个训练不变

learn(num_learning_iterations=10000, init_at_random_ep_len=True)
 ├─ 随机化每个环境的回合起点；历史清零；掩码一半 0、一半 1
 │
 ├─ it = 0 … 9,999 ─────────────── RL 阶段（教师）─────────────────────────────┐
 │   每次迭代：                                                                │
 │   ├─ 翻转掩码（鲁棒 ↔ 自适应）                                               │
 │   ├─ 采样 24 步：latent = f(c)（自适应组）或 0（鲁棒组）；鲁棒组 5% 概率被推   │
 │   ├─ GAE（两组分别标准化优势）                                               │
 │   ├─ update()：PPO 20 步；每 10 次迭代对抗者也更新 20 步；历史编码器不训练     │
 │   ├─ 对抗者最大强度 = (it+1)/10000 m/s                                       │
 │   └─ it = 0、5000 时保存模型                                                │
 │                                                                            │
 ├─ it = 10,000：切换 ─────────────────────────────────────────────────────────┤
 │   act_from_context=False（学生）；关闭对抗者；冻结观测标准化；保存 model_10000 │
 │                                                                            │
 ├─ it = 10,000 … 14,999 ─────── finetune 阶段（学生）──────────────────────────┤
 │   每次迭代：                                                                │
 │   ├─ 翻转掩码                                                               │
 │   ├─ 采样 24 步：latent = 历史编码器 base 输出（自适应组）或 0（鲁棒组）；无推力 │
 │   └─ finetune()：只训练历史编码器 + epinet（20 步）；策略、f、对抗者都不动     │
 │                                                                            │
 ├─ 训练结束 ──────────────────────────────────────────────────────────────────┘
 │   collect_validation_data()：两轮 × 4096 环境 × 1000 步，学生驱动、无推力、确定性
 │   → 约 819 万个不确定性值 → 101 个分位数 → 写进网络
 └─ 保存 model_14999.pt（唯一含有效验证分位数的模型）

评估（另一条命令）：python -m source.eval --load_run ... --checkpoint model_14999.pt [场景参数]
 └─ load()：恢复参数 → set_uncertainty_params() 算 β、λ → evaluate() 跑一个回合
```

**数据量**：每次迭代 98,304 步；RL 阶段共约 9.8 亿步，finetune 约 4.9 亿步，合计约 **14.7 亿**环境步（约 8,200 小时的机器狗"经验"，按 50 Hz 计）。

**时间估算**【估计】：服务器冒烟测试 16 个环境时每次迭代约 0.55–1.6 s，不能直接外推到 4096 个环境。按选题阶段对 RTX 4090 级别 GPU 的类比（4096 环境约 1.2–1.3 s/iter），15,000 次迭代约 5–6 小时；考虑到 GPU 与他人共享，实际可能更长。正式训练前应先跑 50 次迭代测速。

---

## 11. 六种算法在 runner 里走哪些分支

开关来自 `cli_utils.py:546-620`（`update_agent_cfg_by_alg`）。

| 算法 | 论文中的名字 | 掩码方式 | 鲁棒分支是什么 | 对抗者 | finetune（历史编码器） | 验证集 | 评估时 latent | 评估时退回方式 |
|---|---|---|---|---|---|---|---|---|
| `gram` | GRAM | 每次迭代翻转（`collect_data_mix=True`） | 同一 actor，输入 0 | 开（推鲁棒组） | 有，5000 次 | 混合两组 | 学生 base 输出 × α | **α 软缩放**（`apply_bias=True`，`act_inference_adapt=True`） |
| `gram_separate` | Separate Data | **回合重置时翻转**（`robust_mask_reset_update=True`，`collect_data_mix=False`） | 同一 actor，输入 0 | 开 | 有 | 第 0 轮全自适应、第 1 轮全鲁棒 | 同 GRAM | α 软缩放 |
| `gram_modular` | Modular | 回合重置时翻转 | **独立的鲁棒 actor/critic**（`robust_as_zeros=False`，鲁棒 actor 只看观测） | 开 | 有 | 两轮分开 | 学生 base 输出（不缩放） | **硬切换**：不确定性 > q₀.₉₉ 时整体改用鲁棒 actor（`calculate_uncertainty_mask`） |
| `robust_rl` | Robust RL | 全部 1（`robust_train_only`） | 独立鲁棒 actor，只看观测 | 开 | 无（`finetune_iterations=0`） | 照常收集（有 epinet=False，指标为 0） | 不用 | 始终用鲁棒 actor（`act_inference_robust=True`） |
| `contextual_rl` | Contextual RL | 全部 0（`adapt_train_only`） | 不使用 | **关**（`adversary_prob=0`，环境推力强度 0） | 有（普通历史编码器，无 epinet） | 照常 | 学生估计 | 无退回（`act_inference_adapt=True`） |
| `domain_rand` | Domain Rand. | 全部 1（`robust_train_only`） | 独立 actor，只看观测 | **关** | 无 | 照常 | 不用 | 始终用"鲁棒"actor（其实就是不看 latent 的 DR 策略） |

**几个容易混淆的点**：
1. **域随机化在代码里是"不带对抗者的鲁棒 RL"**：都走 `robust_train_only`，用独立的、只看观测的 actor；区别只在有没有对抗者。
2. **鲁棒 RL 和域随机化的策略看不到 latent**，所以也不需要历史编码器，finetune 次数被设为 0。
3. **GRAM 和 Separate 的唯一区别是掩码怎么翻转**（以及验证集怎么采），网络和损失完全相同。这是一个很干净的消融。
4. **Modular 有两个独立策略**，用硬阈值切换，对应"传统的监督切换"思路；GRAM 是一个策略 + 软缩放。
5. 没有对应论文 "No φ_GRAM" 消融的独立算法名。【推断】它是用 `gram` 训练出的模型，在评估时不开 `apply_bias`（即不做 α 缩放）得到的。仓库的命令行里没有直接提供这个开关的组合，需要查看 README 或自己改 `cli_utils.py` 的 eval 分支。

---

## 12. 读完 runner 后对改代码的提示

| 我们想做的事 | 要改 runner 的哪里 | 说明 |
|---|---|---|
| **分组退回**：掩码从 1 列变 G 列 | 第 263–264 行初始化、第 198–219 行翻转函数 | 例如 G = 2：每次迭代为每个环境随机抽一个子集（00、01、10、11），而不是简单翻转 |
| 训练时让"不可信组"的参数超出范围 | 不在 runner，在环境事件里；但 runner 需要在掩码变化时通知环境 | 类似 `adversary_update_sim` 的方式，把掩码写进事件参数 |
| **运行中途发生故障** | 主循环第 311–334 行 | 在某一步按概率触发"电机变弱/失效"事件；同时上下文要逐步更新（存储和 `self.context` 都要改） |
| 验证集按组定标 | 第 519–606 行 | `calculate_uncertainty_metric` 返回 [N, G]，分位数按组算，存 [G, 101] |
| 评估时记录每组 α | 第 628–707 行 | `alpha` 改为 [N, 1000, G]，这是论文里最直观的图："哪一组触发了退回" |
| 评估时中途加载荷（复现 Fig. 4 右） | 第 647 行的循环里，t = 500（10 s）时改质量 | 仓库没有这段代码，需要用 Isaac Lab 的接口在运行中修改刚体质量 |

---

## 13. 自测题

1. 训练默认一共多少次迭代？哪些属于 RL 阶段、哪些属于 finetune 阶段？依据是哪几行代码？
2. 用 4 个环境演示 GRAM 在前 3 次迭代里的鲁棒/自适应分配。一条完整轨迹里两种模式大约多久切换一次？
3. Separate Data 消融和 GRAM 在 runner 里的区别是什么？
4. 进入 finetune 时，runner 做了哪四件事？各自对应论文的哪句话？
5. `_update_observation_history` 在环境重置时做了什么？为什么？
6. 对抗者强度在第 4,999 次迭代后是多少？第 0 次迭代采样时有推力吗？
7. 验证集是怎样采集的？为什么要关掉对抗者？`alive` 掩码起什么作用？
8. 验证集采完后，β 和 λ 是在哪里算出来的？为什么同一次运行里紧接着评估会有问题？
9. 评估时，GRAM 的退回是靠 `robust_masks` 还是靠 α？为什么？
10. 日志里 `History loss` 在前 10,000 次迭代为什么一直是 0？`Value function loss` 在后 5,000 次为什么一直是 0？

<details>
<summary>参考答案</summary>

1. 15,000 次。it = 0–9,999 为 RL，it = 10,000–14,999 为 finetune。依据：第 275–277 行（`tot_iter = start + 10000 + 5000`，`finetune_start_iter = tot_iter − 5000`）和第 356–359 行。
2. 初始化 [0, 0, 1, 1]；迭代 0 前翻转为 [1, 1, 0, 0]；迭代 1 为 [0, 0, 1, 1]；迭代 2 为 [1, 1, 0, 0]。每 24 步（约 0.48 s）切换一次。
3. GRAM 每次迭代开始时翻转所有环境的掩码；Separate 设置 `robust_mask_reset_update=True`，只在环境回合重置时翻转该环境，所以一个回合只用一种模式（第 304–314 行）。另外验证集采集时 Separate 的两轮分别全自适应、全鲁棒。
4. ① `act_from_context=False`，改用学生采样（"Data collection uses the student policy"）；② 关闭对抗者（"We do not apply an adversary during the supervised learning phase"）；③ 冻结观测标准化；④ 保存 finetune 前的模型（第 282–302 行）。
5. 先把重置环境的历史全部清零，再滑动窗口放入新观测。因为旧回合的历史不能带入新回合，否则历史编码器会根据上一回合的运动来估计新回合的环境。
6. (4999 + 1) / 10000 = 0.5 m/s（每次推再乘 [0, 1] 随机数）。第 0 次迭代采样时强度是初始值 0，没有推力；强度在第 0 次 `update()` 之后才变为 0.0001。
7. 训练结束后用训练环境（ID）、学生策略、确定性动作、无推力，采两轮各 1000 步；默认两轮都按训练时的方式一半一半、每 24 步交替。关对抗者是为了让验证集是"干净的 ID 数据"，否则推力造成的高不确定性会被当作正常，β 定得过高。`alive` 保证只统计每个环境第一个回合存活期间的数据，排除摔倒过程和重置后的补零历史。
8. 在 `load()` 第 147 行调用 `set_uncertainty_params()` 时算出。`collect_validation_data` 只存了分位数，没有重新计算 β、λ，所以必须重新加载模型才生效。
9. 靠 α。GRAM 评估时 `act_inference_adapt=True`，`act_inference` 把 `robust_masks` 覆盖为全 0；同时 `history_epinet_apply_bias=True`，`encode_history` 里把 latent 乘以 α。
10. RL 阶段 `train_and_finetune=False`，`update()` 把 history_loss 设为 0（`gram_ppo.py:336-340`）。finetune 阶段只调用 `finetune()`，它从不计算价值损失，累加器保持 0（`gram_ppo.py:610-612`）。
</details>
