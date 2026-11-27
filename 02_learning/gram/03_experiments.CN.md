# 03 实验精读：每张表、每张图在证明什么

读实验时，每张表/图都按五个问题来看：
1. **怎么读这张表/图？**（行、列、坐标轴各是什么）
2. **它想证明什么？**
3. **怎么比的？**（场景、对比方法、指标）
4. **每个数字说明了什么？**
5. **它没证明什么？如果我是审稿人会问什么？**

> 数字来源：Table III–V 直接取自正文表格。Fig. 4、Fig. 5 的数值是从 PDF 文字层提取的柱状图标注，**图中柱子与数字的对应关系需对照原图核对**，汇报时如果引用，请先打开 PDF 看一眼。

---

## 0. 先学会三个基本功

### 0.1 "归一化任务回报"是什么

**回报**就是一个回合里奖励的总和（见 [01 前置知识](01_background.CN.md) §1.2）。不同场景下回报的绝对值差别很大（比如上坡时天然得分低），不好横向比，所以作者把它**缩放到 [0, 1]**：1 表示满分，0 表示最差。

**【注意】** 论文**没有写具体怎么归一化**（除以理论最大回报？除以某个参考策略的回报？）。所以：
- 同一张表里的数字可以互相比较；
- 不要把 0.58 理解成"完成了 58% 的任务"，它只是一个相对分数。

**还有一个细节**：仿真评估时，代码只保留"速度跟踪"相关的奖励项（见 [04 代码精读](04_code_walkthrough.CN.md)），所以这个分数衡量的是**跟速度指令跟得好不好**，而不包括动作平滑等正则项。摔倒会提前结束回合，后面的分全拿不到，所以摔倒会大幅拉低分数。

### 0.2 "±"是什么

表里的 "0.92 ± 0.01" 中，± 后面的数通常有两种可能：
- **标准差（std）**：多次重复实验结果的波动大小；
- **标准误（standard error）**：标准差 ÷ √重复次数，衡量"平均值本身"估得准不准。

**论文没有写是哪一种，也没写重复了几次（几个随机种子）。**

**为什么这很重要**：判断两个数"差别是否真实"，要看差距和 ± 的相对大小。
- 例：0.92 ± 0.01 vs 0.87 ± 0.01，差 0.05，是 ± 的 5 倍，**差距可信**；
- 例：0.58 ± 0.01 vs 0.59 ± 0.01，差 0.01，和 ± 一样大，**基本可以认为没差别**。

一个粗略的经验：差距小于两个 ± 之和，就不要说"更好"。

### 0.3 "近 OOD / 远 OOD"各是什么

| 类别 | 包含的场景 | 怎么得到这一列的数字 |
|---|---|---|
| ID | 从训练范围（Table II）随机采样 | — |
| 近 OOD | 加 6 kg、5° 坡、5 cm 粗糙、后髋冻结 | **四个场景的平均** |
| 远 OOD | 加 9 kg、10° 坡、10 cm 粗糙、随机关节冻结 | **四个场景的平均** |

**近 OOD、远 OOD 的数字是四个不同场景平均出来的**，论文正文没有给每个场景单独的分数。

---

## 1. Table III：仿真主结果（最重要的一张表）

### 1.1 怎么读这张表

- **每一行**是一种算法：上面 4 行是 GRAM 和三个对比方法，下面 3 行是 GRAM 的消融版本；
- **每一列**是一类测试场景：ID、近 OOD、远 OOD；
- **每个格子**是归一化平均任务回报，越高越好。

**读表顺序建议**：先**竖着**看每一列谁最高（谁在这类场景最好），再**横着**看每一行从 ID 到远 OOD 掉了多少（谁的泛化最稳）。

### 1.2 数据

| 算法 | ID | 近 OOD | 远 OOD |
|---|---|---|---|
| **GRAM** | 0.92 ± 0.01 | **0.79 ± 0.02** | 0.58 ± 0.01 |
| 鲁棒 RL | 0.87 ± 0.01 | 0.74 ± 0.02 | **0.59 ± 0.01** |
| 情境 RL | **0.94 ± 0.00** | 0.75 ± 0.02 | 0.42 ± 0.03 |
| 域随机化 | 0.93 ± 0.01 | 0.74 ± 0.03 | 0.43 ± 0.03 |
| *消融* | | | |
| No φ_GRAM | 0.93 ± 0.00 | **0.80 ± 0.01** | 0.55 ± 0.02 |
| Separate Data | 0.92 ± 0.00 | 0.74 ± 0.02 | 0.46 ± 0.03 |
| Modular | 0.94 ± 0.00 | 0.74 ± 0.02 | 0.41 ± 0.02 |

