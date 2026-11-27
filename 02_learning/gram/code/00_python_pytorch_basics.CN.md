# 代码 00：读懂 GRAM 代码需要的 Python 与 PyTorch 基础

> 这篇写给"会一点 Python、没正经写过 PyTorch"的读者。每个知识点都按同一个顺序讲：
> **要干什么 → GRAM 里的真实代码 → 逐行解释 → 小数字手算 → 小结 → GRAM 里在哪用到**。
>
> 代码路径都相对于官方仓库根目录 `gram/`。行号以官方原版为准（服务器上的兼容版本只改了 import 名称，行号基本一致）。
>
> 标注约定：**【代码事实】** 直接读代码得到；**【推断】** 根据代码和库的默认行为推出来，没有实际运行验证；**【已验证】** 在本地用 PyTorch 跑过小例子。

---

## 目录

- 第一部分 Python 基础
  - 1.1 类、`__init__` 与 `self`
  - 1.2 继承与 `super()`
  - 1.3 `@property`：把方法当属性用
  - 1.4 `*args` 与 `**kwargs`
  - 1.5 `@configclass` / `dataclass`：配置类
  - 1.6 函数里定义类（闭包）
  - 1.7 `import`、包、模块路径与 `python -m`
  - 1.8 `argparse`：命令行参数
  - 1.9 `eval("字符串")`、`getattr` 这类"按名字取东西"
- 第二部分 PyTorch 张量
  - 2.1 张量、`shape`、`dtype`、`device`
  - 2.2 `dim` 是什么：按哪一维操作
  - 2.3 `unsqueeze`
  - 2.4 `repeat`
  - 2.5 `reshape` 与 `Flatten`
  - 2.6 `cat`
  - 2.7 `sum(dim)`、`mean(dim)`、`var(dim)`
  - 2.8 `clamp`
  - 2.9 `exp` 与 GRAM 的 α
  - 2.10 `quantile`：分位数
  - 2.11 广播（broadcasting）
  - 2.12 布尔索引与掩码
  - 2.13 随机数：`torch.randn`、`torch.rand`、`torch.bernoulli`
- 第三部分 神经网络
  - 3.1 `nn.Module`
  - 3.2 `nn.Linear` 与 `nn.Sequential`、ELU 激活
  - 3.3 参数、`requires_grad`、`nn.Parameter`
  - 3.4 `itertools.chain` 拼接参数（以及 GRAM 里的一个坑）
  - 3.5 初始化：Xavier 与 gain
- 第四部分 训练的机械过程
  - 4.1 前向、损失、反向、更新
  - 4.2 优化器 Adam
  - 4.3 梯度裁剪 `clip_grad_norm_`
  - 4.4 `detach` 与 `torch.no_grad` / `torch.inference_mode`
  - 4.5 `train()` 与 `eval()` 模式
- 第五部分 概率分布
  - 5.1 `Normal`：高斯分布
  - 5.2 `sample`、`log_prob`、`entropy`
- 第六部分 保存与加载：`state_dict`、`torch.save`、`torch.load`
- 自测题

---

# 第一部分 Python 基础

## 1.1 类、`__init__` 与 `self`

**要干什么**：把"数据"和"操作这些数据的函数"打包在一起。GRAM 里的每个网络、每个算法、每个环境包装器都是一个类。

**GRAM 里的真实代码**（`source/algs/gram/gram_actor_critic.py:22-28`，节选）：

```python
class GRAMActorCritic(nn.Module):

    def __init__(
        self,
        num_actor_obs,
        num_critic_obs,
        num_actions,
        ...
```

**逐行解释**：
- `class GRAMActorCritic(...)`：定义一个类，名字叫 `GRAMActorCritic`。类就像"图纸"。
- `def __init__(self, ...)`：**构造函数**。用图纸造一个具体对象（叫"实例"）时，Python 会自动调用它，用来做初始化：建网络层、存参数。
- `self`：指"正在被造的这个对象本身"。在类的方法里，`self.actor = ...` 的意思是"把 actor 存到这个对象身上"，之后其他方法可以用 `self.actor` 取出来。

**例子**：

```python
actor_critic = GRAMActorCritic(45, 45, 12, 26, num_latent=8, obs_history_length=16)
```

这一行做了两件事：造一个对象，并自动执行 `__init__`。执行完后，`actor_critic.actor` 就是策略网络，`actor_critic.critic` 就是价值网络。

> 这里的 45、26 等数字是示例：26 是上下文维度（论文 Table II）；45 是观测维度的【推断】值，见 2.6 节。

**小结**：类 = 图纸；`__init__` = 造对象时自动执行的初始化；`self` = 这个对象自己。

**GRAM 里在哪用到**：所有 `.py` 文件。最重要的类：`GRAMActorCritic`（`gram_actor_critic.py:22`）、`GRAMPPO`（`gram_ppo.py`）、`GRAMOnPolicyRunner`（`gram_on_policy_runner.py:29` 附近）、`GRAMAdversary`（`gram_adversary.py`）、`ContextRslRlVecEnvWrapper`（`envs/context_env_wrapper.py`）。

---

## 1.2 继承与 `super()`

**要干什么**：在已有的类上"加东西、改东西"，不用从头写。

**GRAM 里的真实代码**：

```python
class GRAMActorCritic(nn.Module):          # gram_actor_critic.py:22
    def __init__(self, ...):
        super().__init__()                  # gram_actor_critic.py:75
```

```python
class ScaledDCMotor(DCMotor):              # envs/envs_utils.py:345
    def __init__(self, cfg: ScaledDCMotorCfg, *args, **kwargs):
        super().__init__(cfg, *args, **kwargs)
        self._set_effort_scale()
```

**逐行解释**：
- `class GRAMActorCritic(nn.Module)`：括号里是**父类**。`GRAMActorCritic` 继承了 PyTorch 的 `nn.Module`，自动获得"管理参数、搬到 GPU、保存加载"等能力。
- `super().__init__()`：先执行父类的初始化。**必须写**，否则 `nn.Module` 内部用来登记子网络和参数的字典还没建好，后面 `self.actor = nn.Sequential(...)` 会报错。
- `ScaledDCMotor(DCMotor)`：Isaac Lab 自带一个直流电机模型 `DCMotor`，GRAM 继承它，只**额外**加了"电机强度倍数"。先 `super().__init__(...)` 让父类把电机建好，再调用自己的 `_set_effort_scale()` 加上新功能。

**重写（override）**：子类可以定义和父类同名的方法，覆盖父类的行为。例如 `ScaledDCMotor._clip_effort`（`envs_utils.py:376`）覆盖了父类的力矩限幅：先乘以强度倍数，再调用父类的限幅：

```python
    def _clip_effort(self, effort: torch.Tensor) -> torch.Tensor:
        scaled_effort = self._effort_scale * effort
        return super()._clip_effort(scaled_effort)
```

**数值例子**：PD 算出某关节需要 10 N·m，这个电机的强度倍数是 0.8，则先变成 8 N·m，再交给父类按上限 23.5 N·m 限幅，结果仍是 8 N·m。若需要 30 N·m、倍数 1.2，先变成 36，再被限到 23.5。

**小结**：继承 = 在别人的类上改；`super()` = 调用父类的同名方法。

**GRAM 里在哪用到**：`gram_actor_critic.py:22,75`；`envs_utils.py:29`（`ScaledJointPositionAction` 继承 Isaac Lab 的 `JointPositionAction`）、`:125`（`ShiftScaleClampJointPositionAction` 又继承 `ScaledJointPositionAction`，两层继承）、`:345,376`；`unitree_go2_custom_env.py:82,93`（配置类继承 Isaac Lab 的 Go2 配置）。

---

## 1.3 `@property`：把方法当属性用

**要干什么**：有些值需要"算一下"才能得到，但用起来想像普通变量一样，不想写括号。

**GRAM 里的真实代码**（`gram_actor_critic.py:422-432`）：

```python
    @property
    def action_mean(self):
        return self.distribution.mean

    @property
    def action_std(self):
        return self.distribution.stddev

    @property
    def entropy(self):
        return self.distribution.entropy().sum(dim=-1)
```

**逐行解释**：
- `@property` 是一个"装饰器"（写在函数上面、以 `@` 开头的东西），它把下面的方法变成"属性"。
- 用的时候写 `actor_critic.action_mean`，**不加括号**，Python 会自动调用这个方法并返回结果。

**例子**：`gram_actor_critic.py:497` 里写的是 `actions = self.action_mean`，没有括号，得到的是当前高斯分布的均值，也就是"确定性动作"。

**小结**：`@property` 让方法用起来像变量。看到一个没有括号、却需要计算的"变量"，就去找带 `@property` 的同名方法。

**GRAM 里在哪用到**：`gram_actor_critic.py:422-432`；`gram_adversary.py:94,98`；`envs_utils.py:93`（`action_scale`）、`:157`（`action_shift`）。

---

## 1.4 `*args` 与 `**kwargs`

**要干什么**：让函数能接收"不确定数量"的参数，或者把一大包参数原样转交给别的函数。

- `*args`：把多余的**位置参数**收成一个元组；
- `**kwargs`：把多余的**关键字参数**（`名字=值`）收成一个字典。

**GRAM 里的真实代码 1**（`gram_actor_critic.py:73`）：`GRAMActorCritic.__init__` 参数列表最后是 `**kwargs`。

为什么要它？因为 runner 创建网络时是这样调用的（`gram_on_policy_runner.py:52-54`）：

```python
        actor_critic: GRAMActorCritic = actor_critic_class(
            num_obs, num_critic_obs, self.env.num_actions, num_context, **self.policy_cfg
        ).to(self.device)
```

`**self.policy_cfg` 把配置字典"拆开"成一堆 `名字=值`。这个字典里有很多 `GRAMActorCritic` 用不到的键（比如对抗者的 `adversary_hidden_dims`），这些用不到的就被 `**kwargs` 收走、忽略，不会报错。

**GRAM 里的真实代码 2**（`source/train.py:47`）：

```python
        create_custom_env(args_cli.task, **train_inputs_cfg.to_dict())
```

`train_inputs_cfg.to_dict()` 返回一个字典，比如 `{"base_mass_min": -1.0, "base_mass_max": 3.0, ...}`；`**` 把它拆成 `base_mass_min=-1.0, base_mass_max=3.0, ...` 传给函数。

**数值例子**：

