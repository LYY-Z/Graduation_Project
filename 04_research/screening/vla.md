# VLA 与基础策略方向粗筛（第一轮，非精读）

日期：2026-11-24。范围：开源 VLA 的微调与部署、RL 微调 VLA、动作块执行与推理延迟、VLA 与底层控制器的接口、腿足/轮足语言条件策略。
记号：【事实】来自摘要、论文正文、仓库页，已打开核对；【评价】我的判断；【猜想】未验证的研究设想。

## 1. 检索范围

- 来源：arXiv 摘要页与 HTML 正文、RSS/PMLR(CoRL) 论文集页面、NeurIPS/ICLR 页面、GitHub 仓库首页、Hugging Face 模型页、LeRobot 文档。
- 查询（英文，WebSearch，2026-11-24）：real-time chunking VLA；openpi π0.5 微调显存；SmolVLA；OpenVLA-OFT；RL fine-tuning VLA（ConRFT/RLinf/SimpleVLA-RL/π*0.6）；quadruped VLA language-conditioned locomotion；wheeled-legged VLA；DSRL；training-time RTC / VLASH；NaVILA。
- 工具局限：WebFetch 返回的是小模型对网页的摘要，数字已尽量要求"逐字引用"，但仍未逐一回到原 PDF 复核；标"未给出"的是页面没出现，不代表论文没有。
- 未做：没有按会议论文集做系统枚举；没有逐篇打开 OpenReview 评审意见；没有核实服务器 GPU（STATUS 中"RTX PRO 5000"型号和显存未核实，下文显存判断都以"单卡 ≥24GB / ≥48GB"分档，不假设具体值）。
- 标注"页面未给出显存/时长/演示量"的格子，需要精读或跑通后补。

## 2. 总览

| # | 工作 | 状态 | 与双平台关系 | 初评 |
|---|---|---|---|---|
| 1 | π0.5 / π0 + openpi（含 UR5 微调示例） | π0.5：CoRL 2025 正式发表 | UR7e 直接可做；Go2-W 不适用端到端 | A |
| 2 | Real-Time Chunking (RTC) | NeurIPS 2025 | 问题在两平台都存在（延迟/块衔接） | A |
| 3 | DSRL（潜在噪声空间 RL 引导冻结策略） | CoRL 2025 | 方法可迁移，Go2-W 需自己论证 | A |
| 4 | VLASH（未来状态感知异步推理） | 预印本（v2 2026-07） | 同 RTC，有代码 | B+ |
| 5 | Training-time RTC | 预印本 | 同上，作者无代码，LeRobot 已集成 | B |
| 6 | OpenVLA-OFT | RSS 2025 | UR7e 可行但 7B 偏重；Go2-W 不适用 | B |
| 7 | SmolVLA | 预印本（未查到录用） | 单卡友好；UR7e 可行 | B |
| 8 | GR00T N1 / N1.7 | N1 预印本；N1.7 为代码发布 | 人形为主；UR7e 可微调 | B |
| 9 | ConRFT | RSS 2025 | 实机 RL 范式；基建绑定 Franka | B |
| 10 | SimpleVLA-RL | ICLR 2026 | 仅仿真，8×80GB | C |
| 11 | RLinf-VLA | RSS 2026 | 框架；论文仅仿真 | B |
| 12 | π*0.6 / RECAP | RSS 2026 | 无代码 | C |
| 13 | NaVILA | RSS 2025 | 仅 Go2 侧；是"高层 VLA → RL 低层"的现成范例 | B |
| 14 | MobileVLA-R1 | 预印本 | 四足，无录用信息 | C |
| 15 | LocoVLM | 预印本 | 无代码，实机未确认 | C |
| 16 | FWBC-VLA | 预印本（2026-09） | 轮足+臂，无代码 | C |

## 3. 候选详情