### 1.3 文字版柱状图

每个 █ 代表 0.02 分（从 0.40 开始画，方便看差距）：

```
ID（训练见过的情况）
  情境RL   0.94 ███████████████████████████
  域随机化 0.93 ██████████████████████████▌
  GRAM     0.92 ██████████████████████████
  鲁棒RL   0.87 ███████████████████████▌        ← 明显偏保守

近 OOD（有点陌生）
  GRAM     0.79 ███████████████████▌            ← 四个方法里最高
  情境RL   0.75 █████████████████▌
  鲁棒RL   0.74 █████████████████
  域随机化 0.74 █████████████████

远 OOD（很陌生）
  鲁棒RL   0.59 █████████▌
  GRAM     0.58 █████████                       ← 与鲁棒 RL 持平
  域随机化 0.43 █▌
  情境RL   0.42 █                               ← 掉得最狠
```

### 1.4 每个数字说明什么

| 数字 | 说明什么 |
|---|---|
| 情境 RL ID 0.94 | 在见过的情况下，"知道环境再调整"是最好的策略 |
| 鲁棒 RL ID 0.87 | 一直保守的代价：比最好的低 0.07，是表里 ID 列最大的差距 |
| 情境 RL 远 OOD 0.42 | 从 ID 0.94 掉到 0.42，**掉了一半多**。估错了还很自信，后果严重 |
| 鲁棒 RL 远 OOD 0.59 | 从 0.87 掉到 0.59，掉得最少。保守的好处在这里体现 |
| GRAM ID 0.92 | 只比最好的低 0.02：大部分时刻 α≈1，按适应模式走 |
| GRAM 近 OOD 0.79 | 四种方法里最高：有点陌生但还能适应时，"能适应就适应" |
| GRAM 远 OOD 0.58 | 与鲁棒 RL 的 0.59 差 0.01，在 ± 范围内，等于追平 |
| 域随机化 ≈ 情境 RL | DR 在 ID（0.93）和远 OOD（0.43）都和情境 RL 很接近，说明在这个任务上"知道环境"带来的 ID 提升不大，而两者在 OOD 下都不鲁棒 |

### 1.5 三个对比方法各自的位置：取舍图

```
          ID 性能
            ↑
  情境RL 0.94 ●  DR 0.93 ●
            |      ● GRAM 0.92
            |
  鲁棒RL 0.87 ●
            +——————————————————→ 远 OOD 性能
           0.42   0.43      0.58 0.59
```

- **情境 RL**：在左上角，ID 最好、远 OOD 最差——典型的"适应型"；
- **鲁棒 RL**：在右下角，远 OOD 最好、ID 最差——典型的"保守型"；
- **GRAM**：在**右上角**，ID 只比最好的低 0.02，远 OOD 只比最好的低 0.01，**两头都接近最好**。

这张取舍图就是全文想表达的核心：**其他方法都在"ID 好"和"OOD 好"之间做取舍，GRAM 打破了这个取舍**。

### 1.6 作者的论述

**【原文】** "We see in Table III that contextual RL achieves the best ID performance as expected. GRAM achieves performance that is similar to contextual RL and domain randomization in ID contexts, while robust RL is overly conservative in this setting."

> 翻译：情境 RL 如预期在 ID 上表现最好。GRAM 在 ID 上的表现与情境 RL 和域随机化相近，而鲁棒 RL 在这种设定下过于保守。

**【原文】** "Conservative ID performance is the main drawback of robust RL methods, which can be meaningful in practical real-world settings where we expect to encounter ID conditions the majority of the time."

> 翻译：ID 表现保守是鲁棒 RL 方法的主要缺点，这在实际中很要紧，因为**我们预计大部分时间遇到的都是 ID 情况**。

**【原文】** "GRAM leverages its adaptation capabilities to maintain strong performance in near OOD contexts without being overly conservative, outperforming all other methods in this setting. As deployment environments become more difficult in the far OOD setting, GRAM achieves robust performance comparable to robust RL."

> 翻译：GRAM 利用其适应能力在近 OOD 情况下保持强性能而不过于保守，**在这种设定下优于所有其他方法**。当部署环境在远 OOD 设定下变得更难时，GRAM 取得与鲁棒 RL **相当**的鲁棒性能。

注意作者的措辞：近 OOD 用的是 "outperforming"（优于），远 OOD 用的是 "comparable"（相当）。**作者自己也没说远 OOD 比鲁棒 RL 好**。

