# 代码 01：项目结构与运行流程

> 这一篇回答三个问题：
> 1. 仓库里每个文件是干什么的？
> 2. 它依赖的 Isaac Sim、Isaac Lab、rsl_rl 分别是什么？
> 3. 敲下 `python -u -m source.train --alg_name gram --id_context default` 回车之后，从启动到训练结束，**按时间顺序**发生了什么？
>
> 看完这篇，再去读 `code/02`（环境）、`code/03`（网络）、`code/05`（PPO 与存储）等细节文件，就知道每个零件装在整机的哪个位置。
>
> 行号以官方原版为准（MERL 仓库，Isaac Lab v1.0.0）。标注：**【代码事实】** 读代码所得；**【推断】** 根据代码和依赖库的默认行为推出，未逐项运行核实；**【新版】** 服务器上 Isaac Lab 0.54.2 的对应名称。
>
> Python 和 PyTorch 语法不熟的地方，先看 [code/00 基础](00_python_pytorch_basics.CN.md)。

---

## 目录

1. 先看全局：一张图
2. 仓库里每个目录和文件
3. 依赖：Isaac Sim、Isaac Lab、rsl_rl、gymnasium
4. Isaac Lab 的"管理器式环境"是什么
5. 从回车到训练结束：按时间顺序的完整过程
6. `source/launcher.py` 逐行讲解
7. `source/train.py` 逐行讲解
8. `source/eval.py` 逐行讲解（和 train 的不同之处）
9. `source/utils/cli_utils.py` 逐函数讲解
   - 9.1 `create_parser`：全部命令行参数分组列表
   - 9.2 `parse_custom_inputs_cfg`：环境配置怎么被命令行覆盖
   - 9.3 `set_adversary_magnitude_by_alg`
   - 9.4 `update_agent_cfg_by_alg`：六种算法逐分支讲解
   - 9.5 `parse_agent_cfg`：算法配置怎么被命令行覆盖
10. 六种算法开关总表
11. 调用链总图
12. 运行后会产出什么文件
13. 常用命令手册
14. 新旧版本命名对照
15. 自测题

---

## 1. 先看全局：一张图

```
命令行  python -u -m source.train --alg_name gram --id_context default
   │
   ▼
┌──────────────────────── source/train.py ─────────────────────────┐
│ ① 启动仿真器（launcher.py：解析参数 + 启动 Isaac Sim）            │
│ ② 生成并注册"定制 Go2 任务"（envs/：按命令行生成环境配置）        │
│ ③ 读取环境配置 env_cfg、算法配置 agent_cfg（cli_utils.py）        │
│ ④ 固定随机种子，确定日志目录                                      │
│ ⑤ gym.make 创建 4096 个并行 Go2 仿真环境                          │
│ ⑥ 包一层 ContextRslRlVecEnvWrapper：额外提供 26 维上下文 c        │
│ ⑦ 创建 GRAMOnPolicyRunner：内部建网络、PPO、对抗者、数据存储      │
│ ⑧ runner.learn()：10000 次 RL + 5000 次适应模块训练 + 验证集定标   │
│ ⑨ 关闭环境和仿真器                                                │
└───────────────────────────────────────────────────────────────────┘
   │
   ▼
logs/unitree_go2_custom/<时间戳>/  里面有 model_*.pt、TensorBoard 日志、配置 yaml
```

**一句话**：`train.py` 只是"总装车间"，自己几乎不做计算；真正的环境在 `source/envs/`，真正的算法在 `source/algs/gram/`，所有可调参数在 `source/utils/cli_utils.py`。

---

## 2. 仓库里每个目录和文件

官方仓库共约 2150 行 Python（不含依赖库）。

```
gram/
├── README.md                 说明：安装步骤、训练与评估命令示例
├── environment.yaml          conda 环境定义（Python 3.10、PyTorch 2.2.2 + CUDA 11.8 等）
├── LICENSE.md, LICENSES/     开源许可证（BSD-3-Clause）
├── CONTRIBUTING.md           贡献说明
├── .github/ .reuse/ .vscode/ .pre-commit-config.yaml .gitignore   开发辅助配置，和算法无关
└── source/                   ← 全部源代码（是一个 Python 包）
    ├── __init__.py           空文件（只有版权声明），让 source 成为包
    ├── launcher.py           解析命令行参数 + 启动 Isaac Sim（26 行）
    ├── train.py              训练入口（123 行）
    ├── eval.py               评估入口（133 行）
    ├── algs/                 算法
    │   ├── __init__.py       转发：from source.algs.gram import GRAMOnPolicyRunner
    │   └── gram/
    │       ├── __init__.py               转发 GRAMOnPolicyRunner
    │       ├── gram_actor_critic.py      【核心】所有网络：策略、价值、上下文编码器、历史编码器、epinet；α 的计算（741 行）
    │       ├── gram_ppo.py               PPO 更新、对抗者更新、历史编码器（适应模块）的监督训练（646 行）
    │       ├── gram_on_policy_runner.py  训练主循环、鲁棒/适应分配交替、验证集定标、评估（776 行）
    │       ├── gram_adversary.py         对抗者网络（输出推力方向）（154 行）
    │       └── gram_rollout_storage.py   存放一轮收集的数据（含观测历史、上下文、mask）（197 行）
    ├── envs/                 环境
    │   ├── __init__.py       任务清单 CUSTOM_ENVS、两个分发函数
    │   ├── unitree_go2_cfg.py          实验设置的默认值（default / wide 两套 ID 上下文）（133 行）
    │   ├── unitree_go2_custom_env.py   按设置生成 Go2 环境配置和 PPO 配置并注册到 gym（301 行）
    │   ├── envs_utils.py               定制零件：带倍数/偏置/限位的动作项、带强度倍数的电机、摩擦随机化、对抗推力、训练用初始姿态（392 行）
    │   └── context_env_wrapper.py      环境包装器：读取 26 维上下文 c 并归一化到 [−1, 1]（203 行）
    └── utils/
        ├── __init__.py       空
        ├── cli_utils.py      全部命令行参数 + 把参数写进两份配置（763 行）
        └── torch_utils.py    权重初始化函数 weight_init（Xavier）（35 行）
```

**"改哪里"速查**：

| 想改的东西 | 去哪个文件 |
|---|---|
| 训练范围（质量、摩擦、电机强度、零偏） | `envs/unitree_go2_cfg.py` 或命令行 |
| 奖励、地形、执行器、观测项 | `envs/unitree_go2_custom_env.py` |
| 动作怎么变成关节目标、电机强度、推力怎么施加 | `envs/envs_utils.py` |
| 上下文 c 包含哪些量、怎么归一化 | `envs/context_env_wrapper.py` |
| 网络结构、不确定性、α | `algs/gram/gram_actor_critic.py` |
| 损失函数、优化器 | `algs/gram/gram_ppo.py` |
| 训练流程、鲁棒/适应怎么交替、定标 | `algs/gram/gram_on_policy_runner.py` |
| 默认超参数、各算法开关 | `utils/cli_utils.py` |

**哪些文件是从别处改来的**（README 末尾说明）：`launcher.py`、`train.py`、`eval.py`、`envs_utils.py`、`cli_utils.py` 改编自 Isaac Lab；`algs/gram/` 下 5 个文件改编自 rsl_rl。所以读这些文件时，很多"框架代码"和 Isaac Lab / rsl_rl 官方示例长得一样，**真正属于 GRAM 的改动**集中在：上下文、epinet、α、robust_masks、对抗者、finetune 阶段。

---

## 3. 依赖：Isaac Sim、Isaac Lab、rsl_rl、gymnasium

GRAM 是"站在三层框架之上"写的：

```
┌─────────────────────────────────────────────┐
│ GRAM（source/）                              │  本仓库：算法改动 + 定制环境
├─────────────────────────────────────────────┤
│ rsl_rl v2.0.0                                │  ETH 的 PPO 实现：OnPolicyRunner、PPO、ActorCritic
├─────────────────────────────────────────────┤
│ Isaac Lab v1.0.0                             │  机器人学习框架：环境管理器、任务、Go2 配置
├─────────────────────────────────────────────┤
│ Isaac Sim 4.1.0（含 PhysX 物理引擎）         │  NVIDIA 仿真器：GPU 上并行算几千个机器人的物理
├─────────────────────────────────────────────┤
│ PyTorch 2.2.2 + CUDA 11.8                    │  张量计算、神经网络
└─────────────────────────────────────────────┘
```

| 组件 | 是什么 | GRAM 用它做什么 |
|---|---|---|
| **Isaac Sim** | NVIDIA 的机器人仿真器，基于 Omniverse 平台，物理用 PhysX，能在 GPU 上同时仿真几千个机器人 | 提供物理世界。GRAM 的 4096 个 Go2 同时在 GPU 里跑 |
| **Isaac Lab**（前身 Orbit） | 在 Isaac Sim 上搭的机器人学习框架，提供"管理器式环境"、各种机器人和任务的现成配置 | GRAM 继承它自带的 Go2 粗糙地形速度跟踪任务配置，在上面改 |
| **rsl_rl** | ETH Zurich 机器人系统实验室（RSL）写的轻量 PPO 库，Isaac Lab 默认用它训练足式机器人 | GRAM 的 runner、PPO、存储都继承自它，再加 GRAM 的东西 |
| **gymnasium** | 强化学习环境的标准接口（`reset`、`step`），前身是 OpenAI Gym | Isaac Lab 用它的注册表登记任务，`gym.make("任务名")` 创建环境 |

**为什么版本卡得这么死**：Isaac Lab 和 rsl_rl 版本之间的接口变化很大（模块改名、观测改成字典等），GRAM 是按 v1.0.0 + v2.0.0 写的。服务器上的兼容做法是：升级到 Isaac Sim 5.1 + Isaac Lab 0.54.2，但**保留 rsl_rl 2.0.0**，并补一个旧版接口的包装器，GRAM 算法的 7 个文件不改。详见 [07 服务器与复现](../07_server_and_reproduction.CN.md)。

---

## 4. Isaac Lab 的"管理器式环境"是什么

Isaac Lab 把一个强化学习环境拆成若干个**管理器**（manager），每个管理器负责一件事，由配置类里的一个字段描述。GRAM 的环境配置 `UnitreeGo2CustomEnvCfg` 就是在改这些字段。

