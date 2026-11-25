# 从日志到论文结果

## 1. 三项复现工作各验证了什么

| 工作 | 实际运行路径 | 可回答的问题 |
| --- | --- | --- |
| 作者数据复算 | 作者四份 CSV 和六足分析 notebook | 已发表数据按公开脚本能否得到报告指标 |
| 原版四组试跑 | 服务器隔离 Conda 环境运行 v1.0.0 原入口 | 本方环境能否用发布代码从航点走到终点 |
| 正式独立重跑 | 用 CPU 网格加速入口重新跑四组各 20 次 | 独立生成的运动轨迹是否复现补偿收益的趋势 |

作者仓库中通用的 `analysis/FLAIR_released_plots.ipynb` 主要含实机分析。六足四组应定位到 Zenodo 的 `FLAIR_plots_simplified_Hexapod.ipynb`。Notebook 是能逐单元执行代码的文件。引用单元编号按从零计数。 [官方源码](https://github.com/adaptive-intelligent-robotics/FLAIR/tree/v1.0.0) · [六足 notebook 与原始数据](https://zenodo.org/records/14546657) · [执行记录](../../05_experiments/flair/reproduction.CN.md)

## 2. 怎样手动启动一组

服务器使用独立 Python 3.10 Conda 前缀，Python 本身运行实验代码，JAX 在 CPU 上计算，Brax 提供物理推进，QDax 读步态库，GPJax 用于模型组件。已用组合是 JAX/jaxlib 0.4.22、GPJax 0.6.0、Brax 0.10.2。无需另外打开一个 GUI。下例假定沿用归档里的专用环境及已准备的源码。 [直接依赖](../../05_experiments/flair/results/provenance/requirements-cpu.txt) · [解析后的依赖](../../05_experiments/flair/results/provenance/requirements-resolved.txt)

```bash
cd "$HOME/lyy_ws/flair_reproduction"
workspace="$PWD"
python_flair="$workspace/.conda/lyy_flair_v100_cpu_py310/bin/python"
source_root="$(cat "$workspace/runs/source_path.txt")"
cd "$source_root/fast_adaptation/example"
MPLBACKEND=Agg "$python_flair" flair_example.py \
  --circuit chicane_broken_leg --num-reps 1 \
  --results "$workspace/runs/manual-weakened-flair-01"
```

`MPLBACKEND=Agg` 使 Matplotlib 在无交互桌面的环境写图。入口从当前目录找到默认的 `map_elites_map`。每次运行使用新输出路径，目录名里的 `weakened-flair` 只是提醒人读，真正的分组由开关决定。

| 运行组 | 在上面基础上增加的选项 |
| --- | --- |
| 健康，FLAIR 关 | `--perturbation-off --adaptation-off` |
| 健康，FLAIR 开 | `--perturbation-off` |
| 减力，FLAIR 关 | `--adaptation-off` |
| 减力，FLAIR 开 | 基础命令 |

要看模拟画面，在同一个命令追加 `--save-html`。程序保存积累的物理状态，再生成 HTML 回放。轨迹 PNG 可先快速查看是否走到了预定路线。运行过程中的终端日志可查看当前目标、传感值、补偿输出和耗时。 [选项定义](../../03_code/references/FLAIR/fast_adaptation/example/flair_example.py:1472) · [图与回放导出](../../03_code/references/FLAIR/fast_adaptation/example/flair_example.py:1158)

## 3. 日志怎样对应到运行中的变量

| 输出 | 粒度 | 推荐先看 |
| --- | --- | --- |
| `*_replication_main_0.csv` | 回合 0，初始行及每个记录传感步 | `target_id`、位置 `tx,ty`、参考 `human_cmd_*`、实测 `vx,wz` |
| `*_replication_adaptation_0.csv` | 每条速度指令 | Driver 期望、FLAIR 输出、扰动层输出 |
| `*_gp_damage_introspection_0.csv` 与 `*_learnt_state_functions_0.csv` | 补偿分支的在线诊断 | 两侧参数、状态函数参数或 offset |
| `*_trajectory_0.png`、`*_vx_0.png`、`*_wz_0.png` | 一个回合的图 | 路线、参考与实测曲线 |
| `*_html_0.html` | 可选，一个回合的回放 | 姿态与动作演化 |
| 配置 CSV | 每次实验设置 | 数据收集、训练、步态库与 Driver 配置 |

主日志的 `Reps` 是重复编号，`Laps` 和 `target_id` 表示进度，`Damage_Type` 标记扰动类别。腿部减力由物理环境设置，`Scaling_Value=1.0` 仍可能出现在减力日志里。补偿表与主日志频率不同，逐行比对时应按时间和指令周期关联。 [记录字段](../../03_code/references/FLAIR/fast_adaptation/example/flair_example.py:920) · [逐回合写入](../../03_code/references/FLAIR/fast_adaptation/example/flair_example.py:1103)

**判定一次成功。** 回合最后有命中航点 31 的位置证据，距离在 0.3 m 容差内，并结合完成标记和异常日志。原代码设置结束后还会走完这轮传感循环，检查末 6 行能覆盖做出完成判定时的读数。部分异常会被捕获、打印后继续写 CSV，所以排查时同时看进程状态、异常和终点。 [结束判定](../../03_code/references/FLAIR/fast_adaptation/example/flair_example.py:141) · [异常与保存](../../03_code/references/FLAIR/fast_adaptation/example/flair_example.py:1875)

## 4. 把真实日志的头三行对回源码

以下摘自作者公开的减力、开启 FLAIR 数据。取部分字段，数字保留至六位小数。

| Timesteps | target_id | target_tx | tx | ty | human_cmd_lin_x | human_cmd_ang_z | vx | wz |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 0 | 0.0000 | 0.000000 | 0.000000 | 0.000 | 0.000 | 0.000000 | 0.000000 |
| 2 | 1 | 1.6709 | 0.002750 | 0.006780 | 0.030 | 0.000 | 0.000000 | 0.000000 |
| 3 | 1 | 1.6709 | 0.014405 | 0.017742 | 0.030 | 0.000 | 0.037490 | 0.020717 |

第 1 行在真正进入控制循环前写入。起始位置已在航点 0，第一次计算参考指令时切到航点 1。第 2、3 行的参考还保持 0.03 和 0，但传感值已经随环境推进变化。表里可以看到位置与速度字段按各自路径产生，跟踪评估会处理时延及单位。第 3 行若只按同一行计算，误差为 `sqrt((0.03749-0.03)²+0.020717²) ≈ 0.02203`，作者 notebook 用对齐后的反馈另算。源码里的样例 CSV 是列结构样例，完整试验行应读取作者数据或服务端运行结果。 [作者原始 CSV](https://zenodo.org/records/14546657/files/hexapod_main_flair.csv?download=1) · [初始化日志调用](../../03_code/references/FLAIR/fast_adaptation/example/flair_example.py:1659)

## 5. 正式复现如何得到 80 回合

正式任务分 4 个分片，每片 4 个实验组，每组运行 5 回合，即 4×4×5=80。相同分片的四组使用同一个种子入口，分片种子从 40260 到 40263。每个种子经内部 PRNG 分出不同 reset 随机量，提高覆盖。比较时可用 `shard + rep` 配对，控制初始扰动噪声等因素。原版默认种子来自当前系统时间，手动启动主要用于教学与运行核对。 [原版 PRNG](../../03_code/references/FLAIR/fast_adaptation/example/flair_example.py:520) · [正式验收表](../../05_experiments/flair/results/data/formal_trials.csv) · [配对表](../../05_experiments/flair/results/data/formal_paired.csv)

| 服务端项目脚本 | 输入 | 输出或检查 |
| --- | --- | --- |
| `review_author.py` | 作者 notebook 和四份 CSV | 用作者函数复算图、指标与总表 |
| `fast_cpu_example.py` | 原发布版入口、运行开关与输出目录 | 外层替换网格加样和筛选的 CPU 执行路径 |
| `check_fast_grid.py` | 六批有效样本数量不同的输入 | 对照格子编号、更新数组和筛选掩码 |
| `compare_cpu_paths.py` | 同种子、减力场景 | 第 110 条指令前的两版短轨迹对照 |
| `run_formal.sh` | 四个种子分片与四组试验 | 80 回合主日志与补偿诊断 |
| `summarize_formal.py` | 正式批次的逐回合日志 | 完成验收、同一行误差和配对汇总 |
| `compare_metrics.py`、`analyze_formal.sh` | 作者数据与独立批次数据 | 同口径对照表和派生统计 |

CPU 加速的着力点是稀疏网格。按照执行记录，加样只处理命中的单元，选择只在有数据的单元执行，边界情况走原实现。六批网格数值逐元素一致，同种子短轨迹的 551 行主日志和 110 行指令日志数值列最大差为 0，整圈逐值等价仍需验证。本地直接审阅的模块为 v1.0.0，服务端项目脚本行为依据已归档执行记录和结果。 [项目脚本与验证记录](../../05_experiments/flair/reproduction.CN.md) · [短轨迹比较](../../05_experiments/flair/results/provenance/summary.txt) · [发布版源码核验](../../05_experiments/flair/results/provenance/verified-source.txt)

## 6. 一行速度数据怎样变成一个实验成绩

`FLAIR_plots_simplified_Hexapod.ipynb` 的核心是第 9、10、14、55 单元。第 20、23、26、29 单元分别载入减力关、健康关、健康开、减力开。

1. `process_data` 读 CSV，保留使用的列，按回合/赛段/时间排序，计算 `TimeDelta`。删除不在 `(0,0.5)` 内的间隔并处理缺失值。
2. 完成时间按目标编号累积 `TimeDelta`，每个目标取末值，再对各目标求和。这里的秒来自实验日志时基。
3. `create_error_dataframe` 取参考指令和反馈时间。原样复算时，它把日志中的 `wz` 映射为 `-wz*pi/180`，裁剪前进和转向反馈。随后用前 100、后 300 点构造窗口，用互相关为两个分量找滞后，将索引限制在 30 到 100 点范围，匹配随后反馈。离线评估会查看之后的样本，这与在线指令配对是两套流程。
4. 每个有效时刻，以参考和对齐后的反馈算二维欧氏距离。假设目标 `(0.03,0.02)`、匹配反馈 `(0.02,0.01)`，得到 `sqrt(0.01² + 0.01²) ≈ 0.0141`。原指标按该定义合成，不单独赋给它位置或速度的物理单位。
5. 同一回合先对逐点误差取中位数，再对同组 20 个回合的中位数取组中位数。按回合统计可避免长回合因行数多而获得更大权重。

| 汇总字段 | 计算口径 | 用途 |
| --- | --- | --- |
| `median_raw_error` | 用同一行参考与 Brax 反馈算误差 | 快速检查趋势 |
| `median_aligned_native_yaw_error` | 做时间对齐，保留 Brax 原生偏航率 | 检查转向转换对结论的影响 |
| `median_notebook_error` | 依作者 notebook 原样跑，包括偏航变换 | 复现论文的主表 |
| `median_notebook_duration_s` | 作者口径的组中位完成时间 | 比较每组走完路线所需日志时间 |

六足源代码把车体角速度分量写入日志，notebook 的角速度转换值得专门核对。用相同代码精确复算是一种证据，保留 Brax 原生反馈重算是另一种口径检查。直接将原 notebook 的偏航变换移到 Go2-W 之前，应依据平台坐标、符号和单位独立验证。 [作者 notebook](https://zenodo.org/records/14546657/files/FLAIR_plots_simplified_Hexapod.ipynb?download=1) · [组统计](../../05_experiments/flair/results/data/comparison_metrics.csv)

## 7. 三个百分数的分母

| 指标 | 计算与解释 |
| --- | --- |
| 本方减力组总误差下降约 13.0% | `(0.050362 − 0.043791) / 0.050362`。分母是减力关 FLAIR 的总误差 |
| 本方减力组完成时间缩短 26.45 s | 组中位完成时间 197.05 s 减 170.60 s |
| 作者六足额外误差恢复 138.8% | `(E减力关 − E减力开) / (E减力关 − E健康关)`。用 0.050322、0.044313、0.045992 代入。减力开组低于健康关组，故可超过 100% |

本方保留原生偏航率对齐后，减力组误差从 0.052797 降到 0.046424，约 12.1%。实机的 74.4% 来自论文 GVR-Bot 多赛段汇总，属于另一平台和评测集。当前独立复现覆盖六足 Chicane 固定减力主对照。 [论文实机结果](https://doi.org/10.1038/s41467-026-70256-y) · [本方执行总结](../../05_experiments/flair/reproduction.CN.md)

## 8. 自己动手追一回合

1. 打开作者四组数据之一，按 `Sections_index` 取一回合，沿 `target_id` 看机器人如何从首航点走到最后一个航点。
2. 选一个转弯航点，取到达前后 `human_cmd_ang_z` 与 `wz`，看曲线峰值会不会错开。
3. 若使用服务端自己跑出的回合，打开同回合的补偿日志，检查实际补偿前后指令是否变化。用第 2 篇的求逆式解释方向。
4. 查 `formal_trials.csv` 中任意一个组合的 20 行，按回合编号定位同条件的另一组。
5. 从 `comparison_metrics.csv` 找出两组 notebook 误差列，自己算一遍降幅，再比较原生偏航率的结果。

掌握这五步以后，可以从一张统计图回到对应的回合、指令、反馈和源码。 [作者原始数据](https://zenodo.org/records/14546657) · [原版四组轨迹](../../05_experiments/flair/results/figures/smoke-v100-long_trajectories.png)

