# DDPM：从直觉到公式

## 文档用途

这份文档整理本学习过程中关于 DDPM（Denoising Diffusion Probabilistic Model，去噪扩散概率模型）的全部核心问题，目标是从零解释：

- 高斯噪声是什么，以及如何加入图片或动作；
- 为什么公式中出现平方根；
- \(x_0,x_t,\epsilon,\alpha_t,\beta_t,\bar\alpha_t\) 分别是什么；
- 为什么连续加噪后可以直接写出闭式公式；
- 为什么反向过程要使用贝叶斯公式；
- 后验均值 \(\tilde\mu_t\)、后验方差 \(\tilde\beta_t\) 如何得到；
- 反向均值公式为什么是
  \[
  \mu_\theta(x_t,t)
  =
  \frac{1}{\sqrt{\alpha_t}}
  \left(
  x_t-
  \frac{\beta_t}{\sqrt{1-\bar\alpha_t}}
  \epsilon_\theta(x_t,t)
  \right);
  \]
- \(\sigma_t\) 从哪里来，以及为什么出现 \(\sigma_tz\)；
- 训练、生成和 Diffusion Policy 的对应关系。

第一次建议先读数字例子，再回看正式推导。暂时不必背下所有系数，先理解每个量的作用。

---

## 1. DDPM 的两条方向

### 1.1 前向过程：人为加噪

从真实样本 \(x_0\) 开始，逐步加入随机噪声：

\[
x_0\rightarrow x_1\rightarrow x_2\rightarrow\cdots\rightarrow x_T
\]

最后的 \(x_T\) 几乎变成纯高斯噪声。

### 1.2 反向过程：学习去噪

生成时从纯噪声开始，逐步恢复：

\[
x_T\rightarrow x_{T-1}\rightarrow x_{T-2}\rightarrow\cdots\rightarrow x_0
\]

网络每一步都判断当前样本中混入了什么噪声，然后向更干净的方向移动。

可以把它想成“泼墨和清理”：

- \(x_0\)：干净样本；
- 前向过程：逐渐泼入随机墨水；
- \(x_t\)：被泼墨后的样本；
- \(\epsilon_\theta\)：网络猜测墨水的形状；
- 反向过程：根据猜测逐步清理。

---

## 2. 所有变量到底是什么

先只看一个数字。整张图片或一段动作只是把同样的运算同时作用在很多数字上。

| 符号 | 含义 |
|---|---|
| \(x_0\) | 干净样本；图像任务中是原图，动作任务中是干净动作序列 |
| \(x_t\) | 扩散第 \(t\) 步后的带噪样本 |
| \(t\) | 扩散时间步，\(0\) 表示干净，\(T\) 表示几乎纯噪声 |
| \(\epsilon_t\) | 第 \(t\) 步新抽取的噪声 |
| \(\epsilon\) | 多步噪声合并后的等效噪声 |
| \(\epsilon_\theta(x_t,t)\) | 神经网络预测的噪声；\(\theta\) 是网络参数 |
| \(z\) | 反向采样时新抽取的随机噪声 |
| \(\beta_t\) | 第 \(t\) 步加入的噪声方差 |
| \(\alpha_t\) | 第 \(t\) 步保留信号的方差比例，\(\alpha_t=1-\beta_t\) |
| \(\bar\alpha_t\) | 累计保留比例，\(\bar\alpha_t=\alpha_1\alpha_2\cdots\alpha_t\) |
| \(\mu_\theta\) | 反向分布的中心，也就是 \(x_{t-1}\) 最可能的位置 |
| \(\sigma_t\) | 反向分布的标准差，控制随机波动大小 |

图像通常表示成张量：

\[
x_0\in\mathbb R^{C\times H\times W}
\]

批量输入时常见形状是 \([B,C,H,W]\)。Diffusion Policy 中，被扩散的对象是动作序列：

\[
A^0_t\in\mathbb R^{T_p\times D_a}
\]

其中 \(T_p\) 是预测的动作步数，\(D_a\) 是动作维度。

---

## 3. 高斯分布不是一个数字

### 3.1 一维高斯

