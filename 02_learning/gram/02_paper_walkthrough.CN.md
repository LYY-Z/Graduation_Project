# 02 论文逐节精读

原文：`01_papers/research/GRAM.pdf`（MERL 技术报告版 TR2026-057，内容与 RA-L 正式版一致）。下文"p.x"指论文印刷页码。

**怎么用这份文档**：
1. 每节先看"**这一节在说什么（大白话）**"，建立直觉；
2. 再看公式的逐符号解释和**数值代入例子**，拿笔算一遍；
3. 然后打开 PDF 对照原文读一遍，重点看下面引用的英文原句；
4. 每节末尾的"**读论文时应该问自己的问题**"，试着自己先回答，再看答案。

前置概念（MDP、PPO、教师—学生、epinet 等）如果还不熟，先读 [01 前置知识](01_background.CN.md)。

标注约定：
- **【原文】** 作者写的事实，通常附英文原句和中文翻译；
- **【解读】** 我们对原文的解释；
- **【注意】** 容易被问到、或原文没说清的地方；
- **【依据代码】** 论文没写、从官方代码读出来的。

---

## 0. 基本信息

**这一节在说什么（大白话）**：这篇论文是谁写的、发在哪、什么时候。见老师时，这些信息要张口就来。

| 项 | 内容 |
|---|---|
| 题目 | GRAM: Generalization in Deep RL with a Robust Adaptation Module |
| 题目翻译 | GRAM：带鲁棒适应模块的深度强化学习泛化 |
| 发表 | IEEE Robotics and Automation Letters (RA-L)，vol.11, no.2, pp.2218–2225, 2026；DOI 10.1109/LRA.2025.3641155 |
| 时间线 | 2025-08-14 投稿，2025-10-24 修改，2025-11-20 录用；编辑 Jens Kober |
| 作者 | James Queeney（一作，MERL / MIT）、Xiaoyi Cai（MIT）、Alexander Schperberg、Radu Corcodel（MERL）、Mouhacine Benosman（Amazon Robotics，原 MERL）、Jonathan P. How（MIT） |
| 资深作者 | Benosman 与 How 并列 |
| 代码 | https://github.com/merlresearch/gram（训练与评估代码，无权重） |
| 平台 | Unitree Go2 四足（纯腿，12 个关节） |

**RA-L 是什么级别**：IEEE 机器人与自动化领域的主流期刊，以短文（6–8 页）为主，审稿周期快。很多 RA-L 论文会同时在 ICRA / IROS 会议上宣讲。本文从投稿到录用约 3 个月。

**作者背景（老师可能问"这是谁的工作"）**：
- **Benosman**：MERL 资深研究员，长期做**自适应控制、学习型控制**，控制背景深厚。这也解释了论文为什么把问题表述为"适应与鲁棒的结合"。
- **Jonathan How**：MIT 航空航天系教授，做多智能体规划、鲁棒控制和学习。
- **Queeney**：之前做分布鲁棒、安全强化学习（参考文献 [24][26] 都是他的）。

所以这是一篇**有控制背景的团队、用学习方法做"适应+鲁棒"**的工作，正好对应老师说的"老问题、新方法"。

---

## 1. 摘要（Abstract）

**这一节在说什么（大白话）**：强化学习训练出来的机器人，在见过的情况下要做得好，在没见过的情况下也不能崩。我们做了一个"一个网络两种本事"的方法，在 Go2 上仿真和实机都验证了。

**【原文】** "The reliable deployment of deep reinforcement learning in real-world settings requires the ability to generalize across a variety of conditions, including both in-distribution scenarios seen during training as well as novel out-of-distribution scenarios."

> 翻译：要在真实世界可靠地部署深度强化学习，必须能在各种条件下泛化，既包括训练时见过的分布内场景，也包括新的、没见过的分布外场景。

**【原文】** "In this work, we present a framework for dynamics generalization in deep reinforcement learning that unifies these two distinct types of generalization within a single architecture."

> 翻译：本文提出一个深度强化学习中的动力学泛化框架，在**单一架构**里统一这两种不同类型的泛化。

两个核心部件：
1. 一个**鲁棒适应模块**（robust adaptation module），能识别并应对 ID 和 OOD 的环境动力学；
2. 一个**联合训练流程**（joint training pipeline），同时追求 ID 适应和 OOD 鲁棒。

**【解读】** 一句话：**一个网络，平时像自适应控制那样针对性调整，没把握时像鲁棒控制那样保守。**

**"dynamics generalization"（动力学泛化）是什么意思？** 任务不变（都是"按指令速度走"），变的是机器人和环境的**物理特性**（重量、摩擦、电机力气、地形）。泛化到不同的物理特性，叫动力学泛化。区别于"任务泛化"（学会新任务）和"视觉泛化"（看到新画面）。

---

## 2. 引言（Section I）与 Fig. 1

**这一节在说什么（大白话）**：现在有两派方法，一派会"看情况调整"但遇到没见过的就犯傻，一派"一直很小心"但平时太慢。我们要把两派的优点合在一起。

### 2.1 问题背景

**【原文】** "Contextual RL techniques [1] such as teacher-student training [2]–[4] learn to identify and adapt to the current environment dynamics to achieve the best performance, but this adaptation is only reliable for the range of in-distribution (ID) scenarios seen during training."

> 翻译：情境强化学习技术（如教师—学生训练）学会识别并适应当前的环境动力学，以获得最好的性能，但这种适应**只在训练时见过的分布内场景范围内可靠**。

**【原文】** "Robust RL methods [5], [6] such as adversarial training [7], on the other hand, maximize the worst-case performance across a range of possible environment dynamics, providing generalization to out-of-distribution (OOD) scenarios at the cost of conservative performance in ID environments."

> 翻译：另一方面，鲁棒强化学习方法（如对抗训练）最大化一系列可能环境动力学下的最坏情况性能，能泛化到分布外场景，**代价是在分布内环境中表现保守**。

### 2.2 Fig. 1 画了什么

根据图注（p.1）：
- 图的主题："GRAM generalizes to both ID and OOD environment dynamics at deployment time with a single unified architecture."（GRAM 用单一统一架构，在部署时同时泛化到 ID 和 OOD 环境动力学）
- 图里表达的机制："GRAM introduces a robust adaptation module that quantifies uncertainty about the deployment environment using a recent history of observations, and biases latent context estimates towards a special robust latent feature (z_rob) when uncertainty is high."
> 翻译：GRAM 引入一个鲁棒适应模块，用最近的观测历史量化对部署环境的不确定性，**在不确定性高时把隐变量估计偏向一个特殊的鲁棒隐变量 z_rob**。

（图的具体画面请对照 PDF 第 1 页，这里根据图注描述。）

### 2.3 三个贡献（p.1）

