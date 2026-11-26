# 当前状态与交接

更新：2026-11-24。这是所有 agent 和协作者的**第一入口**：只记录当前状态和判断，详细证据通过链接查看。长期目标与质量标准见[研究目标与标准](04_research/00_goals_and_standards.CN.md)。

## 1. 阶段

**选题调研（第 1–2 周）**：平台已收敛为 Go2-W（2026-11-24）。正在按 Go2-W 重新筛选基础论文和创新空间，尚未确认基础论文、研究问题或创新点。

## 2. 已确认的决定

| 日期 | 决定 | 依据 |
|---|---|---|
| 2026-11-24 | 研究范围放宽为机器人运动控制中的学习驱动或学习与控制结合方法（RL、VLA、世界模型等）；扰动适应与恢复只是可选方向 | 用户更新 |
| 2026-11-24 | 路线：基础论文 → 复现 → 在其上创新 → 对照与消融 → Go2-W 与 UR7e 双平台实机 → 论文；工期 3–4 个月 | 用户要求 |
| 2026-11-24 | 计算在用户服务器（个人工作空间 + 独立 Conda 环境）；本地 PC 只做文献、代码和文档 | 用户要求 |
| 2026-11-24 | 目录调整为 02 学习 / 04 研究 / 05 实验 / 06 汇报；本文件作为交接入口 | 用户确认方案 |
| 2026-11-24 | `03_code` 中的空子模块目录不作处理 | 用户确认，对后续工作无影响 |
| 2026-11-24 | **平台改为只做 Go2-W**，UR7e 不再作为要求；PACE 不再是默认首选，与其他候选按 Go2-W 重新比较 | 用户决定：两个平台同时实现不现实 |
| 2026-11-24 | **基础论文不必是 Go2-W 原生**。选题排序以论文本身价值和后续创新方向为主，复现难度为次；只要有可复现的基础（代码或足够细的方法描述），平台不必完全一致 | 用户更新 |
| 2026-11-24 | **选题以论文价值和后续创新点为主**；复现只需有基础条件、服务器能兼容即可接受；基础论文尽量选近两年（2025–2026） | 用户更新 |
| 2026-11-25 | 创新点不必是空白领域：有明确动机的方法结合、针对性改进、面向轮足的适配均可，但须有对比与消融证明 | 用户确认（无科研经验，请主模型以专家身份把关） |
| 2026-11-25 | 方案必须能回答传统控制方向的质疑：为什么学习方法比传统控制（MPC、WBC、PD 等）更好；决策备忘需含该论证，实验应含传统控制基线 | 用户要求 |
| 2026-11-25 | **服务器已有环境的权重放低**：只要能在服务器（Linux + Blackwell GPU）上运行，重装或新建环境都可以接受；选题不应因技术栈不同而排除 | 用户要求跳出既有思路、扩大方向 |

## 3. 暂定判断（可被新证据推翻）

- ~~双平台筛选条件放在最前面~~（2026-11-24 起不再适用，平台只做 Go2-W）。此前按双平台门槛得出的排序需要重评，尤其是因 G1 被降级的 Go2/腿足候选。
- **初步看最可行的层级**是"关节空间学习策略 + 底层 PD/速度伺服"，分平台训练、分平台部署：Go2-W 可复用 robot_lab 加 rl_sar 的链路，UR7e 用关节位置/速度目标。力矩层方法、在 Go2-W 上做端到端 VLA、需要大量真实数据的世界模型，部署风险较高，但仍按同一标准评估，不预先排除。依据见[双平台接口审查](02_learning/platform/interfaces.CN.md)和[平台与 benchmark 审查](04_research/reviews/platform_and_benchmark_review.md)。
- **扰动恢复方向的常见组合已被占据。** 历史编码器加自适应策略、冻结策略加门控/有界残差、变化检测加工况召回都已有先例。详见[阶段比较 §4、§8](04_research/review.CN.md)。
- 阶段样本 GRAM、ESCP、SADL、TAM 等**未被确认为基础论文**。
- 第二轮粗筛：四个方向都没有找到腿足和机械臂都有公开实机链路的现成底座。双平台问题最自然落在"关节目标 → 伺服/执行器 → 关节响应"这一层；端到端 VLA 只在 UR7e 上可行。精读结论：PACE 作为复现与部署底座最稳，RWM-U 和 DSRL 不作首选；创新点尚未成立。