```python
def f(a, b, **kwargs):
    print(a, b, kwargs)

d = {"a": 1, "b": 2, "c": 3}
f(**d)        # 输出：1 2 {'c': 3}
```

`a`、`b` 被认领，`c` 进了 `kwargs`。

**小结**：`**字典` 在调用处是"拆包"，在定义处是"收包"。GRAM 用它把一大份配置一路传下去。

**GRAM 里在哪用到**：`gram_actor_critic.py:73`；`gram_on_policy_runner.py:53,56,99`；`train.py:47`；`eval.py:48`；`envs/__init__.py:26-28`；`unitree_go2_custom_env.py:78`。

---

## 1.5 `@configclass` / `dataclass`：配置类

**要干什么**：用一个类专门存一组"配置项"，每项有名字、类型和默认值。比字典更清楚，也方便继承和修改。

**GRAM 里的真实代码**（`source/envs/unitree_go2_cfg.py:29-47`，节选）：

```python
@configclass
class UnitreeGo2CustomDefaultIDCfg:
    """Config for Unitree Go2 custom task w/ default ID context set."""

    """Terrain."""
    terrain_roughness_cm: float = 0.0
    terrain_slope_degrees: float = 0.0
    height_scan: bool = False
    ...
    """Additive base mass."""
    base_mass_min: float = -1.00
    base_mass_max: float = 3.00
```

**逐行解释**：
- `@configclass`：Isaac Lab 提供的装饰器，基于 Python 标准库的 `dataclass`。它会根据下面写的"字段"自动生成 `__init__` 等方法。
- `terrain_roughness_cm: float = 0.0`：一个字段，名字叫 `terrain_roughness_cm`，类型是浮点数，默认值 0.0。
- 中间那些 `"""Terrain."""` 只是给人看的分组说明，不起作用。
- `configclass` 比普通 `dataclass` 多了一些功能，比如 `.to_dict()`（转成字典，`train.py:47` 用到）、允许字段默认值是可变对象（列表等）。

**继承与 `__post_init__`**（`unitree_go2_cfg.py:125-133`）：

```python
@configclass
class UnitreeGo2CustomWideIDCfg(UnitreeGo2CustomDefaultIDCfg):
    """Config for Unitree Go2 custom task w/ wide ID context set."""

    def __post_init__(self):
        super().__post_init__()

        self.base_mass_max = 9.00
        self.base_mass_context_scale_max = 9.00
```

- `UnitreeGo2CustomWideIDCfg` 继承默认配置，所有字段一样，**只把附加质量上限从 3 kg 改成 9 kg**。这就是论文 Fig. 5 的"宽训练"。
- `__post_init__`：`dataclass` 的规矩，自动生成的 `__init__` 执行完后，会再调用 `__post_init__`，可以在这里改字段。

**数值例子**：

```python
cfg = UnitreeGo2CustomWideIDCfg()
cfg.base_mass_min   # -1.0（继承来的）
cfg.base_mass_max   # 9.0（被 __post_init__ 改掉）
cfg.to_dict()["friction_mult_max"]  # 4.5
```

**小结**：配置类 = 带默认值的"参数表"。改实验设置，通常就是改它的字段，或者从命令行覆盖它的字段。

**GRAM 里在哪用到**：`unitree_go2_cfg.py`（全文件）；`unitree_go2_custom_env.py:81-93`（环境和 PPO 配置类）；`envs_utils.py:107,174,382`（动作项和电机的配置类）。

> 新版 Isaac Lab：`from omni.isaac.lab.utils import configclass` 改为 `from isaaclab.utils import configclass`。

---

## 1.6 函数里定义类（闭包）

**要干什么**：根据运行时的参数"现场生成"一个配置类。GRAM 的环境配置就是这样造出来的，第一次看会很困惑。

**GRAM 里的真实代码**（`unitree_go2_custom_env.py:37-104`，节选）：

```python
def create_unitree_go2_custom_env(
    task,
    terrain_roughness_cm,
    ...
    **kwargs
):

    @configclass
    class UnitreeGo2CustomEnvCfg(UnitreeGo2RoughEnvCfg):
        def __post_init__(self):
            super().__post_init__()
            if activate_self_collisions:
                self.scene.robot.spawn.articulation_props.enabled_self_collisions = True
            ...
```

**逐行解释**：
- 外层是一个**函数** `create_unitree_go2_custom_env`，参数是一大堆实验设置。
- 函数**内部**定义了一个类 `UnitreeGo2CustomEnvCfg`。
- 类的 `__post_init__` 里直接用了外层函数的参数 `activate_self_collisions`。这在 Python 里是允许的，叫**闭包**：内部定义的东西能"记住"外层函数的变量。
- 函数最后用 `gym.register(...)` 把这个类登记到一个全局表里（`:296-301`），之后别的地方按任务名就能找到它。

**为什么这么写**：Isaac Lab 是"按任务名从注册表里取配置类、再实例化"的。GRAM 想让配置随命令行变化，就在注册之前、在函数里现场生成一个"已经把命令行参数写进去"的类。

**小结**：看到函数里面定义类，就理解成"按参数现场生成图纸，然后登记"。

**GRAM 里在哪用到**：`unitree_go2_custom_env.py:37-301`。

---

## 1.7 `import`、包、模块路径与 `python -m`

**要干什么**：把别的文件里的代码拿来用。

**几个概念**：
- **模块**：一个 `.py` 文件。
- **包**：一个文件夹，里面有 `__init__.py`。`gram/source/` 就是一个包，`source/algs/`、`source/envs/`、`source/utils/` 都是子包。
- **模块路径**：用点号表示文件夹层级。`source.algs.gram.gram_actor_critic` 指 `source/algs/gram/gram_actor_critic.py`。

**GRAM 里的真实代码**（`source/train.py:34-37`）：

```python
    from source.algs import GRAMOnPolicyRunner
    from source.envs import CUSTOM_ENVS, create_custom_env
    from source.envs.context_env_wrapper import ContextRslRlVecEnvWrapper
    from source.utils.cli_utils import parse_agent_cfg, parse_custom_inputs_cfg
```

- 第一行能直接从 `source.algs` 拿到 `GRAMOnPolicyRunner`，是因为 `source/algs/__init__.py` 里写了 `from source.algs.gram import GRAMOnPolicyRunner`，而 `source/algs/gram/__init__.py` 又写了 `from source.algs.gram.gram_on_policy_runner import GRAMOnPolicyRunner`。`__init__.py` 起到"转发"的作用。

**`python -u -m source.train` 是什么意思**：
- `-m source.train`：把 `source.train` 当作**模块**运行，Python 会从**当前目录**开始找 `source/train.py`。所以必须在仓库根目录 `gram/` 下执行。好处是 `from source.xxx import ...` 这类绝对导入都能找到。
- 如果写 `python source/train.py`，Python 会把 `source/` 当成起点，`import source...` 就找不到，会报 `ModuleNotFoundError`。
- `-u`：不缓冲输出（unbuffered），打印内容立刻出现在终端或日志里。训练很长，用它方便实时看进度。
- `if __name__ == "__main__":`（`train.py:119`）：只有"直接运行这个文件"时才执行下面的代码；被别的文件 `import` 时不执行。

**特殊的写法：在函数里面 import**（`train.py:11-37`）：`train()` 函数的第一件事是 `from source.launcher import args_cli, simulation_app`，然后才 import Isaac Lab 的模块。原因是：**Isaac Lab 的大部分模块必须在 Isaac Sim 启动之后才能 import**，而 `source/launcher.py` 被 import 时就会启动 Isaac Sim。详见 [01 项目结构与运行流程](01_project_structure_and_run_flow.CN.md)。

**"只为副作用而 import"**（`train.py:26`）：`import omni.isaac.lab_tasks` 之后再没直接用它。它的作用是：这个包被导入时，会把 Isaac Lab 自带的所有任务登记到 gym 的注册表里，包括 GRAM 要继承的 Go2 配置。

**小结**：在仓库根目录用 `python -m source.train` 运行；`__init__.py` 负责转发；GRAM 里很多 import 写在函数内部，是为了等仿真器先启动。

**GRAM 里在哪用到**：`train.py:16-37`；`eval.py:16-37`；`launcher.py:9-11`；各 `__init__.py`。

> 新版 Isaac Lab：`omni.isaac.lab` → `isaaclab`，`omni.isaac.lab_tasks` → `isaaclab_tasks`，rsl_rl 包装器 `omni.isaac.lab_tasks.utils.wrappers.rsl_rl` → `isaaclab_rl.rsl_rl`。

---

## 1.8 `argparse`：命令行参数

**要干什么**：让用户在命令行里写 `--num_envs 16` 这样的参数，程序读进来使用。

**GRAM 里的真实代码**（`source/utils/cli_utils.py:14-29`，节选）：

```python
def create_parser():
    """Create parser for training / evaluation."""
    # create parser
    parser = argparse.ArgumentParser(description="Command line parser.")
    parser.add_argument("--video", action="store_true", default=False, help="Record videos during training.")
    ...
    parser.add_argument("--num_envs", type=int, default=4096, help="Number of environments to simulate.")
    parser.add_argument("--seed", type=int, default=1, help="Seed used for the environment")
    parser.add_argument("--max_iterations", type=int, default=10000, help="RL training iterations.")
```

**逐行解释**：
- `argparse.ArgumentParser(...)`：建一个"参数解析器"。
- `add_argument("--num_envs", type=int, default=4096, ...)`：登记一个参数。命令行写了 `--num_envs 16`，就得到整数 16；没写就用默认 4096。
- `action="store_true"`：**开关型**参数。命令行里出现 `--video` 就是 `True`，不出现就是 `False`，后面不跟值。
- `choices=[...]`：只允许这几个取值，例如 `--alg_name` 只能是六种算法之一（`cli_utils.py:109-122`）。
- `nargs="+"`：后面可以跟一个或多个值，收成列表。例如 `--actor_hidden_dims 512 256 128` 得到 `[512, 256, 128]`。
- `nargs="+", action="append"`（`cli_utils.py:282`、`:302`）：可以**多次**出现，每次得到一个列表，最后是"列表的列表"。例如 `--motor_fault_indices 0 --motor_fault_indices 3 4` 得到 `[[0], [3, 4]]`。
- `parser.parse_args()`（`launcher.py:17`）：真正去读命令行，返回一个对象 `args_cli`，用 `args_cli.num_envs` 取值。参数名里的 `-` 会自动变成 `_`，但 GRAM 的参数本来就用下划线。