| 管理器 / 配置字段 | 负责什么 | GRAM 的改动（`unitree_go2_custom_env.py`） |
|---|---|---|
| `scene`（场景） | 有哪些东西：机器人、地形、传感器 | 平地或粗糙/斜坡地形（`:102-154`）；开启自碰撞（`:99-100`）；去掉高度扫描（`:171-173`）；执行器换成 `ScaledDCMotor`（`:192-203`） |
| `actions`（动作） | 网络输出怎么变成对机器人的指令 | 换成 `ShiftScaleClampJointPositionAction`：缩放、加零偏、限位（`:176-189`） |
| `observations`（观测） | 网络能看到什么 | 去掉机身线速度（`:248`）；可关闭观测噪声（`:250-251`） |
| `rewards`（奖励） | 每一步怎么打分 | 改权重、加机身高度和非期望接触惩罚（`:254-276`）；评估时只保留跟踪奖励（`:283-287`） |
| `terminations`（终止） | 什么情况下回合结束 | 评估时，机身/髋/大腿/头部碰地即终止（`:289-292`） |
| `events`（事件） | 随机化和扰动，分 `startup`（启动时一次）、`reset`（每次重置）、`interval`（定期） | 加质量（`:213`）、摩擦随机化（`:215-226`，startup）、对抗推力（`:205-210`，interval）、训练用随机初始姿态（`:231-240`，reset） |
| `commands`（指令） | 给机器人的目标，如目标速度 | 速度范围、航向范围、重采样时间、站立环境比例（`:243-246`） |
| `curriculum`（课程） | 随训练进度调整难度 | 关掉地形课程（`:103-104`） |

**时间关系**【推断，继承 Isaac Lab Go2 配置，和论文一致】：
- 物理步长 `sim.dt = 0.005 s`（200 Hz），PD 控制器在每个物理步都算一次力矩；
- `decimation = 4`：策略每 4 个物理步做一次决策，即 **50 Hz**；
- 回合最长 20 s，即 **1000 个策略步**。

**一次 `env.step(actions)` 内部大致做了什么**【推断，Isaac Lab 管理器式环境的标准流程】：

```
1. 动作管理器：把 12 维网络输出 → 12 个关节目标角（缩放 0.25、加默认姿态、加零偏、限位）
2. 重复 4 次（decimation）：
     执行器：PD 算力矩 τ = Kp(q目标 − q) − Kd·q̇，乘电机强度倍数，限幅 23.5 N·m
     PhysX 前进 0.005 s
3. 更新传感器、指令
4. 奖励管理器：算这一步的奖励
5. 终止管理器：判断哪些环境要结束
6. 对结束的环境：事件管理器执行 reset 事件，重新随机初始化
7. interval 事件：如对抗推力
8. 观测管理器：拼出新的观测（加噪声）
返回 (obs, reward, done, info)
```

**"一次迭代"和"一步"的区别**（读日志时容易混）：
- **一步**（step）：每个环境走 1/50 秒。
- **一次迭代**（iteration）：每个环境走 `num_steps_per_env` 步（【推断】Isaac Lab Go2 默认 24 步），收集完数据后做一次 PPO 更新。4096 环境 × 24 步 = 98,304 条数据 / 迭代。
- 论文的"10,000 次更新"就是 10,000 次迭代。

---

## 5. 从回车到训练结束：按时间顺序的完整过程

以 `python -u -m source.train --alg_name gram --id_context default` 为例。

| 阶段 | 发生了什么 | 代码位置 |
|---|---|---|
| 0 | Python 以模块方式运行 `source/train.py`，执行到 `if __name__ == "__main__":`，调用 `train()` | `train.py:119-121` |
| 1 | `train()` 第一行 `from source.launcher import ...`，触发 `launcher.py` 被执行 | `train.py:16` |
| 1.1 | 建参数解析器，加入 GRAM 的约 150 个参数 | `launcher.py:14` → `cli_utils.py:14-352` |
| 1.2 | 再加入 Isaac Sim 启动器自己的参数（如 `--headless`、`--device`） | `launcher.py:16` |
| 1.3 | 解析命令行，得到 `args_cli` | `launcher.py:17` |
| 1.4 | 强制无界面模式 | `launcher.py:19` |
| 1.5 | **启动 Isaac Sim**（这一步要十几秒到一分钟，会打印大量 Kit 日志） | `launcher.py:25-26` |
| 2 | Isaac Sim 启动后，才 import Isaac Lab、gymnasium、torch 等 | `train.py:20-37` |
| 2.1 | `import omni.isaac.lab_tasks`：Isaac Lab 自带任务全部登记到 gym 注册表 | `train.py:26` |
| 3 | 设置 TF32 等 GPU 计算选项 | `train.py:39-42` |
| 4 | 生成实验设置：从 `default` 配置开始，用命令行覆盖 | `train.py:46` → `cli_utils.py:355-526` |
| 5 | 按实验设置生成 Go2 环境配置类和 PPO 配置类，登记成任务 `Isaac-Velocity-Custom-Unitree-Go2-v0` | `train.py:47` → `envs/__init__.py:26` → `unitree_go2_custom_env.py:37-301` |
| 6 | 从注册表取出环境配置，设 `num_envs=4096` | `train.py:50-52` |
| 7 | 从注册表取出 PPO 配置，再按算法名和命令行改写 | `train.py:53` → `cli_utils.py:625-763` |
| 8 | 固定 Python、NumPy、PyTorch 的随机种子（默认 1） | `train.py:56-59` |
| 9 | 确定日志目录 `logs/unitree_go2_custom/<时间戳>[_run_name]` | `train.py:62-69` |
| 10 | `gym.make(...)`：**真正在 GPU 上创建 4096 个 Go2 和地形**（要一些时间） | `train.py:72` |
| 11 | 可选：包一层录像 | `train.py:74-83` |
| 12 | 包一层 `ContextRslRlVecEnvWrapper`：读出每个环境的 26 维上下文 c | `train.py:85` → `context_env_wrapper.py` |
| 13 | 创建 `GRAMOnPolicyRunner`：建 `GRAMActorCritic`（全部网络）、`GRAMPPO`（三个优化器）、`GRAMAdversary`、数据存储 | `train.py:88` → `gram_on_policy_runner.py:32-132` |
| 14 | 记录 git 状态（便于以后知道用的是哪版代码） | `train.py:90` |
| 15 | 如果指定了 `--load_run`，加载旧模型继续训练 | `train.py:92-98` |
| 16 | 环境随机种子 | `train.py:101` |
| 17 | 把两份配置存成 yaml | `train.py:104-105` |
| 18 | **`runner.learn(10000)`：训练主循环**（见下） | `train.py:111` |
| 19 | 关闭环境；`train()` 返回后关闭仿真器 | `train.py:114,123` |

**第 18 步 `runner.learn` 内部的时间线**【代码事实，`gram_on_policy_runner.py:221-380`】：

```
迭代 0 ~ 9999（RL 阶段，共 10000 次）
  每次迭代：
    - 所有环境的 robust_mask 翻转（0↔1），一半做适应训练、一半做鲁棒训练
    - 每个环境走 num_steps_per_env 步，收集数据
        适应组：策略输入 [观测, z = f(c)]
        鲁棒组：策略输入 [观测, 0]，对抗者以 5% 概率推机身
    - PPO 更新：策略、价值、上下文编码器
    - 每 10 次迭代更新一次对抗者；推力强度随进度从 0 线性增到 1
    - 迭代号是 5000 的倍数时保存 model_<迭代号>.pt

迭代 10000：进入 FINETUNE 阶段
    - 策略改用历史编码器的估计（act_from_context = False）
    - 关闭对抗者
    - 观测归一化统计冻结
    - 保存一次 model_10000.pt（进入 finetune 前的快照）

迭代 10000 ~ 14999（适应模块训练，共 5000 次）
    - 仍然收集数据（策略输入来自历史编码器）
    - 只训练历史编码器 + epinet（监督回归 f(c)），策略不再更新

循环结束后：
    - collect_validation_data()：在 ID 环境里跑一遍，收集不确定性 ‖σ̂‖²，算 101 个分位数，存进模型
    - 保存最终模型 model_14999.pt   ← 评估要用的就是它
```

细节见 code 目录中讲 runner 和 PPO 的文件（`05_ppo_and_storage.CN.md` 等）。

---

## 6. `source/launcher.py` 逐行讲解

**这段代码要干什么**：解析命令行参数，并启动 Isaac Sim。它很短，但有一个关键设计：**把"启动仿真器"放在一个单独模块的顶层代码里**，谁 import 它，谁就触发启动。

```python
"""Create parser and launch Isaac Sim Simulator."""


from omni.isaac.lab.app import AppLauncher                 # :9

from source.utils.cli_utils import create_parser           # :11

# create parser
parser = create_parser()                                    # :14
# append AppLauncher cli args
AppLauncher.add_app_launcher_args(parser)                   # :16
args_cli = parser.parse_args()                              # :17
# always run in headless mode
args_cli.headless = True                                    # :19
# always enable cameras to record video
if args_cli.video:                                          # :21
    args_cli.enable_cameras = True                          # :22

# launch omniverse app
app_launcher = AppLauncher(args_cli)                        # :25
simulation_app = app_launcher.app                           # :26
```

**逐行解释**：
- `:9` `AppLauncher`：Isaac Lab 提供的"仿真器启动器"。这是**唯一**能在 Isaac Sim 启动之前 import 的 Isaac Lab 模块。【新版】`from isaaclab.app import AppLauncher`。
- `:11` 导入 GRAM 自己的参数定义函数。`cli_utils.py` 顶部只 import 了 `argparse`，没有依赖仿真器，所以可以提前导入。
- `:14` 建解析器，登记 GRAM 的全部参数（第 9.1 节）。
- `:16` 再登记 AppLauncher 自己的参数，如 `--headless`、`--device`、`--enable_cameras`、`--kit_args` 等。【新版】新版 AppLauncher 自己已经定义了 `--cpu` 等参数，和 GRAM 的 `--cpu`（`cli_utils.py:23`）重名，会报"参数冲突"，服务器兼容版删掉了 GRAM 这一个重复参数。
- `:17` 解析命令行。
- `:19` **强制无界面**：不管命令行写了什么，都不开图形窗口。服务器没有显示器，训练也不需要画面。
- `:21-22` 如果要录像，必须开启相机渲染。
- `:25-26` **启动 Isaac Sim**。`simulation_app` 是仿真器应用对象，最后要调用它的 `.close()` 关闭。

**为什么必须先启动仿真器再 import 其他模块**：Isaac Lab 的大部分模块底层依赖 Omniverse 的扩展（`omni.*`、`pxr` 等），这些扩展只有在 Isaac Sim 应用启动后才会被加载到 Python 路径里。提前 import 会报 `ModuleNotFoundError`。所以 GRAM 的 `train.py`、`eval.py` 把所有 Isaac Lab 相关的 import 都写在函数内部、`launcher` 之后。

