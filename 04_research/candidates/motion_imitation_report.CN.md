# 无轮运动数据向轮足迁移模仿：可行性核查（精简版）

日期：2026-11-25。按用户要求只做可行性核查，**不含**课题方案、16 周计划和提问清单。标记：【作者】原文事实；【评价】我们的判断。

## 1. 基础论文

**推荐：Fu 等，*Learning diverse natural behaviors for enhancing the agility of quadrupedal robots*，Nature Communications 17:5857（2026），DOI 10.1038/s41467-026-72475-9**（2025-05-10 投稿，2026-04-17 录用，p1）。

- 【作者】从真实狗的动捕数据（AI4Animation，约 20 分钟）学习：半监督 InfoGAIL（GAIL 类对抗模仿，与 AMP 同属一类）训练基础行为控制器 BBC，可切换 walk/pace/trot/canter/jump 五种步态，同时跟踪速度指令；用 EASI 只拿 80 s 真机数据辨识 PD 参数；在 **Go2 实机**上用深度相机完成敏捷赛道，平均 1.1 m/s，峰值 3.2 m/s（p1、p7、p11）。
- 【作者】开源：MIT 许可，含 Go2 重定向数据、BBC/TSC/EASI 训练代码和 `go2_deploy`（SDK2 + LCM 桥，Docker）。仓库 github.com/NJU-RLC/quadrupedal-agility，提交 15d16ea（2026-08-04）。
- 【评价】选它的理由：正式发表、2026 年、四足**实机**、狗数据、全链路开源，与 Go2-W 同为宇树平台。另外几篇不如它合适：
  - ADD（SIGGRAPH Asia 2025）只在 Go1 仿真上做了速度任务（p8–9 图 6、8）；
  - SMP（TOG 45(4) 2026）实机只有 G1 人形（p12–13 图 11）；
  - Walk Like Dogs 是预印本，未见代码；
  - Multi-AMP（ICRA 2023）年份较旧。
- 【评价】这篇论文的短板：没有报告能耗或 CoT；MPC 基线取自 GitHub 个人实现（文献 55），偏弱；正文没有交代实机重复次数。

**MimicKit 的角色**：【评价】只作**方法实现的参考和基线来源**，提供 AMP/ADD/SMP 代码；**不宜作主底座**。理由见 §2。主底座建议用 robot_lab Go2W（Isaac Lab，可走 rl_sar 部署链，见 [go2w_feasibility](../../05_experiments/go2w_feasibility.CN.md) §1.3–1.4），再把判别器奖励和 Fu 的数据移植进去。

## 2. 复现可行性