**数值例子**：

```
python -m source.train --alg_name robust_rl --num_envs 16 --max_iterations 2 --video
```

得到：`args_cli.alg_name == "robust_rl"`，`args_cli.num_envs == 16`，`args_cli.max_iterations == 2`，`args_cli.video == True`，`args_cli.seed == 1`（默认）。

**一个容易混淆的点**：很多参数默认值是 `None`（例如 `--base_mass_min`，`cli_utils.py:262`）。`None` 表示"命令行没指定，用配置类里的默认值"。`parse_custom_inputs_cfg` 里大量出现 `if args_cli.xxx is not None: inputs_cfg.xxx = args_cli.xxx` 就是这个意思。

**小结**：`argparse` 把命令行变成 `args_cli` 对象；默认值为 `None` 的参数表示"不覆盖配置文件"。

**GRAM 里在哪用到**：`cli_utils.py:14-352`；`launcher.py:14-17`。

---

## 1.9 `eval("字符串")`：按名字取类

**要干什么**：配置里只存了类名字符串，比如 `"GRAMActorCritic"`，运行时要把它变成真正的类。

**GRAM 里的真实代码**（`gram_on_policy_runner.py:51-56`）：

```python
        actor_critic_class = eval(self.policy_cfg.pop("class_name"))  # GRAMActorCritic
        ...
        alg_class = eval(self.alg_cfg.pop("class_name"))  # GRAMPPO
```

**逐行解释**：
- `self.policy_cfg.pop("class_name")`：从配置字典里取出键 `"class_name"` 的值，同时把这个键删掉。值是 `"GRAMActorCritic"`，来自 `cli_utils.py:760`。
- `eval("GRAMActorCritic")`：把字符串当 Python 代码执行，得到当前文件里已经 import 的类 `GRAMActorCritic`。
- 为什么要 `pop` 而不是只取：之后会用 `**self.policy_cfg` 把剩下的配置传给类，不能再带着 `class_name` 这个键。

> 这里的 `eval` 是 Python 内置函数，和"评估模型"无关，也和 `model.eval()` 无关。

**小结**：配置里存类名，运行时用 `eval` 变回类。

**GRAM 里在哪用到**：`gram_on_policy_runner.py:51,55`；类名在 `cli_utils.py:760-761` 设定。

---

# 第二部分 PyTorch 张量

## 2.1 张量、`shape`、`dtype`、`device`

**要干什么**：神经网络里所有数据都是**张量**（tensor），可以理解为"多维数组"，能在 GPU 上快速计算，并能自动求导。

| 概念 | 含义 | 例子 |
|---|---|---|
| 张量 | 多维数组 | `torch.tensor([[1., 2.], [3., 4.]])` |
| `shape` | 每一维有多长 | 上例 `shape = (2, 2)` |
| `dtype` | 数据类型 | `torch.float32`（GRAM 绝大部分）、`torch.int64`（下标）、`torch.bool`（真假） |
| `device` | 放在哪里算 | `"cpu"` 或 `"cuda:0"`（第 0 块 GPU） |

**GRAM 里最常见的几种形状**（以 4096 个并行环境为例）：

| 变量 | 形状 | 含义 |
|---|---|---|
| `obs` | (4096, 45) | 每个环境一行观测【45 为推断值，见 2.6】 |
| `context` | (4096, 26) | 每个环境的 26 维真实上下文 |
| `latent` | (4096, 8) | 每个环境的 8 维隐变量 z |
| `obs_history` | (4096, 16, 45) | 每个环境最近 16 步观测 |
| `actions` | (4096, 12) | 每个环境 12 个关节目标 |
| `robust_masks` | (4096, 1) | 每个环境一个 0/1，1 表示"本轮做鲁棒训练" |
| `latent_all` | (8, 4096, 8) | epinet 8 个随机样本 × 4096 环境 × 8 维隐变量 |

**规律**：第 0 维几乎总是"第几个环境"，这一维也叫 **batch 维**。

**GRAM 里的真实代码**（`gram_on_policy_runner.py:255-264`）：

```python
        obs_history = torch.zeros(
            (self.env.num_envs, self.obs_history_length, obs.shape[1]), dtype=torch.float32, device=self.device
        )
        ...
        robust_masks = torch.zeros((self.env.num_envs, 1), dtype=torch.float32, device=self.device)
        robust_masks[int(self.env.num_envs / 2) :] = 1
```

- `torch.zeros(形状, dtype=..., device=...)`：造一个全 0 张量，直接放在 GPU 上。
- `obs.shape[1]`：观测的第 1 维长度，即观测维度。
- `robust_masks[2048:] = 1`：后一半环境（第 2048 到 4095 个）设为 1，其余为 0。这就是"一半环境做适应训练，一半做鲁棒训练"的初始分配。

**`.to(device)`**：把张量或网络搬到指定设备。例如 `gram_on_policy_runner.py:54` 的 `.to(self.device)` 把整个网络搬到 GPU。**参与同一次计算的张量必须在同一设备上**，否则报错。

**小结**：张量 = 多维数组；先看 `shape`，第 0 维通常是环境编号。

---

## 2.2 `dim` 是什么：按哪一维操作

很多操作有 `dim` 参数，意思是"**沿着这一维做，做完这一维就消失（或被合并）**"。

**例子**：`x` 形状 (2, 3)：

```
x = [[1, 2, 3],
     [4, 5, 6]]
```

- `x.sum(dim=0)`：沿第 0 维（"行"方向往下）加 → `[5, 7, 9]`，形状 (3,)
- `x.sum(dim=1)`：沿第 1 维（"列"方向往右）加 → `[6, 15]`，形状 (2,)
- `dim=-1`：最后一维。对二维张量来说 `dim=-1` 等于 `dim=1`。

**记忆方法**：`dim=k` 的那一维会被"压扁"掉。

---

## 2.3 `unsqueeze`：增加一个长度为 1 的维度

**要干什么**：给张量"加一层括号"，方便后面做 `repeat` 或广播。

**GRAM 里的真实代码**（`gram_actor_critic.py:579`）：

```python
            encoder_feature_repeat = encoder_feature.unsqueeze(dim=0).repeat((self.history_epinet_num_samples, 1, 1))
```

**手算例子**：

```
a = [1, 2, 3]                 shape (3,)
a.unsqueeze(dim=0)  → [[1, 2, 3]]          shape (1, 3)
a.unsqueeze(dim=-1) → [[1], [2], [3]]      shape (3, 1)
```

在 GRAM 里：`encoder_feature` 形状 (4096, F)，`unsqueeze(dim=0)` 变成 (1, 4096, F)，为下一步沿第 0 维复制 8 份做准备。

另一个例子（`gram_actor_critic.py:612`）：`alpha.unsqueeze(dim=-1) * latent_mean`。`alpha` 形状 (4096,)，变成 (4096, 1)，才能和形状 (4096, 8) 的 `latent_mean` 逐行相乘（见 2.11 广播）。

**小结**：`unsqueeze(k)` 在第 k 个位置插入长度 1 的维度。

**GRAM 里在哪用到**：`gram_actor_critic.py:579,584,601,612,614,739`；`gram_ppo.py` 中 epinet 相关的 history loss（约 `:280-290`）。

---

## 2.4 `repeat`：沿某些维度复制

**要干什么**：把同一份数据复制多份。GRAM 用它让"同一段历史"配上 8 个不同的随机数 ε，一次算出 8 个 epinet 输出。

**GRAM 里的真实代码**（`gram_actor_critic.py:579-587`）：

```python
            encoder_feature_repeat = encoder_feature.unsqueeze(dim=0).repeat((self.history_epinet_num_samples, 1, 1))

            epinet_samples = torch.randn(
                (self.history_epinet_num_samples, self.history_epinet_dim), device=encoder_feature.device
            )
            epinet_samples_repeat = epinet_samples.unsqueeze(dim=1).repeat((1, encoder_feature.shape[0], 1))

            # shape: (epinet_samples, batch_size, total_epinet_input_size)  # noqa: E800
            epinet_input = torch.cat([encoder_feature_repeat, epinet_samples_repeat], dim=-1)
```

**`repeat((8, 1, 1))` 的含义**：第 0 维复制 8 次，第 1、2 维各 1 次（不变）。

**手算例子**（缩小规模：2 个样本、2 个环境、特征 3 维、随机数 2 维）：

```
encoder_feature (2 环境, 3 特征) =
  [[a1, a2, a3],     ← 环境 0
   [b1, b2, b3]]     ← 环境 1

unsqueeze(0) → (1, 2, 3)
repeat((2,1,1)) → (2, 2, 3)：
  样本 0: [[a1,a2,a3],[b1,b2,b3]]
  样本 1: [[a1,a2,a3],[b1,b2,b3]]      （两份一模一样）

epinet_samples (2 样本, 2 维) =
  [[e00, e01],      ← 样本 0 的随机数
   [e10, e11]]      ← 样本 1 的随机数

unsqueeze(1) → (2, 1, 2)
repeat((1,2,1)) → (2, 2, 2)：
  样本 0: [[e00,e01],[e00,e01]]        （所有环境共用样本 0 的随机数）
  样本 1: [[e10,e11],[e10,e11]]

cat(dim=-1) → (2, 2, 5)：
  样本 0: [[a1,a2,a3,e00,e01],[b1,b2,b3,e00,e01]]
  样本 1: [[a1,a2,a3,e10,e11],[b1,b2,b3,e10,e11]]
```

**结论**：每个"样本"里，所有环境用同一组随机数 ε；不同样本用不同的 ε。所以同一个环境的历史，会配上 8 个不同的 ε 送进 epinet，得到 8 个输出。

> 【代码事实】一个细节：同一时刻，**所有环境共用这 8 个 ε**，不是每个环境各抽 8 个。这不影响结果的统计意义，但读代码时要知道。

**小结**：`repeat` = 复制；这里用于"一份历史 × 8 个随机数"。

**GRAM 里在哪用到**：`gram_actor_critic.py:579,584,634,639`；`gram_ppo.py` history loss 里 `obs_batch_repeat`（约 `:281-286`）。

---

## 2.5 `reshape` 与 `nn.Flatten`

**要干什么**：不改数据，只改"怎么分维度"。总元素数必须不变。

**GRAM 里的真实代码 1**（`gram_actor_critic.py:597-601`，epinet 的 `mlp_dot` 类型）：

