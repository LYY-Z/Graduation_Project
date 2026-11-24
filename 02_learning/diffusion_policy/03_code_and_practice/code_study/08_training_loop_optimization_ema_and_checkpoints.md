# 第 8 节：训练循环、优化、EMA 与检查点

## 本节要回答的问题

前面已经追踪到一个 batch 怎样进入策略、扩散模型怎样计算噪声预测损失。本节继续回答：损失算出来以后，程序怎样让模型变好？训练何时验证、何时保存？EMA 又是什么？

主要入口是 TrainDiffusionUnetImageWorkspace.run()，模型损失在 DiffusionUnetImagePolicy.compute_loss() 中，配置由训练 YAML 提供。可对照仓库中的 diffusion_policy/workspace/train_diffusion_unet_image_workspace.py 和 diffusion_policy/policy/diffusion_unet_image_policy.py。

## 1. 先区分三个“模型状态”

训练时容易把下面三个概念混为一谈：

| 名称 | 是什么 | 作用 |
|---|---|---|
| 在线模型（online model） | 当前正在被梯度更新的策略参数 | 继续学习下一个 batch |
| EMA 模型 | 对在线模型参数的历史平滑平均 | 通常用于更稳定的验证、保存或推理 |
| 检查点（checkpoint） | 磁盘上保存的一份训练状态快照 | 中断后恢复，或交给评估程序使用 |

EMA 不是第二种训练算法，也不是把 loss 再平均一次。它是给模型参数做平滑：

$$
\theta_{\mathrm{EMA}}\leftarrow
\rho\theta_{\mathrm{EMA}}+(1-\rho)\theta_{\mathrm{online}}
$$

例如 $\rho=0.99$ 时，新在线参数只占很小比例，EMA 因而不会被某一次较大的参数抖动立刻带偏。它仍然是一套网络参数，可以像普通模型一样做推理。

## 2. 一个 batch 的更新顺序

对一个 batch，主训练步骤可以读成下面这条链：

~~~text
batch → policy.compute_loss(batch) → loss.backward()
      → optimizer.step() → optimizer.zero_grad()
      → 学习率调度器更新 → EMA 更新
~~~

逐项看：

1. compute_loss(batch)：策略对 batch 中的动作计划加噪，网络预测噪声，返回一个标量损失。细节见第 7 节。
2. loss.backward()：PyTorch 根据计算过程中的链式法则，计算每个可训练参数对 loss 的影响，即梯度。它只计算“该往哪个方向调整”，此时参数还没有被优化器改动。
3. optimizer.step()：优化器使用梯度和学习率更新参数。AdamW 还会根据梯度历史自适应调整每个参数的步长，并带有权重衰减设置。
4. optimizer.zero_grad()：清除刚才累积在参数上的梯度，为下一批数据做准备。PyTorch 默认会累加梯度；不清零会把多个 batch 的梯度意外叠加。
5. 学习率调度器：按预定计划调整学习率。学习率就是每次参数更新的尺度；过大可能越过较好的参数区域，过小则学习很慢。仓库配置可能使用预热加余弦衰减，具体以所选 YAML 为准。
6. EMA 更新：用刚刚更新过的在线参数，缓慢更新 EMA 参数。

这里的 backward() 不是“模型自己记住了答案”，而是把这一批训练样本提供的误差信号转换成参数更新方向。

## 3. epoch、step、global_step

- batch：DataLoader 一次交给训练循环的一组样本。
- step / global_step：处理一个 batch 并进行一次优化更新。global_step 通常跨 epoch 连续递增。
- epoch：训练数据集大致完整遍历一遍。每个 epoch 中有很多 batch/step。

因此，“训练 100 个 epoch”不是只更新 100 次参数；若每个 epoch 有 200 个 batch，大约会有 20,000 次更新（忽略最后不完整 batch 等细节）。

## 4. 训练循环不只有更新

Workspace 的 run() 通常还负责这些外围工作：

- 恢复训练：若指定 resume，从检查点恢复 Workspace、策略和优化器等状态。
- 准备数据：创建训练 Dataset、DataLoader，以及可能的验证 DataLoader。
- 准备环境评估器：构造 EnvRunner，定期用策略实际跑任务。
- 记录指标：记录训练 loss、验证 loss、环境分数、时间、epoch 和 step 等。
- 周期性评估：训练 loss 看起来变小，不代表闭环行为一定成功，因此还要在模拟环境 rollout。
- 保存检查点：按配置保存最近版本，以及按验证表现保留较好的版本。

这里有两种“验证”，不要混淆：

1. 验证集 loss：不反向传播，只测策略在保留演示片段上的噪声预测误差。
2. 环境 rollout：把策略放进模拟环境，让它真正连续执行动作，统计任务表现。

验证集 loss 是训练目标的检查；环境 rollout 更接近“能不能完成任务”。两者有关联，但不是同一个指标。

## 5. no_grad 与评估

评估时通常不需要求参数梯度。torch.no_grad() 告诉 PyTorch 暂时不保存反向传播所需的中间信息，可以减少内存和计算开销。

它不会冻结或删除模型参数，也不等于切换到 EMA。是否调用 EMA、用哪个模型，是 Workspace 的显式逻辑。

## 6. 检查点通常保存什么

训练检查点可能包含：

- Workspace/策略配置；
- 当前在线模型参数；
- EMA 模型参数（若启用）；
- 优化器、学习率调度器状态；
- 当前 epoch、global step；
- 归一化器参数以及恢复训练所需的其他状态。

为什么保存优化器和 step？只存网络权重可以做推理，但无法完整续上原训练过程：优化器的历史动量、学习率进度和训练计数也会影响后续学习。

仓库还可根据配置维护 latest、best 或 top-k 检查点。具体命名和筛选指标看实际配置；不要仅凭文件名假定哪个是最佳策略。

## 7. 训练如何落到代码

可以按调用关系搜索：

~~~text
train.py
  └─ 创建 Workspace
      └─ Workspace.run()
          ├─ DataLoader 取 batch
          ├─ policy.compute_loss(batch)
          ├─ loss.backward()
          ├─ optimizer.step()
          ├─ EMA 更新
          ├─ validation / EnvRunner
          └─ checkpoint 与日志
~~~

建议阅读时分别找：compute_loss、backward、optimizer.step、EMA updater、验证区块和 save_checkpoint。不要把全部几百行都当成一个“模型公式”。

## 本节自测

1. backward() 和 optimizer.step() 分别做什么？
2. 为什么每轮更新后要清空梯度？
3. EMA 平滑的是 loss 还是参数？通常为什么保留它？
4. 验证集 loss 与模拟环境 rollout 有什么区别？
5. 只保存策略权重，为什么不足以完整恢复训练？

参考答案：计算梯度；使用梯度更新参数；清除会跨 batch 累加的梯度；EMA 平滑模型参数；验证 loss 测预测误差，rollout 测闭环任务表现；恢复训练还需要优化器、学习率进度和训练计数等状态。

下一节：[模拟评估、EnvRunner 与滚动控制](09_simulation_runner_and_receding_horizon.md)。