\[
\epsilon\sim\mathcal N(0,1)
\]

表示反复抽取 \(\epsilon\) 时，数字大多靠近 0，方差为 1。一次实际抽样可能得到：

\[
-0.4,\quad0.2,\quad1.1,\quad-1.7
\]

所以：

- \(\mathcal N(0,1)\) 是抽样规则；
- \(\epsilon=-0.4\) 才是一次具体抽到的数字。

### 3.2 多维高斯

\[
\epsilon\sim\mathcal N(0,I)
\]

表示每个位置独立抽取一个标准高斯数字。\(I\) 是单位矩阵，表示每个位置方差为 1、位置之间协方差为 0。

例如图片噪声可能是：

\[
\epsilon=
\begin{bmatrix}
-0.4&0.2\\
1.1&-1.7
\end{bmatrix}
\]

它与图片具有相同形状。

中间的 \(x_t\) 不一定是一张可以直接显示的正常图片。像素常先归一化到 \([-1,1]\)，加噪后出现超出范围的数是正常的。

---

## 4. 一步前向加噪

DDPM 规定：

\[
\boxed{
x_t=\sqrt{\alpha_t}x_{t-1}
+\sqrt{1-\alpha_t}\epsilon_t
}
\]

令：

\[
\beta_t=1-\alpha_t
\]

也可以写成：

\[
x_t=\sqrt{\alpha_t}x_{t-1}
+\sqrt{\beta_t}\epsilon_t
\]

其中：

- \(\sqrt{\alpha_t}x_{t-1}\)：保留旧样本；
- \(\sqrt{\beta_t}\epsilon_t\)：加入新噪声。

### 4.1 数字例子

设：

\[
x_{t-1}=0.8,\quad\alpha_t=0.8,\quad\epsilon_t=-1
\]

则：

\[
x_t=\sqrt{0.8}\times0.8+\sqrt{0.2}\times(-1)
\approx0.268
\]

旧值 \(0.8\) 被噪声污染成了 \(0.268\)。

### 4.2 为什么是平方根

独立变量满足：

\[
\operatorname{Var}(aX+bY)
=a^2\operatorname{Var}(X)+b^2\operatorname{Var}(Y)
\]

所以：

\[
\operatorname{Var}
\left(
\sqrt{\alpha_t}X+\sqrt{\beta_t}Y
\right)
=\alpha_t+\beta_t=1
\]

平方根的作用是把方差比例转换成振幅系数，使整体尺度稳定。若错误使用 \(\alpha_tX+\beta_tY\)，方差会变成 \(\alpha_t^2+\beta_t^2\)。

---

## 5. 多次加噪为什么仍然容易计算

两步展开：

\[
x_1=\sqrt{\alpha_1}x_0+\sqrt{1-\alpha_1}\epsilon_1
\]

\[
x_2=\sqrt{\alpha_2}x_1+\sqrt{1-\alpha_2}\epsilon_2
\]

代入得到：

\[
x_2
=\sqrt{\alpha_1\alpha_2}x_0
+
\sqrt{\alpha_2(1-\alpha_1)}\epsilon_1
+
\sqrt{1-\alpha_2}\epsilon_2
\]

后两项是独立高斯变量的加权和，仍是高斯变量。它们可以合并为一份新的标准高斯噪声 \(\epsilon\)：

\[
x_2
=\sqrt{\alpha_1\alpha_2}x_0
+
\sqrt{1-\alpha_1\alpha_2}\epsilon
\]

定义：

\[
\boxed{
\bar\alpha_t=\alpha_1\alpha_2\cdots\alpha_t
}
\]

便得到任意时刻的闭式公式：

\[
\boxed{
x_t=\sqrt{\bar\alpha_t}x_0
+
\sqrt{1-\bar\alpha_t}\epsilon
}
\]

训练时不必真的逐步加噪 \(t\) 次；随机抽一个 \(t\) 和一份 \(\epsilon\)，即可直接构造 \(x_t\)。

---

## 6. 为什么最后接近标准高斯噪声

因为每个 \(\alpha_t<1\)，累计乘积会越来越小：