```python
            elif self.history_epinet_type == "mlp_dot":
                epinet_output_difference = epinet_output_difference.reshape(
                    (epinet_output_difference.shape[0], epinet_output_difference.shape[1], -1, self.history_epinet_dim)
                )
                epinet_term_all = (epinet_output_difference * epinet_samples_repeat.unsqueeze(dim=-2)).sum(dim=-1)
```

**手算形状**：
- `epinet_output_difference`：(8 样本, 4096 环境, 64)。64 = 隐变量 8 × ε 维度 8。
- `reshape((8, 4096, -1, 8))`：`-1` 表示"这一维你自己算"，64 ÷ 8 = 8，结果 (8, 4096, 8, 8)，可以看作每个样本、每个环境一个 8×8 的矩阵 M。
- `epinet_samples_repeat.unsqueeze(dim=-2)`：(8, 4096, 8) → (8, 4096, 1, 8)。
- 相乘再 `sum(dim=-1)`：就是矩阵 M 乘以向量 ε：结果 (8, 4096, 8)。

**用一个 2×2 的小例子手算"矩阵乘向量"**：

```
M = [[1, 2],      ε = [10, 20]
     [3, 4]]

M * ε（广播，每一行逐元素乘 ε）= [[10, 40],
                                  [30, 80]]
sum(dim=-1) = [50, 110]   ← 正好等于 M @ ε
```

**含义**：`mlp_dot` 型 epinet 先根据历史特征算出一个 8×8 矩阵，再乘以随机向量 ε。输出对 ε 是**线性**的：ε 变，输出跟着按比例变。这样网络只要把矩阵学成接近 0，输出就几乎不随 ε 变化，方差就小。这正是"训练见过的输入上方差小"的实现方式。

**GRAM 里的真实代码 2**（`gram_actor_critic.py:169-171`）：

```python
        encode_layers = []
        encode_layers.append(nn.Flatten())
        encode_layers.append(nn.Linear(num_actor_obs * self.obs_history_length, history_encoder_hidden_dims[0]))
```

`nn.Flatten()` 把 (4096, 16, 45) 展平成 (4096, 720)：保留第 0 维（环境），把后面的维度连成一条。所以历史编码器的输入是 16 × 45 = 720 维的长向量【45 为推断值】。

**小结**：`reshape` 只换维度划分；`-1` 自动推算；`Flatten` 把每个样本拉成一条向量。

**GRAM 里在哪用到**：`gram_actor_critic.py:170,186,571,573,598,653`。

---

## 2.6 `cat`：拼接

**要干什么**：把几个张量沿某一维首尾相接。

**GRAM 里的真实代码**（`gram_actor_critic.py:449-453`）：

```python
    def update_distribution(self, observations, latent, robust_masks):
        actor_input = torch.cat([observations, latent], dim=-1)
        if self.robust_as_zeros:
            robust_latent = torch.zeros_like(latent.detach())
            robust_actor_input = torch.cat([observations, robust_latent], dim=-1)
```

**逐行解释**：
- `torch.cat([observations, latent], dim=-1)`：把观测和隐变量**横着拼**，作为策略网络的输入。这就是论文里 π(a | s, z) 的 "s, z"。
- `torch.zeros_like(x)`：造一个和 x 形状、类型、设备都一样的全 0 张量。这里就是 z_rob = 0。
- 鲁棒分支的输入 = [观测, 全 0]。

**手算例子**：

```
observations (2 环境, 3) = [[1,2,3],[4,5,6]]
latent       (2 环境, 2) = [[0.1,0.2],[0.3,0.4]]
cat(dim=-1) → (2, 5) = [[1,2,3,0.1,0.2],
                        [4,5,6,0.3,0.4]]
cat 的零向量版本     = [[1,2,3,0,0],
                        [4,5,6,0,0]]
```

**观测维度 45 是怎么来的**【推断】：GRAM 的环境继承 Isaac Lab 的 Go2 速度跟踪配置，策略观测默认包含：机身线速度 3、机身角速度 3、投影重力 3、速度指令 3、关节位置 12、关节速度 12、上一步动作 12、高度扫描若干维。GRAM 去掉了机身线速度（`unitree_go2_custom_env.py:248`，`base_lin_vel = None`）和高度扫描（`:171-173`），剩下 3+3+3+12+12+12 = **45**。实际数值以运行时打印的网络结构为准。

**小结**：`cat` 沿某维拼接；GRAM 用它把"观测 + 隐变量"拼成策略输入。

**GRAM 里在哪用到**：`gram_actor_critic.py:450,453,529-535,575,587,642`；`gram_on_policy_runner.py:399`（拼日志）。

---

## 2.7 `sum(dim)`、`mean(dim)`、`var(dim)`

**要干什么**：沿某一维求和、求平均、求方差。GRAM 的**不确定性**就是用这三个算出来的，必须吃透。

**GRAM 里的真实代码**（`gram_actor_critic.py:603-609`）：

```python
            latent_all = latent + self.history_epinet_coef_active * epinet_term_all
            latent_mean = latent_all.mean(dim=0)

            if self.history_epinet_apply_bias:
                latent_std_l2 = latent_all.var(dim=0).sum(dim=-1)
                uncertainty = (latent_std_l2 - self.history_epinet_shift_param).clamp(min=0)
                alpha = torch.exp(self.history_epinet_scale_param * uncertainty * -1)
```

**形状变化**：

| 表达式 | 形状 | 含义 |
|---|---|---|
| `latent` | (4096, 8) | base 网络的输出，每个环境一个 8 维估计 |
| `epinet_term_all` | (8, 4096, 8) | epinet 对 8 个 ε 的输出 |
| `latent + ...` | (8, 4096, 8) | 广播相加，8 个"集成成员"的估计 |
| `latent_all.mean(dim=0)` | (4096, 8) | 8 个样本的平均 = 论文的 μ̂ |
| `latent_all.var(dim=0)` | (4096, 8) | 8 个样本的方差，**每一维各一个** = 论文的 σ̂² |
| `.sum(dim=-1)` | (4096,) | 8 维方差加起来，**每个环境一个标量** = 论文的 ‖σ̂‖² |

**手算例子**【已验证】（3 个样本、1 个环境、隐变量 2 维）：

```
3 个样本的估计：
  样本 0: [1, 2]
  样本 1: [3, 2]
  样本 2: [5, 2]

mean(dim=0) = [(1+3+5)/3, (2+2+2)/3] = [3, 2]

var(dim=0)：
  第 0 维：值 1,3,5，均值 3，偏差平方 4,0,4，和 8，除以 (3-1)=2 → 4
  第 1 维：值 2,2,2，方差 0
  = [4, 0]

sum(dim=-1) = 4 + 0 = 4
```

**注意两点**：
1. `torch.var` 默认是**无偏估计**，除以 N−1 而不是 N，对应论文式 (7) 的 1/(N−1)。
2. **`.sum(dim=-1)` 这一步把"哪一维不确定"的信息丢掉了**。上例中第 0 维很不确定（方差 4），第 1 维完全确定（方差 0），加起来只剩一个数 4。**这就是我们方向要改的地方**：如果第 0 维代表"电机"、第 1 维代表"地面"，求和后就分不出是谁不确定。

**小结**：`mean(dim=0)` 得到 μ̂；`var(dim=0)` 得到每维方差；`sum(dim=-1)` 把每维方差压成一个标量。

**GRAM 里在哪用到**：`gram_actor_critic.py:604,607,677,687-693`；`gram_ppo.py` history loss（`.pow(2).sum(dim=-1).mean(dim=0)`，约 `:244-250`）；`gram_on_policy_runner.py:751`（按存活步数求 α 的平均）。

---

## 2.8 `clamp`：截断到范围内

**要干什么**：把小于下限的值改成下限，大于上限的值改成上限。

**GRAM 里的真实代码 1**（`gram_actor_critic.py:608`）：

```python
                uncertainty = (latent_std_l2 - self.history_epinet_shift_param).clamp(min=0)
```

这就是论文式 (9) 里的 (·)⁺ = max(·, 0)。

**手算例子**（shift β = 2.0）：

```
latent_std_l2 = [1.5, 2.0, 3.2]
减去 β        = [-0.5, 0.0, 1.2]
clamp(min=0)  = [0.0, 0.0, 1.2]
```

前两个环境不确定性没超过阈值，`uncertainty = 0`，后面算出 α = 1，完全相信估计。

**GRAM 里的真实代码 2**（`gram_actor_critic.py:463-464`）：

```python
        mean = robust_masks * robust_mean + (1 - robust_masks) * adapt_mean
        mean_clamp = mean.clamp(min=-20.0, max=20.0)
```

动作均值被限制在 [−20, 20]，防止网络输出极端值导致数值问题。

**小结**：`clamp(min=, max=)` 截断；GRAM 用它实现 (·)⁺ 和防止数值爆炸。

**GRAM 里在哪用到**：`gram_actor_critic.py:464,559,608,666-672`（限制 log_std 范围）；`envs_utils.py:167`（关节目标限位）、`:284`（对抗动作）。

---

## 2.9 `exp` 与 GRAM 的 α

**GRAM 里的真实代码**（`gram_actor_critic.py:609`）：

```python
                alpha = torch.exp(self.history_epinet_scale_param * uncertainty * -1)
```

即 α = exp(−λ · uncertainty)。

**手算例子**：设 β = 2.0（验证集 0.90 分位数），q99 = 3.0（验证集 0.99 分位数）。

λ 的计算（`gram_actor_critic.py:719-723`）：

```
λ = −ln(0.01) / (q99 − β) = 4.605 / (3.0 − 2.0) = 4.605
```

| ‖σ̂‖² | 减 β 后 clamp | α = exp(−4.605 × ·) | 含义 |
|---|---|---|---|
| 1.5 | 0 | 1.000 | 完全相信估计 |
| 2.0 | 0 | 1.000 | 刚好到阈值 |
| 2.5 | 0.5 | exp(−2.30) = 0.100 | 大部分退回 |
| 3.0 | 1.0 | exp(−4.605) = 0.010 | 几乎完全退回 |
| 4.0 | 2.0 | 0.0001 | 完全退回 |

然后 `latent = alpha.unsqueeze(dim=-1) * latent`（`:614`）：α = 0.1 时，8 维隐变量全部缩到原来的 10%，向 0（z_rob）靠近。

**小结**：α 从 1 指数衰减到接近 0；阈值和衰减速度由验证集分位数决定。