## 4. 已核验的条件与未解决问题

- **服务器已核验**（[盘点记录](05_experiments/server/inventory.CN.md)）：2 × RTX PRO 5000 **Blackwell**（单卡约 48 GB，sm_120），驱动 580，CUDA 13.0；96 线程 CPU、251 GiB 内存；Ubuntu 22.04 + ROS 2 Humble。根分区只剩 30 G，工作空间需放到 `/data3`（待确认后再建）。已有 Isaac Sim 5.1 + PyTorch 2.7 cu128 环境可作为起点。固定在 CUDA 11.x / Isaac Sim 4.x 的旧代码需移植。
- 未解决：Go2-W 能否开放底层 `lowcmd` 控制、UR7e 的 PolyScope 版本、实机安全设施和实验室可用时间，在调研中逐项核对。

## 5. 下一步

1. ~~只读盘点服务器~~（已完成）。
2. ~~四个方向粗筛~~（已完成，[screening/](04_research/screening/)，约 60 篇）。按 G1–G5 门槛缩小名单，见[候选比较 §0](04_research/review.CN.md)。
3. ~~精读 PACE、RWM-U、DSRL~~（已完成，结论见[候选比较 §0.4](04_research/review.CN.md)）。PACE 可行性最高，但三篇都还没有导出通过查重的创新点。
3a. ~~按 Go2-W 单平台重新筛选~~（已完成，见[候选比较 §0.5](04_research/review.CN.md)）。
3b. ~~精读 LocoWM、MoE-CTS、热与负载感知~~（已完成，见[候选比较 §0.6](04_research/review.CN.md)）。
3c. ~~用户在 A/B/C 中选择~~（用户改为放宽平台限制，按论文价值重排，A/B/C 保留为候选）。
3d. ~~按新标准重排~~（已完成，见[候选比较 §0.7](04_research/review.CN.md)）。
3e. ~~首推 CaT~~（CaT 为 2024 年、价值中等，按用户新标准降为备选）。
3f. ~~精读具身尺度律、SimDist、Multi-Loco~~（已完成，见[候选比较 §0.8](04_research/review.CN.md)）。
3h. 用户要求扩大选择面：再选其他论文和方向，对价值高但复现难的与复现易的统一评估（已完成，见[候选比较 §0.9](04_research/review.CN.md)）。**待用户选方向**，再对选中的 2–3 篇精读和复核发表状态。SimDist 暂不定。
3g. （暂缓）暂定 SimDist 为主候选、Multi-Loco 为备选。确认前需排除 SimDist 的工程风险：JAX 在 sm_120 上能否运行、Go2-W 的定位方案（用户确认 Go2-W 带激光雷达，型号与 SimDist 所用 LIO 是否兼容待核）、轮打滑方向的全文查重。
3i. ~~三项排查 + 传统控制证据~~（已完成）。ASAP 因需机身全局状态（动捕）被否；查重为部分覆盖，轮足/轮通道未见先例。
4. **决策备忘第 2 版**（[decision_memo.CN.md](04_research/decision_memo.CN.md)）：Go2-W 差距归因与分阶段对齐——PACE 悬空辨识复现 + 低维轮—地接触补偿；三份 Opus 审核结论为"有条件批准"（[review_opus/](04_research/review_opus/)）。**待用户与老师确认**，实机条件见 [lab_requirements](05_experiments/lab_requirements.CN.md)。
4'. 原计划：写一份决策备忘：一篇基础论文 + 1–2 个创新方案，附对照、实机方案、预算与风险，交用户与老师确认。

## 6. 决策日志

重要判断改变时追加一行：日期、改变内容、原因、证据链接。被取代的文档在开头注明"已被取代"并链接到这里。

