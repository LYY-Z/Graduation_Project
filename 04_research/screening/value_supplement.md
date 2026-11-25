# 基础论文补查：已发表且有代码的高价值候选（2026-11-24）

范围与方法：按用户新标准（论文价值 > 创新方向 > 复现基础，平台不必 Go2-W 原生）补查此前候选池（`screening/*.md`、`candidates/*.md`）漏掉的工作。已出现的论文不重复（PACE、SPI-Active、LocoFormer、CaT、DIAL-MPC、MoE-CTS、SAC 追上 PPO、RWM-U、DiffuseLoco/DMLoco、FLORES、ATRos 等均已在池中）。搜索工具对会议论文集覆盖有限，本表不是穷尽；2026 年 RSS/CoRL/ICRA/RA-L 的录用名单没有逐一过。

核实口径：
- **发表状态**写出处类型。「PMLR」指 proceedings.mlr.press 论文页；「arXiv 评论」指 arXiv 摘要页 Comments 字段；「Crossref」指 api.crossref.org 返回的记录；「自述」指项目页或 README 自称，未见官方论文集或期刊页。
- **代码**均通过 GitHub API 或 README 实际打开。「最近 push」取 API 的 `pushed_at`，不等同于最近一次功能提交。没有找到官方仓库的写「未找到」，不代表不存在。
- 我们的评价、设想与作者事实分开写；设想均标【设想】。

## 1. 主表