### 1.7 消融实验：三个部件分别有没有用

**怎么读消融**：消融版本 = GRAM 去掉某个部件。如果去掉后分数下降，说明这个部件有用；下降越多，越重要。

| 消融 | 去掉了什么 | ID | 近 OOD | 远 OOD | 和 GRAM 比 | 说明 |
|---|---|---|---|---|---|---|
| No φ_GRAM | 用联合训练，但部署时**不用 α 混合**，直接用估计 | 0.93 | 0.80 | 0.55 | ID +0.01，近 OOD +0.01，远 OOD −0.03 | **α 混合主要在远 OOD 起作用**，在 ID 和近 OOD 反而略亏 |
| Separate Data | 一条轨迹只用一种分配，**不混合数据** | 0.92 | 0.74 | 0.46 | 近 OOD −0.05，远 OOD −0.12 | **混合数据收集很重要**，是三个部件里影响最大的 |
| Modular | 两个独立策略，按不确定性阈值**硬切换** | 0.94 | 0.74 | 0.41 | ID +0.02，近 OOD −0.05，远 OOD −0.17 | **统一架构 + 软混合远优于硬切换**；Modular 远 OOD 甚至比情境 RL 还差 |

**【原文】** "We see that these approaches can lead to comparable or slightly improved ID performance, but this comes at the cost of robustness in OOD scenarios. GRAM's single unified policy with its robust adaptation module and joint training pipeline provide both adaptive ID and robust OOD performance, a combination that is difficult to achieve with other approaches."

> 翻译：这些做法可能带来相当或略好的 ID 性能，但代价是 OOD 鲁棒性。GRAM 的单一统一策略、鲁棒适应模块和联合训练流程，同时提供了自适应的 ID 性能和鲁棒的 OOD 性能，这是其他方法难以做到的。

**Modular 为什么这么差？** 论文没有解释。一个合理的推测【推断】：两个独立策略在硬切换的瞬间动作会突变，而且"鲁棒策略"从没练过"从适应策略手里接过一个正在走的机器人"。GRAM 的混合数据收集正好练了这种衔接。

### 1.8 如果我是审稿人会问什么

1. **近 OOD 上 No φ_GRAM（0.80）比 GRAM（0.79）还高。** 正文说 GRAM 在近 OOD "outperforming all other methods"，这里的"other methods"指三个基线，不含消融。但这说明：**在近 OOD 上，α 混合本身没有带来收益**，近 OOD 的优势主要来自联合训练。
2. **远 OOD 上 GRAM（0.58）和鲁棒 RL（0.59）基本持平**，GRAM 在远 OOD 并没有超过鲁棒 RL，只是"追平"。
3. **No φ_GRAM 远 OOD 0.55，比情境 RL 的 0.42 高很多。** 这说明**联合训练本身**（让同一网络也学过 z=0 下被推的情况）就带来了大部分鲁棒性，α 混合只额外贡献 0.03。审稿人会问："GRAM 的提升主要来自不确定性模块，还是来自对抗训练？"
4. **"±"是什么？种子数多少？** 论文没写重复了几个随机种子，也没写 ± 是标准差还是标准误。差距只有 0.01–0.03 的比较（如 0.58 vs 0.59、0.79 vs 0.80）是否显著，无法判断。
5. **"近 OOD / 远 OOD"四类场景被平均在一起**。不同场景（加重、坡、粗糙、冻结）各自的分数没有在正文给出，可能某些场景 GRAM 好、某些差，平均后看不出来。
6. **归一化方式**没有说明（除以什么得到 [0,1]）。
7. **为什么没有"鲁棒 RL + 情境 RL 的简单平均"或"其他不确定性方法"作为基线？** 例如用集成或 MC Dropout 代替 epinet。

---

## 2. Fig. 4：α 的行为（证明"它确实能识别 OOD"）

### 2.1 怎么读这张图

Fig. 4 有三个子图（左、中、右），每个子图都有**上下两排**：
- **上排**：平均 α（所有时刻的 α 平均）；
- **下排**：**25%-CVaR α**（最小的 25% 个 α 的平均，反映"最没把握的那些时刻"有多不确定）。

α 越接近 1 = 越相信估计（适应模式）；越接近 0 = 越退回 z_rob（鲁棒模式）。

