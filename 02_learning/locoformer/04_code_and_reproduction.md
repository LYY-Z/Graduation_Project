# 04 参考代码阅读与复现边界

本篇回答“上述机制在当前项目里由谁实现”。核对对象是本地参考仓库，核对日期2026-11-02，未执行训练、推理或仿真。

<a id="provenance"></a>
## 1. 首先确认代码来源

[本地仓库](../../03_code/locoformer/README.md)的Git origin指向lucidrains/locoformer，`pyproject.toml`作者为Phil Wang，版本0.4.0，仓库链接指向Codeberg；README标记wip。

核对提交：`79ce9d72d1137015e0212284f06656c83bb414e7`，工作区无未提交更改。这是第三方实现，包含论文之后的多种扩展，不能把所有类、损失和默认参数都归于LocoFormer原论文。

尤其要区分：论文跨大量程序化机器人训练；`train_microduck.py`是一个Microduck训练示例，不自动等于作者完整跨本体训练系统。

<a id="files"></a>
## 2. 先看这些文件，不要一开始逐行读所有模块

```text
03_code/locoformer/
├── README.md                使用示例与项目说明
├── pyproject.toml           Python要求、依赖与安装元数据
├── train_microduck.py       本手册主读入口：环境、采集、PPO调用、评估
├── train_gym.py             另一套环境与learn/dataloader调用路径
├── train_animal.py          其他实验入口
├── train_enwik8.py          序列任务入口
├── locoformer/
│   ├── __init__.py          包导出
│   └── locoformer.py        网络、缓存、GAE、PPO与扩展模块
└── tests/test_locoformer.py  功能测试与使用方式参考
```

建议顺序：`train()`默认值→模型构造→采集循环→`ppo()`→`forward()`→TransformerXL/Attention→再回看环境。

`train_microduck.py`头部有uv脚本依赖元数据，包括MuJoCo等；本地包通过editable路径引用。`pyproject.toml`的依赖清单与某个脚本所需的完整环境不一定相同。

<a id="config"></a>
## 3. 默认配置与实际模型对象

| 项目 | Microduck默认值 | 来源 |
|---|---:|---|
| 并行环境 | 12 | `train()`参数 |
| 每环境采集长度 | 256 | `steps_per_env` |
| 同批优化轮数 | 4 | `epochs` |
| 学习率 | 5e-4 | Adam |
| 内部维度 | 64 | dim |
| Transformer层数 | 1 | depth |
| 注意力头数 | 4 | heads |
| 每头维度 | 32 | dim_head |
| segment长度 | 16 | window_size |
| γ、λ | .99、.95 | GAE配置 |
| PPO裁剪ε | .2 | clip |
| 熵权重 | .002 | ent_coef |
| 动作分布 | Beta，unimodal=True | unembedder配置 |
| Critic | 默认32个区间，HLGaussLoss | 模型类默认值 |
| 优化器 | 一个Adam覆盖模型参数 | 入口构造 |

这些值来自代码默认值，命令参数和`smoke`会覆盖其中部分。`smoke=True`变成2个环境、32步、1轮优化等，不应继续按12×256×4解释。

模型构造中：

```python
model = Locoformer(
    embedder=dict(dim=dim, dim_state=venv.obs_dim),
    unembedder=dict(..., continuous_dist_type='beta', ...),
    transformer=dict(dim=dim, depth=depth, window_size=window_size, ...),
    policy_network=...,
    value_network=...,
    ...
)
optim = Adam(model.parameters(), lr=learning_rate)
```

字典被模型类转换成具体组件，MLP/Transformer等分配权重；优化器引用这些参数。创建模型没有完成训练；加载checkpoint则把保存的权重写到对应模块。

代码位置：[默认值](../../03_code/locoformer/train_microduck.py:588)、[模型与优化器](../../03_code/locoformer/train_microduck.py:645)。

<a id="environment"></a>
## 4. 环境输入与动作执行：比抽象论文图更具体

### 4.1 `observe()`拼接了什么

`MicroduckEnv.observe()`拼接投影重力、局部速度数组的前三项、关节位置相对home的偏差、关节速度、上一动作与二维command。

这些是数值向量拼接，不是相加。若对应关节维度为D，各项通常给出形状为`6 + 3D + 2`的观测；具体D由模型资产确定。速度分量的物理含义应按MuJoCo接口的空间速度排列核对，不能仅凭函数名自行把前三项叫线速度。

这也解释：`embed_past_action=False`只是不启用额外动作嵌入分支，观测本身仍包含`last_action`。

### 4.2 默认动作并非每一维直接等于最终关节角

策略先采样原生分布动作，保存它的log_prob，再重缩放为环境接口动作。入口接口范围为(-1.5,1.5)。

环境默认`cpg=True`：前一部分动作影响周期控制相关量，另一部分影响直接控制关节的偏置，并结合home控制与幅度限制。`cpg=False`时路径不同。

因此不能把Microduck默认示例描述成“网络每个维度都是某个关节的最终绝对角度”。论文统一关节目标是方法描述，这个环境还有特定控制结构。