\[
\bar\alpha_t=\prod_{s=1}^t\alpha_s\longrightarrow0
\]

所以：

\[
\sqrt{\bar\alpha_t}x_0\longrightarrow0
\]

\[
\sqrt{1-\bar\alpha_t}\epsilon\longrightarrow\epsilon
\]

最终：

\[
x_T\approx\epsilon,\qquad\epsilon\sim\mathcal N(0,I)
\]

有限 \(T\) 时通常是非常接近而非绝对相等；噪声日程会被设计为让它足够接近。

生成时就可以固定从：

\[
x_T\sim\mathcal N(0,I)
\]

开始。

---

## 7. 反向过程究竟要计算什么

前向过程已知：

\[
x_{t-1}\longrightarrow x_t
\]

反向想要：

\[
x_t\longrightarrow x_{t-1}
\]

但一个 \(x_t\) 可能由很多不同的 \(x_{t-1}\) 产生，所以反向结果不是一个确定数字，而是一个概率分布：

\[
p_\theta(x_{t-1}\mid x_t)
\]

这里：

- \(q\)：人为设计的前向过程；
- \(p_\theta\)：神经网络学习的反向过程；
- \(\theta\)：神经网络参数。

训练时有真实的 \(x_0\)，可以研究精确后验：

\[
\boxed{
q(x_{t-1}\mid x_t,x_0)
}
\]

生成时没有真实 \(x_0\)，所以让网络预测噪声，再估计 \(x_0\)。

---

## 8. 贝叶斯公式如何得到反向后验

令：

\[
y=x_{t-1}
\]

前向一步给出：

\[
q(x_t\mid y)
=
\mathcal N(\sqrt{\alpha_t}y,\beta_t)
\]

从原图到上一步给出：

\[
q(y\mid x_0)
=
\mathcal N\left(
\sqrt{\bar\alpha_{t-1}}x_0,
1-\bar\alpha_{t-1}
\right)
\]

根据贝叶斯公式：

\[
q(y\mid x_t,x_0)
\propto
q(x_t\mid y)q(y\mid x_0)
\]

写成指数形式：

\[
q(y\mid x_t,x_0)
\propto
\exp\left[
-\frac12
\left(
\frac{(x_t-\sqrt{\alpha_t}y)^2}{\beta_t}
+
\frac{(y-\sqrt{\bar\alpha_{t-1}}x_0)^2}
{1-\bar\alpha_{t-1}}
\right)
\right]
\]

展开平方后，所有与 \(y\) 有关的部分都能整理成：

\[
-\frac12(Ay^2-2By)
\]

而：

\[
-\frac12(Ay^2-2By)
=
-\frac A2\left(y-\frac BA\right)^2+\text{常数}
\]

这正是高斯分布的形式，因此后验仍是高斯：

\[
\boxed{
q(x_{t-1}\mid x_t,x_0)
=
\mathcal N(\tilde\mu_t,\tilde\beta_t I)
}
\]

整理得到：

\[
\boxed{
\tilde\beta_t
=
\frac{
(1-\bar\alpha_{t-1})\beta_t
}{
1-\bar\alpha_t
}
}
\]

\[
\boxed{
\tilde\mu_t
=
\frac{
\sqrt{\bar\alpha_{t-1}}\beta_t
}{
1-\bar\alpha_t
}x_0
+
\frac{
\sqrt{\alpha_t}(1-\bar\alpha_{t-1})
}{
1-\bar\alpha_t
}x_t
}
\]

这就是“高斯前向过程使后验可解析”的含义：均值和方差都可以直接算出来。

---

## 9. 网络为什么预测噪声

闭式前向公式是：

\[
x_t=
\sqrt{\bar\alpha_t}x_0+
\sqrt{1-\bar\alpha_t}\epsilon
\]

训练时知道真正抽取的 \(\epsilon\)，所以网络学习：

\[
\boxed{
\epsilon_\theta(x_t,t)\approx\epsilon
}
\]

由上式解出原图：

\[
\sqrt{\bar\alpha_t}x_0
=
x_t-\sqrt{1-\bar\alpha_t}\epsilon
\]