| 子图 | 横轴 | 纵轴 | 想证明 |
|---|---|---|---|
| 左 | 三类场景：ID / 近 OOD / 远 OOD | α（0–1） | 越陌生，α 越小 |
| 中 | 附加质量 0/3/6/9 kg；每个质量两根柱：默认训练 vs 宽训练 | α | α 的下降取决于"训练时见没见过"，不是取决于"质量本身大不大" |
| 右 | 时间 0–20 s（10 s 时突然加 9 kg）；两条曲线：默认训练 vs 宽训练 | α | α 能在运行中随变化实时下降 |

**图注原文**："GRAM average α (top) and 25%-CVaR α (bottom). Left: Deployment environments from Table III with default ID context set for training. Middle: Range of added base mass deployment scenarios (default vs. wide ID context sets for training). Right: 9 kg base mass added 10 seconds into deployment (default vs. wide ID context sets for training)."

> 翻译：GRAM 的平均 α（上）和 25%-CVaR α（下）。左：Table III 中的部署环境，用默认 ID 上下文集训练。中：不同附加质量的部署场景（默认与宽 ID 上下文集训练对比）。右：部署 10 秒时加上 9 kg 质量（默认与宽 ID 上下文集训练对比）。

### 2.2 读数（从 PDF 文字层提取，需对照原图）

**左图**：

| | ID | 近 OOD | 远 OOD |
|---|---|---|---|
| 平均 α | 约 0.95 | 约 0.88 | 约 0.82 |
| 25%-CVaR α | 约 0.76 | 约 0.46 | 约 0.28 |

**每个数字说明什么**：
- ID 平均 α 0.95：见过的情况下，绝大部分时刻都在适应模式；
- ID 的 CVaR 0.76：即使在 ID，最没把握的 25% 时刻 α 也会降到 0.76 左右，这和"β 取 0.90 分位数、约 10% 时刻 α<1"的设计一致；
- 远 OOD 平均 0.82、CVaR 0.28：大部分时刻仍在适应，但有一部分时刻几乎完全退回。

**中图**：
- 默认训练（质量范围 [−1, 3] kg）下，质量越大 α 越小：0 kg、3 kg 时平均 α 约 0.95，6 kg 约 0.86，9 kg 约 0.72；CVaR 在 9 kg 时约 0.21；
- 宽训练（质量范围 [−1, 9] kg）下，0–9 kg 的平均 α 都维持在约 0.91–0.95。

（具体每根柱子的数值以原图为准。）

**右图（原图为曲线；下面的趋势是根据正文和图注推断的，请看原图确认）**：
- 横轴是时间 0–20 s，第 10 s 加上 9 kg；
- 默认训练的曲线：前 10 s α 在高位，加重后 α 明显下降；
- 宽训练的曲线：加重后 α 基本不变或只轻微波动，因为 9 kg 在它的训练范围内。

### 2.3 关键解读

**【原文】** "As we consider generalization beyond the ID context set seen during training, GRAM automatically identifies and reacts to the increased uncertainty of OOD deployment environments by decreasing the coefficient α_t in (9)."

> 翻译：当考虑训练所见 ID 上下文集之外的泛化时，GRAM 通过降低式 (9) 中的系数 α，**自动识别并应对** OOD 部署环境中增加的不确定性。

**【原文】** "Note that OOD environments lead to high uncertainty at certain timesteps during deployment (resulting in low 25%-CVaR α), but for many timesteps the adaptive locomotion skills learned during training can still be applied (resulting in moderate α on average)."

> 翻译：注意，OOD 环境会在部署中的**某些时刻**导致高不确定性（所以 25%-CVaR α 较低），但在**很多时刻**训练中学到的适应性运动技能仍然可用（所以平均 α 处于中等水平）。

**【解读】**
- 即使在远 OOD，**平均 α 也有 0.8 左右**，说明 GRAM 大部分时刻仍然在"适应"，只在少数时刻退回鲁棒。
- 所以 GRAM 不是"进入 OOD 就一直保守"，而是**逐时刻地**、时而适应时而保守。
- 中图是全文最有说服力的证据之一：**同样是 9 kg，训练见过就不退回，没见过就退回**，说明 α 衡量的确实是"见没见过"，而不是"质量大不大"。

**【原文】** "As shown in Fig. 4, GRAM detects low uncertainty (high average and 25%-CVaR α) across a range of added base masses when trained on the wide ID context set because these scenarios were all seen during training, resulting in adaptive performance similar to contextual RL. When trained on the default ID context set, GRAM decreases α for large added base masses to capture OOD environment uncertainty, achieving robust performance similar to robust RL."