| # | 论文 | 发表与出处 | 代码与仿真器 | 平台 | 价值 | 可能的创新方向【设想】 | 迁到 Go2-W 的路径 | 风险 |
|---|---|---|---|---|---|---|---|---|
| 1 | **Towards Embodiment Scaling Laws in Robot Locomotion**（Ai 等，UCSD/TU Darmstadt/DFKI；arXiv 2505.05753） | CoRL 2025。[arXiv 评论](https://arxiv.org/abs/2505.05753)写 "CoRL 2025"；[PMLR v305 ai25a](https://proceedings.mlr.press/v305/ai25a.html) pp.3483–3515 | [BoAi01/embodiment-scaling-laws](https://github.com/BoAi01/embodiment-scaling-laws)，最近 push 2026-07-21，BSD-3；Isaac Lab（README 指向 Isaac Lab 安装，版本未写）；给出 RL 专家权重（约 5 GB）和 URMA 蒸馏权重（约 1 GB）；GenBot1K 机器人配置包 | 约 1000 个程序生成的腿足形态；论文称零样本迁到真机 Go2 与 H1（出处：arXiv 摘要，复现代码里无 Go2 部署说明） | 高：顶会、规模化与通用策略范式，真机在 Go2 上有结果 | 把 URMA 的关节描述扩展到"轮子"关节类型，让 Go2-W 成为训练分布外或分布内的一个形态；跨形态策略加在线适应 | 在 GenBot1K 的 URMA 输入（关节描述 + 关节状态）里加入 Go2-W 的 4 个速度控制轮关节，12 腿关节沿用位置目标；只需要新增机器人资产与轮关节动作类型 | 数据量大（README：每机器人 1.3–7 GB，全集约 4 TB，需本地生成）；仓库 README 标 Gendog 任务 0–331，与论文"约 1000"不一致；轮子不在原分布内，零样本大概率不成立；Isaac Lab 版本需对齐服务器 5.1 |
| 2 | **Multi-Loco**：RL 增强扩散的多形态腿足运动（Yang 等，SUSTech/LimX；arXiv 2506.11470） | CoRL 2025。[PMLR v305 yang25a](https://proceedings.mlr.press/v305/yang25a.html) pp.1030–1048；[arXiv 评论](https://arxiv.org/abs/2506.11470)只写 "19 pages" | [clearlab-sustech/multi_loco_isaacgym](https://github.com/clearlab-sustech/multi_loco_isaacgym)，最近 push 2025-05-25，Apache-2.0；**Isaac Gym Preview 3 + Python 3.8**；README 称训练分两阶段：EDM 扩散预训练 + PPO 残差策略；统一 TRON-1 的点足与轮足两种模式。仓库与论文的对应关系只来自仓库名与 README 标题（论文页和项目页未链接代码），需核对 | 项目页称在双足、轮式双足、人形、四足上真机测试；README 只含 TRON-1 | 中高：顶会；扩散先验加 RL 残差，且显式覆盖"轮足/点足切换" | 扩散先验 + 残差 RL 用于 Go2-W 的 16 维动作，轮腿协同；残差输出做有界约束以保护执行器 | Isaac Gym 代码需移植到 Isaac Lab 5.x（Blackwell 不能用 Isaac Gym）；先复现 TRON-1 轮足统一策略，再换 Go2-W 资产 | 仓库小（6 星），无权重；不是 Go2-W 原生；扩散策略 50 Hz 机载推理需单独验证；DSRL 精读时已判断"扩散运动策略本身要先造"，此处因有现成流程而部分缓解 |
| 3 | **Divide, Discover, Deploy**：分解式技能发现（Cathomen、Mittal、Vlastelica、Hutter，ETH/NVIDIA；arXiv 2508.19953） | CoRL 2025（口头报告）。[arXiv 评论](https://arxiv.org/abs/2508.19953)写 "Accepted to CoRL 2025"；[PMLR v305 cathomen25a](https://proceedings.mlr.press/v305/cathomen25a.html)；Oral 来自[项目页](https://leggedrobotics.github.io/d3-skill-discovery/) | [leggedrobotics/d3-skill-discovery](https://github.com/leggedrobotics/d3-skill-discovery)，最近 push 2026-01-09，BSD-3；**Isaac Lab 2.2（Isaac Sim 4.5+）+ rsl_rl v2.2.0**；含 DIAYN、METRA、三个 USD 环境与下游任务；README 要求 16 GB+ 显存（4096 环境 24 GB），带 Docker | ANYmal-D（真机，零样本） | 中高：顶会 Oral；无任务奖励的技能库加对称/风格先验，真机安全性数据明确（作者报告不安全接触下降 85%） | 对 Go2-W 做"轮腿混合技能发现"：因子化为基座速度、朝向、轮腿模式；风格项里加入执行器温升或电流惩罚 | 在 Isaac Lab 中换 Go2-W 资产与 16 维动作；USD 环境与奖励无需大改；rsl_rl 栈与 robot_lab 一致 | Isaac Lab 2.2 → 服务器 Isaac Lab 对应 Sim 5.1，需小版本升级与回归测试；技能发现的下游任务价值要自己论证；ANYmal-D 与 Go2-W 的质量、足端形态差异大，风格/对称先验要重设 |
| 4 | **AME-2**：基于注意力神经地图编码的敏捷通用腿足运动（Zhang、Klemm、Yang、Hutter，ETH；arXiv 2601.08485） | **未核实**。[项目页](https://sites.google.com/leggedrobotics.com/ame-2)写 "IEEE TRO 2026"，README 的 BibTeX 也写 T-RO 2026；arXiv 页只见 "Journal Submission" 页眉，未查到 IEEE Xplore。前作 AME-1 已核实：Science Robotics vol.10 no.105，2025-08-27（[Crossref](https://api.crossref.org/works/10.1126/scirobotics.adv3604)，arXiv 2506.09588） | [leggedrobotics/ame2_minimal](https://github.com/leggedrobotics/ame2_minimal)，最近 push 2026-11-23；**Isaac Lab 2.3.2（Isaac Sim 5.1）**，与服务器环境一致；教师/学生训练、Mid360 激光神经建图在环；README 自称"half-archived"、不再接受功能贡献 | 论文：ANYmal-D、TRON1、G1、H1（项目页）；开源的最小版只含 G1 | 中高（若 T-RO 属实）：感知式地形泛化、神经建图；但最小版只带人形配置 | 在 Go2-W 上做"轮足感知式运动"；注意力地图编码加轮腿切换；或只取其训练 recipe（教师-学生 + 多头 critic + Muon 优化器） | 需 Go2-W 的高程输入：Go2 可选 L1/Mid360 类激光，要先确认实验室配置；Go2-W 资产与观测接口自己接；先在仿真中完成"感知 + 轮足" | 开源版是 G1 的 minimal 重写，不是论文全部实验；T-RO 状态未核；Go2-W 有无可用外部感知未核；工作量重 |
| 5 | **SRU**：空间增强循环记忆的长距离无地图导航（Yang 等，ETH；arXiv 2506.05997） | IJRR，vol.45 no.11，pp.1682–1706，DOI 10.1177/02783649251401926（[Crossref](https://api.crossref.org/works/10.1177/02783649251401926)） | 五个仓库（[项目页](https://michaelfyang.github.io/sru-project-website/)列出）：[sru-navigation-sim](https://github.com/leggedrobotics/sru-navigation-sim)（Isaac Lab 导航环境，MIT，最近 push 2026-10-25）、[sru-navigation-learning](https://github.com/leggedrobotics/sru-navigation-learning)（rsl_rl 扩展，PPO/SPO/MDPO，最近 push 2026-11-17；README 明言不含仿真环境与任务）、[sru-robot-deployment](https://github.com/leggedrobotics/sru-robot-deployment)（**Unitree B2W** 部署栈，ROS 2 Jazzy/Gazebo，最近 push 2026-07-10） | **Unitree B2W（轮足四足）真机**；底层 50 Hz 运动策略加 5 Hz 导航 | 中：IJRR；轮足真机链路完整；但属导航层，运动控制只是被调用的底层策略 | 在导航与运动之间加约束层；用 Go2-W 的底层策略重训导航；或研究轮足底层策略对导航的影响 | B2W 与 Go2-W 同属 Unitree 轮足，ROS 2 部署栈可参考；需另备 Go2-W 的底层速度策略（可用 robot_lab） | 运动控制创新空间小；底层策略来源未在本轮核实；需深度相机与 Jetson 级算力 |
| 6 | **Hybrid Internal Model (HIM)**（Long 等，OpenRobotLab；arXiv 2312.11460） | ICLR 2024，**自述**：[仓库 README](https://github.com/Sage-PhysicalAI/HIMLoco) 写 "accepted by ICLR 2024"；未核到 OpenReview 或论文集页 | [Sage-PhysicalAI/HIMLoco](https://github.com/Sage-PhysicalAI/HIMLoco)（原 OpenRobotLab，已迁移），最近提交 2024-05-14；**Isaac Gym Preview 4，PyTorch 1.10 cu113，Python 3.7**；README：部署指南未发布 | Go1、Aliengo 等（论文，未在本轮核实具体清单） | 中：社区常用底座；FLORES（RA-L 2026，已在池）的轮足实现基于它（来自 `wheel_legged.md`，本轮未再核实） | 轮足版"混合内部模型"：用 Go2-W 轮速与关节响应预测机体速度，做轮足状态估计；或 HIM 加热/约束 | 代码需整体移植到 Isaac Lab（旧栈、Blackwell 不可用）；已有 robot_lab 的 HIM 类实现可参照（未核实） | 年代偏早、仓库已停更两年半；ICLR 状态仅自述；创新空间被后续自适应工作占据较多 |
| 7 | **SoloParkour**：从特权经验做视觉运动的约束 RL（Chane-Sane、Amigo 等，LAAS/Gepetto；arXiv 2409.13678） | CoRL 2024。[arXiv 评论](https://arxiv.org/abs/2409.13678)写 "CoRL 2024" | [Gepetto/SoloParkour](https://github.com/Gepetto/SoloParkour)，最近 push 2025-05-05；基于 **IsaacGymEnvs / Isaac Gym**，Python 3.8；脚本含特权策略、经验生成、视觉策略三阶段；DDPG 类离策略 | Solo-12（小型四足，真机） | 中：约束 RL（CaT 同组延续）与离策略特权经验学习；但平台与任务（视觉跑酷）偏离 | 约束式离策略 RL 用于 Go2-W（能耗、温度约束）；与池中 CaT、SAC 追上 PPO 形成对照 | Isaac Gym → Isaac Lab 移植；换 Go2-W 资产；去掉视觉分支只留约束 + 离策略 | 与池中 CaT 同路线，查重风险高；Solo-12 与 Go2-W 差距大；年代偏早 |
| 8 | **Learning Deployable Locomotion Control via Differentiable Simulation**（Schwarke 等，ETH；arXiv 2404.02887） | CoRL 2025。[PMLR v305 schwarke25a](https://proceedings.mlr.press/v305/schwarke25a.html) pp.3665–3684；[arXiv 评论](https://arxiv.org/abs/2404.02887)写 CoRL 2025 | **未找到官方代码**：ETH `leggedrobotics` 组织仓库列表（按最近 push 排序、含 100 个以内）中无对应仓库 | ANYmal-D 真机零样本 | 高（方法新）：可微接触模型 + 解析梯度训练，样本效率高 | 可微仿真的轮足接触模型；可微仿真加世界模型 | 需自己实现可微接触模型与环境；Go2-W 轮地接触还要另建 | **无代码**，复现要从头写；3–4 个月工期风险高 |
| 9 | **FACET**：阻抗参考跟踪的力自适应控制（Xu 等，清华/上海期智；arXiv 2505.06883） | CoRL 2025。[PMLR v305 xu25c](https://proceedings.mlr.press/v305/xu25c.html) pp.705–720；Oral 来自第三方清单（[CoRL 2025 论文索引](https://github.com/smallfryy/corl-2025-papers)，未核官方日程） | **未找到官方代码**：项目页 `egalahad.github.io/facet/` 返回 404；GitHub 搜索只有镜像/注册类仓库。作者个人账号下有 `active-adaptation`（最近 push 2025-06-20），与 FACET 的关系**未核实** | 仿真 Go2、G1、B1+Z1；真机 Go2（出处：[arXiv 摘要的二手综述，未直接核原文]） | 中高：真机 Go2，顺应外力的柔顺运动；与"力感知/载荷"主题接近 | 轮足的外力顺应：把 CoM 虚拟弹簧阻尼参考扩展到轮速；后续 2610.08637 已用其作基线 | 在 Isaac Lab 里实现参考模型和教师-学生训练，难度中等，但需自写 | 无官方代码；后续工作 2610.08637 已出现，查重要做 |
| 10 | **Motion Priors Reimagined**（Zhang、Li、Miki、Hutter，ETH；arXiv 2505.16084） | CoRL 2025。[PMLR v305 zhang25j](https://proceedings.mlr.press/v305/zhang25j.html) pp.3762–3777 | 第三方 CoRL 索引给出 `leggedrobotics/motionpriors`，GitHub API 返回 404，**未找到可用代码**；[项目页](https://anymalprior.github.io)无代码链接，提到 IsaacGym | ANYmal-D 真机 | 中：平地动物运动先验迁到复杂地形的分层残差 RL | 把运动先验换成轮足先验，高层残差负责轮腿切换 | 需自己重建先验训练与残差层 | 无代码；方法较薄 |

## 2. 未入主表但值得一提（发表状态已核，缺代码或相关性弱）

| 论文 | 发表与出处 | 代码 | 备注 |
|---|---|---|---|
| **SHOES**（Tsuruhara 等；arXiv 2610.16457） | CoRL 2026，[arXiv 评论](https://arxiv.org/abs/2610.16457)写 "Accepted at CoRL 2026" | 未找到 | 冻结仿真策略 + 恒等初始化的小模块在线适应，**真机 Go2**（穿鞋）。与池中 GRAM/TAM/FADA 同类，只作查重参照 |
| **ROGER** 奖励增益自适应（Srisuchinnawong、Manoonpong；arXiv 2510.10759） | RSS 2025 压缩版，[arXiv 评论](https://arxiv.org/abs/2510.10759)；v2 2026-06 | 页面未列代码 | 约束式运动学习，真机 60 kg 四足；非 Go2 |
| **Not Only Rewards But Also Constraints**（Kim 等，KAIST Hwangbo 组；arXiv 2308.12517） | T-RO 2024，[arXiv 评论](https://arxiv.org/abs/2308.12517)写 "Accepted to T-RO 2024" | KAIST `railabatkaist` 公开仓库中未见（只有 `raisimGym_nature` 等） | 约束 RL 经典工作；基于 RaiSim，非 Isaac 系 |
| **DTC: Deep Tracking Control**（Jenelten 等，ETH） | Science Robotics vol.9 no.86，2024-01-17（[Crossref](https://api.crossref.org/works/10.1126/scirobotics.adh5401)） | arXiv 页无代码 | 学习 + 轨迹优化结合的典型；无代码，难复现 |

## 3. 我认为最强的 3 篇

**① Embodiment Scaling Laws（表 #1）。** 顶会、代码和权重齐全、Isaac Lab 栈与服务器一致，真机已在 Go2 上有零样本结果；最关键的是它自然引出"把轮子并入统一形态表示"这个问题，而 Go2-W 的 12 位置 + 4 轮速恰好落在这个缺口上。只有 PMLR 页与 arXiv 评论两个出处，但互相一致。主要代价是数据量大和轮子不在原分布内，需要先做小规模验证，再决定是否投入。

**② Multi-Loco（表 #2）。** 唯一在已核实的候选里**显式覆盖轮足/点足切换**，并且给出"扩散预训练 + PPO 残差"的完整两阶段流程，论文为 CoRL 2025（PMLR 已核）。它与此前被排除的 DSRL 不同：扩散先验在这里有现成流程。风险是代码在 Isaac Gym 上、仓库小、与论文的对应关系只有仓库 README 自述，必须先核对再投入移植。

**③ Divide, Discover, Deploy（表 #3）。** CoRL 2025 Oral，官方代码在 Isaac Lab + rsl_rl 栈，最接近服务器已有环境，复现成本最低；创新方向（轮腿因子化技能、执行器风格项）与 Go2-W 的 4 轮 + 12 腿结构吻合。弱点是下游任务价值需自己论证，且轮足上的技能发现尚无直接先例这件事我**没有做系统查重**。

备选：SRU（表 #5）是唯一在 Unitree 轮足（B2W）上有完整开源栈的已发表工作（IJRR），若选题偏向"轮足 + 感知/导航"可替换 ③。

## 4. 没把握或未核实的地方

- AME-2 的 T-RO 录用只有作者项目页与 README 自述，未见 IEEE 页面；表中标"未核实"。
- HIM 的 ICLR 2024 只有 README 自述。
- Multi-Loco 仓库是否就是论文官方代码：论文页与项目页均未链接，对应关系由仓库 README 标题和作者单位推断。
- Go2 零样本真机（ESL）、FACET 的真机平台，来自 arXiv 摘要或检索摘要，没有读到论文正文；ESL 的 Go2 部署代码仓库内没有。
- FACET 的 Oral 来自第三方 CoRL 索引，未核官方日程。
- 「无官方代码」类结论（FACET、可微仿真、Motion Priors）仅基于项目页与 GitHub 组织/搜索 API，可能漏掉作者个人账号下的仓库。
- 搜索工具返回有限，2026 年 RSS/CoRL/ICRA 的录用名单没有逐篇过；世界模型、学习 + MPC、能耗/热保护方向本轮未找到比池中已有的更强的"已发表 + 有代码"新项，不代表不存在。
- 仓库"最近 push"不等于最近功能提交；依赖版本（Isaac Lab 2.2 对 5.1 等）都需在服务器上实测。
