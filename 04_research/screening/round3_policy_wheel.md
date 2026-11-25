# 第三轮检索：无模型 RL 策略层面（轮足 / 感知运动 / 先验与生成式 / 训练算法）

检索日期：2026-11-24。范围：用于四足/轮足/人形运动的无模型 RL 策略层面新进展。方法：WebSearch（约 20 轮）+ arXiv abs/html 页 + GitHub REST API（`gh` 不可用，用 curl 读提交、目录树、README、pyproject）。未安装、未运行任何代码，未改其他文件。
标记：**【事实】** 来自论文页或仓库原文；**【评价】** 本次筛选者判断；**【设想】** 未验证。评分 1–5：V 论文价值、I 创新空间、R 复现难度（5 最难）、D 部署难度（5 最难）。
查重只做了 2–3 轮网页检索，结论写作"未检索到"，不等于"不存在"。

## 0. 先排除已有候选

已 grep `screening/*.md`、`candidates/*.md`。以下已在库中，本轮不再深挖：MoE-CTS、CaT、LocoFormer、具身尺度律、Multi-Loco、D3、FLORES、NaVILA、AME-2、SRU、HIM、SoloParkour、FADA、MUJICA、ATRos、DSRL、AWARE、CTBC、热感知（2603.01631、2605.27046）、SAC 追上 PPO（2605.24975）、FPO、GenPO、Diffusion-MPC、LocoVLM、MobileVLA-R1。
对已有候选的新信息各一句：
- Diff-CAST（2605.08804）在 `candidates/dsrl.md` 中出现过，但此前未单独评估；本轮在下表第 5 行给出（Go2、Isaac Gym、N-P3O，较此前印象更贴近 Go2-W）。
- 本轮未发现 MUJICA、ATRos、AME-2 的新版本或新代码。

## 1. 主表（10 篇）