1. **鲁棒适应模块**（Section IV）：用 **epistemic neural network [8]** 给情境 RL 加上对环境的不确定性度量；
2. **联合训练流程**（Section V）：把教师—学生（为了 ID 适应）和对抗 RL（为了 OOD 鲁棒）结合，训练**一个统一的策略**；
3. **实验**：Go2 仿真（Section VII）+ 实机（Section VIII）。

**【注意】** 贡献 1 的"新"不在 epinet 本身（epinet 是 Osband 2023 的），而在**把认知不确定性用作"适应 ↔ 鲁棒"的切换信号**，并且把鲁棒模式**嵌入同一个隐空间**（z_rob）。

> **读论文时应该问自己的问题**
> - Q：作者说的"两类方法"真的是对立的吗？有没有已有工作同时做两件事？
> - A：有一些，比如相关工作里提到的"按不确定性切换到恢复策略"（[31]），但那是两个独立策略硬切换。GRAM 的区别是一个网络、软混合。消融里的 Modular 就是在模拟那种做法。
> - Q：贡献里哪些是新的，哪些是借来的？
> - A：教师—学生、对抗训练、epinet 都是借来的；新的是"用不确定性混合"+"z_rob 嵌入隐空间"+"联合训练与交替分配"。

---

## 3. 相关工作（Section II）

**这一节在说什么（大白话）**：别人在做什么、哪里不够。作者把相关工作分成"会适应的""会鲁棒的""会切换的"三类，然后说"我们是把切换放进了会适应的那一类里"。

| 类别 | 代表 | 作者认为的不足 |
|---|---|---|
| 情境 RL | 教师—学生 [2] Lee 2020、[3] RMA、[4] Margolis 2024；自监督推断上下文 [11] RL2AC、[12] HIMLoco；通用 RL 中的上下文推断 [13]–[20] | 只针对 ID 训练，OOD 泛化依赖训练分布 |
| 鲁棒 RL | 对抗推力 [7][21]；扰动动作 [22]、观测 [23]、转移 [24]–[26] | 牺牲 ID 性能 |
| 多策略 / 多模式 | 恢复策略切换 [31] ABS；从有限行为中选择 [30] Walk These Ways、[32] | 多个策略之间切换 |

**【原文】** "All of these methods are designed to adapt across the range of ID contexts seen during training, but are not specifically trained to handle OOD contexts with different environment dynamics. As a result, their ability to generalize is sensitive to the distribution of ID training contexts..."

> 翻译：这些方法都是为了在训练见过的 ID 上下文范围内做适应而设计的，并没有专门训练去处理动力学不同的 OOD 上下文。因此，它们的泛化能力**对训练时 ID 上下文的分布很敏感**。

**【原文】** "Contextual RL can also be viewed as learning a collection of policies for ID adaptation, and our robust adaptation module extends this approach to incorporate a mode for robust OOD generalization as well."

> 翻译：情境 RL 也可以看成学习了一族用于 ID 适应的策略，我们的鲁棒适应模块扩展了这一做法，**再加入一个用于鲁棒 OOD 泛化的模式**。

**【解读】** 这个视角很重要：策略 π(a∣s, z) 对每个不同的 z 都是一个不同的"子策略"，所以情境 RL 本身就是"一族策略"。GRAM 只是在这族策略里**专门训练好其中一个点（z=0）当作鲁棒模式**。

**【注意】** 相关工作里**没有**讨论：
- 控制领域的鲁棒自适应控制（σ-修正、L1 自适应等）；
- 按因素分解的上下文估计（如 HIMLoco 的显式速度估计 + 隐式表示、按物理量分组的工作）；
- 执行器故障 / 容错。

这几块正是我们可以切入、也是老师可能追问的地方。

> **读论文时应该问自己的问题**
> - Q：引用的情境 RL 基线里最新的是哪年？
> - A：Margolis 2024（IJRR）和 HIMLoco（ICLR 2024）。但实验对比的"情境 RL"是一般的教师—学生做法，没有直接跑 HIMLoco。

---

## 4. 问题建模（Section III）

**这一节在说什么（大白话）**：用数学语言把问题说清楚。"环境参数 c"决定机器人怎么动；训练时能看到 c，部署时看不到；训练只覆盖一部分 c，但希望所有 c 都表现好。

### 4.1 上下文 RL（式 1）

$$J(\pi, c) = \mathbb{E}_{\tau\sim(\pi,c)}\Big[\sum_{t=0}^{\infty}\gamma^t r(s_t,a_t)\Big]$$

**逐符号解释**：

| 符号 | 读法 | 含义 |
|---|---|---|
| J(π, c) | "J 派 c" | 策略 π 在上下文 c 下的表现分数 |
| 𝔼 | 期望 | 对很多条轨迹求平均（因为动作和环境有随机性） |
| τ ~ (π, c) | τ 服从 | 轨迹 τ 是用策略 π 在上下文 c 下跑出来的 |
| γᵗ | gamma 的 t 次方 | 第 t 步奖励的折扣 |
| r(sₜ, aₜ) | | 第 t 步的奖励 |

**数值例子**：γ = 0.99，假设机器狗每一步都拿到 0.8 分，跑满 1000 步：

J ≈ 0.8 × (1 − 0.99¹⁰⁰⁰) / (1 − 0.99) ≈ 0.8 × 100 = **80**

（等比数列求和；0.99¹⁰⁰⁰ ≈ 0.00004，可以忽略。）如果在第 200 步摔倒结束，后面的奖励全没了，J 会小很多。所以"不摔倒"本身就很值钱。

**MDP 的定义**：M_c = (S, A, p_c, r, ρ₀, γ)。其中只有 **p_c 带下标 c**：
- **只有转移依赖 c**："varying dynamics"（动力学变化）；
- **奖励 r 不变**："same task"（任务相同）。

### 4.2 问题陈述（式 2）

**【原文】** "We assume that the context is available as privileged information during training, but is not available for deployment."

> 翻译：我们假设训练时上下文作为特权信息可得，但部署时不可得。

- 训练只能覆盖 ID 子集 C_ID ⊂ C；
- OOD 集 C_OOD = C \ C_ID（"\"是集合差，表示"在 C 里但不在 C_ID 里"）；
- 目标：

$$\max_\pi J(\pi,c),\quad \forall c\in C = C_{ID}\cup C_{OOD}$$

> 读法：找一个策略 π，使得对所有 c（不管见没见过），J 都尽量大。

**【原文】** "adaptive ID performance and robust OOD performance represent two distinct types of generalization with different objectives, making it challenging to achieve both with a single policy."

> 翻译：自适应的 ID 性能和鲁棒的 OOD 性能代表两种目标不同的泛化，**很难用一个策略同时做到**。

**为什么难？** 举例：
- 在 ID 的"冰面"情况下，最好的走法是小碎步；在 ID 的"粗糙地"情况下，最好的走法是大步。适应型策略会根据估计切换。
- 但遇到 OOD 时，适应型策略的估计可能错得离谱，比如在泡沫上估计成"粗糙地"，于是大步走，摔了。
- 鲁棒型策略不管什么情况都用折中偏保守的走法，在冰面和粗糙地上都不是最好，但在泡沫上也不至于摔。