\[
\boxed{
\hat x_0
=
\frac{
x_t-\sqrt{1-\bar\alpha_t}\epsilon_\theta(x_t,t)
}{
\sqrt{\bar\alpha_t}
}
}
\]

所以网络预测噪声后，就能间接估计原图。

---

## 10. 反向均值公式逐步推导

真实后验均值可以记成：

\[
\tilde\mu_t=c_{1,t}x_0+c_{2,t}x_t
\]

其中：

\[
c_{1,t}
=
\frac{\sqrt{\bar\alpha_{t-1}}\beta_t}
{1-\bar\alpha_t}
\]

\[
c_{2,t}
=
\frac{\sqrt{\alpha_t}(1-\bar\alpha_{t-1})}
{1-\bar\alpha_t}
\]

生成时没有真实 \(x_0\)，所以使用 \(\hat x_0\)：

\[
\mu_\theta
=c_{1,t}\hat x_0+c_{2,t}x_t
\]

代入：

\[
\hat x_0
=
\frac{
x_t-\sqrt{1-\bar\alpha_t}\epsilon_\theta
}{
\sqrt{\bar\alpha_t}
}
\]

得到：

\[
\mu_\theta
=
c_{1,t}
\frac{
x_t-\sqrt{1-\bar\alpha_t}\epsilon_\theta
}{
\sqrt{\bar\alpha_t}
}
+
c_{2,t}x_t
\]

接下来只是收集两类项。利用：

\[
\bar\alpha_t=\alpha_t\bar\alpha_{t-1}
\]

可得 \(x_t\) 的总系数为 \(1/\sqrt{\alpha_t}\)，噪声预测项的系数为：

\[
-\frac{\beta_t}
{\sqrt{\alpha_t}\sqrt{1-\bar\alpha_t}}
\]

因此：

\[
\boxed{
\mu_\theta(x_t,t)
=
\frac1{\sqrt{\alpha_t}}
\left(
x_t-
\frac{\beta_t}
{\sqrt{1-\bar\alpha_t}}
\epsilon_\theta(x_t,t)
\right)
}
\]

这条公式的来源是：

\[
\boxed{
\text{贝叶斯后验均值}
\rightarrow
\text{用 }\hat x_0\text{ 替换 }x_0
\rightarrow
\text{代数整理}
}
\]

注意：

\[
x_t-
\frac{\beta_t}{\sqrt{1-\bar\alpha_t}}\epsilon_\theta
\]

只是括号内部，外面还有 \(1/\sqrt{\alpha_t}\)。并且：

\[
\beta_t=1-\alpha_t
\]

---

## 11. \(\sigma_t\) 从哪里来

理论后验为：

\[
q(x_{t-1}\mid x_t,x_0)
=
\mathcal N(\tilde\mu_t,\tilde\beta_t I)
\]

第二个参数 \(\tilde\beta_t\) 是方差，不是标准差。

高斯分布的抽样公式是：

\[
X\sim\mathcal N(\mu,\sigma^2I)
\quad\Longleftrightarrow\quad
X=\mu+\sigma z
\]

其中：

\[
z\sim\mathcal N(0,I)
\]

在使用真实后验方差的基本 DDPM 设定中：

\[
\boxed{
\sigma_t^2=\tilde\beta_t
}
\qquad
\boxed{
\sigma_t=\sqrt{\tilde\beta_t}
}
\]

反向采样为：

\[
\boxed{
x_{t-1}
=
\mu_\theta(x_t,t)+\sigma_tz
}
\]

其中：

- \(\mu_\theta\)：下一步的中心；
- \(\sigma_t\)：允许的随机波动大小；
- \(z\)：这一次新抽取的随机噪声；
- \(\sigma_tz\)：实际加入的随机偏移。

一些实现会将反向方差固定为 \(\tilde\beta_t\)，另一些实现使用 \(\beta_t\) 或学习方差；因此论文算法中的 \(\sigma_t\) 有时只写成一个预先规定的噪声标准差。它不是 \(\epsilon_\theta\)，也通常不是网络直接预测的量。

