# 代码精读 02：仿真环境（`source/envs/`）

> 这一篇讲 GRAM 的"训练场"：机器狗在什么地面上走、身上加了多少重量、电机有多大力气、动作怎么变成关节角、谁在推它、奖励怎么算、"环境参数"（上下文）怎么交给网络。
>
> 读者假设：没写过 Isaac Lab，PyTorch 只会一点。每段按"这段要干什么 → 代码原文 → 逐行解释 → 数值例子 → 小结"来讲。
>
> 代码版本：merlresearch/gram 官方仓库（Isaac Lab v1.0 写法，`omni.isaac.lab.*` 命名空间）。服务器上的兼容版只把 import 改成了 `isaaclab.*`，逻辑相同。行号以官方仓库为准。
>
> 标注约定：
> - **【代码事实】** 直接从本仓库代码读出来的；
> - **【推断·Isaac Lab 默认】** 来自 GRAM 继承的 Isaac Lab 父类配置。父类不在本仓库里，这些值是按 Isaac Lab v1.0 的写法推断的，**需在服务器 `work/IsaacLab` 中核对**，汇报时不要当成确定事实。

---

## 目录

0. 先懂几个 Isaac Lab 概念
1. `__init__.py`：任务入口
2. `unitree_go2_cfg.py`：所有"环境旋钮"的默认值
3. `unitree_go2_custom_env.py`：组装环境
4. `envs_utils.py`：自定义的动作、事件、电机
5. `context_env_wrapper.py`：把 26 维上下文交给网络
6. 一张图串起来：一个仿真步里发生了什么
7. 迁移到 Go2-W 要改哪里
8. 怎么加"运行中故障 / 中途加载荷"
9. 自测题

---

## 0. 先懂几个 Isaac Lab 概念

### 0.1 Isaac Sim 与 Isaac Lab

- **Isaac Sim**：NVIDIA 的物理仿真器，底层物理引擎叫 **PhysX**，能在 GPU 上同时跑几千个机器人。
- **Isaac Lab**：建在 Isaac Sim 上的机器人学习框架，提供"搭环境、算奖励、接强化学习库"的一整套工具。GRAM 用的是 v1.0。

### 0.2 "Manager-based"（基于管理器）的环境

Isaac Lab 把一个强化学习环境拆成很多**管理器（manager）**，每个管理器管一件事。你只需要写一个**配置类**（`...Cfg`），在里面列出各种"项（term）"，框架会自动调用。

| 管理器 | 管什么 | GRAM 里对应 |
|---|---|---|
| 场景 scene | 有哪些物体：机器人、地形、传感器 | Go2 机器人、平地或粗糙地形、接触传感器 |
| 动作 action | 网络输出的数字怎么变成关节指令 | `ShiftScaleClampJointPositionAction` |
| 观测 observation | 给网络看什么 | 角速度、重力方向、关节角、关节速度、指令、上一步动作 |
| 事件 event | 在特定时刻改环境：启动时、重置时、每隔一段时间 | 摩擦随机化、加质量、对抗推力、重置关节 |
| 指令 command | 给机器人的目标 | 目标速度 [vx, vy, ωz] |
| 奖励 reward | 每步打分 | 跟踪速度、惩罚抖动等 |
| 终止 termination | 什么时候结束一个回合 | 超时、机身着地 |
| 课程 curriculum | 难度逐步提高 | GRAM **关掉了** |

**事件的三种模式**（后面反复出现）：
- `startup`：环境**创建时**执行一次；
- `reset`：每个回合**重置时**执行；
- `interval`：运行过程中**每隔一段时间**执行。

> 这一点对理解 GRAM 非常关键：GRAM 的摩擦、质量、电机强度、关节零偏，**全都只在环境创建时随机一次**（见 §5.4）。

### 0.3 配置类与 `__post_init__`

```python
@configclass
class UnitreeGo2CustomEnvCfg(UnitreeGo2RoughEnvCfg):
    def __post_init__(self):
        super().__post_init__()
        ...修改父类的设置...
```

- `@configclass`：Isaac Lab 的装饰器，把类变成一个"配置数据结构"（类似 Python 的 dataclass）。
- **继承**：`UnitreeGo2CustomEnvCfg` 继承 Isaac Lab 自带的 `UnitreeGo2RoughEnvCfg`（Go2 粗糙地形速度跟踪任务），先拿到父类的全部设置。
- `__post_init__`：对象创建完后自动执行的函数。GRAM 在这里**覆盖**父类的部分设置。

所以 GRAM 的环境 = **Isaac Lab 官方 Go2 任务 + GRAM 的修改**。没被修改的部分（比如观测噪声大小、仿真步长）都沿用父类默认值。

### 0.4 并行环境与张量形状

GRAM 训练时同时跑 `num_envs = 4096` 个机器人。代码里几乎每个量都是一个张量，第一维是环境编号：

| 量 | 形状 | 含义 |
|---|---|---|
| 动作 | (4096, 12) | 每个机器人 12 个关节 |
| 上下文 | (4096, 26) | 每个机器人 26 个环境参数 |
| 机身速度 | (4096, 6) | 线速度 3 + 角速度 3 |

看到 `[:, :4]` 意思是"所有环境、前 4 列"；看到 `unsqueeze(dim=-1)` 意思是在最后加一维，方便广播相乘。

### 0.5 PD 控制：策略输出怎么变成力矩

GRAM 的策略**不直接输出力矩**，而是输出**目标关节角** q\*。底层 PD 控制器把它变成力矩：

$$\tau = K_p\,(q^* - q) - K_d\,\dot q$$

- q：当前关节角；q̇：当前关节角速度；
- Kp = 25 N·m/rad：角度差 1 rad 产生 25 N·m 力矩，相当于"弹簧硬度"；
- Kd = 0.5 N·m·s/rad：角速度 1 rad/s 产生 0.5 N·m 阻力，相当于"阻尼"。

**数值例子**：某关节当前 q = 0.80 rad，目标 q\* = 0.90 rad，正以 q̇ = 2.0 rad/s 转动。

τ = 25 × (0.90 − 0.80) − 0.5 × 2.0 = 2.5 − 1.0 = **1.5 N·m**

**控制的视角**：策略工作在 50 Hz，PD 在 200 Hz（每个策略步内 PD 算 4 次）。这是典型的**分层控制**：上层（学习）给设定值，下层（PD）做伺服。老师若问"强化学习输出什么"，答"关节目标角，底层还是 PD"。

---

## 1. `__init__.py`：任务入口

### 这段要干什么

告诉训练脚本：有一个自定义任务叫 `Isaac-Velocity-Custom-Unitree-Go2-v0`，以及怎么拿到它的配置、怎么创建它。

### 代码（`source/envs/__init__.py:5-30`）

```python
from source.envs.unitree_go2_cfg import get_unitree_go2_custom_env_config
from source.envs.unitree_go2_custom_env import create_unitree_go2_custom_env

CUSTOM_ENVS = [
    "Isaac-Velocity-Custom-Unitree-Go2-v0",
]

def get_custom_inputs_cfg(task, id_context):
    if task in CUSTOM_ENVS:
        cfg = get_unitree_go2_custom_env_config(id_context)
    else:
        raise ValueError("custom task %s not defined" % task)
    return cfg

def create_custom_env(task, **kwargs):
    if task in CUSTOM_ENVS:
        create_unitree_go2_custom_env(task, **kwargs)
    else:
        raise ValueError("custom task %s not defined" % task)
```

### 逐行解释

| 行 | 作用 |
|---|---|
| 5–6 | 导入两个函数：一个拿配置，一个创建环境 |
| 12–14 | 支持的任务名列表，目前只有一个 |
| 17–23 | `get_custom_inputs_cfg`：按 `id_context`（`"default"` 或 `"wide"`）返回一套"环境旋钮" |
| 26–30 | `create_custom_env`：用这些旋钮创建并**注册**环境（注册后 `gym.make` 才能找到它） |

### 在整个流程中的位置

`train.py` 大致这样用（`train.py:35-85`，简化）：

```
train_inputs_cfg = get_custom_inputs_cfg(task, id_context)   # 拿旋钮
...命令行参数覆盖旋钮...
create_custom_env(task, **train_inputs_cfg.to_dict())      # 注册环境
env_cfg = parse_env_cfg(task, ...)                          # 读出环境配置
env = gym.make(task, cfg=env_cfg)                           # 创建 4096 个机器人
env = ContextRslRlVecEnvWrapper(env, train_inputs_cfg)      # 包一层，提供上下文
```

### 小结

`__init__.py` 只是"总开关"。真正的内容在下面三个文件。

---

## 2. `unitree_go2_cfg.py`：所有"环境旋钮"的默认值

### 这段要干什么

把所有可调的环境参数集中放在一个类里，给出默认值。命令行参数可以覆盖它们（在 `cli_utils.py` 里处理）。

### 2.1 选择 default 还是 wide（`unitree_go2_cfg.py:12-21`）

```python
def get_unitree_go2_custom_env_config(id_context):
    if id_context == "default":  # Default ID context set
        cfg = UnitreeGo2CustomDefaultIDCfg()
    elif id_context == "wide":  # Wide ID context set
        cfg = UnitreeGo2CustomWideIDCfg()
    else:
        raise ValueError("invalid id_context")
    return cfg
```

- `default`：论文 Table II 的训练范围；
- `wide`：只把附加质量上限从 3 kg 改成 9 kg，对应论文 Fig. 5 的"宽训练"。

### 2.2 逐项讲解默认配置（`unitree_go2_cfg.py:29-117`）

下面按代码顺序，把每个配置项的**物理含义、单位、默认值**讲清楚。

#### (1) 地形（`:33-36`）

```python
terrain_roughness_cm: float = 0.0
terrain_slope_degrees: float = 0.0
height_scan: bool = False
```

| 项 | 单位 | 默认 | 含义 |
|---|---|---|---|
| `terrain_roughness_cm` | 厘米 | 0 | 地面起伏高度上限；0 = 平地。评估"5 cm / 10 cm 粗糙地面"时设 5 或 10 |
| `terrain_slope_degrees` | 度 | 0 | 坡度；正数上坡、负数下坡。评估"5° / 10° 坡"时用 |
| `height_scan` | — | False | 是否给机器人"看"周围地面高度（激光雷达式高度图）。GRAM **不用**，只用本体感知 |

> 训练时三项都是默认值：**平地、无坡、不看地形**。这就是论文说的"only trained on flat, solid ground"。

#### (2) 自碰撞（`:38-39`）

```python
activate_self_collisions: bool = True
```

打开后，机器人自己的腿和腿、腿和身体之间也会碰撞（更真实）。

#### (3) 附加机身质量（`:41-47`）

```python
base_mass_min: float = -1.00
base_mass_max: float = 3.00
base_mass_context_include: bool = True
base_mass_context_scale: bool = True
base_mass_context_scale_min: float = -1.00
base_mass_context_scale_max: float = 3.00
```

| 项 | 含义 |
|---|---|
| `base_mass_min/max` | 每个机器人机身质量**增加**一个 [−1, 3] kg 的随机量（负数表示减轻 1 kg） |
| `..._context_include` | 是否把这个量放进上下文（给教师网络看） |
| `..._context_scale` | 是否把它归一化到 [−1, 1] |
| `..._context_scale_min/max` | 归一化用的区间 |

> **为什么"随机范围"和"归一化区间"要分开写？** 评估时会把质量设成 9 kg（超出训练范围），但归一化区间仍然按训练时的 [−1, 3] 算。这样 9 kg 归一化后是 4，**远大于 1**，网络从没见过这么大的输入，这正是"OOD"的含义。两者分开，才能保证评估时网络看到的数值和训练时的标尺一致。

