# 全部选题方向的统一比较

日期：2026-11-25。本文汇总从接手至今出现过的全部方向，包括老师给的阅读论文与原有方向、前几轮调研的候选，以及系统普查后的新方向，用同一套标准比较。最终选择与方案见[决策备忘第 3 版](../04_research/decision_memo.CN.md)。

## 1. 评分标准

| 维度 | 看什么 |
|---|---|
| 创新 | 能否在 Go2-W 上提出清楚、可查重通过的新东西。组合、解决局限、跨领域迁移、新能力、检验主张都算 |
| 价值 | 基础论文是否为顶刊顶会正式发表；成果能投到什么级别 |
| 可行 | 代码与复现基础、服务器可运行（可重装环境）、Go2-W 实机条件、本科 3–4 个月能否完成、实机风险 |

分数为主模型评价（1–10 分），依据见各行链接。"发表"一列只写已核实的正式出处。

## 2. 总表

### A. 老师给的论文与接手时的原有方向

| 方向 | 基础论文与发表 | 创新 | 价值 | 可行 | 结论与主要原因 |
|---|---|---|---|---|---|
| LocoFormer：长上下文跨形态适应 | CoRL 2025（PMLR v305） | 3 | 8 | 2 | 论文价值高，但无官方代码，训练规模极大（大量程序生成本体加极端随机化）；作者已在 Go2-W 变体上做了实机，核心目标被占（[学习手册](../02_learning/locoformer/README.md)、[具身尺度律核查](../04_research/candidates/embodiment_scaling.md)） |
| FLAIR：六足快速在线适应 | 已复现（Brax 六足） | 3 | 5 | 4 | 原任务是六足加正弦步态库的速度补偿，迁到 Go2-W 要重做控制器；在线补偿方向拥挤（[复现记录](../05_experiments/flair/reproduction.CN.md)） |
| Diffusion Policy（UR7e） | RSS 2023 / IJRR 2024 | 2 | 7 | — | 机械臂方向，平台已改为只做 Go2-W，不再适用（[部署记录](../05_experiments/ur7e_diffusion_policy/deployment_record.CN.md)） |
| TAM：力矩适配 | CoRL 2026 | 3 | 7 | 2 | 机械臂力矩接口；Go2-W 腿是位置指令、轮是速度指令，力矩合同不匹配（[阶段比较 §3](../04_research/review.CN.md)） |
| GRAM：鲁棒适应模块 | RA-L 2026，有 Go2 代码 | 3 | 6 | 6 | 方法对口，但"历史编码器 + 自适应策略"已被大量占据，创新空间小；可作适应类基线 |
| RMA / ESCP / SADL / ASID：扰动适应、在线辨识 | RSS 2021 / AAAI 2022 / 预印本 / RSS 2024 | 2 | 6 | 5 | 接手时的"扰动适应与恢复"主线；常见组合均已被做过，后来降为可选方向（[阶段比较 §4、§8](../04_research/review.CN.md)） |

### B. 前几轮调研的候选

| 方向 | 基础论文与发表 | 创新 | 价值 | 可行 | 结论与主要原因 |
|---|---|---|---|---|---|
| PACE：差距归因 + 着地接触补偿 | IJRR 2026，有代码 | 4 | 7 | 7.5 | 稳，但开拓性弱；**并入最终主线，作使能方法与保底**（[汇报](pace/report.CN.md)） |
| 电机过热 + 热约束 | 预印本 + CaT（IROS 2024） | 5 | 5 | 6 | 2026 年已有 4 篇，基础论文未正式发表（[汇报](thermal/report.CN.md)） |
| 部署时快速适应（TEMPO） | NeurIPS 2026，无代码 | 5 | 6 | 5 | 方向拥挤，真机在线更新有风险（[汇报](adaptation/report.CN.md)） |
| 雷达感知避障（Omni-Perception） | CoRL 2025，训练代码未公开 | 5 | 7 | 4 | 竞争多，L1 雷达偏稀，工程链长（[汇报](perception/report.CN.md)） |
| SimDist：世界模型 + 实机适应 | RSS 2026 | 6 | 8 | 3 | 实机要外接 RTX 4090 级笔记本做 50 Hz 规划，JAX 旧栈（[证据卡](../04_research/candidates/simdist.md)） |
| ASAP：动作残差对齐 | RSS 2025 | 4 | 8 | 3 | 需要机身全局状态（原作者用动捕），真机数据难采（[证据卡](../04_research/candidates/asap.md)） |
| 具身尺度律 | CoRL 2025 | 4 | 8 | 1 | 原训练约 160 卡 × 5 天，算力不可及 |
| Multi-Loco：扩散 + RL 跨形态 | CoRL 2025 | 5 | 6 | 5 | 论文证据偏薄，Isaac Gym 需移植（[证据卡](../04_research/candidates/multi_loco.md)） |
| MoE-CTS / RoboGauge | RSS 2026，有 Go2 权重 | 5 | 8 | 4 | 单次训练约 7 天，创新点偏评估工具（[证据卡](../04_research/candidates/moe_cts.md)） |
| LocoWM：世界模型残差 | 预印本（原生 Go2-W） | 4 | 4 | 7 | 未正式发表，方法薄（[证据卡](../04_research/candidates/locowm.md)） |
| RWM-U / DSRL | workshop / CoRL 2025 | 3 | 5 | 4 | RWM-U 发布不全；DSRL 在 Go2-W 上不成立（[证据卡](../04_research/candidates/rwm_u.md)、[DSRL](../04_research/candidates/dsrl.md)） |
| CaT 约束训练 | IROS 2024 | 3 | 5 | 8 | 年份偏早、价值中等；可作约束类工具 |
| DIAL-MPC / FlashSAC 等 | ICRA 2025 / RSS 2026 | 3 | 6 | 5 | 需外部定位，或只换算法、创新弱 |

