# 从路径点到机器人运动

## 1. 一个回合从哪里开始

运行 `flair_example.py` 后，Python 从文件底部的 `if __name__ == "__main__":` 进入。开头的 `class Driver` 等语句先定义工具。到主程序创建 `Driver(...)`、`EnvironmentManager(...)` 等对象时，才有这次实验实际使用的驾驶器、仿真器和模型对象。主程序解析 CLI、选择路线和扰动、读取步态库、创建日志，然后进入多回合循环。每个回合开始时重置仿真状态、航点索引和 FLAIR 的在线状态。 [实验入口](../../03_code/references/FLAIR/fast_adaptation/example/flair_example.py:1463) · [回合初始化](../../03_code/references/FLAIR/fast_adaptation/example/flair_example.py:1620)

| 对象 | 保存什么 | 从哪读 |
| --- | --- | --- |
| `Driver` | 路线、当前航点编号、切换容差与速度限幅 | [定义](../../03_code/references/FLAIR/fast_adaptation/example/flair_example.py:89) |
| `FLAIR` | 数据收集器、在线拟合器、生成修正指令的对象 | [定义](../../03_code/references/FLAIR/fast_adaptation/example/flair_example.py:181) |
| `EnvironmentManager` | Brax 状态、步态库、当前步态参数、步态时钟、传感缓存 | [定义](../../03_code/references/FLAIR/fast_adaptation/example/flair_example.py:514) |
| `PerturbationManager` | 命令层扰动配置。主实验的腿部减力直接在 Brax 配置中生效 | [定义](../../03_code/references/FLAIR/fast_adaptation/example/flair_example.py:770) |
| `MetricManager` | 按时间记录参考速度、车体轨迹及补偿诊断 | [定义](../../03_code/references/FLAIR/fast_adaptation/example/flair_example.py:866) |

`--adaptation-off` 使参考速度直接作为补偿阶段的输出。`--perturbation-off` 选择健康条件。两个开关独立，因此得到健康/减力各有 FLAIR 开/关。四组均由同一个 Driver 跟同一条路线，均查同一份步态库。健康组开启补偿也可能有收益，因为有限步态库和真实仿真响应之间存在偏差。 [参数与扰动选择](../../03_code/references/FLAIR/fast_adaptation/example/flair_example.py:1472)

### 一次外层循环长什么样

下面是按实际调用顺序简写的伪代码。比如 `driver.follow_path(...)` 是让已创建的 `driver` 执行它的方法。定义里的 `self.target` 会记住当前对象的航点索引，下一次调用还可以读取它。左边三个变量接收右边函数返回的三个结果。

```python
while not driver_done:
    若累计到训练检查时机且启用了适应:
        flair.train_model()

    driver_done, v_target, w_target = driver.follow_path(最新位置与朝向)
    v_send, w_send, ... = flair.get_command(v_target, w_target, 最新状态)
    根据实验分支处理扰动并记录指令
    for each_sensor_reading in range(5):
        env_state = env_manager.step(送入底层的速度指令)
        最新状态、位姿与实测速度 = env_manager.get_sensor()
        保存反馈与主日志

    flair.add_datapoint(本轮反馈、发过的指令与原始期望)
```

这个循环中的“最新位姿”先作为下一轮 Driver 的输入，速度反馈又给 FLAIR 用于学习。代码运行到函数调用时会进入相应定义，函数返回后继续往下走。 [原循环](../../03_code/references/FLAIR/fast_adaptation/example/flair_example.py:1690)

## 2. 航点是地图上的坐标

`chicane_path` 是一个 Python 列表，每项是两个浮点数。例如第 0 项 `(0, 0)`，第 1 项 `(1.6709, 0)`。乘以 `chicane_number_laps = 2` 时，Python 把列表重复拼接一次。16 个坐标形成 32 个顺序目标，索引为 0 到 31。航点没有逐点指定机器人关节、步态或到达时间。 [路线源文件](../../03_code/references/FLAIR/fast_adaptation/example/path_config.py:1) · [载入路线](../../03_code/references/FLAIR/fast_adaptation/example/flair_example.py:1512)