> 翻译：如 Fig. 4 所示，用宽 ID 上下文集训练时，GRAM 在各种附加质量下都检测到低不确定性（平均和 25%-CVaR α 都高），因为这些场景训练时都见过，所以表现出与情境 RL 相似的适应性能。用默认 ID 上下文集训练时，GRAM 对大的附加质量降低 α 以反映 OOD 环境的不确定性，取得与鲁棒 RL 相似的鲁棒性能。

### 2.4 如果我是审稿人会问什么

1. **右图（10 s 时加 9 kg）在官方代码里找不到对应实现**，复现需要自己写运行中加质量的事件。
2. α 下降之后，**多快能降下来？恢复要多久？** 论文没有量化 α 的响应时间。历史只有 16 步（0.32 s），理论上反应应该很快，但没有数据。
3. 平均 α 在远 OOD 还有 0.82，那么**哪些时刻在退回？** 是刚落地时？是加速时？论文没有分析。
4. **我们的切入点**：如果 OOD 只来自一个因素（比如只是加重），α 下降会把**所有**隐变量维度一起缩小，包括本来还准确的摩擦估计。论文没有分析"部分维度可信"的情况。
5. **只画了质量这一种因素的扫描**。摩擦、电机强度超出范围时 α 怎么变，没有给出。

---

## 3. Fig. 5：训练范围的影响（证明"GRAM 能自动适应不同的训练设定"）

### 3.1 怎么读这张图

- 两个子图并排：**左边 = 默认训练**，**右边 = 宽训练**；
- 每个子图里 4 根柱子，分别是 GRAM、鲁棒 RL、情境 RL、域随机化；
- 纵轴是归一化任务回报；**测试场景都是"加 9 kg"**；
- 注意：两个子图的**纵轴刻度不同**（左边从 0.25 到 1.00，右边从 0.70 到 1.00），直接看柱子高度会被误导，要看数字。

**图注原文**："Average normalized task returns for 9 kg added base mass scenario. Left: Training with default ID context set from Table II. Right: Training across wide added base mass range of [−1.00, 9.00]."

> 翻译：9 kg 附加质量场景下的平均归一化任务回报。左：用 Table II 的默认 ID 上下文集训练。右：在 [−1, 9] kg 的宽附加质量范围上训练。

### 3.2 设定

在 9 kg 负载下评估：
- **默认训练**：质量范围 [−1, 3] kg，9 kg 是远 OOD；
- **宽训练**：质量范围 [−1, 9] kg，9 kg 是 ID。

**这个设计巧在哪**：测试场景完全一样（都是 9 kg），只改变"训练时见没见过"。如果某个方法的表现随训练范围大幅翻转，就说明它依赖训练范围选得对不对。

### 3.3 读数（需对照原图）

| 算法 | 默认训练（9 kg 为 OOD） | 宽训练（9 kg 为 ID） | 变化 |
|---|---|---|---|
| GRAM | 约 0.50 | 约 0.89 | 两种设定都接近当时最好 |
| 鲁棒 RL | 约 0.50 | 约 0.78 | 宽训练时被三种方法甩开 |
| 情境 RL | 约 0.31 | 约 0.92 | 从最差变成最好 |
| 域随机化 | 约 0.31 | 约 0.90 | 同上 |

**文字版对比**：

```
默认训练（9 kg 没见过）          宽训练（9 kg 见过）
  GRAM    0.50 █████████████       情境RL  0.92 ███████████████████████
  鲁棒RL  0.50 █████████████       域随机化0.90 ██████████████████████▌
  情境RL  0.31 ████████            GRAM    0.89 ██████████████████████
  域随机化0.31 ████████            鲁棒RL  0.78 ███████████████████▌
```

### 3.4 每个数字说明什么

- **情境 RL 0.31 → 0.92**：同一个方法，只因训练范围不同，表现差三倍。说明情境 RL **非常依赖训练范围**；
- **鲁棒 RL 0.50 → 0.78**：在 9 kg 见过的情况下仍然最差，说明鲁棒 RL **不会利用已知信息**，一直保守；
- **GRAM 0.50 → 0.89**：两种情况下都接近当时最好的方法。

**【原文】** "We see in Fig. 5 that the generalization capabilities of the baseline algorithms strongly depend on the set of ID contexts seen during training... Unlike the baseline algorithms, GRAM identifies ID contexts from OOD contexts at deployment time in a way that automatically adjusts for different choices of C_ID."

> 翻译：Fig. 5 表明，基线算法的泛化能力**强烈依赖**训练时见过的 ID 上下文集……与基线不同，GRAM 在部署时区分 ID 与 OOD 上下文的方式，能**自动适应**不同的 C_ID 选择。