**数值例子**：命令 `python -m source.train --num_envs 16 --device cuda:0` 解析后：`args_cli.num_envs = 16`、`args_cli.device = "cuda:0"`（AppLauncher 参数）、`args_cli.headless = True`（被第 19 行强制）。

**小结**：`launcher.py` = 解析参数 + 启动仿真器；它被 import 的那一刻就会启动 Isaac Sim。

---

## 7. `source/train.py` 逐行讲解

**这段代码要干什么**：把环境、配置、runner 组装起来，然后开始训练。

### 7.1 第 11-18 行：两种启动方式

```python
def train(launcher=None):
    """Train agent."""

    # Load
    if launcher is None:
        from source.launcher import args_cli, simulation_app
    else:
        simulation_app, args_cli = launcher
```

- 正常命令行运行时 `launcher=None`，执行 `from source.launcher import ...`，触发第 6 节的启动过程，拿到 `args_cli` 和 `simulation_app`。
- 也可以由别的脚本先启动好仿真器，再把 `(simulation_app, args_cli)` 传进来，避免重复启动。【推断】这是为了在一个进程里连续跑多个任务（比如训练完接着评估），官方仓库里没有用到。

### 7.2 第 20-37 行：仿真器启动后才 import

```python
    import os
    import random
    from datetime import datetime

    import gymnasium as gym
    import numpy as np
    import omni.isaac.lab_tasks
    import torch
    from omni.isaac.lab.envs import ManagerBasedRLEnvCfg
    from omni.isaac.lab.utils.dict import print_dict
    from omni.isaac.lab.utils.io import dump_yaml
    from omni.isaac.lab_tasks.utils import get_checkpoint_path, parse_env_cfg
    from omni.isaac.lab_tasks.utils.wrappers.rsl_rl import RslRlOnPolicyRunnerCfg

    from source.algs import GRAMOnPolicyRunner
    from source.envs import CUSTOM_ENVS, create_custom_env
    from source.envs.context_env_wrapper import ContextRslRlVecEnvWrapper
    from source.utils.cli_utils import parse_agent_cfg, parse_custom_inputs_cfg
```

| 导入 | 用途 |
|---|---|
| `os`、`random`、`datetime` | 路径拼接、Python 随机种子、生成时间戳目录名 |
| `gymnasium as gym` | `gym.make` 创建环境、`gym.wrappers.RecordVideo` 录像 |
| `numpy as np` | NumPy 随机种子 |
| `omni.isaac.lab_tasks` | **只为副作用**：登记 Isaac Lab 自带的全部任务，GRAM 要继承其中的 Go2 配置 |
| `torch` | 设置 GPU 计算选项、随机种子 |
| `ManagerBasedRLEnvCfg` | 只用于类型标注（`env_cfg: ManagerBasedRLEnvCfg = ...`），方便阅读 |
| `print_dict` | 打印字典 |
| `dump_yaml` | 把配置存成 yaml 文件 |
| `get_checkpoint_path` | 根据 run 名找到要加载的 `.pt` 文件 |
| `parse_env_cfg` | 从注册表取出环境配置并设置环境数量等 |
| `RslRlOnPolicyRunnerCfg` | 只用于类型标注 |
| `GRAMOnPolicyRunner` 等 4 行 | GRAM 自己的模块 |

【新版】`omni.isaac.lab` → `isaaclab`；`omni.isaac.lab_tasks` → `isaaclab_tasks`；`omni.isaac.lab_tasks.utils.wrappers.rsl_rl` → `isaaclab_rl.rsl_rl`。服务器兼容版另外放了一个从 v1.0.0 拷来的包装器 `source/compat/rsl_rl_vecenv_v1.py`，以保持 rsl_rl 2.0 的接口。

### 7.3 第 39-42 行：GPU 计算选项

```python
    torch.backends.cuda.matmul.allow_tf32 = True
    torch.backends.cudnn.allow_tf32 = True
    torch.backends.cudnn.deterministic = False
    torch.backends.cudnn.benchmark = False
```

- **TF32**：NVIDIA Ampere 及以后的显卡支持的一种矩阵乘法格式，精度比 float32 略低（有效位 10 位），但快很多。开了对强化学习几乎没影响。
- `cudnn.deterministic = False`：不强制每次结果完全一致（强制会变慢）。
- `cudnn.benchmark = False`：不自动搜索最快卷积算法。GRAM 没有卷积层，这项无实际影响。

### 7.4 第 44-47 行：生成并注册定制任务

```python
    # create custom task
    if args_cli.task in CUSTOM_ENVS:
        train_inputs_cfg = parse_custom_inputs_cfg(args_cli.task, args_cli.id_context, args_cli, eval_mode=False)
        create_custom_env(args_cli.task, **train_inputs_cfg.to_dict())
```

- `args_cli.task` 默认是 `"Isaac-Velocity-Custom-Unitree-Go2-v0"`（`cli_utils.py:52`），在 `CUSTOM_ENVS` 列表里（`envs/__init__.py:12-14`）。
- `parse_custom_inputs_cfg(..., eval_mode=False)`：从 `default`（或 `wide`）配置开始，用命令行覆盖，得到"实验设置"对象 `train_inputs_cfg`（第 9.2 节）。
- `create_custom_env(task, **字典)`：把实验设置拆成关键字参数，交给 `create_unitree_go2_custom_env`，在函数里现场生成环境配置类并 `gym.register` 登记（见 code/00 的 1.6 节"闭包"）。

**数值例子**：命令行没写任何环境参数时，`train_inputs_cfg.base_mass_min = -1.0`、`base_mass_max = 3.0`、`friction_mult_min = 0.05`、`friction_mult_max = 4.5`、`motor_strength_mult_min = 0.8`、`motor_strength_mult_max = 1.2`、`adversary_magnitude = 1.0`（由 9.3 节的函数按算法设定）。

### 7.5 第 49-53 行：取出两份配置

```python
    env_cfg: ManagerBasedRLEnvCfg = parse_env_cfg(
        args_cli.task, use_gpu=not args_cli.cpu, num_envs=args_cli.num_envs, use_fabric=not args_cli.disable_fabric
    )
    agent_cfg: RslRlOnPolicyRunnerCfg = parse_agent_cfg(args_cli.task, args_cli, eval_mode=False)
```

- `parse_env_cfg`：从注册表按任务名找到 `UnitreeGo2CustomEnvCfg`，实例化，并设置在 GPU 上运行、环境数 4096、启用 Fabric（Omniverse 的高速数据接口，比直接读写 USD 场景文件快）。【新版】参数名改为 `device=...`，不再有 `use_gpu`。
- `parse_agent_cfg`：从注册表取出 `UnitreeGo2CustomPPORunnerCfg`，再按算法名和命令行改写（第 9.4、9.5 节）。

**两份配置的分工**：

| 配置 | 类型 | 管什么 |
|---|---|---|
| `env_cfg` | `UnitreeGo2CustomEnvCfg` | 环境：场景、动作、观测、奖励、事件…… |
| `agent_cfg` | `UnitreeGo2CustomPPORunnerCfg` | 算法：网络大小、PPO 超参、GRAM 开关、迭代次数、日志 |
| `train_inputs_cfg` | `UnitreeGo2CustomDefaultIDCfg` | 实验设置的"原始参数表"，用来生成 `env_cfg`，也交给上下文包装器 |

### 7.6 第 55-69 行：种子与日志目录

```python
    random.seed(agent_cfg.seed)
    np.random.seed(agent_cfg.seed)
    torch.manual_seed(agent_cfg.seed)
    torch.cuda.manual_seed(agent_cfg.seed)

    log_root_path = os.path.join("logs", agent_cfg.experiment_name)
    log_root_path = os.path.abspath(log_root_path)
    print(f"[INFO] Logging experiment in directory: {log_root_path}")
    log_dir = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    if agent_cfg.run_name:
        log_dir += f"_{agent_cfg.run_name}"
    log_dir = os.path.join(log_root_path, log_dir)
```

- 四个随机数源都用同一个种子（默认 `--seed 1`）。**要做多种子实验，就改 `--seed`**。
- 日志根目录：`logs/` + `experiment_name`。`experiment_name` 在 `unitree_go2_custom_env.py:88` 设为 `"unitree_go2_custom"`（命令行 `--experiment_name` 在 `cli_utils.py:32` 定义，但【代码事实】`parse_agent_cfg` 里并没有把它写进 `agent_cfg`，所以命令行改不了它）。
- `os.path.abspath`：相对路径变绝对路径。`logs/` 是相对于**当前工作目录**的，所以在仓库根目录运行时，日志就在 `gram/logs/` 下。
- 运行目录名：时间戳，如 `2026-11-26_16-59-53`，有 `--run_name compat16` 时变成 `2026-11-26_16-59-53_compat16`。

### 7.7 第 71-85 行：创建环境

```python
    env = gym.make(args_cli.task, cfg=env_cfg, render_mode="rgb_array" if args_cli.video else None)
    if args_cli.video:
        video_kwargs = {
            "video_folder": os.path.join(log_dir, "videos"),
            "step_trigger": lambda step: step % args_cli.video_interval == 0,
            "video_length": args_cli.video_length,
            "disable_logger": True,
        }
        ...
        env = gym.wrappers.RecordVideo(env, **video_kwargs)
    env = ContextRslRlVecEnvWrapper(env, train_inputs_cfg)
```

- `gym.make(任务名, cfg=env_cfg)`：按注册信息里的 `entry_point="omni.isaac.lab.envs:ManagerBasedRLEnv"`（`unitree_go2_custom_env.py:298`）创建 Isaac Lab 的管理器式环境，在 GPU 里生成 4096 个机器人。
- 录像：每 2000 步（`--video_interval` 默认）录 200 步（`--video_length` 默认）。`lambda step: ...` 是一个匿名函数，判断第几步开始录。
- **包装器**（wrapper）：在原环境外面再套一层，增加或改变接口，就像给手机套壳。
  - `ContextRslRlVecEnvWrapper`（`envs/context_env_wrapper.py`）继承自 Isaac Lab 的 `RslRlVecEnvWrapper`（把 Isaac Lab 环境转成 rsl_rl 要的接口），**额外**在构造时读出每个环境的上下文 c，提供 `get_context()`。
  - 26 维 c 的组成：附加质量 1 + 摩擦 1 + 电机强度 12 + 关节零偏 12。每一项都线性映射到 [−1, 1]：例如质量范围 [−1, 3] kg 中，−1 kg → −1，1 kg → 0，3 kg → +1（`context_env_wrapper.py:125-127` 等）。
  - 【代码事实】c 只在包装器构造时读一次（`__init__` 里调用 `_set_context`），之后不再更新。这和"质量、摩擦、电机强度都只在启动时随机一次"是对应的，也是"仓库没有运行中变化"的根源。详见 code/02。