**【注意】** 式 (2) 是"对所有 c 都最大化"，严格说是一个**多目标**问题，没有唯一解。论文没有给出这个多目标的具体权衡方式，而是用"ID 上做适应、OOD 上做鲁棒"来近似。老师若问"式 2 怎么优化"，答：它不是直接优化的目标，而是设计目标；实际优化的是式 (10)。

### 4.3 教师—学生训练（式 3、式 4）

**教师阶段（式 3）**：

$$L_{RL} = \mathbb{E}_{c\sim C_{ID}}\big[L_\pi(c) + L_V(c)\big]$$

| 符号 | 含义 |
|---|---|
| L_RL | 强化学习的总损失 |
| c ~ C_ID | 从 ID 范围里随机抽上下文 |
| L_π(c) | PPO 的策略损失（让好动作概率变大） |
| L_V(c) | PPO 的价值损失（让 Critic 估得准） |

- 上下文编码器 f：C → Z = ℝᵈ（d = 8），z_t = f(c_t)；
- 策略 π(a∣s, z)，价值 V(s, z)；
- **f、π、V 一起用 PPO 训练**。注意 f 不是单独训练的，它的训练信号来自 RL 损失，即"z 怎么编码，策略才能拿高分"。

**学生阶段（式 4）**：

$$L_{enc} = \mathbb{E}_{c\sim C_{ID}}\ \mathbb{E}_{\tau\sim(\pi,c)}\big[\ \|f(c_t) - \phi(h_t)\|^2\ \big]$$

| 符号 | 含义 |
|---|---|
| h_t | 历史 (s_{t−H}, a_{t−H}, …, s_t)，H = 16 |
| φ(h_t) | 适应模块从历史估计出的 8 维 ẑ |
| f(c_t) | 教师的"标准答案" z |
| ‖·‖² | 欧氏距离的平方，即各维差的平方和 |

**数值例子**（为了好算，用 3 维代替 8 维）：
- 标准答案 f(c) = [0.5, −0.2, 0.1]
- 学生估计 φ(h) = [0.4, −0.1, 0.1]
- 差 = [0.1, −0.1, 0]，平方和 = 0.01 + 0.01 + 0 = **0.02**

训练就是让这个数在大量样本上平均尽量小。

**【原文】** "where expectation is taken with respect to trajectories sampled using the student policy in ID contexts"

> 翻译：期望是对**用学生策略**在 ID 上下文中采样的轨迹求的。

**为什么用学生策略采数据，不用教师？** 部署时机器人是按学生的估计在走，走出来的历史分布和教师走出来的不一样。用学生自己采的数据训练，训练分布才和部署分布一致。这和模仿学习里的 DAgger 思想类似。

**【原文】** "This training represents a form of implicit system identification across ID contexts."

> 翻译：这种训练是一种在 ID 上下文上的**隐式系统辨识**。

> **读论文时应该问自己的问题**
> - Q：f 输出的 8 维 z，每一维有物理含义吗？
> - A：没有。f 是普通神经网络，训练信号只有"让策略拿高分"，8 维 z 是混在一起的压缩表示。这一点对我们的"分组"改进很关键：如果想按物理因素分开判断，首先要让 z 分块。

---

## 5. 鲁棒适应模块（Section IV）与 Fig. 2——核心

**这一节在说什么（大白话）**：普通学生模块只给一个估计，不管自己有没有把握。GRAM 让学生模块"多答几次"，答案一致说明有把握，就用这个估计；答案很乱说明没把握，就把估计往 0 拉，0 代表"按最保守的方式走"。

### 5.1 动机

**【原文】** "The learned adaptation module φ is trained to identify ID contexts from history, so its output ẑ_t = φ(h_t) and resulting policy π(a_t | s_t, ẑ_t) are only reliable for the distribution of ID history inputs h_t that were observed during training."

> 翻译：学到的适应模块 φ 是被训练来从历史中识别 ID 上下文的，所以它的输出 ẑ 以及由此得到的策略，**只对训练中观察到的那类 ID 历史输入可靠**。

**【解读】** 普通 RMA 的问题不是"估不准"，而是"**估不准时自己不知道**"。

### 5.2 Epistemic 网络结构（式 5）

$$\phi(h_t, \varepsilon) = \phi_{base}(h_t) + \phi_{epi}(\tilde h_t, \varepsilon)$$

| 符号 | 含义 | GRAM 中的设置 |
|---|---|---|
| φ_base(h_t) | 普通的适应网络，主估计 | MLP 512-256-128，输出 8 维 |
| φ_epi | 小网络，制造"分歧" | MLP 16-16 |
| ε | 随机输入，ε ~ N(0, I) | m = 8 维 |
| h̃_t | h_t 拼接 φ_base 最后一个隐藏层的输出，**梯度截断** | — |

**【原文】** "...and h̃_t is the concatenation of h_t and the output from the last hidden layer of φ_base with gradients stopped as in [8]."

> 翻译：h̃ 是 h_t 与 φ_base 最后一个隐藏层输出的拼接，并按 [8] 的做法截断梯度。

**"梯度截断"是什么意思**：训练 epinet 时，误差不往 base 网络传。这样 base 网络只负责"估得准"，epinet 只负责"表达不确定性"，两者互不干扰。

### 5.3 均值与方差（式 6、式 7）

$$\hat\mu(h_t) = \frac1N\sum_{i=1}^N \phi(h_t,\varepsilon^{(i)}),\qquad \hat\sigma^2(h_t) = \frac{1}{N-1}\sum_{i=1}^N\big(\phi(h_t,\varepsilon^{(i)}) - \hat\mu(h_t)\big)^2$$

**【原文】** "where all operations are performed per-dimension."（所有运算都逐维进行。）

- 同一个 h_t，采 N = 8 个随机 ε，得到 8 个 8 维估计；
- **逐维**算均值和方差：μ̂ 和 σ̂² 都是 8 维向量；
- 之后用的"总方差" ‖σ̂(h_t)‖² 是 8 维方差**求和成一个标量**。

**数值例子：手算一维的均值和方差**

**情况 A：见过的历史**。隐变量第 1 维，8 个样本：
0.42, 0.45, 0.40, 0.47, 0.43, 0.44, 0.41, 0.46

- 均值 μ̂ = 3.48 / 8 = **0.435**
- 偏差：−0.015, +0.015, −0.035, +0.035, −0.005, +0.005, −0.025, +0.025
- 偏差平方和 = 0.000225×2 + 0.001225×2 + 0.000025×2 + 0.000625×2 = 0.0042
- 方差 σ̂² = 0.0042 / 7 = **0.0006**

**情况 B：没见过的历史**。同一维，8 个样本：
0.1, 0.9, −0.3, 0.6, 0.2, 1.1, −0.5, 0.4