### 11.1 为什么最后一步常令 \(z=0\)

因为：

\[
\bar\alpha_0=1
\]

所以：

\[
\tilde\beta_1
=
\frac{(1-\bar\alpha_0)\beta_1}
{1-\bar\alpha_1}
=0
\]

因此：

\[
\sigma_1=0
\]

最后一步不再注入随机噪声，直接输出最终结果。

---

## 12. 一个完整的数值反向例子

设：

\[
\alpha_1=\alpha_2=0.8,\qquad
\beta_1=\beta_2=0.2,\qquad
x_0=2
\]

构造第 2 步样本：

\[
\bar\alpha_2=0.8\times0.8=0.64
\]

\[
x_2
=
\sqrt{0.64}\times2+\sqrt{0.36}\times(-2)
=0.8\times2+0.6\times(-2)
=0.4
\]

假设网络准确预测：

\[
\epsilon_\theta(x_2,2)=-2
\]

### 12.1 估计原图

\[
\hat x_0
=
\frac{0.4-\sqrt{0.36}\times(-2)}
{\sqrt{0.64}}
=
\frac{0.4+1.2}{0.8}
=2
\]

### 12.2 计算反向中心

\[
\mu_\theta
=
\frac1{\sqrt{0.8}}
\left(
0.4-
\frac{0.2}{\sqrt{0.36}}(-2)
\right)
\approx1.193
\]

### 12.3 计算反向标准差

\[
\bar\alpha_1=0.8
\]

\[
\tilde\beta_2
=
\frac{(1-0.8)\times0.2}{1-0.64}
=0.111
\]

\[
\sigma_2=\sqrt{0.111}\approx0.333
\]

### 12.4 抽取上一步

若这一次抽到：

\[
z=0.3
\]

则：

\[
x_1
=1.193+0.333\times0.3
\approx1.293
\]

这里：

- \(\hat x_0=2\)：估计的干净值；
- \(\mu_\theta=1.193\)：\(x_1\) 的中心；
- \(\sigma_2=0.333\)：波动大小；
- \(z=0.3\)：这次随机抽到的偏移；
- \(x_1=1.293\)：真正得到的上一步样本。

---

## 13. 训练算法

训练时有干净样本 \(x_0\)，因此可以自己制造带噪样本并保留真实答案。

流程：

1. 从数据集取一个干净样本 \(x_0\)；
2. 随机选扩散步 \(t\)；
3. 抽取标准高斯噪声 \(\epsilon\)；
4. 使用闭式公式构造 \(x_t\)；
5. 网络输入 \(x_t,t\)，输出 \(\epsilon_\theta(x_t,t)\)；
6. 比较预测噪声与真实噪声；
7. 用梯度下降更新 \(\theta\)。

伪代码：

    x0 = 从数据集取干净样本
    t = 在 1 到 T 中随机抽一个时间步
    epsilon = torch.randn_like(x0)
    xt = sqrt(bar_alpha[t]) * x0 + sqrt(1 - bar_alpha[t]) * epsilon
    epsilon_hat = model(xt, t)
    loss = mean((epsilon_hat - epsilon) ** 2)
    更新模型参数

训练目标：

\[
\boxed{
\mathcal L(\theta)
=
\mathbb E
\left[
\left\|
\epsilon-\epsilon_\theta(x_t,t)
\right\|^2
\right]
}
\]

网络输出与 \(\epsilon\) 形状相同。

---

## 14. 生成算法

生成时没有 \(x_0\)，所以先抽取纯噪声：

\[
x_T\sim\mathcal N(0,I)
\]

然后从 \(T\) 反向循环到 1：

    x = 标准高斯噪声
    for t = T, T-1, ..., 1:
        epsilon_hat = model(x, t)
        mu = 1 / sqrt(alpha[t]) * (
             x - beta[t] / sqrt(1 - bar_alpha[t]) * epsilon_hat
        )
        if t > 1:
            z = 标准高斯噪声
        else:
            z = 0
        x = mu + sigma[t] * z
    返回 x

每一次循环都只去掉一部分噪声：