| 项目 | 证据 | 结论 |
|---|---|---|
| MimicKit 的 Go2 配置 | 仓库提交 a2c4152（2026-11-18）中有 `data/envs/{deepmimic,amp,add}_go2_env.yaml`、`args/*go2*`；`dataset_go2_locomotion.yaml` 列出 7 段动作（pace/trot/walk0–3/run） | 存在。但 `go2.xml` 与 `.pkl` 动作文件不在 git 里，需从 README 中的 SharePoint 链接下载，**未下载核实** |
| MimicKit Go2 能否直接用 | `amp_go2_agent.yaml:53` 中 `task_reward_weight: 0.0`，即纯模仿、没有速度指令任务（steering 环境只有人形）；grep 不到域随机化、观测噪声或导出代码；控制模式对所有关节统一设置（`newton_engine.py:866–892`，`isaac_lab_engine.py:206–215`） | Go2-W 需要腿走位置控制、轮走速度控制，**必须改引擎**；还要补齐速度任务、域随机化和部署 |
| 判别器输入 | `amp_env.py:336–357` 用全部关节角、机身速度和足端位置 | 正是"轮子会被判为不像"的根源，也就是我们要改的地方 |
| sm_120 | Fu 的代码依赖 Isaac Gym Preview 4 + torch 2.3.1 cu118（README）。NVIDIA 论坛称 Preview 4 的 PhysX 只编译到 SM_80，在 SM_120 上无法运行（[链接](https://forums.developer.nvidia.com/t/isaac-gym-preview-4-incompatible-with-rtx-5080-blackwell-sm-120-libphysxgpu-64-so-missing-sm-120-kernels/367941/2)）。MimicKit 的默认 args 全部指向 Isaac Gym；它的 Isaac Lab 后端按 v3.0.0-EA API 编写，服务器为 Isaac Sim 5.1；Newton 1.6.1 后端在 sm_120 上的表现**未实测** | **两份代码都不能原样运行**。robot_lab v2.3.2 与服务器环境同代，是阻力最小的路线 |
| 实机链 | Fu 有 Go2（12 关节）部署代码；rl_sar 已支持 Go2-W（16 关节）；MimicKit 无部署 | 可行：用 rl_sar 部署 Go2-W，Fu 的观测与估计器设计作参考 |
| 接入 Go2-W 的工作量 | 需要：把 Fu 的数据按 Go2-W 的腿长和轮心重新重定向（两者几何差异**未核实**）、把判别器移植进 robot_lab、做轮/腿混合动作 | 【评价】约 4–6 周可以得到能训练的基线 |

## 3. 查重

**范围**：
- OpenAlex 关键词检索 4 组（wheel-legged × AMP / motion imitation / mocap / motion prior，2022–2026）；
- OpenAlex 施引检索：Multi-AMP 132 条、Escontrela AMP 216 条，按标题中的 wheel/roller/skate 筛选；
- 第四轮网页检索；
- Semantic Scholar 被限流（429），**未完成**。

| 工作 | 状态 | 与本方向的差别 |
|---|---|---|
| Multi-AMP 轮腿（Vollenweider 等，arXiv 2203.14912） | ICRA 2023 | 轮腿 ANYmal 用 AMP，但参考数据由控制器生成、**本身带轮**，不涉及无轮数据 |
| 人形轮滑 AMP（arXiv 2607.10815） | 2026 预印本，仅仿真 | 动捕数据本身就含滑行，不存在形态缺口 |
| 局部 AMP 推车（arXiv 2603.26659） | 2026 预印本 | **判别器只看下半身**的做法已有先例，"只判别腿部特征"不能算方法新意 |
| Fu 等 Nat Commun 2026；Walk Like Dogs（arXiv 2507.00677） | 正式发表 / 预印本 | 狗数据迁移到无轮四足 |
| Learning to Walk and Fly with AMP | IROS 2024 | 机器人多出数据里没有的运动方式，与本方向类似，**全文未读，需补读** |

**结论：部分覆盖。** 检索范围内**没有发现**"无轮动物数据 → 轮足、滚动容许模仿"这一组合。但其中的组件（局部特征判别器、轮腿 AMP）已经存在，新意在于问题定义和轮足适配，不是新算法。这不等于"没有人做过"。

## 4. 致命风险与判断

1. **应用价值**：轮子滚动时腿基本不动，"狗的步态风格"只在迈步或混合步态时才有意义。按 Bjelonic 的结果，混合步态只在部分速度区间省能，所以"像狗"有可能让 CoT 变差。CoT 必须事先定为主指标，并接受负结果。
2. **软件栈**：Fu 的代码和 MimicKit 默认配置都基于 Isaac Gym，不能在 sm_120 上运行，必须移植。
3. **重定向**：Go2-W 足端是轮，Fu 的 Go2 数据需要重新映射。
4. **抢先**：局部 AMP 已有先例；Go2-W 和动物模仿都是热点。
5. **实机**：rl_sar #178 报告过 Go2-W 策略剧烈抖动。

**判断：有条件可行。** 依据：基础论文正式发表且全链路开源，实机部署链存在，查重显示问题组合尚空。条件有三个：
- 第 2 周前在服务器上用 robot_lab Go2W 跑通带判别器奖励的训练（关卡）；
- 事先写定价值指标：与纯 RL 的 Go2W 在相同速度下比 CoT，并设一个风格确实有用的混合任务（如边滚动边跨越低障碍）；
- 确认 Go2-W 的腿部几何后，完成重定向。

【评价】初步评分 **5.5/10**：低于 PACE 方案（7/10），主要扣在应用价值论证和"组件已有"两点。
