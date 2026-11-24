# 学习与研究导航

当前研究目标和长期要求见[交接说明](00_research_handoff.CN.md)。详细教材与调研资料按用途分开，论文见[原始资料索引](../01_papers/README.md)，源码在 `03_code/`。

| 用途 | 入口 |
|---|---|
| 研究调研与选题 | [research](research/README.md) |
| DDPM、Diffusion Policy、UR7e | [学习路线](diffusion_policy/README.md) |
| LocoFormer、长记忆与 PPO | [学习手册](locoformer/README.md) |
| FLAIR 源码与复现 | [学习入口](flair/README.md) |
| 实验平台 | [Go2-W 硬件、双平台接口与连接](platform/README.md) |
| PPT 与讲稿 | [reports](reports/README.md) |
| 服务器可视化 | [VNC](platform/vnc.md) |

## 基础概念怎么衔接

共同基础是张量、网络、参数、前向、损失、梯度和优化器。Diffusion Policy 从演示学习噪声预测并生成动作块；LocoFormer 从交互回报训练历史条件策略；FLAIR 从实际响应在线更新补偿模型。训练信号和时间组织各不相同。

| 疑问 | 阅读位置 |
|---|---|
| 网络、参数和前向到底是什么？ | [网络基础](locoformer/02_network_and_memory.md#tensors) |
| 加噪、高斯、平方根和反向公式 | [DDPM 推导](diffusion_policy/01_foundations/02_ddpm_from_intuition_to_formula.md) |
| score、动作扩散和 DDIM | [条件动作扩散](diffusion_policy/02_paper_study/02_action_diffusion_and_formulas.md) |
| 视觉、FiLM、EMA 和控制窗口 | [网络与控制](diffusion_policy/02_paper_study/03_control_network_and_design.md) |
| QKV、segment 和缓存 | [网络与记忆](locoformer/02_network_and_memory.md) |
| Trial、Episode 和训练时间链 | [全流程](locoformer/01_paper_and_full_pipeline.md#concepts) |
| 奖励、优势、重新前向和 PPO 更新 | [强化学习与 PPO](locoformer/03_reinforcement_learning_and_ppo.md) |
| 相机、checkpoint、限幅与实体执行 | [重构代码讲解](diffusion_policy/05_code_and_deployment/README.md) |
| 航点怎样到六足结果统计 | [FLAIR 源码](flair/README.md) |

遇到公式或代码，先明确它处于哪个阶段、数据从哪里来、使用哪版参数或缓存、结果交给谁，再用小例子连接。详细疑问索引见各教材，不再维护一份重复的总教材。
