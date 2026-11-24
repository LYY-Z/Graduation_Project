# 条件动作扩散与关键公式

## 1. 从普通 DDPM 只做三处替换

普通 DDPM 的任务是从噪声生成一个样本：

\[
x^K\rightarrow x^{K-1}\rightarrow\cdots\rightarrow x^0
\]

Diffusion Policy 保留这套去噪机制，但做三处替换：

| 普通 DDPM | Diffusion Policy |
|---|---|
| 干净样本 \(x^0\) | 干净未来动作序列 \(A_t^0\) |
| 带噪样本 \(x^k\) | 带噪未来动作序列 \(A_t^k\) |
| 无条件噪声预测器 \(\epsilon_\theta(x^k,k)\) | 观察条件下的噪声预测器 \(\epsilon_\theta(O_t,A_t^k,k)\) |

最重要的结论是：

\[
\boxed{
\text{被逐步加噪和去噪的是动作序列 }A_t,\text{ 不是观察 }O_t
}
\]

观察只告诉模型“当前场景是什么样”；动作序列才是模型需要生成的对象。

---

## 2. 动作序列在计算机中是什么形状

若动作维度为 \(D_a\)，预测时域为 \(T_p\)，一条干净动作序列可以写成：

\[
A_t^0\in\mathbb R^{T_p\times D_a}
\]

例如机械臂动作是末端位姿增量加夹爪状态：

\[
D_a=7
\]

预测 16 步：

\[
T_p=16
\]

那么单条样本的形状为：

\[
[16,7]
\]

训练时使用批量 \(B\)：

\[
[B,T_p,D_a]
\]

动作序列中的每一个数都可能被加高斯噪声。它与图像 DDPM 的区别仅在于张量维度不同。

---

## 3. 条件 \(O_t\) 是什么

观察 \(O_t\) 可以包含最近 \(T_o\) 步的信息：

\[
O_t=
(I_{t-T_o+1:t},s_{t-T_o+1:t})
\]

其中：

- \(I\)：一个或多个相机图像；
- \(s\)：本体感觉，例如末端位姿、关节位置、夹爪开度；
- \(T_o\)：观察时域。

图像通常先经过视觉编码器，得到特征：

\[
f_t=\operatorname{Encoder}(O_t)
\]

去噪网络实际接收：

\[
\epsilon_\theta(f_t,A_t^k,k)
\]

为了书写简单，论文记为：

\[
\epsilon_\theta(O_t,A_t^k,k)
\]

它的输出形状与带噪动作相同：

\[
\epsilon_\theta(O_t,A_t^k,k)
\in\mathbb R^{T_p\times D_a}
\]

每个输出数字都是该动作元素的噪声预测，不是一个高层语言动作。

---

## 4. 训练：怎样把示范变成练习题

训练数据中有专家演示：

\[
(O_t,A_t^0)
\]

其中 \(A_t^0\) 是专家从控制时刻 \(t\) 开始的未来动作片段。

一次训练迭代做以下事情。

### 第一步：取干净动作序列

\[
A_t^0
\]

例如它包含“靠近、抓取、抬起、放下”全过程中的连续控制量。

### 第二步：随机选择扩散步

\[
k\sim\operatorname{Uniform}\{1,\ldots,K\}
\]

模型因此会同时学习轻度、中度和重度噪声下的去噪。

### 第三步：抽取高斯噪声

\[
\epsilon\sim\mathcal N(0,I)
\]

噪声张量与 \(A_t^0\) 形状完全相同。

### 第四步：构造带噪动作

使用标准 DDPM 写法：

\[
A_t^k
=
\sqrt{\bar\alpha_k}A_t^0
+
\sqrt{1-\bar\alpha_k}\epsilon
\]

论文第 2 节有时将不同噪声等级写成 \(\epsilon^k\)，并简写为：

\[
A_t^0+\epsilon^k
\]

两种写法表达的核心相同：在由 \(k\) 决定的尺度下，给干净动作序列注入已知高斯噪声。标准实现通常由 scheduler 完成精确缩放。

### 第五步：预测噪声

\[
\hat\epsilon=
\epsilon_\theta(O_t,A_t^k,k)
\]

网络同时利用：

- 当前场景和机器人状态 \(O_t\)；
- 当前带噪动作序列 \(A_t^k\)；
- 当前噪声等级 \(k\)。

### 第六步：计算损失并更新参数

\[
\boxed{
\mathcal L=
\left\|
\epsilon-
\epsilon_\theta(O_t,A_t^k,k)
\right\|^2
}
\]

网络预测得越接近实际加入的噪声，损失越小。

训练伪代码：

    取一批示范窗口 (O_t, A_t^0)
    随机抽取每条样本的扩散步 k
    epsilon = 与 A_t^0 同形状的标准高斯噪声
    A_t^k = scheduler.add_noise(A_t^0, epsilon, k)
    epsilon_hat = model(O_t, A_t^k, k)
    loss = 平均平方误差(epsilon_hat, epsilon)
    对网络参数 theta 做梯度下降

---