- 均值 μ̂ = 2.5 / 8 = **0.3125**
- 偏差平方和 ≈ 0.045 + 0.345 + 0.375 + 0.083 + 0.013 + 0.620 + 0.660 + 0.008 ≈ 2.149
- 方差 σ̂² = 2.149 / 7 ≈ **0.307**

相差约 500 倍。

**"总方差"怎么算**：假设 8 维的方差分别是 [0.0006, 0.0010, 0.0004, 0.307, 0.0008, 0.0005, 0.0007, 0.0009]，那么

‖σ̂‖² = 0.0006 + 0.0010 + … + 0.0009 ≈ **0.312**

**【注意】这个"求和成标量"就是我们改进的切入点**：上面这个例子里，只有第 4 维在"乱"，其他 7 维都很有把握。但求和以后只剩一个 0.312，**看不出是哪一维在乱**。后面 α 也只能统一地缩小全部 8 维。

### 5.4 训练 epinet（式 8）

$$L^{GRAM}_{enc} = \mathbb{E}_{\varepsilon\sim q}\ \mathbb{E}_{c\sim C_{ID}}\ \mathbb{E}_{\tau}\big[\ \|f(c_t) - \phi(h_t,\varepsilon)\|^2\ \big]$$

- 和式 4 的区别只有一处：多了 𝔼_ε，即**对每个随机输入 ε，估计都要接近 f(c)**；
- 结果：在训练见过的历史上，不同 ε 的输出被拉到一起（都靠近 f(c)），方差小；没见过的历史上没有这个约束，方差大。

**【原文】** "By doing so, the total variance of the latent feature estimates ‖σ̂(h_t)‖² will be small over the distribution of history inputs h_t that were seen during training (i.e., trajectories sampled from ID contexts), but not for histories in OOD contexts with different dynamics not seen during training."

> 翻译：这样一来，隐变量估计的总方差在训练中见过的历史输入上会很小，而在训练中没见过的、动力学不同的 OOD 上下文的历史上则不会小。

**【注意】** 这句话是**经验性的期望**，不是保证。epinet 对"没见过"的敏感程度取决于先验网络、网络容量等，论文没有给理论保证。

### 5.5 GRAM 的输出（式 9）——全文最重要的公式

$$\phi_{GRAM}(h_t) = (1-\alpha_t)\, z_{rob} + \alpha_t\,\hat\mu(h_t)$$
$$\alpha_t = \exp\!\big(-\lambda\,(\|\hat\sigma(h_t)\|^2 - \beta)^+\big)$$

**逐符号解释**：

| 符号 | 含义 | 取值 |
|---|---|---|
| φ_GRAM(h_t) | 最终给策略的隐变量 | 8 维 |
| z_rob | 鲁棒隐变量，"我不知道环境是什么" | **0 向量**（0_d） |
| μ̂ | 数据驱动的环境估计 | epinet 8 个样本的均值 |
| α_t | 可信度，∈ [0, 1] | 不确定性低 → 1，高 → 0 |
| ‖σ̂‖² | 总不确定性（标量） | 见 5.3 |
| β（shift，平移） | 不确定性的"容忍阈值" | 验证集上 ‖σ̂‖² 的 0.90 分位数 |
| λ（scale，缩放） | 衰减速度 | 使 0.99 分位数处 α = 0.01 |
| (x)⁺ | max(x, 0) | 不确定性低于 β 时括号里是 0，α 恰好等于 1 |

**【原文】** "where (·)⁺ = max(·, 0) and α_t ∈ [0, 1], with α_t ≈ 1 when uncertainty is low and α_t ≈ 0 when uncertainty is high."

> 翻译：其中 (·)⁺ = max(·, 0)，α ∈ [0, 1]；不确定性低时 α ≈ 1，高时 α ≈ 0。

**λ 的推导**（论文没写出，按定义推）：设 q₉₀、q₉₉ 为验证集分位数，令 β = q₉₀，要求 α(q₉₉) = 0.01：

exp(−λ(q₉₉ − q₉₀)) = 0.01 → λ(q₉₉ − q₉₀) = −ln 0.01 = 4.605

$$\lambda = \frac{4.605}{q_{99}-q_{90}}$$

**数值代入：算一条 α 曲线**

假设验证集上 q₉₀ = 2.0，q₉₉ = 4.0（这两个数是为了讲解编的，不是论文的值）。则：
- β = 2.0
- λ = 4.605 / (4.0 − 2.0) ≈ 2.30

不同不确定性下的 α：

| 不确定性 ‖σ̂‖² | ‖σ̂‖² − β | (·)⁺ | λ × (·)⁺ | α = exp(−…) | 含义 |
|---|---|---|---|---|---|
| 0.5 | −1.5 | 0 | 0 | **1.000** | 完全相信估计 |
| 2.0 | 0 | 0 | 0 | **1.000** | 刚到阈值，仍完全相信 |
| 2.5 | 0.5 | 0.5 | 1.15 | **0.316** | 只保留约三成 |
| 3.0 | 1.0 | 1.0 | 2.30 | **0.100** | 只保留一成 |
| 3.5 | 1.5 | 1.5 | 3.45 | **0.032** | 基本退回 |
| 4.0 | 2.0 | 2.0 | 4.61 | **0.010** | 按设计，q₉₉ 处 α = 0.01 |
| 5.0 | 3.0 | 3.0 | 6.91 | **0.001** | 完全退回 |

**文字版 α 曲线**：

```
α
1.0 ┤■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
    │                                         ■
0.5 ┤                                          ■
    │                                           ■■
0.1 ┤                                             ■■■
0.0 ┤                                                ■■■■■■■■■■■■■■■
    └──────────────────────────────────────────┬────┬────┬────┬────► 不确定性
    0                                          2.0  2.5  3.0  4.0
                                               β              q99
```

**看出什么**：
1. 不确定性在 β 以下时，α 是**平的 1**：正常波动不会触发退回；
2. 过了 β 之后，α **下降得非常快**：在这个例子里，从 2.0 到 3.0 就从 1 掉到 0.1；
3. 所以 GRAM 的行为接近"**带平滑过渡的开关**"。

**混合后的隐变量**：假设 μ̂ = [0.8, −0.4, …]，α = 0.316，则

φ_GRAM = 0.316 × [0.8, −0.4, …] + 0.684 × [0, 0, …] = [0.253, −0.126, …]

估计被"缩小"到原来的约三成，往 0 靠拢。

**【原文】为什么叫"证据"**："This formulation is motivated by the posterior predictive mean in evidential deep learning [34], where z_rob represents a robust prior, μ̂(h_t) is a data-driven estimate, and α_t is the normalized evidence."

> 翻译：这个公式受证据深度学习中**后验预测均值**的启发：z_rob 代表一个鲁棒的先验，μ̂ 是数据驱动的估计，α 是归一化的证据量。

**【原文】为什么要 β 和 λ**："We include a scale parameter λ and shift parameter β to allow for easy finetuning of α_t based on the output magnitude of the trained epinet in ID contexts..."

