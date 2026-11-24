# 从反馈到下一次补偿

## 1. FLAIR 学的是动作效果

想象 Driver 要求 `(0.03, 0)`，表示小幅直行。为了抵消跑偏，FLAIR 实际发了 `(0.034, -0.015)`。过了一小段时间，车体测得 `(0.029, 0.002)`。这组示意数字各有用途。

- `(0.03, 0)` 衡量最后是否完成了驾驶意图。
- `(0.034, -0.015)` 是模型需要解释的输入。
- `(0.029, 0.002)` 是反馈提供的监督目标。

响应模型要回答“这个工况里，执行这条命令，会得到怎样的运动”。下次发令时方向倒过来，给定期望运动，找可能实现它的命令。FLAIR 在运行中拿新反馈更新响应。六足实验加载预先生成的步态库，在线更新的是补偿层。 [补偿与样本入口](../../03_code/references/FLAIR/fast_adaptation/example/flair_example.py:356)

## 2. 从五行反馈取出一条样本

`flair_example.py` 每次外层循环先发一条速度指令，随后跑默认 5 个记录传感步。循环把每步的状态、传感时间、前进速度、角速度存到 `buffer_*`。随后 `FLAIR.add_datapoint` 把这一批交给 `DataCollection.data_collection`。外层临时缓冲会在下一条命令重建，收集器内部的命令和传感滑窗跨命令保留。 [反馈缓冲与调用](../../03_code/references/FLAIR/fast_adaptation/example/flair_example.py:1760)

例如一条直行命令刚发出，身体仍沿上次命令转弯。用发令瞬间这条反馈拟合，会把上一次动作误配给新动作。收集器按时间戳保留近期命令与传感序列，定位候选窗口，分别为前进和转向寻找延迟，检查命令是否处于过渡段，最后选择代表性的指令和反馈。当相关性不足或某个分量恒定时，可沿源码中的默认区间路径阅读。收集器还会拒绝 NaN、未达到采样间隔、缺少候选数据等情况。其返回既可能是有效 `final_datapoint`，也可能是 `None` 加错误码。一条命令因此可以贡献一条样本，也可能没有样本。 [样本生成与拒绝条件](../../03_code/references/FLAIR/fast_adaptation/src/flair/functionality_controller/data_collection.py:146) · [缓冲区](../../03_code/references/FLAIR/fast_adaptation/src/flair/functionality_controller/data_collection.py:496) · [窗口与延迟](../../03_code/references/FLAIR/fast_adaptation/src/flair/functionality_controller/data_collection.py:748)

有效样本记录 ID，命令与传感时间，原始参考 `intent_*`，补偿命令 `command_*`，诊断用的 `gp_prediction_*`，传感响应 `sensor_*` 及命令侧状态。字段索引 14 是八维状态。速度分量可以从不同传感位置取代表值。训练用配对来自在线收集器。最终成绩另外通过离线 notebook 计算，两处有各自的延迟与筛选设置。 [样本字段](../../03_code/references/FLAIR/fast_adaptation/src/flair/functionality_controller/data_collection.py:324)

## 3. 数据经过三层保存

| 层 | 作用 | 调试时看什么 |
| --- | --- | --- |
| `buffer_*` 和 `DataCollection.buffer_*` | 保存待匹配的指令序列、传感序列和时间戳 | 某个读数关联了哪一次命令，配对是否跨越故障事件 |
| `FLAIR.datapoints` | 用带 ID 的固定容量结构暂存已配对样本 | 返回 `None` 的位置，ID、命令/反馈字段、有效槽位 |
| `AdaptiveGP.dataset` 与 `minibatch_dataset` | 提供响应拟合数据和近期异常检查数据 | 样本落点、被筛选数量、训练前后参数与重置 |

网格数据集把相近输入分到单元内，限制重复数据挤占容量。读 `Grid.add` 可以看更新，读 `Grid.select` 可以看邻居和新颖度相关的筛选。这里的网格放**在线观测样本**。第 1 篇讲的 MAP-Elites 网格放**预生成步态**，两者索引和用途不同。 `GRID_RESOLUTION=101` 是适应模块的一个配置值，随仓步态库的 50×50 则来自 `map_elites_map/config.csv`，不要从名字相似就推断共用网格。 [网格选择](../../03_code/references/FLAIR/fast_adaptation/src/flair/functionality_controller/dataset_grid.py:123) · [格子写入](../../03_code/references/FLAIR/fast_adaptation/src/flair/functionality_controller/dataset_grid.py:235) · [数据集配置](../../03_code/references/FLAIR/fast_adaptation/src/flair/flair/adaptation_config.py:51)

## 4. 模型什么时候更新

主循环在下一次发令前检查 `call_since_last_training`。默认 `model_command_ratio = int(10/1) = 10`，累计到门槛后调用 `FLAIR.train_model`，调用分支把计数器归零。实际以计数和分支为准。进入该方法以后：

1. `adaptive_gp.update` 将有效点加入拟合集及近期小批次。
2. 旧模型和当前样本的误差达到重置条件时，代码清空相应在线状态。触发条件使用近期匹配数据的误差统计及配置阈值。
3. `gp_update` 再检查新增点数。源码使用严格大于 `latest_train_total_position + min_diff_datapoint`，默认门槛 2，所以新增点计数达到 3 才越过该门槛。
4. 拟合成功后，将新状态参数和地图等结果写入 `self.adaptation`。随后 `FLAIR.get_command` 读取该对象里的新参数。