## 5. 论文中的公式 (4) 和 (5)

论文将 Diffusion Policy 的反向更新写为：

\[
A_t^{k-1}
=
\alpha
\left(
A_t^k
-\gamma\epsilon_\theta(O_t,A_t^k,k)
+\mathcal N(0,\sigma^2I)
\right)
\]

这是一种将调度参数合并表达的写法：

- \(A_t^k\)：当前带噪动作序列；
- \(\epsilon_\theta(O_t,A_t^k,k)\)：网络预测的噪声或等价的去噪方向；
- \(\gamma\)：本步沿去噪方向移动多少；
- \(\alpha\)：本步的缩放；
- \(\mathcal N(0,\sigma^2I)\)：反向采样中的随机扰动；
- \(A_t^{k-1}\)：更干净一级的动作序列。

它与标准 DDPM 形式：

\[
x_{k-1}=
\mu_\theta(x_k,k)+\sigma_kz
\]

表达的是同一个过程。不要将论文中的 \(\alpha,\gamma,\sigma\) 逐字当成基础 DDPM 文档里的同名系数；论文这里强调的是“由噪声日程控制的一步随机去噪更新”。

论文训练公式为：

\[
\boxed{
\mathcal L
=
\operatorname{MSE}
\left(
\epsilon^k,
\epsilon_\theta(O_t,A_t^0+\epsilon^k,k)
\right)
}
\]

它表达的就是上一节的六步训练过程。

---

## 6. 推理：机器人真正如何获得动作

新场景下没有专家动作 \(A_t^0\)，只有当前观察 \(O_t\)。因此先从纯随机动作开始：

\[
A_t^K\sim\mathcal N(0,I)
\]

然后从 \(k=K\) 循环到 1：

1. 输入 \(O_t,A_t^k,k\)；
2. 网络预测当前动作序列中的噪声；
3. scheduler 用噪声预测计算更干净的 \(A_t^{k-1}\)；
4. 重复直到得到 \(A_t^0\)。

伪代码：

    读取当前观察 O_t
    编码观察特征
    A = 与动作序列同形状的标准高斯噪声
    for k = K, K-1, ..., 1:
        epsilon_hat = model(O_t, A, k)
        A = scheduler.step(epsilon_hat, k, A)
    返回 A

最终返回的是：

\[
A_t^0=(a_t,a_{t+1},\ldots,a_{t+T_p-1})
\]

即一段未来连续动作。

---

## 7. 为什么观察不参与加噪

有一种做法是把观察和动作拼成一个长向量，再同时去噪：

\[
(O_t,A_t)
\]

论文选择不这么做，而是直接学习：

\[
p(A_t\mid O_t)
\]

原因有两个。

### 7.1 观察不是需要生成的未知量

机器人已经拍到了当前图像，也已经读到了自身状态。没有必要在生成动作时重新“猜一遍未来状态或当前图像”。

### 7.2 视觉特征可以只提取一次

一次动作生成需要 \(K\) 次去噪。如果观察也在去噪张量中，或每次都重新编码图像，计算会很昂贵。

论文的做法是：

\[
O_t\rightarrow f_t
\]

先编码一次视觉特征 \(f_t\)，随后在 \(K\) 次去噪中重复使用它。这有助于满足实时控制需求，也使视觉编码器能端到端训练。

---

## 8. 条件扩散为什么能解决多种正确动作

考虑观察 \(O_t\) 固定，而合理动作序列有两类：

\[
A^{\mathrm{left}}
\quad\text{和}\quad
A^{\mathrm{right}}
\]

普通回归可能输出平均动作：

\[
\frac12
\left(
A^{\mathrm{left}}+A^{\mathrm{right}}
\right)
\]

而扩散模型从不同随机初值：

\[
A_t^K\sim\mathcal N(0,I)
\]

出发，经多步去噪后可以落在不同高概率区域：

\[
A_t^K\rightarrow A^{\mathrm{left}}
\]

或：

\[
A_t^K\rightarrow A^{\mathrm{right}}
\]

一次 rollout 内通常会形成一个一致的动作序列；这比每个单步独立随机选左或右更不容易抖动。

---

## 9. 本章自测

1. Diffusion Policy 中被加噪的张量是什么？
2. 为什么 \(O_t\) 是条件而不是去噪对象？
3. \(k\) 与机器人真实控制时刻 \(t\) 的区别是什么？
4. 训练时真实噪声为什么是免费的监督标签？
5. 推理时为什么从随机动作序列开始？
6. 论文公式中的 \(\alpha,\gamma,\sigma\) 在概念上分别控制什么？
7. 为什么同一观察下不同随机初值可以产生不同合理动作？

## 10. 论文式 (1) 的完整角色：反向去噪一步

将 DDPM 的样本 \(x\) 换成动作计划 \(A_t\)，典型反向更新写为：

\[
A_t^{k-1}=
\frac{1}{\sqrt{\alpha_k}}
\left(
A_t^k-
\frac{\beta_k}{\sqrt{1-\bar\alpha_k}}
\epsilon_\theta(O_t,A_t^k,k)
\right)
+\sigma_kz.
\]