\[
x_t\rightarrow x_{t-1}
\]

重复很多次后才得到最终 \(x_0\)。

---

## 15. 最容易混淆的几个量

### 15.1 \(\epsilon\) 和 \(z\) 不是同一个角色

它们都可以从 \(\mathcal N(0,I)\) 抽取，但用途不同：

- \(\epsilon\)：训练时加入前向过程的噪声；
- \(\epsilon_\theta\)：网络对 \(\epsilon\) 的预测；
- \(z\)：反向采样时新抽取的随机噪声。

### 15.2 \(\beta_t\)、\(\tilde\beta_t\)、\(\sigma_t\) 不一样

- \(\beta_t\)：前向第 \(t\) 步的噪声方差；
- \(\tilde\beta_t\)：理论反向后验的方差；
- \(\sigma_t=\sqrt{\tilde\beta_t}\)：反向抽样使用的标准差。

### 15.3 \(\mu_\theta\) 不是 \(x_{t-1}\)

\[
\mu_\theta
\]

是中心，而：

\[
x_{t-1}=\mu_\theta+\sigma_tz
\]

是从中心附近真正抽取的样本。

### 15.4 后验为什么带 \(x_0\)

\[
q(x_{t-1}\mid x_t,x_0)
\]

是理论推导中的精确后验。训练时知道 \(x_0\)，生成时不知道，所以用网络预测噪声间接估计 \(\hat x_0\)。

### 15.5 反向公式不是简单的 \(x_t-\epsilon_\theta\)

因为 \(x_t\) 和噪声的尺度受 \(\alpha_t,\bar\alpha_t\) 控制，必须经过：

\[
\frac1{\sqrt{\alpha_t}}
\quad\text{和}\quad
\frac{\beta_t}{\sqrt{1-\bar\alpha_t}}
\]

的校正。

---

## 16. 与 Diffusion Policy 的对应关系

Diffusion Policy 使用同样的数学结构，只是被扩散的对象不是图片，而是动作序列。

| DDPM 图像生成 | Diffusion Policy |
|---|---|
| 干净图片 \(x_0\) | 干净动作序列 \(A^0_t\) |
| 带噪图片 \(x_t\) | 带噪动作序列 \(A^k_t\) |
| 图片噪声 \(\epsilon\) | 动作张量噪声 \(\epsilon\) |
| 条件可能是文本或类别 | 条件是视觉和本体观测 \(O_t\) |
| 网络预测图像噪声 | 网络预测动作噪声 |
| 生成图片 | 生成未来动作序列 |

为避免两个时间概念混淆：

- \(t\)：机器人控制时刻；
- \(k\)：扩散去噪步（有些材料仍用 \(t\) 表示扩散步）。

动作条件扩散可写成：

\[
\epsilon_\theta(A^k_t,k,O_t)
\]

含义是：

> 在观测 \(O_t\) 的条件下，网络预测动作序列 \(A^k_t\) 中的噪声。

生成时从随机动作序列开始，逐步去噪得到一段未来动作，只执行前面几步，然后获得新观测并重新规划。这叫滚动时域控制（receding horizon control）。

---

## 17. 一页式总流程

### 前向训练题目

\[
x_0
\xrightarrow[\text{随机 }t,\epsilon]{\text{闭式加噪}}
x_t
\xrightarrow{\text{网络}}
\epsilon_\theta
\]

训练网络使：

\[
\epsilon_\theta\approx\epsilon
\]

### 反向生成

\[
x_T
\xrightarrow{\epsilon_\theta}
\hat x_0
\xrightarrow{\text{后验均值公式}}
\mu_\theta
\xrightarrow{+\sigma_tz}
x_{t-1}
\]

循环执行：

\[
x_T\rightarrow x_{T-1}\rightarrow\cdots\rightarrow x_0
\]

最核心的四条公式是：

\[
\boxed{
x_t=
\sqrt{\bar\alpha_t}x_0+
\sqrt{1-\bar\alpha_t}\epsilon
}
\]

\[
\boxed{
\epsilon_\theta(x_t,t)\approx\epsilon
}
\]