| # | 论文 / 出处（核实程度） | V | I | R | D | 创新设想（Go2-W，【设想】） | 最接近工作 | 3–4 个月 |
|---|---|---|---|---|---|---|---|---|
| 1 | **FlashSAC**（Kim 等；arXiv 2604.04539；arXiv comments 写 **RSS'26**；搜索结果中出现 roboticsproceedings.org/rss22/p099，但 PDF 无法读出文本，论文集页**部分核实**） | 4 | 3 | 2 | 1 | 把 FlashSAC 作为 Go2-W（12 腿位置 + 4 轮速）的训练器，并研究约束（CaT / P3O 类）在 off-policy 下是否仍成立；样本效率高后可探索真机小量数据微调轮地打滑 | SAC 追上 PPO（ETH，2605.24975，已在库）；FastSAC/Holosoma（仅人形）；HTS-SAC（MDPI，轮腿四足 SAC，仅见搜索摘要未打开） | **可完成**（算法替换型；风险在奖励敏感性与约束兼容） |
| 2 | **FastSAC / FastTD3 人形 15 分钟配方**（Seo 等；arXiv 2512.01996；无录用信息；代码 amazon-far/holosoma） | 3 | 3 | 2 | 1 | 与 #1 同线，可作对照基线：PPO vs FastSAC vs FlashSAC 在 Go2-W 混合运动上的系统对比 | #1；ETH SAC | **可完成**，但与 #1 合并为一个课题更合理 |
| 3 | **Hiking in the Wild**（Zhu 等；arXiv 2601.07718；项目页标 **CoRL 2026**，arXiv 无 comments，**论文集页未核实**）及同组 Deep Whole-body Parkour（2601.07701，无代码链接） | 4 | 4 | 3 | 3 | 深度/高度图感知 + AMP 目标的单阶段跑酷框架迁到 Go2-W：把"边缘检测 + 脚体积点"的落脚安全改成"轮接触面/轮缘安全"，做轮式越台阶与跳落 | 轮足爬楼：Chamorro（2402.06143，盲）、CTBC（轮双足，盲）；未检索到"轮足 + 感知 + 跑酷"的直接工作；SoloParkour（已在库） | **勉强**（栈完全匹配，但需自建 Go2-W 资产、参考动作、感知输入） |
| 4 | **APT-RL**（Kang 等，KAIST HOUND；*Science Robotics* 2026-07-15，DOI 10.1126/scirobotics.adz7397，arXiv 页写明；arXiv 2607.13579） | 5 | 3 | 5 | 4 | 把"轨迹优化数据 → Transformer VAE 潜在动作 → 步态专属力矩解码器 → RL 选步态（2 Hz）"迁到轮足：预训练"滚行/步行"两个解码器，RL 只选模式 | MUJICA（技能指示变量）、AWARE（Gumbel 专家选择）、ATRos（无预设步态）；未检索到"轮足 + 动作预训练 Transformer" | **不可行（完整复现）**；只能借思想做小规模版本 |
| 5 | **Diff-CAST**（Chen 等；arXiv 2605.08804，v2 2026-05-12；**无录用信息**） | 3 | 4 | 3 | 2 | 用扩散先验给"滚行 + 迈步"混合步态打风格奖励，并把轮电机力矩/速度/髋温上限写成约束（N-P3O）；用状态转移而非动作建模，使参考数据可由 MPC 或已有策略生成 | Multi-AMP（ETH 2022，轮足，多 AMP，需手工切换）；Diff-CAST 本身；ATRos；MUJICA | **可完成**（无代码，需自写扩散先验；Isaac Gym 需移植到 Isaac Lab） |
| 6 | **PGTT**（Ntagkas 等；arXiv 2510.18348；arXiv 页写明 **IROS 2026**；v2 2026-07-22） | 3 | 4 | 3 | 2 | 相位引导的落脚结构 + 高度图，迁到 Go2-W：引入"滚行/抬腿"模式相位，用高度图统计量决定抬腿高度，做有雷达的轮足爬楼 | CTBC、Chamorro（盲爬楼）；未检索到"轮足 + 雷达高度图 + 相位引导" | **可完成**（有 Go2 + 雷达实机链路与代码；JAX 栈兼容性待测） |
| 7 | **DHAL**（Liu 等，UMich；arXiv 2503.01842；无录用信息） | 3 | 4 | 4 | 2 | 用离散时间混合自动机 + 多 critic + beta 策略，让 Go2-W 自动识别"滚行/步行/混合"模式，替代手工模式或技能指示变量 | MUJICA、AWARE、ATRos；DHAL 原文做滑板 | **勉强**（Isaac Gym 需移植；模式识别的评估指标要自设） |
| 8 | **Omni-Perception**（Wang 等；**CoRL 2025**，PMLR v305 wang25b；arXiv 2505.19214） | 4 | 4 | 4 | 3 | 原始雷达点云端到端避障迁到 Go2-W 高速轮式行驶（转向与轮速耦合，滚行时的动态障碍反射） | AWARE（M20，RA-L 2026，感知方式未核）；REASAN（2512.09537，单雷达，legged，代码 ASIG-X/REASAN，**未打开**）；未检索到"轮足 + 原始点云 + 端到端" | **勉强**（训练代码未放出，只有 LidarSensor） |
| 9 | **GPO**（Liao 等；arXiv 2601.20668；无录用信息） | 2 | 3 | 3 | 2 | 渐进放开动作空间：先只放开腿，再放开轮速（课程式），检验是否缓解轮腿耦合探索难 | 无直接工作；与课程学习类似 | **可完成**但贡献偏弱 |
| 10 | **轮足四足预测式节能步态选择 + 残差 RL**（Yang 等；**IROS 2025**，pp.18919-18925，arXiv 页写明；arXiv 2601.10723） | 3 | 3 | 3 | 2 | 把 1 秒功率预测网络换成端到端能耗约束；与 Go2-W 的"长距离过热"问题结合 | ATRos、Matsuzawa Go2-W（2606.21387，已在库） | **可完成**，但与已有 ATRos/热感知路线重叠 |

## 2. 逐篇证据与评语

### 2.1 FlashSAC（行 1）
- 【事实】arXiv 2604.04539：SAC 基础上减少梯度步数、增大模型和数据吞吐，限制权重/特征/梯度范数；60+ 任务、10 个仿真器；摘要称人形 sim-to-real 训练时间从小时降到分钟。
- 【事实】仓库 Holiday-Robot/FlashSAC：MIT；最近提交 `87edc90`（2026-04-09）；有 `play_isaaclab.py`、`scripts/run_isaaclab.sh`；README 列出 Blackwell 配置：Python 3.11、**torch 2.9.1**、isaacsim 5.1.0、isaaclab 2.3.0，并引 Isaac Lab issue 4371（"required for Blackwell GPUs"）。Isaac Lab 任务清单为 Anymal-C/D、G1、H1、Franka 等，**没有 Go2-W**。
- 【评价】与服务器的 sm_120 要求一致，但服务器现有 torch 2.7 环境不够，需新建 uv 环境（独立 conda/uv，不改他人环境）。接入 robot_lab 的 Go2-W 需写环境包装，不是改一行配置。
- 【评价】价值：算法通用、RSS 级别（部分核实）。创新空间受限于"换算法"本身是否算贡献：需要给出轮足特有的结论，例如轮速通道的动作缩放对 off-policy 的影响、约束处理。ETH 论文 2605.24975 指出 FastSAC/FastTD3 依赖任务特定奖励工程（来自检索摘要，未读全文）。
- 【未核实】FlashSAC 论文中的人形真机实验细节、实机评估是否包含四足；Go2 机载算力对策略网络无影响（推理端与 PPO 相同）。