#### (4) 摩擦倍数（`:49-55`）

```python
friction_mult_min: float = 0.05
friction_mult_max: float = 4.50
...（context 相关同上）
```

- 足端摩擦系数 = 默认值 × 倍数，倍数在 [0.05, 4.5] 之间。
- 0.05 倍几乎是冰面，4.5 倍是非常"粘"的地面。

#### (5) 电机强度（`:57-67`）

```python
motor_strength_mult_min: float = 0.80
motor_strength_mult_max: float = 1.20
...（context 相关）
motor_fault_indices: list = None

motor_Kp: float = 25.0
motor_Kd: float = 0.5
```

| 项 | 含义 |
|---|---|
| `motor_strength_mult_min/max` | 每个电机输出力矩再乘一个 [0.8, 1.2] 的倍数，**12 个电机各自独立随机** |
| `motor_fault_indices` | 电机故障：指定某些电机力矩倍数变成 0（完全无力）。默认 None = 不用。**论文没用这个功能**，但它对我们做容错很有用，见 §4.6 |
| `motor_Kp / motor_Kd` | PD 增益，见 §0.5 |

#### (6) 动作的平移、缩放、限幅（`:69-88`）

```python
hip_scale_mult: float = 0.5

action_mult_indices: list = None
action_mult_min: float = 0.0
action_mult_max: float = 0.0
action_mult_count: int = None
action_mult_context_include: bool = False
action_mult_context_scale: bool = True
action_mult_context_scale_min: float = 0.0
action_mult_context_scale_max: float = 1.0

joint_bias_min: float = -0.10
joint_bias_max: float = 0.10
...（context 相关）

joint_pos_clamp: bool = True
```

| 项 | 默认 | 含义 |
|---|---|---|
| `hip_scale_mult` | 0.5 | 髋关节（hip，左右摆动那个）的动作幅度只有其他关节的一半 |
| `action_mult_indices` | None | **关节冻结**：选哪些关节，把它们的动作乘一个倍数。默认不用；评估"冻结后髋/随机关节冻结"时才设置 |
| `action_mult_min/max` | 0 / 0 | 冻结时的倍数，0 = 动作完全不起作用 |
| `action_mult_count` | None | 倍数是否从有限个离散值里选 |
| `action_mult_context_include` | **False** | 冻结信息**不**放进上下文，所以训练时网络不知道"关节冻结"这件事，它对网络来说是真正的 OOD |
| `joint_bias_min/max` | ±0.1 rad | 关节零点偏差：每个关节的目标角加一个固定偏移（模拟标定误差），约 ±5.7° |
| `joint_pos_clamp` | True | 目标角超出关节物理限位时截断 |

#### (7) 对抗者（`:90-91`）

```python
adversary_magnitude: float = 0.0
```

推力事件的总幅值。配置文件默认 0，训练时由 `cli_utils.py` 改成命令行的 `--adversary_magnitude`（默认 1.0）；**评估时强制为 0**（`cli_utils.py` 的 `set_adversary_magnitude_by_alg`）。情境 RL 和域随机化训练时也是 0。

#### (8) 任务指令（`:93-106`）

```python
target_x_vel_min: float = -1.0
target_x_vel_max: float = 1.0
target_y_vel_min: float = -1.0
target_y_vel_max: float = 1.0
target_heading_min: float = -math.pi
target_heading_max: float = math.pi
rel_standing_envs: float = 0.02
resample_time_min: float = 10.0
resample_time_max: float = 10.0
start_yaw_min: float = -math.pi
start_yaw_max: float = math.pi
```

| 项 | 单位 | 含义 |
|---|---|---|
| `target_x_vel` | m/s | 目标前后速度，[−1, 1] |
| `target_y_vel` | m/s | 目标左右速度，[−1, 1] |
| `target_heading` | rad | 目标朝向，[−π, π]；转向角速度由"当前朝向与目标朝向之差"算出 |
| `rel_standing_envs` | 比例 | 2% 的机器人收到"站着别动"的指令 |
| `resample_time` | 秒 | 每 10 秒换一个新指令（一个回合 20 秒，所以换一次）。**评估时改成 10⁶ 秒，即整个回合不换** |
| `start_yaw` | rad | 出生时随机朝向 |

#### (9) 其他（`:108-117`）

| 项 | 含义 |
|---|---|
| `disable_obs_noise` | True 时关掉观测噪声 |
| `eval_mode` | 评估模式：只保留跟踪奖励、更严格的摔倒判定，见 §3.9 |
| `terminate_contacts` | 评估时髋、大腿、头碰地也算失败 |
| `display_*` | 录视频用，与训练无关 |

### 2.3 Wide 配置（`unitree_go2_cfg.py:125-133`）

```python
@configclass
class UnitreeGo2CustomWideIDCfg(UnitreeGo2CustomDefaultIDCfg):
    def __post_init__(self):
        super().__post_init__()
        self.base_mass_max = 9.00
        self.base_mass_context_scale_max = 9.00
```

只改两项：质量上限和归一化上限都变成 9 kg。其余与 default 相同。

**数值例子**：加 9 kg 时，归一化后的上下文值：
- default 训练：(9 − (−1)) / (3 − (−1)) = 2.5 → −1 + 2×2.5 = **4.0**（远超 [−1, 1]，网络没见过）；
- wide 训练：(9 − (−1)) / (9 − (−1)) = 1.0 → −1 + 2×1.0 = **1.0**（正好在边界，网络见过）。

这就是 Fig. 5 里同样 9 kg、两种训练结果截然不同的根源。

### 2.4 Table II 与代码对照

| 论文 Table II | 代码 | 一致？ |
|---|---|---|
| 摩擦倍数 [0.05, 4.50] | `friction_mult_min/max` | ✓ |
| 附加质量 [−1, 3] kg | `base_mass_min/max` | ✓ |
| 电机强度 ×12 [0.8, 1.2] | `motor_strength_mult_min/max` | ✓ |
| 关节零偏 ×12 [−0.1, 0.1] rad | `joint_bias_min/max` | ✓ |

### 小结

- 这个文件是"旋钮面板"，没有逻辑，只有默认值。
- 训练 = 平地 + 四类随机参数 + 推力对抗者；评估 = 把某些旋钮拧到训练范围外。
- 记住两个关键：**归一化区间固定为训练范围**（所以 OOD 的上下文值会超出 [−1, 1]）；**冻结关节不进上下文**。

---

## 3. `unitree_go2_custom_env.py`：组装环境

### 这段要干什么

在 Isaac Lab 官方 Go2 任务的基础上，按上一节的旋钮改出 GRAM 的环境，然后注册成一个 gym 任务。

### 3.1 整体结构（`:37-301`）

```python
def create_unitree_go2_custom_env(task, terrain_roughness_cm, ..., **kwargs):

    @configclass
    class UnitreeGo2CustomPPORunnerCfg(UnitreeGo2RoughPPORunnerCfg):
        ...训练器配置...

    @configclass
    class UnitreeGo2CustomEnvCfg(UnitreeGo2RoughEnvCfg):
        def __post_init__(self):
            super().__post_init__()
            ...地形、动作、执行器、事件、指令、观测、奖励、评估模式...

    gym.register(id=task, ...)
```

**一个 Python 技巧**：两个配置类定义在**函数内部**，所以 `__post_init__` 里可以直接用函数参数（如 `terrain_roughness_cm`）。这叫**闭包**。好处是每次调用都能根据参数生成一个新的配置类。

### 3.2 继承的父类里有什么

【推断·Isaac Lab 默认】`UnitreeGo2RoughEnvCfg` 继承自 Isaac Lab 的 `LocomotionVelocityRoughEnvCfg`，大致包含：

| 部分 | 父类默认（v1.0，需核对） |
|---|---|
| 仿真步长 | sim.dt = 0.005 s（200 Hz），decimation = 4 → 策略 50 Hz |
| 回合长度 | 20 s |
| 机器人 | Go2 的 USD 模型和执行器配置 |
| 地形 | 地形生成器（多种粗糙地形 + 课程） |
| 传感器 | 高度扫描器、足端接触传感器 |
| 观测 | 线速度、角速度、重力投影、指令、关节角、关节速度、上一步动作、高度扫描 |
| 事件 | 摩擦随机化、加机身质量、外力、重置姿态、重置关节、定时推（Go2 配置中可能已关闭） |
| 奖励 | 速度跟踪、各种惩罚 |
| 终止 | 超时、机身触地 |

论文与代码都写"策略 50 Hz、PD 200 Hz"，与上面的推断一致。下面逐段看 GRAM 改了什么。

### 3.3 训练器配置（`:81-90`）

```python
@configclass
class UnitreeGo2CustomPPORunnerCfg(UnitreeGo2RoughPPORunnerCfg):
    def __post_init__(self):
        super().__post_init__()
        self.max_iterations = 10000
        self.save_interval = 5000
        self.experiment_name = "unitree_go2_custom"
        self.neptune_project = "gram"
        self.wandb_project = "gram"
```

- 继承 Isaac Lab 的 Go2 PPO 配置（学习率、每次迭代步数、网络大小等的默认值）；
- 只改了：最大迭代 10000（论文"10,000 updates"），每 5000 次存一次模型，日志名。
- 【推断·Isaac Lab 默认】每个环境每次迭代采样 24 步（`num_steps_per_env=24`），需核对。

### 3.4 自碰撞与关闭课程（`:98-104`）

```python
if activate_self_collisions:
    self.scene.robot.spawn.articulation_props.enabled_self_collisions = True

self.curriculum.terrain_levels = None
self.scene.terrain.terrain_generator.curriculum = False
```

- **课程（curriculum）**：父类会随着训练进步，让机器人去更难的地形。GRAM **关掉**，因为它只在平地训练。

### 3.5 地形（`:106-154`）

#### 这段要干什么

按 `terrain_roughness_cm` 和 `terrain_slope_degrees` 选地形：平地、粗糙地、上坡、下坡。

#### 代码

```python
if (terrain_roughness_cm > 0) or (terrain_slope_degrees != 0) or display_mode:
    self.scene.terrain.terrain_generator.size = (50, 50)
    self.scene.terrain.terrain_generator.num_rows = 4
    self.scene.terrain.terrain_generator.num_cols = 4

    if terrain_roughness_cm > 0:
        self.scene.terrain.terrain_generator.sub_terrains = {
            "random_rough": terrain_gen.HfRandomUniformTerrainCfg(
                proportion=1.0,
                noise_range=(0.00, terrain_roughness_cm * 0.01),
                noise_step=0.01,
                downsampled_scale=0.25,
                border_width=0.10,
            )
        }
    elif terrain_slope_degrees > 0:
        terrain_slope = math.tan(terrain_slope_degrees / 180 * math.pi)
        self.scene.terrain.terrain_generator.sub_terrains = {
            "hf_pyramid_incline": terrain_gen.HfPyramidSlopedTerrainCfg(
                proportion=1.0,
                slope_range=(abs(terrain_slope), abs(terrain_slope)),
                platform_width=2.0,
                border_width=0.10,
                inverted=True,
            )
        }
    elif terrain_slope_degrees < 0:
        ...同上，但没有 inverted=True...
    elif display_mode:
        ...起伏为 0 的"粗糙地"（仅为了显示效果）...
else:
    self.scene.terrain.terrain_type = "plane"
    self.scene.terrain.terrain_generator = None
```

#### 逐行解释

