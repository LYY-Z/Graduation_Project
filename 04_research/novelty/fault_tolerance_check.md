# 可行性核查：轮—腿冗余容错运动（Go2-W）

核查日期 2026-11-25。工具：本地文献表 + WebSearch/WebFetch 约 8 轮；未用 Google Scholar/IEEE Xplore 原生检索。"未找到"只对此范围成立。

## 1. 基础论文（正式发表，足式容错 RL）
| 论文 | 出处 | 代码 |
|---|---|---|
| FT-Net | RA-L 2023，10.1109/LRA.2023.3329766 | 仅图与补充材料，无训练器 |
| Random Joint Masking | ICRA 2024（arXiv 2403.00398） | 无 |
| Multi-Task Active FT Controller（SOLO8） | ICRA 2024 | 未找到 |
| DreamFLEX | ICRA 2025 | 无 |
| FT-CPG（Go1，多关节） | RA-L 10(7) 2025 | 未找到 |
| Contrastive Forward Prediction | CoRL 2025（PMLR 305） | 未找到 |
| FT-WBC（Go2+臂） | CoRL 2026 作者声明录用 | "coming soon" |

- ADAPT（arXiv 2312.17606，执行器退化，Isaac Gym）有代码 github.com/WentDong/Adapt，README 称投 DAI 2023，**正式 venue 未确认**，不可当"顶会基础论文"。
- 最可用的代码底座：IIT `fault-locomotion-isaaclab`（Isaac Lab，Go2，含训练/部署），对应 MoE 容错论文，**仅 arXiv 2606.25965，未录用**。发布的 Go2 权重用真值故障标签（oracle），12 腿动作，需自行移植到 16 自由度。
- 腿故障=PD 刚度阻尼置零（free-swing），源码已有，可借鉴。
- 本地 venue 表中"容错"条目 ICRA26/RA-L 另有 RENet（视觉失效，不相关）、TOLEBI（双足，ICRA26）。

## 2. 查重（轮足 × 容错）
未找到任何"轮足/轮式四足 + 执行器失效 RL 容错"的直接工作。最近 5 项：
1. IIT Kyon "Adaptive Gait Timing"（arXiv 2608.07328，2026-08，预印本）：纯腿，**把 "fault tolerance in hybrid wheeled-legged systems" 明列为未来工作**。差别：无轮。同时是抢发风险信号。
2. MoE 容错（arXiv 2606.25965）：纯腿，Go2。
3. FT-WBC（CoRL26）：腿故障下的腿臂操作，无轮。
4. 轮式移动机器人容错（Mecanum arXiv 2512.06444；重载轮式 arXiv 2502.03278）：经典/分层控制、无腿，无轮—腿切换。
5. 双足轮足跌倒恢复 FTSR（RA-L 11(8) 2026）：是摔倒恢复，不是电机失效。
判定：**未覆盖**（置信度中等；中文库、IEEE 原生检索未查）。

## 3. 价值
- IJRR 2025 综述（Ha 等，Learning-based legged locomotion，10.1177/02783649241312698）目录含 §8.5 "Hybrid Wheeled-legged Locomotion" 与 §8.4 "Safety"——**轮足混合明确是开放问题**；正文未能抓取，"容错"是否被点名**未核实**。
- 容错被点名：Kyon 论文（见上）。
- 现实投稿：RA-L、ICRA/IROS 工作坊或 IROS 短文；顶会（CoRL/RSS）需要强实机结果，本科周期偏难。毕设论文+一篇 RA-L/IROS 投稿为合理上限。

## 4. 可行性
- 仿真：Isaac Lab 里屏蔽轮/腿电机很容易——事件中把对应关节 stiffness/damping 置零（free）或把 target 钉住并设大阻尼/锁定（lock），或乘以效力 mask；IIT 仓已有范例。难点不在故障注入，而在：(a) Go2-W 轮足混合基础策略要先训出来（robot_lab 有 Go2-W 环境，需确认其 wheel 速度控制与走/滚两种模态都可用）；(b) "改走/改滚"模态要靠奖励设计涌现，易出现不理想的拖行；(c) 故障 onset 随机、估计器（历史/特权蒸馏）需自己做；(d) 轮坏时"改走"，轮是脚端的圆柱，行走模态本身非标准步态。
- 实机（下述凭 Unitree 通用 lowcmd 经验，**本次未查官方文档核实 Go2-W 具体接口**）：lowcmd 下对目标电机 kp=kd=tau=0 理论上可模拟无力；轮电机 kd=0 即自由转。风险：腿关节置零后机身失支撑，必须吊架/保护；锁死用高 kd/位置钉死，易过流发热；须先关闭 sport service。软件屏蔽无法模拟真实电机的热/摩擦行为，只能叫"模拟故障"。
- 工期：3–4 个月本科——仿真验证+一类故障（轮失效）实机演示可完成；多故障+实机全覆盖偏紧。

## 5. 致命风险与结论
1. 基础轮足策略训不稳/实机 sim2real 失败（吞掉一半工期）。
2. 被抢发：Kyon 论文已点名该方向，窗口可能只有数月。
3. "无力轮子"被动滚动对行走的影响小、"腿坏改轮"需要腿仍能撑身，实验场景若太容易则创新性被审稿人质疑。
4. 对照"只用腿的容错方法"需自行移植 IIT/AcL 类方法，无现成 Go2-W 版本。

**结论：有条件可行。** 条件：先在 2–3 周内确认 robot_lab Go2-W 能稳定训出走/滚策略；故障范围收窄到"单轮失效+单腿关节失效"。
评分：创新性 7/10，论文价值 6/10，可行性 6/10。