> 翻译：我们加入缩放参数 λ 和平移参数 β，以便根据训练好的 epinet 在 ID 情况下的输出量级，方便地微调 α。

**【解读】** epinet 输出的方差绝对大小没有意义（取决于网络初始化等），只有和"训练分布内的典型值"相比才有意义。β、λ 就是用来做这个"相对化"的。

### 5.6 为什么 z_rob = 0 是巧妙的设计

**【原文】** "By defining a special robust latent feature z_rob, we incorporate the failure mode of OOD dynamics directly into the existing adaptation framework as a single instance in latent feature space."

> 翻译：通过定义一个特殊的鲁棒隐变量 z_rob，我们把"OOD 动力学"这种失效模式直接纳入现有的适应框架，**作为隐空间中的一个点**。

**【原文】** "Note that the privileged context encoding z_t = f(c_t) begins training near z_rob = 0_d for a randomly initialized context encoder, and the RL loss L_RL in (3) incentivizes z_t to move away from z_rob as needed to achieve adaptive performance."

> 翻译：注意，随机初始化的上下文编码器输出的 z 在训练开始时就接近 z_rob = 0，RL 损失会促使 z **在需要适应时**离开 z_rob。

**【解读】** 三层意思：
1. **鲁棒模式只是隐空间里的一个点**，不需要单独的鲁棒网络。同一个策略 π(a∣s, z)：z = 估计值时是适应模式，z = 0 时是鲁棒模式。
2. **0 是一个"自然"的中心点**：上下文编码器最后一层初始化增益很小（代码里 1e-4），所以训练初期所有 z 都接近 0；训练中 z 只在"有必要适应"时才离开 0。
3. **混合 (1−α)·0 + α·μ̂ = α·μ̂**：就是把估计往原点"缩"，有点像统计里的**收缩估计**，也像鲁棒自适应控制里的 **σ-修正**（参数估计向标称值泄漏）。

**比喻**：一台收音机，旋钮在中间（0）是"自动保守模式"，往各个方向拧代表不同路况的"专门模式"。听不清信号时，就把旋钮往中间拧。

**【注意】** 中间值（0 < α < 1）对应的 α·μ̂ 是隐空间里 0 和 μ̂ 之间的一个点。**训练时策略从没见过这些"缩小版"的 z**（训练时要么是 f(c)，要么是 0）。为什么中间值也能产生合理行为？论文没有直接讨论，隐含的假设是隐空间足够平滑。这是一个可以追问的点。

### 5.7 Fig. 2 画了什么

根据图注（p.3）：
- **上半部分**："Epistemic neural network φ outputs a sample mean and variance of latent feature estimates for a history h_t, which are used to calculate φ_GRAM in (9)."
> 翻译：认知神经网络对一段历史输出隐变量估计的样本均值和方差，用于按式 (9) 计算 φ_GRAM。
  → 即：历史 → epinet（多个 ε）→ 一团点 → 算均值和方差 → 代入式 9。
- **下半部分**："In ID contexts, variance of latent feature estimates will be low and φ_GRAM will be close to the mean estimate. In OOD contexts with different environment dynamics, variance will be high and φ_GRAM will output an estimate close to z_rob."
> 翻译：在 ID 情况下，估计的方差低，φ_GRAM 接近均值估计；在动力学不同的 OOD 情况下，方差高，φ_GRAM 输出接近 z_rob 的估计。
  → 即：ID 时那团点很集中、输出落在点团中心；OOD 时点团很散、输出被拉到原点附近。

> **读论文时应该问自己的问题**
> - Q：如果 epinet 在某个 OOD 情况下**方差也很小**（"自信地错了"），会怎样？
> - A：α 仍是 1，GRAM 就退化成普通情境 RL，同样会犯错。论文没有讨论 epinet 漏检的情况。
> - Q：不确定性是标量，那么"只有一部分 OOD"时会怎样？
> - A：整个隐变量一起缩小，其他还准确的信息也被丢掉。这是我们的改进点。

---

## 6. 训练（Section V）与 Fig. 3、Alg. 1

**这一节在说什么（大白话）**：上面讲的是"部署时怎么用"。这一节讲"训练时怎么让一个网络同时学会两种本事"：把几千个仿真环境分成两组，一组正常练（看得到真实路况），一组练"在被人推的情况下、不知道路况也要走稳"，每次迭代两组互换。最后再单独训练学生模块。

### 6.1 总体流程

**【原文】Alg. 1：Joint RL training pipeline**

```
for K updates do
    In adaptive training environments, collect standard ID data with π(a_t | s_t, z_t), z_t = f(c_t). Calculate L_RL^ID.
    In robust training environments, collect adversarial data with π(a_t | s_t, z_rob) and π̃_adv(ã_t | s_t). Calculate L_RL^OOD.
    Optimize the RL loss L_RL^GRAM = L_RL^ID + L_RL^OOD.
    Alternate training environment assignments.
end
```

**逐行解释**：

| 行 | 原文 | 翻译 | 解释 |
|---|---|---|---|
| 1 | for K updates do | 进行 K 次更新 | K = 10,000 |
| 2 | In adaptive training environments, collect standard ID data with π(a∣s, z), z = f(c). Calculate L_RL^ID | 在**自适应训练环境**里，用策略 π 加真实编码 z = f(c) 收集普通的 ID 数据，算 ID 部分的 RL 损失 | 这组和普通教师训练一模一样：策略"开卷"走路 |
| 3 | In robust training environments, collect adversarial data with π(a∣s, z_rob) and π̃_adv. Calculate L_RL^OOD | 在**鲁棒训练环境**里，用策略 π 加 z_rob = 0、同时有对抗者 π̃_adv 捣乱，收集对抗数据，算 OOD 部分的 RL 损失 | 这组策略"闭眼"（z = 0）还要被推，学的是"保守但稳" |
| 4 | Optimize L_RL^GRAM = L_RL^ID + L_RL^OOD | 两部分损失加起来一起优化 | 同一个策略网络同时接受两种梯度 |
| 5 | Alternate training environment assignments | 交换各环境的分配 | 上一轮是自适应组的环境，下一轮变成鲁棒组，反之亦然 |

**【原文】Fig. 3 图注**："Joint RL training pipeline used by GRAM, which combines standard ID data collection and adversarial data collection for every RL update. Training environments are assigned to adaptive training or robust training at each iteration, and assignments alternate between iterations. RL training is followed by supervised learning to train the adaptation network φ(h_t, ε)."

> 翻译：GRAM 使用的联合 RL 训练流程，每次 RL 更新都同时包含普通 ID 数据收集和对抗数据收集。每次迭代，训练环境被分配为自适应训练或鲁棒训练，分配在迭代之间交替。RL 训练之后，再用监督学习训练适应网络 φ(h, ε)。

Fig. 3 中还有仿真中的 Go2 机器狗画面，**绿色箭头表示速度指令**（论文 Section VII 原文："The simulated quadruped robot can be seen in Fig. 3, with the velocity command represented by a green arrow."）。