| 代码 | 含义 |
|---|---|
| `size = (50, 50)` | 每块子地形 50 m × 50 m |
| `num_rows = 4, num_cols = 4` | 4×4 共 16 块 |
| `HfRandomUniformTerrainCfg` | "高度场随机均匀地形"：地面每个格点的高度在一个范围内均匀随机 |
| `noise_range=(0, roughness×0.01)` | 高度范围。roughness=5 → 0~0.05 m，即最高 5 cm 的起伏 |
| `noise_step=0.01` | 高度以 1 cm 为台阶取值 |
| `downsampled_scale=0.25` | 每 0.25 m 取一个随机高度点，再插值，避免地面"太碎" |
| `border_width=0.10` | 地形边缘 10 cm 平的边 |
| `math.tan(deg/180*π)` | 把角度换成坡度（斜率）：5° → tan5° ≈ 0.0875 |
| `HfPyramidSlopedTerrainCfg` | 金字塔形坡：中间平台、四周斜坡 |
| `platform_width=2.0` | 中间平台 2 m 宽 |
| `inverted=True` | 金字塔倒过来（中间低四周高）。机器人从中间平台出发往外走，所以是**上坡** |
| 无 `inverted` | 正金字塔（中间高四周低），往外走是**下坡** |
| `terrain_type = "plane"` | 平地：无限大平面，**训练时就是这一支** |

**数值例子**：评估"10° 坡"时，slope = tan(10°) ≈ 0.176，即每走 1 m 升高约 17.6 cm。

#### 小结

训练用无限平面；评估时才生成粗糙地或坡。地形本身**不是上下文**的一部分，网络从没在上下文里见过"坡度"这个量，所以坡、粗糙地面属于"上下文里根本没有的变化"，和"质量超范围"是两种不同的 OOD。

### 3.6 动作项（`:175-189`）

```python
self.actions.joint_pos = ShiftScaleClampJointPositionActionCfg(
    asset_name="robot",
    joint_names=[".*"],
    scale=0.25,
    use_default_offset=True,
    hip_scale_mult=hip_scale_mult,
    action_mult_indices=action_mult_indices,
    action_mult_min=action_mult_min,
    action_mult_max=action_mult_max,
    action_mult_count=action_mult_count,
    joint_bias_min=joint_bias_min,
    joint_bias_max=joint_bias_max,
    joint_pos_clamp=joint_pos_clamp,
)
```

| 参数 | 含义 |
|---|---|
| `joint_names=[".*"]` | 正则表达式，匹配**所有**关节（Go2 共 12 个） |
| `scale=0.25` | 网络输出乘 0.25 得到角度偏移（rad） |
| `use_default_offset=True` | 在默认站姿角度上加偏移 |
| 其余 | 传给 GRAM 自定义的动作类，见 §4.1–4.2 |

完整的计算公式在 §4.2 详细讲。

### 3.7 执行器（`:191-203`）

```python
self.scene.robot.actuators["base_legs"] = ScaledDCMotorCfg(
    joint_names_expr=[".*_hip_joint", ".*_thigh_joint", ".*_calf_joint"],
    effort_limit=23.5,
    saturation_effort=23.5,
    velocity_limit=30.0,
    stiffness=motor_Kp,
    damping=motor_Kd,
    friction=0.0,
    motor_strength_mult_min=motor_strength_mult_min,
    motor_strength_mult_max=motor_strength_mult_max,
    motor_fault_indices=motor_fault_indices,
)
```

| 参数 | 值 | 含义 |
|---|---|---|
| `joint_names_expr` | hip / thigh / calf | 匹配髋、大腿、小腿关节，4 条腿 × 3 = 12 个 |
| `effort_limit` | 23.5 N·m | 最大输出力矩 |
| `saturation_effort` | 23.5 N·m | 堵转力矩（DC 电机模型用，见 §4.6） |
| `velocity_limit` | 30 rad/s | 最大转速 |
| `stiffness` | 25 | 即 Kp |
| `damping` | 0.5 | 即 Kd |
| `friction` | 0 | 关节摩擦 |
| 后三项 | — | GRAM 加的：电机强度随机和故障 |

**执行器（actuator）**：仿真里的"电机模型"，决定"给了 PD 目标之后，实际输出多大力矩"。`"base_legs"` 是名字，后面上下文包装器靠这个名字找到电机强度（§5.3）。

### 3.8 事件（`:205-239`）

#### (1) 对抗推力（`:206-211`）

```python
self.events.adversary_push = EventTerm(
    func=adversarial_push_by_setting_velocity,
    mode="interval",
    interval_range_s=(0.0, 0.0),
    params={"magnitude": adversary_magnitude},
)
```

- `mode="interval"` + 间隔 (0, 0)：【推断】间隔为 0，意味着**每个策略步都调用一次**这个函数。
- 真正推不推、往哪推，由训练代码每步写进 `params["adversary_actions"]` 和 `params["adversary_masks"]` 决定（`gram_ppo.py:114-117`）。详见 §4.4。

#### (2) 附加质量（`:214`）

```python
self.events.add_base_mass.params["mass_distribution_params"] = (base_mass_min, base_mass_max)
```

- 只改了父类已有事件的范围参数。
- 【推断·Isaac Lab 默认】父类的 `add_base_mass` 是 `startup` 模式、作用在 `base` 刚体、操作为 `"add"`（加法），需核对。上下文包装器的读法（§5.2）也印证了它作用在机身上。

#### (3) 摩擦（`:216-227`）

```python
self.events.physics_material = EventTerm(
    func=randomize_friction,
    mode="startup",
    params={
        "friction_mult_range": (friction_mult_min, friction_mult_max),
        "static_friction_default": 0.8,
        "dynamic_friction_default": 0.6,
        "restitution_default": 0.0,
        "num_buckets": 64,
        "asset_cfg": SceneEntityCfg("robot", body_names=".*foot"),
    },
)
```

- **替换**父类的摩擦事件，用 GRAM 自己的 `randomize_friction`（§4.3）。
- 静摩擦默认 0.8，动摩擦默认 0.6，弹性 0（落地不反弹）。
- `body_names=".*foot"`：只改足端的摩擦。
- `mode="startup"`：**只在创建时随机一次**。

#### (4) 出生朝向（`:229`）

```python
self.events.reset_base.params["pose_range"]["yaw"] = (start_yaw_min, start_yaw_max)
```

每次重置时，机身朝向在 [−π, π] 随机。

#### (5) 训练时的关节重置（`:231-239`）

```python
if not eval_mode:
    self.events.reset_robot_joints = EventTerm(
        func=reset_joints_train,
        mode="reset",
        params={
            "stand_range": (0.0, 1.0),
            "position_delta_range": (-0.10, 0.10),
        },
    )
```

只在训练时用：每次重置，机器人可能从"趴着"到"站着"之间的任意姿态开始（§4.5），让策略学会从各种姿态起身。评估时用父类默认的重置。

### 3.9 指令（`:241-246`）

```python
self.commands.base_velocity.resampling_time_range = (resample_time_min, resample_time_max)
self.commands.base_velocity.ranges.heading = (target_heading_min, target_heading_max)
self.commands.base_velocity.rel_standing_envs = rel_standing_envs
self.commands.base_velocity.ranges.lin_vel_x = (target_x_vel_min, target_x_vel_max)
self.commands.base_velocity.ranges.lin_vel_y = (target_y_vel_min, target_y_vel_max)
```

把 §2.2(8) 的指令参数填进父类的速度指令。

【推断·Isaac Lab 默认】父类速度指令开启了"航向模式"（`heading_command=True`）：给一个目标朝向，指令生成器用比例控制算出偏航角速度 ωz = k·(目标朝向 − 当前朝向)，并限幅。这与论文"calculate the yaw angular velocity command throughout the episode based on a target heading direction"一致。

### 3.10 观测（`:248-252`，以及 `:171-173`）

```python
if not height_scan:
    self.scene.height_scanner = None
    self.observations.policy.height_scan = None
...
self.observations.policy.base_lin_vel = None

if disable_obs_noise:
    self.observations.policy.enable_corruption = False
```

GRAM 对父类观测做了两处删除：
1. **去掉高度扫描**：不看地形；
2. **去掉机身线速度**：实机上 Go2 没有可靠的线速度传感器（只能估计），所以不给。

#### 观测向量有多长？

【推断·Isaac Lab 默认，需核对】删除后剩下的观测项和维度：

| 顺序 | 观测项 | 维度 | 含义 | 噪声（父类默认，需核对） |
|---|---|---|---|---|
| 1 | `base_ang_vel` | 3 | 机身角速度（IMU 陀螺仪） | ±0.2 均匀噪声 |
| 2 | `projected_gravity` | 3 | 重力方向在机身坐标系下的投影，反映机身倾斜 | ±0.05 |
| 3 | `velocity_commands` | 3 | 指令 [vx, vy, ωz] | 无 |
| 4 | `joint_pos`（相对默认站姿） | 12 | 关节角 − 默认角 | ±0.01 |
| 5 | `joint_vel`（相对） | 12 | 关节角速度 | ±1.5 |
| 6 | `actions` | 12 | 上一步网络输出 | 无 |
| | **合计** | **45** | | |

算法：3 + 3 + 3 + 12 + 12 + 12 = **45**。

这个数是推断的，可以用两个方法核对：
- 冒烟测试保存的模型里，`history_encoder.1.weight` 的输入维度应该是 45 × 16 = 720（16 是历史长度）；
- 或在服务器上打印 `obs.shape`。

**投影重力**是什么？把世界坐标系里的重力向量 (0, 0, −1) 转到机身坐标系。机身水平时是 (0, 0, −1)；机身前倾时 x 分量变成正或负。它相当于"机器人感觉到自己往哪边歪"，是 IMU 能算出来的。

> 论文写观测是"joint angles, joint velocities, projected gravity, and base angular velocities"，没提指令和上一步动作。代码里两者都有（指令当然必须给）。

### 3.11 奖励（`:254-276`）

#### 这段要干什么

覆盖父类的奖励权重，注释说"coefficients updated to match Margolis 2024"（按论文引用 [4] 调整）。

#### 代码

```python
if task == "Isaac-Velocity-Custom-Unitree-Go2-v0":
    self.rewards.track_lin_vel_xy_exp.weight = 1.0
    self.rewards.track_ang_vel_z_exp.weight = 0.5
    self.rewards.lin_vel_z_l2.weight = -2.0
    self.rewards.ang_vel_xy_l2.weight = -0.05
    self.rewards.flat_orientation_l2.weight = -0.1
    self.rewards.dof_torques_l2.weight = -1e-5
    self.rewards.dof_acc_l2.weight = -2.5e-7
    self.rewards.action_rate_l2.weight = -0.01
    self.rewards.feet_air_time.weight = 1.0
    self.rewards.dof_pos_limits.weight = -10.0

    self.rewards.base_height_l2 = RewTerm(
        func=mdp.base_height_l2, weight=-30.0, params={"target_height": 0.34}
    )
    self.rewards.undesired_contacts = RewTerm(
        func=mdp.undesired_contacts,
        weight=-1.0,
        params={
            "sensor_cfg": SceneEntityCfg("contact_forces", body_names=".*thigh|.*calf|.*hip"),
            "threshold": 1.0,
        },
    )
```

#### 每一项的含义

权重是**代码事实**；公式是【推断·Isaac Lab 默认】的函数定义，需核对。