**为什么这对实际应用重要**：实际部署前，你不知道会遇到多重的负载。用 GRAM，你不需要事先"猜对"训练范围：猜大了，它像情境 RL；猜小了，它像鲁棒 RL。

### 3.5 如果我是审稿人会问什么

- 宽训练下，GRAM（约 0.89）仍低于情境 RL（约 0.92），说明"不确定性的定标"让它在 ID 下也有一部分时刻退回，付出了一点 ID 性能。
- 在默认训练下，GRAM 和鲁棒 RL 都只有 0.50 左右，**9 kg 的绝对表现并不好**。GRAM 的优势是"不比鲁棒 RL 差"，而不是"解决了 9 kg"。
- 只对"质量"这一个因素做了宽/窄训练的对比，其他因素没做。

---

## 4. Table IV：实机中等难度场景（所有方法都能完成）

### 4.1 怎么读这张表

- **行**：4 个场景 + 平均 + 成功率；
- **列**：3 个算法（实机没有跑域随机化）；
- **格子**：从起点走到 6 m 外终点所用的时间（秒），**越短越好**，± 是 5 次的波动；
- 成功率：20/20 = 4 个场景 × 5 次全部成功。

**任务**：前进速度指令 1.0 m/s，走 6 m。所以**理想时间是 6 s**。实际都超过 6 s，部分原因是起步加速、部分原因是跟不上指令速度。

### 4.2 数据

| 场景 | GRAM | 鲁棒 RL | 情境 RL |
|---|---|---|---|
| 正常 | **7.95 ± 0.05** | 8.07 ± 0.18 | 8.62 ± 0.04 |
| 后髋关节冻结 | **7.70 ± 0.16** | 8.79 ± 0.20 | 9.33 ± 0.30 |
| 5° 下坡 | **6.97 ± 0.17** | 7.05 ± 0.16 | 7.05 ± 0.15 |
| 5° 上坡 | **10.03 ± 0.23** | 10.92 ± 0.50 | 12.51 ± 0.35 |
| 平均 | **8.17** | 8.71 | 9.38 |
| 成功率 | 20/20 | 20/20 | 20/20 |

**换算成平均速度**（6 m ÷ 时间，便于直观感受）：

| 场景 | GRAM | 鲁棒 RL | 情境 RL |
|---|---|---|---|
| 正常 | 0.75 m/s | 0.74 m/s | 0.70 m/s |
| 后髋冻结 | 0.78 m/s | 0.68 m/s | 0.64 m/s |
| 5° 上坡 | 0.60 m/s | 0.55 m/s | 0.48 m/s |

（含起步加速段，所以都低于指令的 1.0 m/s。）

### 4.3 每个数字说明什么

| 观察 | 说明什么 |
|---|---|
| GRAM 每个场景都最快 | 中等变化下，GRAM 的"能适应就适应"有效 |
| 正常场景 GRAM 7.95 vs 鲁棒 RL 8.07，差 0.12 s | 差距和鲁棒 RL 的 ±0.18 差不多，**正常场景两者其实接近** |
| 后髋冻结 GRAM 7.70 vs 鲁棒 RL 8.79，差 1.09 s | 差距明显 |
| 5° 下坡三者几乎一样 | 下坡本身帮助前进，难度低 |
| 5° 上坡 情境 RL 12.51 s | 比 GRAM 慢 25%，上坡对情境 RL 来说是 OOD（训练全是平地） |
| **情境 RL 正常场景也最慢（8.62 s）** | 对它来说，真实世界本身就有点 OOD |

**【原文】** "Robust RL can be overly conservative, which leads to slower time-to-goal in these moderate scenarios. Contextual RL suffers from a sim-to-real gap due to its lack of robustness when only trained on the moderate variations described by C_ID in Table II, resulting in the slowest time-to-goal across all scenarios."

> 翻译：鲁棒 RL 可能过于保守，导致这些中等场景中到达时间较慢。情境 RL 由于只在 Table II 的中等变化上训练、缺乏鲁棒性，**受到仿真到实机差距的影响**，在所有场景中到达时间都最慢。

### 4.4 如果我是审稿人会问什么

1. **后髋冻结时 GRAM（7.70 s）比正常（7.95 s）还快**，这有点反直觉。作者没有解释。可能是冻结后步态变化、或者 5 次样本的波动。**这是一个很好的提问点**，体现你认真看了数据。
2. **实机上冻结关节是怎么实现的？** 论文没写。仿真代码里"冻结"是把动作倍数置 0（关节被拉回默认角度），实机可能是锁位置，两者不一定等价。
3. 每格只有 5 次，样本量小。
4. **到达时间只反映速度**，没有报告能耗、姿态稳定性、跟踪误差等其他指标。

