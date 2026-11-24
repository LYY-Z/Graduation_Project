# Diffusion Policy 代码学习路线

本文档组面向 Python 和深度学习基础较弱的读者。目标是沿着官方仓库的真实调用路径，读懂训练配置、演示数据、策略模型、训练循环、模拟评估和真实机器人接口。这里讲代码“如何把论文方法实现出来”，理论公式仍以论文学习资料为准。

## 文档结构

本目录按执行顺序组织；所有文件名和目录名使用英文，正文使用中文。

| 顺序 | 文档 | 学习目标 |
|---|---|---|
| 1 | [仓库地图与 Python 基础](01_repository_map_and_python_basics.md) | 认出代码入口、主要目录、函数、类、对象、继承和字典 |
| 2 | [YAML、Hydra 与程序入口](02_yaml_hydra_and_entrypoints.md) | 看懂配置组合、对象创建，以及命令如何走到 Workspace |
| 3 | [Workspace 与训练生命周期](03_workspace_and_training_lifecycle.md) | 理解谁管理模型、数据、训练、评估和保存 |
| 4 | [ReplayBuffer、Dataset 与序列采样](04_replaybuffer_dataset_and_sampling.md) | 理解演示数据如何存储、拆分 episode、抽取时间窗口 |
| 5 | [张量形状、DataLoader 与归一化](05_tensor_shapes_dataloader_and_normalization.md) | 跟踪一个 batch 的字段、时间维、动作维和数值尺度 |
| 6 | [Policy 与视觉编码器](06_policy_and_visual_encoder.md) | 理解图片/状态如何成为条件特征，策略如何定义输入输出 |
| 7 | [扩散 U-Net、Scheduler 与损失](07_diffusion_unet_scheduler_and_loss.md) | 把论文去噪器、噪声日程和 MSE 对应到代码 |
| 8 | [训练循环、优化、EMA 与检查点](08_training_loop_optimization_ema_and_checkpoints.md) | 跟读反向传播、学习率、验证、日志和模型保存 |
| 9 | [模拟评估、EnvRunner 与滚动控制](09_simulation_runner_and_receding_horizon.md) | 理解策略如何在 Push-T 模拟环境里预测、执行、再观察 |
| 10 | [评估入口与配置变体](10_evaluation_entrypoint_and_config_variants.md) | 读懂 eval.py、任务/方法配置族和不同实验命令 |
| 11 | [真实机器人代码路径](11_real_robot_code_path.md) | 了解相机、共享内存、RealEnv、控制器与策略如何衔接 |
| 12 | [其他模块、基线、脚本与测试](12_supporting_modules_baselines_and_tests.md) | 给仓库剩余代码分类，并知道何时需要读它们 |
| 13 | [端到端复习图与自测](13_end_to_end_review_and_self_test.md) | 脱离笔记复述一次训练和一次推理的完整数据流 |

## 建议学习节奏

每次只读一篇。先看“本节要回答的问题”，再跟着图和代码片段读；遇到不认识的 Python 语法时先查第 1 篇，不要一开始逐行背完整文件。每读完一篇，用文末自测确认自己能说明输入、输出和调用者。

推荐主线：

~~~text
train.py 与 Hydra 配置
→ Workspace
→ Dataset / ReplayBuffer / SequenceSampler
→ batch 与归一化
→ Policy / 视觉编码器 / Conditional U-Net
→ compute_loss 与优化器
→ EnvRunner 模拟评估
→ predict_action 与滚动时域控制
→ eval.py / checkpoint
→ 真实机器人和仓库扩展
~~~

## 阅读边界

- 代码以本地仓库当前版本为准；文件名、依赖和命令可能与其他分支或论文伪代码略有不同。
- 先掌握视觉 Diffusion Policy 的主线。Transformer、IBC、BET、Robomimic、数据转换脚本属于扩展内容。
- 本学习路线用于读代码，不表示当前环境已经配置好，也不要求现在运行实验。
- 真实机器人代码涉及实体设备和运动控制；先理解调用路径，不要在没有硬件、限位和安全准备时尝试执行。

## 与学习手册的关系

- 论文到代码的总表：[论文到官方代码](../01_paper_to_official_code.md)
- 复现与故障定位：[最小复现与调试](../02_minimal_reproduction_and_debug.md)
- 论文公式与 DDPM 理论：[学习地图](../../README.md)