| 奖励项 | 权重 | 公式（大意） | 鼓励/惩罚什么 |
|---|---|---|---|
| `track_lin_vel_xy_exp` | +1.0 | exp(−‖v_cmd,xy − v_xy‖² / σ²) | 水平速度跟上指令。误差 0 时得 1，误差越大越接近 0 |
| `track_ang_vel_z_exp` | +0.5 | exp(−(ωz_cmd − ωz)² / σ²) | 转向角速度跟上指令 |
| `lin_vel_z_l2` | −2.0 | v_z² | 惩罚上下颠簸 |
| `ang_vel_xy_l2` | −0.05 | ωx² + ωy² | 惩罚机身左右/前后晃 |
| `flat_orientation_l2` | −0.1 | g_x² + g_y²（投影重力的水平分量） | 惩罚机身倾斜 |
| `dof_torques_l2` | −1e-5 | Σ τᵢ² | 惩罚力矩大，即省能量 |
| `dof_acc_l2` | −2.5e-7 | Σ q̈ᵢ² | 惩罚关节加速度大，即动作要平滑 |
| `action_rate_l2` | −0.01 | Σ (aₜ − aₜ₋₁)² | 惩罚动作突变 |
| `feet_air_time` | +1.0 | Σ (腾空时间 − 阈值) × [刚落地] | 鼓励迈出完整的步子，不要小碎步拖地 |
| `dof_pos_limits` | −10.0 | 超出关节软限位的量 | 惩罚关节逼近极限 |
| `base_height_l2` | −30.0 | (h − 0.34)² | 机身高度保持 0.34 m（Go2 的站立高度） |
| `undesired_contacts` | −1.0 | 接触力 > 1 N 的大腿/小腿/髋的个数 | 惩罚除了脚以外的部位碰地 |

**数值例子（速度跟踪）**：【推断】父类 σ² = 0.25。指令 vx = 1.0，实际 vx = 0.8，vy = 0：误差² = 0.04，奖励 = exp(−0.04/0.25) = exp(−0.16) ≈ **0.85**。如果实际只有 0.5，误差² = 0.25，奖励 = exp(−1) ≈ **0.37**。所以速度差一点，奖励掉得不多；差很多，奖励掉得很快。

【推断·Isaac Lab 默认】奖励管理器每步会把"权重 × 函数值"再乘以策略步长 dt = 0.02 s，然后求和。

**这和论文 Table III 的"归一化任务回报"是什么关系？** 评估时只保留跟踪项（见下一节），所以论文的分数只反映"速度跟得准不准"，和步态好不好看无关。

#### 小结

奖励 = 2 个跟踪正奖励 + 若干稳定性/平滑性惩罚 + 1 个步态奖励。

> **迁移到 Go2-W 时**：`feet_air_time`（鼓励抬脚）和轮式滚动矛盾；`base_height_l2` 的 0.34 m 是 Go2 的数值；`undesired_contacts` 的身体名要换。见 §7。

### 3.12 评估模式（`:280-292`）

```python
if eval_mode:
    for key in self.rewards.__dict__.keys():
        if not key.startswith("track"):
            self.rewards.__dict__[key] = None

    if terminate_contacts:
        self.terminations.base_contact.params["sensor_cfg"].body_names = (
            "base|.*hip|.*thigh|Head_upper|Head_lower"
        )
```

| 改动 | 含义 |
|---|---|
| 删掉所有不以 `track` 开头的奖励 | 评估分只看**速度跟踪**，Table III 的数字就是这么来的 |
| 终止条件加严 | 机身、髋、大腿、头任一碰地就算摔倒，回合结束。摔倒后后面的跟踪奖励都拿不到，所以分数会低 |

【推断】"归一化到 [0, 1]"大概是用"每步最大可能跟踪奖励 × 回合长度"去除，具体在 runner 的 `evaluate` 函数里，见代码精读的训练部分。

### 3.13 注册任务（`:296-301`）

```python
gym.register(
    id=task,
    entry_point="omni.isaac.lab.envs:ManagerBasedRLEnv",
    disable_env_checker=True,
    kwargs={"env_cfg_entry_point": UnitreeGo2CustomEnvCfg, "rsl_rl_cfg_entry_point": UnitreeGo2CustomPPORunnerCfg},
)
```

- `gym.register`：把任务名登记到 gymnasium，之后 `gym.make(task)` 就能创建；
- `entry_point`：用 Isaac Lab 的通用 `ManagerBasedRLEnv` 类来创建；
- `kwargs`：告诉它环境配置类和训练器配置类是哪两个。

### 本节小结

| 部分 | GRAM 改了什么 |
|---|---|
| 地形 | 训练用平面；评估可选粗糙/坡；关掉课程 |
| 动作 | 自定义：髋幅度减半、关节零偏、可选关节冻结、限幅 |
| 执行器 | 自定义 DC 电机：12 个电机强度随机、可选电机故障 |
| 事件 | 加对抗推力（每步）、改质量范围、改摩擦（足端，64 档）、随机出生朝向、随机起始姿态 |
| 指令 | 速度范围 ±1 m/s，10 s 换一次 |
| 观测 | 去掉线速度和高度扫描，剩 45 维（推断） |
| 奖励 | 按 Margolis 2024 改权重；加机身高度和非足端接触惩罚 |
| 评估 | 只留跟踪奖励；严格摔倒判定 |

---

## 4. `envs_utils.py`：自定义的动作、事件、电机

这是环境部分**最需要细读**的文件，因为"电机强度""关节零偏""冻结关节""电机故障""对抗推力"全在这里实现。

### 4.1 `ScaledJointPositionAction`：缩放动作与关节冻结（`:29-100`）

#### 这段要干什么

在 Isaac Lab 的标准"关节位置动作"上加两样东西：
1. 髋关节的动作幅度单独缩小；
2. 可以让某些关节的动作乘一个倍数（倍数为 0 = 冻结）。

#### (a) 构造函数（`:37-49`）

```python
def __init__(self, cfg: ScaledJointPositionActionCfg, env: ManagerBasedRLEnv):
    super().__init__(cfg, env)

    # scale with hip mult
    scale_vec = torch.ones_like(self._offset) * self.cfg.scale
    scale_vec[:, :4] *= self.cfg.hip_scale_mult
    self._scale = scale_vec

    # default action scale
    self._action_scale = torch.ones((self.num_envs, self.action_dim), dtype=torch.float32, device=self.device)

    self._set_action_scale()
```

| 行 | 解释 |
|---|---|
| 39 | 调用父类，父类会准备好 `_offset`（默认站姿角度）、`_raw_actions` 等 |
| 42 | `scale_vec`：形状和 `_offset` 一样 (num_envs, 12)，每个元素都是 0.25 |
| 43 | **前 4 列**再乘 0.5 → 0.125。【推断】Isaac Lab 里 Go2 的关节顺序是按"类型优先"排的：前 4 个是 4 条腿的髋关节，接着 4 个大腿、4 个小腿。这一行就是靠这个顺序假设"前 4 个是髋" |
| 44 | 存为每个关节的缩放 |
| 47 | `_action_scale`：每个环境、每个关节一个倍数，默认全 1 |
| 49 | 按配置设置倍数（冻结） |

> **为什么髋关节幅度要小？** 髋关节负责腿的左右外展，幅度太大机器人容易"劈叉"。这是常见的工程技巧。
>
> **注意**：`[:, :4]` 是硬编码。迁移到 Go2-W（16 个关节）时，关节顺序会变，这一行必须重写，见 §7。

#### (b) 设置关节倍数：`_set_action_scale`（`:51-90`）

这是"冻结关节"的实现，逻辑有点绕，用一个例子慢慢走。

```python
def _set_action_scale(self):
    action_scale_default = np.ones((self.num_envs, self.action_dim))

    if self.cfg.action_mult_indices is not None:
        action_scale_mask_options = np.zeros((len(self.cfg.action_mult_indices), self.action_dim))
        for row_idx, action_idx in enumerate(self.cfg.action_mult_indices):
            if not (action_idx == [-1]):
                action_scale_mask_options[row_idx, action_idx] = 1.0

        mask_indices = np.random.choice(len(self.cfg.action_mult_indices), self.num_envs)
        action_scale_idx_mask = action_scale_mask_options[mask_indices]
        action_scale_default_mask = 1.0 - action_scale_idx_mask

        if self.cfg.action_mult_count is not None:
            idx_scale_choices = np.linspace(
                self.cfg.action_mult_min, self.cfg.action_mult_max, self.cfg.action_mult_count
            )
            if idx_scale_choices.shape[0] > 1:
                action_scale_idx_mults = np.random.choice(idx_scale_choices, self.num_envs)
            else:
                action_scale_idx_mults = np.ones(self.num_envs) * idx_scale_choices[0]
        else:
            if self.cfg.action_mult_min < self.cfg.action_mult_max:
                action_scale_idx_mults = self.cfg.action_mult_min + (
                    np.random.random(self.num_envs) * (self.cfg.action_mult_max - self.cfg.action_mult_min)
                )
            else:
                action_scale_idx_mults = np.ones(self.num_envs) * self.cfg.action_mult_min

        action_scale_idx_mults = np.expand_dims(action_scale_idx_mults, axis=-1)
        action_scale_idx_active = action_scale_idx_mask * action_scale_idx_mults
        action_scale_default_active = action_scale_default_mask * action_scale_default

        action_scale = action_scale_default_active + action_scale_idx_active
    else:
        action_scale = action_scale_default

    self._action_scale[:] = torch.tensor(action_scale, dtype=torch.float32, device=self.device)
```

**`action_mult_indices` 的格式**：一个"列表的列表"，每个子列表是**一种冻结方案**。例如命令行写

```
--action_mult_indices 2 --action_mult_indices 3 --action_mult_indices -1
```

得到 `[[2], [3], [-1]]`，意思是三种方案：只冻结关节 2、只冻结关节 3、不冻结（`-1` 表示"空方案"）。

**逐步走一遍**（假设 3 个环境、4 个关节，方案 `[[2],[3],[-1]]`，min = max = 0）：

1. `action_scale_mask_options`（3 种方案 × 4 关节）：
   ```
   方案0: [0, 0, 1, 0]   ← 关节 2 被选中
   方案1: [0, 0, 0, 1]   ← 关节 3 被选中
   方案2: [0, 0, 0, 0]   ← -1，谁都不选
   ```
2. `mask_indices`：给每个环境随机挑一种方案，比如 [1, 0, 2]。
3. `action_scale_idx_mask`：
   ```
   环境0: [0, 0, 0, 1]
   环境1: [0, 0, 1, 0]
   环境2: [0, 0, 0, 0]
   ```
4. `action_scale_default_mask = 1 − 上面`：没被选中的关节为 1。
5. 倍数：min = max = 0，走 `else` 分支，全是 0。
6. 合成：被选中的关节 = 0，其余 = 1：
   ```
   环境0: [1, 1, 1, 0]   ← 关节 3 冻结
   环境1: [1, 1, 0, 1]   ← 关节 2 冻结
   环境2: [1, 1, 1, 1]   ← 正常
   ```

**三种倍数取法**：
- 给了 `action_mult_count`：在 [min, max] 等间隔取 count 个值，每个环境随机挑一个（离散）；
- min < max：在 [min, max] 均匀随机（连续）；
- min = max：所有环境同一个值（GRAM 默认，0）。

#### (c) 动作处理（`:96-100`）

```python
def process_actions(self, actions: torch.Tensor):
    self._raw_actions[:] = actions
    self._processed_actions = (self._raw_actions * self._action_scale) * self._scale + self._offset
```

目标角 = 原始输出 × 关节倍数 × 缩放 + 默认角。这个类的子类（§4.2）会再加零偏和限幅。

#### 关键理解："冻结"到底冻结了什么？

当倍数 = 0：目标角 = 0 × ... + 默认角 = **默认站姿角**，不管网络输出什么。