**【原文】** "Note that the robust adaptation module φ_GRAM(h_t) is only applied at deployment time and not during training."

> 翻译：注意，鲁棒适应模块 φ_GRAM **只在部署时使用，训练时不用**。

### 6.2 RL 训练的细节

1. **并行环境分两组**：自适应训练 / 鲁棒训练（代码里初始各一半）。

2. **每次迭代内，一个环境的数据全部按同一种方式收集**。

   **【原文】** "Within each iteration of RL training, all data for a given training environment is collected according to either standard ID data collection or adversarial data collection... This provides temporal consistency when training the policy for adaptive or robust performance, respectively."
   > 翻译：在每次 RL 迭代内，某个训练环境的所有数据都按普通 ID 收集或对抗收集中的一种进行……这为分别训练适应性能或鲁棒性能提供了**时间上的一致性**。

3. **迭代之间交替分配**。

   **【原文】** "We alternate these assignments between iterations, which allows full trajectories to contain a mixture of both forms of data. As shown in our experiments, this mixed data collection design provides additional robustness benefits compared to using the same training assignment for entire trajectories."
   > 翻译：我们在迭代之间交替这些分配，使完整的轨迹包含两种数据的混合。实验表明，这种**混合数据收集**设计相比整条轨迹用同一种分配，带来额外的鲁棒性收益。

   - 【解读，依据代码】runner 配置继承 Isaac Lab 的 Go2 PPO 默认值，一次迭代每个环境走 24 步（约 0.48 s；24 是 Isaac Lab 默认值，需在服务器版本上确认）。一个回合最长 1000 步，所以一条轨迹里两种模式大约每 0.5 s 切换一次。
   - **时间线示意**（一个环境）：

   ```
   时间(s):  0      0.48     0.96     1.44     1.92  ...
   模式:     [自适应][ 鲁棒 ][自适应][ 鲁棒 ] ...
   z 输入:   f(c)    0+推    f(c)    0+推
   ```

   - **这有什么用**：轨迹前半段可能是在 z_rob 下被推着走，后半段又按 f(c) 走。策略因此要学会"**从鲁棒模式接手后继续走好**"，以及"**被推乱之后切回适应模式也能稳住**"。部署时 α 是逐时刻变化的，正好需要这种"模式之间平滑衔接"的能力。

4. **自适应环境**：z_t = f(c_t)，普通教师训练，更新 π、V、f。损失记作 L_RL^ID。

5. **鲁棒环境**：z = z_rob；加一个**对抗者策略** π̃_adv，用 RL 训练来**最小化**策略的回报。

   **【原文】** "In our experiments on a Unitree Go2 quadruped robot, the adversary applies forward and lateral external forces to the robot's body 5% of the time during data collection, where the direction of the external force is learned by the adversary."
   > 翻译：在 Go2 实验中，对抗者在数据收集期间 **5% 的时间**对机身施加**前向和侧向外力**，外力的**方向由对抗者学习**。

   - 推力对线速度的影响从 0 增加到 1 m/s（随训练进度线性增加，Sec. VI）；
   - 【注意，依据代码】代码里不是真的"施加力"，而是在被选中的时刻**直接给机身水平速度加一个增量**（最多 1 m/s，方向由对抗者给出），等效于一次瞬时冲击，见 [04 代码精读](04_code_walkthrough.CN.md)；
   - **数值感受**：5% 的时间，50 Hz 下就是平均每秒约 2–3 次被"踢一下"，每次最多让机身速度突变 1 m/s，而机器狗本身速度指令也就 ±1 m/s。这个扰动是很强的。
   - 损失记作 L_RL^OOD。

6. **总损失（式 10）**：

$$L^{GRAM}_{RL} = L^{ID}_{RL} + L^{OOD}_{RL}$$

   同一个策略网络同时接受两种梯度。两项权重都是 1，没有额外调权。

**【原文】** "Note that adversarial RL provides a method for sampling worst-case trajectories during training, which leads to robust generalization in unseen OOD contexts at deployment time when the robust latent feature z_rob is provided to the policy as input."

> 翻译：对抗 RL 提供了一种在训练中**采样最坏情况轨迹**的方法，当把 z_rob 作为输入提供给策略时，这能在部署时带来对没见过的 OOD 情况的鲁棒泛化。

**【注意】** 这句话里有一个**关键假设**：用"推力"这一种对抗扰动训练出来的鲁棒性，能泛化到加重、斜坡、粗糙地面、关节冻结等**完全不同类型**的 OOD。论文用实验支持了这一点，但没有解释为什么。作者自己在局限里也承认 OOD 泛化"depends on how well the robust RL training pipeline captures worst-case OOD dynamics"。

### 6.3 适应模块训练

**【原文】** "Data collection uses the student policy π(a_t | s_t, ẑ_t) with ẑ_t = μ̂(h_t) or ẑ_t = z_rob, depending on the training assignment. We do not apply an adversary during the supervised learning phase, as the goal is to train the epinet in (5) to output estimates with low variance in ID contexts."

> 翻译：数据收集使用学生策略，ẑ 取 μ̂(h) 或 z_rob，取决于训练分配。**监督学习阶段不施加对抗者**，因为目标是训练 epinet 在 ID 情况下输出低方差的估计。

- 用式 (8) 训练 epinet 结构的 φ(h, ε)；
- 【依据代码】历史编码器和 epinet 默认**只在最后 5000 次 finetune 中训练**，前 10000 次 RL 阶段不训练它们（这与论文"RL 之后接监督阶段"的描述一致）。

**【解读】** 不加对抗者是为了让"训练分布"干净，只包含 ID 情况。如果训练时也有推力，epinet 会把"被推"当作见过的情况，部署时遇到类似扰动就不会提高不确定性。

**三个阶段一览**：

| 阶段 | 迭代数 | 训练什么 | 环境设置 |
|---|---|---|---|
| ① RL 联合训练 | 10,000 | 策略 π、价值 V、上下文编码器 f、对抗者 | 两组交替；鲁棒组有推力 |
| ② 监督训练适应模块 | 5,000 | φ_base 和 epinet | 学生策略采数据，**无推力** |
| ③ 定标 | 一次 | 算 β、λ | ID 验证集 |

> **读论文时应该问自己的问题**
> - Q：为什么鲁棒组用 z = 0 而不是随机 z？
> - A：要让 0 成为一个"专门的保守点"。如果用随机 z，策略学不到一个固定的保守行为，部署时也就没有明确的退路。
> - Q：两项损失等权相加，有没有可能一项压过另一项？
> - A：论文没讨论。环境是一半一半分的，数据量相同，所以等权是一个自然的选择。

---

## 7. 算法与实现细节（Section VI）

**这一节在说什么（大白话）**：具体用多大的网络、训练多少步、β 和 λ 怎么定。

### 7.1 Table I：实现参数