### 2.2 FastSAC / Holosoma（行 2）
- 【事实】arXiv 2512.01996：FastSAC、FastTD3，单张 RTX 4090 约 15 分钟训练人形运动；G1、T1。仓库 amazon-far/holosoma：Apache-2.0；最近提交 `c9882fc`（2026-11-24）；README 写"IsaacGym (no longer supported)"，支持 IsaacSim；机器人只有 G1、T1；算法 PPO 与 FastSAC；含部署推理管线。
- 【评价】与 #1 重叠，作为对照基线和工程参考（部署管线、ONNX 导出）。

### 2.3 Hiking in the Wild（行 3）
- 【事实】arXiv 2601.07718（v2 2026-10-13）：深度 + 本体直接映射关节动作，无外部定位/建图；Terrain Edge Detection + Foot Volume Points 的落脚安全；Flat Patch Sampling 生成可行导航目标；G1 实机，速度至 2.5 m/s。项目页标 CoRL 2026，并称代码开源。
- 【事实】仓库 project-instinct/InstinctLab：Isaac Sim 5.1.0、Isaac Lab 2.3.2、Python 3.11（README 徽章）；最近提交 `de6b92f`（2026-09-09）；许可 CC BY-NC 4.0（NOASSERTION）；跑酷任务 ID `Instinct-Parkour-Target-Amp-G1-v0`，使用 AMASS 参考动作；`--exportonnx` 导出，配套 instinct_onboard 部署。
- 【评价】这是本轮与服务器栈（Isaac Sim 5.1 / Py3.11）最吻合的"感知 + AMP + 跑酷"开源底座。难点：它是人形，Go2-W 需要自建机器人配置、AMP 参考动作（轮足没有现成 mocap）或改成无 AMP 的奖励；Go2-W 实机通过雷达而非深度相机取地形，需改感知输入（Go2-W 是否另装深度相机：未核）。
- 【未核实】Deep Whole-body Parkour（2601.07701）无录用信息、无代码链接；Hiking 的 CoRL 2026 录用未在论文集页核实。

### 2.4 APT-RL（行 4）
- 【事实】arXiv 2607.13579（作者版，Science Robotics 2026-07-15）：HOUND 四足；Isaac Gym；PPO；180,000 条轨迹优化数据（约 15.5 小时，生成约 8 分钟）；TVAE 学共享潜空间，步态专属力矩解码器（trot、bound）；RL 输出潜动作 + 辅助 PD 目标；步态选择 2 Hz；教师-学生感知蒸馏，深度 D435 + 2D 激光；室外实机峰值 6 m/s（三级台阶跳落）。
- 【事实】作者自述局限：主要是矢状面运动，无快速转向和侧移；仅两种步态；撞击加速度常超 10 g 时雷达读数不可靠；预训练数据是 2D、平地。无代码链接。
- 【评价】发表级别最高，但是复现不可行：自研机器人、Isaac Gym、力矩接口、无代码。Go2-W 若走力矩层，还要核对 lowcmd 开放程度（`STATUS.CN.md` 仍列为未解决）。只建议借鉴"预训练动作先验 + RL 只选模式"的结构。

### 2.5 Diff-CAST（行 5）
- 【事实】arXiv 2605.08804：机器人 **Unitree Go2**；仿真 Isaac Gym；PPO；约束处理用 **N-P3O**（非 CaT），约束为关节位置/速度/力矩，使用自适应非对称惩罚；扩散先验建模状态转移（不含动作），条件于速度指令；约 10 分钟无标签 mocap；基线为普通 AMP；实机 3 m/s 冲刺 15 s：Diff-CAST 力矩超限 0 次，去掉约束 RL 为 57 次；表 II 跟踪误差 1.08 对 AMP 的 26.85。
- 【事实】论文未说明 mocap 来源，层数/网络大小/扩散超参未给，没有限制节，没有代码链接。
- 【评价】机器人和约束方法与 Go2-W 的 P3O 路线（MUJICA 用 P3O）接近；缺点：未见录用信息、无代码、表 I 部分数值来源不清。创新设想的卖点是"状态转移型先验可用 MPC/已有策略生成参考，不依赖轮足 mocap"。

