# 证据卡：Multi-Loco（RL 增强扩散的多形态腿足运动）

日期：2026-11-24。性质：论文正文（arXiv HTML v1）+ 仓库只读审查（GitHub API 与 raw 文件）+ 文献检索。**没有运行任何代码，没有下载权重，没有在服务器上验证。**
标注约定：**作者事实**＝论文或仓库自述；**评价**＝本次审查者判断；**猜想**＝未经验证的设想；"未核实"＝没查到。
证据强度说明：正文由 arXiv HTML 抓取后转述，HTML 没有页码，下文用节号、表号、图号定位；PMLR 版页码范围为 pp.1030–1048，**具体表/图所在页未核实**。表 2 的数字经两次独立抓取一致；表 3/4/5、§3.2.2 的百分比、§3.2.3、附录 A/B 的细节只抓取一次，标"单次转述"，引用前应对 PDF 复核。

## 1. 基本信息与发表状态

| 项 | 内容 |
|---|---|
| 论文 | Yang, Fu, Cao, Guo, Wensing, Zhang, Chen，*Multi-Loco: Unifying Multi-Embodiment Legged Locomotion via Reinforcement Learning Augmented Diffusion*，arXiv 2506.11470（标题是 "Reinforcement Learning Augmented Diffusion"，不是 "RL-Augmented"） |
| 版本 | arXiv 仅 v1，2025-06-13，评论栏 "19 pages"（arXiv 摘要页） |
| 发表 | **CoRL 2025，PMLR vol.305，pp.1030–1048**，会议日期 2025-09-27 至 30（[PMLR yang25a](https://proceedings.mlr.press/v305/yang25a.html)，页面更新 2025-10-07；OpenReview forum id `ypDETG94BS`）。录用级别（口头/海报）未核实 |
| 作者与机构 | 项目页：Shunpeng Yang、Zhen Fu（共同一作）、Zhefeng Cao、Junde Guo：SUSTech；Patrick Wensing：Notre Dame；Wei Zhang：SUSTech + LimX Dynamics；Hua Chen：浙大-UIUC 联合学院 + LimX Dynamics（[multi-loco.github.io](https://multi-loco.github.io)） |
| 项目页 | 有，但**没有代码链接，没有实机视频描述，实验节为空**；只有一个图注（草地、斜坡、楼梯、碎石） |
| 摘要数字 | 相对标准 PPO（高斯策略）平均回报提升 10.35%，轮式双足最高 13.57%（arXiv/PMLR 摘要） |

## 2. 论证链（价值部分）

### 2.1 问题与动机（作者原文，§1）
不同形态腿足机器人的观测、动作维度和动力学不同，通常每个机器人单独训练策略。作者认为运动比操作更难做跨形态抽象，因为它强依赖机器人动力学和地面接触。

### 2.2 方法（§2、附录 A、B）
1. **维度对齐（§2.1）**：观测和动作零填充到各机器人中的最大维度，用二值掩码 b 标记有效动作维。例：12 维四足填充到 20 维。附录 A.2：观测填充到 68 维、动作填充到 20 维；归一化用 5%/95% 分位数映射到 [-1, 1]（单次转述）。
2. **扩散预训练（§2.2、附录 A）**：EDM 扩散模型 + DiT 主干，离线训练，掩码去噪得分匹配（式 2，只在有效维上算损失）。推理用 5 步 Euler 采样（附录 A.3、算法 1）。表 3 超参：观测窗口 10、预测窗口 4、DiT 深度 3、d_model 256、8 头、学习率 3e-4、EMA 0.999（单次转述）。
3. **残差 RL（§2.3、附录 B）**：最终动作 a = a_prior + Δa（式 3）。扩散先验冻结，只在线训练**所有机器人共享的残差 actor**；K=4 种机器人**各有独立 critic**（吃特权状态），多 critic PPO。残差惩罚 r_d = α‖Δa‖₁，表 6 残差系数 0.2。训练环境为 Isaac Gym，建立在 humanoid_gym 和 legged_gym 上。
4. **形态如何表示**：论文声称"不依赖显式形态输入"（§2 / 表 1 "Independent of Joint Information"）。**评价**：实质是"零填充到固定槽位 + 每个机器人的掩码"，附录 A.2 自己写了 morphology-specific masks，critic 也按机器人分开。所谓 morphology-agnostic 是指不需要关节描述符/图结构（对比 URMA、GenLoco），而不是不需要知道是哪个机器人。作者没有讨论这一张力。
5. **轮足/点足如何统一**：表 4：点足双足观测 26 维、动作 6 维；轮式双足观测 28 维、动作 8 维（含轮状态 7 维），轮式机器人不使用步态相位输入（附录 B.1，单次转述）。**两者是两种独立的机器人，各自进同一个填充空间**，论文没有"模式变量"，也没有同一机器人在轮/足两种模式间切换的实验。仓库 README 把 TRON-1 的点足（PF）与轮足（WF）两种构型称为"unified policy"，也是按构型分开的两套槽位数据。

### 2.3 数据（§3.2，附录 A.4、A.5）
- 训练数据来自"用基线 RL 训练出的各机器人策略所生成的 rollout"（§3.2 原话大意）。即**专家就是各机器人自己的 PPO 基线**。
- 表 3："Maximum Samples per Robot: 2048000"；附录 A.5 基线混合比例为每个机器人 25%；A.4 做了 1%、10%、25%、50%、100% 的双足数据量扫描（图 7）：低于 25% 时行为不稳、地形通过差。
- 论文内部不一致：表 3 写 500 epoch、batch 8192，算法 1 写 400K epoch、batch 512，未说明以哪个为准（单次转述）。
- 算力：单张 3090，总训练 3–12 小时，视机器人与数据量（附录）。并行环境数未给。

### 2.4 关键实验与数字

| 结果 | 数字 | 出处 |
|---|---|---|
| CR-DP+RA 相对 RL 基线平均回报 | +10.35%（双足 12.49%、轮式双足 13.57%、四足 4.38%、人形 10.97%） | 图 3(a)，§3.2.2 正文 |
| 跨机器人扩散 CR-DP 相对单机器人扩散 SR-DP | 平均 +17.96%（双足 17.81、轮式 7.52、四足 20.47、人形 26.02） | 图 3(a)，§3.2.2 |
| 达到基线最大平均回报的比例 | CR-DP 87.78%，CR-DP+RA 113.57% | §3.2.2（单次转述） |
| 轮式双足越障（图 4） | CR-DP 对 SR-DP 总体 +2.67%（离散障碍 6.10%、粗糙斜坡 3.87%）；CR-DP+RA 对基线总体 +3.46%（离散 15.13%、斜坡 11.57%） | §3.2.1，图 4（单次转述） |
| 消融表（MEL / LVT / AVT，均值±标准差） | 点足 基线 18.71±0.37 / 1.39±0.25 / 0.94±0.17；CR-DP+RA 18.13±0.46 / 1.42±0.29 / 0.97±0.20。轮式 基线 18.29±0.37 / 2.48±0.58 / 1.28±0.30；CR-DP+RA 18.86±0.33 / 2.72±0.53 / 1.36±0.28。人形 基线 18.88±0.43 / 1.57±0.27 / 1.23±0.20；CR-DP+RA 19.11±0.44 / 1.58±0.28 / 1.35±0.23。四足 基线 19.79±0.17 / 5.45±0.37 / 4.34±0.30；CR-DP+RA 19.60±0.19 / 5.42±0.50 / 4.32±0.41 | 表 2（两次抓取一致） |
| Go2 零样本（未见机器人） | a1 组：CR-DP+RA AR 387.57±6.15，CR-DP 325.24±8.63；go2 组：CR-DP+RA 295.96±5.81，CR-DP 256.05±5.72 | 附录 A.6，表 5、图 9（单次转述） |
| 采样步数 | 3/5/10/15 步折中，>20 步收益递减，选 5 步；无表格 | 附录 A.3，图 6 |
| 数据构成 | 减少点足或四足数据影响可忽略；减少轮式数据损害轮式性能；减少人形数据也降低轮式性能（作者解读为跨机器人协同） | 附录 A.5，图 8 |

### 2.5 实机
- 四个平台：点足双足、轮式双足、全尺寸人形、四足（§3.1），**正文不给具体型号**（项目页同样未命名）。
- 部署：Intel i9-13900HX，50 Hz，EtherCAT（§3.2.3）。图 1、3(b)、3(c) 只有定性展示（人形零样本 sim2real、点足双足下楼梯、草地/斜坡/楼梯/碎石）。
- **没有任何实机定量指标**（成功率、速度跟踪误差、能耗均无）。
- 附录 A.6 的 Go2 实验：正文称"部署"，但图 9 的证据看起来是仿真结果，**是否上了真机未核实**。

### 2.6 作者承认的局限（§5）
需要观测-动作配对数据，不能用无动作标注的动捕；为全新形态直接合成策略"仍是开放问题"；未来工作是无动作训练与零/少样本适配。

## 3. 评价：方法实质、论证检查

1. **方法实质（评价）**：多教师策略蒸馏（把 4 个 PPO 专家蒸馏进一个填充空间中的 EDM-DiT）+ 在其上叠加一个冻结先验的有界残差 PPO。组件都不新：EDM/DiT 来自 CleanDiffuser 生态，"冻结先验 + 残差 RL"是常见套路，新意在于把它们在跨形态腿足上组合，并把"表 1 的四个勾"（形态无关、不依赖关节信息、跨任务、生成式）占满。
2. **教师与学生的比较是循环的（评价）**：扩散先验的训练数据来自 RL 基线本身，而最终评测又拿同一个 RL 基线作对照。CR-DP+RA 的 +10.35% 是"蒸馏 + 再用 RL 微调多训练一阶段"相对"单阶段 PPO"的差，不能排除多出来的训练步数、残差惩罚改变奖励尺度（附录 A.6 作者自己承认 a1/go2 的回报差异来自期望机身高度奖励项）等混杂。
3. **文字与表 2 不一致**：§3.2.2 称 CR-DP+RA 在四个机器人、所有指标上都有一致优势；表 2 里点足的 MEL（18.13 vs 18.71）和四足的 MEL/LVT/AVT 反而略低于基线，且多数差值落在标准差内。真正明显的只有轮式双足（LVT 2.48→2.72，约 +10%，标准差 0.5 左右）。论文没有显著性检验。
4. **图 3 图注写 "SR-DP+RA"，正文写 "CR-DP+RA"**，命名不一致。
5. **价值判断**：CoRL 2025，问题有意义（跨形态运动的统一策略），Table 1 的定位清晰，且是少数把轮式机器人放进跨形态扩散的工作。但实验证据偏薄：实机无定量数字、教师即基线、增益小且部分指标为负。作为"基础论文"，它的价值在**框架与设定**，不在结果的说服力。
6. **控制层级**：策略输出为各关节动作槽位（腿位置目标 + 轮速度目标，具体缩放见仓库任务文件，**未读**），与 Go2-W 的 12 位置 + 4 轮速度同一层级。**评价**：接口层面兼容，没有力矩层依赖。

## 4. 引用与后续影响

- OpenAlex 查询（2026-11-24）：**14 篇施引文献**（Semantic Scholar 当次被限流返回 429，Google Scholar 未查）。题目与出处：
  Scalable and General Whole-Body Control for Cross-Humanoid Locomotion（ICML 2026）；Embodiment-Aware Generalist Specialist Distillation for Unified Humanoid Whole-Body Control（ICRA 2026）；H-Zero（ICRA 2026）；Toward a Multi-Embodied Grasping Agent（RA-L 2026）；Robust Fall Recovery for Armless Bipedal-Wheeled Robots via Force-Guided Learning（RA-L 2026，**未读，是否涉扩散未核实**）；Cross-Hand Latent Representation for VLA；Any2Any；MorFiC（零样本四足迁移，价值校准）；Gaussian Evolutionary Specialists 协同设计；DynaWM；Learning Perceptive Platform Adaptive Locomotion Controllers for Quadrupedal Robots；Diffusion models in robotics: a comprehensive review（Frontiers 2026）；Gait-parameterized RL across morphologies（Intelligent Service Robotics 2026）；RL-driven Diffusion Models（TPAMI 2026，综述）。
- **评价**：施引集中在人形跨形态与综述，**没有一篇是"扩散先验 + 轮足/Go2-W"的直接后续**；14 篇的体量说明有一定关注度但未形成独立方向。施引列表是被引计数而非"实质借鉴"，各篇引用方式未读。
- 同类扩散 + RL 微调的并行工作：DMLoco（arXiv 2507.05674，扩散多任务预训练 + 在线 PPO 微调，四足，DDIM + TensorRT 机载 50 Hz，页面无录用信息、无代码）。

## 5. 复现条件

### 5.1 仓库是否官方（评价：高度可信为官方，但未被论文链接）

| 证据 | 内容 |
|---|---|
| 所有者 | GitHub 组织 `clearlab-sustech`（CLEAR LAB，主页 wzhanglab.site，即第六作者 Wei Zhang 的 SUSTech 实验室） |
| 贡献者 | `MoreInfoy`（154 次提交，资料名 YANG Shunpeng，bio "PhD Student, HKUST"，与论文一作同名）、`isaac94128`（22 次，无资料）、`zhenfu128`（5 次，资料名 Zhen Fu，所在 SUSTech，与论文共同一作同名） |
| 内容对应 | `rl_alg/.../maskededm.py`、`unified_edm_policy.py`、`ppo_unified_edm.py`（掩码 EDM 与 EDM+残差 PPO）；四类机器人任务（biped / biped_wheel / humanoid / quadruped）；扩散数据混合脚本 `mixed_data_process*.py`；与论文四种形态一致 |
| 缺口 | 论文页、arXiv 页、项目页都**不链接**该仓库；仓库 README 无作者、无论文、无 BibTeX |
| 时间线 | 创建 2024-12-23，最后推送 **2025-05-25**（早于 arXiv 2025-06-13）；181 个提交；6 星；Apache-2.0；仓库体积约 378 MB（含 CleanDiffuser 整库与机器人网格） |

**评价**：作者身份（两名论文作者的 GitHub 账号）和内容对应都支持官方；但它是论文投稿前的内部快照，README 只讲 TRON-1，"官方发布"状态未被作者确认。**未核实**：代码与论文表 3/6 超参的一致性、humanoid 和 quadruped 的具体型号。

### 5.2 仓库里有什么、没有什么
- **有**：四个专家基线权重 `scripts/direct/baseline/{biped,biped_wheel,humanoid,quadruped}.pt`（6.7 / 7.0 / 10.7 / 8.7 MB，来自 GitHub 树信息）；EDM 配置与 `stats.pt`；TRON-1 部署脚本（LimX SDK）和 ONNX 示例；PPO、SAC、CTS 等训练代码。（本次粗筛 value_supplement.md 写"无权重"，**应更正为：有专家权重，EDM 权重只有外链**。）
- **没有**：训练用扩散数据集（README 要求自己用 `play_{MODE}.py record_data=True num_envs=2048` 采集）；EDM 检查点本体——README 指向一个飞书文档链接下载，**该链接是否可访问、是否需登录、文件内容是否匹配，未核实**；`scripts/edm/edm_baseline/` 目录里只见 `edm_conf.yaml`、`stats.pt`、tfevents。
- 部署依赖 LimX 的 `limxsdk` 与 `pointfoot-mujoco-sim`，对 Go2-W 无用。
- README 环境名前后不一致（`unified_policy` vs `tron_unified_policy`），说明文档未精修。

### 5.3 Isaac Gym 依赖范围与移植工作量
- Isaac Gym Preview 3 + Python 3.8（README），PyTorch 版本未写。
- **依赖集中**：我统计了 `source/`、`rl_alg/rl_alg`、`scripts/{unified,edm,direct}`（不含整库 vendored 的 CleanDiffuser）共约 1.36 万行 Python，其中 import `isaacgym` 的文件约 4.6–4.9 千行：核心是 `source/mdp/core/sim/isaacsim.py`（1416 行，**文件名叫 isaacsim 但 import 的是 isaacgym**，29 处 gymapi/gymtorch 调用）；四个 `env/*.py`（约 180 行/个）、四个 `task/*.py`（约 400–490 行/个，每个仅 2 处 gym 调用，主体是 torch 张量运算）；`utils/{math,terrain,utils}.py`；`scripts/unified/multiprocess.py`（319 行）。
- **不依赖 Isaac Gym 的部分**（评价：这才是论文贡献所在）：`rl_alg/`（PPO、多 critic、EDM 策略、储存、归一化）、`cleandiffuser`、`scripts/edm/` 的训练脚本、数据混合脚本。
- **评价（工作量估计，未实测）**：
  - 不要整体移植 `source/mdp`。对 Go2-W 的路线应是：沿用服务器上已有的 Isaac Lab + robot_lab 的 Go2 / Go2-W 任务当环境，把 `rl_alg` 的 EDM 与残差 PPO 通过一层环境适配器接入；重写部分 = 观测/动作的填充与掩码、数据录制、多机器人并行调度（`multiprocess.py` 的思路）。粗估 2–3 周含调试。
  - 若坚持复现原 TRON-1 四机器人环境：要把 1.4 千行仿真层 + 四个任务（地形、域随机化、电机模型 `MotorModel`、奖励）移到 Isaac Lab，粗估 4–6 周，且 TRON-1/人形/四足资产的 USD 转换需要自己做；**对 3–4 个月工期不划算**。
  - Python 3.8 + 旧 PyTorch 与 sm_120 不兼容：`rl_alg` 和 `cleandiffuser` 要升到 Py3.11 + PyTorch ≥2.7 cu128，纯 PyTorch 代码预计小改，但 CleanDiffuser 的 vendored 依赖（kitchen、block_pushing 等环境）要剥离。（猜想，未试）

### 5.4 最小可复现实验建议（先不运行，等用户确认）
目标：**不复现 TRON-1，复现"流水线本身"在 Go2 与 Go2-W 两个机器人上的缩小版**。
1. 在 robot_lab（Isaac Lab）里训练两个 PPO 专家：Go2（12 维）与 Go2-W（16 维）。这一步 robot_lab 已有，几小时到一天量级（未实测）。
2. 各自录制约 2×10⁶ 条（观测, 动作）对（对齐论文表 3 的每机器人 2,048,000 上限，数据量需在小规模下验证）。
3. 按论文 §2.1 做零填充 + 掩码，训练一个 EDM-DiT（深度 3、d_model 256），对比 SR-DP（各自单训）与 CR-DP（联合）。
4. 冻结先验，训练共享残差 PPO（残差系数 0.2），做 PPO / CR-DP / CR-DP+RA 三方对照，3 个种子，指标沿用 MEL / LVT / AVT。
5. 检查点：50 Hz 推理延迟（5 步 Euler，机载算力未核）；Go2-W 腿/轮切片是否会互相干扰。
通过标准（建议）：CR-DP+RA 在 Go2-W 上不低于 PPO 基线且不弱于 SR-DP；若连这点都无法复现，说明论文增益主要来自混杂因素，应转向其他底座。
**评价**：这一最小实验同时是后面创新方向的基线，不是浪费。

### 5.5 服务器兼容性小结
- 好：训练代价低（论文自述 3090 上 3–12 小时）；双 5000 Blackwell 够用；Isaac Lab 5.1 环境已有。
- 差：官方环境是 Isaac Gym（不可用）；扩散推理延迟与机载算力未核实。

## 6. 创新空间

### 6.1 三个方向（均需 Go2-W 实机可验证）

**方向 A：腿式先验迁移到轮足——"槽位扩展"（推荐）**
- 问题：Multi-Loco 的局限是新形态无法直接合成策略；Go2 腿式数据廉价且充足，而 Go2-W 多出 4 个轮速度槽位，**先验里没有轮子**。要回答：腿式扩散先验能否为 Go2-W 提供有用的腿部运动模式，使轮槽位只需少量 RL 学习？
- 方法草图：用 Go2（12 维）与 Go2-W（16 维）两类专家数据预训练掩码 EDM；对照"仅 Go2 先验"、"Go2 + Go2-W 先验"、"无先验 PPO"、"Go2 PPO 微调到 Go2-W"；残差 PPO 在轮槽位上做主要修正；可加一个"轮/腿比例"的条件输入作为轻量模式变量。
- 对照与消融：先验数据来源（仅腿 / 仅轮 / 混合）；数据量（1%–100%，沿用论文图 7 设计）；掩码 vs 学习型形态嵌入；残差惩罚系数；采样步数 3/5/10；与 URMA 式关节描述符做对照（可行性未核）。
- 实机指标：速度跟踪误差、楼梯/台阶成功率、轮腿切换的响应时间、实机能耗（电池 BMS，需核对读数可用性）、推理延迟。
- 工作量（评价）：中。约 6–8 周，含扩散推理的机载部署。
- 风险：Multi-Loco 自己的表 2 显示增益小，需要先证明"扩散先验比简单微调有用"，否则故事不成立。

**方向 B：热/力矩预算约束的有界残差**
- 问题：Go2-W 轮式行驶使髋关节过载发热，Matsuzawa 等（arXiv 2606.21387）靠周期性抬腿分摊，且热量没有进入策略训练。
- 方法草图：扩散先验提供步态/行驶模式的多模态候选，残差受"热/力矩预算"约束（带约束 PPO 如 P3O，约束项来自辨识的热模型）；残差范数从固定 L1 惩罚换成预算驱动。
- 对照与消融：无约束残差；固定 L1；仅热奖励（对标 Go2 热感知预印本）；有无先验。
- 实机指标：电机温升曲线、连续行驶时长（到阈值）、COT、速度跟踪。
- 工作量：重。热模型需自建，Go2-W 温度字段可读性有保留（读数整数度、有滞后，来自 thermal_aware.md 记录）；实机长时间实验耗时。
- **评价**：创新性来自"热"而非"扩散"，与 Multi-Loco 的耦合弱，更像另一张卡片 thermal_aware.md 的模块。

**方向 C：扩散先验的模式混合与平滑切换**
- 问题：Go2-W 在行驶与步行之间切换时，单策略要么多模态平均、要么靠外部选择器。扩散的多模态采样是否能在不加选择器时保持两种模式互不污染？
- 方法草图：用纯轮行驶专家与腿步行（锁轮）专家的数据训练模式条件扩散先验，模式由指令/地形触发；残差 RL 负责过渡。
- 对照与消融：MUJICA 式技能选择器、模式条件蒸馏（见 §7）、无先验的多模式 PPO；条件 vs 无条件扩散。
- 实机指标：切换时延、切换时的机身高度/速度跳变、台阶成功率、能耗。
- 工作量：中到重。
- **评价**：与现有工作重叠最多（见 §7），作为主创新点风险最大。

### 6.2 推荐顺序（评价）
方向 A > 方向 C（若能找到清晰差异） > 方向 B（作模块）。A 的理由：贴合论文自己的局限；数据在 robot_lab 内即可产生；对照简单明确；实机指标易测。**前提：先做 §5.4 的最小实验，确认扩散先验相对基线有增益。**

## 7. 查重（2025–2026 近邻，检索日期 2026-11-24）

**检索方式**：WebSearch 约十条查询（扩散 + 轮足、跨形态 + 轮足、轮腿模式切换、Go2-W、Multi-Loco 后续、TRON1 扩散）+ OpenAlex 施引列表。**检索工具有限，不是穷尽检索**；Google Scholar 与 Semantic Scholar 的施引列表未取到。

| # | 工作 | 状态与出处 | 与本方向的关系与差别 |
|---|---|---|---|
| 1 | **Multi-Loco** 本身 | CoRL 2025（PMLR v305） | 已含轮式双足 + 点足双足 + 人形 + 四足的扩散 + 残差；**没有轮式四足（Go2-W 型）**，没有轮腿模式切换 |
| 2 | **LocoFormer**（arXiv 2509.23745） | 预印本，venue 未核实；仓库已存 `01_papers/locoformer`；检索摘要：单策略零样本部署 Go2 与 Go2-W，锁轮后自动切换到步行，后腿双足模式 | 最接近"Go2-W 单策略轮腿统一"；用长上下文 Transformer 在线适应，**不是扩散，不是先验 + 残差**。方向 C 必须与它对照 |
| 3 | **MUJICA**（arXiv 2605.13058） | 预印本，2026-05-13；Go2-W 实机（来自本仓库 wheel_legged.md） | 技能指示变量 + 高层选择器，单一本体策略；覆盖全向移动、攀台、倒地恢复。与方向 C 重叠，差别在扩散先验 vs 选择器 |
| 4 | **Transformable Quadruped Wheelchair**（Akamisaka、Nagao；Sensors 26(2):566，2026-01，DOI 10.3390/s26020566） | 已发表（MDPI Sensors）；代码仓库自述公开（`transformable-quadruped-wheelchair-lab`，未核） | 对步行/轮式各训一个策略再做**模式条件蒸馏**成单策略。最接近方向 C 的"蒸馏统一"思路；平台为自制可变形轮椅，无扩散 |
| 5 | **DMLoco**（arXiv 2507.05674） | 预印本（v2 2025-09-12），无录用信息 | 扩散多任务预训练 + 在线 PPO 微调，仅四足；证明"扩散 + RL 微调"本身不新，Multi-Loco 之外的并行工作 |
| 6 | **Energy-Efficient Omnidirectional Locomotion for Wheeled Quadrupeds**（Yang 等，arXiv 2601.10723） | IROS 2025（arXiv 页标注）；改装 Unitree Go1 轮式四足实机 | 能量预测选名义步态 + 残差 RL，节能最高 35%（自述）；"先验步态 + 残差"思路在轮式四足上**已有先例**，但先验是参数化步态而非扩散 |
| 7 | **ATRos**（arXiv 2510.09980） | IROS 2025 轮足研讨会投稿，4 页，Go2W EDU 初步实机 | 无预设步态的行驶-行走混合运动，无量化能耗；小体量 |
| 8 | **Matsuzawa 等**（arXiv 2606.21387） | 预印本，v1 2026-06-19，v2 2026-11-13；Go2-W 实机 | 热过载与周期性抬腿；方向 B 的动机来源，热量未进策略 |
| 9 | **Ségas 等**（arXiv 2611.22231，2026-11-17） | 预印本（来自本仓库 thermal_aware.md 记录，本次未重新抓取） | Go2 实机热感知学习，已占据 Go2 上的热路线；方向 B 须与之区分 |
| 10 | **KING**（arXiv 2608.01015） | IROS 2026（arXiv 评论栏） | 用 URDF 图统一腿/轮机器人的**里程计**，不是控制策略；仅说明"腿轮统一表示"在估计侧有人做 |
| 11 | Lee 等 ETH（Science Robotics 2024，轮足 ANYmal 行走-驾驶切换） | 已发表（来自本仓库 wheel_legged.md） | 学习型行走-驾驶平滑切换的里程碑，无扩散 |

**结论（如实写）**：
- **"扩散先验 + 残差 RL 用于轮式四足（Go2-W 型）"**：在本次检索范围内**没有找到直接已做的工作**。Multi-Loco 已覆盖"轮式双足"，DMLoco 覆盖"四足扩散 + PPO 微调"，但两者都没有轮式四足；这是一个窄但真实的空档。**不能说无人做**——检索有限，且 Multi-Loco 作者团队（LimX 背景）很可能继续做轮式平台。
- **"Go2-W 轮腿模式统一/切换"**：**已被覆盖较多**（LocoFormer、MUJICA、模式条件蒸馏、ATRos、Lee 2024）。以"统一/切换"本身作创新点站不住，必须靠"扩散先验的作用"这一区别并用对照证明。
- **"热/能耗感知"**：Go2 已有 Ségas，Go2-W 已有 Matsuzawa 手工方案；"进入策略训练"的空档窄。
- 综合：方向 A 最干净但依赖先验确有增益；方向 C 查重风险最高；方向 B 与 Multi-Loco 耦合弱。

## 8. 总体判断

1. **论文价值：中。** 顶会、设定清晰、是少数覆盖轮式机器人的跨形态扩散工作，但实验增益小且部分指标为负，教师即基线，实机无定量数据，方法组件均为现成。**价值在设定与框架，不在结果。**
2. **作为基础论文**：官方代码很可能存在且体量适中，专家权重在仓库里，EDM 权重只有外链；主要障碍是 Isaac Gym（不可用）与 TRON-1 专用环境。**可行路线是只借 `rl_alg` + EDM 流水线，环境改用 robot_lab/Isaac Lab**，不移植 `source/mdp`。
3. **创新空间**：方向 A 为主。创新点是否成立取决于 §5.4 的最小实验能否证明先验有用。

## 9. 没有核实的事项

- 论文 PDF 页码；表 3/4/5/6 与 §3.2.2、§3.2.3、附录各数字（单次转述）的逐项核对。
- 论文中四个实机的型号；附录 A.6 的 Go2 是否真机。
- 仓库是否被作者认可为官方发布；仓库与论文超参是否一致；`ppo_unified_edm.py` 的多 critic 实现（未读源码）。
- 飞书 EDM 权重链接是否可用及内容。
- 机载（Go2-W 的 Jetson 等）上 5 步 DiT 推理延迟。
- Semantic Scholar / Google Scholar 施引；施引论文的引用方式；Robust Fall Recovery for Armless Bipedal-Wheeled Robots 是否涉及扩散。
- LocoFormer 的录用状态与 Go2-W 细节（只见检索摘要，仓库 PDF 本次未读）；Ségas（2611.22231）本次未重抓。
- 轮式双足 / 点足的具体硬件是否为 TRON-1（仓库暗示，论文未写）。
