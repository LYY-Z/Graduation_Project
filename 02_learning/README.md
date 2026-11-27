# 02 学习资料

**放什么**：论文精读、代码逐行讲解、基础概念、平台与服务器使用说明。
**不放什么**：论文原文（[01_papers](../01_papers/README.md)）、调研比较（[04_research](../04_research/README.md)）、实验记录（[05_experiments](../05_experiments/README.md)）。

当前研究状态见 [STATUS](../STATUS.CN.md)。

## 目录清单

| 目录 | 内容 | 状态 |
|---|---|---|
| [gram/](gram/README.md) | **GRAM 学习手册**：前置知识、论文逐节、实验、代码逐行（`code/` 7 篇）、批判性阅读、老师问答、服务器与复现 | ★ 当前主线 |
| [platform/](platform/README.md) | Go2-W 硬件手册、输入输出接口、**服务器操作入门**、VNC | 常用参考 |
| [locoformer/](locoformer/README.md) | LocoFormer 论文、网络与记忆、PPO 讲解 | 历史调研，已不在主线（PPO 部分仍可参考） |
| [diffusion_policy/](diffusion_policy/README.md) | DDPM、Diffusion Policy、UR7e 部署 | 历史调研，已不在主线 |
| [flair/](flair/README.md) | FLAIR 源码与指标 | 历史调研，已不在主线 |

## 推荐阅读顺序

| 顺序 | 内容 |
|---|---|
| 1 | [GRAM 学习手册](gram/README.md)：按手册里的顺序读 |
| 2 | [服务器操作入门](platform/server_guide.CN.md)：学会登录服务器、看训练进度 |
| 3 | [Go2-W 硬件手册](platform/go2w.CN.md)：了解实机平台 |
| 需要时 | [PPO 讲解](locoformer/03_reinforcement_learning_and_ppo.md)：另一种角度讲强化学习 |

## 基础概念速查

| 疑问 | 阅读位置 |
|---|---|
| MDP、PPO、教师—学生、认知不确定性 | [GRAM 01 前置知识](gram/01_background.CN.md) |
| 张量、shape、网络、梯度、PyTorch 写法 | [GRAM code/00 Python 与 PyTorch 基础](gram/code/00_python_pytorch_basics.CN.md) |
| PPO、GAE 手算 | [GRAM code/05 PPO 与数据存储](gram/code/05_ppo_and_storage.CN.md) |
| 网络、参数和前向 | [网络基础](locoformer/02_network_and_memory.md#tensors) |
| 奖励、优势、PPO 更新 | [强化学习与 PPO](locoformer/03_reinforcement_learning_and_ppo.md) |
| 加噪、扩散模型公式 | [DDPM 推导](diffusion_policy/01_foundations/02_ddpm_from_intuition_to_formula.md) |