动作进入MuJoCo控制与子步仿真，才形成实际身体状态。目标与实际不一致正是动力学响应的一部分。

### 4.3 并行环境怎样运行

`VecEnv`用spawn进程和Pipe管理各环境。每次把对应动作发给各worker，再收集观测、奖励、term、trunc、info。环境结束时该worker重置，入口继续获得新观测。

12是batch中相互独立的环境序列，不是把12台身体的历史相互混合。

代码：[观测](../../03_code/locoformer/train_microduck.py:212)、[动作处理](../../03_code/locoformer/train_microduck.py:261)、[VecEnv](../../03_code/locoformer/train_microduck.py:423)。

<a id="collection"></a>
## 5. 采集循环究竟调用谁

每次外层采集循环：

```python
stateful_fwd = model.get_stateful_forward(
    has_batch_dim=True, has_time_dim=False, inference_mode=True
)
```

这个包装器内部保留cache。输入`[B,D_obs]`时补上时间轴，变成`[B,1,D_obs]`，再调用`model.forward()`。

采集每一步：

```text
obs_t
→ stateful_fwd：网络前向并维护cache
→ unembedder.sample：抽取动作
→ log_prob：保存原生动作的旧密度信息
→ rescale_from_native：变成环境接口动作
→ venv.step：环境实际执行
→ 保存obs、act、logp、rew、val、done、ep_id
```

256次循环期间不执行Adam.step，参数保持不变。`no_grad()`表示不建立这段采集的梯度记录，不表示网络不计算或不更新缓存。

每个环境的done会使其ep_id递增。当前入口每批采集重新创建stateful包装器，缓存从空开始，这与“同一物理任务无限跨批次保留记忆”不同。

最后额外计算一个末端value，不额外执行环境动作；对未done的最后位置把bootstrap加入保存的reward副本。

代码：[采集](../../03_code/locoformer/train_microduck.py:692)、[末端处理与stack](../../03_code/locoformer/train_microduck.py:733)、[stateful包装器](../../03_code/locoformer/locoformer/locoformer.py:2373)。

<a id="shapes"></a>
## 6. 保存后与训练时的主要张量

设B=12、T=256、L=16、动作维D_a：

| 数据 | 大致形状 | 是否固定用于同批优化 |
|---|---|---|
| states | [B,T,D_obs] | 是 |
| actions | [B,T,D_a] | 是 |
| old log-prob | 逐动作维时[B,T,D_a] | 是 |
| rewards、old values、done | [B,T] | 是 |
| episode IDs | [B,T] | 是 |
| 每窗states | [B,L,D_obs]，末窗可短 | 同一保存数据的切片 |
| 当前动作logits | 由动作分布参数化决定 | 每轮重新算 |
| Critic raw logits | [B,L,32]，默认 | 每轮重新算 |
| 隐藏表示 | [B,L,64]，默认 | 每轮重新算 |

不要把[B,T]的整组观测误读成3072维单个观测。B和T是不同轴，loss会按有效时间位置归并。

<a id="ppo-functions"></a>
## 7. `ppo()`内部的精确顺序

1. 生成padding与done相关掩码，统计有效位置数N。
2. 用保存的reward、old value计算GAE与returns；再标准化优势。
3. 沿时间维把状态、动作、旧logp、优势、returns等同步split。
4. `cache=None`，依次处理各窗口。
5. 调用`forward(..., cache=cache, detach_cache=True, return_raw_value_logits=True)`。
6. 用当前logits计算**保存动作**的当前log_prob。
7. 用新旧log_prob之差取exp，算比例及Actor裁剪损失。
8. 默认逐动作维平均，再加入熵项；按有效位置求和并除以整批N。
9. `HLGaussLoss(value_logits, returns)`得到Critic损失，同样筛选和归一化。
10. 每窗对Actor+Critic损失执行backward，累积参数梯度。
11. 窗口循环结束后梯度限幅，Adam.step，再zero_grad。

旧缓存的detach发生在前向返回路径，不是在所有PPO更新结束后才补做。

标准clip分支默认启用；仓库还支持SPO、Delight PG和辅助目标等扩展。当前入口未启用的模块，不应加入正在解释的主流程。

代码：[GAE与分段](../../03_code/locoformer/locoformer/locoformer.py:1931)、[窗口前向](../../03_code/locoformer/locoformer/locoformer.py:2029)、[损失](../../03_code/locoformer/locoformer/locoformer.py:2042)、[更新](../../03_code/locoformer/locoformer/locoformer.py:2134)。

<a id="timeline"></a>
## 8. 一次采集到四次参数更新

```text
θ0采集12×256条名义记录 → 保存D

ppo(D)，第1轮：
16个窗口顺序计算，参数始终θ0
每窗backward累积梯度
末尾一次Adam.step → θ1

ppo(D)，第2轮：cache从空重建，θ1→θ2
ppo(D)，第3轮：cache从空重建，θ2→θ3
ppo(D)，第4轮：cache从空重建，θ3→θ4

θ4采集新数据D2，之后重复
```