\[
\boxed{
\hat x_0=
\frac{x_t-\sqrt{1-\bar\alpha_t}\epsilon_\theta}
{\sqrt{\bar\alpha_t}}
}
\]

\[
\boxed{
x_{t-1}=\mu_\theta(x_t,t)+\sigma_tz
}
\]

其中：

\[
\boxed{
\mu_\theta
=
\frac1{\sqrt{\alpha_t}}
\left(
x_t-
\frac{\beta_t}{\sqrt{1-\bar\alpha_t}}
\epsilon_\theta
\right)
}
\]

以及：

\[
\boxed{
\sigma_t^2=\tilde\beta_t
=
\frac{(1-\bar\alpha_{t-1})\beta_t}
{1-\bar\alpha_t}
}
\]

---

## 18. 自测题

1. \(\mathcal N(0,I)\) 是一个具体的数字，还是抽数字的规则？
2. 为什么前向公式中使用 \(\sqrt{\alpha_t}\) 而不是 \(\alpha_t\)？
3. \(\bar\alpha_t\) 和 \(\alpha_t\) 的区别是什么？
4. 为什么 \(x_T\) 可以接近标准高斯噪声？
5. \(\epsilon\)、\(\epsilon_\theta\)、\(z\) 分别在什么时候出现？
6. 为什么生成时没有 \(x_0\) 仍然可以使用后验公式？
7. \(\mu_\theta\) 是最终的 \(x_{t-1}\) 吗？
8. \(\sigma_t\) 是方差还是标准差？
9. 反向后验为什么可以通过贝叶斯公式得到？
10. Diffusion Policy 中被逐步去噪的是图片，还是动作序列？

参考答案应能说出：

- \(\mathcal N(0,I)\) 是分布规则，一次抽样才得到具体噪声张量；
- 平方根用于把方差比例转换成振幅系数；
- \(\bar\alpha_t\) 是多个 \(\alpha\) 的乘积；
- \(\epsilon_\theta\) 是网络预测的前向噪声，\(z\) 是反向新抽的噪声；
- \(\mu_\theta\) 是反向分布的中心，不等于最终样本；
- \(\sigma_t\) 是标准差，\(\sigma_t^2\) 是方差；
- 后验由贝叶斯公式和高斯乘积得到；
- Diffusion Policy 去噪的是动作序列。

---

## 19. DDPM 为什么能够生成新样本

DDPM 不是把一份随机噪声凭空“画成”图片。它在训练数据上学习的是：从不同噪声等级的样本回到高概率数据区域的反向规则。

训练数据有一个未知分布：

\[
x_0\sim p_{\mathrm{data}}(x)
\]

前向过程把这个复杂分布逐步变成一个已知的简单分布：

\[
x_0\rightarrow x_1\rightarrow\cdots\rightarrow x_T,\qquad
x_T\approx\mathcal N(0,I)
\]

如果每一步真实反向条件分布都已知：

\[
q(x_{t-1}\mid x_t)
\]

那么从 \(q(x_T)\) 抽样后，按反向条件分布逐步抽样：

\[
x_T\rightarrow x_{T-1}\rightarrow\cdots\rightarrow x_0
\]

最终得到的 \(x_0\) 就会重新服从数据分布 \(p_{\mathrm{data}}\)。

实际中 \(q(x_{t-1}\mid x_t)\) 不知道，因此网络用：

\[
p_\theta(x_{t-1}\mid x_t)
\]

近似它。预测噪声的网络 \(\epsilon_\theta\) 正是在学习这个反向转移需要的方向与均值。

因此 DDPM 能生成，是因为它学会了：

\[
\boxed{
\text{已知高斯噪声分布}
\rightarrow
\text{逐步回到训练数据分布}
}
\]

而不是因为“加噪声”本身具有生成能力。

---

## 20. 学习 Diffusion Policy 前，DDPM 学到什么程度就够

如果目标是读懂并复现 Diffusion Policy，不必先学完所有扩散模型高级理论。

已经必须掌握的内容是：