### 7.8 第 87-98 行：创建 runner，可选加载

```python
    runner = GRAMOnPolicyRunner(env, agent_cfg.to_dict(), log_dir=log_dir, device=agent_cfg.device)
    runner.add_git_repo_to_log(__file__)
    if agent_cfg.resume:
        resume_path = get_checkpoint_path(log_root_path, agent_cfg.load_run, agent_cfg.load_checkpoint)
        print(f"[INFO]: Loading model checkpoint from: {resume_path}")
        runner.load(resume_path)
```

- `agent_cfg.to_dict()`：配置类变成嵌套字典，runner 内部按键取用。
- `GRAMOnPolicyRunner.__init__`（`gram_on_policy_runner.py:32-132`）里做的事：
  1. 从包装器取上下文 c（4096 × 26）、观测维数；
  2. 用 `eval("GRAMActorCritic")` 建全部网络，搬到 GPU；
  3. 用 `eval("GRAMPPO")` 建 PPO 算法（含三个 Adam 优化器）；
  4. 建观测归一化器；
  5. 建数据存储（`init_storage`）；
  6. 建对抗者网络，连同上下文、环境等交给 PPO（`init_extras`）。
- `add_git_repo_to_log(__file__)`：登记要记录 git 状态的代码仓库，第一次迭代时把 `git diff` 存进日志目录，便于以后追溯"这次训练用的是哪版代码"。
- `resume`：只有命令行给了 `--load_run` 时才为 True（`cli_utils.py:639-643`）。`get_checkpoint_path` 在 `logs/unitree_go2_custom/<load_run>/` 下按 `load_checkpoint` 的模式找文件。【推断】默认模式是 `model_.*.pt`，取排序后最后一个，即迭代号最大的那个。

### 7.9 第 100-116 行：保存配置、训练、关闭

```python
    env.seed(agent_cfg.seed)

    dump_yaml(os.path.join(log_dir, "params", "env.yaml"), env_cfg)
    dump_yaml(os.path.join(log_dir, "params", "agent.yaml"), agent_cfg)

    if args_cli.calculate_validation_metrics_only:
        runner.calculate_and_save_validation_metrics()
    else:
        runner.learn(num_learning_iterations=agent_cfg.max_iterations, init_at_random_ep_len=True)

    env.close()

    return simulation_app
```

- `dump_yaml`：把两份完整配置存成 yaml。**复现时一定要看这两个文件**，它们记录了所有实际生效的参数，包括从 Isaac Lab 继承来的默认值。
- `--calculate_validation_metrics_only`：不训练，只对加载的模型重新收集验证集、重算分位数并保存（`gram_on_policy_runner.py:471-495`）。用于"模型已训好，只想换定标方式"。
- `runner.learn(..., init_at_random_ep_len=True)`：开始训练。`init_at_random_ep_len=True` 让 4096 个环境的"回合已进行时间"随机错开（`gram_on_policy_runner.py:242-245`），避免所有环境同时重置，数据更平稳。
- `max_iterations` 默认 10000，这只是 **RL 阶段**的次数；finetune 的 5000 次在 runner 内部另加（`tot_iter = start_iter + num_learning_iterations + self.finetune_iterations`，`:276`）。

### 7.10 第 119-123 行

```python
if __name__ == "__main__":
    simulation_app = train()
    simulation_app.close()
```

直接运行时执行训练，最后关闭仿真器。不调用 `close()`，进程可能挂住不退出。

**小结**：`train.py` 的 9 个动作：启动 → 生成任务 → 取配置 → 种子与目录 → 建环境 → 包上下文 → 建 runner → 训练 → 关闭。

---

## 8. `source/eval.py` 逐行讲解（和 train 的不同之处）

**这段代码要干什么**：加载训练好的模型，在指定场景下（如 9 kg、10° 坡）跑一个完整回合，统计回报和 α，存成 pickle 文件。

`eval.py` 和 `train.py` 结构几乎一样，下面只讲不同之处。

| 位置 | train.py | eval.py | 含义 |
|---|---|---|---|
| `:46` | `eval_mode=False` | `eval_mode=True` | 实验设置进入评估模式（第 9.2 节）：固定指令、关推力、只留跟踪奖励等 |
| `:49-50` | 无 | `else: eval_inputs_dict = dict()` | 非定制任务时给空字典 |
| `:56` | `eval_mode=False` | `eval_mode=True` | 算法配置进入评估模式（第 9.4 节）：改用历史编码器、开 α 等 |
| `:67-77` | 日志在 `<时间戳>/` | 有 `--load_run` 时日志在 `<load_run>/eval/` | 评估结果放在被评估模型的目录下 |
| `:108-109` | 无 | 没给 `--load_run` 时打印警告 | 会评估一个**未训练**的模型，结果无意义 |
| `:115` | `runner.learn(...)` | `runner.evaluate(eval_inputs_dict, deterministic=...)` | 不训练，只评估 |
| `:118-121` | 存 yaml | `dump_pickle(.../eval_<run_name>, eval_log)` | 存评估结果 |

**第 115 行 `deterministic=(not args_cli.stochastic_eval)`**：默认用**确定性动作**（取高斯分布的均值，不抽样），加 `--stochastic_eval` 才抽样。

**`runner.evaluate` 做了什么**【代码事实，`gram_on_policy_runner.py:618-776`】：
1. 切换到评估模式；
2. `env.reset()`，从头开始；
3. 跑满一个回合的最大步数（1000 步），每一步：
   - 记录 α 和不确定性（仅 GRAM 类算法，`:645-653`）；
   - `act_inference` 出动作；
   - `env.step`；
   - 累加奖励，**只累加"还活着"的环境**（`total_rewards += rewards * alive`，`:673`）；摔倒后 `alive` 变 0，之后不再计分；
4. 打包结果：

```python
        eval_log = {
            "params": eval_inputs_dict,                        # 本次评估的全部场景参数
            "returns": total_rewards.numpy(force=True),        # 每个环境的总回报，形状 (num_envs,)
            "episode_length": total_steps.numpy(force=True),   # 每个环境活了多少步
        }
        if self.alg.actor_critic.history_epinet:
            alpha_ave = torch.sum(alpha * alive_mask, dim=-1) / torch.sum(alive_mask, dim=-1)
            eval_log["alpha"] = alpha_ave.numpy(force=True)    # 每个环境存活期间的平均 α
```

加 `--save_eval_detailed` 还会存逐步的存活掩码、α、不确定性等（`:756-768`）；加 `--print_stats` 会在终端打印 α 和不确定性的分位数（服务器冒烟测试日志里那串 `Q01 … Q99` 就是它）。

**论文的"归一化回报"怎么从这里得到**【推断】：评估模式下只剩两项跟踪奖励（线速度权重 1.0、角速度权重 0.5）。若每步奖励按 Isaac Lab 惯例乘以策略步长 0.02 s，则每步满分 (1.0 + 0.5) × 0.02 = 0.03，1000 步满分 30。论文的 [0, 1] 归一化很可能就是 `returns / 30`。仓库里**没有**归一化和画图的脚本，需要自己写，并先核对奖励是否乘了步长。

**小结**：`eval.py` = 加载模型 + 评估模式的环境 + 跑一个回合 + 存 pickle；回报只统计跟踪奖励，摔倒后停止计分。

---

## 9. `source/utils/cli_utils.py` 逐函数讲解

这个文件有 5 个函数：

| 函数 | 行号 | 作用 |
|---|---|---|
| `create_parser` | `:14-352` | 定义全部命令行参数 |
| `parse_custom_inputs_cfg` | `:355-526` | 生成"实验设置"（环境侧），用命令行覆盖默认值 |
| `set_adversary_magnitude_by_alg` | `:529-539` | 按算法决定推力强度 |
| `update_agent_cfg_by_alg` | `:542-622` | 按算法名设置 GRAM 的各种开关 |
| `parse_agent_cfg` | `:625-763` | 生成算法配置，用命令行覆盖 |

### 9.1 `create_parser`：全部命令行参数

下面按代码里的分组逐一列出。"默认"一栏为 `None` 的，表示"不覆盖配置文件里的值"；开关型（`store_true`）默认 False。

#### (1) 通用参数（`:18-45`，基本照搬 Isaac Lab 示例）

| 参数 | 默认 | 含义 |
|---|---|---|
| `--video` | False | 训练中录像 |
| `--video_length` | 200 | 每段录像多少步 |
| `--video_interval` | 2000 | 每隔多少步录一段 |
| `--cpu` | False | 用 CPU 跑仿真（极慢，基本不用）【新版】与 AppLauncher 参数冲突，兼容版已删 |
| `--disable_fabric` | False | 关闭 Fabric，改用 USD 读写（慢，调试用） |
| `--num_envs` | **4096** | 并行环境数。冒烟测试用 16 |
| `--seed` | **1** | 随机种子 |
| `--max_iterations` | **10000** | RL 阶段迭代次数（不含 finetune） |
| `--experiment_name` | None | 实验文件夹名（【代码事实】未被写入配置，不生效） |
| `--run_name` | None | 运行目录名后缀 |
| `--load_run` | None | 加载哪个运行目录的模型（给了就 `resume=True`） |
| `--checkpoint` | None | 加载哪个 `.pt` 文件（可写文件名或模式） |
| `--logger` | None | `tensorboard` / `wandb` / `neptune`，不写时用配置里的默认（runner 里缺省为 tensorboard） |
| `--log_project_name` | None | wandb / neptune 的项目名 |

#### (2) 任务与评估（`:52-60`）

| 参数 | 默认 | 含义 |
|---|---|---|
| `--task` | `Isaac-Velocity-Custom-Unitree-Go2-v0` | 任务名，目前只有这一个定制任务 |
| `--id_context` | `default` | 训练范围：`default`（质量 −1~3 kg）或 `wide`（−1~9 kg） |
| `--stochastic_eval` | False | 评估时抽样动作（默认用均值） |
| `--save_eval_detailed` | False | 评估存逐步详细数据 |
| `--print_stats` | False | 评估时打印 α 与不确定性分位数 |

#### (3) finetune（适应模块训练）（`:63-77`）

| 参数 | 默认 | 含义 |
|---|---|---|
| `--calculate_validation_metrics_only` | False | 只重算验证集分位数，不训练 |
| `--finetune_iterations` | **5000** | 适应模块训练次数（鲁棒 RL、DR 会被改成 0） |
| `--train_and_finetune` | False | finetune 阶段是否同时继续训练策略（默认不训练） |
| `--finetune_fresh_start` | False | 加载模型时丢弃已有的历史编码器参数，从头训 |
| `--finetune_w_adversary` | False | finetune 阶段保留对抗者（默认关，对应论文"监督阶段不加对抗者"） |
| `--num_learning_epochs_finetune` | None | finetune 每次更新的 epoch 数（不写则同 RL 阶段） |