**GRAM 里在哪用到**：`gram_actor_critic.py:609,695,719-723`。

---

## 2.10 `quantile`：分位数

**要干什么**：0.9 分位数是"有 90% 的数比它小"的那个值。GRAM 用它从验证集里自动确定 β 和 λ。

**GRAM 里的真实代码**（`gram_actor_critic.py:706-723`，节选）：

```python
    def set_uncertainty_params(self):
        # shift / scale parameters for GRAM alpha calculation
        if self.history_epinet_finetune_shift and self.validation_quantiles_saved:
            self.history_epinet_shift_param = self.validation_quantiles_value.quantile(
                q=self.history_epinet_finetune_min_quantile
            )
        ...
        if self.history_epinet_finetune_scale and self.validation_quantiles_saved:
            latent_std_l2_quantile = self.validation_quantiles_value.quantile(
                q=self.history_epinet_finetune_max_quantile
            )
            self.history_epinet_scale_param = (
                math.log(self.history_epinet_finetune_target)
                * -1
                / (latent_std_l2_quantile - self.history_epinet_shift_param)
            )
```

**怎么算分位数（线性插值）**【已验证】：

```
数据（已排序）：[1, 2, 3, 4, 5]，共 n = 5 个
quantile(0.9)：位置 = (n−1) × 0.9 = 3.6
  → 在第 3 个（值 4）和第 4 个（值 5）之间，往后走 0.6
  → 4 + 0.6 × (5 − 4) = 4.6
quantile(0.5)：位置 2.0 → 值 3（中位数）
```

**GRAM 的两步分位数**（这一点很容易看晕）：
1. 训练结束时，`collect_validation_data` 收集大量 ‖σ̂‖² 值，算出 101 个分位数（0%, 1%, …, 100%），存到 `validation_quantiles_value`（`gram_on_policy_runner.py:603`）。这 101 个数随模型一起保存进 checkpoint。
2. `set_uncertainty_params` 再对这 101 个数取 0.90 和 0.99 分位数，得到 β 和 q99。因为第 1 步已经是均匀间隔的分位数，第 2 步的结果近似等于原始数据的 0.90、0.99 分位数。

**小结**：`quantile(q)` 用线性插值求分位数；GRAM 用验证集的 q90 当阈值 β，用 q99 决定衰减速度 λ。

**GRAM 里在哪用到**：`gram_actor_critic.py:157-160,706-730`；`gram_on_policy_runner.py:603,738-747`（打印 α 分布）。

---

## 2.11 广播（broadcasting）

**要干什么**：形状不同的张量做逐元素运算时，PyTorch 会自动把长度为 1 的维度"扩展"到对方的长度，不用手动复制。

**规则**：从最后一维往前对齐比较，每一维要么相等，要么其中一个是 1（或缺失），否则报错。

**GRAM 里的真实代码**（`gram_actor_critic.py:463`）：

```python
        mean = robust_masks * robust_mean + (1 - robust_masks) * adapt_mean
```

**形状**：`robust_masks` (4096, 1)，`robust_mean` 和 `adapt_mean` (4096, 12)。(4096, 1) 的第 1 维是 1，被广播成 12。

**手算例子**（2 个环境、3 个关节）：

```
robust_masks = [[1],      ← 环境 0：鲁棒训练
                [0]]      ← 环境 1：适应训练
robust_mean  = [[9, 9, 9],
                [9, 9, 9]]
adapt_mean   = [[1, 2, 3],
                [4, 5, 6]]

robust_masks * robust_mean       = [[9,9,9],[0,0,0]]
(1 − robust_masks) * adapt_mean  = [[0,0,0],[4,5,6]]
相加 mean                        = [[9,9,9],[4,5,6]]
```

**含义**：每个环境按自己的 mask 选择用鲁棒分支还是适应分支的输出。这种"乘 mask 再相加"的写法相当于**逐环境的 if-else**，但能在 GPU 上并行。

**另一个广播**（`gram_actor_critic.py:603`）：`latent` (4096, 8) + `epinet_term_all` (8, 4096, 8)。前者缺第 0 维，自动补成 (1, 4096, 8) 再扩成 (8, 4096, 8)。也就是 8 个样本共用同一个 base 输出，各自加上不同的 epinet 项。

**小结**：广播 = 自动扩展长度为 1 的维度；GRAM 用"mask × A + (1 − mask) × B"实现逐环境选择。

**GRAM 里在哪用到**：`gram_actor_critic.py:463,467,470,544,603,612,614`；`gram_ppo.py` 中 `robust_masks_batch` 相关（约 `:234-236,253-256`）；`envs_utils.py:291`（对抗推力 × mask）。

---

## 2.12 布尔索引与掩码

**要干什么**：按条件挑出张量的一部分。

**GRAM 里的真实代码**（`gram_actor_critic.py:735-741`，Modular 消融用的硬切换）：

```python
    def calculate_uncertainty_mask(self, uncertainty_metric):
        uncertainty_mask_bool = uncertainty_metric > self.uncertainty_max_threshold
        uncertainty_mask_bool[torch.isnan(uncertainty_metric)] = False

        uncertainty_mask = uncertainty_mask_bool.to(dtype=torch.float32).unsqueeze(dim=-1)

        return uncertainty_mask
```

**逐行解释**：
- `uncertainty_metric > 阈值`：逐元素比较，得到布尔张量（True/False）。
- `x[torch.isnan(...)] = False`：把 NaN（无效值）对应位置设为 False。方括号里放布尔张量，就是"只选 True 的位置"。
- `.to(dtype=torch.float32)`：True→1.0，False→0.0，变成可以参与乘法的 mask。
- `.unsqueeze(dim=-1)`：(4096,) → (4096, 1)，方便广播。

**手算例子**（阈值 3.0）：

```
uncertainty_metric = [1.0, 3.5, nan, 2.9]
> 3.0              = [F, T, F, F]     （nan 比较结果为 F，又被显式设为 F）
转 float           = [0., 1., 0., 0.]
unsqueeze(-1)      = [[0.],[1.],[0.],[0.]]
```

只有第 1 个环境切到鲁棒策略。

**另一个例子**（`gram_on_policy_runner.py:738`）：`alpha[alive_mask == 1].quantile(q=0.01)`，只统计"机器人还活着（没摔倒）"那些时刻的 α。

**小结**：比较运算得到布尔张量；方括号里放布尔张量就是按条件选取。

**GRAM 里在哪用到**：`gram_actor_critic.py:735-741`；`gram_on_policy_runner.py:732-768`（评估统计）。

---

## 2.13 随机数：`torch.randn`、`torch.rand`、`torch.bernoulli`

| 函数 | 分布 | GRAM 里的用途 |
|---|---|---|
| `torch.randn(形状)` | 标准正态 N(0, 1) | epinet 的随机输入 ε（`gram_actor_critic.py:581,636`） |
| `torch.randn_like(x)` | 同上，形状同 x | 随机上下文编码器加噪（`:562`，默认关闭） |
| `torch.rand(形状)` | 均匀分布 [0, 1) | 训练时初始站姿的随机比例（`envs_utils.py` 的 `reset_joints_train`） |
| `torch.bernoulli(p)` | 以概率 p 取 1 | 对抗者每一步是否施加推力，p = 0.05（`gram_adversary.py:135-138`） |

**手算例子：`torch.bernoulli`**

```
p = [0.05, 0.05, 0.05, 0.05]（4 个环境）
torch.bernoulli(p) 可能得到 [0., 0., 1., 0.]
```

平均每 20 步有 1 步被推。这就是论文"5% of the time"的实现。

**随机种子**（`train.py:56-59`）：

```python
    random.seed(agent_cfg.seed)
    np.random.seed(agent_cfg.seed)
    torch.manual_seed(agent_cfg.seed)
    torch.cuda.manual_seed(agent_cfg.seed)
```

固定种子后，"随机"序列就固定了，同样的设置跑两次结果应该接近。【推断】GPU 并行物理仿真本身可能有不确定性，所以不保证每一位都相同。论文没有写用了几个种子。

**小结**：`randn` 正态、`rand` 均匀、`bernoulli` 抛硬币；种子决定随机序列。

---

# 第三部分 神经网络

## 3.1 `nn.Module`

**要干什么**：PyTorch 里所有网络的"基类"。继承它之后：
- 在 `__init__` 里赋给 `self.xxx` 的子网络、参数会被**自动登记**；
- `.parameters()` 能列出所有可训练参数；
- `.to(device)` 能把整个网络搬到 GPU；
- `.state_dict()` 能导出全部参数，用于保存。

**GRAM 里的真实代码**：`GRAMActorCritic(nn.Module)`（`gram_actor_critic.py:22`）里有 `self.actor`、`self.critic`、`self.context_encoder`、`self.history_encoder`、`self.history_epinet_trainable`、`self.history_epinet_prior` 等子网络，全部自动登记。

**`forward` 方法**：一般网络会定义 `forward`，调用 `net(x)` 时自动执行它。**GRAM 的 `GRAMActorCritic.forward` 直接抛出 `NotImplementedError`**（`:419-420`），因为它不是"一个输入一个输出"的网络，而是一组网络的容器，外部通过 `act`、`evaluate`、`encode_history` 等方法调用。其中的子网络（如 `self.actor`）是 `nn.Sequential`，可以直接 `self.actor(x)` 调用。

**小结**：`nn.Module` = 网络的基类，负责登记参数、搬设备、保存加载。

---

## 3.2 `nn.Linear`、`nn.Sequential` 与 ELU 激活

**要干什么**：搭建多层感知机（MLP）。GRAM 的所有网络都是 MLP。

**GRAM 里的真实代码**（`gram_actor_critic.py:91-104`，策略网络）：

```python
        mlp_input_dim_a = num_actor_obs + num_latent
        ...
        actor_layers = []
        actor_layers.append(nn.Linear(mlp_input_dim_a, actor_hidden_dims[0]))
        actor_layers.append(activation)
        for layer_index in range(len(actor_hidden_dims)):
            if layer_index == len(actor_hidden_dims) - 1:
                actor_layers.append(nn.Linear(actor_hidden_dims[layer_index], num_actions))
            else:
                actor_layers.append(nn.Linear(actor_hidden_dims[layer_index], actor_hidden_dims[layer_index + 1]))
                actor_layers.append(activation)
        self.actor = nn.Sequential(*actor_layers)
```