---

## 5. Table V：实机困难场景（至少一个基线失败）

### 5.1 怎么读这张表

- **行**：3 个困难场景 + 合计；
- **列**：3 个算法；
- **格子**：成功次数/尝试次数，每格 5 次；
- 这 3 个场景的共同点：**都远超训练范围**（训练只有平地、最多 3 kg）。

### 5.2 数据

| 场景 | GRAM | 鲁棒 RL | 情境 RL |
|---|---|---|---|
| 9 kg 负载 | 5/5 | （见下） | 0/5 |
| 湿滑地面（白板） | 5/5 | （见下） | 2/5 |
| 坡道接泡沫 | 5/5 | （见下） | 0/5 |
| **合计** | **15/15** | **12/15** | **2/15** |

> 鲁棒 RL 的分场景数字在 PDF 文字层里排版错位（三个场景是 5/5、4/5、3/5 的某种组合），合计 12/15 是确定的。引用分场景数字前请看原图。

**场景说明**（Fig. 6 图注："Difficult controlled hardware experiments where at least one baseline algorithm fails. GRAM achieves 100% success rate on these tasks. From top to bottom: 9 kg Payload, Slippery, Ramp to Foam."）：
- **9 kg 负载**：背上 9 kg，是训练上限 3 kg 的三倍；Go2 本体约 15 kg【推断：常见公开参数，论文未写】，9 kg 是很大的负担；
- **湿滑地面**：在白板上走，摩擦很低；
- **坡道接泡沫**：先上一段坡，再走上软泡沫。

### 5.3 失败原因（作者描述）

**【原文】** "Because these scenarios represent far OOD environment dynamics relative to the set of ID training environments, contextual RL only reached the goal in 2 out of 15 trials. Many of these failures occurred when dynamics changed within a trial, such as when the robot first stepped onto the foam or slippery whiteboard."

> 翻译：由于这些场景相对于 ID 训练环境属于远 OOD 动力学，情境 RL 在 15 次中只有 2 次到达终点。**许多失败发生在试验过程中动力学变化的时刻**，例如机器人第一次踩上泡沫或湿滑白板的时候。

**【原文】** "Robust RL successfully reached the goal in 12 out of 15 trials, with failures caused by the robot becoming stuck due to the conservative wide gait learned from robust training."

> 翻译：鲁棒 RL 在 15 次中成功 12 次，失败原因是机器人**因鲁棒训练学到的保守宽步态而卡住**。

| 算法 | 失败类型 | 根本原因 |
|---|---|---|
| 情境 RL | 踩上新地面的瞬间失败 | **估错了还很自信**，按错误估计调整动作 |
| 鲁棒 RL | 卡住走不动 | **太保守**，宽步态在某些地形上反而不行 |
| GRAM | 无 | 两种失败都避开了 |

### 5.4 解读

这张表最能说明 GRAM 的卖点：
- 情境 RL 的失败 = "**适应型方法估错还很自信**"；
- 鲁棒 RL 的失败 = "**保守型方法太保守**"；
- GRAM 两种失败都避开了。

### 5.5 如果我是审稿人会问什么

- 每个场景 5 次，15 次全部成功。从统计上看，15/15 vs 12/15 的差距**并不显著**（样本太少）。
- **"动力学在一次试验中途变化"正是 GRAM 的强项**（白板、泡沫都是走上去才变）。这和我们关注的"运行中突然变化"高度相关，但论文没有给出 α 在这些时刻的变化曲线。
- 只有成功率，没有记录 GRAM 在这些场景里**花了多少时间**，是否也变得很慢。

---

## 6. Fig. 7：户外定性实验

**图注原文**："Qualitative outdoor experiments. GRAM is trained in simulation on flat, solid ground, and achieves robust zero-shot sim-to-real transfer across a variety of outdoor terrains not seen during training. From left to right: grass with storm drain, uneven dirt, wood chips."

> 翻译：户外定性实验。GRAM 在仿真中只在平坦坚硬地面上训练，在多种训练中没见过的户外地形上实现了鲁棒的零样本仿真到实机迁移。从左到右：带雨水篦子的草地、不平的土路、木屑。

- **只有照片和视频，没有数字**，属于"定性展示"；
- 作用：说明在训练完全没见过的户外地形上也能走；
- **没有和基线对比**，所以不能说明 GRAM 比别的方法好，只能说明 GRAM 能走。

---

