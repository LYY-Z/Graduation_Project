# DDPM 与 Diffusion Policy 学习手册

这套资料按“基础 → 论文 → 官方源码 → 部署代码 → 复习”组织。首次学习按下表顺序阅读；复习时用疑问索引定位，不必重读全部章节。

| 顺序 | 内容 | 入口 |
|---|---|---|
| 1 | 机器学习、DDPM、机器人控制与 RL 背景 | [机器学习与模仿学习](01_foundations/01_ml_dl_and_imitation.md) · [DDPM 完整推导](01_foundations/02_ddpm_from_intuition_to_formula.md) · [控制与 RL](01_foundations/03_robot_control_and_rl.md) |
| 2 | 问题、建模、方法、网络、实验与局限 | [中文阅读](02_paper_study/00_paper_chinese_reading.md) · [问题与流程](02_paper_study/01_problem_and_full_pipeline.md) · [公式](02_paper_study/02_action_diffusion_and_formulas.md) · [网络与控制](02_paper_study/03_control_network_and_design.md) · [实验](02_paper_study/04_experiments_appendix_limits.md) |
| 3 | 官方仓库、配置、训练与评估 | [论文到源码](03_code_and_practice/01_paper_to_official_code.md) · [13 节代码教材](03_code_and_practice/code_study/README.md) · [最小复现](03_code_and_practice/02_minimal_reproduction_and_debug.md) |
| 4 | UR7e 硬件输入、checkpoint、推理与受限执行 | [六章部署代码教材](05_code_and_deployment/README.md) · [已完成部署记录](deployment_record.CN.md) |
| 5 | 查公式、回顾疑问和准备汇报 | [公式卡](04_review/01_symbols_and_formula_cards.md) · [疑问索引](04_review/02_faq_and_question_index.md) · [复述与自测](04_review/03_paper_recap_and_self_test.md) |

## 学习目标与复习路线


不看资料时，你应能画出并解释：

```text
最近的图像和机器人状态 O_t
          │
          ├── 视觉编码与状态特征 ──┐
          │                       ↓ 作为条件
随机动作计划 A_t^K ──反复预测噪声并去噪──> A_t^0
                                             │
                                  只执行前 T_a 个动作
                                             │
                                   得到新 O_(t+T_a)，重复
```

这里有两个完全不同的时间轴：

| 记号 | 含义 | 例子 |
|---|---|---|
| `t` | 机器人真实地行动和再次观察的时刻 | 现在、0.1 秒后、0.2 秒后 |
| `k` | 一次规划内部从噪声去到动作计划的步骤 | `K, K-1, ..., 0` |

把它们混成同一个 `t` 是读这篇论文最常见的混乱来源。

每读一章先回答：输入是什么？输出是什么？解决什么失败模式？训练和推理分别怎样使用？首次学习的顺序见上表。

### 公式复习

先看 [符号表与公式卡](04_review/01_symbols_and_formula_cards.md)，再按问题跳转：

- “高斯噪声是什么、为什么有平方根？” → DDPM 的前向过程。
- “反向均值为什么是这个式子、`sigma` 从哪来？” → DDPM 的贝叶斯后验与反向采样。
- “为什么 DDIM 可以跳步、score 为什么要除？” → 条件动作扩散的 DDIM/score 小节。

公式读法固定为：**变量是什么 → 在训练还是推理用 → 公式想得到什么 → 每个系数为什么在这里**。不要从系数开始背。

### 汇报复习

先读论文精读 01、03、04；然后完成 [论文复述与自测](04_review/03_paper_recap_and_self_test.md) 的 2 分钟、5 分钟和 10 分钟复述。

答辩至少应说出：

1. 它学习的是条件动作序列分布，而不是一个单动作；
2. 扩散采样能保留多个合理动作模式；
3. 只执行序列前段并重规划，使控制保持闭环；
4. 论文用多任务、消融和真实机器人实验提供证据，同时也有数据覆盖和推理速度的局限。



## 代码与验证资料

当前工程为 [diffusion_policy_ur7e](../../03_code/diffusion_policy_ur7e/README.CN.md)；原论文实现为 [diffusion_policy](../../03_code/diffusion_policy/README.md)。原始部署证据保存在 [code.zip](../../99_archive/code.zip)，整理后的事实与指标见[部署记录](deployment_record.CN.md)。旧部署六章、早期组织计划、清单与报告插入稿已收录 [history.zip](../../99_archive/history.zip) 的 `organization_20261123/`，现行代码学习统一使用 `05_code_and_deployment/`。

训练噪声 MSE 降低不等于闭环任务成功。原工程的实机记录与后续重构的离线检查分别解释，操作以当前项目 README 和 Guide 为准。

继续：[LocoFormer](../locoformer/README.md) · [学习总入口](../README.md) · [汇报资料](../reports/README.md)。