**逐行解释**：
- `nn.Linear(输入维, 输出维)`：全连接层，计算 y = W·x + b。W 是"输出维 × 输入维"的矩阵，b 是偏置向量。
- `activation`：激活函数，这里是 ELU（`:76` 由字符串 `"elu"` 转成）。没有激活函数，多层线性层叠起来还是线性的，表达不了复杂关系。
- 循环：按 `actor_hidden_dims = [512, 256, 128]` 依次加层。
- `nn.Sequential(*列表)`：把层按顺序串起来，`self.actor(x)` 就依次过每一层。`*` 把列表拆开成多个参数。

**展开后的结构**（输入 45 + 8 = 53 维【45 为推断值】）：

```
索引 0: Linear(53 → 512)
索引 1: ELU
索引 2: Linear(512 → 256)
索引 3: ELU
索引 4: Linear(256 → 128)
索引 5: ELU
索引 6: Linear(128 → 12)     ← 输出 12 个关节的动作均值，最后一层没有激活
```

这也解释了 checkpoint 里的参数名 `actor.0.weight`、`actor.2.weight`、`actor.4.weight`、`actor.6.weight`：数字就是 Sequential 里的索引，ELU 没有参数，所以 1、3、5 不出现。

**参数量手算**：Linear(53→512) 有 53×512 + 512 = 27,648 个参数。

**ELU 激活**：

```
ELU(x) = x            当 x > 0
       = e^x − 1      当 x ≤ 0
```

| x | ELU(x) |
|---|---|
| 2.0 | 2.0 |
| 0.0 | 0.0 |
| −1.0 | e^−1 − 1 = −0.632 |
| −5.0 | −0.993 |

和 ReLU 相比，负数部分不是 0，而是平滑趋近 −1，梯度不会完全消失。

**切片取子网络**（`gram_actor_critic.py:574`）：

```python
                encoder_feature = self.history_encoder[:-1](observations_history).detach()
```

`nn.Sequential` 支持切片，`[:-1]` 表示"去掉最后一层"。历史编码器结构是 `Flatten, Linear(720→512), ELU, Linear(512→256), ELU, Linear(256→128), ELU, Linear(128→8)`，去掉最后一层后输出的是 128 维的"最后一个隐藏层特征"。这就是论文式 (5) 里 h̃ 用到的 "the output from the last hidden layer of φ_base"。

**小结**：`Linear` = 矩阵乘加偏置；`Sequential` = 按顺序串起来；ELU = 平滑版 ReLU；`[:-1]` 取掉最后一层得到隐藏特征。

**GRAM 里在哪用到**：`gram_actor_critic.py:94-138`（actor、critic、上下文编码器）、`:169-181`（历史编码器）、`:197-263`（epinet）、`:290-316`（独立鲁棒网络，仅 Modular/鲁棒 RL/DR 使用）；`gram_adversary.py`（对抗者网络）。

---

## 3.3 参数、`requires_grad`、`nn.Parameter`

**要干什么**：区分"要训练的数"和"固定的数"。

- `requires_grad=True`：这个张量参与求导，训练时会被更新。`nn.Linear` 的 W、b 默认如此。
- `requires_grad=False`：不求导，不会被优化器改变。

**GRAM 里的真实代码 1：可训练的动作标准差**（`gram_actor_critic.py:122-126`）：

```python
        self.use_log_std = use_log_std
        if self.use_log_std:
            self.log_std = nn.Parameter(torch.log(init_noise_std * torch.ones(num_actions)))
        else:
            self.std = nn.Parameter(init_noise_std * torch.ones(num_actions))
```

- `nn.Parameter(张量)`：把一个普通张量登记为网络的可训练参数。
- 存 log_std 而不是 std：std 必须大于 0，存对数后可以取任意实数，用的时候 `torch.exp(self.log_std)` 一定是正数（`:434-438`）。
- 初值：`init_noise_std = 1.0` → log_std = log(1) = 0 → std = 1。

**GRAM 里的真实代码 2：冻结的先验网络**（`gram_actor_critic.py:226-227`）：

```python
                self.history_epinet_prior = nn.Sequential(*epinet_layers)
                self.history_epinet_prior.requires_grad_(requires_grad=False)
```

epinet 的"先验网络"随机初始化后**永远不训练**，这是 epinet 能区分"见过/没见过"的关键（见 [01 前置知识](../01_background.CN.md) 4.2 节）。

**GRAM 里的真实代码 3：不训练但要保存的数**（`gram_actor_critic.py:157-159`）：

```python
        self.validation_quantiles_q = nn.Parameter(torch.linspace(0, 1, 101), requires_grad=False)
        self.validation_quantiles_value = nn.Parameter(torch.zeros(101), requires_grad=False)
        self.validation_quantiles_saved = nn.Parameter(torch.tensor(False), requires_grad=False)
```

为什么要包成 `nn.Parameter` 又设 `requires_grad=False`？因为这样它们会被登记进 `state_dict`，**跟着模型一起保存到 checkpoint**，评估时加载模型就能恢复 β、λ。这是个保存数据的小技巧。

- `torch.linspace(0, 1, 101)`：0 到 1 等间隔 101 个数：[0.00, 0.01, …, 1.00]。

**小结**：`nn.Parameter` 登记参数；`requires_grad=False` 冻结；GRAM 用"冻结参数"保存验证集分位数。

---

## 3.4 `itertools.chain` 拼接参数（以及 GRAM 里的一个坑）

**要干什么**：把几个网络的参数串成一个序列，交给同一个优化器。

**GRAM 里的真实代码**（`gram_actor_critic.py:369-381` 和 `:405-412`）：

```python
        if self.robust_as_zeros:
            self.ac_params = itertools.chain(
                self.actor.parameters(),
                std_params,
                self.critic.parameters(),
                self.context_encoder.parameters(),
            )

            self.ac_adapt_params = itertools.chain(
                self.actor.parameters(),
                std_params,
                self.critic.parameters(),
            )
        ...
        self.context_params = self.context_encoder.parameters()
        self.opt_params = self.ac_params

        if self.history_epinet:
            self.history_params = itertools.chain(
                self.history_encoder.parameters(),
                self.history_epinet_trainable.parameters(),
            )
```

**逐行解释**：
- `self.actor.parameters()`：返回 actor 所有参数的**生成器**（generator，一种"逐个吐出元素"的对象）。
- `itertools.chain(a, b, c)`：把几个序列首尾串起来，逐个吐出。
- 用途：
  - `opt_params`（= `ac_params`）：交给主优化器，训练 actor、std、critic、上下文编码器（`gram_ppo.py:59`）；
  - `history_params`：交给历史优化器，训练历史编码器和 epinet 的可训练部分（`gram_ppo.py:61`），**注意不包括 prior**；
  - `ac_adapt_params`、`context_params`：用于梯度裁剪（`gram_ppo.py:217,220`）。

**一个需要知道的坑**【代码事实 + 已验证】：生成器和 `itertools.chain` **只能遍历一次**，遍历完就空了。
- `optim.Adam(opt_params, ...)` 在构造时会把参数全部读出来存到优化器内部，这没问题；
- 但 `ac_adapt_params`、`context_params`、`history_params` 被反复传给 `clip_grad_norm_`（`gram_ppo.py:217,220,333,593`）。第一次调用后它们就空了，之后的调用拿到的是空序列。
- `history_params` 更早就被 `Adam` 的构造函数读空了，所以 `:333` 的裁剪一次都不会生效。

本地小实验【已验证，PyTorch 1.13】：

```python
g = itertools.chain(m.parameters())
clip_grad_norm_(g, 1.0)   # 第一次：返回 244.95（真的算了梯度范数并裁剪）
clip_grad_norm_(g, 1.0)   # 第二次：返回 0.0（序列已空，什么都没做）
```

【推断】因此 GRAM 训练中，梯度裁剪实际上**只在第一次小批量更新时对 actor/critic 生效，之后基本不起作用**；历史编码器从未被裁剪。PPO 本身有比例裁剪和自适应学习率，训练仍然能收敛，论文结果就是在这种实现下得到的。复现时**不要随手"修正"它**，否则训练行为会和论文不同；如果要改，应作为一个单独记录的变量。（PyTorch 2.x 的 `clip_grad_norm_` 对生成器的处理方式相同，服务器 torch 2.7 上应同样如此，未在服务器上单独验证。）

**小结**：`itertools.chain` 串参数给优化器；但它只能用一次，GRAM 的梯度裁剪因此基本不生效。

---

## 3.5 初始化：Xavier 与 gain

**要干什么**：给网络的权重一个合适的初值。初值太大，输出会爆炸；太小，信号传不下去。

**GRAM 里的真实代码 1**（`source/utils/torch_utils.py:11-16`）：

```python
def weight_init(module):
    """Initializes PyTorch module weights based on Xavier normal."""
    if isinstance(module, nn.Linear):
        nn.init.xavier_normal_(module.weight)
        try:
            module.bias.data.zero_()
```

**GRAM 里的真实代码 2**（`gram_actor_critic.py:346-359`）：

```python
        if init_nn_weights:
            self.apply(weight_init)
            nn.init.xavier_normal_(self.actor[-1].weight, gain=actor_gain)
            nn.init.xavier_normal_(self.critic[-1].weight, gain=critic_gain)
            nn.init.xavier_normal_(self.context_encoder[-1].weight, gain=context_gain)
            nn.init.xavier_normal_(self.history_encoder[-1].weight, gain=history_gain)
            ...
        if self.history_epinet:
            nn.init.xavier_normal_(self.history_epinet_trainable[-1].weight, gain=history_epinet_gain)
            nn.init.xavier_normal_(self.history_epinet_prior[-1].weight, gain=history_epinet_prior_gain)
```

**逐行解释**：
- `self.apply(weight_init)`：对网络里**每一个**子模块调用一次 `weight_init`。是 Linear 就用 Xavier 正态初始化权重、把偏置清零。
- Xavier 正态：权重从 N(0, std²) 抽取，std = gain × √(2 / (输入维 + 输出维))。默认 gain = 1。
- 然后**单独重新初始化每个网络的最后一层**，gain 设为 1e-4（命令行默认值，`cli_utils.py:96-102`），只有先验网络的 gain 是 1.0（`:104-106`）。
- `self.actor[-1]`：Sequential 的最后一个元素，即输出层。

**手算例子**：