## 7. 实验部分整体评价

### 7.1 设计得好的地方

| 优点 | 说明 |
|---|---|
| 对比方法有代表性 | 正好是"适应"和"鲁棒"两个极端，加上最常用的 DR |
| 消融直接对应贡献 | 三个消融分别验证 α 混合、混合数据、统一架构 |
| Fig. 5 设计巧妙 | 同一个 9 kg，换训练范围，结论随之翻转，有力地说明 α 衡量的是"见没见过" |
| 只在平地训练 | 排除"OOD 场景其实练过"的嫌疑，泛化证据更干净 |
| 实机有失败分析 | 不只报成功率，还说明基线为什么失败 |

### 7.2 不足

| 不足 | 影响 |
|---|---|
| 种子数、± 的含义未写 | 0.01–0.03 级别的差距无法判断显著性 |
| 近/远 OOD 四类场景合并报告 | 看不出各场景的差异 |
| 对抗者只有推力一种 | 鲁棒性来源单一，作者自己也承认 |
| 运行中变化只有一个仿真例子（Fig. 4 右）且无代码 | "突然变化"这个最有实际意义的场景，定量证据最少 |
| 没有与其他不确定性方法比 | 如集成、MC Dropout、重构误差等，无法判断 epinet 是否必要 |
| 没有与 HIMLoco、DreamWaQ 等更新的自适应方法比 | 情境 RL 基线代表的是 2020–2024 年的教师—学生 |
| 没有传统控制基线 | 例如 MPC 或基于模型的鲁棒控制器，控制背景的审稿人可能会问 |
| 实机每格 5 次 | 样本量小 |
| 没有分析"部分因素 OOD"的情况 | 只有整体 α，看不出哪部分导致退回 |

最后两行，正是我们方向的出发点。

### 7.3 把所有实验串成一条论证链

```
Table III  ── GRAM 在仿真里"ID 接近最好、远 OOD 接近最好"         （主张成立）
   │
   ├─ 消融   ── 三个部件各自有用，混合数据最重要                   （为什么成立）
   │
Fig. 4     ── α 确实在 OOD 时降低，而且是逐时刻的                 （机制是真的在起作用）
   │
Fig. 5     ── α 衡量的是"见没见过"，能自动适应训练范围             （机制的本质）
   │
Table IV/V ── 实机上同样成立，且避开了两类基线各自的失败方式       （不只是仿真现象）
   │
Fig. 7     ── 户外没见过的地形也能走                              （定性补充）
```

**读论文的一个通用技巧**：先看实验部分的论证链，再回头看方法，就能明白作者"为什么要设计这个部件"。

---

## 自测题

1. Table III 中，哪个数字说明"α 混合"对远 OOD 有用？贡献了多少？
2. 哪个消融说明混合数据收集的重要性？
3. 为什么说 Fig. 5 证明了 α 衡量的是"见没见过"？
4. 实机上情境 RL 为什么在正常场景下也最慢？
5. 如果老师问"GRAM 在远 OOD 上比鲁棒 RL 好吗"，怎么回答？
6. 举两个你认为实验设计不够充分的地方。
7. 读 Fig. 5 时为什么不能直接比较左右两个子图的柱子高度？
8. 25%-CVaR α 和平均 α 各反映什么？为什么都要画？

<details>
<summary>参考答案</summary>

1. GRAM 0.58 vs No φ_GRAM 0.55，α 混合贡献约 0.03。
2. Separate Data：远 OOD 从 0.58 降到 0.46。
3. 同样是 9 kg：默认训练（没见过）时 α 明显下降，宽训练（见过）时 α 保持高位，GRAM 的表现也分别接近鲁棒 RL 和情境 RL。
4. 它只在中等变化下训练、缺少鲁棒性，真实世界和仿真的差距本身就超出了它的适应范围，即仿真到实机的差距。
5. 不比它好，基本持平（0.58 vs 0.59）。GRAM 的优势是"远 OOD 追平鲁棒 RL 的同时，ID 和近 OOD 明显好于鲁棒 RL"。
6. 例如：种子数和 ± 含义未写；对抗者只有推力；没有和其他不确定性方法或传统控制方法比；运行中变化的定量实验太少；没有按场景分开报告。
7. 两个子图的纵轴刻度不同（左边从 0.25 起，右边从 0.70 起），要看标注的数字。
8. 平均 α 反映"大部分时间在什么模式"；25%-CVaR α 反映"最没把握的时刻退回得有多深"。只看平均会掩盖短暂但深度的退回，所以两个都要看。
</details>