然后 PD 控制器会用 25 N·m/rad 的"弹簧"**把这个关节拉回默认角**。所以：
- 这个关节**不是锁死不动**：受外力时它会偏离，然后被弹回；
- 它**也不是无力**：它仍然有力，只是一直想回到默认角。

更准确的说法是"**这个关节不再听网络的指挥，固定伺服在站姿角上**"。

> 实机上"冻结关节"如果是用机械方式锁住，或者设成高刚度位置锁，行为会不同。论文没说实机怎么做的。这是论文与代码之间一个值得注意的细节。

#### (d) 配置类（`:106-119`）

```python
@configclass
class ScaledJointPositionActionCfg(mdp.JointPositionActionCfg):
    class_type: type[ActionTerm] = ScaledJointPositionAction
    hip_scale_mult: float = 1.0
    action_mult_indices: list = None
    action_mult_min: float = 1.0
    action_mult_max: float = 1.0
    action_mult_count: int = None
```

`class_type` 告诉 Isaac Lab："用这个配置时，创建 `ScaledJointPositionAction` 类的对象"。这是 Isaac Lab 中"配置 ↔ 实现"的绑定方式。

### 4.2 `ShiftScaleClampJointPositionAction`：零偏与限幅（`:125-189`）

#### 这段要干什么

在 §4.1 基础上再加两步：
1. **关节零偏**（shift）：每个关节加一个固定的随机偏移，模拟"关节零位标定不准"；
2. **限幅**（clamp）：目标角不超过关节物理极限。

#### (a) 构造与零偏采样（`:133-155`）

```python
def __init__(self, cfg, env):
    super().__init__(cfg, env)
    self._action_shift = torch.zeros((self.num_envs, self.action_dim), dtype=torch.float32, device=self.device)
    self._set_action_shift()
    self.joint_pos_min = self._asset.data.default_joint_limits[..., 0]
    self.joint_pos_max = self._asset.data.default_joint_limits[..., 1]

def _set_action_shift(self):
    if self.cfg.joint_bias_min < self.cfg.joint_bias_max:
        action_shift = self.cfg.joint_bias_min + (
            np.random.random((self.num_envs, self.action_dim)) * (self.cfg.joint_bias_max - self.cfg.joint_bias_min)
        )
    else:
        action_shift = np.ones((self.num_envs, self.action_dim)) * self.cfg.joint_bias_min
    self._action_shift[:] = torch.tensor(action_shift, dtype=torch.float32, device=self.device)
```

- 每个环境、每个关节独立在 [−0.1, 0.1] rad 里均匀采一个偏移；
- **只在构造时采一次**，整个训练期间不变；
- `default_joint_limits[..., 0]` / `[..., 1]`：每个关节的下限 / 上限。

#### (b) 完整计算链（`:160-168`）

```python
def process_actions(self, actions: torch.Tensor):
    self._raw_actions[:] = actions
    processed_actions = (self._raw_actions * self._action_scale) * self._scale + self._offset + self._action_shift
    if self.cfg.joint_pos_clamp:
        processed_actions.clamp_(min=self.joint_pos_min, max=self.joint_pos_max)
    self._processed_actions[:] = processed_actions
```

**完整公式**：

$$q^*_j = \text{clamp}\Big(a_j \cdot m_j \cdot s_j + q^{default}_j + b_j,\ q^{min}_j,\ q^{max}_j\Big)$$

| 符号 | 代码变量 | 含义 |
|---|---|---|
| a_j | `_raw_actions` | 网络输出 |
| m_j | `_action_scale` | 关节倍数（1 = 正常，0 = 冻结） |
| s_j | `_scale` | 0.25，髋关节 0.125 |
| q_j^default | `_offset` | 默认站姿角 |
| b_j | `_action_shift` | 关节零偏，[−0.1, 0.1] rad |

#### (c) 数值例子：一个小腿关节

【推断】Go2 小腿关节默认站姿角约 −1.5 rad（Isaac Lab Go2 配置，需核对；这里只是为了演示）。

| 步骤 | 计算 | 结果 |
|---|---|---|
| 网络输出 | a = 0.8 | 0.8 |
| × 关节倍数（正常） | 0.8 × 1 | 0.8 |
| × 缩放 | 0.8 × 0.25 | 0.20 rad |
| + 默认角 | 0.20 + (−1.5) | −1.30 rad |
| + 零偏（这个环境采到 +0.07） | −1.30 + 0.07 | **−1.23 rad** |
| 限幅 | 在关节范围内 | −1.23 rad |

**再看同一关节被冻结时**：倍数 = 0 → 0 + (−1.5) + 0.07 = −1.43 rad。注意：**冻结后零偏还在**，所以关节其实固定在"带偏差的默认角"上。

**髋关节**：同样 a = 0.8，缩放是 0.125，只偏移 0.10 rad。

#### (d) 关节零偏的物理含义

零偏 b 加在**目标角**上，对网络来说相当于：
"我让它转到 −1.30，它实际去了 −1.23。"
这模拟了**实机编码器零位标定误差**：你以为的 0° 和电机认为的 0° 不一样。网络需要从运动历史中把这个偏差"认出来"并补偿。

> **一个容易混淆的点**：零偏改的是"目标角"，不是"观测到的关节角"。观测里的关节角仍然是真实值。

#### 小结

动作链：**网络输出 → ×冻结倍数 → ×0.25（髋 0.125） → +站姿 → +零偏 → 限幅 → PD**。其中"冻结倍数"和"零偏"都是**每个环境在创建时随机一次**。

### 4.3 `randomize_friction`：64 档摩擦（`:195-264`）

#### 这段要干什么

给每个环境的足端设置一个随机摩擦系数。这是对 Isaac Lab 自带 `randomize_rigid_body_material` 的修改版。

#### 代码分段讲解

**(1) 取出资产、整理环境编号（`:212-224`）**

```python
asset: RigidObject | Articulation = env.scene[asset_cfg.name]
...
if env_ids is None:
    env_ids = torch.arange(env.scene.num_envs, device="cpu")
else:
    env_ids = env_ids.cpu()
```

`startup` 模式下 `env_ids` 是 None，就处理所有环境。注意放到 **CPU** 上：PhysX 的材质接口要求 CPU 张量。

**(2) 先全部设成默认（`:227-231`）**

```python
materials = asset.root_physx_view.get_material_properties()
materials[..., 0] = static_friction_default   # 0.8
materials[..., 1] = dynamic_friction_default  # 0.6
materials[..., 2] = restitution_default       # 0.0
```

- `materials` 的形状：(环境数, 碰撞形状数, 3)。最后一维 3 个数是 [静摩擦, 动摩擦, 弹性]。
- 机器人的**所有**碰撞形状（身体、腿、脚）先统一设成默认。

**(3) 64 档采样（`:234-236`）**

```python
friction_mult_buckets = torch.linspace(friction_mult_range[0], friction_mult_range[1], num_buckets, device="cpu")
friction_mult_idx = torch.randint(num_buckets, (env.scene.num_envs,), device="cpu")
friction_mult = friction_mult_buckets[friction_mult_idx]
```

- `linspace(0.05, 4.5, 64)`：在 0.05 到 4.5 之间等间隔取 64 个值，间隔 = (4.5 − 0.05) / 63 ≈ **0.0706**；
- 每个环境随机挑一档。

> **为什么分"桶"而不是连续随机？** PhysX 中每种不同的摩擦组合都要创建一种物理材质，而材质数量有上限。分成 64 档，最多只需要 64 种材质。这是工程上的限制，Isaac Lab 原版也这么做。

**(4) 只改指定部位：足端（`:239-261`）**

```python
if isinstance(asset, Articulation) and asset_cfg.body_ids != slice(None):
    num_shapes_per_body = []
    for link_path in asset.root_physx_view.link_paths[0]:
        link_physx_view = asset._physics_sim_view.create_rigid_body_view(link_path)
        num_shapes_per_body.append(link_physx_view.max_shapes)

    for body_id in asset_cfg.body_ids:
        start_idx = sum(num_shapes_per_body[:body_id])
        end_idx = start_idx + num_shapes_per_body[body_id]
        materials[:, start_idx:end_idx, 0] = static_friction_default * friction_mult.unsqueeze(dim=-1)
        materials[:, start_idx:end_idx, 1] = dynamic_friction_default * friction_mult.unsqueeze(dim=-1)
else:
    materials[..., 0] = static_friction_default * friction_mult.unsqueeze(dim=-1)
    materials[..., 1] = dynamic_friction_default * friction_mult.unsqueeze(dim=-1)
```

- 一个"刚体"（如一只脚）可能由几个碰撞形状组成。代码先数清每个刚体有几个形状，然后按顺序找到"脚"对应的形状区间；
- 只把脚的摩擦乘上倍数；身体、腿保持 0.8 / 0.6。
- `body_ids`：由 `body_names=".*foot"` 匹配出来的 4 只脚的编号。

**(5) 写回仿真（`:264`）**

```python
asset.root_physx_view.set_material_properties(materials, env_ids)
```

#### 数值例子

某环境采到第 10 档：倍数 = 0.05 + 10 × 0.0706 ≈ 0.756。
- 静摩擦 = 0.8 × 0.756 ≈ 0.605；
- 动摩擦 = 0.6 × 0.756 ≈ 0.454。

最滑的档：0.8 × 0.05 = **0.04**（像冰面）；最粘的档：0.8 × 4.5 = **3.6**。

> 【推断】PhysX 中两个物体接触时，实际摩擦是两者材质的组合（默认取平均）。所以脚和地面接触时的有效摩擦还取决于**地面材质**。上下文里记录的是"脚的摩擦"，不是"有效摩擦"。这一点不影响训练逻辑，但解释"摩擦倍数 0.05 有多滑"时要留心。

#### 小结

摩擦：**每个环境在创建时从 64 档中随机挑一档**，只改脚，静/动摩擦同比例缩放。

### 4.4 `adversarial_push_by_setting_velocity`：对抗推力（`:270-296`）

#### 这段要干什么

按对抗者的决定，给被选中的机器人机身突然加一个水平速度，模拟"被推了一下"。

#### 代码

```python
def adversarial_push_by_setting_velocity(
    env, env_ids, magnitude=0.0, adversary_actions=None, adversary_masks=None,
    asset_cfg=SceneEntityCfg("robot"),
):
    asset: RigidObject | Articulation = env.scene[asset_cfg.name]

    if (adversary_actions is not None) and (adversary_masks is not None) and (magnitude > 0):
        vel_w = asset.data.root_vel_w[env_ids]
        processed_adversary_actions = adversary_actions.clamp(min=-1, max=1)
        vel_xy_push_all = magnitude * processed_adversary_actions
        vel_xy_push = vel_xy_push_all[env_ids]
        vel_w[:, :2] += adversary_masks[env_ids] * vel_xy_push
        asset.write_root_velocity_to_sim(vel_w, env_ids=env_ids)
```

#### 逐行解释

| 代码 | 解释 |
|---|---|
| `if ... magnitude > 0` | 三个条件都满足才推。评估时 magnitude = 0，**永远不推** |
| `root_vel_w` | 机身在**世界坐标系**下的速度，6 维：[vx, vy, vz, ωx, ωy, ωz] |
| `clamp(-1, 1)` | 推力向量每个分量限制在 [−1, 1] |
| `magnitude * ...` | 乘总幅值（训练时 1.0） |
| `vel_w[:, :2] += mask * push` | **只改前两维（水平 vx、vy）**；mask 为 1 才加，为 0 不加 |
| `write_root_velocity_to_sim` | 把新速度直接写进仿真器 |

#### `adversary_actions` 和 `adversary_masks` 从哪来？