| 层 | 输入→输出 | gain | std = gain × √(2/(in+out)) |
|---|---|---|---|
| actor 最后一层 | 128 → 12 | 1e-4 | 1e-4 × √(2/140) = 1e-4 × 0.1195 ≈ 1.2e-5 |
| 上下文编码器最后一层 | 64 → 8 | 1e-4 | 1e-4 × √(2/72) ≈ 1.7e-5 |
| epinet 先验最后一层 | 16 → 64 | 1.0 | √(2/80) ≈ 0.158 |
| actor 第一层 | 53 → 512 | 1（默认） | √(2/565) ≈ 0.0595 |

**为什么最后一层 gain 这么小**：这样刚开始训练时，所有网络的**输出都几乎是 0**：
- actor 输出 ≈ 0 → 动作 ≈ 0 → 关节目标 ≈ 默认站姿，机器人一开始"站着不乱动"；
- 上下文编码器输出 ≈ 0 → **z ≈ 0 = z_rob**。这正是论文说的"the privileged context encoding z_t = f(c_t) begins training near z_rob = 0_d"。代码就是靠这个初始化实现的；
- epinet 可训练部分输出 ≈ 0，而**先验网络 gain = 1，输出不小**。所以训练开始时 epinet 的输出主要由先验决定，随 ε 变化很大；训练后，可训练部分在"见过的输入"上学会抵消先验。

**小结**：Xavier 初始化按层大小定方差；GRAM 把最后一层缩得极小，使训练从"输出≈0、z≈z_rob"开始；只有 epinet 先验保持正常大小。

**GRAM 里在哪用到**：`torch_utils.py:11-35`；`gram_actor_critic.py:346-359`；`gram_adversary.py`（对抗者最后一层同理）。

---

# 第四部分 训练的机械过程

## 4.1 前向、损失、反向、更新

神经网络训练的每一步都是这四件事：

```
1. 前向（forward）：输入数据，算出输出
2. 损失（loss）：比较输出和目标，算出一个标量，越小越好
3. 反向（backward）：自动求出损失对每个参数的梯度（偏导数）
4. 更新（step）：每个参数沿着让损失变小的方向挪一小步
```

**GRAM 里的真实代码**（`gram_ppo.py:215-221`，PPO 的更新）：

```python
            self.optimizer.zero_grad()
            loss.backward()
            nn.utils.clip_grad_norm_(self.actor_critic.ac_adapt_params, self.max_grad_norm)
            ...
            nn.utils.clip_grad_norm_(self.actor_critic.context_params, self.max_grad_norm)
            self.optimizer.step()
```

**逐行解释**：
- `zero_grad()`：把上一次留下的梯度清零。PyTorch 的梯度默认是**累加**的，不清零会把多次的梯度加在一起。
- `loss.backward()`：从损失出发，沿着计算图往回求所有参数的梯度，存在每个参数的 `.grad` 里。
- `clip_grad_norm_`：梯度裁剪（见 4.3）。
- `optimizer.step()`：用梯度更新参数。

**一个最简单的手算例子**：只有一个参数 w = 2，输入 x = 3，目标 y = 9，用平方损失、学习率 0.01、普通梯度下降：

```
前向：ŷ = w·x = 6
损失：L = (ŷ − y)² = 9
反向：dL/dw = 2(ŷ − y)·x = 2 × (−3) × 3 = −18
更新：w ← w − 0.01 × (−18) = 2.18
```

w 变大了，下一次 ŷ = 6.54，更接近 9。

**GRAM 里有三个独立的优化器**（`gram_ppo.py:59-61`）：

| 优化器 | 训练谁 | 损失 |
|---|---|---|
| `self.optimizer` | actor、std、critic、上下文编码器 | PPO 损失（式 3、式 10） |
| `self.adversary_optimizer` | 对抗者 | 对抗者的 PPO 损失（让策略回报变低） |
| `self.history_optimizer` | 历史编码器 + epinet 可训练部分 | 历史损失（式 8：回归 f(c)） |

**小结**：每次训练 = 清梯度 → 反向 → 裁剪 → 更新；GRAM 有三套独立的"参数 + 优化器 + 损失"。

---

## 4.2 优化器 Adam

**要干什么**：比普通梯度下降更聪明地更新参数。它为每个参数维护"梯度的滑动平均"和"梯度平方的滑动平均"，自动调整每个参数的步长。几乎所有深度强化学习都用它。

**GRAM 里的真实代码**（`gram_ppo.py:59-61`）：

```python
        self.optimizer = optim.Adam(self.actor_critic.opt_params, lr=self.learning_rate)
        self.adversary_optimizer = optim.Adam(self.adversary_policy.parameters(), lr=self.adversary_lr)
        self.history_optimizer = optim.Adam(self.actor_critic.history_params, lr=self.history_lr)
```

- `lr`：学习率，每步走多大。历史优化器默认 1e-3（`cli_utils.py:224`）。
- 主优化器的学习率是**自适应**的（`gram_ppo.py:190` 附近修改 `param_groups` 里的 `lr`）：根据新旧策略的 KL 散度自动调大调小。【推断】基础值和规则继承自 Isaac Lab Go2 的 PPO 默认配置（学习率 1e-3、`schedule="adaptive"`、`desired_kl=0.01`），需在安装的 Isaac Lab 里核对。服务器冒烟测试日志里学习率从 0.00225 变到 0.003375，说明自适应调整在起作用。

**小结**：Adam 是自带"自适应步长"的优化器；学习率可以在训练中被修改。

---

## 4.3 梯度裁剪 `clip_grad_norm_`

**要干什么**：如果某次梯度特别大，会让参数一下子跳太远，训练崩掉。裁剪的做法是：把所有参数的梯度拼成一个大向量，算它的长度（L2 范数）；如果超过上限，就整体等比例缩小到上限。

**手算例子**：两个参数的梯度是 [3, 4]，范数 = √(9+16) = 5；上限 `max_grad_norm = 1.0`，缩放系数 = 1/5，裁剪后 = [0.6, 0.8]，方向不变，长度变成 1。

**GRAM 里的位置**：`gram_ppo.py:217,219,220,333,415,593`。

> 如 3.4 节所述，GRAM 里传入的多数是"只能用一次的迭代器"，【推断】所以这些裁剪基本不生效（对抗者 `:415` 用的是 `self.adversary_policy.parameters()`，每次调用都新生成，**对抗者的裁剪是正常生效的**）。

**小结**：裁剪 = 梯度太长就等比例缩短。

---

## 4.4 `detach` 与 `torch.no_grad` / `torch.inference_mode`

三者都和"不要求导"有关，但作用范围不同。

| 写法 | 作用范围 | 效果 |
|---|---|---|
| `x.detach()` | **一个张量** | 得到一个数值相同、但"切断了和前面计算的联系"的张量。之后的计算对它求导时，梯度不会传回前面 |
| `with torch.no_grad():` | **一段代码块** | 块里的所有计算都不记录计算图，省内存、更快，结果不能求导 |
| `with torch.inference_mode():` | 一段代码块 | 和 `no_grad` 类似，限制更严、更快，专门用于推理 |

**GRAM 里的真实代码 1：`detach` 切断梯度**（`gram_actor_critic.py:571-575`）：

```python
            if self.history_epinet_input_type == "full":
                encoder_feature = self.input_flattener(observations_history).detach()
            elif self.history_epinet_input_type == "concat":
                full_feature = self.input_flattener(observations_history).detach()
                encoder_feature = self.history_encoder[:-1](observations_history).detach()
                encoder_feature = torch.cat([full_feature, encoder_feature], dim=-1)
```

这就是论文式 (5) 里说的 "with gradients stopped as in [8]"：epinet 用 base 网络的隐藏特征作为输入，但**训练 epinet 时梯度不回传到 base 网络**。否则 epinet 的训练会改动 base 网络的特征，两者互相干扰。

**手算理解**：设 h = w·x，y = 3·h，L = y。
- 不 detach：dL/dw = 3·x，w 会被更新；
- 若 y = 3·h.detach()：对 L 求导时 h 被当作常数，dL/dw = 0，w 不动。

**GRAM 里的真实代码 2：`detach` 防止鲁棒分支影响隐变量**（`gram_actor_critic.py:452`）：

```python
            robust_latent = torch.zeros_like(latent.detach())
```

这里 `zeros_like` 本来就和 latent 的数值无关，加 `detach` 是保险写法，保证鲁棒分支不会有梯度流回上下文编码器。

**GRAM 里的真实代码 3：`no_grad` 计算"目标值"**（`gram_ppo.py:230-238` 附近，节选）：

```python
                with torch.no_grad():
                    latent_context = self.actor_critic.encode_context(context_batch)
                    ...
```

训练历史编码器时，目标是上下文编码器的输出 f(c)。这个目标**只是标签，不应该被改动**，所以放在 `no_grad` 里算。

**GRAM 里的真实代码 4：`inference_mode` 收集数据**（`gram_on_policy_runner.py:280`）：

```python
            with torch.inference_mode():
```

和环境交互、收集数据时不需要求导，整个 rollout 放在 `inference_mode` 里。真正求导发生在之后的 `self.alg.update()` 里，它会用存下来的数据**重新前向一遍**再求导。

**小结**：`detach` 管一个张量，`no_grad`/`inference_mode` 管一段代码；GRAM 用 `detach` 实现论文里的"截断梯度"，用 `no_grad` 计算监督目标。

---

## 4.5 `train()` 与 `eval()` 模式

`nn.Module.train()` / `.eval()` 切换网络的"模式"，影响 Dropout、BatchNorm 这类层的行为。GRAM 的网络里没有这类层，所以对网络本身影响不大。

**GRAM 里真正受影响的是观测归一化器**（`gram_on_policy_runner.py:61-62,295-297`）：

```python
            self.obs_normalizer = EmpiricalNormalization(shape=[num_obs], until=None).to(self.device)
            ...
                    if self.empirical_normalization:
                        self.obs_normalizer.eval()
                        self.critic_obs_normalizer.eval()
```

- `EmpiricalNormalization`（来自 rsl_rl）：在线统计观测的均值和方差，把观测变成"均值 0、方差 1"。
- **训练模式**下，它边用边更新统计量；**评估模式**下，统计量冻结。
- GRAM 在进入 finetune 阶段时把它切到 eval 模式（`:295-297`），保证监督学习阶段的输入分布不再漂移。
- 它的统计量随 checkpoint 保存（`obs_norm_state_dict`），部署时必须一起加载，否则网络看到的输入尺度不对。

