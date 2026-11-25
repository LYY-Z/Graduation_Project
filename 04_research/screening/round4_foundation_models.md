# 第四轮：基础模型 / VLA / LLM-VLM × 足式与轮足机器人（跳出旧思路）

日期：2026-11-25。
本轮刻意不推荐：执行器辨识与 sim-to-real 对齐、部署期在线适应、热约束、激光雷达几何避障。它们只作对比出现。
记号：【事实】已打开摘要页、论文集页或仓库页核对过；【评价】我的判断；【猜想】未验证的研究设想；【未核实】查不到或没打开。
与已有文件的关系：`vla.md` 第 13–16 条已粗筛过 NaVILA、MobileVLA-R1、LocoVLM、FWBC-VLA，这里只补充新信息，不重复。

## 0. 检索说明与局限

- 来源：arXiv 摘要页、RSS / PMLR(CoRL) / CVF / IJCAI 论文集页、GitHub 仓库首页、项目主页。查询时间为 2026-11-25。
- 查询主题：腿足 VLN/VLA（NaVILA、Uni-NaVid、StreamVLN、DualVLN/InternVLA-N1、VAMOS）；LLM/VLM 设计奖励、课程或域随机化（DrEureka 后续、SDS、CurricuLLM、LAPP、GROVE、Video2Reward、RDA）；VLM 高层 + RL 底层（VLM-PC、LocoVLM、ODYSSEY）；VLM 预测地面物理属性（FSL、Walking on Ice）；VLM 语义代价图（RECAST、CATNAV、Language as Cost）；轮足模态切换；Go2-W 相关工作。
- 工具局限：WebFetch 返回的是小模型对网页的摘要，不是原文。仓库的"最近提交日期"在 GitHub 首页摘要里基本拿不到，下文凡写"未显示"的都属于未核实，不代表仓库不活跃。
- 没做的事：没有逐一打开 OpenReview；没有按会议论文集系统枚举；没有跑任何代码；Science Robotics 的一篇疑似相关论文（DOI 10.1126/scirobotics.aee1549，搜索摘要题为 "Bridging vision-language reasoning and learned control for legged navigation in the wild"）返回 403，标题、作者、内容都未核实，下文不使用。
- Go2-W 扩展计算：经销商页面称 Go2-W 基础款配 Orin Nano（40 TOPS），Plus 及以上配 Orin NX（100 TOPS）【未核实，非 Unitree 官方页】。下文默认 7B 级 VLM 需要外接 GPU（笔记本或服务器经 Wi-Fi），机载只跑 RL 底层策略。

## 1. 候选总览（12 篇 + 1 篇平台参照）

| # | 工作 | 发表状态（出处） | 代码 | 平台 | 初评 |
|---|---|---|---|---|---|
| 1 | NaVILA | RSS 2025（论文集 p018） | 有，VLA + 低层分仓 | Go2 / T1 / G1 | B+（基线） |
| 2 | Uni-NaVid | RSS 2025（论文集 p013） | 有，MIT | 实机未写明 | B |
| 3 | StreamVLN | ICRA 2026（arXiv comments） | 有，含 Go2 实机部署 | Go2 | A |
| 4 | DualVLN / InternVLA-N1（Ground Slow, Move Fast） | InternNav README 标 ICLR 2026，arXiv 页无 comments【未在 OpenReview 核实】 | 有，InternNav（MIT） | Turtlebot4 / Go2 / G1（据搜索摘要） | A |
| 5 | VAMOS | 预印本（项目页写 Under Review） | 仅推理与 ROS 部署，1 次提交 | Spot（腿）+ UW Hound（轮） | A-（思想），C（复现） |
| 6 | DrEureka（参照，2024） | RSS 2024 | 有，MIT，IsaacGym | Go1 | 参照 |
| 7 | SDS | CoRL 2025（PMLR 305） | 有，基于 DrEureka 代码 | Go1（+ANYmal 仿真） | A- |
| 8 | CurricuLLM | ICRA 2025（DOI 10.1109/ICRA55743.2025.11128783） | 有，SB3 + gymnasium | Berkeley Humanoid | B |
| 9 | LAPP | arXiv 2504.15472；作者主页 PDF 文件名含 "2025_RSS"【录用未核实】 | arXiv 页无代码链接 | 四足（实机未确认） | B- |
| 10 | GROVE | CVPR 2025 Oral | 部分开源（关键模块待发布） | 仿真人形，ANYmal 仿真 | C（对本课题） |
| 11 | Friction-Aware Safety Locomotion（FSL） | Humanoids 2025（arXiv comments） | 无 | 自制轮式倒立摆 | B（思想） |
| 12 | Walking on Ice（WoI） | IJCAI 2026（论文集 PDF 已打开） | 未见 | 人形 | B（思想） |
| 13 | VLM-PC / LocoVLM（合并） | VLM-PC 预印本；LocoVLM 为 ICRA 2025 SafeVLMs Workshop | 均无 | Go1 | C |
| — | Go2-W 长距离导航（参照） | arXiv 2606.21387，v2 2026-11；Tsukuba Challenge 2025 实测 | 未见 | **Go2-W** | 底层基线参照 |