由训练代码每步写进这个事件的参数（`gram_ppo.py:99-117`、`gram_adversary.py:135-149`）：

1. 对抗者网络看到机器人的观测，输出一个**角度 θ**；
2. 转成向量：(cos θ, sin θ) × 随机大小，随机大小在 [0, 当前最大值] 均匀取，当前最大值随训练进度从 0 线性增长到 1；
3. **掩码** = 伯努利(0.05) × 鲁棒掩码：
   - 每个机器人每步有 5% 概率被推；
   - 而且**只推鲁棒组的机器人**，自适应组不推。

#### 数值例子

训练进行到一半：最大值 = 0.5。某机器人这一步被选中（5% 概率），对抗者输出 θ = 90°，随机大小采到 0.3：
- 推力向量 = 0.3 × (cos90°, sin90°) = (0, 0.3)；
- 若机身原速度 (0.8, 0.0) m/s，推后变成 (0.8, **0.3**) m/s，机器人突然往左侧滑。

#### 关键理解："改速度"不等于"施加力"

| | 施加外力 | 直接改速度（GRAM 代码） |
|---|---|---|
| 物理过程 | 力持续作用一段时间，速度逐渐变化 | 速度瞬间跳变，相当于一次**无限短的冲击** |
| 和质量的关系 | 同样的力，越重的机器人速度变化越小 | **和质量无关**：加 3 kg 的机器人也被推出同样的速度 |
| 冲量 | F × Δt | m × Δv，随质量变化 |

**为什么这么做？** 简单、好控制，Isaac Lab 自带的 `push_by_setting_velocity` 也是这样实现的。

**对理解论文的影响**：论文说"applies forward and lateral external forces"，严格说是**速度冲击**。这不影响结论，但老师若问"推力有多大（多少牛顿）"，正确的回答是："代码里是直接给机身水平速度加最多 1 m/s 的增量，不是以牛顿为单位的力。"

### 4.5 `reset_joints_train`：从"趴"到"站"的随机起始姿态（`:301-339`）

#### 这段要干什么

训练时每次重置，让机器人从趴下和站立之间的某个姿态开始，并加一点随机扰动，让策略学会起身。

#### 代码（核心部分）

```python
default_joint_pos = asset.data.default_joint_pos[env_ids].clone()
joint_vel = asset.data.default_joint_vel[env_ids].clone()

down_joint_pos = torch.tensor(
    [[0.10, -0.10, 0.10, -0.10, 1.36, 1.36, 1.36, 1.36, -2.65, -2.65, -2.65, -2.65]],
    device=default_joint_pos.device,
)

low, high = stand_range
stand_weight = torch.rand(*(default_joint_pos.shape[0], 1), device=...) * (high - low) + low

low, high = position_delta_range
add_joint_pos = torch.rand(*default_joint_pos.shape, device=...) * (high - low) + low

joint_pos = down_joint_pos + stand_weight * (default_joint_pos - down_joint_pos)
joint_pos += add_joint_pos
...限幅到软限位...
asset.write_joint_state_to_sim(joint_pos, joint_vel, env_ids=env_ids)
```

#### 逐行解释

| 代码 | 解释 |
|---|---|
| `down_joint_pos` | **趴下姿态**的 12 个关节角：4 个髋 ±0.10，4 个大腿 1.36，4 个小腿 −2.65（腿完全折叠）。也印证了"前 4 个是髋、中间 4 个大腿、后 4 个小腿"的顺序 |
| `stand_weight` | 每个机器人一个 [0, 1] 的随机数 w |
| `joint_pos = down + w × (default − down)` | **线性插值**：w = 0 → 趴着；w = 1 → 站着；w = 0.5 → 半蹲 |
| `add_joint_pos` | 每个关节再加 [−0.1, 0.1] rad 的随机扰动 |
| 限幅 | 不超过关节软限位 |
| `joint_vel` | 初始关节速度用默认值（一般为 0） |

#### 数值例子

小腿：趴 −2.65，假设站立默认角 −1.5【推断】；w = 0.3：
−2.65 + 0.3 × (−1.5 − (−2.65)) = −2.65 + 0.345 = **−2.305 rad**，再加一点扰动。

#### 小结

训练时起始姿态在"趴—站"之间随机，评估时不用这个函数（用父类的默认重置）。

### 4.6 `ScaledDCMotor`：电机强度与电机故障（`:345-389`）

这是**对我们方向最重要的一段代码**：电机强度是 GRAM 上下文里的 12 维；电机故障接口是做容错实验的起点。

#### 先懂：DC 电机模型（Isaac Lab 的 `DCMotor`）

真实电机的最大力矩不是一个固定值，而是**随转速下降**：转得越快，能输出的力矩越小。这就是**力矩—转速曲线**。

【推断·Isaac Lab 默认】`DCMotor` 的限幅规则大致是：

$$\tau_{max}(\dot q) = \tau_{sat}\Big(1 - \frac{\dot q}{\dot q_{max}}\Big),\qquad \tau_{min}(\dot q) = \tau_{sat}\Big(-1 - \frac{\dot q}{\dot q_{max}}\Big)$$

再与 ±effort_limit 取交集。

用 Go2 的参数（τ_sat = 23.5 N·m，q̇_max = 30 rad/s）：

| 关节转速 q̇（同向） | 能输出的最大力矩 |
|---|---|
| 0 rad/s | 23.5 N·m |
| 10 rad/s | 23.5 × (1 − 1/3) ≈ 15.7 N·m |
| 20 rad/s | 23.5 × (1 − 2/3) ≈ 7.8 N·m |
| 30 rad/s | 0 N·m |

**控制视角**：这就是电机的**输出饱和**，而且饱和边界随转速变化。

#### (a) 构造：采样电机强度（`:351-371`）

```python
def __init__(self, cfg, *args, **kwargs):
    super().__init__(cfg, *args, **kwargs)
    self._set_effort_scale()

def _set_effort_scale(self):
    self._effort_scale = torch.ones_like(self.computed_effort)
    self._effort_scale.uniform_(self.cfg.motor_strength_mult_min, self.cfg.motor_strength_mult_max)

    if self.cfg.motor_fault_indices is not None:
        motor_fault_mask_options = np.ones((len(self.cfg.motor_fault_indices), self._effort_scale.shape[-1]))
        for row_idx, action_idx in enumerate(self.cfg.motor_fault_indices):
            if not (action_idx == [-1]):
                motor_fault_mask_options[row_idx, action_idx] = 0.0

        mask_indices = np.random.choice(len(self.cfg.motor_fault_indices), self._effort_scale.shape[0])
        motor_fault_mask = motor_fault_mask_options[mask_indices]
        motor_fault_mask = torch.tensor(motor_fault_mask, dtype=torch.float32, device=self._effort_scale.device)

        self._effort_scale[:] = self._effort_scale * motor_fault_mask
```

| 行 | 解释 |
|---|---|
| `computed_effort` | 父类的"计算出的力矩"张量，形状 (环境数, 12) |
| `uniform_(0.8, 1.2)` | 每个环境、每个电机独立在 [0.8, 1.2] 均匀采一个倍数 |
| `motor_fault_indices` | 格式和 §4.1 的 `action_mult_indices` 一样：每个子列表是一种故障方案，`[-1]` = 无故障 |
| `motor_fault_mask_options` | 默认全 1；被选中的电机置 **0** |
| `mask_indices` | 每个环境随机挑一种方案 |
| 最后一行 | 强度倍数 × 故障掩码：故障电机倍数变成 **0** |

**和 §4.1 的区别**：冻结关节是把**动作**乘 0（关节被 PD 拉回站姿，仍然有力）；电机故障是把**力矩**乘 0（关节**完全无力**，像断电一样随外力摆动）。

#### (b) 力矩限幅时乘上倍数（`:376-379`）

```python
def get_effort_scale(self):
    return self._effort_scale

def _clip_effort(self, effort: torch.Tensor) -> torch.Tensor:
    scaled_effort = self._effort_scale * effort
    return super()._clip_effort(scaled_effort)
```

- 父类在算完 PD 力矩后，会调用 `_clip_effort` 做饱和限幅；
- GRAM 重写了这个函数：**先乘强度倍数，再按 DC 电机曲线限幅**。

**完整的力矩计算链**：

$$\tau_{applied} = \text{clip}_{DC}\Big(k_j \cdot \big[K_p(q^* - q) - K_d \dot q\big]\Big)$$

k_j 是第 j 个电机的强度倍数。

#### (c) 数值例子

接 §0.5 的例子，PD 算出 1.5 N·m：

| 情况 | k | 乘倍数后 | 限幅后（低速时上限 23.5） |
|---|---|---|---|
| 正常电机 | 1.0 | 1.5 | 1.5 N·m |
| 弱电机 | 0.8 | 1.2 | 1.2 N·m |
| 强电机 | 1.2 | 1.8 | 1.8 N·m |
| 故障电机 | 0 | 0 | **0 N·m** |

需要大力矩时差别更明显：PD 算出 22 N·m、转速 10 rad/s 时：
- k = 1.0：22 → 被限到 15.7 N·m；
- k = 0.8：17.6 → 被限到 15.7 N·m；
- k = 1.2：26.4 → 被限到 15.7 N·m。

> **一个有意思的结论**：由于倍数乘在**限幅之前**，k > 1 的"强电机"在饱和时并不能输出更多力矩，上限还是 DC 曲线。也就是说，电机强度主要改变的是"**等效增益**"（相当于 Kp、Kd 都乘了 k），而不是"最大力气"。这是读代码才能发现的细节，论文的"motor strength multiple"字面上看不出来。
>
> 从控制角度：k 相当于**执行器增益不确定性**，这在控制里是一个经典的不确定性类型。

#### (d) 配置类（`:382-389`）

```python
@configclass
class ScaledDCMotorCfg(DCMotorCfg):
    class_type: type = ScaledDCMotor
    motor_strength_mult_min: float = 1.0
    motor_strength_mult_max: float = 1.0
    motor_fault_indices: list = None
```

#### 对我们的意义

| 问题 | 答案 |
|---|---|
| 电机故障接口能直接用吗？ | 能用，命令行 `--motor_fault_indices` 即可 |
| 能模拟"跑着跑着电机坏了"吗？ | **不能**。`_set_effort_scale` 只在构造时调用一次，故障从一开始就存在，整个训练/评估期间不变 |
| 故障信息进上下文了吗？ | 间接进了：上下文读的是 `get_effort_scale()`（§5.3），故障电机的倍数是 0。按训练范围 [0.8, 1.2] 归一化后是 (0 − 0.8)/0.4 × 2 − 1 = **−5**，远超 [−1, 1]，是一个很强的 OOD 信号 |
| 要做运行中故障怎么办？ | 加一个 `interval` 事件，在某个时刻修改 `_effort_scale`，见 §8 |

---

## 5. `context_env_wrapper.py`：把 26 维上下文交给网络

### 这段要干什么

强化学习库 rsl_rl 只认识"观测、动作、奖励"，不知道"上下文"。这个包装器在 Isaac Lab 的标准包装器上加一个 `get_context()` 方法，把每个环境的环境参数读出来、归一化、拼成一个向量，供教师网络使用。

### 5.1 包装器是什么

**包装器（wrapper）**：在一个对象外面再套一层，增加或修改功能，但对外接口不变。

```
ManagerBasedRLEnv（Isaac Lab 原生环境）
   ↓ 套一层
RslRlVecEnvWrapper（Isaac Lab 提供：把接口转成 rsl_rl 要的样子）
   ↓ 再套一层
ContextRslRlVecEnvWrapper（GRAM 写的：加上 get_context）
```