| 组件 | 设置 | 说明 |
|---|---|---|
| 策略 π、价值 V、对抗者 π̃_adv | MLP 512-256-128 | 三层隐藏层，神经元数依次为 512、256、128 |
| 上下文编码器 f | MLP 64-64 | 26 维 → 8 维，小网络 |
| 基础适应网络 φ_base | MLP 512-256-128 | 输入是 16 步历史展平后的长向量 |
| Epinet φ_epi | MLP 16-16 | 很小 |
| 隐变量维度 d | 8 | |
| 历史长度 H | 16 | 50 Hz 下 = 0.32 s |
| Epinet 随机输入维度 m | 8 | |
| 每个数据点的随机样本数 N | 8 | 每次推理算 8 遍 epinet |

**"MLP 512-256-128"怎么读**：多层感知机（全连接网络），输入 → 512 个神经元 → 256 → 128 → 输出。

**部署时的计算量感受**：N = 8 只针对 epinet（16-16 的小网络），base 网络只算一遍，所以多算 8 次的开销很小。论文说"all computation is performed onboard"（全部在机载计算）。

### 7.2 训练规模

**【原文】** "We perform 10,000 updates during RL training, followed by a supervised learning phase where we train the adaptation network for 5,000 updates."

> 翻译：RL 训练进行 10,000 次更新，之后监督学习阶段训练适应网络 5,000 次更新。

- PPO + Rudin 2022 的大规模并行方案 [35]；
- 所有网络都是前馈网络（同 [4]），epinet 设计按 [8]。

**对抗者强度的课程**：

**【原文】** "The adversary policy is trained to apply worst-case external forces that cause abrupt changes to the robot's forward and lateral linear velocity... the impact of the force on linear velocity increases from 0.0 to 1.0 meters per second over the course of training."

> 翻译：对抗者被训练来施加最坏情况的外力，使机器人前向和侧向线速度**突变**……外力对线速度的影响在训练过程中从 0 增加到 1 m/s。

这是一种**课程学习**：先易后难，开始不推，逐渐加大，避免一开始就被推得学不会走路。

### 7.3 β、λ 的定标

**【原文】** "We set β to be the u_min = 0.90 quantile of the validation set (note that α_t = 1.00 when ‖σ̂(h_t)‖² ≤ β), and we set λ such that α_t = 0.01 at the u_max = 0.99 quantile of the validation set."

> 翻译：β 取验证集的 0.90 分位数（注意不确定性 ≤ β 时 α = 1），λ 设为使 α 在验证集 0.99 分位数处等于 0.01。

**【解读】** 这个定标很实用：不需要人工调阈值，用"训练分布内不确定性的统计分布"自动决定什么算"异常"。

**【注意】** 这也意味着：**按设计，即使在 ID 情况下，也有约 10% 的时刻 α < 1**，约 1% 的时刻 α ≈ 0.01。所以 GRAM 在 ID 下略逊于情境 RL（0.92 vs 0.94）是这个设计的代价之一。

**分位数选择的含义**：

| 如果把 β 取成 | 效果 |
|---|---|
| 0.90 分位数（论文） | ID 下约 10% 时刻会部分退回 |
| 0.99 分位数（更宽松） | ID 下很少退回，ID 性能更好，但对 OOD 反应更迟钝 |
| 0.50 分位数（更严格） | ID 下一半时刻会部分退回，很保守 |

论文没有做这个敏感性分析，这也是一个可以补的实验。

### 7.4 可替换性

**【原文】** "However, note that it is also possible to apply GRAM with different choices of contextual RL methods for ID adaptation and robust RL methods for OOD generalization, which represents an interesting avenue for future work."

> 翻译：不过，也可以把 GRAM 和其他的情境 RL 方法（用于 ID 适应）以及其他的鲁棒 RL 方法（用于 OOD 泛化）组合使用，这是未来工作的一个有趣方向。

**【解读】** 作者明说：适应部分、鲁棒部分都可以换。这给了"A+B"式改进的空间。

---

## 8. 仿真实验设置（Section VII 开头）

**这一节在说什么（大白话）**：在 Isaac Lab 里让 Go2 按指令速度走，只在平地上训练，然后在各种没见过的情况下测。

| 项 | 设置 |
|---|---|
| 仿真器 | Isaac Lab |
| 任务 | 速度跟踪：v_cmd = [vx, vy, ωz]；vx, vy ~ U(−1, 1) m/s；ωz 由目标航向计算 |
| 观测 | 带噪声的本体感知：关节角、关节速度、投影重力、机身角速度（代码里还包括速度指令和上一步动作，**不含机身线速度**） |
| 动作 | 12 个关节的目标角度 |
| 底层 | PD 控制器 200 Hz，Kp = 25，Kd = 0.5 |
| 策略频率 | 50 Hz |
| 回合长度 | 最长 20 s = 1000 步 |
| 奖励 | 沿用 Margolis 2024 [4]：速度跟踪 + 平滑稳定步态的正则项 |
| 训练地形 | **全部在平坦硬地面上** |
| 评估指标 | 归一化的平均速度跟踪回报，[0, 1] |

**"U(−1, 1)"是什么**：均匀分布，在 −1 到 1 之间随机取值。所以指令可能是前进、后退、左右平移的任意组合。

**"ωz 由目标航向计算"**：不直接给转向角速度，而是给一个"目标朝向"，根据当前朝向和目标朝向的差算出需要的转向速度。

**为什么不含机身线速度**：实机上机身线速度没法直接测（需要状态估计器，会有误差），去掉它更贴近实机。这也增加了难度：策略只能从关节和 IMU 推断自己走得多快。

**评估场景**：

| 类别 | 场景 | 与训练的差距 |
|---|---|---|
| ID | 从 Table II 范围采样 | 无 |
| 近 OOD | ① 加 6 kg ② 5° 坡 ③ 5 cm 粗糙地面 ④ 后髋关节冻结 | 中等 |
| 远 OOD | ① 加 9 kg ② 10° 坡 ③ 10 cm 粗糙地面 ④ 随机关节冻结 | 大 |

**【原文】** "We conduct this analysis by training all methods on flat, solid ground across the ID context set C_ID described in Table II, which represents moderate dynamics variations that are commonly used to promote sim-to-real transfer."

> 翻译：所有方法都在平坦坚硬的地面上、在 Table II 描述的 ID 上下文集上训练，这代表了**常用于促进仿真到实机迁移的中等动力学变化**。

**对比方法**：鲁棒 RL（对抗训练 [7]）、情境 RL（教师—学生 [2]–[4]）、域随机化 [37]。

实验结果的逐表解读见 [03 实验精读](03_experiments.CN.md)。

---

## 9. 实机实验设置（Section VIII 开头）

**这一节在说什么（大白话）**：把仿真训好的策略直接放到真的 Go2 上，不再训练，看能不能走。

- Go2 实机，**零样本仿真到实机**；
- 策略**只在平坦硬地面、Table II 的中等变化下训练**；

