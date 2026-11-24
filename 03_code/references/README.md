# LocoFormer 学习参考源码

本目录用于本地阅读，保留六个核心项目的源码快照。现有主算法库位于 [../locoformer](../locoformer/README.md)。

| 项目 | 学习重点 | 入口 |
| --- | --- | --- |
| BabyLocoFormer | 身体生成、TXL 与训练接线 | [生成脚本](BabyLocoFormer/model/generate_quad.py)、[算法子模块](BabyLocoFormer/rsl_rl/rsl_rl/modules/actor_critic_transformerxl.py) |
| GenBot1K 所属项目 | 多本体生成、关节描述和配置 | [生成代码](embodiment-scaling-laws/generation)、[结构样例](embodiment-scaling-laws/learning_sample) |
| MetaMorph | 观测补齐、掩码和动作过滤 | [环境封装](metamorph/metamorph/envs/wrappers/multi_env_wrapper.py) |
| URMA | 逐关节编码与共享策略 | [策略代码](one_policy_to_run_them_all/one_policy_to_run_them_all/algorithms/uni_ppo/ppo/policy.py) |
| GenLoco | 多形态四足控制 | [项目说明](GenLoco/README.md) |
| BodyTransformer | 身体结构注意力 | [项目说明](BodyTransformer/README.md) |

源码快照包含代码、许可证、文档和小型文本配置。仿真框架、SDK、网格、权重、完整数据集和 Git 历史在服务器部署时准备。源码中引用的运行资产可能尚未配备。

Baby 的自定义 RSL-RL 源码用于理解网络与训练；GenBot 另保留一个四足 URDF 和元数据供阅读。各项目原始提交、保留范围和后续参考来源见 [sources.json](sources.json)。

本次下载的完整仓库已移入 Windows 回收站，可按需恢复。