关闭 FLAIR 时，主循环跳过这个更新分支，`FLAIR.get_command` 输出 Driver 参考。示例仍构建对象并走共用日志路径，因此从终端看到某些 GP 相关初始化消息也符合开关行为。 [主循环训练条件](../../03_code/references/FLAIR/fast_adaptation/example/flair_example.py:1690) · [训练与参数传递](../../03_code/references/FLAIR/fast_adaptation/example/flair_example.py:421) · [新增点判断](../../03_code/references/FLAIR/fast_adaptation/src/flair/functionality_controller/adaptive_gp_state_fast.py:249) · [重置实现](../../03_code/references/FLAIR/fast_adaptation/src/flair/functionality_controller/adaptive_gp_state_fast.py:288)

## 5. 从状态算出偏差，再求修正指令

论文中的状态条件模型可以用平面朝向建模方向相关扰动。例如同一个前进命令，在迎风时与侧风时可能产生不同反馈。Driver 另用完整四元数把目标转到车体坐标，回答“目标在我的哪个方向”。

**六足示例存在一个命名与数值来源的差异。** `get_sensor` 写的是 `sensor_yaw, sensor_roll, sensor_pitch = brax.math.quat_to_euler(quaternion)`，然后把 `sensor_yaw` 放到 `state[5]`。已固定的 Brax v1 接口实际返回 `[x, y, z]` 欧拉分量，因此六足默认取到的是第一个 x 分量，而变量名和配置注释称其为 yaw。纯绕 z 轴的四元数可以验证这个顺序。本文的六足结果沿用源码，解释实机朝向条件或迁移到 Go2-W 时应显式核对坐标与索引。 [赋值和状态元组](../../03_code/references/FLAIR/fast_adaptation/example/flair_example.py:725) · [默认状态选项](../../03_code/references/FLAIR/fast_adaptation/src/flair/flair/adaptation_config.py:120) · [Brax v1 欧拉角实现](https://github.com/google/brax/blob/v0.10.2/brax/v1/math.py)

推理把选定状态裁到配置区间，再算 `p(s) = a + b*s + c*s² + d*s³` 并限幅。`a,b,c,d` 是历史样本拟合出的数字。以默认 `multi_optimisation` 读源码时，能看到它对几种候选基函数分别做有界最小二乘，选残差代价较低的一种，其他系数置零。由此能解释为什么发令函数写成多项式形式，也能解释默认单次拟合通常只保留一种基函数。样本的右侧目标来自实际速度和命令之差。最小二乘在找一组受限数字，使预测偏差和样本偏差一致。拟合里的二阶候选是带符号的平方 `sign(s)*s²`，发令表达式写的是普通平方。研究时应记录所选基函数与实测预测效果，避免将两段实现写成数学上完全相同。 [候选基函数与回归](../../03_code/references/FLAIR/fast_adaptation/src/flair/functionality_controller/adaptive_gp_state_fast.py:693)

源码把 `p` 变成两侧等效比例 `p1=min(1,1-p)`、`p2=min(1,1+p)`，再用宽度参数组成二维线性映射。这个映射是上层速度响应先验，也可用于六足输出的等效近似。两侧响应不同后，前进指令会影响转向，转向指令也能影响前进。以行向量记，预测关系是 `y ≈ u @ S + [offset, 0]`。已知期望运动 `r` 时，代码反向求 `u = (r - [offset,0]) @ inv(S)`，再夹到有效命令范围。

一个纯教学例取 `p=0.2`、宽度 0.5、offset 为 0。代码给 `p1=0.8, p2=1`，矩阵按行写为 `[[0.9,0.4],[0.025,0.9]]`。直接发 `(0.03,0)`，模型预测 `(0.027,0.012)`，前进偏低且有正转向。若要求预测得到 `(0.03,0)`，解出约 `(0.03375,-0.015)`。这就串起了“算出 p、算出两侧比例、反推指令”。真实效果仍由 Brax 下一步反馈核对。 [矩阵构造、求逆与裁剪](../../03_code/references/FLAIR/fast_adaptation/src/flair/functionality_controller/functionality_controller.py:191)

## 6. 论文的两层模型与六足发令分支

论文以全局先验解释大范围偏差，用局部高斯过程细化某些命令附近的预测。可以像查一张地图那样理解，先知道整张图大致怎样变化，再用附近实际观测补充细节。代码层面要看三个调用点。

| 问题 | 源码行为 |
| --- | --- |
| 发布版六足默认模式是什么 | `ADAPTATION_VERSION = STATE_FAST` |
| 默认下发的补偿怎样算 | `use_state=True`，进入 `_get_state_only_prior`，按状态模型求逆 |
| 带状态 GP 的查找在哪里 | `STATE_FAST_GP` 下满足状态、数据集及核等条件，进入 `_get_state_gp_prior` 后选择候选 |

`AdaptiveGP` 更新流程仍存在，`gp_prediction_*` 仍作为现成字段使用。读字段时以 `get_command` 分支为准。论文贡献可以概括为用在线反馈拟合可逆的响应模型；六足 CPU 实验的实际补偿公式应同时标注对应的默认快路径。 [适应版本](../../03_code/references/FLAIR/fast_adaptation/src/flair/flair/adaptation_config.py:14) · [发令分支](../../03_code/references/FLAIR/fast_adaptation/src/flair/functionality_controller/functionality_controller.py:233) · [论文 Methods](https://doi.org/10.1038/s41467-026-70256-y)

## 7. 从这段代码接到后续试探研究

原版已经有明确的数据边界，先匹配成样本，再加入模型，最后把新参数交给发令。在实现提议中的两分支实验时，先固定实际执行的一段试探动作和全部反馈，然后只切换选定样本对**上层模型**的可见性。保留同份原始日志用于评分。需要按命令及反馈窗口追踪试探样本 ID，防止被拒绝的样本换批后重新入库或跨过故障边界混入。这个切口可以检查相同动作的反馈通过模型究竟产生了多少后续收益。 [研究计划](../../99_archive/history.zip)