`RslRlVecEnvWrapper` 负责把 Isaac Lab 的环境变成 rsl_rl 的 `VecEnv` 接口：
- `get_observations()` → 返回 (观测, 额外信息)；
- `step(actions)` → 返回 (观测, 奖励, 是否结束, 额外信息)；
- 还有 `num_envs`、`num_actions` 等属性。

GRAM 的 runner 在初始化时调用 `self.env.get_context()`（`gram_on_policy_runner.py:40`），拿到上下文的维度来构建网络。

> 服务器兼容版中，新版 Isaac Lab 的包装器已改成 TensorDict 接口，所以专门从 v1.0 复制了旧包装器（`source/compat/rsl_rl_vecenv_v1.py`），保持元组接口不变。

### 5.2 `__init__` 与 `_setup_context_args`（`:13-106`）

```python
def __init__(self, env, inputs_cfg):
    super().__init__(env)
    self._setup_context_args(inputs_cfg)
    self._set_context()
```

`_setup_context_args` 对五类参数（质量、摩擦、动作倍数、关节零偏、电机强度）重复同一个模式。以质量为例（`:21-35`）：

```python
self.base_mass_context_include = inputs_cfg.base_mass_context_include
self.base_mass_context_scale = inputs_cfg.base_mass_context_scale
if self.base_mass_context_include and self.base_mass_context_scale:
    if inputs_cfg.base_mass_context_scale_min is not None:
        self.base_mass_context_scale_min = inputs_cfg.base_mass_context_scale_min
    else:
        self.base_mass_context_scale_min = inputs_cfg.base_mass_min
    ...max 同理...
    self.base_mass_context_scale_range = self.base_mass_context_scale_max - self.base_mass_context_scale_min
```

意思是：记下"要不要包含""要不要归一化"，以及归一化的最小值和区间宽度；如果没单独指定归一化区间，就用随机范围。

**摩擦多了一行**（`:51`）：`self.default_friction = 0.8`，即默认静摩擦，用来把绝对摩擦换算回倍数。

### 5.3 `_set_context`：逐类读出并归一化（`:108-199`）

#### 统一的归一化公式

除摩擦需要先换算外，每一类都用：

$$x_{context} = -1 + 2\cdot\frac{x - x_{min}}{x_{max} - x_{min}}$$

把训练范围 [x_min, x_max] 线性映射到 **[−1, 1]**。训练范围内 → [−1, 1]；范围外 → 超出 [−1, 1]。

> 你给的任务说明里提到"[−1,1] 或 [0,1]"。代码里**全部是 [−1, 1]**：先算 0–1 的比例，再 ×2 −1。

#### (1) 质量（`:113-130`）

```python
term_cfg = self.unwrapped.event_manager.get_term_cfg("add_base_mass")
asset_cfg = term_cfg.params["asset_cfg"]
asset = self.unwrapped.scene[asset_cfg.name]
body_ids = asset_cfg.body_ids
mass = asset.root_physx_view.get_masses()
default_mass = asset.data.default_mass
delta_mass = mass[:, body_ids] - default_mass[:, body_ids]
...
delta_shift_scale = (delta_mass - self.base_mass_context_scale_min) / self.base_mass_context_scale_range
delta_mass_context = -1 + 2 * delta_shift_scale
```

- 从"加质量"事件的配置里找到它作用于哪个刚体（机身）；
- **当前质量 − 默认质量 = 加了多少**；
- 归一化。维度 **1**。

**例子**：加了 1 kg → (1 − (−1)) / 4 = 0.5 → −1 + 1 = **0.0**。

#### (2) 摩擦（`:133-155`）

```python
term_cfg = self.unwrapped.event_manager.get_term_cfg("physics_material")
...
materials = asset.root_physx_view.get_material_properties()
self.materials = materials[:, -1, :].to(device=self.device)
friction = self.materials[:, :1]

friction_mult = friction / self.default_friction
friction_shift_scale = (friction_mult - self.friction_mult_context_scale_min) / self.friction_mult_context_scale_range
friction_context = -1 + 2 * friction_shift_scale
```

| 行 | 解释 |
|---|---|
| `materials[:, -1, :]` | 取**最后一个**碰撞形状的材质。注释说"−1 index captures material of a foot"，即假设最后一个形状是一只脚 |
| `[:, :1]` | 只取静摩擦（静、动摩擦是同一个倍数缩放的，取一个就够） |
| `friction / 0.8` | 换算回倍数 |
| 归一化 | 到 [−1, 1]。维度 **1** |

**例子**：倍数 0.756 → 静摩擦 0.605 → 0.605/0.8 = 0.756 → (0.756 − 0.05)/4.45 ≈ 0.159 → −1 + 0.317 = **−0.683**。

> **一个隐含假设**："最后一个碰撞形状是脚"依赖 Go2 模型中刚体和形状的排列顺序。迁移到 Go2-W 时，最后一个形状可能是轮子，也可能是别的，必须核对。

#### (3) 动作倍数（`:158-169`）

```python
if self.action_mult_context_include:
    action_scale = self.unwrapped.action_manager.get_term("joint_pos").action_scale.detach()
    ...
```

默认 `action_mult_context_include = False`，**不进上下文**。所以"冻结关节"对网络是不可见的。如果打开，会多 12 维。

#### (4) 关节零偏（`:172-183`）

```python
action_shift = self.unwrapped.action_manager.get_term("joint_pos").action_shift.detach()
action_shift_context = -1 + 2 * (action_shift - (-0.1)) / 0.2
```

直接从动作项读出 12 个零偏，归一化。维度 **12**。

**例子**：零偏 +0.07 rad → (0.07 + 0.1)/0.2 = 0.85 → **0.7**。

#### (5) 电机强度（`:186-197`）

```python
motor_scale = self.unwrapped.scene["robot"].actuators["base_legs"].get_effort_scale()
motor_scale_context = -1 + 2 * (motor_scale - 0.8) / 0.4
```

通过执行器名字 `"base_legs"` 拿到 12 个强度倍数，归一化。维度 **12**。

**例子**：k = 1.1 → (1.1 − 0.8)/0.4 = 0.75 → **0.5**；故障电机 k = 0 → **−5.0**。

#### (6) 记录维度（`:199`）

```python
self.context_dim = self.context.shape[1]
```

### 5.4 上下文的最终顺序与维度

| 位置 | 内容 | 维度 |
|---|---|---|
| 0 | 附加质量 | 1 |
| 1 | 摩擦倍数 | 1 |
| （动作倍数） | 默认不包含 | 0 |
| 2–13 | 12 个关节零偏 | 12 |
| 14–25 | 12 个电机强度 | 12 |
| **合计** | | **26** |

> 论文 Table II 的列出顺序是"摩擦、质量、电机、零偏"，**和代码的拼接顺序不同**。读代码或做分组时，以代码顺序为准。

### 5.5 一个非常重要的事实：上下文只读一次

```python
def __init__(self, env, inputs_cfg):
    super().__init__(env)
    self._setup_context_args(inputs_cfg)
    self._set_context()          # ← 只在这里调用

def get_context(self) -> torch.Tensor:
    return self.context          # ← 直接返回存好的值
```

【代码事实】`_set_context` 只在包装器创建时调用一次，`get_context` 每次都返回同一个张量。

结合前面几节：
- 摩擦：`startup` 事件，创建时一次；
- 质量：【推断】`startup` 事件，创建时一次；
- 关节零偏：动作项构造时一次；
- 电机强度/故障：执行器构造时一次。

**结论**：在 GRAM 的训练中，**每个环境（4096 个中的每一个）的 26 维上下文从头到尾是固定的**。机器人摔倒、重置、开始新回合，上下文都不变。训练相当于"4096 台参数各不相同的机器狗，各自练了 10000 次迭代"。

**对我们的影响**：
1. 这解释了为什么仓库里**没有运行中变化的代码**：整个设计就是"每个环境一套固定参数"；
2. 要做"运行中加载荷/电机突然坏了"，不仅要加事件修改物理参数，还要**同步更新** `self.context`，否则教师网络看到的上下文就是错的（见 §8）；
3. 4096 个环境意味着上下文空间被 4096 个点采样。26 维空间里 4096 个点其实很稀疏，这可能是为什么上下文要先压缩到 8 维。【我们的推断】

### 小结

上下文包装器 = 在 rsl_rl 接口上加 `get_context()`；26 维 = 质量 1 + 摩擦 1 + 零偏 12 + 电机 12；全部归一化到 [−1, 1]（以训练范围为标尺）；**创建时读一次，之后不变**。

---

## 6. 一张图串起来：一个策略步里发生了什么

```
[训练代码] 网络输出 a (4096×12)
     │                          [训练代码] 对抗者：θ、大小、5%掩码×鲁棒组
     ▼                                │ 写入 adversary_push 事件参数
动作管理器 process_actions             │
  q* = clamp(a·m·0.25(髋0.125) + q_default + b)
     │
     ▼  （以下在一个策略步内重复 4 次，200 Hz）
执行器 ScaledDCMotor
  τ = clip_DC( k · [25(q* − q) − 0.5·q̇] )
     │
     ▼
PhysX 物理仿真一步（dt = 0.005 s，脚的摩擦按 64 档之一）
     │
     ▼  （4 次之后）
事件管理器：interval 事件 adversary_push
  若被选中：v_xy += 推力向量（直接改速度）
     │
     ▼
观测管理器：45 维观测（加噪声）
奖励管理器：跟踪 + 惩罚
终止管理器：超时 / 机身触地 → 重置（reset 事件：姿态、关节）
     │
     ▼
[训练代码] 拿到 obs、reward、done；上下文 get_context() 返回固定的 26 维
```

> 事件和物理步的先后顺序（interval 事件在物理步之前还是之后执行）属于 Isaac Lab 的内部实现，【推断】是在物理步之后、计算观测之前，需核对。

---

## 7. 迁移到 Go2-W 要改哪里

Go2-W：12 个腿关节（位置控制）+ 4 个轮子（速度控制），共 16 个执行器。

### 7.1 改动清单