- 2026-11-24：交接入口由 `02_learning/00_research_handoff.CN.md` 改为本文件；该文件的长期标准部分迁至 `04_research/00_goals_and_standards.CN.md`，研究范围按用户更新改写。
- 2026-11-24：完成服务器只读盘点。GPU 为 Blackwell 架构（sm_120），据此把"能否在 PyTorch ≥2.7 / Isaac Sim 5.x 上运行"列为候选筛选门槛。
- 2026-11-24：完成第二轮四方向粗筛，按 G1–G5 门槛选出 PACE、RWM-U、DSRL 精读。已核实：PACE 的 arXiv 元数据写 IJRR 2026，论文的运动训练环境未公开（issue #30），作者同事已在轮足上用过 PACE（issue #36）；RWM-U 无录用信息。依据见 [review §0](04_research/review.CN.md)。
- 2026-11-24：精读完成。DSRL 被排除（Go2-W 上不成立）；RWM-U 降为备选（发表级别低、发布不全、主要方向已被覆盖）；PACE 定为暂定底座候选，创新点待定。已核实：OmniReset（arXiv 2603.15789）已按 PACE 流程在 UR5e/UR7e 上辨识。
- 2026-11-24：用户决定平台只做 Go2-W，UR7e 不再要求。原因：双平台同时实现不现实（第二轮粗筛也未找到双平台底座）。影响：G1 门槛取消，PACE 不再默认首选，按 Go2-W 重新比较。
- 2026-11-24：按 Go2-W 重排。LocoWM（预印本，原生 Go2-W，环境与服务器一致，已核对仓库）和 MoE-CTS（RSS 2026，Go2，带权重）升到最前；热与负载感知被识别为 Go2-W 特有的未解决问题；PACE 降为组件。依据见 [review §0.5](04_research/review.CN.md)。
- 2026-11-24：Go2-W 三项精读完成。LocoWM 适合作复现底座，但方法薄；MoE-CTS 已核实为 RSS 2026，但工作量重；热与负载感知最接近的工作是 Ségas 等的预印本（2026-11-17，Go2）。三条路线的取舍交用户决定。
- 2026-11-24：用户放宽基础论文的平台限制：不必 Go2-W 原生，以论文价值和创新方向为主、复现基础为次。A/B/C 三条路线不作废，与其他候选一起按新标准重排。
- 2026-11-24：放宽平台后重排并核对发表状态。SimDist、MoE-CTS 在 RSS 2026 论文集核到；CaT 为 IROS 2024 且基于 Isaac Lab。暂定首推 CaT + Go2-W 热/轮速约束，次选 SimDist。依据见 [review §0.7](04_research/review.CN.md)。
- 2026-11-24：用户明确以论文价值和创新点为主、近两年优先。CaT（2024）降为备选；精读具身尺度律、SimDist、Multi-Loco。依据见 [value_rerank](04_research/screening/value_rerank.md)、[value_supplement](04_research/screening/value_supplement.md)。
- 2026-11-24：三篇精读完成。SimDist 价值与创新点组合最好但工程风险高；Multi-Loco 证据偏薄、复现中等；具身尺度律算力不可及且核心目标已被 LocoFormer 覆盖。暂定 SimDist 为主候选。依据见 [review §0.8](04_research/review.CN.md)。
- 2026-11-24：SimDist 暴露出外接 GPU 笔记本、技术栈多、底座 6–8 周等实际顾虑；用户要求扩大选择面并统一评估价值与复现难度。启动第三轮检索。
- 2026-11-24：第三轮完成。新增 ASAP、TEMPO、Omni-Perception、Hiking in the Wild、FlashSAC 等价值高且复现/部署可控的候选；ASAP 最均衡。依据见 [review §0.9](04_research/review.CN.md)。
- 2026-11-25：启动 ASAP 精读、"辨识 + delta action"查重、Go2-W 平台可行性核实三项排查；新增要求：方案须能回应传统控制的质疑。
- 2026-11-25：排查完成。ASAP 需动捕，否决；Go2-W 底层模式下无官方机身速度，倾向只用本体感觉数据的方法。决策备忘草案：以 PACE 为基础论文，创新点为不需动捕的轮足着地残差（[decision_memo](04_research/decision_memo.CN.md)）。
- 2026-11-25：用户确认 Go2-W 为宇树开发版；已写实机实验条件清单（05_experiments/lab_requirements.CN.md）；启动三项 Opus 审核（PACE 原文、最接近工作全文、最终查重与审稿批判），输出至 04_research/review_opus/。
- 2026-11-25：三份 Opus 审核完成并据此修订备忘：研究问题改为"差距归因 + 检验 PACE '悬空数据足够'在轮子上是否成立"；补偿改为接触侧 4–8 个物理参数（Dao & Fern 显示高维残差 CMA-ES 学不动）；加相机 + AprilTag 使打滑可观测；补强基线（调过的域随机化等）；设第 0 周与第 6 周关卡；正式方案 B。更正证据卡与备忘中 PACE 的若干事实（首个应用不成立、#22 维护者改口、ANYmal 数据已公开、运动实验用 Isaac Gym）。
- 2026-11-25：用户请主模型代为判断。主模型推荐方案 1（PACE 复现 + 差距归因与轮—地接触补偿），理由：最符合用户"论文价值与创新优先、近两年"标准，零结果也可发表为结论，答辩最好回应传统控制；切换条件：第 0 周底层权限或刚性悬吊架不具备，则改走方案 2（电机过热 + 约束训练）。待用户与老师确认。
- 2026-11-25：用户保留方案 1，并要求整理向老师汇报的材料。已写 [06_reports/pace/report.CN.md](06_reports/pace/report.CN.md)：PACE 精读（价值、问题、局限、挑战、方法细节、实验与证据强度、与传统控制比较、复现难度、创新价值）+ 课题方案 + 读论文的问题清单 + 老师可能的提问。前期以 MuJoCo 假真机开发为主，第 5 周集中采真机数据。
- 2026-11-25：用户要求把其他好的备选也按 PACE 汇报的格式总结。启动三份 Opus 备选汇报：电机过热（06_reports/thermal/）、雷达感知（06_reports/perception/）、部署时快速适应（06_reports/adaptation/）；完成后做横向比较。
- 2026-11-25：三份备选汇报完成（Opus，子代理无法写报告文件，由主会话写入）：电机过热 6/10（基础论文 Ségas 预印本 + CaT）、部署时快速适应 6/10（TEMPO，NeurIPS 2026，无代码）、雷达避障 5.5/10（Omni-Perception，训练代码未公开）；PACE 主方案 7/10 维持首选。横向比较见 [06_reports/options_overview.CN.md](06_reports/options_overview.CN.md)。
- 2026-11-25：用户指出调研陷入循环（反复围绕 sim-to-real 对齐与适应），要求跳出既有思路。启动第四轮发散检索：基础模型/VLA/LLM 用于足式机器人、技能与运动生成（模仿、敏捷技能、移动操作）、真实世界学习与 real-to-sim；输出 `04_research/screening/round4_*.md`。
- 2026-11-25：第四轮发散检索完成，9 个新方向汇总于 [options_overview](06_reports/options_overview.CN.md)。主模型判断最有希望的新方向：轮足动作模仿（无轮数据迁移到轮足）与 3DGS 视觉轮足策略（VR-Robo）；已启动两份 Opus 精读汇报，完成后与 PACE 统一比较，不预设 PACE 为首选。
- 2026-11-25：两个新方向的 Opus 可行性核查完成：轮足动作模仿 5.5/10（基础 Fu 等 Nat Commun 2026；价值论证风险大）、3DGS 视觉轮足 5.5/10（VR-Robo 代码只开源一半）。扩大检索后 PACE 方案（7/10）仍为首选。按用户要求，未通过可行性判断的方向不写完整方案。
- 2026-11-25：第五轮系统普查完成：会议（385 篇，venue_sweep_2025_2026.md）、期刊（38,332 篇中筛出 151 篇，venue_sweep_journals.md）、跨领域借鉴（10 个领域，cross_domain_sweep.md，车辆动力学最有价值）、arXiv 轮足+学习预印本（69 篇，最后一轮新增 0，saturation_closure.md）。三源一致：轮足上的仿真—真机对齐未见先例。待办：精读最接近约 5 篇全文做最终查重（含 Terramechanics-Aware Adaptive Quadrupedal Locomotion，RA-L 2026），再写最终文档。用户已要求暂停。
- 2026-11-25：**最终选题（待用户与老师确认）**：不可转向轮足（Go2-W）的腿辅助转向，基于实测标定的轮—地模型（车辆动力学少参数模型 + PACE 悬空辨识）的学习控制；用改编的汽车标准操纵试验评价。理由：用户要求加入开拓性标准；四份普查与全文查重显示核心空白在（[final_check](04_research/novelty/final_check.md)、[pioneering_check](04_research/novelty/pioneering_check.md)），Science Robotics 2026 滑移转向装载机工作为顶刊依据。设第 1–2 周实机探针（腿姿对转弯功率影响 <10% 则走保底）。详见 [decision_memo 第 3 版](04_research/decision_memo.CN.md)。
- 2026-11-25：用户要求参考文献须为顶刊顶会、创新可为组合/解决局限/跨领域等。从会议 167 篇、期刊 91 篇的局限与未来工作抽取（[limitations_conf](04_research/screening/limitations_conf.md)、[limitations_journal](04_research/screening/limitations_journal.md)）出发，按 12 种创新方式生成候选并核查。结论：维持腿辅助转向为主线（核心依据改为顶刊顶会：Lee SciRob 2024、PACE IJRR 2026、滑移转向装载机 SciRob 2026、Swift Nature 2023、Deep Dynamics RA-L 2024）；新增第一备选'轮—腿冗余容错'（7/6/6）；'滚/走转换驱动'6/5/6 风险为结论平凡。核实 Go2-W 读不到单电机电流，只能用整机 power_v×power_a 与 tau_est×dq。
- 2026-11-25：按用户要求，把接手以来全部方向（含老师给的 LocoFormer、TAM、FLAIR、Diffusion Policy、GRAM/RMA/ESCP/SADL/ASID 等）统一评分比较，见 [options_overview](06_reports/options_overview.CN.md)。结论不变：主线腿辅助转向 + 标定轮—地模型；老师给的论文多作背景、基线与方法参考。
- 2026-11-25：腿姿辅助转弯专项查重：部分覆盖（Hao 等 RICAI 2023 用腿缩轴距辅助滑移转向，规划+PID；Racing 2026 Go2-W 抗侧倾；ETH 系列未涉及）。主线保留，措辞改为在前人基础上，差异为擦地目标+多几何量+RL+实测侧向力模型；第 0 周增加理论收益估算。见 [leg_turning_check](04_research/novelty/leg_turning_check.md)。
- 2026-11-25：最终评估定稿：主线腿姿协同转弯 + 实测标定轮—地模型；核心科学问题明确为擦地、姿态代价、稳定性的权衡（学习的必要性来源）；新增几何规则基线（Hao 2023 式）为关键对照。第一备选轮—腿冗余容错。待用户与老师讨论。
- 2026-11-25：用户质疑腿姿转弯'已被 Hao 做过、不难想到却无论文'。引入价值信号检验（顶会同类线 / 强组点名未来工作 / 实际需求）：腿姿转弯仅见于小会，降为备选；**轮—腿冗余容错三项通过，定为最终主线**（基础论文 Random Joint Masking ICRA 2024 等；IIT Kyon 预印本点名轮足容错为未来工作）。保底为轮—地标定对齐。见 [decision_memo 第 4 版](04_research/decision_memo.CN.md)。
- 2026-11-26：写成向老师汇报的选题文档 [06_reports/fault_tolerance/report.CN.md](06_reports/fault_tolerance/report.CN.md)（选题过程、老师方向的去向、Random Joint Masking 精读、方案、Q&A）。基础论文已核实 ICRA 2024 pp.9751–9757，无代码。旧 PACE 汇报标注为已被取代。
- 2026-11-26：用户指出基础论文无代码、超参不全。补复现方案：robot_lab 作底座（与 legged_gym 同源），IIT fault-locomotion-isaaclab（BSD-3，Isaac Lab，Go2，2026-11 更新）作实现参考，缺失超参用默认值并问作者，复现目标为表 II 相对趋势；有代码的备选基础论文为 GRAM（Isaac Lab 1.0，需移植）。方向不变。
- 2026-11-26：决策备忘第 5 版。研究问题（轮足局部执行器变化）不变；基础论文由 Random Joint Masking（无代码）改为 GRAM（RA-L 2026，官方代码，老师给的论文）；核心机制采纳 Codex 建议的'选择性鲁棒适应'（经主模型核实 DMCM、CERTAIN、GRAM 出处），加理想上限检验关卡。选题汇报需按新基础论文重写第 2 部分，待用户确认后进行。
- 2026-11-26：**最终定稿**：主线 GRAM + 选择性鲁棒适应；条件备选 AugMPC（需 MPC 支持）、MoE-CTS/RoboGauge（偏评价）；保底 GRAM 复现 + 失效分析。综合 Codex 两轮意见，主模型收窄候选面、补充因素分组与变化类型、第 1 周代码移植关卡。已派 Sonnet 精读 GRAM 并审代码（输出 04_research/candidates/gram.md），完成后重写选题汇报。