**【原文】** "All policies were trained on flat, solid ground with the moderate variations described by C_ID in Table II, which differs from prior works on legged locomotion that evaluate generalization after training on a broad set of diverse environments (e.g., [3])."

> 翻译：所有策略都只在平坦坚硬的地面上、用 Table II 中的中等变化训练，这**不同于以往足式运动工作**在大量多样环境上训练后再评估泛化（如 RMA）。

- 50 Hz 输出目标关节角，内置 PD 200 Hz，Kp = 25，Kd = 0.5；
- **全部计算在机载完成**；
- 受控实验：7 个场景，前进 6 m，v_x = 1.0 m/s；每场景每算法 5 次，3 个算法，共 7 × 5 × 3 = **105 次**；
- 定性实验：户外草地 + 雨水篦子、不平土路、木屑。

**【解读】** "只在平地训练"是故意的：作者想证明 GRAM 的泛化不靠"把各种地形都练过"，而是靠"识别没见过 → 切换鲁棒"。这比 RMA 那种在各种地形上训练的设定更能体现 OOD 泛化。

---

## 10. 结论与局限（Section IX）

**这一节在说什么（大白话）**：总结一下我们做了什么；承认 OOD 能做多好取决于对抗训练练得多全面，以后可以换别的鲁棒训练方法、换别的机器人。

**【原文·局限】** "Because OOD contexts are unknown during training by definition, the OOD generalization of GRAM depends on how well the robust RL training pipeline captures worst-case OOD dynamics, which may lead to failures in extreme OOD scenarios."

> 翻译：由于 OOD 上下文按定义在训练时是未知的，GRAM 的 OOD 泛化取决于鲁棒 RL 训练流程能多好地捕捉最坏情况的 OOD 动力学，**在极端 OOD 场景下可能失败**。

**【原文】** "We applied a standard choice of adversary that worked well in our controlled hardware trials and qualitative outdoor experiments on a quadruped robot, but it would be interesting to combine GRAM with other robust RL techniques and explore its generalization capabilities across a broader range of unstructured environments."

> 翻译：我们使用了一种标准的对抗者选择，在四足机器人的受控实机试验和户外定性实验中效果良好，但**将 GRAM 与其他鲁棒 RL 技术结合**、并在更广泛的非结构化环境中探索其泛化能力，会很有意义。

**【原文·未来工作】** "GRAM is a flexible deep RL framework that can be extended to other robots and tasks, where domain-specific knowledge can be incorporated through the choice of ID context set for adaptive training and the choice of adversary for robust training."

> 翻译：GRAM 是一个灵活的深度 RL 框架，可以扩展到**其他机器人和任务**，**领域知识**可以通过选择自适应训练用的 ID 上下文集和鲁棒训练用的对抗者来引入。

**【解读】** 作者自己指出两个延伸方向：
1. 换更好的鲁棒训练方式（不只推力）；
2. 扩展到其他机器人和任务，通过**选择上下文集**和**选择对抗者**引入领域知识。

我们的方向（轮足、按部件分组、执行器类扰动）正好落在第 2 点上：**轮足的领域知识 = 轮/腿两类执行器 + 腿轮冗余**。

---

## 全文结构速记

```
问题：ID 要适应，OOD 要鲁棒，一个策略难兼顾
  ↓
方法：
  模块  —— epinet 估计不确定性 → α → 在 μ̂ 和 z_rob=0 之间混合（式 9）
  训练  —— 一半环境用 f(c) 普通训练，一半用 z=0 + 推力对抗者；迭代间交替（式 10）
         —— 再监督训练 epinet 回归 f(c)，不加对抗者（式 8）
  定标  —— β=验证集 q90，λ 使 q99 处 α=0.01
  ↓
实验：
  仿真  —— 平地训练；ID / 近 OOD / 远 OOD；对比鲁棒 RL、情境 RL、DR；3 个消融
  实机  —— 7 个场景 105 次；难场景 15/15；户外定性
  ↓
局限：OOD 依赖对抗者；只试了推力和四足
```

## 部署时一个时刻发生了什么（把所有零件串起来）

```
1. 读传感器：关节角、关节速度、投影重力、角速度 + 速度指令 + 上一步动作 → 当前观测 s
2. 把 s 放进 16 步的历史缓冲 h
3. φ_base(h) → 一个 8 维估计
4. 采 8 个随机 ε，epinet 算 8 次 → 8 个 8 维估计 → 均值 μ̂、逐维方差
5. 8 维方差求和 → 总不确定性 u
6. α = exp(−λ·max(u − β, 0))
7. z = α · μ̂          （因为 z_rob = 0）
8. 策略 π(s, z) → 12 个目标关节角
9. PD 控制器（200 Hz）→ 电机力矩
（每 20 ms 重复一次，即 50 Hz）
```

---

## 自测题

1. 写出式 (9)，说明 α 的取值范围，以及 β、λ 是怎么定的。
2. 为什么 z_rob 取 0 不需要额外的鲁棒网络？
3. 训练时用 φ_GRAM 吗？为什么？
4. 监督训练阶段为什么不加对抗者？
5. "混合数据收集"指什么？对照组是哪个？
6. 按 GRAM 的定标方式，ID 情况下 α 有多大比例的时刻小于 1？
7. 不确定性是向量还是标量？这一点为什么重要？
8. 手算：β = 1，λ = 2，不确定性为 1.5 时 α 是多少？μ̂ = [1, −2] 时 φ_GRAM 是多少？
9. 学生阶段为什么用学生策略自己采数据？

<details>
<summary>参考答案</summary>

1. φ_GRAM = (1−α)z_rob + αμ̂，α = exp(−λ(‖σ̂‖²−β)⁺) ∈ [0,1]。β 取验证集 ‖σ̂‖² 的 0.90 分位数；λ = −ln0.01 / (q99 − q90)，使 0.99 分位数处 α=0.01。
2. 鲁棒模式就是同一个策略网络输入 z=0。训练时鲁棒组的数据就是在 z=0 下用对抗者采的，所以同一个网络学会了"z=0 时保守地走"。
3. 不用。训练时自适应组用真实 f(c)，鲁棒组用 0；φ_GRAM 只在部署时使用。
4. 要让 epinet 只把 ID 情况当作"见过"，部署时遇到扰动才会提高不确定性。
5. 同一个环境在不同迭代间交替做自适应训练和鲁棒训练，一条完整轨迹里混有两种数据。对照组是 Separate Data（一条轨迹只用一种分配）。
6. 约 10%（‖σ̂‖² 超过 0.90 分位数的时刻）。
7. 标量（8 维方差求和）。因为它只能回答"整体可不可信"，不能回答"哪部分不可信"，于是一旦不确定就整体退回。这是我们想改进的地方。
8. α = exp(−2 × 0.5) = exp(−1) ≈ 0.368；φ_GRAM ≈ [0.368, −0.736]。
9. 部署时是学生在走，学生走出来的历史分布和教师不同；用学生自己的数据训练，训练分布和部署分布一致。
</details>