> 名字容易混：`model.eval()` 是"切到评估模式"，`source/eval.py` 是"评估脚本"，Python 的 `eval("...")` 是"执行字符串"。三者毫无关系。

**小结**：`train()/eval()` 切模式；在 GRAM 里主要影响观测归一化是否继续更新。

---

# 第五部分 概率分布

## 5.1 `Normal`：高斯分布

**要干什么**：PPO 的策略不是直接输出一个动作，而是输出一个**概率分布**，再从中抽样。这样训练时能"探索"不同动作。GRAM 用对角高斯分布：每个关节一个独立的正态分布，均值由网络给出，标准差是可训练参数。

**GRAM 里的真实代码**（`gram_actor_critic.py:463-472`）：

```python
        mean = robust_masks * robust_mean + (1 - robust_masks) * adapt_mean
        mean_clamp = mean.clamp(min=-20.0, max=20.0)

        if self.use_log_std:
            log_std = robust_masks * self.robust_log_std + (1 - robust_masks) * self.log_std
            std = torch.exp(log_std)
        else:
            std = robust_masks * self.robust_std + (1 - robust_masks) * self.std

        self.distribution = Normal(mean_clamp, mean_clamp * 0.0 + std)
```

**逐行解释**：
- 均值：按 mask 在鲁棒分支和适应分支之间选（见 2.11）。
- 标准差：同样按 mask 选。注意当 `robust_as_zeros=True`（GRAM 默认）时，`self.robust_log_std` 就是 `self.log_std` 本身（`:277`），两个分支共用同一个标准差。
- `mean_clamp * 0.0 + std`：一个小技巧。`std` 形状是 (12,)，乘 0 加上去后被广播成和 `mean_clamp` 一样的 (4096, 12)。
- `Normal(均值, 标准差)`：建一个分布对象。

**小结**：策略 = 对角高斯分布，均值来自网络，标准差是可训练参数。

---

## 5.2 `sample`、`log_prob`、`entropy`

| 方法 | 作用 | GRAM 里的位置 |
|---|---|---|
| `distribution.sample()` | 抽一个随机动作 | `gram_actor_critic.py:482,499,518` |
| `distribution.mean` | 不抽样，直接用均值（确定性动作，评估用） | `:424,497,516` |
| `distribution.log_prob(a)` | 动作 a 在这个分布下的**对数概率密度** | `:447`，PPO 算新旧策略比值时用 |
| `distribution.entropy()` | 分布的**熵**，越大越"随机" | `:432`，PPO 损失里加熵奖励鼓励探索 |

**GRAM 里的真实代码**（`gram_actor_critic.py:430-432,446-447`）：

```python
    @property
    def entropy(self):
        return self.distribution.entropy().sum(dim=-1)
    ...
    def get_actions_log_prob(self, actions):
        return self.distribution.log_prob(actions).sum(dim=-1)
```

为什么要 `.sum(dim=-1)`：12 个关节是独立的，联合分布的对数概率 = 各关节对数概率之**和**，联合熵 = 各关节熵之**和**。结果是每个环境一个数。

**手算例子**【已验证】：标准正态 N(0, 1)：

```
log_prob(0) = −0.5 × ln(2π) = −0.9189
log_prob(1) = −0.9189 − 0.5 × 1² = −1.4189
entropy     = 0.5 × ln(2πe) = 1.4189
```

GRAM 初始 std = 1（3.3 节），12 个关节，所以训练开始时每个环境的策略熵 = 12 × 1.4189 ≈ **17.03**。训练中 std 逐渐变小，熵下降，说明策略越来越"确定"。看训练日志时可以用这个数判断探索程度。

**`log_prob` 在 PPO 里怎么用**（概念）：PPO 要算"新策略选这个动作的概率 ÷ 旧策略选这个动作的概率"，用对数写就是 exp(新 log_prob − 旧 log_prob)。这个比值被限制在 [1−ε, 1+ε] 之间，防止一次更新改太多。细节见 [code/05 PPO 与数据存储](05_ppo_and_storage.CN.md)。

**小结**：`sample` 用于训练时探索，`mean` 用于评估；`log_prob` 和 `entropy` 用于 PPO 损失；12 个关节要求和。

---

# 第六部分 保存与加载

**要干什么**：训练好的模型要存到硬盘，评估或部署时再读回来。

**GRAM 里的真实代码**（`gram_on_policy_runner.py:159-176`，保存）：

```python
    def save(self, path, infos=None):
        saved_dict = {
            "model_state_dict": self.alg.actor_critic.state_dict(),
            "optimizer_state_dict": self.alg.optimizer.state_dict(),
            "iter": self.current_learning_iteration,
            "infos": infos,
            "alg_name": self.cfg["alg_name"],
            "hardware_cfg": self.hardware_cfg,
            "actor_critic_cfg": self.actor_critic_cfg,
            "empirical_normalization": self.empirical_normalization,
        }
        if self.empirical_normalization:
            saved_dict["obs_norm_state_dict"] = self.obs_normalizer.state_dict()
            saved_dict["critic_obs_norm_state_dict"] = self.critic_obs_normalizer.state_dict()

        torch.save(saved_dict, path)
```

**逐行解释**：
- `state_dict()`：返回一个"参数名 → 张量"的字典，例如 `{"actor.0.weight": ..., "log_std": ..., "validation_quantiles_value": ...}`。
- `torch.save(字典, 路径)`：存成 `.pt` 文件。
- 存了什么：网络参数、优化器状态（继续训练要用）、迭代次数、算法名、网络结构配置、观测归一化统计量。
- 服务器冒烟测试的 checkpoint 约 7.0 MB、134 万个参数，和这些网络规模相符。

**加载**（`gram_on_policy_runner.py:134-157`，节选）：

```python
    def load(self, path, load_optimizer=True):
        loaded_dict = torch.load(path)
        ...
        self.alg.actor_critic.load_state_dict(loaded_dict["model_state_dict"], strict=False)
        self.alg.actor_critic.set_uncertainty_params()
```

- `load_state_dict(..., strict=False)`：把参数填回网络；`strict=False` 表示"名字对不上的就跳过，不报错"。配合 `finetune_fresh_start` 选项（`:137-145`，删掉历史编码器的参数后再加载）使用。
- 加载后立刻 `set_uncertainty_params()`：用刚加载的验证集分位数重新算 β、λ。**这一步决定了评估时 α 的计算方式**。

**小结**：`state_dict` + `torch.save` 保存，`torch.load` + `load_state_dict` 加载；GRAM 的 β、λ 也随模型保存和恢复。

---

# 自测题

1. `latent_all` 形状 (8, 4096, 8)，写出 `latent_all.var(dim=0)` 和 `latent_all.var(dim=0).sum(dim=-1)` 的形状，并说明每个数的含义。
2. 3 个样本的估计为 [2, 0]、[2, 2]、[2, 4]，手算 `mean(dim=0)`、`var(dim=0)`、`var(dim=0).sum(dim=-1)`。
3. β = 1.0，q99 = 2.0，某时刻 ‖σ̂‖² = 1.5，求 λ 和 α。
4. `robust_masks = [[0],[1]]`，`adapt_mean = [[1,1],[2,2]]`，`robust_mean = [[5,5],[6,6]]`，求 `mean`。
5. 为什么 GRAM 训练一开始 z 就接近 z_rob = 0？是哪一行代码保证的？
6. `detach()` 和 `with torch.no_grad():` 的区别是什么？GRAM 在哪里用 `detach` 实现了论文里的"截断梯度"？
7. 为什么 `validation_quantiles_value` 用 `nn.Parameter(..., requires_grad=False)` 存？
8. 为什么必须在仓库根目录用 `python -m source.train`，而不能 `python source/train.py`？
9. 12 个关节、std 都为 1 的对角高斯策略，熵是多少？如果训练后 std 都变成 e^−1 ≈ 0.368，熵变成多少？
10. GRAM 里 `itertools.chain` 造成了什么后果？复现时应该怎么处理？

<details>
<summary>参考答案</summary>

1. `var(dim=0)`：(4096, 8)，每个环境、每个隐变量维度在 8 个 ε 样本上的方差；`.sum(dim=-1)`：(4096,)，每个环境一个总不确定性 ‖σ̂‖²。
2. mean = [2, 2]；var：第 0 维 [2,2,2] 方差 0，第 1 维 [0,2,4] 均值 2、偏差平方和 8、除以 2 得 4，所以 var = [0, 4]；sum = 4。
3. λ = −ln(0.01)/(2.0 − 1.0) = 4.605；uncertainty = 1.5 − 1.0 = 0.5；α = exp(−4.605 × 0.5) = exp(−2.30) ≈ 0.10。
4. 环境 0 用适应分支 [1,1]，环境 1 用鲁棒分支 [6,6]，`mean = [[1,1],[6,6]]`。
5. 上下文编码器最后一层用 gain = 1e-4 的 Xavier 初始化，输出几乎为 0：`gram_actor_critic.py:350`（`nn.init.xavier_normal_(self.context_encoder[-1].weight, gain=context_gain)`），默认 gain 来自 `cli_utils.py:98`。
6. `detach` 只作用于一个张量，切断它和之前计算的梯度联系；`no_grad` 作用于整段代码，整段都不记录计算图。GRAM 在 `gram_actor_critic.py:571-577`（以及 `:626-632`）对 epinet 的输入特征 `.detach()`，实现论文式 (5) 的 "with gradients stopped"。
7. 包成 `nn.Parameter` 才会进入 `state_dict`，随 checkpoint 保存和加载；`requires_grad=False` 保证优化器不会改动它。这样评估时加载模型就能恢复 β、λ。
8. `-m` 让 Python 从当前目录（仓库根）开始找模块，`from source.xxx import ...` 才能找到；直接运行文件时搜索起点是 `source/` 目录本身，找不到名为 `source` 的包。
9. 每个关节熵 = 0.5·ln(2πe) + ln(std)。std = 1 时 12 × 1.4189 ≈ 17.03；std = e^−1 时每个关节 1.4189 − 1 = 0.4189，12 个共约 5.03。
10. 生成器只能遍历一次，导致传给 `clip_grad_norm_` 的 actor/critic/上下文编码器参数在第一次之后为空、历史编码器参数从一开始就为空，所以梯度裁剪基本不生效（对抗者除外）。论文结果就是在这种实现下得到的，复现时应保持原样；若要修正，应作为单独记录的实验变量，并分别报告修正前后的结果。
</details>