`Driver.follow_path(x_pos, y_pos, quaternion)` 先计算世界坐标中的目标方向 `[target_x - x_pos, target_y - y_pos, 0]`。随后用逆旋转把它放到车体坐标里。机器人面朝东和面朝北时，地图上的同一目标对应不同的转向操作，这就是必须传入朝向的原因。四元数是用四个数字表示姿态的形式，这一步只需知道它提供坐标旋转。函数用 `atan2(车体横向分量, 车体前向分量)` 算朝向误差，用向量长度算距离。

距离小于 `0.3` 时，Driver 切换到下一目标并重新算指令。若已经是最后一个目标，就返回 `(True, 0, 0)`。其余情况下，前进速度按距离比例生成后限在 0 到 0.03，转向按朝向误差乘 0.1 后限在 −0.05 到 0.05。小于 10° 时设转向为零，大于 45° 时前进目标改为 0.005。先理解这些是示例的驾驶规则，再区分后面适应模块的速度范围。 [航点跟踪的完整实现](../../03_code/references/FLAIR/fast_adaptation/example/flair_example.py:119)

例如教学中设机器人已在第一目标附近，朝向 −30°，下一个点位于世界坐标正东方向。目标在车体左前侧，`atan2` 得到约 +30°，Driver 会给出正的偏航指令，约 0.0524 经限幅后为 0.05。实测运行以 Brax 的姿态和坐标约定为准。

## 3. 同一个速度值在链路里有三个角色

| 数值 | 源码字段 | 来自哪里 |
| --- | --- | --- |
| 参考 `(v*, ω*)` | `human_cmd_lin_x, human_cmd_ang_z` | 自动 Driver 的期望。变量名中的 `human` 沿用了人类驾驶指令接口 |
| 补偿后 `(u_v, u_ω)` | `adaptation_cmd_lin_x, adaptation_cmd_ang_z` | 交给底层的速度指令。开关决定用模型求得的值还是透传值 |
| 实测 `(v, ω)` | `sensor_vx, sensor_wz`，主 CSV 写为 `vx, wz` | Brax 物理推进后的反馈 |

例如，要求直行时 Driver 给 `(0.03, 0)`。若模型认为前进会引起正向偏转，它可能给出负的转向补偿。这里传给步态库的仍是两个速度数字。实际速度要等物理推进后才能测到。主实验 `chicane_broken_leg` 的扰动在物理模型内，`perturbation_cmd_*` 在该分支等于补偿后值。阅读其他 scaling 路线时要核对调用点，原版 `env_manager.step` 的前进参数使用 `perturbation_cmd_lin_x`，转向参数实际使用 `adaptation_cmd_ang_z`。 [发令顺序](../../03_code/references/FLAIR/fast_adaptation/example/flair_example.py:1704) · [实际传参](../../03_code/references/FLAIR/fast_adaptation/example/flair_example.py:1767)

## 4. 步态库为何能把两个数变成 18 个数

作者事先用 MAP-Elites 搜索许多正弦控制器，在正常仿真中评价它们产生的速度表现，并将表现放进二维格子。行为描述的两维是前进速度与偏航率。可以把部署期的格子想成一个按运动效果索引的表。它记录的重点是每个条目的一套步态参数。配置网格为 50 × 50，参数文件的形状为 2500 × 24。格子空缺与实际可达性要以库的数据为准。读 `genotypes.npy` 可以看步态参数，`centroids.npy` 是查找用的格子中心，另有描述符和适应度文件。 [库配置](../../03_code/references/FLAIR/fast_adaptation/example/map_elites_map/config.csv) · [加载位置](../../03_code/references/FLAIR/fast_adaptation/example/flair_example.py:586) · [离线生成程序](../../03_code/references/FLAIR/fast_adaptation/example/train_map_elites.py)

1. `EnvironmentManager.step` 收到一对新的速度指令。
2. `get_cells_indices` 按指令寻找一个中心，再用索引取出这一格的 24 个参数。判断条件比较原始指令值，指令发生数值变化时，即使仍落在同一格，也会再次查找并把 `self.timestep` 清零。
3. `inference_fn(params, env_state, timestep)` 用正弦函数算这一小步关节目标。当前示例正弦计算直接使用参数和步数，函数签名中的 `env_state` 没有参与正弦式。
4. 下一小步继续用同一个参数向量，步数加一，正弦值就会变化。到这里才出现长度 18 的动作。