另有 VLM 语义代价图一类（RECAST 预印本 2026-09、CATNAV 预印本 2026-03、Language as Cost IROS 2025 有代码），离"避障"太近，只在方向 1 的对比里提到。

## 2. 候选详情

### 1. NaVILA（RSS 2025）——作为"高层 VLA + RL 低层"的标准基线
- 已在 `vla.md` #13 详述，这里只补充。
- 【事实】仓库 AnjieCheng/NaVILA：Apache-2.0，737 星，17 次提交；有训练脚本 `sft_8frames.sh`、R2R 评测、HF 权重 `a8cheng/navila-llama3-8b-8f`；Isaac Sim 评测迁到 `yang-zj1026/NaVILA-Bench`；无实机部署文档。低层 `yang-zj1026/legged-loco`：MIT，460 星，仅 2 次提交，Isaac Lab 1.1.0 + Isaac Sim 4.1.0，支持 Go2 与 H1，无检查点，无部署代码。
- 【事实】高层输出语言化中层动作，映射成固定速度指令，再由 RL 低层执行（`vla.md` 已记）。
- 【事实】VAMOS 论文在自己的实验里把 NaViLA 作为基线，报告成功率 10%（VAMOS 90%）。这是竞争对手报告的数字，场景偏户外复杂地形。
- Go2-W 创新点【猜想】：NaVILA 的接口是"离散速度"，完全不知道机器人有轮。Go2-W 的轮/腿两种模态在速度上限、能耗、可通过性上差别很大，这正是接口层的空白（见方向 1）。
- 难点：训练 VLA 本体不可复现（作者用 16 节点 A100 预训练，`vla.md` 已记）；只能用权重做推理。8B 推理需外接 GPU。