| # | 位置 | 现在 | 要改成 | 原因 |
|---|---|---|---|---|
| 1 | 继承的父类 `UnitreeGo2RoughEnvCfg` | Go2 | Go2-W 的环境配置（或以 Go2 为模板自己写） | 机器人模型、默认姿态、关节名都不同 |
| 2 | 机器人资产 | Go2 USD | Go2-W 的 USD/URDF 及 `ArticulationCfg` | 多了 4 个轮子关节和轮子刚体 |
| 3 | 动作项 `custom_env.py:176-189` | 一个动作项，`joint_names=[".*"]`，全是位置 | **拆成两个动作项**：腿用 `ShiftScaleClampJointPositionAction`（`joint_names` 只匹配 hip/thigh/calf）；轮子用**关节速度动作**（如 Isaac Lab 的 `JointVelocityAction`），给一个速度缩放 | 轮子是连续旋转，没有"目标角"；位置控制会让轮子转到某个角度就停 |
| 4 | 髋关节缩放 `envs_utils.py:43` | `scale_vec[:, :4] *= ...` | 按关节名查出髋关节的索引再缩放 | 硬编码依赖"前 4 个是髋"；Go2-W 关节顺序可能不同 |
| 5 | 关节零偏、限幅 | 对所有关节 | **只对腿**；轮子不加零偏（零位对轮子无意义）、不按位置限幅 | 轮子是连续关节 |
| 6 | 执行器 `custom_env.py:192-203` | 只有 `"base_legs"` | 保留腿的执行器；**新增轮子执行器**（速度控制：stiffness = 0，damping 作为速度增益；力矩和转速上限按 Go2-W 轮毂电机参数） | 轮子要速度伺服 |
| 7 | 电机强度与故障 | 12 维 | 腿 12 维 + 轮 4 维 = **16 维**；轮子执行器也用 `ScaledDCMotor` 式的倍数 | 我们要研究轮子失效 |
| 8 | 上下文 `context_env_wrapper.py:186-197` | 只读 `"base_legs"` | 再读轮子执行器的倍数并拼接；上下文从 26 维变成 30 维（或按分组重排） | 同上；分组方案还需要把顺序按"环境组 / 执行器组"整理 |
| 9 | 摩擦 `custom_env.py:216-227` | `body_names=".*foot"` | 改成轮子刚体名（如 `".*wheel"`，按 Go2-W 模型确认） | 轮足着地的是轮子 |
| 10 | 摩擦上下文 `context_env_wrapper.py:141` | `materials[:, -1, :]`（假设最后一个形状是脚） | 明确按轮子刚体的形状索引读取 | 不能依赖排列顺序 |
| 11 | 重置姿态 `envs_utils.py:322-325` | 12 维趴下姿态 | 按 Go2-W 关节数和顺序重写（轮子关节可设 0） | 维度和角度都不同 |
| 12 | 观测 | 关节角/速度各 12 维 | 腿关节角 12 + 轮子**不给绝对角**（连续旋转，角度无意义）+ 关节速度 16 + 上一步动作 16 | 轮子角度没有意义，轮速有意义 |
| 13 | 奖励 `feet_air_time` | +1.0 | 去掉或大幅降低，或改成只在"步行模式"下生效 | 鼓励抬脚，与轮式滚动矛盾 |
| 14 | 奖励 `base_height_l2` | 目标 0.34 m | 按 Go2-W 的站立高度重设 | 轮子使站姿高度不同 |
| 15 | 奖励 `undesired_contacts` | thigh / calf / hip | 按 Go2-W 的刚体名改；允许轮子接触 | 身体名不同 |
| 16 | 奖励（新增） | — | 轮速平滑、轮子打滑惩罚等（视任务） | 轮足特有 |
| 17 | 终止条件（评估） | `Head_upper` 等名字 | 按 Go2-W 的刚体名改 | 名字不同 |

### 7.2 工作量提示

- 第 3、6、7、8 项是**结构性改动**，影响网络输入/输出维度，必须一起改；
- 第 13–16 项是**调参性改动**，需要训练几轮看效果；
- 已有 Go2-W 的开源强化学习实现（如 DreamWaQ_Go2W、HIMLoco-for-Go2W）可以参考资产和奖励设置。

---

## 8. 怎么加"运行中故障 / 中途加载荷"

### 8.1 思路

现在所有参数都在创建时定死。要让它们"在第 t 秒突然变化"，需要：

1. 加一个 `interval` 事件（或在 runner 中按时间触发）；
2. 在事件里修改物理参数：电机倍数、机身质量；
3. **同步更新上下文**：包装器的 `self.context` 对应位置也要改，否则训练时教师网络看到的"真相"是错的；
4. 评估时记录"变化时刻"，用于计算恢复时间等指标。

### 8.2 运行中电机故障（伪代码）

```python
# envs_utils.py 中新增
def midrun_motor_fault(env, env_ids, fault_prob, fault_joint_ids, fault_value,
                       actuator_name="base_legs"):
    """运行中随机让某些电机失效。"""
    actuator = env.scene["robot"].actuators[actuator_name]
    scale = actuator._effort_scale                # (num_envs, num_joints)

    # 1. 选出这一次要发生故障的环境
    hit = torch.rand(len(env_ids), device=scale.device) < fault_prob
    ids = env_ids[hit]
    if len(ids) == 0:
        return

    # 2. 每个被选中的环境随机挑一个关节
    j = torch.tensor(fault_joint_ids, device=scale.device)[
        torch.randint(len(fault_joint_ids), (len(ids),), device=scale.device)]

    # 3. 改物理参数：0 = 完全无力；0.3 = 只剩 30%
    scale[ids, j] = fault_value

    # 4. 记录，供上下文包装器和评估统计使用
    env.extras.setdefault("fault_events", []).append((env.common_step_counter, ids, j))


# unitree_go2_custom_env.py 的 __post_init__ 中新增
self.events.midrun_fault = EventTerm(
    func=midrun_motor_fault,
    mode="interval",
    interval_range_s=(8.0, 12.0),          # 每 8~12 秒检查一次
    params={"fault_prob": 0.2, "fault_joint_ids": [0, 1, 2, 3],
            "fault_value": 0.0},
)
```

**回合重置时要恢复**：故障不应该延续到下一个回合（除非就是想研究"永久故障"）。需要再加一个 `reset` 事件，把 `_effort_scale` 恢复成该环境原来的随机值（构造时先备份一份 `_effort_scale_nominal`）。

### 8.3 中途加载荷（伪代码）

```python
def midrun_add_mass(env, env_ids, add_kg_range, asset_cfg):
    asset = env.scene[asset_cfg.name]
    masses = asset.root_physx_view.get_masses()               # CPU 张量
    ids_cpu = env_ids.cpu()
    add = torch.empty(len(ids_cpu)).uniform_(*add_kg_range)
    masses[ids_cpu, asset_cfg.body_ids] += add.unsqueeze(-1)
    asset.root_physx_view.set_masses(masses, ids_cpu)
    # 注意：改质量后，惯量是否需要同步更新，要查 Isaac Lab 对应版本的做法
```

用于复现论文 Fig. 4 右（10 s 时加 9 kg）：评估时设 `interval_range_s=(10.0, 10.0)`，并保证只触发一次（例如在函数里用一个标志位记录"已加过"）。

### 8.4 同步更新上下文（伪代码）

```python
# context_env_wrapper.py 中新增
def refresh_context(self):
    """重新读取物理参数，更新上下文。在 step 之后调用。"""
    self._set_context()

# 在 step() 中调用，或只在事件发生后调用以节省开销
def step(self, actions):
    out = super().step(actions)
    if self.dynamic_context:
        self.refresh_context()
    return out
```

> 注意：`_set_context` 读质量时用的是 `get_masses()`，会反映运行中加的质量；读电机时用的是 `get_effort_scale()`，也会反映故障。所以**直接重新调用 `_set_context` 就能拿到新值**，不用重写读取逻辑。

### 8.5 和选择性鲁棒适应的关系

- 训练时：这些事件让一部分环境**在回合中途**进入"某组参数超出范围"的状态，这正是"部分可信"训练要的数据；
- 评估时：可以测"故障发生后 α 多久下降、速度掉多少、多久恢复"，这些指标论文都没有。

---

## 9. 自测题

**1.** GRAM 的观测里为什么没有机身线速度？观测向量一共多少维，怎么算出来的？

**2.** 写出一个关节从"网络输出"到"施加的力矩"的完整计算链。

**3.** "冻结关节"（`action_mult=0`）和"电机故障"（`motor_fault_indices`）有什么区别？

**4.** 摩擦倍数为什么要分成 64 档，而不是连续随机？

**5.** 对抗推力为什么说"不是力"？这和机器人质量有什么关系？

**6.** 加 9 kg 时，default 训练和 wide 训练下的质量上下文值分别是多少？这说明了什么？

**7.** 26 维上下文的拼接顺序是什么？哪一类参数默认不进上下文？

**8.** 训练过程中，一个环境的上下文会变化吗？为什么？这对"运行中故障"实验意味着什么？

**9.** 电机强度倍数 k = 1.2 时，电机能输出比 23.5 N·m 更大的力矩吗？为什么？

**10.** 迁移到 Go2-W，动作项为什么必须拆成两个？

<details>
<summary>参考答案</summary>

**1.** 实机上 Go2 没有直接测量机身线速度的传感器，只能估计，给了会造成仿真到实机的差距，所以删掉。观测约 45 维【推断】：角速度 3 + 投影重力 3 + 指令 3 + 关节角 12 + 关节速度 12 + 上一步动作 12。

**2.** 网络输出 a → 乘关节倍数 m（冻结时为 0）→ 乘缩放 0.25（髋 0.125）→ 加默认站姿角 → 加关节零偏 b → 限幅到关节范围，得到目标角 q\* → PD：Kp(q\* − q) − Kd·q̇ → 乘电机强度 k → 按 DC 电机力矩—转速曲线限幅 → 施加到关节。

**3.** 冻结关节改的是**动作**：关节不再听网络的，PD 仍然把它拉回（带零偏的）站姿角，关节**有力**。电机故障改的是**力矩**：力矩乘 0，关节**完全无力**，随外力摆动。另外，冻结默认不进上下文；电机故障通过电机强度（变成 0，归一化后为 −5）间接进了上下文。

**4.** PhysX 中每种摩擦组合要单独建一种物理材质，材质数量有上限，分档能把数量控制在 64 种以内。

**5.** 代码是直接给机身水平速度加一个增量（瞬时冲击），而不是施加一段时间的力。速度增量与质量无关，所以重的机器人和轻的机器人被"推"出同样的速度变化，但实际承受的冲量（m·Δv）不同。

**6.** default：(9 + 1)/4 = 2.5 → **4.0**；wide：(9 + 1)/10 = 1 → **1.0**。说明同样的物理情况，相对于不同的训练范围，可能是"见过"也可能是"远远没见过"。这正是 Fig. 5 的实验设计。

**7.** 质量 1 → 摩擦 1 → 关节零偏 12 → 电机强度 12。动作倍数（冻结关节）默认不进上下文。

**8.** 不会。四类参数都在环境创建时随机一次，上下文也只在包装器创建时读一次。要做运行中故障，必须自己加事件修改物理参数，并同步刷新上下文。

**9.** 低速、力矩不饱和时，输出确实是 1.2 倍；但饱和时，倍数乘在限幅之前，上限仍是 DC 电机曲线（静止时 23.5 N·m），所以不能超过。电机强度更像"等效 PD 增益"的不确定性，而不是"最大力气"的不确定性。

**10.** 腿关节是位置控制（给目标角），轮子是连续旋转，需要速度控制（给目标转速）。位置动作的缩放、零偏、按角度限幅对轮子都没有意义。拆成两个动作项后，还可以分别设置缩放和执行器。
</details>

---

## 附：本篇中"需在服务器核对"的事项汇总

| # | 事项 | 怎么核对 |
|---|---|---|
| 1 | 观测总维度 45 | 打印 `obs.shape`，或看模型中 `history_encoder.1.weight` 的输入维度是否为 720 |
| 2 | 观测噪声大小 | 查 `work/IsaacLab` 中 velocity 任务的 `ObservationsCfg` |
| 3 | `add_base_mass` 的模式（startup）和作用刚体（base） | 查 Go2 rough 配置及其父类的 `EventCfg` |
| 4 | 跟踪奖励的 σ²（0.25） | 查 `RewardsCfg` 中 `track_lin_vel_xy_exp` 的 `std` |
| 5 | `num_steps_per_env = 24` | 查 Go2 的 `rsl_rl_ppo_cfg` |
| 6 | DC 电机限幅公式 | 查 `isaaclab/actuators/actuator_pd.py` 的 `DCMotor._clip_effort` |
| 7 | Go2 关节顺序（前 4 个为髋） | 打印 `robot.data.joint_names` |
| 8 | 摩擦材质的组合方式 | 查 PhysX 材质的 `friction_combine_mode` |
| 9 | 新版 Isaac Lab（0.54.2）上述默认值是否与 v1.0 一致 | 逐项对比 upstream v1.0 与当前版本，这也是复现计划的第一步 |
