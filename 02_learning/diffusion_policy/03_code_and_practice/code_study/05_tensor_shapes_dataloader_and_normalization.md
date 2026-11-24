# 第 5 节：张量形状、DataLoader 与归一化

## 本节要回答的问题

1. Dataset 的单个样本和 DataLoader 的 batch 有什么区别？
2. B、T、Do、Da 各是哪一维？
3. 归一化为什么要做，怎样保证推理时尺度一致？

## 1. 一维数组、矩阵和张量

Tensor 是多维数字数组。可以把维度想成每层的索引：

- 向量：一个维度，例如机器人位置 [x,y]；
- 矩阵：两个维度，例如一段时间内的动作 [时间, 动作维]；
- 更高维张量：例如一批图片 [批次, 通道, 高度, 宽度]。

读形状时不要只看数字，先给每一维命名。对 Diffusion Policy 来说，B 通常是 batch，T 是时间，Do 是 observation 特征数，Da 是动作特征数。

## 2. Dataset 样本到 batch 的形状

PushTImageDataset 的单个样本通常有：

| 字段 | 单样本形状 | 含义 |
|---|---|---|
| obs.image | [T, 3, 96, 96] | T 帧 RGB 图像 |
| obs.agent_pos | [T, 2] | 每帧二维推杆位置 |
| action | [T, 2] | 对应的二维动作 |

DataLoader 一次取出 B 个样本后，在最前面加 batch 维：

| 字段 | batch 形状 |
|---|---|
| obs.image | [B, T, 3, 96, 96] |
| obs.agent_pos | [B, T, 2] |
| action | [B, T, 2] |

DataLoader 的工作主要是组合样本、按配置打乱训练样本、按 num_workers 并行读取。它不会理解动作含义，也不会执行神经网络。

## 3. RGB 图片布局要一致

图片存储常见格式是 H,W,C，例如 96×96 的 RGB 图片为 [96,96,3]。卷积视觉网络常接收 C,H,W，即 [3,96,96]。PushTImageDataset 使用 moveaxis 把通道维移到前面，再除以 255 转成约 [0,1]。

若把 HWC 当成 CHW，网络会误把高度当通道。图像通道顺序、数值范围和维度顺序是读数据代码时的三个基本检查点。

## 4. 三个时间长度不要混为一谈

配置中常出现：

| 名称 | 代码意义 | 例子 |
|---|---|---|
| horizon / T_p | 一次生成的完整动作计划长度 | 16 |
| n_obs_steps / T_o | 策略使用多少帧历史观察 | 2 |
| n_action_steps / T_a | 每次预测后实际执行多少动作 | 8 |

训练 Dataset 样本的长度通常按 horizon 切出动作序列。推理时策略生成这个计划，但控制器只执行其中一段，执行后会重新观察并规划。训练序列长度、观察帧数和实际执行长度是三个不同参数。

## 5. 归一化在改变单位尺度

位置以米计、角度以弧度计、夹爪可能是 0 到 1；若量级差异很大，数值大的维度可能主导平方误差。LinearNormalizer 根据训练数据计算缩放和偏置，再做线性变换。

PushTImageDataset 的代码中：

- action 和 agent_pos 使用 limits 模式拟合逐维最小值、最大值，通常映射到约 [-1,1]；
- image 使用专门的范围变换，把 [0,1] 映射到 [-1,1]；
- 近似常数的维度不会被极小范围放大到异常大。

归一化公式可先看成：

~~~text
归一化值 = 原始值 × scale + offset
~~~

训练时网络处理归一化数据；推理得到动作后，必须用同一 normalizer.unnormalize() 还原到环境/控制器期望的尺度。检查点保存了 normalizer 参数的一部分，使评估时可复用。重新随意拟合一组尺度会导致模型输出和动作单位不匹配。

## 6. shape_meta：给模型的形状说明书

配置中的 shape_meta 说明动作和每个 observation 键的形状、类型。例如：

~~~yaml
action:
  shape: [2]
obs:
  image:
    shape: [3, 96, 96]
    type: rgb
  agent_pos:
    shape: [2]
    type: low_dim
~~~

Dataset 应输出与这些定义一致的数据。策略构造时据此推断动作维数和视觉编码器输入格式；若 shape_meta 与真实数组不一致，通常会在网络前向时触发形状断言或矩阵维度错误。

## 7. 看见形状变化时怎么追

把张量经过每个步骤时写成：

~~~text
Dataset 单样本: image [T,3,H,W], action [T,Da]
DataLoader batch: image [B,T,3,H,W], action [B,T,Da]
策略取最近观察: image [B,To,3,H,W]
折叠时间供视觉编码: image [B*To,3,H,W]
编码后恢复时间: features [B,To,Df]
拼接观察特征: global_cond [B,To*Df]
动作去噪对象: trajectory [B,Tp,Da]
~~~

读代码时重点问：哪一维是 batch？时间维是否折叠或恢复？最后一维是动作还是特征？任何一步都应能解释形状为什么变化。

## 本节自测

1. DataLoader 为什么会把 [T,Da] 变成 [B,T,Da]？
2. Push-T 图像为什么从 HWC 转成 CHW？
3. horizon 和 n_action_steps 为什么不是一回事？
4. 预测动作为什么必须反归一化？

答案要点：DataLoader 叠样本成 batch；卷积输入约定通道优先；horizon 是计划长度、n_action_steps 是执行长度；控制器需要原始动作尺度。