### 2. Uni-NaVid（RSS 2025）
- 链接：[arXiv 2412.06224](https://arxiv.org/abs/2412.06224)；[RSS 论文集 p013](https://www.roboticsproceedings.org/rss21/p013.html)；[jzhzhang/Uni-NaVid](https://github.com/jzhzhang/Uni-NaVid)。
- 【事实】视频输入 VLA，统一 VLN、ObjectNav、具身问答、人跟随四类任务；360 万训练样本；在线 token 合并后约 5Hz 推理（README 写单卡 A100）。代码 MIT，370 星，13 次提交；基于 LLaMA-VID / NaVid，EVA-CLIP + Vicuna-7B；有两阶段训练脚本和离线评测，VLN-CE 评测在另外的仓库。
- 【未核实】实机机型（项目页与 README 都没写）；实机部署代码未提供；实机成功率数字项目页未给出。
- Go2-W 创新点【猜想】：多任务统一，可做"人跟随 + 轮式高速"场景。
- 难点：无部署代码；7B 推理需外接 GPU；训练从头需多卡（未给数字）。
- 初评 B：被 StreamVLN / DualVLN 在工程完整度上超过。

### 3. StreamVLN（ICRA 2026）
- 链接：[arXiv 2507.05240](https://arxiv.org/abs/2507.05240)（v2 2026-07-09，comments："Accepted to ICRA 2026"）；仓库 [InternRobotics/StreamVLN](https://github.com/InternRobotics/StreamVLN)。
- 【事实】基于 LLaVA-Video / LLaVA-NeXT；快：滑动窗口 KV cache 的流式对话上下文；慢：3D 感知的 token 剪枝记忆。仓库有一阶段训练、DAgger 数据采集、二阶段联合训练（SLURM 多节点示例）、多卡评测、两套 HF 权重（基准复现用 / 实机部署用）、预采集轨迹数据；`realworld/` 目录含 **Unitree Go2 部署代码与指南（2025-08-28 加入）**。环境 Python 3.9、PyTorch 2.1.2、CUDA 12.4。648 星，16 次提交，最近 news 2025-09-28。许可 CC BY-NC-SA 4.0。
- 【事实，来自搜索摘要对论文正文的转述，未逐字核对】实机：Go2 + 上仰的 RealSense D455，图像传到远端 RTX 4090 工作站；推理约 0.27s 出 4 个动作，通信室内约 0.2s、室外约 1.0s。
- 【事实，搜索摘要】后续工作把它当 Go2 基线，报告的问题包括"走走停停"（LiveVLN）、对光照和措辞敏感、牺牲任务完成换避障；试验次数都很小。
- Go2-W 创新点【猜想】：①把它的离散动作接到 Go2-W 的轮腿低层上，研究"同一高层、不同运动模态"；②它的"走走停停"在轮式下会更明显（轮式速度高、单步位移大），可作为接口问题来做。
- 复现/实机难点：PyTorch 2.1.2 + CUDA 12.4 不支持 sm_120，需要在 Blackwell 上升级到 CUDA 12.8+ 和对应 PyTorch / flash-attn 重新编译【评价：可做但要花 1–2 周】；只做推理时，一张 Blackwell 卡足够跑 7B（显存档次未核实）；训练多节点，不必复现训练，只用权重。
- 初评 A：近两年正式发表 + Go2 实机代码 + 权重，是方向 1 最好的起点。

### 4. DualVLN / InternVLA-N1（"Ground Slow, Move Fast"）
- 链接：[arXiv 2512.08186](https://arxiv.org/abs/2512.08186)（v1 2025-12-09，arXiv 页无 comments）；[InternRobotics/InternNav](https://github.com/InternRobotics/InternNav)；HF `InternRobotics/InternVLA-N1-DualVLN`。
- 【事实】System 2 是 VLM 全局规划器，输出像素目标与隐目标；System 1 是轻量 Diffusion Transformer 策略。据搜索摘要转述论文正文：System 2 为 7B、约 2Hz，System 1 约 30Hz；实机覆盖 Turtlebot4（轮式）、Go2、G1；模型卡称只用仿真数据（InternData-N1）训练。
- 【事实】InternNav：代码 MIT，数据 CC BY-NC-SA 4.0；1.2k 星，84 次提交；最近 news 为 v0.3.0（2026-01）；2025-09 发布 InternVLA-N1 实机部署代码，2025-12 发布训练代码；附 Go2 的 3D 打印安装件；README 把 DualVLN 标为 ICLR 2026、StreamVLN 和 NavDP 标为 ICRA 2026。
- 【未核实】ICLR 2026 录用（只见 README 自述）；System 1 训练算力。
- Go2-W 创新点【猜想】：双系统天然有"慢语义 / 快运动"的分工，Go2-W 的"运动模态"可以放在 System 1 与 RL 低层之间，或者让 System 2 输出模态偏好。
- 难点：框架大、依赖多；同样有 sm_120 环境迁移问题；System 1 输出的是轨迹，接 Go2-W 还需要一个跟踪层。
- 初评 A：工程最完整、维护最活跃；论文状态需补核。

### 5. VAMOS（预印本）——"同一规划器，按本体能力调制"
- 链接：[arXiv 2510.20818](https://arxiv.org/abs/2510.20818)；[项目页](https://vamos-vla.github.io)；[vamos-vla/vamos](https://github.com/vamos-vla/vamos)。
- 【事实】高层 VLM（PaliGemma 2 3B，用 29.8 小时多源导航数据训练）在像素空间输出候选路径；每种本体一个轻量 MLP 可通过性模型（输入高程、位置、朝向，仿真中训练）对路径打分、否决物理上不可行的路径；可以用自然语言加偏好（"prefer ramps over stairs"）。平台 Spot（腿）+ UW Hound（轮）。项目页报告：总体成功率 VAMOS 90%、ViPlanner 67%、模块化栈 53%、NoMaD 27%、NaViLA 10%；楼梯 vs 坡道测试中轮式机器人不加能力调制时 40% 失败于楼梯，加了以后成功率 90%（以上来自作者自己的页面）。
- 【事实】仓库只有推理与 ROS Noetic 部署，1 次提交，62 星，许可未显示；未见规划器训练、可通过性模型训练和仿真环境。
- Go2-W 创新点【猜想】：VAMOS 用"两台不同机器人"体现本体差异；Go2-W **一台机器人自带两种能力剖面**（轮滚 / 腿走），可以把"本体能力模型"变成"同一机器人的两个模态可通过性模型"，决定路径和模态。检索中没有找到这样做的工作（见方向 1 查重）。
- 难点：训练部分不开源，只能借思想；可通过性 MLP 需要自己在 Isaac Lab 里用 Go2-W 低层策略滚出数据训练（这是本科可控的工作量）。
- 初评：思想 A-，作为可复现基础 C。

### 6. DrEureka（RSS 2024，参照，不在 2025–2026 范围内）
- 链接：[arXiv 2406.01967](https://arxiv.org/abs/2406.01967)；[eureka-research/DrEureka](https://github.com/eureka-research/DrEureka)。
- 【事实】LLM 同时写奖励和域随机化参数；Go1 实机；IsaacGym Preview 4 + PyTorch 1.10 cu113；含前进行走、走球两个环境和基于 Walk These Ways 的 Go1 部署；MIT，947 星，10 次提交。作者在局限里写到可以把真实世界执行失败作为 LLM 调参的反馈。
- 【评价】它的"DR 部分"属于本轮要避开的 sim-to-real 对齐；这里只作为 LLM 设计奖励的代码基础（SDS 就是在它上面改的）。IsaacGym Preview 4 不支持 sm_120 的可能性很大【未核实】，实际应移植到 Isaac Lab。
- 【未找到】2025–2026 年 DrEureka 的直接后续论文（两次检索均未命中）。

### 7. SDS — See it, Do it, Sorted（CoRL 2025）
- 链接：[arXiv 2410.11571](https://arxiv.org/abs/2410.11571)；[PMLR 305:1879-1897](https://proceedings.mlr.press/v305/stamatopoulou25a.html)；[项目页](https://rpl-cs-ucl.github.io/SDSweb)；[RPL-CS-UCL/SDS](https://github.com/RPL-CS-UCL/SDS)。
- 【事实】从**单段演示视频**生成奖励：GPT-4o 读取时空网格编码的关键帧，按 SUS 思维链把行为分解为子目标，写出可执行奖励；PPO 在 IsaacGym 中训练；把训练视频和适应度指标回传给 GPT-4o 迭代改奖励。Go1 实机学到 trot / bound / pace / hop 四种步态，摘要称步态匹配 100%、实机零失败；称可推广到 ANYmal。
- 【事实】仓库基于 DrEureka 代码；Python 3.8、PyTorch 2.4.0 cu121、easy_ViTPose（ViTPose++）；OpenAI API；Go1 部署沿用 Walk These Ways + Docker；51 次提交，106 星，许可未显示。
- 平台差异：Go1 → Go2-W 需要换 URDF、换动作空间（加 4 轮速度）、换部署链（Unitree SDK2）。
- Go2-W 创新点【猜想】：①**轮腿混合技能**没有人设计过奖励模板（例如"边滚边抬腿过坎""单侧轮滑转弯""跪姿滚行"），SDS 式"看视频写奖励"正好可用；②视频来源可以是人遥控 Go2-W 录的视频或其他轮足机器人的视频；③把 GPT-4o 换成本地开源 VLM（服务器上跑），可比较闭源 / 开源在奖励质量上的差别。
- 难点：训练算力低（单卡 IsaacGym 级别，迭代若干轮 × 每轮多个候选，作者未给总时长）；API 费用与可复现性（闭源模型版本漂移）；指标"步态匹配"对轮足需要重新定义。
- 初评 A-：近两年正式发表、有代码、有四足实机，是方向 2 最合适的基础。

### 8. CurricuLLM（ICRA 2025）
- 链接：[arXiv 2409.18382](https://arxiv.org/abs/2409.18382)；[labicon/CurricuLLM](https://github.com/labicon/CurricuLLM)。
- 【事实】LLM 把目标任务拆成子任务序列（自然语言），再翻成奖励代码与目标分布，逐级训练；仿真任务 Fetch-Push/Slide、AntMaze、Berkeley Humanoid；人形策略部署到实机。仓库用 gymnasium-robotics + stable-baselines3，OpenAI API，196 次提交，29 星；未见实机部署代码，许可未显示。
- Go2-W 创新点【猜想】：用于"轮—腿过渡"这类难直接训练的技能的课程。
- 难点：代码不基于 Isaac 系列，迁移到 Go2-W 要重写环境；仓库关注度低。
- 初评 B：思路可借鉴，代码基础弱。

### 9. LAPP（arXiv 2504.15472）
- 【事实】LLM 对 RL 过程中的轨迹对打偏好标签，在线训练 Transformer 偏好预测器作为奖励，与环境奖励一起用 PPO 优化；评测四足运动与灵巧操作，称实现了四足后空翻。arXiv 页无 comments、无代码链接。
- 【未核实】作者主页 PDF 文件名为 `2025_RSS_LAPP.pdf`，但我没在 RSS 2025 论文集中查到；实机平台。
- Go2-W 创新点【猜想】：用于"风格"类难以写成公式的目标（平顺、像动物、不晃相机）。
- 初评 B-：状态和代码都不清楚。

### 10. GROVE（CVPR 2025 Oral）
- 【事实】LLM 生成物理约束、VLM 评估语义与自然度、多轮迭代；Pose2CLIP 把姿态映射到语义空间以免渲染；称迁移到 ANYmal 仿真。代码 [jiemingcui/GROVE-pytorch](https://github.com/jiemingcui/GROVE-pytorch) 的 TODO 显示 Pose2CLIP 与 RL 训练代码未发布。
- 初评 C（对本课题）：仿真角色动画为主，无实机，代码不全；只作为"VLM 作评委"的相关工作引用。

### 11. Friction-Aware Safety Locomotion for Wheeled-legged Robots（Humanoids 2025）
- 链接：[arXiv 2409.09845](https://arxiv.org/abs/2409.09845)（v1 2024-09，标题 FSL-LVLM；v2 2025-08-04 改题；comments：Accepted to Humanoids 2025）。
- 【事实】VLM + 检索增强生成（RAG）在接触前估计前方地面摩擦系数，作为显式输入给 RL 策略，策略据此提前调整速度；平台为自制轮式倒立摆（WIP）；湿滑地面上只用本体感知的基线失败，本方法完成轨迹跟踪。v1 与 v2 方法有变化（v1 叫 Friction-From-Vision）。无代码。
- Go2-W 创新点【猜想】：从两轮倒立摆扩展到四轮腿 Go2-W，并且让先验不只控制速度，还控制"滚 / 走"模态。
- 初评 B：思想直接相关，复现要自己搭；会被认为接近"适应"（见方向 3 的风险）。

### 12. Walking on Ice（IJCAI 2026）
- 链接：[IJCAI-26 论文 0694](https://www.ijcai.org/proceedings/2026/0694.pdf)（已下载 PDF 读首页）。作者来自哈工大。
- 【事实】VLM 摩擦预测器在摩擦变化前给出预判（主动），加上关节历史编码器的摩擦估计器（被动）；人形；摘要称相对 DWL 成功率提高 8.5%，打滑率降低 5.15%；极端场景成功率 98.3%。代码【未见】，实机细节未读到。
- 初评 B：说明"VLM 预测地面物理属性 → 条件化 RL"在 2025–2026 已经进入正式会议，四足轮足上的版本我没检到。

### 13. VLM-PC 与 LocoVLM（合并说明）
- VLM-PC（[arXiv 2407.02666](https://arxiv.org/abs/2407.02666)，Stanford/Berkeley，Go1）：VLM 做上下文适应 + 多步技能规划与重规划，选择爬、钻、绕等技能。只有 v1（2024-07），项目页有 ICRA 风格 PDF，录用未核实；无代码。
- LocoVLM（[arXiv 2602.10399](https://arxiv.org/abs/2602.10399)）：项目页显示实机为 Go1，出处为 ICRA 2025 SafeVLMs Workshop；VLM 推理 <100ms、50Hz 控制；无代码。
- 初评 C：都是"VLM 选技能"，四足上已有人做，Go2-W 上要有新意需靠轮腿模态。

### 参照：Go2-W 长距离实地导航（arXiv 2606.21387）
- 【事实】日本团队（Matsuzawa 等），v1 2026-06-19，v2 2026-11-13；把本体感知 RL 运动控制器扩展到 16 自由度 Go2-W，发现轮式行驶使髋关节过载发热，加入周期性抬脚分散负载；Tsukuba Challenge 2025 实地约 2.8km（人行道、公园、台阶）不因过热停机。未见代码和发表会议。
- 【评价】它是 Go2-W 底层 RL 可行性的直接证据，也说明"热"已有人做（与旧方向重叠，本轮不展开）。对方向 1、3 来说，它是"不懂语义的强底层"基线的样子。

## 3. 提炼出的研究方向

三个方向都是"大模型只做慢的语义判断，RL/经典控制做快的运动执行"，区别在于大模型介入的位置：导航接口（方向 1）、训练期的奖励设计（方向 2）、运动策略的条件输入（方向 3）。

### 方向 1（首推）：面向轮足双模态的"能力感知"语言导航接口

**要解决的问题**
现有腿足 VLN（NaVILA、StreamVLN、DualVLN）的高层只输出"前进 / 转向 / 停"或轨迹，默认机器人只有一种运动方式。Go2-W 同时具备轮式（平地快、省电，过不了台阶）和腿式（过台阶、碎石，慢、耗电）。高层不知道这一点，就会出现两类损失：该滚的地方走（慢、费电），该走的地方滚（卡住、摔）。VAMOS 用"每种机器人一个可通过性模型"处理跨本体差异，但它的两种能力剖面分属两台机器人。

**为什么有价值**
- 【评价】问题来自 Go2-W 这个平台本身，不是硬套；轮足机器人（Go2-W、B2-W、ANYmal on wheels）是工业热点，语言导航 + 轮足模态的组合在检索中是空白（见查重）。
- 实机演示直观：同一句指令，"走廊滚过去，楼梯走上去"。
- 对传统控制质疑的回应：底层仍是 RL/可验证控制，大模型只做语义与偏好；可以把"激光高程阈值规则切换"作为传统基线放进对比，用数据回答"为什么要大模型"——几何规则看不出湿滑瓷砖、草地、软垫、"请安静 / 别压草坪"等语义约束。

**推荐基础论文**
StreamVLN（ICRA 2026，有 Go2 部署代码与权重）作为高层；VAMOS（预印本）作为"能力调制"的思想来源；NaVILA（RSS 2025）作为"VLA → 速度指令 → RL 低层"接口范式与基线；Go2-W 长距离导航（arXiv 2606.21387）作为底层可行性参照。备选高层：DualVLN（InternNav）。

**本科可做的创新点草案**
1. 底层：在 Isaac Lab 训练 Go2-W 的"速度 + 模态"条件策略（模态 ∈ {滚, 走}，可选第三种"混合"），输入本体感知，输出 12 腿关节目标 + 4 轮速度。这一步是工作量主体，但是已有 Go2-W RL 先例。
2. 模态可通过性模型（借 VAMOS）：用底层策略在仿真里对随机地形 patch 滚出成功率 / 能耗 / 时间，训练两个小 MLP：`f_roll(高程 patch, 速度)`、`f_walk(...)`，输出可通过概率和代价。
3. 接口：冻结 StreamVLN 的高层输出（动作 / 子目标）→ 用两个可通过性模型 + 可选的 VLM 语义偏好（一次低频 VLM 询问，如"前面是草坪 / 地毯 / 湿地"）选择模态与速度上限 → 底层执行。
4. 对比实验（同一高层、同一指令集，只换接口）：
   - B1 固定腿式（NaVILA 式接口）；B2 固定轮式；B3 本体感知自动切换（底层自己学切换，或 FLORES 式绊倒触发）；B4 激光高程阈值规则切换（传统基线）；Ours-geo（只用可通过性模型）；Ours-full（+ VLM 语义偏好）。
   - 指标：任务成功率、完成时间、能耗（电池电流积分）、模态切换次数、卡住 / 摔倒次数、人工干预次数。
   - 场景：仿真（Isaac Lab 或 VLN-CE 上叠加地形）+ 实机 3–4 类路线（走廊 + 台阶、草地 + 路面、斜坡、带语言偏好"别从草坪走"）。每条 10 次以上。
5. 消融：去掉 VLM 语义；去掉能耗项；高层频率变化（1Hz / 0.5Hz / 0.2Hz）对轮式高速下的影响（与 StreamVLN 的"走走停停"问题衔接）。

**查重初判**
- 【事实】检索"wheel-legged + VLM 模态切换"未找到同类：最接近的是 2026 Frontiers 的双足轮腿 MoE 切换（无语言、无 VLM）、FLORES（本体触发）、ATRos（能效）、FSL（两轮倒立摆、只调速度）。"VLN + 轮足"两次检索都只返回 NaVILA。
- 【风险】VAMOS 如果正式发表并扩展到"单机多模态"，会撞题；需要在开题时再查一次 2026 下半年 arXiv。

**风险**
- 高层环境：StreamVLN / InternNav 依赖较旧的 PyTorch + CUDA，迁到 sm_120 需要重编 flash-attn 等，可能耗 1–2 周。
- 网络延迟：作者报告室外通信约 1.0s（搜索摘要转述），轮式高速时更危险，必须加速度上限和本地安全层。
- 底层训练：Go2-W 轮腿混合策略的奖励调试会占大量时间；建议先做"两个独立策略 + 切换"，再考虑统一策略。
- 评价指标的说服力：实机次数少时统计意义弱，需要预先定好场景和次数。

**与之前方向比较**
- 更好：问题是 Go2-W 独有的；有正式发表 + 有 Go2 实机代码的基础；演示效果强；论文可以投 ICRA/IROS 类会议的导航或轮足方向。
- 更差：系统集成链条长（VLN 高层 + 通信 + 可通过性模型 + 底层），比单一的辨识或适应工作风险更分散；依赖外接 GPU 和 Wi-Fi。

### 方向 2：大模型闭环设计 Go2-W 轮腿混合技能的奖励

**要解决的问题**
轮腿混合动作（边滚边跨坎、侧向轮滑、跪姿滚行、单侧抬腿转弯）没有成熟的奖励模板。人工写奖励靠反复试错；Eureka/SDS 类方法能自动写奖励，但都在纯腿式机器人上验证，评委（LLM/VLM）只看"适应度数字"或人体姿态视频。

**为什么有价值**
- 【评价】把"奖励设计"这一 RL 最依赖经验的环节自动化，对新平台（尤其是轮足）价值直接；结果是标准 RL 策略，部署不依赖大模型，实机可以完全机载。
- 对传统控制质疑：对比对象可以是人工奖励 RL，也可以是 MPC / 规则步态的同一技能；大模型只在训练期出现，答辩时容易讲清"大模型没进控制回路"。

**推荐基础论文**
SDS（CoRL 2025，有代码，Go1 实机）为主；DrEureka（RSS 2024，代码基础）；CurricuLLM（ICRA 2025）提供"课程"思路；RDA（RLC 2026，[arXiv 2606.01672](https://arxiv.org/abs/2606.01672)，VLM 看轨迹视频总结失败模式再改奖励，仅操作 / 人形仿真）提供"视觉评委"思路；MoVLR（[arXiv 2512.23077](https://arxiv.org/abs/2512.23077)，预印本，肌骨模型）同类。

**本科可做的创新点草案**
1. 把 SDS 管线从 IsaacGym/Go1 移植到 Isaac Lab/Go2-W（动作空间加轮）。
2. 新增"轮腿结构化提示"：把轮接触、轮速、腿相位作为显式观测和奖励原语提供给 LLM；新增"VLM 视频评委"——用渲染视频 + 关键量曲线（轮滑移率、足端抬高）让 VLM 指出失败模式。
3. 对比：人工奖励（Go2-W 参照论文式）、Eureka（仅数字反馈）、SDS 原版（视频 + 数字）、Ours（轮腿原语 + VLM 失败分析）。每种方法给相同的 GPU 小时预算。
4. 指标：3–4 个技能的任务成功率、达到阈值所需迭代数 / GPU 小时、人工干预次数、实机成功率；闭源（GPT 系）与本地开源 VLM 各跑一遍，报告方差（每种方法至少 3 个随机种子）。
5. 实机：只部署每个技能的最终策略，验证可迁移性；不做在线调参（避免滑回 sim-to-real 方向）。

**查重初判**
- 【事实】检索未找到"LLM/VLM 设计轮足（wheel-legged）奖励"的工作；DrEureka 后续未检到；SDS、Video2Reward（ECAI 2024）、LAPP、GROVE 都是纯腿式或仿真角色。
- 【评价】"LLM 写奖励"整体已较拥挤，创新只能落在"轮腿混合 + 视觉失败分析"上，审稿人可能认为增量小。

**风险**
- 复现性：闭源 API 版本漂移，结果难以复现；要固定模型版本并保存全部生成的奖励代码。
- API 费用和速率限制【未估算】；改用开源 VLM 时，奖励代码质量可能明显下降。
- 实机：LLM 写出的奖励可能利用仿真漏洞，迁移到实机失败——这时容易被迫回到 sim-to-real，需要提前在奖励原语里加约束。

**与之前方向比较**
- 更好：基础论文有代码且是 CoRL 2025；实机部署最简单（大模型不上机）；GPU 需求小。
- 更差：方法新意最弱；"轮腿技能"本身的应用价值需要讲故事；与"大模型 + 机器人"的热点结合度不如方向 1 直观。

### 方向 3：视觉语言先验条件化的轮腿运动（地面属性 → 速度 / 模态）

**要解决的问题**
轮子对地面摩擦和软硬比脚更敏感（打滑、陷入）。本体感知只能在接触之后知道地面变了；VLM 能从图像提前判断"湿瓷砖、冰、草、沙、地毯"。FSL（Humanoids 2025）在两轮倒立摆上做了"VLM 估摩擦 → RL 调速"，Walking on Ice（IJCAI 2026）在人形上做了"VLM 预测 + 本体估计"。四轮腿上还没检到。

**为什么有价值**
- 【评价】有两篇 2025–2026 正式发表的近邻，说明问题被认可；四轮腿上加入"模态"维度（湿滑处改腿走，还是降速滚）是自然扩展。
- 实验便宜：一台 Go2-W、几块地垫 / 塑料膜 / 草地 / 碎石就能做。

**推荐基础论文**
FSL（Humanoids 2025）；Walking on Ice（IJCAI 2026）；VLM-PC（预印本）作为技能选择参照；底层参照 Go2-W 长距离导航论文。

**本科可做的创新点草案**
1. 底层：Go2-W 策略在仿真中以"摩擦等级 / 地面类别"作为显式条件输入训练（训练时用仿真真值）。
2. 先验：前置相机图像 → VLM（服务器上开源 VLM，或机载小模型 + 缓存，参考 CATNAV 的语义缓存）→ 地面类别 / 摩擦等级；可选 RAG 查表（FSL 做法）。
3. 对比：盲策略（只本体，DR 训练）；本体估计器；VLM 先验；VLM 先验 + 本体估计融合。
4. 指标：轮滑移率（轮速 vs 机体速度）、速度跟踪误差、摔倒 / 停滞次数、过渡段（地面变化前后 1s）的峰值滑移；VLM 判错时的退化幅度（故意给错先验的消融）。

**查重初判**
- 【事实】四足轮腿 + VLM 摩擦先验未检到；但两轮版本（FSL）和人形版本（WoI）都已发表，新意只剩"平台 + 模态维度"。

**风险**
- 【评价】与之前反复出现的"部署期适应"方向非常接近（本体估计器部分就是适应），用户可能觉得又回到了老路；需要把重点放在"语义先验"而非"适应"上。
- VLM 对摩擦的判断误差大，实验可能显示"本体估计器已经够用"，导致结论不利。

**与之前方向比较**
- 更好：实验最便宜，3–4 个月最稳；有两篇正式发表近邻做参照。
- 更差：与旧方向重叠最大；论文价值偏中等，后续创新空间较小。

## 4. 总体判断（评价）

1. 足式机器人上的"大模型"工作，在 2025–2026 已经稳定成"分层"范式：大模型低频出语义 / 子目标 / 奖励，RL 或扩散策略高频执行（NaVILA、StreamVLN、DualVLN、VAMOS、LocoVLM、SDS）。端到端 VLA 直接出关节指令的腿足工作仍少，且不可复现。本科毕设应站在分层范式里找接口问题，不要训练大模型本体。
2. Go2-W 最有辨识度的切入点是"轮 / 腿双模态"。三条方向里只有方向 1 把这一点和大模型的长处（语义、语言偏好）结合起来，且有正式发表并附 Go2 部署代码的基础（StreamVLN），所以首推方向 1。
3. 方向 2 是保底：GPU 和实机风险都最低，但新意最弱。方向 3 最稳，但与旧循环重叠最大，只建议作为方向 1 的一个子模块（VLM 语义偏好里包含地面属性）。
4. 共同的硬风险：①现有 VLN 代码栈（PyTorch 2.1 / CUDA 12.4 / IsaacGym Preview 4）在 Blackwell sm_120 上需要升级重编；②7B 级模型无法放在 Orin NX 上，实机必须外接 GPU，通信延迟要进实验设计；③Go2-W 底层 lowcmd / 轮速接口仍未核实（继承自前几轮的待办）。

## 5. 未核实与待办

- DualVLN 的 ICLR 2026 录用（只见 InternNav README）；LAPP 是否 RSS 2025；VLM-PC 是否 ICRA 录用；Uni-NaVid 实机机型。
- StreamVLN 实机数字（0.27s 推理 / 0.2–1.0s 通信）来自搜索摘要对论文正文的转述，需回到 PDF 核对。
- 所有仓库的最近提交日期（GitHub 首页摘要拿不到），开题前应 `git log` 核对。
- Science Robotics DOI 10.1126/scirobotics.aee1549 的内容（403，未读）。
- Go2-W 扩展计算的官方规格（Orin Nano / NX、8GB / 16GB）。
- 没有查到 2025–2026 年 DrEureka 的直接后续，以及"LLM 设计轮足奖励"的工作；结论限于本次检索词。

## 6. 来源

- NaVILA：https://roboticsproceedings.org/rss21/p018.html ；https://github.com/AnjieCheng/NaVILA ；https://github.com/yang-zj1026/legged-loco
- Uni-NaVid：https://www.roboticsproceedings.org/rss21/p013.html ；https://github.com/jzhzhang/Uni-NaVid ；https://pku-epic.github.io/Uni-NaVid
- StreamVLN：https://arxiv.org/abs/2507.05240 ；https://github.com/InternRobotics/StreamVLN
- DualVLN / InternNav：https://arxiv.org/abs/2512.08186 ；https://github.com/InternRobotics/InternNav ；https://huggingface.co/InternRobotics/InternVLA-N1-DualVLN
- VAMOS：https://arxiv.org/abs/2510.20818 ；https://vamos-vla.github.io ；https://github.com/vamos-vla/vamos
- DrEureka：https://arxiv.org/abs/2406.01967 ；https://github.com/eureka-research/DrEureka
- SDS：https://proceedings.mlr.press/v305/stamatopoulou25a.html ；https://rpl-cs-ucl.github.io/SDSweb ；https://github.com/RPL-CS-UCL/SDS
- CurricuLLM：https://arxiv.org/abs/2409.18382 ；https://github.com/labicon/CurricuLLM
- LAPP：https://arxiv.org/abs/2504.15472 ；https://pingcheng-jian.github.io/data/2025_RSS_LAPP.pdf
- GROVE：https://openaccess.thecvf.com/content/CVPR2025/html/Cui_GROVE_A_Generalized_Reward_for_Learning_Open-Vocabulary_Physical_Skill_CVPR_2025_paper.html ；https://github.com/jiemingcui/GROVE-pytorch
- Video2Reward：https://arxiv.org/abs/2412.05515 ；RDA：https://arxiv.org/abs/2606.01672 ；MoVLR：https://arxiv.org/abs/2512.23077
- FSL：https://arxiv.org/abs/2409.09845 ；Walking on Ice：https://www.ijcai.org/proceedings/2026/0694.pdf
- VLM-PC：https://arxiv.org/abs/2407.02666 ；LocoVLM：https://arxiv.org/abs/2602.10399 ；https://locovlm.github.io
- 代价图类：RECAST https://arxiv.org/abs/2609.32595 ；CATNAV https://arxiv.org/abs/2603.22800 ；Language as Cost https://arxiv.org/abs/2508.03138
- 其他：ODYSSEY https://arxiv.org/abs/2508.08240 ；OrionNav https://arxiv.org/abs/2410.06239 ；Go2-W 导航 https://arxiv.org/abs/2606.21387 ；轮腿切换 https://www.frontiersin.org/journals/robotics-and-ai/articles/10.3389/frobt.2026.1788395/full ；FLORES https://arxiv.org/abs/2507.22345 ；ATRos https://arxiv.org/abs/2510.09980
