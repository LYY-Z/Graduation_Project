# 05 实验记录

**放什么**：服务器盘点、复现与训练记录、可行性核查、实机实验条件，以及对应的数据和结果文件。
**不放什么**：讲解性内容（[02_learning](../02_learning/README.md)）、汇报材料（[06_reports](../06_reports/README.md)）。训练产生的模型和日志留在服务器上，不提交到仓库。

## 文件清单

| 文件 | 内容 | 状态 |
|---|---|---|
| [gram_reproduction.CN.md](gram_reproduction.CN.md) | **GRAM 复现记录**：服务器工作区、代码版本、论文版本参数核对、速度测试、训练任务与进度、后续计划 | ★ 当前主文档，随训练更新 |
| [server/inventory.CN.md](server/inventory.CN.md) | 服务器盘点：GPU、CPU、内存、磁盘、驱动、已有环境（不含密码） | 常用参考 |
| [go2w_feasibility.CN.md](go2w_feasibility.CN.md) | Go2-W 底层接口、状态字段、robot_lab / rl_sar 支持与风险 | 实机前参考 |
| [go2w_onboard_compute.CN.md](go2w_onboard_compute.CN.md) | Go2-W 机载算力能否跑 MPC 与 RL 推理 | 实机前参考 |
| [go2w_mpc_opensource.CN.md](go2w_mpc_opensource.CN.md) | Go2-W MPC 开源实现调研 | 历史参考（AugMPC 备选） |
| [lab_requirements.CN.md](lab_requirements.CN.md) | 实机实验条件：吊架、场地、安全、时间，供与老师确认 | 待确认 |
| [flair/reproduction.CN.md](flair/reproduction.CN.md) | FLAIR 六足复现（数据在 `flair/results/`） | 历史调研，已不在主线 |
| [ur7e_diffusion_policy/deployment_record.CN.md](ur7e_diffusion_policy/deployment_record.CN.md) | UR7e Diffusion Policy 部署记录 | 历史项目，已不在主线 |

## 相关资料

- GRAM 服务器环境核查与复现风险：[02_learning/gram/07_server_and_reproduction.CN.md](../02_learning/gram/07_server_and_reproduction.CN.md)
- 服务器怎么用：[02_learning/platform/server_guide.CN.md](../02_learning/platform/server_guide.CN.md)

## 记录要求

每条记录写明：目的、代码版本（仓库与提交号）、环境、命令或配置、结果文件、结论与边界。区分"能运行""核心结果已对齐""目标平台已部署"三种程度。