- 前向加噪、闭式公式和 \(\mathcal N(0,I)\)；
- 噪声预测 MSE 训练目标；
- 条件输入如何进入 \(\epsilon_\theta\)；
- 从 \(x_T\) 反向采样到 \(x_0\)；
- \(\mu_\theta,\sigma_t,z\) 的角色；
- 噪声调度和 DDIM 的“少步采样更快”直觉。

可以暂时延后的内容包括：

- ELBO 与 KL 散度的完整严格证明；
- score matching 的一般理论；
- 连续时间 SDE/ODE；
- classifier-free guidance；
- DPM-Solver 的详细推导；
- 研究型的不同参数化与学习方差方法。

进入 Diffusion Policy 后，只需做变量替换：

\[
x_0\longrightarrow A_t^0,\qquad
x_k\longrightarrow A_t^k
\]

\[
\epsilon_\theta(x_k,k)
\longrightarrow
\epsilon_\theta(O_t,A_t^k,k)
\]

也就是：普通 DDPM 生成样本，Diffusion Policy 在观测条件下生成未来动作序列。

## 21. 噪声日程与 iDDPM 的 square cosine schedule

噪声日程不是一张随机噪声图，也不是网络输出。它是训练前预先写好的数表：

\[
\beta_1,\ldots,\beta_K
\quad\Rightarrow\quad
\alpha_k=1-\beta_k,\qquad
\bar\alpha_k=\prod_{i=1}^k\alpha_i.
\]

\(\beta_k\) 表示第 \(k\) 个扩散等级增加的**方差比例**，\(\alpha_k\) 表示这一步保留的方差比例，\(\bar\alpha_k\) 表示从干净样本累计保留到第 \(k\) 级的比例。真正抽取的噪声是 \(\epsilon\)，网络预测的是 \(\epsilon_\theta\)，二者都不是日程。

论文采用 iDDPM 的 square cosine schedule。令 \(u\in[0,1]\)，先定义：

\[
\bar\alpha(u)=
\frac{\cos^2\left(\frac{u+s}{1+s}\frac{\pi}{2}\right)}
{\cos^2\left(\frac{s}{1+s}\frac{\pi}{2}\right)},
\qquad s=0.008.
\]

离散化后：

\[
\beta_k=
\min\left(
1-\frac{\bar\alpha(k/K)}{\bar\alpha((k-1)/K)},0.999
\right).
\]

平方出现在这里，是因为 \(\bar\alpha\) 表示方差/能量比例；真正混合样本的振幅仍然是 \(\sqrt{\bar\alpha}\) 和 \(\sqrt{1-\bar\alpha}\)。余弦形状的作用是让“由清晰到纯噪声”的难度平滑变化；它是一项经验设计，不是模型在运行时重新学习的东西。

## 22. DDPM 与 DDIM：同一训练目标，不同采样路径

DDPM 的相邻采样遵循本章前面的贝叶斯反向高斯分布，通常含 \(\sigma_k z\) 的随机抽样。DDIM 保留同一个已训练噪声预测器，却用下面两步把当前等级 \(k\) 直接跳到较干净的等级 \(j<k\)：

\[
\hat x_0=
\frac{x_k-\sqrt{1-\bar\alpha_k}\epsilon_\theta(x_k,k)}
{\sqrt{\bar\alpha_k}},
\]

\[
x_j=
\sqrt{\bar\alpha_j}\hat x_0+
\sqrt{1-\bar\alpha_j}\epsilon_\theta(x_k,k)
\quad\text{（确定性 DDIM 形式）}.
\]

跳步并不是凭空减少噪声。闭式前向公式说明：若知道同一个干净样本和同一份标准噪声，任何等级都是按该等级系数重新混合的结果。DDIM 先估计 \(\hat x_0\) 和当前噪声，再按 \(j\) 的系数重新组合。

因此：

- DDPM 与 DDIM 通常训练同一个 \(\epsilon_\theta\)；
- 差异主要发生在**推理/采样阶段**；
- DDIM 的确定性形式可少用很多去噪步，适合需要实时控制的 Diffusion Policy；
- 它不等于相邻 DDPM 后验的随机采样，二者是不同但都可使用的生成轨迹。