### C. 跳出原有思路后的新方向（第四轮）

| 方向 | 基础论文与发表 | 创新 | 价值 | 可行 | 结论与主要原因 |
|---|---|---|---|---|---|
| 轮足动作模仿（无轮数据迁移到轮足） | Fu 等，Nature Communications 2026 | 6 | 7 | 5 | 价值论证难：轮子滚动时腿几乎不动，"像狗"可能更费电（[核查](../04_research/candidates/motion_imitation_report.CN.md)） |
| 3DGS 视觉轮足策略 | VR-Robo，RA-L 2025 | 6 | 6 | 4 | 重建、对齐、部署代码未开源，工程链最长（[核查](../04_research/candidates/gs_visual_report.CN.md)） |
| 能力感知语言导航 | StreamVLN，ICRA 2026 | 6 | 7 | 3 | 7B 模型需外接 GPU，系统链最长 |
| 学习型里程计 | Legolas，CoRL 2024 | 5 | 6 | 6 | 无代码；偏估计而非控制 |
| 学习型防侧翻安全过滤 | Gameplay Filters，CoRL 2024 | 6 | 6 | 4 | 实机侧翻风险，代码栈旧 |
| 大模型设计奖励 | SDS，CoRL 2025 | 3 | 5 | 7 | 新意弱 |

### D. 系统普查后的方向（顶刊顶会依据）

| 方向 | 核心依据（顶刊顶会） | 创新 | 价值 | 可行 | 结论与主要原因 |
|---|---|---|---|---|---|
| 腿姿协同转弯 + 实测标定轮—地模型 | Lee SciRob 2024；PACE IJRR 2026；滑移转向装载机 SciRob 2026；Swift Nature 2023；Deep Dynamics RA-L 2024 | 6 | 6 | 6 | **降为备选**。核心想法已见于 Hao 等 RICAI 2023（缩轴距助转弯），且只出现在小会，价值信号弱（[决策备忘](../04_research/decision_memo.CN.md)、[开拓性核查](../04_research/novelty/pioneering_check.md)、[最终查重](../04_research/novelty/final_check.md)） |
| **轮—腿冗余容错** | FT-Net RA-L 2023；Random Joint Masking ICRA 2024；DreamFLEX ICRA 2025；FT-CPG RA-L 2025；CoRL 2025 | **7** | **7** | **6** | **最终主线**（价值信号三项通过：顶会同类线、强组点名未来工作、实际需求）。容错是最稀疏主题之一，轮足上未见；多数基础论文无代码，有被抢风险（[核查](../04_research/novelty/fault_tolerance_check.md)） |
| 打滑率约束的牵引力控制 RL | 车辆 TCS/ABS + CaT | 6 | 6.5 | 5.5 | 打滑时地速估计最不准；可作主线的扩展任务（[跨领域](../04_research/screening/cross_domain_sweep.md)） |
| RL vs MPC 极限操控归因 | Song SciRob 2023 | 6 | 7 | 4 | 高速实机风险，工期紧 |
| 滚/走转换由能量还是可行性驱动 | Shafiee 等 Nat. Commun. 2024 | 6 | 5 | 6 | 平地上滚总比走省电，结论可能平凡（[核查](../04_research/novelty/mode_transition_check.md)） |
| 外挂 L1 自适应 | L1+RL，RA-L 2022 | 4 | 5 | 7 | 适应方向拥挤 |
| 运行时失效预警 | FIPER，NeurIPS 2025 | 5 | 5 | 6 | 单独成题偏薄 |
| 形态对称性 | IROS 2024 / ICRA 2024 | 3 | 4 | 9 | 作训练插件 |

## 3. 结论

**最终主线：轮—腿冗余容错**（见[决策备忘第 4 版](../04_research/decision_memo.CN.md)）。保底为轮—地标定对齐（PACE 延伸），备选为腿姿协同转弯。

判断方法是"价值信号检验"：有没有顶刊顶会的同类工作，有没有强课题组把它点名为下一步，有没有实际需求。腿姿转弯的核心想法只出现在小会，被降级；容错三项都通过。

老师给的论文与原有方向（LocoFormer、TAM、FLAIR、Diffusion Policy、GRAM 与 RMA 等扰动适应类）价值高，但对 Go2-W 本科毕设有硬伤：算力或代码不具备、接口不匹配，或方向拥挤。它们在论文中作背景与对照：GRAM、RMA 可作适应类基线；LocoFormer 说明适应类已有强先例。