它不是新的、比 DDPM 更简单的政策公式，而是同一条 DDPM 反向采样式的动作版本。

| 部分 | 在做什么 |
|---|---|
| \(A_t^k\) | 当前带噪的整段动作计划 |
| \(\epsilon_\theta(O_t,A_t^k,k)\) | 根据观察判断其中的噪声 |
| 括号中的减法 | 用预测噪声修正计划，得到更干净方向 |
| \(1/\sqrt{\alpha_k}\) | 贝叶斯后验整理后必须存在的尺度修正 |
| \(\sigma_kz\) | 从反向高斯分布围绕中心抽取一个具体样本 |

\(\sigma_kz\) 不是“又把执行动作变随机”，而是规划过程中从条件动作分布采样的随机部分。最后拿去执行的是多轮去噪结果的前段。

## 11. KL 散度：在推导中衡量两个分布差多少

KL 散度比较两个概率分布 \(q\) 和 \(p\)：

\[
D_{\mathrm{KL}}(q\|p)
=\mathbb E_q\left[\log\frac{q}{p}\right].
\]

它不是某个真实动作数据，也不是“再额外拿一条动作监督”。直觉上，它衡量：如果真实的反向分布是 \(q\)，模型写出的反向分布是 \(p_\theta\)，二者有多不一致。

DDPM 的变分推导会出现 KL 项；在常用固定方差和噪声参数化下，训练可化为（或常用近似为）预测已注入噪声的 MSE：

\[
\|\epsilon-\epsilon_\theta(O_t,A_t^k,k)\|^2.
\]

因此实践训练循环通常只显式计算噪声 MSE。不要理解成“每个 batch 同时独立计算一份 MSE 再额外计算一份 KL”；KL 解释了这个训练目标从何而来。

## 12. DDIM：为什么能跳过中间去噪等级

若当前在 \(k\) 级，网络可先估计干净计划：

\[
\hat A_t^0=
\frac{A_t^k-\sqrt{1-\bar\alpha_k}
\epsilon_\theta(O_t,A_t^k,k)}
{\sqrt{\bar\alpha_k}}.
\]

然后要跳到任意更干净等级 \(j<k\) 时，确定性 DDIM 重新组合：

\[
A_t^j=
\sqrt{\bar\alpha_j}\hat A_t^0+
\sqrt{1-\bar\alpha_j}
\epsilon_\theta(O_t,A_t^k,k).
\]

原因是前向闭式式本来就说“任一级 = 干净计划的一部分 + 标准噪声的一部分”。已估计这两部分后，换成 \(j\) 的系数即可。DDIM 与相邻 DDPM 后验抽样不同，但可复用同一个训练网络；Diffusion Policy 正利用这一点减少推理时间。

## 13. score：不是训练参数梯度，而是采样时的动作方向

对带噪动作计划的条件密度 \(p_k(A^k\mid O)\)，score 定义为：

\[
s_k(A^k,O)=\nabla_{A^k}\log p_k(A^k\mid O).
\]

它的方向指向“动作计划在当前观察下更高概率的区域”。这发生在**推理/采样的概念层面**，不是用来更新网络参数的 \(\nabla_\theta L\)。

为什么网络预测噪声可以给出 score？一维高斯

\[
y\sim\mathcal N(\mu,\sigma^2)
\]

的 score 为：

\[
\frac{\partial\log p(y)}{\partial y}
=-\frac{y-\mu}{\sigma^2}.
\]

而前向噪声残差 \(y-\mu=\sigma\epsilon\)，代入得到：

\[
-\frac{\sigma\epsilon}{\sigma^2}
=-\frac{\epsilon}{\sigma}.
\]

在第 \(k\) 个扩散等级，\(\sigma=\sqrt{1-\bar\alpha_k}\)，于是训练好后：

\[
\boxed{
\hat s_\theta(A^k,O,k)=
-\frac{\epsilon_\theta(O,A^k,k)}
{\sqrt{1-\bar\alpha_k}}
}.
\]

“除以”不是人为添加的技巧，而是把单位方差噪声预测转换成动作密度对动作坐标的斜率。实际代码通常不会自动求导 \(\log p\)；它直接预测 \(\epsilon_\theta\)，再代入 DDPM/DDIM 更新系数。

## 14. EBM 对比与控制理论小节

能量模型（EBM）可写成：

\[
p(A\mid O)=\frac{\exp[-E(O,A)]}{Z(O)}.
\]

低能量表示较合理动作，但归一化常数 \(Z(O)\) 涉及所有可能连续动作，训练或采样常依赖负样本/优化。论文用此说明扩散的 MSE 噪声监督为何通常更直接稳定：真实注入噪声已知，不需要显式枚举或归一化所有动作。

论文第 4.5 节用线性控制的玩具推导解释：在简单 LQR 风格情形，动作去噪可对应向反馈控制律靠近。它不是论文实际部署的另一套控制算法，也不改变“条件扩散生成动作计划 + RHC 执行”的主流程。