#### (4) 网络大小（`:80-91`）

| 参数 | 默认 | 含义 |
|---|---|---|
| `--actor_hidden_dims` | None（配置里为 512 256 128） | 策略网络隐藏层 |
| `--critic_hidden_dims` | None（512 256 128） | 价值网络 |
| `--context_hidden_dims` | None（64 64） | 上下文编码器 |
| `--adversary_hidden_dims` | None | 对抗者 |
| `--history_encoder_hidden_dims` | None（512 256 128） | 历史编码器 |
| `--history_epinet_hidden_dims` | None（16 16） | epinet |

括号里的值来自 `GRAMActorCritic.__init__` 的默认参数（`gram_actor_critic.py:32-56`），与论文 Table I 一致。

#### (5) 初始化（`:94-106`）

| 参数 | 默认 | 含义 |
|---|---|---|
| `--no_init_nn_weights` | False | 不做 Xavier 初始化 |
| `--use_std_direct` | False | 直接学 std 而不是 log_std |
| `--actor_gain` / `--critic_gain` / `--context_gain` / `--adversary_gain` / `--history_gain` | **1e-4** | 各网络最后一层的初始化增益（很小 → 初始输出≈0） |
| `--history_epinet_gain` | **1e-4** | epinet 可训练部分最后一层 |
| `--history_epinet_prior_gain` | **1.0** | epinet 先验网络最后一层（正常大小） |

#### (6) 训练（`:109-130`）

| 参数 | 默认 | 含义 |
|---|---|---|
| `--alg_name` | **`gram`** | 六选一：`gram`、`gram_separate`、`gram_modular`、`robust_rl`、`contextual_rl`、`domain_rand` |
| `--no_empirical_normalization` | False | 关闭观测归一化（默认开） |
| `--num_learning_epochs` | None | 每次 PPO 更新把数据过几遍（不写用 Isaac Lab 默认） |
| `--num_mini_batches` | None | 每遍分几个小批量 |
| `--robust_mask_update_every` | **1** | 每几次迭代翻转一次 robust_mask（1 = 每次都换） |

#### (7) 对抗者（`:133-148`）

| 参数 | 默认 | 含义 |
|---|---|---|
| `--adversary_magnitude` | **1.0** | 推力最大强度（单位：对线速度的改变量 m/s） |
| `--adversary_clamp` | 5.0 | 对抗者网络输出的限幅 |
| `--no_adversary_random_scale` | False | 默认每次推力强度在 [0, 当前上限] 里随机取，加此项则固定取上限 |
| `--adversary_random_angle` | False | 推力方向随机（不再由对抗者学习），可作消融 |
| `--adversary_max_scale_start` | 0.0 | 推力上限的起始值（随训练线性增到 1） |
| `--adversary_prob` | **0.05** | 每一步被推的概率（论文"5% of the time"） |
| `--adversary_update_every` | **10** | 每 10 次迭代更新一次对抗者 |
| `--adversary_init_noise_std` | 1.0 | 对抗者初始动作标准差 |

#### (8) 上下文与历史编码器（`:151-224`）

| 参数 | 默认 | 含义 |
|---|---|---|
| `--robust_use_latent_actor` | False | 独立鲁棒策略也输入隐变量（只对 `robust_as_zeros=False` 的算法有意义） |
| `--no_robust_use_latent_critic` | False | 独立鲁棒价值网络不输入隐变量 |
| `--num_latent` | **8** | 隐变量 z 维度 d |
| `--latent_detach_actor` / `--latent_detach_critic` | False | 策略/价值网络的梯度不传回上下文编码器 |
| `--no_context_critic` | False | 价值网络不输入隐变量 |
| `--obs_history_length` | **16** | 历史长度 H |
| `--context_encoder_clamp` | False | 上下文编码器输出限幅 |
| `--context_encoder_clamp_value` | 1.0 | 限幅值 |
| `--context_encoder_stochastic` | False | 上下文编码器输出加噪声 |
| `--context_encoder_noise_std` | 0.25 | 噪声标准差 |
| `--history_epinet_output_type` | **`base`** | 适应时用 base 输出还是 epinet 均值（**论文式 9 写的是均值，代码默认用 base**） |
| `--no_history_epinet_finetune_scale` | False | 不用验证集定 λ（λ 固定为 1） |
| `--no_history_epinet_finetune_shift` | False | 不用验证集定 β（β 固定为 0） |
| `--history_epinet_finetune_min_quantile` | **0.90** | β 取验证集的哪个分位数 |
| `--history_epinet_finetune_max_quantile` | **0.99** | 在哪个分位数处 α 达到目标值 |
| `--history_epinet_finetune_target` | **0.01** | 该分位数处的 α 目标值 |
| `--history_epinet_type` | `mlp_dot` | epinet 类型：`mlp`（直接拼 ε）或 `mlp_dot`（输出矩阵乘 ε） |
| `--history_epinet_input_type` | `concat` | epinet 输入：`full`（原始历史）、`concat`（原始历史 + base 隐藏特征）、`intermediate`（只用隐藏特征） |
| `--history_epinet_dim` | **8** | ε 的维度 m |
| `--history_epinet_num_samples` | **8** | 每次采样 ε 的个数 N |
| `--history_epinet_coef` | 1.0 | epinet 项的系数 |
| `--history_loss_actions` | False | 历史损失里加"动作一致"项 |
| `--history_loss_robust_as_zeros` | False | 鲁棒组数据的回归目标设为 0 |
| `--history_loss_adapt_only` | False | 历史损失只用适应组数据 |
| `--history_loss_include_epinet` | False | 历史损失合并计算 base 和 epinet（默认分开算） |
| `--history_lr` | **1e-3** | 历史编码器学习率 |

#### (9) 验证集（`:227-243`）

| 参数 | 默认 | 含义 |
|---|---|---|
| `--collect_data_from_context` | False | 收集验证数据时用 f(c)（默认用历史编码器） |
| `--collect_data_stochastic` | False | 收集时抽样动作（默认确定性） |
| `--uncertainty_metric_full_only` | False | 只用完整回合的数据算分位数 |
| `--uncertainty_metric_adapt_only` | False | 只用适应组的数据算分位数 |

#### (10) 环境上下文与场景（`:248-321`）

| 参数 | 默认 | 含义 |
|---|---|---|
| `--terrain_roughness_cm` | None（0） | 粗糙地形高度（cm）；论文 5 / 10 |
| `--terrain_slope_degrees` | None（0） | 坡度（度）；正为上坡，负为下坡；论文 5 / 10 |
| `--enable_height_scan` | False | 打开高度扫描观测 |
| `--frozen_joint_type` | `none` | 评估时冻结关节：`none`/`hip`/`thigh`/`calf`/`all`/`custom` |
| `--base_mass_min` / `--base_mass_max` | None（−1 / 3） | 附加质量范围（kg）；评估 9 kg 就写 9 9 |
| `--no_base_mass_context_scale` 及 `--base_mass_context_scale_min/max` | — | 上下文里质量是否归一化、按什么范围归一化 |
| `--friction_mult_min` / `--friction_mult_max` | None（0.05 / 4.5） | 摩擦倍数范围 |
| `--no_friction_mult_context_scale` 等 | — | 同上，摩擦的归一化 |
| `--motor_strength_mult_min` / `--motor_strength_mult_max` | None（0.8 / 1.2） | 电机强度倍数范围 |
| `--motor_fault_indices` | None | 电机故障：可多次出现，每次一组关节编号，每个环境从各组里随机挑一组把力矩置 0；`-1` 表示"无故障"选项 |
| `--no_motor_strength_mult_context_scale` 等 | — | 电机强度的归一化 |
| `--motor_Kp` / `--motor_Kd` | None（25 / 0.5） | PD 增益 |
| `--hip_scale_mult` | **0.5** | 髋关节动作缩放再乘 0.5 |
| `--action_mult_indices` | None | 动作倍数作用的关节组（可多次出现） |
| `--action_mult_min` / `--action_mult_max` / `--action_mult_count` | None（0 / 0 / None） | 被选中关节的动作倍数范围；默认 0 即"冻结"；`count` 表示从范围里取几个离散值 |
| `--no_action_mult_context_scale` 等 | — | 动作倍数的归一化（默认不进上下文） |
| `--joint_bias_min` / `--joint_bias_max` | None（−0.1 / 0.1） | 关节零偏范围（rad） |
| `--no_joint_bias_context_scale` 等 | — | 零偏的归一化 |
| `--no_joint_pos_clamp` | False | 关节目标不按关节限位截断 |

#### (11) 任务指令（`:324-343`）

| 参数 | 默认（训练） | 含义 |
|---|---|---|
| `--target_x_vel_min/max` | −1 / 1 | 前后目标速度范围（m/s） |
| `--target_y_vel_min/max` | −1 / 1 | 左右目标速度范围 |
| `--target_heading_min/max` | −π / π | 目标航向范围（偏航角速度由航向误差算出） |
| `--rel_standing_envs` | 0.02 | 多大比例的环境指令是"原地站着" |
| `--resample_time_min/max` | 10 / 10 | 每隔多少秒换一次指令 |
| `--start_yaw_min/max` | −π / π | 初始朝向 |
| `--disable_self_collisions` | False | 关闭自碰撞 |
| `--disable_obs_noise` | False | 关闭观测噪声 |
| `--no_terminate_contacts` | False | 评估时不因碰撞终止 |

#### (12) 显示（`:346-350`）

`--display_mode`、`--display_type`（`world`/`zoom`/`follow`）、`--display_resolution`：录演示视频用的相机设置，和训练无关。

### 9.2 `parse_custom_inputs_cfg`：实验设置怎么生成

**这段代码要干什么**：从 `default` 或 `wide` 配置出发，用命令行覆盖，并在评估模式下做一些固定的改动，得到交给环境的"实验设置"。

**结构**（`:355-526`）：

```python
def parse_custom_inputs_cfg(task_name, id_context, args_cli, eval_mode):
    from source.envs import get_custom_inputs_cfg
    inputs_cfg = get_custom_inputs_cfg(task_name, id_context)    # 取 default 或 wide 配置
    inputs_cfg.eval_mode = eval_mode
    if args_cli.terrain_roughness_cm is not None:
        inputs_cfg.terrain_roughness_cm = args_cli.terrain_roughness_cm
    ...
```

绝大部分是同一个模式："命令行给了就覆盖，没给就保留默认"。需要特别注意的有四处。

**(a) 冻结关节只在评估时生效**（`:373-384`）：

