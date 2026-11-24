# 机器人控制与强化学习背景

## 文档用途

本论文的主线是行为克隆，不是强化学习。本文件只先提供读 Diffusion Policy 所需的机器人控制直觉，并把完整 RL 笔记作为后半部分的可选背景。若你的目标是继续读论文，应先掌握第 1 节，再按需要学习 RL 的第 2 节以后。

## 1. 读论文前必须会的机器人控制

| 名称 | 记号 | 含义 |
|---|---|---|
| 真实状态 | \(s_t\) | 环境真正发生的一切，如物体位置、摩擦、机器人关节；不一定完全可见 |
| 观测 | \(O_t\) | 相机图像、末端位姿、夹爪状态等模型真正输入 |
| 单步动作 | \(a_t\) | 下一个目标位置、旋转、夹爪开合或速度 |
| 动作计划 | \(A_t=[a_t,\ldots,a_{t+T_p-1}]\) | 未来一段动作，而非单步动作 |

Diffusion Policy 使用滚动时域控制（receding horizon control, RHC）：

\[
O_t\rightarrow A_t
\rightarrow\text{只执行前 }T_a\text{ 步}
\rightarrow O_{t+T_a}\rightarrow\text{重新规划}.
\]

预测整段 \(T_p\) 动作可让动作彼此协调；只执行前 \(T_a\) 步可在物体移动、相机遮挡或执行误差出现后重新观察和纠正。绝不能把“预测 \(T_p\) 步”等同于“必须开环执行 \(T_p\) 步”。

| 时域 | 含义 | 过短/过长的主要代价 |
|---|---|---|
| \(T_o\) | 使用多少历史观测 | 太短看不出运动；太长冗余且视觉开销变大 |
| \(T_p\) | 每次生成多长未来计划 | 太短缺少协调；太长后半段过时、采样慢 |
| \(T_a\) | 每次实际执行多少步 | 太短频繁规划；太长对变化反应慢 |

位置控制输出“末端应到哪里”，底层控制器负责追踪；速度控制输出“这一小段时间应怎样移动”。前者不容易逐步累计小速度误差，后者更容易积分漂移。论文观察到扩散策略与位置控制相配合较好；这不是对所有机器人任务的普遍定理。

论文提到利用未执行的旧计划帮助下一轮初始化（warm start），但没有把尾部拼接、补齐和加噪的精确实现作为核心公式给出。阅读代码时应以具体实现为准，不能把某个猜测当成论文事实。

高层策略可每秒规划十次，低层伺服/逆运动学控制器可用更高频率追踪、限速、碰撞检测和安全停止。真实机器人实验必须保留这些独立安全机制。

## 2. 可选背景：强化学习

> 适用对象：正在学习王树森《深度强化学习》公开课的初学者。
>
> 本文整合“基础知识、价值学习、策略学习”的笔记，并补全 MDP、Bellman 方程、DQN 的关键稳定化设计、优势函数、Actor-Critic、连续动作和与 Diffusion Policy 的关系。保留“小狗训练/打游戏”的直觉，但公式采用较通用的标准记号。

### 2.1 先说结论：你正在学哪两条主线

强化学习（Reinforcement Learning, RL）研究的是：智能体反复和环境互动，通过奖惩学会让**长期总收益**最大的决策方式。

```text
当前处境 S_t --策略 π--> 动作 A_t --环境--> 奖励 R_{t+1}、新处境 S_{t+1}
      ↑                                                               │
      └────────────────────── 用这次经验更新策略 ──────────────────────┘
```

贯穿本章的两条路线：

| 路线 | 先学什么 | 如何决策 | 代表 |
|---|---|---|---|
| 基于价值（value-based） | 每个动作将来值多少分 | 选分数最高的动作 | Q-learning、DQN |
| 基于策略（policy-based） | 直接学动作概率/动作分布 | 按策略采样或输出动作 | REINFORCE、策略梯度 |

Actor-Critic 把两者结合：**Actor** 负责出招，**Critic** 负责评价这招是否比平常好。

---

### 2.2 统一记号：先避免 80% 的混乱

你提供的笔记用 $U_t$ 表示折扣回报。很多教材用 $G_t$；两者本质相同。本文统一用 $G_t$，并把“即时奖励”与“长期回报”分开。