每条腿有顶部关节的一组幅度和相位，中部和末端共享另一组。参数按六条腿分组存储，顺序是顶部幅度 6 个、顶部相位 6 个、下部幅度 6 个、下部相位 6 个。输出按每条腿的三个关节排列。内部例子取顶部幅度 0.8、相位 0、步数 0 时，正弦为零。步数为 12 时，正弦项为 `sin(24π/50) ≈ 0.998`，乘幅度后再乘源码中的 22.5° 缩放，顶部目标约 18°。下部两个关节的缩放为 45°，符号相反。 [正弦控制细节](../../03_code/references/FLAIR/fast_adaptation/example/utils/set_up_hexapod.py:210) · [在线查库和执行](../../03_code/references/FLAIR/fast_adaptation/example/flair_example.py:673)

| 常见数字 | 实际含义 |
| --- | --- |
| 32 | 两圈的目标编号数量 |
| 2 | 一条车体速度指令的维数 |
| 24 | 一套步态设置的参数数量 |
| 18 | 一次 Brax 环境推进收到的关节动作维数 |
| 50 | 正弦函数的一周期步数，也恰好是主程序传感日志的默认标称 Hz，两者各有用途 |
| 5 | 每条上层指令内默认的传感次数，且每次传感调用内部又执行 5 次环境 step |

## 5. 仿真怎样从动作得到新状态

`Hexapod.step` 把上一状态的物理量 `state.qp` 和 18 个目标交给 `sys.step`。物理系统计算执行器作用、接触与积分，返回新的位置、姿态、线速度和角速度。目标角度只是执行器跟踪的参考，实际角度还取决于强度、负载、速度和时间。健康模型中这些执行器强度为 60，减力配置把右侧中腿的 `leg_3_1_2` 和 `leg_3_2_3` 改为 20，`body_leg_3` 仍为 60。主实验一创建环境就选中故障配置，没有把第 16 号航点设成故障触发时刻。 [Brax reset 与 step](../../03_code/references/FLAIR/fast_adaptation/example/brax_environments/hexapod.py:11) · [减力模型](../../03_code/references/FLAIR/fast_adaptation/example/brax_environments/hexapod.py:2110)

`get_sensor` 取躯干的世界位置、四元数和欧拉角。速度在 `update_sensor` 里旋转到车体坐标。代码为每组读数保存 5 个槽位，并在 `get_sensor` 求平均。这个版本的一个源代码核查点是 `EnvironmentManager.step` 在内部推进时写入 `self.env_state`，调用传感更新却传入没有在函数内赋值的 `env_state`。按示例入口运行，这个名字解析到外层在进入调用前已有的状态，不能直接把这些槽位描述成五份全新的物理状态。复现保留原行为，若做精确的时延实验，应先用日志对照两个对象的帧号。 [源代码调用与均值](../../03_code/references/FLAIR/fast_adaptation/example/flair_example.py:689)

## 6. 看懂三层时钟

| 时钟 | 源码证据 | 用途 |
| --- | --- | --- |
| 速度指令周期 | `command_freq=10`、`command_sensor_ratio=int(50/10)=5` | 更新 Driver、修正速度、收集一组反馈 |
| 日志与反馈索引 | `sensor_freq=50`，每条指令内推进 5 次并记 5 行 | 用索引构造标称实验时间 |
| Brax 物理推进 | `EnvironmentManager.repetitions=5`，环境配置 `dt=0.04` 和 `substeps=15` | 生成步态目标并推进动力学 |

这三处的步数各自服务于不同代码层。按默认设置，一次上层指令对应 5 个记录传感步，每个传感步调用 5 次 `self.step_fn`。CSV 的 `Time` 按 `sensor_freq` 生成，论文完成时间复算使用它。终端打印的 `took ...` 来自系统墙钟，CPU 较慢只会改变这一项。要比较故障后恢复秒数，应先核准并统一使用哪一层时间。 [时间戳函数](../../03_code/references/FLAIR/fast_adaptation/example/flair_example.py:81) · [环境步长](../../03_code/references/FLAIR/fast_adaptation/example/brax_environments/hexapod.py:1169)

下一篇跟同一条速度指令及其反馈进入 FLAIR，看看两者如何组成训练样本。 [下一篇](02_feedback_and_adaptation.md)

