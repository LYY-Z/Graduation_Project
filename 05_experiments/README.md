# 实验记录

保存服务器盘点、复现、训练与实机实验的记录、数据和来源。讲解性内容放在 [02_learning](../02_learning/README.md)，汇报材料放在 [06_reports](../06_reports/README.md)。当前研究状态见 [STATUS](../STATUS.CN.md)。

| 记录 | 内容 |
|---|---|
| [服务器盘点](server/inventory.CN.md) | GPU、CPU、内存、磁盘、系统、驱动、CUDA、已有环境（不含密码） |
| [FLAIR 六足复现](flair/reproduction.CN.md) | Chicane 主对照的范围、执行、80 回合批次与指标；数据和来源在 `flair/results/` |
| [UR7e Diffusion Policy 部署](ur7e_diffusion_policy/deployment_record.CN.md) | 已完成的受限部署链路、实现来源和实测依据 |

每条记录写明：目的、代码版本（仓库与提交号）、环境、命令或配置、结果文件、结论与边界。区分"原任务能运行""核心结果已对齐""目标平台已部署"。

- [Go2-W 可行性核实](go2w_feasibility.CN.md)：底层接口、状态字段、robot_lab/rl_sar 支持与风险
- [实机实验条件](lab_requirements.CN.md)：悬吊架、场地、安全、时间，供与老师确认