| 符号 | 名称 | 小狗/游戏类比 |
|---|---|---|
| $S_t=s$ | 状态 state | 小狗此刻位置、眼前是否有障碍；马里奥站在坑前的画面。 |
| $A_t=a$ | 动作 action | 向左、跳、抓取、转方向盘。 |
| $R_{t+1}$ | 即时奖励 reward | 这一步之后得到的饼干/扣分；写成 $t+1$ 是因为它由动作后的环境给出。 |
| $\pi(a\mid s)$ | 策略 policy | 小狗在状态 $s$ 下选动作 $a$ 的概率规则。 |
| $\gamma\in[0,1)$ | 折扣因子 | 对更远将来的分数打折；也让无限任务的总和有限。 |
| $G_t$ | 折扣回报 return | 从现在开始一路拿到的“折后总分”。 |
| $V_\pi(s)$ | 状态价值 | 在 $s$ 且照当前打法 $\pi$ 玩下去，平均能得多少总分。 |
| $Q_\pi(s,a)$ | 动作价值 | 在 $s$ 先出 $a$，之后照 $\pi$ 玩，平均能得多少总分。 |
| $A_\pi(s,a)$ | 优势 advantage | 这招比当前状态的“平均发挥”好多少。 |

对一局在时刻 $T$ 结束的游戏：

$$
G_t=R_{t+1}+\gamma R_{t+2}+\gamma^2R_{t+3}+\cdots+\gamma^{T-t-1}R_T.
$$

例如现在吃金币得到 10 分，下一步可能得到 10 分，$\gamma=0.9$，那么它们对当前回报贡献为 $10+0.9\times10=19$。$\gamma$ 不是说“未来不重要”，而是明确任务对远期奖励的权重；在有限回合任务里也常取接近 1。

---

### 2.3 MDP：把“打游戏”写成数学问题

强化学习通常建模成**马尔可夫决策过程**（MDP）：

$$
\mathcal M=(\mathcal S,\mathcal A,P,R,\gamma).
$$

- $\mathcal S$：状态集合；$\mathcal A$：动作集合。
- $P(s'\mid s,a)$：在 $s$ 做 $a$ 后转移到 $s'$ 的概率。
- $R$：奖励规则，可写成 $R(s,a,s')$ 或随机奖励分布。
- 马尔可夫性：**给定当前状态和动作，下一步的分布不再依赖更早历史。**

游戏画面若不能完整表达过去（例如看不出角色速度），严格说“单帧图像”未必是完整状态，可能只是观测 $O_t$；此时问题更接近 POMDP。初学时先把输入称作状态，但要知道这个边界。

一条轨迹是：

$$
\tau=(S_0,A_0,R_1,S_1,A_1,R_2,\ldots).
$$

强化学习的总目标是找参数 $\theta$，使策略 $\pi_\theta$ 的期望回报最大：

$$
J(\theta)=\mathbb E_{\tau\sim\pi_\theta}[G_0].
$$

**和监督学习的根本差别：** 标签不是事先给定的“正确动作”。智能体的动作会改变之后看到的数据和奖励，且奖励经常延迟很久才出现。这叫信用分配（credit assignment）问题：最后通关的奖励该归功于前面哪一步？

---

### 2.4 价值函数：给“处境”和“出招”打长期分

### 3.1 状态价值与动作价值

$$
V_\pi(s)=\mathbb E_\pi[G_t\mid S_t=s],
$$

$$
Q_\pi(s,a)=\mathbb E_\pi[G_t\mid S_t=s,A_t=a].
$$

两者区别很重要：

- $V_\pi(s)$ 问“此处境按当前打法平均有多好？”
- $Q_\pi(s,a)$ 问“在此处境先走这一步，之后按当前打法，究竟有多好？”

如果策略是随机的，状态价值等于按策略概率加权的动作价值：

$$
V_\pi(s)=\sum_a\pi(a\mid s)Q_\pi(s,a).
$$

所以“把所有动作的概率乘对应得分再相加”是 $V_\pi(s)$ 的正确含义；它不是策略梯度训练时唯一的目标式，而是一个价值定义。

### 3.2 优势函数：不只问“得分高不高”

$$
A_\pi(s,a)=Q_\pi(s,a)-V_\pi(s).
$$

想象小狗在一个本来就很容易拿饼干的房间。拿到 8 分不一定说明刚才这步特别好；若平均本就 9 分，优势是负的。优势回答的是“这一步比这个处境通常水平更好还是更差”。它是后续 Actor-Critic 与 PPO 常用的低方差学习信号。

### 3.3 Bellman 方程：把长期分拆成“一步 + 后面”

这是 RL 的核心递推思想：今天的长期价值 = 今天立即奖励 + 明天开始的长期价值。

$$
V_\pi(s)=\mathbb E_{a\sim\pi,\,s'\sim P}\left[R_{t+1}+\gamma V_\pi(s')\mid S_t=s\right],
$$

$$
Q_\pi(s,a)=\mathbb E\left[R_{t+1}+\gamma\,\mathbb E_{a'\sim\pi}[Q_\pi(S_{t+1},a')]\mid S_t=s,A_t=a\right].
$$

