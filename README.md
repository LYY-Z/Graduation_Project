# 轮足机器人学习运动控制：毕业设计工作区

面向 Unitree Go2-W 轮足机器人，研究学习驱动的运动控制。路线：基础论文复现 → 改进创新 → 对比与消融 → 实机验证 → 论文。

## 当前阶段

| 项目 | 状态 |
|---|---|
| 基础论文 | **GRAM**（IEEE RA-L 2026，鲁棒适应模块） |
| 拟议方向 | 选择性鲁棒适应（按部件分组判断可信度）+ 轮腿冗余容错 |
| 正在做 | GRAM 精读；服务器上复现论文表 III（第一批训练进行中） |
| 详细状态与决策记录 | [STATUS.CN.md](STATUS.CN.md)（接手先读） |

## 我想找……去哪里

| 我想…… | 去这里 |
|---|---|
| 看当前进度、做过哪些决定 | [STATUS.CN.md](STATUS.CN.md) |
| 看给老师的选题调研汇报 | [06_reports/topic_selection/report.CN.md](06_reports/topic_selection/report.CN.md) |
| 系统学习 GRAM（论文 + 代码） | [02_learning/gram/README.md](02_learning/gram/README.md) |
| 准备和老师讨论 GRAM | [02_learning/gram/06_teacher_qa.CN.md](02_learning/gram/06_teacher_qa.CN.md) |
| 看 GRAM 复现进度和参数核对 | [05_experiments/gram_reproduction.CN.md](05_experiments/gram_reproduction.CN.md) |
| 学怎么登录和使用服务器 | [02_learning/platform/server_guide.CN.md](02_learning/platform/server_guide.CN.md) |
| 看服务器硬件和已有环境 | [05_experiments/server/inventory.CN.md](05_experiments/server/inventory.CN.md) |
| 看 Go2-W 硬件、接口 | [02_learning/platform/README.md](02_learning/platform/README.md) |
| 看论文 PDF 原文 | [01_papers/README.md](01_papers/README.md) |
| 看调研过的论文、筛选和查重记录 | [04_research/README.md](04_research/README.md) |
| 看为什么选 GRAM（选题决策） | [04_research/decision_memo.CN.md](04_research/decision_memo.CN.md) |
| 回答"学习控制比传统控制好在哪" | [04_research/learning_vs_model_based.CN.md](04_research/learning_vs_model_based.CN.md) |
| 看实机实验需要的条件（吊架、场地） | [05_experiments/lab_requirements.CN.md](05_experiments/lab_requirements.CN.md) |
| 找旧材料 | [99_archive/README.md](99_archive/README.md) |

## 目录结构

```text
README.md          本页：总导航
STATUS.CN.md       当前状态、决定、下一步、决策日志
AGENTS.md          协作规则
01_papers/         论文原文 PDF、补充材料、视频（只放原始资料，不改动）
02_learning/       学习讲解：论文精读、代码逐行讲解、平台与服务器使用
  ├─ gram/           ★ 当前主线：GRAM 学习手册（论文、实验、代码、问答、复现）
  ├─ platform/       Go2-W 硬件、接口、服务器入门、VNC
  └─ locoformer/ diffusion_policy/ flair/   历史学习资料（已不在主线）
03_code/           本地保存的代码（GRAM 代码在服务器上，不在这里）
04_research/       选题调研：决策备忘、证据卡、粗筛、查重、文献审查
05_experiments/    实验记录：服务器、复现、可行性核查、实机条件
06_reports/        汇报材料：选题汇报（当前）与历史汇报 PPT、讲稿
99_archive/        历史归档压缩包与整理记录
```

## 文件命名约定

| 约定 | 含义 |
|---|---|
| `*.CN.md` / `*.EN.md` | 中文 / 英文正文 |
| 文件名、目录名 | 用英文；正文以中文为主 |
| `README.md` | 每个目录的索引页，说明本目录放什么、从哪里开始看 |
| 同一主题 | 只维护一份当前主文档，不另建"最终版""最新版"副本 |

## 安全提醒

不提交密码、密钥、`.env`、环境目录、缓存和大型权重；服务器密码只在连接时临时提供，不写入任何文件。
