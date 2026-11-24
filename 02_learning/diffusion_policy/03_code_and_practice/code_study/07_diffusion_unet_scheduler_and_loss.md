# 第 7 节：扩散 U-Net、Scheduler 与损失

## 本节要回答的问题

1. 代码里的网络对应论文哪一部分？
2. Scheduler 负责什么，代码在哪里使用它？
3. compute_loss 如何对应“预测添加噪声”的训练目标？
4. 推理时怎么反复从噪声动作计划得到动作？

## 1. 两种职责：网络预测，Scheduler 管噪声过程

DiffusionUnetImagePolicy 中组合了两个核心对象：

- self.model：ConditionalUnet1D，接收当前带噪计划、扩散时间步和观察条件，预测噪声或配置指定的目标；
- self.noise_scheduler：diffusers 的 DDPMScheduler，提供 add_noise 和 step 等扩散过程操作。

Scheduler 按 beta schedule 管理每步噪声量以及反向更新系数。仓库配置通过 _target_ 创建官方 diffusers scheduler，因此不要在策略文件里寻找所有 DDPM 系数的手写实现。

## 2. ConditionalUnet1D 怎样看一段动作

输入动作计划形状约为 [B,Tp,Da]：批次、时间、动作维。网络内部为了 Conv1d 会将时间轴与通道轴换位；最终输出再恢复为同一外部形状。

U-Net 的直觉结构：

~~~text
动作序列特征
→ 下采样：扩大感受范围，捕捉更长时间关系
→ 中间残差块
→ 上采样：恢复时间分辨率
→ 跳跃连接：把早期细节传给后续层
→ 输出每个时间点、每个动作维的预测
~~~

它不是图像 U-Net；这里处理的是一维时间序列，所以名称是 ConditionalUnet1D。

## 3. 扩散步也要告诉网络

同一条动作计划在扩散早期和晚期的噪声程度不同。ConditionalUnet1D 将当前 timestep 编码成向量，和观察条件一起送进残差块。否则仅看一张带噪计划，网络不知道应该执行强去噪还是轻微修正。

残差块通过 FiLM 等条件调制，让观察特征与扩散步影响中间特征。配置中的 cond_predict_scale 控制是否预测缩放项和偏置项。

## 4. compute_loss 对应训练阶段

DiffusionUnetImagePolicy.compute_loss 的大致顺序：

1. 归一化 batch['obs'] 和 batch['action']。
2. 把观察编码成条件特征。
3. 从标准高斯分布抽一份与动作计划同形状的 noise。
4. 为 batch 中每个样本随机抽扩散步 timesteps。
5. 调用 scheduler.add_noise(clean_action, noise, timesteps)，得到 noisy_action。
6. 网络输入带噪计划、扩散步和观察条件，输出 pred。
7. 若 prediction_type 是 epsilon，则 target 就是刚才抽出的 noise。
8. 对 pred 与 target 计算逐元素 MSE，再对有效元素和 batch 求平均。

可简化成：

~~~text
干净专家动作 + 已知随机噪声 + 随机扩散步
→ Scheduler 造训练输入
→ 网络估计噪声
→ MSE(predicted_noise, actual_noise)
~~~

若使用 observation inpainting，mask 规定哪些位置是已知条件；这些位置不参与损失，或在加噪后被覆盖回条件真值。Global condition 配置则把观察特征交给 U-Net，不必把观察也做成需要去噪的序列。

## 5. 反向采样对应推理阶段

predict_action 调用 conditional_sample：

1. torch.randn 创建动作计划形状的纯噪声。
2. scheduler.set_timesteps(num_inference_steps) 设置推理用的反向时间步。
3. 对每个扩散时刻 t，网络预测当前噪声。
4. scheduler.step(model_output, t, trajectory) 计算更干净的前一时刻样本。
5. 循环结束后，得到干净动作计划。

网络只告诉 scheduler 当前噪声估计；每步更新公式由 scheduler 完成。因而 DDPM/DDIM 推理策略通常体现在 scheduler 种类、推理步数和设置上。

## 6. 论文公式与代码的对应

| 论文概念 | 代码对象/变量 | 发生阶段 |
|---|---|---|
| 干净动作 A^0 | batch['action'] 归一化后 | 训练目标 |
| 观察 O | batch['obs'] / obs_dict | 训练与推理条件 |
| 扩散步 k | timesteps / scheduler.timesteps | 每个去噪级别 |
| 加入的高斯噪声 epsilon | noise | 训练时真实答案 |
| 带噪动作 A^k | noisy_trajectory / trajectory | 网络输入 |
| 噪声预测器 epsilon_theta | ConditionalUnet1D | 网络输出 |
| 预测误差 | F.mse_loss | 训练损失 |
| 反向一步 | scheduler.step | 推理采样 |

## 本节自测

1. 网络和 Scheduler 的职责为何不同？
2. 训练代码怎样知道真实噪声答案？
3. prediction_type=epsilon 时，MSE 的 target 是什么？
4. 推理时 Scheduler 对什么张量反复执行 step？

答案要点：网络估计目标，Scheduler 管前向/反向扩散；训练噪声由代码自己采样并保留；target 是同一次采样的 noise；step 更新动作计划。