### 2.6 PGTT（行 6）
- 【事实】arXiv 页：IROS 2026 录用；Go2 实机，LiDAR→高度图（Point-LIO 里程计 + 高程地图），ANYmal-C 仿真；MuJoCo MJX 训练。仓库 NtagkasAlex/phase_guided_terrain_traversal：最近提交 `9bd1338`（2026-07-17）；含训练、评估、`deploy_real.py`（Unitree SDK）；requirements：jax 0.8.0、mujoco 3.3.7、brax 0.13.0，README 说明 CUDA 13 用 `jax[cuda12]==0.8.0`；Python 3.12；无许可证文件内容未核。
- 【评价】有 Go2 + 雷达高度图实机链路和代码，是本轮"最低风险的感知运动底座"。局限：MJX/JAX 栈而非 Isaac；要迁到轮足需自建 MJX 的 Go2-W 模型（SimDist 同样的 JAX 兼容问题需一并核）。方法价值中等（IROS 级，无大规模对比）。【未核实】Point-LIO/高程图是否能在 Go2 机载算力上运行，或需要外接笔记本。

### 2.7 DHAL（行 7）
- 【事实】arXiv 2503.01842：离散时间混合自动机学习，beta 策略分布 + 多 critic；四足滑板实机。仓库 UMich-CURLY/DHAL：legged_gym + rsl_rl，Isaac Gym Preview 4，Python 3.8，最近提交 `62a08b2`（2025-05-12）；GitHub 上有第三方 Go2 滑板分支 DavidSyTao/DHAL_go2（内容与原仓库一致，未核实 Go2 改动）。
- 【评价】思路切中"轮足模式切换"，但是 2025 年、无录用信息；Isaac Gym 不能用，需移植 Isaac Lab。

### 2.8 Omni-Perception（行 8）
- 【事实】CoRL 2025（PMLR v305）；Go2 与 G1（Mid-360）；PPO，4096 环境，Isaac Gym 主训练；PD-RiskNet 近场/远场两路 GRU 处理原始点云；输出 12 关节位置目标；真机 30 次试验：空中障碍 70%、移动行人 90%，Unitree 原生系统均为 0%。局限：草地误判、远场平均会抹去细小障碍。
- 【事实】仓库 aCodeDog/OmniPerception：MIT；最近提交 `a1059ae`（2025-11-05）；README 状态表：LidarSensor "Released[Half]"、训练代码 "In Progress"、部署 "Planned"；声称支持 IsaacGym、Genesis、MuJoCo、Isaac Sim（Warp 后端）。
- 【评价】用原始雷达点云和 Go2-W 已有雷达最吻合；缺训练和部署代码，等于要自己复现 PD-RiskNet。

### 2.9 GPO（行 9）、行 10
- GPO：【事实】时变动作变换先限制再逐步放开动作空间，保持 PPO 更新规则；四足与六足真机零样本；无代码、无录用信息。【评价】主要针对力矩控制，Go2-W 为位置目标，适用性弱。
- 能耗步态选择：【事实】改装 Go1 轮足；1 秒功率预测网络选名义步态，残差 RL 调整；声称最多降低 35% 能耗（摘要）；无代码，项目页 sites.google.com/view/switching-wpg。

## 3. 看过但未入表

| 论文 | 原因 |
|---|---|
| 技能发现 2602.09767（A1，正交 MoE + 多判别器，+18.3% 状态覆盖） | 无录用/代码，仅 A1 |
| Conditional AMP 2509.21810 | 无录用/代码/平台信息 |
| Acrobotics 2509.02727（LNCS 16045 pp.124-138） | 无代码，平台未说明 |
| Frontiers 2026 轮双足 MoE（Diablo） | 期刊，仅仿真（Isaac Gym），台阶 12 cm |
| LocoMamba 2508.11849（*Advanced Engineering Informatics* 2026） | 仅仿真，无代码，平台未说明 |
| Where-to-Learn 2603.27317 | PPO 探索增强，平台与录用未核 |
| 2603.07928 人形雷达爬楼梯 | 人形，无代码 |
| 2611.16337 塌陷地形撤退 | 平台未说明，under review |
| WheeledLab（CoRL 2025 PMLR v305） | RC 小车，非轮足 |

## 4. 评价与未核事项

1. 本方向"高价值 + 有代码 + 栈兼容"集中在两处：算法层（FlashSAC，Blackwell 配置明确）和感知运动层（InstinctLab，Isaac Sim 5.1.0 / Lab 2.3.2 / Py3.11），都不是轮足原生。
2. 轮足原生的新工作多数无代码或仅预印本；轮足 + 感知（雷达/深度）+ 端到端的组合在本轮检索中未发现直接工作，但只检索了有限几轮。
3. 未核实：FlashSAC 的 RSS 论文集页内容；Hiking 的 CoRL 2026 录用；PGTT 的 Go2 机载算力；Go2-W 力矩接口；REASAN、AWARE 的细节；HTS-SAC 的具体内容。
4. 未覆盖：世界模型、VLA 的 locomotion 低层（由其他路负责）。
