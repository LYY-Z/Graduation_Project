# 8 篇论文的算力与硬件需求核实（2026-11-26）

约定：页码为 PDF 页序；"未报告"＝论文正文与附录、官方仓库（README/配置）均未见；【估计】＝我的推算，算法写明，非事实。本次读了 PDF 全文抽取、仓库 README/配置，未运行代码。

## 一、事实表

| 论文 | (a)(b) 训练硬件与规模 | (c) 训练墙钟 | (d) 部署硬件与频率 | (e) 其他重算力 |
|---|---|---|---|---|
| 1 GRAM | GPU 未报告。Isaac Lab，Go2 平地。"We perform 10,000 updates during RL training, followed by … 5,000 updates"（p7）。仓库 `source/utils/cli_utils.py:27,29,68` 默认 4096 环境、10000 迭代、5000 微调迭代；需 Isaac Lab v1.0.0 + Isaac Sim 4.1.0（README） | 未报告 | "all computation is performed onboard"（p9），Go2，型号未写；策略 50 Hz，PD 200 Hz（p7） | 无 |
| 2 MoE-CTS | 论文：IsaacGym，"train 8192 agents in parallel"（p3）；GPU 未报告。仓库 lab3.0 默认 16384 环境（README；`mixed/env_cfg.py:632`），`max_iterations=100000`（`mixed/rsl_rl_cfg.py:17,49`）。检查点名：82.5k（Lab）、137000（Gym）、103.5k（CTS） | 论文未报告。仓库 `docs/from_gym_to_lab.md`（RTX 4090，MoE-CTS，实测 50 迭代）：8192 环境 Gym 2.30 / Lab 2.65 s/iter，显存 9.76/9.13 GiB；16384 环境 Gym 4.70 / Lab 4.37 s/iter，显存 15.63/17.80 GiB。robot_lab 分支 README："Training and saving checkpoints every 500 steps typically takes around 30 minutes"（EPYC 7763 + RTX 4090） | 论文未报告。部署仓库 `unitree_cpp_deploy` README：Go2 Edu，"using an Orin NX or an external computer connected over Ethernet"；策略 50 Hz（论文 p3） | RoboGauge 评测：CPU 多进程，"approximately 5 minutes with num_processes=63"（EPYC 7763） |
| 3 PACE | 辨识："single NVIDIA GeForce RTX 3080"（p12，限"PACE optimizations and simulations"）；N=4096 环境，CMA-ES。策略 PPO：30 000 迭代、每环境 24 步（Table 8，p30），环境数该表未见 | 辨识："converges within 10–24 h"（p18）；单驱动 30 次拟合合计"≈5 h"（p13）。策略：作者在 issue #30 回复："All final locomotion policies were trained for 24h for about 30k iterations on rough terrain"（LeggedGym/Isaac Gym，非 Isaac Lab）；策略训练 GPU 未报告 | 未报告（日志与低层控制 400 Hz，p12） | 实机辨识数据：每次 chirp 20–40 s（p12） |
| 4 AugMPC | "AMD Ryzen Threadripper 7970 CPU, 128 GiB RAM, and an NVIDIA RTX 4090 GPU"（p6）；SAC，800 并行环境，MPC 20 Hz，视野 N=30（p6、p8 附录）；"4–10×10⁶ environment steps, … 9–29 simulated days"（p6）。注意 README 写"1–10×10⁶"，与论文不一致 | "12 simulated days … approximately 5.8 hours of wall time"（p6）；README"≈6 h"；实时因子最高 50 | Centauro 机载，"RL evaluation requires only 0.334 ms on the onboard Intel Core i7-11800H CPU, while the MPC runs in real time"（p6）；策略 4 Hz，MPC 20 Hz（p6） | 瓶颈是 800 个 MPC 实例（CPU），非 GPU |
| 5 Random Joint Masking | 未报告（GPU、环境数、迭代数、PPO 超参均无；仅称在 Isaac Gym 训练） | 未报告 | 未报告（Go1，OptiTrack 外部定位；机载或外接未写） | 无 |
| 6 TAM | 论文未报告训练 GPU、时长、数据量。仓库用 JAX/MJX（`jax[cuda12]`），示例 `--max-steps 200000`、`--num-steps 4000 --history-batch 128`；公开权重目录名含 3472000（步数，仅文件名） | 未报告 | 编码器在工作站 GPU，5 Hz；力矩适配器在控制器 CPU，1 kHz（App B.2，p17）。"RTX 3080 … about 1.29 GB"，编码器单次 0.999±0.045 ms，适配器 0.155 ms；编码器约 4.4M 参数、适配器约 63K（p18）。控制器 CPU 型号未报告 | 对照基线 Online SysID：512 粒子，"effective parallel batch of 5120 simulated worlds"（p19） |
| 7 SimDist | 专家 PPO："4096 parallel simulation environments over 5000 PPO iterations, with 24 environment steps per iteration, for a total of 490M environment steps"（p14）。数据生成：4096 环境×25000 步≈100M 点。预训练 2 epoch、batch 512、约 3.69×10⁵ 次更新（p14）。操作任务：100k 轨迹、约 200k 次更新（p13） | 数据生成 "approximately 7 hours with a single NVIDIA RTX 4500 Ada GPU"；预训练 "approximately 28 hours on a single NVIDIA RTX 4500 Ada GPU"（p14）。专家 PPO 时长未报告；操作任务预训练时长未报告 | "plan at 50 Hz on a laptop with an RTX 4090M"（p6）；UR5e 控制 5 Hz。仓库部署用 Docker + NVIDIA 容器，需 Isaac Sim 4.5.0 | 真实适应 15–30 min 数据（摘要）；适应的计算耗时未报告 |
| 8 LocoFormer | GPU 型号未报告；环境数未报告。Fig. 9（p15）曲线图例为 32/64 GPUs × 3/6 层，虚线 128 GPUs、6 层；图注："4K iterations (28 hours for 6-layer TXL)"，未说明 28 h 对应 32 还是 64 卡 | 最终模型墙钟与迭代数未报告 | 未报告（真机含 Go2、Go2-W、G1、H1，p6）；示例控制频率 50 Hz（p5） | 原文（附录 C，p13）："LocoFormer takes 500 times more compute for 100000 more robots — … amortized compute cost per robot (1 vs. 0.005 day)." 局限节（p9）："highly resource-intensive" |