```python
    if eval_mode:
        if args_cli.frozen_joint_type == "none":
            inputs_cfg.action_mult_indices = None
        elif args_cli.frozen_joint_type == "hip":
            inputs_cfg.action_mult_indices = [[0], [1], [2], [3]]
        elif args_cli.frozen_joint_type == "thigh":
            inputs_cfg.action_mult_indices = [[4], [5], [6], [7]]
        elif args_cli.frozen_joint_type == "calf":
            inputs_cfg.action_mult_indices = [[8], [9], [10], [11]]
        elif args_cli.frozen_joint_type == "all":
            inputs_cfg.action_mult_indices = [[0], [1], [2], [3], [4], [5], [6], [7], [8], [9], [10], [11]]
```

- `action_mult_indices` 是"候选关节组"的列表。每个环境从列表里**随机挑一组**，把那组关节的动作倍数设成 `action_mult_min~max`（默认都是 0），即"冻结"（`envs_utils.py:51-91`）。
- `hip` = 4 个髋关节各成一组，每个环境随机冻结其中一个髋关节；`all` = 12 个关节里随机冻结一个，即论文的"随机冻结关节"（远 OOD）。
- 关节编号 0-3 是髋、4-7 是大腿、8-11 是小腿：【推断】这是 Isaac Lab 对 Go2 关节的排序（按关节类型分组，组内顺序为 FL、FR、RL、RR）。
- **论文近 OOD 的"后髋冻结"**：README 没给命令。【推断】应该用 `--frozen_joint_type custom --action_mult_indices 2 --action_mult_indices 3`（`custom` 在这里没有分支，于是由后面 `:435-436` 的 `--action_mult_indices` 设定），即后左、后右髋各一组。需打印关节名核对编号。
- "冻结"的真实含义：动作倍数为 0，网络对这个关节的输出被乘 0，关节目标 = 默认角度 + 零偏，PD 会把它**拉回默认姿态**，而不是锁在当前位置。

**(b) 电机故障**（`:417-418`）：`--motor_fault_indices` 原样写入。训练和评估都会生效（不在 `if eval_mode` 里）。

**(c) 推力强度交给专门的函数**（`:468`）：`inputs_cfg = set_adversary_magnitude_by_alg(...)`，见 9.3。

**(d) 评估模式下的固定改动**（`:481-507`）：命令行没指定时：

| 设置 | 训练默认 | 评估时改为 | 含义 |
|---|---|---|---|
| `target_heading_min/max` | −π / π | **0 / 0** | 目标航向固定为 0（朝初始方向直走，不转向） |
| `rel_standing_envs` | 0.02 | **0** | 没有"原地站着"的环境 |
| `resample_time_min/max` | 10 / 10 s | **1e6 s** | 整个回合指令不变 |

【推断】x、y 速度仍在 [−1, 1] 里随机，每个环境一个固定的目标速度。

**小结**：`parse_custom_inputs_cfg` = 默认配置 + 命令行覆盖 + 评估模式的固定改动；冻结关节只在评估时生效，电机故障训练评估都生效。

### 9.3 `set_adversary_magnitude_by_alg`（`:529-539`）

```python
def set_adversary_magnitude_by_alg(inputs_cfg, args_cli, eval_mode):
    """Update adversary magnitude based on algorithm."""
    if eval_mode:
        inputs_cfg.adversary_magnitude = 0.0
    else:
        if args_cli.alg_name.startswith("contextual_rl") or args_cli.alg_name.startswith("domain_rand"):
            inputs_cfg.adversary_magnitude = 0.0
        else:
            inputs_cfg.adversary_magnitude = args_cli.adversary_magnitude

    return inputs_cfg
```

| 情况 | 推力强度 |
|---|---|
| 评估（任何算法） | **0**：评估时不推 |
| 训练：情境 RL、域随机化 | **0**：这两个基线不用对抗训练 |
| 训练：GRAM 系列、鲁棒 RL | `--adversary_magnitude`（默认 1.0） |

这是**环境侧**的推力强度上限。实际每一步推不推、往哪推、推多大，由对抗者和 `adversary_prob` 决定（见 code 目录中的环境与 PPO 文件）。

### 9.4 `update_agent_cfg_by_alg`：六种算法逐分支讲解

**这段代码要干什么**：六种算法共用同一套网络和 runner 代码，区别只在几个**开关**。这个函数根据 `--alg_name` 把开关拨好。看懂它，就看懂了论文的四个对比方法和三个消融是怎么实现的。

**第一步：所有开关先归零**（`:544-560`）：

```python
    agent_cfg.alg_name = args_cli.alg_name
    agent_cfg.adapt_train_only = False
    agent_cfg.robust_train_only = False
    agent_cfg.policy.act_inference_robust = False
    agent_cfg.policy.act_inference_adapt = False
    agent_cfg.policy.history_epinet_apply_bias = False
    agent_cfg.policy.robust_as_zeros = False
    agent_cfg.policy.history_epinet = False
    agent_cfg.robust_mask_reset_update = False
    agent_cfg.collect_data_mix = True
    agent_cfg.finetune_iterations = args_cli.finetune_iterations
    agent_cfg.policy.adversary_prob = args_cli.adversary_prob
    agent_cfg.policy.robust_use_latent_actor = args_cli.robust_use_latent_actor
    if args_cli.no_robust_use_latent_critic:
        agent_cfg.policy.robust_use_latent_critic = False
    else:
        agent_cfg.policy.robust_use_latent_critic = True
```

**每个开关的含义**（先记住这张表）：

| 开关 | 为 True 时的含义 |
|---|---|
| `adapt_train_only` | 训练时所有环境都做适应训练（robust_mask 全 0） |
| `robust_train_only` | 训练时所有环境都做鲁棒训练（robust_mask 全 1） |
| `act_inference_adapt` | 评估时强制走适应分支（mask 全 0） |
| `act_inference_robust` | 评估时强制走鲁棒分支（mask 全 1） |
| `history_epinet_apply_bias` | 历史编码器输出乘 α（即 GRAM 的式 9） |
| `robust_as_zeros` | 鲁棒分支 = **同一个**策略网络输入 z = 0；为 False 时鲁棒分支是**另一个独立网络** |
| `history_epinet` | 历史编码器带 epinet（能估计不确定性） |
| `robust_mask_reset_update` | robust_mask 只在环境**重置时**翻转（一条轨迹从头到尾一种模式）；为 False 时每次迭代都翻转（一条轨迹里混合两种模式） |
| `collect_data_mix` | 收集验证数据时也按一半一半混合 |
| `adversary_prob` | 对抗者每步推的概率 |

**第二步：训练还是评估**（`:562-567`）：

```python
    if eval_mode:
        agent_cfg.policy.act_from_context = False
        agent_cfg.policy.adversary_prob = 0.0
    else:
        agent_cfg.policy.act_from_context = True
        agent_cfg.policy.adversary_prob = args_cli.adversary_prob
```

- `act_from_context`：为 True 时隐变量 z 来自上下文编码器 f(c)（训练时用特权信息）；为 False 时来自历史编码器（部署时只能看历史）。
- 评估时永远用历史编码器，且不推。

**第三步：按算法分支**

**① `gram`**（`:569-575`）：

```python
    if args_cli.alg_name == "gram":
        agent_cfg.policy.robust_as_zeros = True
        agent_cfg.policy.history_epinet = True

        if eval_mode:
            agent_cfg.policy.act_inference_adapt = True
            agent_cfg.policy.history_epinet_apply_bias = True
```

- `robust_as_zeros = True`：鲁棒模式就是同一个网络输入 z = 0（论文的 z_rob）。
- `history_epinet = True`：历史编码器带 epinet。
- 训练：`adapt_train_only`、`robust_train_only` 都是 False，所以一半环境适应、一半鲁棒，**每次迭代翻转**（`robust_mask_reset_update = False`）→ 论文的"混合数据收集"。
- 评估：`act_inference_adapt = True` → mask 全 0，始终走"适应分支"；但 `history_epinet_apply_bias = True` → 隐变量先乘 α。α 小时隐变量趋近 0，等于自动滑向鲁棒模式。**这就是式 (9) 的软切换**。

**② `gram_separate`**（`:577-585`，消融"Separate Data"）：

```python
    elif args_cli.alg_name == "gram_separate":
        agent_cfg.policy.robust_as_zeros = True
        agent_cfg.policy.history_epinet = True
        agent_cfg.robust_mask_reset_update = True
        agent_cfg.collect_data_mix = False
        if eval_mode:
            agent_cfg.policy.act_inference_adapt = True
            agent_cfg.policy.history_epinet_apply_bias = True
```

和 GRAM 唯一的区别：`robust_mask_reset_update = True`，mask **只在回合重置时翻转**，一条轨迹从头到尾只有一种模式；`collect_data_mix = False`，验证数据也不混合。对应论文"a variant that applies separate ID and adversarial data collection"。

**③ `gram_modular`**（`:587-590`，消融"Modular"）：

```python
    elif args_cli.alg_name == "gram_modular":
        agent_cfg.policy.history_epinet = True
        agent_cfg.robust_mask_reset_update = True
        agent_cfg.collect_data_mix = False
```

- `robust_as_zeros` 保持 False → 鲁棒分支是**另一个独立的策略网络**（默认只看观测，不看隐变量）。
- 评估时 `act_inference_adapt`、`act_inference_robust`、`apply_bias` 都是 False → 走 `act_inference` 的默认路径：用 `calculate_uncertainty_mask`，不确定性超过验证集 0.99 分位数就**硬切换**到独立鲁棒网络（`gram_actor_critic.py:503-513,735-741`）。
- 对应论文"a modular approach that combines separate robust and adaptive policies at deployment time using an uncertainty threshold for switching"。

**④ `robust_rl`**（`:592-599`，基线"鲁棒 RL"）：

```python
    elif args_cli.alg_name == "robust_rl":
        if not agent_cfg.policy.robust_use_latent_actor:
            agent_cfg.finetune_iterations = 0
        if eval_mode:
            agent_cfg.policy.act_inference_robust = True
        else:
            agent_cfg.robust_train_only = True
```

- 训练：`robust_train_only` → 全部环境走鲁棒分支，即独立鲁棒网络（只看观测，不看上下文），加对抗推力。
- 不需要历史编码器，所以 `finetune_iterations = 0`，总共只训练 10000 次。
- 评估：强制走鲁棒网络。

**⑤ `contextual_rl`**（`:601-607`，基线"情境 RL / 教师—学生"）：

```python
    elif args_cli.alg_name == "contextual_rl":
        agent_cfg.policy.adversary_prob = 0.0
        if eval_mode:
            agent_cfg.policy.act_inference_adapt = True
        else:
            agent_cfg.adapt_train_only = True
```

