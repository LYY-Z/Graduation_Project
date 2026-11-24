# 第 4 节：ReplayBuffer、Dataset 与序列采样

## 本节要回答的问题

1. 专家演示数据在仓库中是什么结构？
2. ReplayBuffer 与 Dataset 有什么区别？
3. SequenceSampler 如何避免跨 episode 取错数据？
4. padding 为什么存在？

## 1. 一份演示不只是单张图

一次机器人演示是按时间记录的序列：

~~~text
时刻 0: 图像/状态 o0，专家动作 a0
时刻 1: 图像/状态 o1，专家动作 a1
...
时刻 n: 图像/状态 on，专家动作 an
~~~

通常很多 episode 被串在一起存储。仓库的 ReplayBuffer 保存各字段的时间序列数组，并在 meta 中存每条 episode 的结束位置。Push-T 示例数据含 img、state、action 和 episode_ends。

ReplayBuffer 是数据存储和切取工具；Dataset 是给 PyTorch 训练过程提供样本的适配层。前者管理底层连续数组及 episode 边界，后者决定一个索引对应什么训练窗口、怎样变成 Tensor。

## 2. PushTImageDataset 的构造流程

见 diffusion_policy/dataset/pusht_image_dataset.py：

1. ReplayBuffer.copy_from_path(...) 从 zarr_path 加载 img、state、action。
2. get_val_mask(...) 按 episode 随机选出验证 episode。
3. downsample_mask(...) 可限制用于训练的 episode 数。
4. SequenceSampler(...) 为训练 episode 预先建立合法切片索引。
5. __getitem__(idx) 按索引从 sampler 取一段，再转换为训练字典。

这意味着训练/验证切分以 episode 为单位，而不是把同一条轨迹的临近帧随机拆进训练和验证，降低时间相邻数据泄漏。

## 3. SequenceSampler 的工作

设 horizon=16，Dataset 的一个样本就是时间长度 16 的片段。SequenceSampler 根据 episode_ends 生成每个窗口的起点和终点。

关键原则：一个窗口只能来自一个 episode。若当前 episode 结束了，采样器不会接着把下一个 episode 的开头拼过来，因为那会制造现实中不存在的连续轨迹。

索引内部包含：

- 在 ReplayBuffer 中实际读取的起止位置；
- 这些有效帧应放进输出窗口的哪一段。

## 4. episode 两端为什么需要 padding

episode 开头之前没有足够历史帧，episode 结尾之后没有足够未来动作。如果不补齐，边界附近的窗口会被丢弃，样本数量变少。SequenceSampler 可以将第一个有效值向前复制，将最后一个有效值向后复制，使窗口长度一致。

padding 不是新采集的机器人动作，而是让固定长度网络输入可用的边界处理。配置里的 pad_before、pad_after 控制补齐范围；具体含义应结合使用的 horizon、观测长度和动作长度查看。

## 5. 一个 Push-T 图像样本怎样变成字典

PushTImageDataset._sample_to_data 做的工作包括：

- state 的前两个维度作为 agent_pos；
- 图片由存储时的 H,W,C 排列改成 C,H,W，并除以 255 转到约 [0,1]；
- action 转成 float32。

得到的形式为：

~~~python
{
    "obs": {
        "image": image,        # [T, 3, 96, 96]
        "agent_pos": agent_pos # [T, 2]
    },
    "action": action           # [T, 2]
}
~~~

__getitem__ 最后通过 torch.from_numpy 把 NumPy 数组转成 PyTorch Tensor。DataLoader 之后会把多个样本叠成 batch。

## 6. 不同字段如何保持时间对齐

同一个样本中的 image、agent_pos、action 都必须对应同一段时间范围。若图片窗口和动作窗口错开，模型会被教成“某个画面对应另一时刻的动作”，训练损失仍可能计算出来，却学到错误映射。

读 Dataset 时应逐项检查：

1. 索引取自哪个 episode？
2. 每个字段切了哪个时间区间？
3. 图像和状态在时间上是否对齐？
4. 输出长度是否是 horizon？
5. 边界 padding 的行为是否符合预期？

## 7. Dataset 的几个 PyTorch 接口

- __len__() 返回可采样窗口的数量。
- __getitem__(idx) 返回某个窗口的 obs 和 action。
- get_validation_dataset() 返回使用验证 episode 的版本。
- get_normalizer() 给训练数据计算尺度参数；下一节详解。

DataLoader 根据 __len__ 和 __getitem__ 反复取样，帮训练循环组成 batch。Dataset 不负责训练模型，也不直接执行机器人。

## 本节自测

1. ReplayBuffer 与 Dataset 的区别是什么？
2. 为什么训练/验证应按 episode 分，而不是随便按帧分？
3. 为什么 SequenceSampler 不能跨 episode 拼接窗口？
4. episode 边缘的复制 padding 代表真实采集数据吗？

答案要点：ReplayBuffer 管底层存储；Dataset 定义训练样本；按 episode 切分减少同轨迹泄漏；跨 episode 不是真实连续过程；padding 是固定长度输入的边界处理。