若永远选最优动作，则有最优 Bellman 方程：

$$
Q^*(s,a)=\mathbb E\left[R_{t+1}+\gamma\max_{a'}Q^*(S_{t+1},a')\mid s,a\right].
$$

这正是 Q-learning/DQN 的学习靶子。它不是凭空“猜下一步”，而是利用递推把遥远未来压缩到下一个状态的估值。

---

### 2.5 TD 学习与 Q-learning：用“一步后的新信息”纠正旧估计

### 4.1 TD target 与 TD error

在实际环境中我们通常不知道 $P$，也无法对全部下一状态做期望。做一次动作后，拿到样本 $(s,a,r,s',d)$：$d=1$ 表示终止。Q-learning 用样本构造：

$$
\underbrace{y}_{\text{TD target}}
=r+\gamma(1-d)\max_{a'}Q(s',a'),
$$

$$
\underbrace{\delta}_{\text{TD error}}=y-Q(s,a).
$$

表格型 Q-learning 的更新是：

$$
Q(s,a)\leftarrow Q(s,a)+\alpha\delta.
$$

它的意思是：“这次新经历告诉我，原先给此动作的分过高/过低；向新目标挪一小步。” $d$ 很重要：如果已经游戏结束，后面没有未来分，应让 target 就是 $r$。

### 4.2 你的数值例子，标准化写法

小孩估计 $Q(s_t,a_t)=10$；走一步拿到 $r=-2$；在新状态中估计最佳未来价值为 5；$\gamma=0.9$，且未终止：

$$
y=-2+0.9\times5=2.5,\qquad \delta=2.5-10=-7.5.
$$

负 TD error 表示这招没有原先想的好，更新会降低 $Q(s_t,a_t)$。这里“5”是**下一状态最大 Q 值估计**，不是已经拿到的真实奖励。

### 4.3 为什么叫 temporal-difference（时序差分）

它比较的是相邻时间的估值：当前 $Q(s,a)$ 与“一步奖励 + 下一状态估值”。它不必等一整局结束才更新（这是相对 Monte Carlo 的优点），但也因此使用了自己的估值做目标，称为 bootstrapping（自举）。

---

### 2.6 DQN：用神经网络近似 Q 表

状态很大（游戏画面、相机图像）时，无法真的存一张 $Q(s,a)$ 表。DQN 用神经网络 $Q_\phi(s,a)$ 或一次输出所有离散动作的分数 $Q_\phi(s,\cdot)$ 来近似它。$phi$ 是价值网络参数；它对应你笔记中的 $\mathbf w$。

### 5.1 DQN 的一个训练 batch

从经验池取 $(s_i,a_i,r_i,s'_i,d_i)$，用目标网络参数 $\bar\phi$ 构建（不对 target 反向传播）：

$$
y_i=r_i+\gamma(1-d_i)\max_{a'}Q_{\bar\phi}(s'_i,a'),
$$

$$
L(\phi)=\frac{1}{B}\sum_{i=1}^B\frac12\left(Q_\phi(s_i,a_i)-\operatorname{stopgrad}(y_i)\right)^2.
$$

代码里通常写成“最小化 loss”，所以用梯度**下降**：

$$
\phi\leftarrow\phi-\eta\nabla_\phi L(\phi).
$$

“为什么要对参数求导？”答案和你的类比一致：神经网络有海量旋钮，梯度给出让当前预测接近 TD target 的局部调节方向。关键补充是：**只通过左侧 $Q_\phi(s_i,a_i)$ 求导；右侧 target 是暂时固定的老师答案。** 若两边同一网络同时快速改变，目标会追着预测跑，训练更不稳。

### 5.2 原版 DQN 的四个关键部件

1. **在线 Q 网络 $Q_\phi$：** 负责当前预测与被优化。
2. **目标网络 $Q_{\bar\phi}$：** 定期从在线网络复制，或缓慢跟随，提供相对稳定的 TD target。
3. **经验回放池 replay buffer：** 存储过去转移，随机抽 batch，打破相邻经验的强相关性并复用数据。
4. **$\epsilon$-greedy 探索：** 以 $1-\epsilon$ 概率选当前最高分动作，以 $\epsilon$ 概率随机动作。否则早期的错误估值会让智能体从不尝试新招。

从 $\epsilon$-greedy 收集的数据再用贪心 $\max Q$ 学习最优策略，所以 Q-learning/DQN 是 **off-policy**：收集数据的行为策略可与目标贪心策略不同。

### 5.3 DQN 的边界

- 原始 DQN 最自然适合**离散、有限动作**，例如上下左右、跳/不跳；它可一次输出每个动作的 Q 分数。
- 连续动作（方向盘转 10.1°、机械臂 6DoF 位姿）不能穷举 $\max_aQ(s,a)$。后续可学 DDPG、TD3、SAC，或用策略网络直接产生连续动作。
- DQN 不是“训练损失下降就成功”。必须用不探索的评估策略跑完整回合，看平均回报/成功率。

---

### 2.7 策略梯度：直接优化“出招概率”

价值法学的是“每个动作值多少”；策略法直接参数化策略 $\pi_\theta(a\mid s)$。

### 6.1 离散与连续动作的策略输出

- **离散动作：** 网络输出 logits，经 softmax 变成各动作概率。例如跳 0.8、后退 0.2。
- **连续动作：** 常令网络输出高斯分布参数 $\mu_\theta(s),\sigma_\theta(s)$，从 $\mathcal N(\mu,\sigma^2)$ 采样连续动作。这里输出不是一张能枚举完的动作概率表，而是一个密度分布。

训练时必须有随机性，以便探索并让“动作概率”可导地参与目标；评估时常用均值动作或更低随机性，具体依算法而定。

### 6.2 REINFORCE 的正确目标与更新

策略优化的目标是：

$$
J(\theta)=\mathbb E_{\tau\sim\pi_\theta}[G_0].
$$

对数导数技巧给出无偏的梯度估计：

$$
\nabla_\theta J(\theta)
=\mathbb E\left[\sum_t\nabla_\theta\log\pi_\theta(A_t\mid S_t)\;G_t\right].
$$

这比“拿单步动作得分 $q_t$ 乘导数”更准确：权重应是从时刻 $t$ 开始的**回报 $G_t$**，因为当前动作会影响之后的奖励。一个 episode 的采样估计可写作：

$$
\hat g=\sum_t\nabla_\theta\log\pi_\theta(a_t\mid s_t)G_t,
\qquad
\theta\leftarrow\theta+\alpha\hat g.
$$

这就是梯度**上升**：希望 $J$（期望回报）变大。深度学习框架通常只提供“最小化 loss”，会实现等价的

$$
L_\pi=-\frac1B\sum_t\log\pi_\theta(a_t\mid s_t)G_t
$$

并对 $L_\pi$ 做梯度下降。两种符号看似相反，目标完全一致。

### 6.3 为什么是 $\log\pi$，而不是直接对概率求导

关键恒等式：

$$
\nabla_\theta\pi_\theta(a\mid s)
=\pi_\theta(a\mid s)\nabla_\theta\log\pi_\theta(a\mid s).
$$

它把“对所有动作/轨迹加权的期望”转换为“从当前策略实际采到的动作”的期望。直觉上，$\nabla\log\pi(a\mid s)$ 是“怎样调整参数能让刚才抽到的动作更可能出现”的方向；再乘 $G_t$：

- $G_t$ 大：沿该方向走，增加这个动作概率；
- $G_t$ 小或为负：反向效果，减少该动作概率。

“只随机试一次就能估计方向”是指得到一个**有噪但无偏**的样本估计，不等于一次就能可靠学会；REINFORCE 的方差往往很大，需要许多轨迹。

### 6.4 Baseline 与优势：降低方差而不改变正确方向

可从回报中减去任何只依赖状态、而不依赖已抽动作的基线 $b(s_t)$：

$$
\nabla_\theta J(\theta)=
\mathbb E\left[\sum_t\nabla_\theta\log\pi_\theta(A_t\mid S_t)(G_t-b(S_t))\right].
$$

最常用 $b(s)=V_\psi(s)$，于是 $G_t-V_\psi(s_t)$ 是“实际比预期好多少”的优势估计。它不会改变期望梯度，却能减少“所有动作一起被偶然高/低回报带偏”的噪声。

---

### 2.8 Actor-Critic：一个负责出招，一个负责点评

纯 REINFORCE 要等完整回合拿到 $G_t$，方差高。Actor-Critic 增加 Critic 来学习 $V_\psi(s)$ 或 $Q_\psi(s,a)$，让 Actor 更快得到评价。

### 7.1 一步 TD advantage

若 critic 估计状态价值：

$$
\delta_t=R_{t+1}+\gamma(1-d_t)V_\psi(S_{t+1})-V_\psi(S_t).
$$

$\delta_t$ 同时是 critic 的 TD error，也可作为一步优势估计：

- $\delta_t>0$：这步比 critic 原先预期好，Actor 应增加这次动作概率。
- $\delta_t<0$：比预期差，Actor 应减少这次动作概率。

### 7.2 最小可用更新逻辑

```text
采样 (s, a, r, s', done)
critic target = r + gamma * (1 - done) * Vψ(s')
delta = critic target - Vψ(s)

更新 Critic：最小化 1/2 * delta²
更新 Actor：最大化 log πθ(a|s) * stopgrad(delta)
```

实作时若用 loss 最小化，Actor loss 可写为 $-\log\pi_\theta(a\mid s)\cdot\operatorname{stopgrad}(\delta)$。`stopgrad` 的意义是：更新 Actor 时将 Critic 的评价当作常数，不让“为了改变评价而改策略网络”的错误梯度混入。

### 7.3 它与后续算法的关系

- **A2C/A3C：** 多环境并行的 Actor-Critic 家族。
- **PPO：** 在策略更新幅度上加约束/裁剪，避免一次更新把策略改得太猛；实践中是很常见的 on-policy 基线。
- **DDPG/TD3/SAC：** 针对连续动作的 actor-critic 家族；SAC 还鼓励策略保持一定熵（探索性）。

先学懂“Actor 以优势更新、Critic 用 TD 学价值”，再学这些算法会轻松得多。

---

### 2.9 一张表：DQN、REINFORCE、Actor-Critic

| 维度 | DQN | REINFORCE | Actor-Critic |
|---|---|---|---|
| 直接学习对象 | $Q(s,a)$ | $\pi_\theta(a\mid s)$ | 策略 + $V$ 或 $Q$ |
| 决策 | $\arg\max_a Q(s,a)$ | 按概率分布采样 | 按 Actor 策略采样/输出 |
| 主学习信号 | TD target、TD error | 完整回报 $G_t$ | TD error / 优势 |
| 典型更新 | 最小化 Q 预测与 target 的差 | 最大化 log-prob × 回报 | Actor 用优势，Critic 用 TD loss |
| 数据性质 | 通常 off-policy、可 replay | 通常 on-policy | 可为 on-policy 或 off-policy |
| 动作空间 | 原版适合离散 | 离散/连续均可 | 离散/连续均可 |
| 主要难点 | 自举 + 函数近似会不稳 | 高方差、样本效率低 | Actor/Critic 互相依赖、超参更多 |

**on-policy/off-policy 的最简解释：** on-policy 主要使用当前正在训练的策略采样的数据；off-policy 可以用不同旧策略甚至随机策略采集的数据来学目标策略。经验回放让 DQN 高度依赖 off-policy 思想。

---

### 2.10 从你的原笔记出发，必须修正的 8 个点

1. **$R_t$ 与 $G_t$ 不同。** $R$ 是单步即时奖励；$G$（你笔记中的 $U$）才是折扣总回报。
2. **Q 不是“真实得分”。** $Q$ 是条件期望的估计；TD target 也是带偏差/噪声的学习目标，不是上帝给的真值。
3. **DQN target 应带终止遮罩。** 终止后不能再加 $\gamma\max Q(s',\cdot)$。
4. **DQN 不只有“平方误差 + 梯度下降”。** replay buffer、target network、探索策略是经典 DQN 能稳定工作的关键结构。
5. **REINFORCE 应使用回报 $G_t$ 或优势，而非含义不清的 $q_t$。** 若 $q_t$ 指 $Q_\pi(s_t,a_t)$，也可作为权重；但必须清楚它是长期动作价值，不是一步奖励。
6. **一次采样不是一次学会。** 策略梯度用采样给无偏方向估计，但估计方差可能很大。
7. **“离散动作要把所有动作概率加起来”不是连续动作困难的唯一原因。** 连续动作可用概率密度；真正变化是求和变积分，且 DQN 的 $\max_aQ$ 不再能枚举。
8. **“直接做决策”仍需要探索与评价。** 策略法不是不要打分；Actor-Critic 正是用价值网络辅助策略学习。

---

### 2.11 与你正在读的 Diffusion Policy 的关系

这点要分清：

- 论文 *Diffusion Policy* 的主设置是**模仿学习/行为克隆（BC）**：数据是专家示范 $(O_t,A_t)$，训练目标是预测加入动作序列的噪声；它不以环境奖励 $R$ 为核心监督。
- 本文的 RL 学习内容是让智能体通过回报优化策略；数据可能来自自己交互，目标是最大化 $J(\theta)$。
- 二者都谈“policy”，但**优化信号不同**：BC 是“像专家动作”，RL 是“让累积回报高”。
- 后续研究确实可将扩散模型用作 RL 的策略表示，但那是进一步工作；不能因此把这篇 Diffusion Policy 基础论文称为 DQN、PPO 或标准 RL 论文。

对你的毕设学习顺序，建议先掌握本文件的 MDP、价值、策略、Actor-Critic，再回到 Diffusion Policy，便能更准确比较：它为什么不用奖励、为何特别重视多峰动作分布、为何动作序列与闭环控制仍然重要。

---

### 2.12 学习检查：不看资料能否回答

### 基础

1. 写出 MDP 五元组，并解释哪一项代表“环境规律”。
2. $R_{t+1}$、$G_t$、$V_\pi(s)$、$Q_\pi(s,a)$ 分别是什么？
3. 为什么 $\gamma$ 既表达时间偏好，也有数学上的稳定作用？
4. 说出 Bellman 递推的自然语言版本。

### DQN

5. 从 $(s,a,r,s',d)$ 写出 DQN 的 TD target；为何有 $(1-d)$？
6. 为什么 target network 的输出不应跟在线网络一起反向传播？
7. replay buffer 和 $\epsilon$-greedy 分别解决什么问题？
8. 为什么原始 DQN 不适合直接穷举机械臂连续位姿动作？

### 策略梯度与 Actor-Critic

9. 为什么 REINFORCE 用 $\log\pi(a\mid s)$ 的梯度？
10. 高回报/低回报会怎样改变已采样动作的概率？
11. baseline 为何不改变期望梯度却能降低方差？
12. Actor 和 Critic 分别训练什么；TD error 为什么能当作优势近似？

### 迁移到论文

13. Diffusion Policy 的训练信号是奖励，还是示范动作的加噪/去噪目标？
14. “策略”这个词在 RL 与 BC 里相同在哪里、不同在哪里？

若第 5、9、12、13 题仍答不清，不要急着看 PPO/SAC；先回到第 4、6、7、10 节，用一个两状态两动作的玩具例子手算一次。

---

### 2.13 最小实践顺序

1. 用表格 Q-learning 解一个 GridWorld：手工打印 $Q(s,a)$，观察 TD error。
2. 用 PyTorch 写一个最小 DQN 跑 CartPole：先只理解数据流，不追求分数。
3. 写 REINFORCE：记录每回合 $G_t$、动作 log-prob、策略 loss。
4. 用 Actor-Critic/PPO 跑同一环境，对比“完整回报”和“优势”的训练波动。
5. 再回到机器人：理解连续动作通常需要 policy distribution/actor，而不是把所有角度离散得极细。

学习资源按用途分工：王树森课程用于建立中文直觉与主线；Sutton & Barto 用于查 MDP、TD、策略梯度的标准定义；OpenAI Spinning Up 用于阅读策略梯度、Actor-Critic、PPO 等实现导向解释。不要一开始同时复现多个复杂算法。

### 2.14 参考资料

- 王树森公开课及讲义仓库：<https://github.com/wangshusen/DRL>
- Sutton & Barto, *Reinforcement Learning: An Introduction*（第 2 版）：<https://mitpress.mit.edu/9780262039246/reinforcement-learning/>
- Mnih et al., DQN：<https://doi.org/10.1038/nature14236>
- Williams, REINFORCE：<https://doi.org/10.1007/bf00992696>
- OpenAI Spinning Up 的强化学习入门与算法说明：<https://spinningup.openai.com/en/latest/>