## 二、"500 times more compute"的解读【估计】

500÷100000＝0.005，故 "1 day" 是单个专家策略的算力，LocoFormer 总量约为其 500 倍，即 500 "day"。"day"是 GPU-day 还是墙钟天，原文未写。若为 GPU-day，则约 12000 GPU 小时；2 卡理想线性扩展需约 250 天。Fig. 9 的小变体按 32 卡×28 h＝896 GPU 小时算（前提：28 h 对应 32 卡，原文未证实），2 卡约 19 天。结论：无法复现，只能用作预训练思想参考。

## 三、能否在服务器（2×RTX PRO 5000 48 GB，96 线程）承受【估计】

吞吐没有实测。下面按 4090 实测值类比，PRO 5000 Blackwell 与 4090 同级的判断来自上游笔记，未验证。

| 论文 | 判断 | 依据 |
|---|---|---|
| GRAM | 可承受 | 4096 环境×10000 迭代。按 MoE-CTS 仓库实测 8192 环境约 2.3–2.7 s/iter 线性折半，约 1.2–1.3 s/iter，得约 3–4 小时（平地更轻，适应阶段另计）。风险在固定 Isaac Lab 1.0/Sim 4.1 与服务器 Sim 5.1 的版本差 |
| MoE-CTS | 可承受但偏重 | 82.5k 迭代×4.37 s（16384 环境）≈100 小时≈4.2 天；Gym 137k×2.30 s（8192）≈88 小时≈3.6 天。显存 ≤18 GiB，单卡可两路并行。仓库要求 Isaac Sim 6.2 / Isaac Lab 3.0，与服务器 5.1 不一致；IsaacGym 在 Blackwell 上不可用（上游笔记） |
| PACE | 可承受 | 辨识 RTX 3080 上 10–24 h，策略 24 h；论文的策略训练基于 Isaac Gym，服务器上需改走 Isaac Lab |
| AugMPC | 可承受，CPU 为主 | GPU 非瓶颈；800 个 MPC 实例吃 CPU。96 线程应不低于其 Threadripper（核数我记为 32，来自记忆，未核）；单核速度未知。MPC 模型栈与版本未核 |
| Random Joint Masking | 可承受 | 无大模型，legged_gym 上 PPO+教师学生，量级与普通速度策略相当（依据：上游笔记称改动量小） |
| TAM | 可承受 | 4.4M 参数，JAX 训练。风险是 JAX 在 sm_120 的兼容性，未测 |
| SimDist | 可承受，约 1.5–2 天/管线 | 7+28 h 是 RTX 4500 Ada 的数字，专家 PPO 另算；Blackwell 48 GB 预期不慢于它。在线规划需外接带 GPU 的笔记本 |
| LocoFormer | 不可承受 | 见第二节 |

## 四、Go2-W 机载对照【估计】

- 8 核主控不对用户开放（见 `05_experiments/go2w_onboard_compute.CN.md`），用户程序须放外接电脑或 Orin 扩展；Orin 型号待确认。
- GRAM、MoE-CTS、RJM：MLP 或小网络，50 Hz，毫秒级，机载可行。
- TAM：编码器需 GPU，适配器 1 kHz。【更正 2026-11-26】Go2-W 底层指令含前馈力矩（tau），并非不开放力矩接口；编码器约 440 万参数、5 Hz，Orin 的 GPU 估计可运行；主要限制是底层通信频率（通常约 500 Hz，需实测）低于 1 kHz。
- SimDist：MPPI 450 采样×8 迭代需 RTX 4090M 笔记本，机载不可行。
- AugMPC：作者在 i7-11800H 级 CPU 上机载实时运行 MPC；Go2-W 的 8 核主控与 Orin NX 能否达到未知，需实测。
- LocoFormer：Transformer 的 KV-cache 推理时延，机载未知。
