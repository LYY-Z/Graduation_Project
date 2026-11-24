# 第 3 节：Workspace 与训练生命周期

## 本节要回答的问题

1. 为什么项目要有 Workspace？
2. 初始化和 run() 有什么区别？
3. Workspace 在训练前、训练中、训练后分别做什么？

## 1. Workspace 是实验流程的总管

在本项目里，策略 Policy 负责“给观察，预测动作”和“计算训练损失”；Workspace 管完整实验的生命周期：建模、读数据、更新参数、验证、模拟评估、写日志、保存检查点。

图像 U-Net 训练使用 diffusion_policy/workspace/train_diffusion_unet_image_workspace.py 中的 TrainDiffusionUnetImageWorkspace。它继承 BaseWorkspace，因而也得到基类提供的 checkpoint 保存/加载和输出目录功能。

## 2. 初始化阶段：创建长期对象

看该 Workspace 的 __init__：

1. super().__init__(cfg, ...) 将配置交给 BaseWorkspace 保存。
2. 根据 seed 设置 PyTorch、NumPy 和 Python random 的随机状态。
3. hydra.utils.instantiate(cfg.policy) 创建策略模型。
4. 如果 use_ema 为真，copy.deepcopy(self.model) 创建 EMA 模型副本。
5. instantiate(cfg.optimizer, params=self.model.parameters()) 创建优化器，并把要更新的模型参数交给它。
6. 初始化 global_step 和 epoch 计数。

此时模型和训练状态已创建，但尚未读取完整训练循环。构造函数的目标是“准备对象”，run() 的目标才是“执行实验”。

## 3. run() 开始：恢复和创建数据组件

run() 首先复制 cfg，之后按配置检查是否从 latest checkpoint 恢复。存在时读取模型状态、优化器状态和训练计数；不存在则从头开始。

接着：

- cfg.task.dataset 创建训练 Dataset；
- DataLoader(dataset, **cfg.dataloader) 负责分批、打乱和并行取样；
- dataset.get_normalizer() 计算观察/动作归一化参数；
- dataset.get_validation_dataset() 构造验证数据；
- normalizer 写入策略与 EMA 策略，使训练和推理使用同一套数值尺度。

第 4、5 节会分别细讲 Dataset 切片和 batch 形状。

## 4. run() 准备优化和评估对象

Workspace 还创建：

- 学习率调度器：按步数调整 optimizer 的学习率；
- EMA 更新器：逐批把在线模型信息平滑到 EMA 模型；
- EnvRunner：定期在模拟环境执行策略；
- W&B 和 JsonLogger：保存训练指标；
- TopKCheckpointManager：按指标保留表现最好的若干模型。

最后将模型和优化器状态移到 cfg.training.device 指定设备，例如 cuda:0 表示第一张 CUDA GPU。

## 5. 训练结束不是唯一评估

训练循环每个 epoch 对训练数据反复处理。配置决定何时：

- rollout_every：在模拟环境中跑策略；
- val_every：计算验证集上的噪声预测损失；
- sample_every：从训练 batch 采样计划作调试比较；
- checkpoint_every：保存 latest 和按指标排名的检查点。

因此一轮训练中包含不同类型的“检查”：

| 检查 | 看什么 | 不能证明什么 |
|---|---|---|
| train_loss | 训练样本上预测噪声的误差 | 不保证闭环任务成功 |
| val_loss | 未用于梯度更新的验证样本误差 | 不等同机器人成功率 |
| rollout score | 策略在环境里完整执行的表现 | 不能单独解释失败原因 |
| 视频 | 观察和动作是否看起来合理 | 需要结合指标和配置判断 |

训练损失和模拟任务成功率都重要，不能互相替代。

## 6. debug 配置的意义

Workspace 中 debug 为真时，会把 epoch、训练 batch、验证 batch 等数量降到很小，并提高评估频率。它的用途是快速检查“程序能否启动、数据和形状是否能走通”。debug 成功不代表模型训得足够好，也不代表论文结果复现完成。

## 7. 用一次调用回顾对象关系

~~~text
Hydra 创建 cfg
→ train.py 根据最外层 _target_ 创建 Workspace
→ Workspace.__init__ 创建 Policy、EMA、Optimizer
→ Workspace.run 创建 Dataset、DataLoader、EnvRunner 和 Logger
→ 训练循环调用 Policy.compute_loss 并更新参数
→ 定期验证、rollout、写日志和 checkpoint
~~~

## 本节自测

1. Workspace 与 Policy 的职责区别是什么？
2. 模型在哪个阶段创建？训练循环在哪个方法？
3. 验证损失和模拟成功率为什么要分开看？
4. debug=true 能证明模型训练效果好吗？

答案要点：Workspace 管实验生命周期，Policy 管预测和损失；构造函数建对象，run 执行实验；离线预测误差不等于闭环成功；debug 只验证小流程可运行。