一批数据在四轮中被重新用于训练，但环境没有重复执行这批动作。每轮名义处理3072个位置，实际损失数取决于有效掩码；16个窗口不等于16次参数更新。

如果使用`learn()`路径，它会通过dataloader选取mini-batch，再调用`ppo()`，一个epoch内可能有多次参数更新。Microduck直接调用`ppo()`，不能把另一入口的batch_size=16又叠加过来解释。

<a id="forward-functions"></a>
## 9. `forward()`内部的调用地图

```text
Locoformer.forward
  ├─ StateEmbedder：原始观测到token
  ├─ 可选过去动作嵌入：本入口不额外启用
  ├─ TransformerXL.forward
  │    ├─ 取各层缓存与Episode信息
  │    ├─ Attention：QKV、位置机制、掩码、组合
  │    ├─ FFN及残差/归一化等
  │    └─ 更新并返回TransformerMemory
  ├─ policy_network + unembedder：动作分布参数
  ├─ to_value_pred：Critic logits，必要时读出标量值
  └─ 若detach_cache=True：只detach返回缓存
```

输入当前段长度加上当前窗口偏移不能超过window_size。训练每次传入当前窗口，采集包装器每次传1步；部分最后窗口可短。

模型中recurrent_cache、门控、可选GRU、MemoryMLP等属于当前第三方实现的具体组织，不应逐项说成原论文公式（2）已经规定的全部结构。

<a id="audit"></a>
## 10. 不能混淆的论文与代码差异

| 项目 | 论文 | 当前Microduck入口 |
|---|---|---|
| 任务空间 | 程序化多本体与广泛随机化 | 特定Microduck示例环境 |
| 历史协议 | 同任务多Trial可共享历史 | done递增ep_id，默认隔离环境episode |
| 网络示例 | 6层L128用于说明记忆范围 | 默认1层L16、dim64 |
| 动作 | 统一关节空间目标位置 | Beta采样后接环境特定CPG/直接控制路径 |
| Critic/PPO详细配置 | 未完整公开 | 有HLGauss、逐维裁剪等具体选择 |
| 恢复训练 | 论文未给完整公开流程 | 加载模型及统计，未保存完整优化器/RNG状态 |

`use_cross_episode_attention=True`还要求额外Actor Transformer条件，不能只开一个布尔值就声称复现了论文全部跨Trial协议。`train_gym.py`也有人工构造跨trial样本的示例，不等同于作者任务生成器。

### 10.1 掩码和终止语义要单独检查

源码`gae_mask=padding_mask & ~done`既影响GAE门控，也用作损失位置筛选。终止位置本身被排除，奖励仍可能通过递推进入此前优势。

一般PPO的bootstrap掩码与“这个动作是否参与训练”的loss掩码不是必须相同；term与trunc也不总应同样处理。这里记录实现行为并提出核验点，没有运行对照实验，不能把它写成已经确认的错误修复。

完全无效窗口会跳过，其缓存延续效果也应在后续复现测试中确认。

### 10.2 checkpoint不等于完整训练快照

当前入口加载`ckpt['model']`到事先创建的网络，并恢复部分更新计数与最佳评估统计。保存内容不包含Adam状态、完整随机数状态与全部环境状态，因此不是精确恢复同一随机训练轨迹。

加载时网络维度与分布配置需匹配。函数名或checkpoint文件名不能代替配置核对。

代码：[加载](../../03_code/locoformer/train_microduck.py:672)、[保存](../../03_code/locoformer/train_microduck.py:783)。

<a id="reproduction"></a>
## 11. 后续复现应该逐层证明什么

本次未运行这些阶段，以下为后续计划：

1. 固定本地Git提交、Python/PyTorch及依赖版本，确认模型资产来源。
2. 在独立环境验证模型可创建、观察和动作形状正确。
3. 检查因果掩码、Episode隔离、部分segment、缓存边界。
4. 用可手算数据核验GAE、终止/截断、loss mask、逐维clip及梯度累计。
5. 做短仿真采集与一次更新，检查旧概率固定、梯度有限、参数确实改变。
6. 检查多轮优化与新批次采集的边界，再评估步态与任务结果。
7. 若目标是论文复现，再获得/重建程序化多本体任务分布和多Trial协议，做正式基线与统计。

“脚本能启动”“有非零梯度”“机器人能走”“复现论文跨本体结果”是不同层级，不能互相代替。

README的`uv run train_microduck.py`是训练命令，不是只读查看。执行会准备依赖或资产、创建输出、可能加载已有checkpoint并开始仿真，因此阅读阶段不应随意运行。

## 12. 与论文汇报衔接

主讲时使用论文方法与证据；代码数字放在补充页并标注第三方。报告应能分别回答：作者做了什么、当前代码实现了什么、本次实际验证了什么。

返回：[总路线](README.md) · [问题索引](05_questions_and_review.md) · [PPO原理](03_reinforcement_learning_and_ppo.md)。