- 训练：`adapt_train_only` → 全部环境用 f(c) 训练（教师），没有推力；之后 5000 次训练历史编码器（学生）。
- `history_epinet = False` → 普通历史编码器，没有不确定性。
- 评估：走适应分支，直接用历史编码器的估计，**不乘 α**。这就是普通 RMA。

**⑥ `domain_rand`**（`:609-618`，基线"域随机化"）：

```python
    elif args_cli.alg_name == "domain_rand":
        agent_cfg.policy.adversary_prob = 0.0
        if not agent_cfg.policy.robust_use_latent_actor:
            agent_cfg.finetune_iterations = 0
        if eval_mode:
            agent_cfg.policy.act_inference_robust = True
        else:
            agent_cfg.robust_train_only = True
```

- 和鲁棒 RL 几乎一样：全部走独立的"只看观测"的网络；
- 唯一区别：**没有推力**（`adversary_prob = 0`，且 9.3 节把推力强度也设成 0）。
- 所以"域随机化"的实现 = "鲁棒 RL 去掉对抗者"。它的鲁棒性只来自训练时随机的质量、摩擦、电机强度、零偏。

**⑦ 其他**（`:619-620`）：算法名不在这六个里就报错。

### 9.5 `parse_agent_cfg`：算法配置怎么生成

**这段代码要干什么**：取出 Isaac Lab 默认的 Go2 PPO 配置（经 GRAM 子类修改），按算法拨开关，再用命令行逐项覆盖。

```python
def parse_agent_cfg(task_name, args_cli, eval_mode):
    from omni.isaac.lab_tasks.utils.parse_cfg import load_cfg_from_registry
    agent_cfg = load_cfg_from_registry(task_name, "rsl_rl_cfg_entry_point")   # :630
    agent_cfg = update_agent_cfg_by_alg(agent_cfg, args_cli, eval_mode)        # :633
    agent_cfg.max_iterations = args_cli.max_iterations                         # :636
    ...
    agent_cfg.policy.class_name = "GRAMActorCritic"                            # :760
    agent_cfg.algorithm.class_name = "GRAMPPO"                                 # :761
    return agent_cfg
```

**配置的来源层次**（越往下优先级越高）：

```
① Isaac Lab 的 UnitreeGo2RoughPPORunnerCfg            （PPO 超参：学习率、γ、λ、clip、epoch 数、每轮步数……）
   ↓ 继承
② GRAM 的 UnitreeGo2CustomPPORunnerCfg                （改 max_iterations=10000、save_interval=5000、experiment_name）
   ↓ update_agent_cfg_by_alg
③ 按算法名设置的开关                                   （第 9.4 节）
   ↓ parse_agent_cfg 后半段
④ 命令行参数                                           （第 9.1 节）
```

**分段说明**：

| 行号 | 做了什么 |
|---|---|
| `:630` | 从注册表取 PPO 配置（任务注册时 `rsl_rl_cfg_entry_point=UnitreeGo2CustomPPORunnerCfg`，`unitree_go2_custom_env.py:299`）。【新版】`isaaclab_tasks.utils.parse_cfg` |
| `:633` | 按算法拨开关 |
| `:636-649` | 迭代次数、种子、加载、run 名、日志器。注意 `--load_run` 给了就 `resume=True` |
| `:652-654` | wandb / neptune 项目名 |
| `:661-670` | 评估和 finetune 相关开关 |
| `:673-684` | 网络大小（命令行给了才覆盖） |
| `:686-694` | 初始化方式和各网络的 gain |
| `:696` | 观测归一化：默认**开** |
| `:699-704` | PPO 的 epoch 数、小批量数、mask 翻转频率 |
| `:707-712` | 对抗者参数 |
| `:715-743` | 上下文与历史编码器、epinet、历史损失 |
| `:746-750` | 验证集收集方式 |
| `:753-757` | "硬件"参数：髋关节缩放、关节限位（随模型一起保存，部署时要用同样的设置） |
| `:760-761` | 指定网络类和算法类的名字，runner 用 `eval` 找到它们 |

**`agent_cfg` 的结构**：顶层是 runner 的设置（迭代次数、日志等），`agent_cfg.policy` 是网络的设置（会以 `**` 传给 `GRAMActorCritic`），`agent_cfg.algorithm` 是 PPO 的设置（以 `**` 传给 `GRAMPPO`）。

**从 Isaac Lab 继承、命令行没有覆盖的 PPO 超参**【推断，Isaac Lab v1.0 Go2 默认值，需在安装目录或 `params/agent.yaml` 里核对】：`num_steps_per_env = 24`、`learning_rate = 1e-3`、`schedule = "adaptive"`、`desired_kl = 0.01`、`gamma = 0.99`、`lam = 0.95`、`clip_param = 0.2`、`entropy_coef = 0.01`、`num_learning_epochs = 5`、`num_mini_batches = 4`、`max_grad_norm = 1.0`、`value_loss_coef = 1.0`、`init_noise_std = 1.0`。**复现时最可靠的做法是训练后直接打开 `params/agent.yaml` 看实际值**，因为新版 Isaac Lab 的默认值可能已经变了。

**小结**：算法配置 = Isaac Lab 默认 → GRAM 子类修改 → 按算法拨开关 → 命令行覆盖。

---

## 10. 六种算法开关总表

| 开关（训练 / 评估） | gram | gram_separate | gram_modular | robust_rl | contextual_rl | domain_rand |
|---|---|---|---|---|---|---|
| 论文中的名字 | GRAM | Separate Data | Modular | Robust RL | Contextual RL | Domain Rand. |
| `robust_as_zeros`（鲁棒=同网络输入 0） | ✔ | ✔ | ✘（独立网络） | ✘（独立网络） | ✘ | ✘（独立网络） |
| `history_epinet` | ✔ | ✔ | ✔ | ✘ | ✘ | ✘ |
| 训练时 mask | 一半一半，每迭代翻转 | 一半一半，重置时翻转 | 一半一半，重置时翻转 | 全鲁棒 | 全适应 | 全鲁棒 |
| 训练时推力 | ✔ | ✔ | ✔ | ✔ | ✘ | ✘ |
| finetune 5000 次 | ✔ | ✔ | ✔ | ✘ | ✔ | ✘ |
| 评估时的动作来源 | 适应分支 × α | 适应分支 × α | 不确定性超阈值则硬切到鲁棒网络 | 鲁棒网络 | 适应分支，不乘 α | 鲁棒网络 |
| 策略看不看隐变量 | 看（鲁棒时为 0） | 看 | 适应看、鲁棒不看 | 不看 | 看 | 不看 |

**读表要点**：
- 鲁棒 RL 和域随机化的唯一区别是有没有推力；
- 情境 RL 和 GRAM 的区别是：有没有鲁棒训练、有没有 epinet、评估时乘不乘 α；
- 三个消融各改一处：Separate 改数据混合方式，Modular 改成两个网络 + 硬切换，No φ_GRAM 不在代码的算法列表里——【推断】它可以用 GRAM 训练好的模型、评估时把 `history_epinet_apply_bias` 关掉得到，但命令行没有直接的开关，需要改代码或加参数。

---

## 11. 调用链总图

```
python -u -m source.train --alg_name gram --id_context default
│
└─ train.py:train()
   │
   ├─ from source.launcher import args_cli, simulation_app
   │    ├─ cli_utils.create_parser()                       定义 ~150 个参数
   │    ├─ AppLauncher.add_app_launcher_args(parser)       加仿真器参数
   │    ├─ parser.parse_args()                             → args_cli
   │    └─ AppLauncher(args_cli).app                       ★ 启动 Isaac Sim
   │
   ├─ import omni.isaac.lab_tasks                          登记 Isaac Lab 自带任务
   │
   ├─ cli_utils.parse_custom_inputs_cfg(eval_mode=False)
   │    ├─ envs.get_custom_inputs_cfg → unitree_go2_cfg.get_unitree_go2_custom_env_config("default")
   │    ├─ 命令行覆盖
   │    └─ set_adversary_magnitude_by_alg                  GRAM → 推力上限 1.0
   │
   ├─ envs.create_custom_env(**cfg)
   │    └─ unitree_go2_custom_env.create_unitree_go2_custom_env
   │         ├─ 定义 UnitreeGo2CustomPPORunnerCfg（继承 Isaac Lab Go2 PPO 配置）
   │         ├─ 定义 UnitreeGo2CustomEnvCfg（继承 Isaac Lab Go2 粗糙地形配置）
   │         │    └─ 用到 envs_utils：ShiftScaleClampJointPositionActionCfg、ScaledDCMotorCfg、
   │         │                      randomize_friction、adversarial_push_by_setting_velocity、reset_joints_train
   │         └─ gym.register("Isaac-Velocity-Custom-Unitree-Go2-v0", ...)
   │
   ├─ parse_env_cfg(task, num_envs=4096)                   → env_cfg
   ├─ cli_utils.parse_agent_cfg(eval_mode=False)            → agent_cfg
   │    ├─ load_cfg_from_registry(task, "rsl_rl_cfg_entry_point")
   │    ├─ update_agent_cfg_by_alg                         GRAM：robust_as_zeros、history_epinet
   │    └─ 命令行覆盖；class_name = GRAMActorCritic / GRAMPPO
   │
   ├─ 随机种子；log_dir = logs/unitree_go2_custom/<时间戳>
   │
   ├─ gym.make(task, cfg=env_cfg)                          ★ 创建 4096 个 Go2
   ├─ ContextRslRlVecEnvWrapper(env, inputs_cfg)            读取 26 维上下文 c
   │
   ├─ GRAMOnPolicyRunner(env, agent_cfg.to_dict(), log_dir)
   │    ├─ GRAMActorCritic(...)                             actor/critic/上下文编码器/历史编码器/epinet
   │    ├─ GRAMPPO(actor_critic, ...)                       三个 Adam 优化器
   │    ├─ EmpiricalNormalization                           观测归一化
   │    ├─ alg.init_storage(...)                            GRAMRolloutStorage
   │    └─ GRAMAdversary + alg.init_extras(...)             对抗者、上下文、环境
   │
   ├─ dump_yaml(params/env.yaml, params/agent.yaml)
   │
   ├─ runner.learn(10000)                                   ★ 训练主循环
   │    ├─ 迭代 0~9999：翻转 mask → alg.act / env.step 收集 → alg.compute_returns → alg.update
   │    │                 每 10 次更新对抗者；每 5000 次保存
   │    ├─ 迭代 10000：切到历史编码器、关对抗者、冻结归一化、保存
   │    ├─ 迭代 10000~14999：收集 → alg.finetune()（只训练历史编码器 + epinet）
   │    ├─ collect_validation_data()                        ★ 算 101 个分位数存进模型
   │    └─ save(model_14999.pt)
   │
   ├─ env.close()
   └─ simulation_app.close()
```