### 1. π0.5 / π0 与 openpi
- 论文与链接：π0.5: a VLA with Open-World Generalization, Black et al. [PMLR v305](https://proceedings.mlr.press/v305/black25a.html)，[arXiv 2504.16054](https://arxiv.org/abs/2504.16054)；代码 [Physical-Intelligence/openpi](https://github.com/Physical-Intelligence/openpi)。
- 发表状态：π0.5 为 CoRL 2025 正式发表（PMLR 305，已核对）。π0 论文本身的录用状态本轮未核对。
- 作者研究的问题【事实】：用异构机器人数据、语义子任务预测、网页数据共训，使 VLA 泛化到新家庭环境。
- 方法类别/动作接口【事实】：VLM + flow-matching 动作专家，输出动作块（后文 RTC 论文用 π0.5，H=50）。openpi 的 UR5 示例：7 维动作（6 关节 + 夹爪），前 6 维训练时转为增量，状态为关节值 + 夹爪，两路相机（基座、腕部）+ 文本提示。
- 部署输入：多路 RGB + 本体状态 + 语言。
- 实验平台与实机：论文为多种移动操作机器人实机；本项目关心的是 openpi 的复现路径。
- 公开材料【事实，已打开】：Apache-2.0（另有 Gemma 许可文件）；`pi0_base`、`pi0_fast_base`、`pi05_base` 基座；`pi05_droid`、`pi05_libero` 等微调权重；README 同时提供 PyTorch 实现（2025-09），但 PyTorch 版不支持 LoRA、FSDP、混合精度、π0-FAST；`examples/ur5` 存在。
- 算力与数据【事实】：README 硬件表：推理 >8GB（RTX 4090）；LoRA 微调 >22.5GB（RTX 4090）；全量微调 >70GB（A100 80GB/H100）。UR5 示例 30,000 步。演示条数：README 未给出，仅称微调数据集"相对较小"。
- 双平台相关性【评价】：UR7e 侧直接对应（UR5 示例、腕部相机、已有 Diffusion Policy 部署链路可复用接口层）。Go2-W 侧无现成接口，端到端 VLA 输出 12 腿+4 轮目标没有公开先例，不应作为 Go2-W 的主线。
- 作者承认的局限：本轮读到的页面未列出（需精读 §Limitations）。
- 创新空间【猜想】：与 #2/#3 组合，在冻结的 π0.5 上做延迟鲁棒执行或 RL 引导；Go2-W 侧只用其"高层指令"思想，不用其动作头。
- 初评 A：UR7e 上最成熟的 VLA 底座，权重/代码/微调脚本/LoRA 显存数字齐全；A 仅针对 UR7e 半边。

### 2. Real-Time Execution of Action Chunking Flow Policies（RTC）
- 链接：[arXiv 2506.07339](https://arxiv.org/abs/2506.07339)；[NeurIPS 2025 poster](https://neurips.cc/virtual/2025/poster/117747)；LeRobot 实现 [文档](https://huggingface.co/docs/lerobot/en/rtc)。
- 发表状态：NeurIPS 2025 正式发表（arXiv 评论栏、NeurIPS 页面均确认）。
- 问题【事实】：动作块策略推理延迟导致块边界停顿或抖动；需要异步执行。
- 方法【事实】：推理时把下一块生成当作 inpainting，冻结必然执行的动作前缀，对其余部分做引导；无需重新训练，适用于扩散/流策略。层级：策略输出之后、控制器之前的执行层。
- 部署输入：任意流/扩散动作块策略 + 估计的推理延迟 d。
- 平台【事实】：仿真 Kinetix 12 个动态任务；真机为双臂 6-DoF 位置控制，6 个任务，480 个实机回合约 28 小时；基座 π0.5，H=50，50Hz 控制；模型延迟 76ms（基线）/97ms（RTC），RTX 4090 bf16，另外注入 100/200ms 延迟。
- 公开材料【事实】：论文页无代码链接；PI 的 Kinetix 参考实现 `real-time-chunking-kinetix`（LeRobot 文档列出，我未打开该仓库）；LeRobot 内置 RTC（支持 Pi0、Pi0.5、SmolVLA，`lerobot-rollout --inference.type=rtc`，已读文档）。论文称 π0.5 训练数据与真机运行代码因专有未公开。
- 算力/数据：无需训练；推理要求同底层 VLA。
- 双平台相关性【评价】：延迟与块衔接问题在 UR7e（VLA 块 → 关节/TCP 目标）与 Go2-W（任何 20–50Hz 的块或高层指令 → 低层 RL）上都真实存在，这是本方向少有的"两平台共同问题"。
- 作者承认的局限【事实】：仅适用于扩散/流策略；比直接采样多出显著计算开销；腿足仅在仿真中涉及，未做真机。
- 创新空间【猜想】：(a) 把 RTC 思想用于"VLA 块 → 低层 RL 策略"的接口，处理高层目标更新对 Go2-W 步态/轮速的突变；(b) 把延迟 d 作为在线估计量，随负载自适应。两项均需查重。
- 初评 A：有真实的双平台共同问题，LeRobot 有可用实现，不用训练；风险在于它偏"工程算法"，创新需落在接口层。

### 3. DSRL：用潜在噪声空间 RL 引导扩散/流策略
- 链接：[arXiv 2506.15799](https://arxiv.org/abs/2506.15799)；[PMLR v305](https://proceedings.mlr.press/v305/wagenmaker25a.html)；代码 [ajwagen/dsrl](https://github.com/ajwagen/dsrl)、[nakamotoo/dsrl_pi0](https://github.com/nakamotoo/dsrl_pi0)。
- 发表状态：CoRL 2025 正式发表（PMLR 条目确认；arXiv 页自身无录用标注）。
- 问题【事实】：行为克隆策略需要昂贵的额外演示，标准 RL 样本效率低；如何只用黑盒访问、不改权重地做在线改进。
- 方法【事实】：对策略的输入噪声（潜在空间）做 RL，冻结基策略权重。控制层级：不改变动作接口，只改变采样噪声。
- 部署输入：基策略 + 稀疏 0/1 奖励 + 在线回合 + 重置。
- 实验【事实】：Franka 抓放方块：基策略 10 条演示，2/10 → 9/10，约 40 回合/3500 步；WidowX 上 Bridge 预训练策略 100–150 回合适配；π0-DROID 在 Franka：开烤面包机 5/20 → 18/20（80 回合）、放勺子 15/20 → 19/20（65 回合）。
- 公开材料【事实，已打开 dsrl_pi0】：MIT；JAX（jax[cuda12]==0.5.0）；含 openpi 与 LIBERO 子模块；真机流程为 DROID 包 + 远端托管 π0；未列显存。RLinf 也有 DSRL 示例（仅见文档标题，未打开）。
- 算力：论文未报告 π0 实验的 GPU 与算力；小型 SAC 训练在噪声上，推理需 π0。
- 双平台相关性【评价】：UR7e：路径清晰（把 Franka/DROID 接口换成 UR7e，基策略用 π0/π0.5 或自训 DP）。Go2-W：可以把"冻结的 RL 运动策略 + 噪声/潜变量"换成同一思想（需要策略有可操控的随机输入），但没有先例，属研究设想。
- 作者承认的局限【事实】：探索受基策略限制；动作分布过窄时可改进空间小；无法事先估计改进上限；仍需奖励、在线回合与重置。
- 创新空间【猜想】：用已有 UR7e + Diffusion Policy 链路做"冻结 DP + 噪声 RL"的真机对照；Go2-W 用冻结 RL 策略 + 潜变量/残差。需要先做查重（残差 RL、ResiP、V-GPS 等已被作为基线）。
- 初评 A：真机样本量小（几十到一百余回合）、权重不动、与 UR7e 现有链路契合；双平台迁移需自己论证。

### 4. VLASH：未来状态感知的异步推理
- 链接：[arXiv 2512.01031](https://arxiv.org/abs/2512.01031)；[mit-han-lab/vlash](https://github.com/mit-han-lab/vlash)。
- 状态：预印本（v1 2025-11-30，v2 2026-07-26；页面未标录用）。
- 问题/方法【事实】：同步推理使机器人停顿；用上一块动作把状态前推，预测执行时刻的状态；不改架构、无额外运行开销。
- 结果【事实】：反应延迟最多降 11.8×（摘要页；先前搜索摘要写 17.4×，v1/v2 数字不一致，待核）；加动作量化后任务完成快 1.5–2.0×；π0.5 打乒乓、打地鼠。
- 公开材料【事实，已打开】：Apache-2.0；支持 π0.5、π0（SmolVLA 未提及）；基于 LeRobot；`vlash train examples/train/pi05/async.yaml`；π0.5 在 RTX 5090 上 >30Hz；LoRA <12GB 与 QLoRA <8GB 仅为未勾选 TODO；README 无微调时长。
- 双平台相关性【评价】：UR7e 可用；Go2-W 上与 RTC 同类问题，但无腿足实验。
- 局限：页面未列；机器人硬件未写。
- 创新空间【猜想】：与 RTC 作系统比较（已有 2026-05 的比较研究 arXiv 2605.08168，我只看到标题，未读）。
- 初评 B+：代码可用，但与 #2 重合，且还需确认录用。

### 5. Training-Time Action Conditioning for Efficient RTC
- 链接：[arXiv 2512.05964](https://arxiv.org/abs/2512.05964)。预印本，页面无评论栏。
- 【事实】：训练时模拟推理延迟、对动作前缀条件化，去掉推理时 inpainting 开销；基于 π0.6，箱子搭建与浓缩咖啡任务；作者无代码。LeRobot 文档称对"兼容的 Pi05 检查点"提供 trained 模式（需 `rtc_training_max_delay > 0` 训练）。
- 评价：对延迟敏感的真机（Go2-W 低层需要稳定节拍）有吸引力，但需要重新微调基座；对 π0.5 的微调显存同 #1。
- 初评 B：想法清楚，但官方无代码、依赖微调。

### 6. OpenVLA-OFT
- 链接：[arXiv 2502.19645](https://arxiv.org/abs/2502.19645)；[RSS 2025 p017](https://www.roboticsproceedings.org/rss21/p017.html)；代码 [moojink/openvla-oft](https://github.com/moojink/openvla-oft)。
- 状态：RSS 2025 正式发表。
- 问题/方法【事实】：并行解码 + 动作块 + 连续动作 + L1 回归，优化 OpenVLA 微调的速度与成功率；OFT+ 加 FiLM 强化语言。
- 实机【事实】：双臂 ALOHA（3 路相机 + 14 维关节状态，25Hz）。演示量：折短裤 20、折衬衫 30、舀入碗 45、放入锅 300 条。
- 算力【事实】：LIBERO 与 ALOHA 微调均用 8×A100/H100，步数 50–150K，页面未给时长。仓库称微调 1–8 卡、27–80GB；推理 LIBERO 约 16GB、ALOHA 约 18GB。A100 上 ALOHA OFT+ 77.9Hz（块吞吐）、延迟 0.321s。
- 公开材料【事实，已打开】：MIT；权重如 `moojink/openvla-7b-oft-finetuned-libero-spatial`；`ALOHA.md`、`LIBERO.md`。
- 局限【事实】：L1 回归可能难以建模真正多模态动作；预训练阶段是否受益未知；无 FiLM 时 ALOHA 语言对齐差。
- 双平台相关性【评价】：7B 在单卡上做全量微调不现实，需要 LoRA；UR7e 可行但相比 openpi 无明显优势；Go2-W 不适用。
- 初评 B：RSS 正式发表且代码/权重齐全，但与 #1 功能重叠且更重。

### 7. SmolVLA
- 链接：[arXiv 2506.01844](https://arxiv.org/abs/2506.01844)；[lerobot/smolvla_base](https://huggingface.co/lerobot/smolvla_base)。
- 状态：预印本；arXiv 页面未列录用。检索范围内没有查到正式发表。
- 【事实】：约 0.45–0.5B 参数；"可单卡训练、消费级 GPU 或 CPU 推理"；含异步推理栈；仅用社区开源数据预训练。Apache-2.0；微调命令 `lerobot-train`，示例 `--steps=100000 --batch_size=4`，可开 gradient checkpointing。页面未给 GPU 型号、显存、时长、演示条数；真机平台（SO-100/101）未在抓取内容中确认。
- 双平台【评价】：算力最友好，适合做 UR7e 上的快速对照；Go2-W 不适用端到端。
- 创新空间【猜想】：作为 #2/#3/#4 的低成本载体，验证方法再换到更大的 π0.5。
- 初评 B：算力友好，但录用状态和性能证据弱于 π 系列。

### 8. GR00T N1 / N1.7
- 链接：[arXiv 2503.14734](https://arxiv.org/abs/2503.14734)；[NVIDIA/Isaac-GR00T](https://github.com/NVIDIA/Isaac-GR00T)。
- 状态：N1 论文为预印本（页面无录用）；仓库已发布 N1.7。
- 【事实，已打开仓库】：代码 Apache-2.0，权重 NVIDIA Open Model License；`nvidia/GR00T-N1.7-3B` 及 LIBERO/DROID/SimplerEnv 微调权重；推理 1 卡 ≥16GB；微调"1 卡以上、建议 ≥40GB"；TensorRT 下 RTX PRO 6000 Blackwell 约 40Hz、Jetson AGX Thor 约 28Hz；有 `UNITREE_G1_SONIC` 后训练标签和 SO-100 示例；示例数据集仅 5 条回合，README 称"训练几千步"，未给推荐演示量。
- 双平台【评价】：Unitree G1 的标签说明与 Unitree 生态有联系，但不是 Go2-W；UR7e 需走 `NEW_EMBODIMENT`。
- 局限：论文以人形为中心，页面未列局限。
- 初评 B：权重和部署数字完整，但 40GB 微调门槛对未核实的 GPU 有风险。

### 9. ConRFT
- 链接：[arXiv 2502.05450](https://arxiv.org/abs/2502.05450)；[RSS 2025 p019](https://roboticsproceedings.org/rss21/p019.html)；[cccedric/conrft](https://github.com/cccedric/conrft)。
- 状态：RSS 2025 正式发表。
- 【事实】：离线（BC + Q 学习）+ 在线（一致性策略 + 人类干预）统一目标微调 VLA（Octo）；8 个真机任务，45–90 分钟在线微调达 96.3% 平均成功率；离线阶段约 20–30 条演示（附录）。
- 仓库【已打开】：Apache-2.0；基于 HIL-SERL，Franka + serl_franka_controllers + ROS Flask 服务；JAX cuda11 `jax==0.4.20`；未列显存和检查点；演示数量未写。
- 双平台【评价】：UR7e 需要重写机器人基础设施；JAX 0.4.20 + CUDA11 与新 Blackwell GPU 的兼容性未知，需验证。Go2-W 不适用。
- 局限：仓库未列。
- 初评 B：有真机样本效率的最强证据之一，但基建绑定 Franka、环境老。

### 10. SimpleVLA-RL
- 链接：[arXiv 2509.09674](https://arxiv.org/abs/2509.09674)；[ICLR 2026](https://iclr.cc/virtual/2026/poster/10009314)；[PRIME-RL/SimpleVLA-RL](https://github.com/PRIME-RL/SimpleVLA-RL)。
- 状态：ICLR 2026 正式发表。
- 【事实】：基于 veRL，对 OpenVLA-OFT 做 GRPO 类在线 RL；每任务一条轨迹冷启动 SFT，LIBERO 17.3 → 91.7（仓库表述）。仓库：MIT；已测环境 8×A800 80GB；仅仿真，真机 RL 为未勾选；π0/π0.5/SmolVLA 在路线图上。
- 双平台【评价】：算力和仿真依赖超出预算，也没有 UR7e 或 Go2-W 仿真环境。
- 初评 C：对本项目的算力和实机要求不匹配。

### 11. RLinf-VLA 与 RLinf
- 链接：[arXiv 2510.06710](https://arxiv.org/abs/2510.06710)；[RSS 2026 p089](https://roboticsproceedings.org/rss22/p089.html)；[RLinf/RLinf](https://github.com/RLinf/RLinf)。
- 状态：RSS 2026 论文集（页面确认）。
- 【事实】：统一框架，支持 OpenVLA/OFT、π0/π0.5、GR00T N1.5–1.7，PPO/GRPO；LIBERO 130 任务 98.11%、ManiSkill 25 任务 97.66%、RoboTwin 6 任务 84.63%；混合流水线 1.61–1.88× 加速。论文页面未提真机实验。仓库：Apache-2.0；真机支持 Franka、ARX X5、Piper、SO101 等；含 IsaacLab 仿真；未给最小显存，推荐 Docker，提及 4×H800。
- 双平台【评价】：可当作工具而非研究对象；UR7e 不在支持列表中。
- 初评 B：做 RL 微调 VLA 时可复用，但算力与 UR7e/Go2-W 适配都需自行承担。

### 12. π*0.6 / RECAP
- 链接：[arXiv 2511.14759](https://arxiv.org/abs/2511.14759)；[RSS 2026 p087](https://www.roboticsproceedings.org/rss22/p087.html)。
- 状态：RSS 2026 论文集。
- 【事实】：优势条件策略，从演示、策略回合、在线纠正中学习；最难任务吞吐翻倍、失败率约减半。页面未给机器人、数据量、参数量，未见开源信息。
- 初评 C：不可复现。仅作为"RL 改进 VLA"的参照与对标。

### 13. NaVILA
- 链接：[arXiv 2412.04453](https://arxiv.org/abs/2412.04453)；[RSS 2025 p018](https://roboticsproceedings.org/rss21/p018.html)；[AnjieCheng/NaVILA](https://github.com/AnjieCheng/NaVILA)；低层 [yang-zj1026/legged-loco](https://github.com/yang-zj1026/legged-loco)。
- 状态：RSS 2025 正式发表（论文集页确认；arXiv 页无评论栏标注）。
- 问题/方法【事实】：腿足视觉语言导航。VLA 输出语言形式的中层动作（如"前进 75cm"），映射为固定速度指令（前进 0.5 m/s、转向 ±π/6 rad/s、停止），再由 PPO 训练的视觉运动策略执行；该策略输入来自 Unitree L1 激光雷达的 2.5D 高度图，输出 12 个腿关节的目标位置，Isaac Lab 训练。
- 实机【事实】：Go2、Booster T1、G1；25 条指令 × 3 次，工作区/家/室外，总体 88%、复杂指令 75%。
- 算力【事实】：VLA 8B；推理单卡 RTX 4090 约 1FPS；W4A16 量化显存 18.5GB → 8.6GB、延迟 594.58ms → 367.80ms；训练：预训练阶段 16 个 A100 节点（每节点 8 卡）30 小时+，NaVILA 指令微调 4 个 A100 节点 18 小时（继承自 VILA，非单卡可复现）。
- 公开材料【已打开】：VLA 仓库 Apache-2.0，权重 `a8cheng/navila-llama3-8b-8f`，训练脚本；YouTube 数据只给标注与视频 ID；低层仓库 MIT，Go2 与 H1，Isaac Lab 1.1.0 + Isaac Sim 4.1.0（需作者 fork），无检查点，无部署说明。
- 作者局限【事实】：真机部分失败（卧室导航无法纠偏）；泛化和空间理解需要更大规模仿真；图像 VLM 计算量大；VLA 未上机载，需传图像。
- 双平台【评价】：只有 Go2 侧；Go2 到 Go2-W 的低层策略需重训（轮速目标）。其价值是给出"VLA 离散语言 → 速度指令 → RL 低层"的最简接口，而 UR7e 没有对应物。
- 创新空间【猜想】：用小 VLM 替代 8B，或研究高层指令频率/延迟对低层的影响，与 #2 衔接。
- 初评 B：Go2 单平台，但是本方向里最完整的"高层 VLA + RL 低层 + 实机"链路。

### 14. MobileVLA-R1
- [arXiv 2511.17889](https://arxiv.org/abs/2511.17889)，预印本，无录用信息；代码 [AIGeeksGroup/MobileVLA-R1](https://github.com/AIGeeksGroup/MobileVLA-R1)（仅从摘要页得到，未打开）。【事实】CoT 数据集 + 监督对齐后 GRPO，四足真机"验证"，具体机型和数据量未给。
- 初评 C：信息不足，预印本，且与 NaVILA 同类。

### 15. LocoVLM
- [arXiv 2602.10399](https://arxiv.org/abs/2602.10399)，预印本（2026-02）。【事实】LLM 建技能库、VLM 做环境语义到技能的映射、风格条件运动策略；指令跟随准确率最高 87%；无需在线调用云端模型。页面未给机型、代码、实机确认。
- 初评 C：无代码，实机未确认。

### 16. FWBC-VLA
- [alphaXiv 2609.03889](https://www.alphaxiv.org/abs/2609.03889)，预印本（2026-09；alphaXiv 页面标注 NeurIPS 2026，未确认录用）。【事实】轮足 + 臂的接触丰富任务；无传感器的残差力矩估计 HSR-Force 产生接触 token 输入动作专家，并向全身控制器叠加有界补偿；5000+ 回合数据；平台为 DeepRobotics（M20S，来自搜索摘要）；无代码。
- 评价：问题设定最接近"VLA 输出 + 轮足低层控制"，但不可复现。
- 初评 C。

## 4. 对 VLA 方向的综合判断（评价，不是作者事实）

1. 端到端 VLA 在 Go2-W 上没有现成接口或先例。检索范围内没有找到以 Go2-W 为平台的 VLA 工作；腿足相关工作都是"高层模型 → 离散语言/速度指令 → RL 低层"（NaVILA、LocoVLM），或仅在仿真/特定机型验证。
2. 因此 VLA 本体只能落在 UR7e；Go2-W 要靠"接口层"问题与之对应：延迟与块衔接（#2、#4、#5）、冻结策略上的轻量 RL 引导（#3）、高层低频指令与低层高频控制的衔接（#13）。这些是 STATUS 里"只对一个平台成立的贡献难以满足要求"的潜在解法，但每一项都还要做查重。
3. 单卡可行性：openpi LoRA >22.5GB、推理 >8GB 是最明确的数字；GR00T 微调建议 ≥40GB；OpenVLA-OFT 27–80GB；SmolVLA 声称可单卡但无数字。结论依赖服务器 GPU 显存，目前仍未核实。
4. 真实数据量：DSRL 在冻结 π0 上几十到一百余回合；ConRFT 20–30 条演示 + 45–90 分钟；OFT 在 ALOHA 上 20–300 条；openpi 无数字。这些量级对 UR7e 遥操作可承受，对 Go2-W 无意义。

## 5. 未覆盖或存疑

- 未核实：π0 论文录用状态；SmolVLA、GR00T N1、VLASH 是否已在 2026 年被录用；VLASH 摘要中的延迟倍数（11.8× 与 17.4× 两个说法冲突）。
- 未打开：PI 的 `real-time-chunking-kinetix` 仓库、RLDX-1、ajwagen/dsrl 仓库本身、MobileVLA-R1 仓库、RLinf 的 DSRL 文档、Spot Micro 的学生项目（CS224R 报告，非正式发表）。
- 未覆盖的方向：Hi Robot/分层 VLA、FAST tokenizer、π0.5 的 Knowledge Insulation、VLA 上的残差 RL（ResiP、Policy Decorator）、移动操作 VLA（腿足 + 臂）、世界模型+VLA；这些应交给其他方向或后续轮次。
- 没有 UR7e 上的 VLA 真机公开工作被确认（仅有 openpi 的 UR5 示例，内容为数据转换说明，不是实机结果）。
- RTX PRO 5000 的显存规格未核实，所有"单卡可行"结论均为条件性。
- Go2-W 底层接口（lowcmd 是否开放、轮速目标接口）未核实，决定了 #13 及类似的低层迁移成本。
