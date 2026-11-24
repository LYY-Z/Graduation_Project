# 代码索引

| 目录 | 用途 |
|---|---|
| [diffusion_policy_ur7e](diffusion_policy_ur7e/README.CN.md) | 当前 UR7e 与腕部相机适配项目 |
| [diffusion_policy](diffusion_policy/README.md) | 原 Diffusion Policy 源码，供论文与实现学习 |
| [locoformer](locoformer/README.md) | lucidrains 第三方实现，供长历史策略与 PPO 学习 |
| [references](references/README.md) | FLAIR、TAM、BabyLocoFormer、MetaMorph 等参考仓库 |

## 源码获取与版本

上述项目以普通源码目录纳入主仓库。克隆本仓库即可取得已保存的源码，无需初始化 Git 子模块；各项目的依赖、数据与模型仍按对应说明准备。

| 项目 | 来源 | 本次纳入时的提交 |
|---|---|---|
| Diffusion Policy | [官方仓库](https://github.com/real-stanford/diffusion_policy) | `5ba07ac6661db573af695b419a7947ecb704690f` |
| UR7e 适配工程 | 本项目维护；上游源码与控制补丁见工程内 `third_party/sources.json` | 原独立工程 `ac98a2b33692afc7cb8b72d713c37f4c66a907fe`，包含此次纳入的文档修订 |
| LocoFormer | [lucidrains 第三方实现](https://github.com/lucidrains/locoformer)，不是论文作者发布 | `79ce9d72d1137015e0212284f06656c83bb414e7` |
| FLAIR | [官方仓库](https://github.com/adaptive-intelligent-robotics/FLAIR)，v1.0.0 | `9e1fa31a8f39b912c5edb61bd65ba15289241276` |

其余参考项目的来源与版本见 [references/sources.json](references/sources.json)。上游许可证随源码保留，后续修改由本仓库提交追踪。

UR7e 模型权重按 [`checkpoint_manifest.json`](diffusion_policy_ur7e/models/checkpoint_manifest.json) 校验，并通过 [`fetch_checkpoint.py`](diffusion_policy_ur7e/scripts/fetch_checkpoint.py) 获取；权重和本地环境不随 Git 提交。

活动项目的源码、权重、第三方依赖和测试保持原结构。旧服务器镜像、UR7e 旧副本和早期部署参考压缩保存在[归档](../99_archive/README.md)，不作为运行入口。

本目录不保留复制的 Linux Python 环境与安装缓存。服务器环境按各项目文档独立准备；本次目录整理未连接或修改服务器。