---

## 12. 运行后会产出什么文件

**训练**（以 GRAM 默认设置为例）【代码事实 + 推断】：

```
gram/logs/unitree_go2_custom/2026-11-26_16-59-53_<run_name>/
├── params/
│   ├── env.yaml            完整环境配置（含继承来的全部默认值）
│   └── agent.yaml          完整算法配置
├── events.out.tfevents.*   TensorBoard 日志：损失、回报、学习率、迭代时间……
├── git/                    【推断】代码仓库的 git diff（store_code_state 生成）
├── videos/                 仅 --video 时
├── model_0.pt              第 0 次迭代后
├── model_5000.pt           第 5000 次迭代后
├── model_10000.pt          进入 finetune 时保存一次，第 10000 次迭代结束时又保存一次并覆盖（【推断】所以"finetune 前"的快照会被覆盖）
└── model_14999.pt          ★ 最终模型（含验证集分位数，评估用它）
```

- 鲁棒 RL、域随机化没有 finetune，最终模型是 `model_9999.pt`。
- 用 `tensorboard --logdir logs/unitree_go2_custom` 可以在浏览器里看训练曲线。
- 服务器冒烟测试（2 次 RL + 1 次 finetune）的最终模型是 `model_2.pt`，约 7.0 MB，和这里的规律一致。

**`.pt` 文件里有什么**（`gram_on_policy_runner.py:159-171`）：`model_state_dict`（全部网络参数 + 验证集分位数）、`optimizer_state_dict`、`iter`、`alg_name`、`hardware_cfg`、`actor_critic_cfg`（网络结构参数）、`empirical_normalization`、`obs_norm_state_dict`、`critic_obs_norm_state_dict`。

**评估**：

```
gram/logs/unitree_go2_custom/<load_run>/eval/
└── eval_<run_name>.pkl     评估结果字典：params、returns、episode_length、alpha（及详细数据）
```

【推断】Isaac Lab 的 `dump_pickle` 会在文件名后自动补 `.pkl`。读取方法：

```python
import pickle
with open("eval_xxx.pkl", "rb") as f:
    log = pickle.load(f)
log["returns"].mean()          # 所有环境的平均回报
log["alpha"].mean()            # 平均 α
```

> 注意：评估默认把结果写到 `eval_<run_name>.pkl`。多个场景评估时，**一定要给不同的 `--run_name`**（如 `--run_name mass9`），否则会互相覆盖。

---

## 13. 常用命令手册

以下命令都在仓库根目录 `gram/` 下运行。

### 13.1 训练（论文 Table III，默认训练范围）

```bash
python -u -m source.train --alg_name gram          --id_context default
python -u -m source.train --alg_name robust_rl     --id_context default
python -u -m source.train --alg_name contextual_rl --id_context default
python -u -m source.train --alg_name domain_rand   --id_context default
python -u -m source.train --alg_name gram_separate --id_context default
python -u -m source.train --alg_name gram_modular  --id_context default
```

### 13.2 宽训练范围（论文 Fig. 5）

```bash
python -u -m source.train --alg_name gram --id_context wide
# 其余算法同理，把 --alg_name 换掉
```

### 13.3 多种子

```bash
for s in 1 2 3; do
  python -u -m source.train --alg_name gram --id_context default --seed $s --run_name gram_s$s
done
```

### 13.4 冒烟测试（快速检查能不能跑）

```bash
python -u -m source.train --alg_name gram --num_envs 16 --max_iterations 2 --finetune_iterations 1 \
    --num_learning_epochs 1 --num_learning_epochs_finetune 1 --num_mini_batches 2 --run_name smoke
```

### 13.5 评估（`<train_folder_name>` 换成训练目录名，如 `2026-11-26_16-59-53`）

| 场景 | 命令参数 | 论文类别 |
|---|---|---|
| ID（默认范围随机） | （不加场景参数） | ID |
| 加 6 kg | `--base_mass_min 6.0 --base_mass_max 6.0` | 近 OOD |
| 加 9 kg | `--base_mass_min 9.0 --base_mass_max 9.0` | 远 OOD |
| 5° 坡 | `--terrain_slope_degrees 5.0` | 近 OOD |
| 10° 坡 | `--terrain_slope_degrees 10.0` | 远 OOD |
| 5 cm 粗糙 | `--terrain_roughness_cm 5.0` | 近 OOD |
| 10 cm 粗糙 | `--terrain_roughness_cm 10.0` | 远 OOD |
| 后髋冻结 | `--frozen_joint_type custom --action_mult_indices 2 --action_mult_indices 3`【推断】 | 近 OOD |
| 随机关节冻结 | `--frozen_joint_type all` | 远 OOD |

完整示例：

```bash
python -u -m source.eval --alg_name gram --id_context default \
    --load_run <train_folder_name> \
    --base_mass_min 9.0 --base_mass_max 9.0 \
    --run_name mass9 --print_stats
```

- `--alg_name` 和 `--id_context` **必须和训练时一致**，否则网络开关和上下文归一化范围对不上。
- 评估默认也是 4096 个环境，可用 `--num_envs` 调小。

### 13.6 和我们方向相关的现成参数（不改代码就能试）

```bash
# 电机整体变弱：所有电机强度 0.5 倍（超出训练范围 0.8~1.2）
python -u -m source.eval --alg_name gram --load_run <dir> \
    --motor_strength_mult_min 0.5 --motor_strength_mult_max 0.5 --run_name weak05

# 电机故障：每个环境随机让 12 个电机中的 1 个力矩为 0
python -u -m source.eval --alg_name gram --load_run <dir> \
    --motor_fault_indices 0 --motor_fault_indices 1 ... --motor_fault_indices 11 --run_name fault1
```

【代码事实】这两种变化都在**环境创建时**一次性设定，整个回合不变，不是"跑着跑着突然坏"。要做运行中故障，需要改环境代码（见 code 目录中讲环境的文件）。

---

## 14. 新旧版本命名对照

服务器上用的是 Isaac Sim 5.1 + Isaac Lab 0.54.2 + rsl_rl 2.0.0。讲解以官方原版为准，对照如下：

| 官方原版（Isaac Lab v1.0.0） | 服务器版（Isaac Lab 0.54.2） |
|---|---|
| `omni.isaac.lab.*` | `isaaclab.*` |
| `omni.isaac.lab_tasks.*` | `isaaclab_tasks.*` |
| `omni.isaac.lab.app.AppLauncher` | `isaaclab.app.AppLauncher` |
| `...velocity.config.unitree_go2...` | `...velocity.config.go2...` |
| `...agents.rsl_rl_cfg` | `...agents.rsl_rl_ppo_cfg` |
| `omni.isaac.lab_tasks.utils.wrappers.rsl_rl` | `isaaclab_rl.rsl_rl`（兼容版改用自带的 `source/compat/rsl_rl_vecenv_v1.py` 以保留旧接口） |
| `parse_env_cfg(..., use_gpu=...)` | `parse_env_cfg(..., device=...)` |
| `--cpu`（GRAM 自定义） | 与 AppLauncher 自带参数冲突，兼容版删除 |
| `dump_pickle` | 新版已移除，兼容版补了一个输出函数 |

---

## 15. 自测题

1. 为什么 `train.py` 里几乎所有 import 都写在 `train()` 函数内部？
2. `train_inputs_cfg`、`env_cfg`、`agent_cfg` 三者分别是什么？哪个会交给上下文包装器？
3. 命令 `python -u -m source.train --alg_name gram` 默认一共做多少次迭代？分哪两段？最终模型的文件名是什么？
4. 鲁棒 RL 和域随机化在代码里的区别是什么？
5. GRAM 评估时 `act_inference_adapt = True`，为什么还能"退回鲁棒模式"？
6. `gram_separate` 和 `gram` 只差哪个开关？它对应论文的哪个消融、想证明什么？
7. `gram_modular` 评估时怎么决定用哪个网络？
8. 评估时，目标航向、站立环境比例、指令重采样时间分别被改成什么？推力是多少？
9. `--frozen_joint_type all` 在训练时有没有作用？它在评估时具体做了什么？
10. 评估 9 kg 和 10° 坡两个场景时，如果都不写 `--run_name`，会发生什么？

<details>
<summary>参考答案</summary>

1. Isaac Lab 的模块依赖 Omniverse 扩展，必须在 Isaac Sim 启动后才能 import；而启动发生在 `from source.launcher import ...` 这一行，所以其余 import 都要放在它之后，只能写在函数里。
2. `train_inputs_cfg` 是实验设置原始参数表（`UnitreeGo2CustomDefaultIDCfg`，含质量、摩擦等范围）；`env_cfg` 是按它生成的 Isaac Lab 环境配置；`agent_cfg` 是算法配置（网络、PPO、GRAM 开关）。`train_inputs_cfg` 交给 `ContextRslRlVecEnvWrapper`，用于确定上下文的组成和归一化范围。
3. 共 15000 次：RL 阶段 10000 次（迭代 0~9999）+ finetune 5000 次（迭代 10000~14999）。最终模型 `model_14999.pt`，含验证集分位数。
4. 两者都只训练"只看观测"的独立鲁棒网络；鲁棒 RL 有对抗推力，域随机化没有（`adversary_prob = 0`，推力强度也为 0）。
5. 因为 `history_epinet_apply_bias = True`，隐变量会先乘 α。α 小时隐变量趋近 0，而训练时同一个网络在 z = 0 下学过鲁棒行为（`robust_as_zeros = True`），所以"适应分支 × 小 α"自然变成鲁棒模式。
6. 差在 `robust_mask_reset_update`（以及 `collect_data_mix`）：Separate 只在回合重置时翻转 mask，一条轨迹只有一种模式。对应消融"Separate Data"，用来证明 GRAM 的"一条轨迹内混合两种数据"有额外的鲁棒性收益（远 OOD 0.58 vs 0.46）。
7. 用 `calculate_uncertainty_mask`：不确定性超过验证集 0.99 分位数的环境切到独立鲁棒网络，否则用适应网络（用历史编码器估计的隐变量，不乘 α）。
8. 航向固定为 0；站立比例 0；重采样时间 1e6 秒（整回合不换指令）；推力为 0。
9. 训练时没有作用（冻结关节的设置在 `if eval_mode:` 里）。评估时，每个环境从 12 个关节里随机选一个，把它的动作倍数设为 0，该关节目标固定为默认角度加零偏，被 PD 拉回默认姿态。
10. 两次评估都写到 `<load_run>/eval/eval.pkl`，后一次覆盖前一次，前一个场景的结果丢失。
</details>
