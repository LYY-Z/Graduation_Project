# FLAIR 六足仿真复现：范围、执行与结果

## 1. 复现范围与验收状态

本次复现针对 Allard 等发表于 *Nature Communications* 的 FLAIR 论文，实验对象为补充材料中的六足机器人 Chicane 弯道主对照。以健康和中右腿减力两种条件，分别比较开启与关闭在线补偿。底层采用作者随仓发布的 MAP-Elites 控制器库。 [FLAIR 论文](https://doi.org/10.1038/s41467-026-70256-y) · [代码归档](https://zenodo.org/records/18336476) · [数据归档](https://zenodo.org/records/14546657)

| 验收项 | 实际状态 | 对应证据 |
| --- | --- | --- |
| 作者数据复核 | 四组各 20 回合，计算出的额外误差恢复比例为 138.773% | [作者数据统计](results/data/author_summary.csv) |
| 原版独立运行 | 四组各完成 1 回合，全部到达末航点 | [原版状态](results/data/smoke-v100-long_status.csv) · [原版逐回合数据](results/data/smoke-v100-long_trials.csv) |
| 加速版单回合 | 四组各完成 1 回合 | [加速版单回合状态](results/data/smoke-v100-fast_status.csv) |
| 正式批次 | CPU 加速版四组各 20 回合，共 80 回合，全部通过验收 | [进程日志](results/provenance/formal-v100.log) · [逐回合记录](results/data/formal_trials.csv) |
| 原版与加速版一致性 | 六批网格输入逐元素一致。同一种子下另比较 110 个控制步，主日志和指令日志的数值列一致 | [短轨迹对照](results/provenance/summary.txt) |
| 后续验证 | 原版与加速版的同种子整圈逐值核验、扩展六足故障工况、GVR-Bot 实机实验、Go2-W 迁移 | 分阶段开展，分别报告 |

**验收结论**　六足主对照复现完成。四组原版各 1 回合验证作者程序可独立运行，80 回合批次提供加速版的量化对照。两者的证据范围分别标注。

## 2. 服务器盘点与隔离

服务器账号为 **robotic_dog**，主机名 **RTXPro5000x2**。执行时通过既有 SSH 别名进入服务器，校内地址在当时的网络环境下超时。服务器为 Linux x86_64，盘点时可见 96 个逻辑 CPU、251 GiB 内存，工作目录所在分区剩余约 266 GiB。六足实验使用 JAX CPU 后端。

环境盘点定位到 Conda 程序 **/opt/miniconda3/bin/conda**。已有环境 **lyy_locoformer_go2w_py311** 用于 LocoFormer。FLAIR 单独建在以下工作空间，项目中集中存放安装缓存和实验产物。软件安装均针对 FLAIR 专用前缀，原有项目与 Conda 基础环境未改动。

~~~text
/home/robotic_dog/lyy_ws/flair_reproduction/
├── .conda/lyy_flair_v100_cpu_py310/    正式实验解释器
├── requirements-cpu.txt               项目直接依赖
├── upstream/                          官方 ZIP、解压后的源码与控制器库
├── data/author/                       原版 notebook 和四份 CSV
├── scripts/                           环境验证后的运行、诊断与统计工具
├── runs/                              源码记录、依赖锁定、配置与逐回合原始日志
└── analysis/                          派生数据、组间统计与绘图输出
~~~

盘点只需查询 Conda 列表和本目录的空间。日常运行直接调用项目内解释器即可，使用交互 shell 时也可激活绝对路径前缀。

~~~bash
ssh robotic-dog-frp
cd "$HOME/lyy_ws/flair_reproduction"
/opt/miniconda3/bin/conda env list
df -h .
python_flair="$PWD/.conda/lyy_flair_v100_cpu_py310/bin/python"
"$python_flair" -VV
"$python_flair" -m pip check
~~~

## 3. 固定版本与准备输入

1. 使用 FLAIR **v1.0.0**，提交为 **9e1fa31a8f39b912c5edb61bd65ba15289241276**。服务器端浅克隆进展缓慢，最终采用 Zenodo 官方归档。归档 MD5 为 **fc9fb0356fb81b5995360891fedc1bf0**。解压后以归档条目逐个比较，202 个文件内容一致。 [公开版本](https://github.com/adaptive-intelligent-robotics/FLAIR/tree/v1.0.0) · [归档逐文件校验](results/provenance/verified-source.txt)
2. 服务器直连 Zenodo 返回 HTTP 403。公开数据从本地下载并核对 MD5，再通过 SCP 传到工作目录。传输后在服务器再次核对所有文件。 [作者数据](https://zenodo.org/records/14546657)
3. 核对原版 **fast_adaptation/example/map_elites_map** 内的 **config.csv** 和控制器库 **repertoire_MAP-Elites_180813**。确认包含 **centroids.npy、descriptors.npy、fitnesses.npy、genotypes.npy**。启动时日志显示实际加载该库，并读取 50×50 的指令网格。
4. 将源码根目录写入 **runs/source_path.txt**，提交号写入 **runs/source_revision.txt**。作者脚本通过相对路径导入模块并读取控制器库，因此需要从 **fast_adaptation/example** 目录启动。

| 作者输入文件 | MD5 |
| --- | --- |
| FLAIR_plots_simplified_Hexapod.ipynb | f4625a2bcdb3ac84b28aaa198392530c |
| hexapod_main_no_flair_no_perturb.csv | 7e96eb7574acd7791e2f667ffdcc3e29 |
| hexapod_main_flair_no_perturb.csv | 2855ecc0a03f66624a67eead9180ea31 |
| hexapod_main_no_flair.csv | dec32648076694b89c1e72b7d2bfc6af |
| hexapod_main_flair.csv | 4d86df193d6d3825fc02e89a6ab8a2cc |

## 4. 环境搭建、故障定位与最终配置

| 阶段 | 现象 | 处理及验证 |
| --- | --- | --- |
| 首轮 Python 3.11、GPJax 0.5.0 | 依赖能安装，导入 GPJax 时触发 dataclass 默认值错误 | 新建 Python 3.10 专用前缀，保留排障记录。 |
| Python 3.10、GPJax 0.5.0 | JAX CPU 计算正常，示例导入缺少 gpjax.kernels.stationary | 对照发布包根目录与容器的依赖清单，切换到根目录指定的 GPJax 0.6.0。 |
| 最终环境 | Python 3.10、GPJax 0.6.0、JAX 和 jaxlib 0.4.22 | pip check、关键包导入、CPU JIT、示例 --help 及四组完整仿真均通过。 |

最终依赖还包括 Brax 0.10.2、QDax 0.3.0、NumPy 1.26.4、SciPy 1.12.0、Optax 0.1.7、Flax 0.7.5、Chex 0.1.85 和 MuJoCo 3.1.6。实际直接依赖与依赖解析结果分别留档。Conda 底包快照位于服务器的 **runs/conda-explicit.txt**。 [直接依赖](results/provenance/requirements-cpu.txt) · [已解析版本](results/provenance/requirements-resolved.txt)

需要重建时使用项目内的新前缀。以下命令锁定已验证的 Conda 底包与 Python 包，创建前确认机器架构与底包快照适配。替换实验解释器前，先完成导入及单回合检查。

~~~bash
cd "$HOME/lyy_ws/flair_reproduction"
test ! -e "$PWD/.conda/lyy_flair_rebuild" || exit 1
export CONDA_PKGS_DIRS="$PWD/.conda/pkgs"
export CONDA_ENVS_PATH="$PWD/.conda"
export PIP_CACHE_DIR="$PWD/.cache/pip"
export PYTHONNOUSERSITE=1 JAX_PLATFORMS=cpu MPLBACKEND=Agg
unset PYTHONHOME PYTHONPATH

rebuild="$PWD/.conda/lyy_flair_rebuild"
/opt/miniconda3/bin/conda create -y -p "$rebuild" --file runs/conda-explicit.txt
"$rebuild/bin/python" -m pip install -r runs/requirements-resolved.txt
"$rebuild/bin/python" -m pip check
"$rebuild/bin/python" -c 'import jax, brax.v1, qdax, gpjax; print(jax.devices()); print(jax.jit(lambda x: x + 1)(1).block_until_ready())'
src="$(cat runs/source_path.txt)"
(cd "$src/fast_adaptation/example" && "$rebuild/bin/python" flair_example.py --help)
~~~

## 5. 作者数据复核

1. **scripts/review_author.py** 从原 notebook 读取四组主实验相关代码单元，直接执行作者的数据处理函数，将派生结果写到 **analysis**。源 CSV 和 notebook 保留原样。主数据读取位于原 notebook 从零计数的第 20、23、26、29 个单元。
2. 按作者规则过滤并匹配目标车体指令与实际响应，在每回合中计算跟踪误差和完成时间，再取组中位数。误差综合了前进速度与偏航率两项，计算前沿用 notebook 的时延匹配与偏航率转换。完成时间取仿真日志时间统计。
3. 每组核得 20 回合。减力无补偿、减力有补偿、健康无补偿三组的误差中位数分别为 0.050322、0.044313 和 0.045992。额外误差恢复比例的分子为减力有无补偿的误差差值，分母为减力无补偿与健康无补偿的误差差值。按未舍入值算得 **138.773%**。补偿组误差低于健康无补偿组时，该比值可以超过 100%。 [作者数据统计](results/data/author_summary.csv) · [四组分布图](results/figures/author_four_groups.png)

~~~bash
cd "$HOME/lyy_ws/flair_reproduction"
python_flair="$PWD/.conda/lyy_flair_v100_cpu_py310/bin/python"
MPLBACKEND=Agg "$python_flair" scripts/review_author.py "$PWD"
~~~

## 6. 原版运行与性能排查

### 6.1 复现组与控制流程

| 组别 | 官方脚本追加开关 |
| --- | --- |
| 健康，关闭补偿 | --perturbation-off --adaptation-off |
| 健康，开启补偿 | --perturbation-off |
| 减力，关闭补偿 | --adaptation-off |
| 减力，开启补偿 | 默认 |

各组使用 **chicane_broken_leg** 路线，航点编号 0–31。减力工况在仿真初始化时启用，源码中的 **leg_3_1_2** 与 **leg_3_2_3** 执行器强度参数由 60 变为 20，**body_leg_3** 保持 60。数据库字段 **Scaling_Value** 可能仍为 1.0，验收应看 **Damage_Type** 与实际环境配置。 [六足环境源码](https://github.com/adaptive-intelligent-robotics/FLAIR/blob/v1.0.0/fast_adaptation/example/brax_environments/hexapod.py)

路径跟踪器按位置和朝向产生前进速度、偏航率目标。补偿器输出实际下发的车体指令，仿真端通过六足控制器库生成动作并取回运动反馈。开启补偿时，FLAIR 将实际指令与反馈对齐后更新内部响应模型，更新后的模型用于后续指令选择。 [六足主程序](https://github.com/adaptive-intelligent-robotics/FLAIR/blob/v1.0.0/fast_adaptation/example/flair_example.py)

### 6.2 首轮超时与原版复验

首轮限时 660 秒。关闭补偿的两组完成，开启补偿的两组退出码为 124，停止前仍在更新。保留首轮日志。延长时限后运行原版四组，各完成 1 回合，均达到最后航点，终点距离均小于 0.3 m。开启补偿的健康、减力回合墙钟用时约 36.3、40.0 分钟。墙钟耗时用于估算复现运行成本，赛道时间由仿真日志给出。 [首轮状态](results/data/smoke-v100_status.csv) · [原版重跑记录](results/data/smoke-v100-long_trials.csv)

~~~bash
cd "$HOME/lyy_ws/flair_reproduction"
batch="upstream_$(date -u +%Y%m%dT%H%M%SZ)"
env -u FLAIR_ENTRYPOINT bash scripts/run_four_groups.sh 1 "$batch"
MPLBACKEND=Agg "$PWD/.conda/lyy_flair_v100_cpu_py310/bin/python" \
  scripts/summarize_rerun.py "runs/$batch"
~~~

### 6.3 CPU 加速与一致性检查

- **定位。** 使用原程序短程采样、JAX 编译日志、cProfile 与网格微基准交叉检查。状态网格使用两个指令维度和一个状态维度，50³ 个单元，共 125,000 个。原版在 CPU 上对整网格执行加入和筛选是主要耗时。
- **实现。** **scripts/fast_cpu_example.py** 从外部入口调用发布版流程，在运行时替换网格加样和筛选。加样主要访问本批命中的单元，筛选只计算有数据的单元。异常索引或快速路径容量不足时调用原实现。官方源码内容保持原样。
- **计算验证。** **check_fast_grid.py** 使用六批不同有效样本数量的输入，检查单元编号、输入数组、反馈数组和选择标记逐元素一致。热运行的加样加筛选约为 0.33–0.36 秒，原操作约为 10–12 秒。该时间来自微基准。
- **轨迹验证。** **compare_cpu_paths.py** 固定种子 40391，比较减力条件前 110 个控制步。551 行主日志及 110 行补偿指令的数值列最大差异为 0。加速版另完成四组整条路线的单回合试跑。完整回合下两版的同种子逐值一致性留作进一步核验。 [短轨迹对照](results/provenance/summary.txt) · [加速版代表轨迹](results/figures/smoke-v100-fast_trajectories.png)

## 7. 正式批次、验收与统计

**scripts/run_formal.sh** 将批次分为 4 个分片，每片四组，每组 5 回合。分片种子为 **40260–40263**，一片内各组共享同样的种子入口。四片合计 16 个进程、80 回合。实验从 **formal-v100-s0** 到 **formal-v100-s3** 存放，脚本通过目录检查保护现有批次。启动新批次应为新批次与统计产物指定独立工作目录，或复制脚本并成套更新运行和分析所用的目录前缀。

| 验收维度 | 核查方法 |
| --- | --- |
| 进程与异常 | 核对 16 个进程退出码，逐回合定位完成标记及异常记录。异常捕获后仍可能留下 CSV。 |
| 完整轨迹 | 核对航点 31、最后一个指令周期内的反馈和 0.3 m 容差。程序在判定到达后会继续记录 5 个传感步，故检查末 6 行，覆盖做出判定时的反馈。 |
| 数据口径 | 按组确认损伤字段和有效回合数。独立运行生成的轨迹数据与作者数据分别归档。 |
| 正式验收 | 16 个进程均正常退出，80 个回合均通过末航点和数据验收。 |

统计使用两层脚本。**summarize_formal.py** 输出每回合状态、原始同一行误差、组统计和配对表。**compare_metrics.py** 对两套数据用相同的分析规则，输出同一行误差、经过对齐并保留 Brax 偏航率的误差、原样应用作者 notebook 得到的误差。**analyze_formal.sh** 执行汇总及分组指标计算。论文口径用于组间主对照，保留原生偏航率的结果用于检查趋势是否受单位处理影响。 [逐回合验收](results/data/formal_trials.csv) · [配对表](results/data/formal_paired.csv) · [指标对照](results/data/comparison_metrics.csv)

| 条件 | 作者误差 | 独立误差 | 作者完成时间（s） | 独立完成时间（s） |
| --- | ---: | ---: | ---: | ---: |
| 健康，关闭 FLAIR | 0.045992 | 0.045961 | 180.75 | 180.25 |
| 健康，开启 FLAIR | 0.043697 | 0.043713 | 151.65 | 151.60 |
| 减力，关闭 FLAIR | 0.050322 | 0.050362 | 196.95 | 197.05 |
| 减力，开启 FLAIR | 0.044313 | 0.043791 | 170.95 | 170.60 |

表中为各组中位数，误差使用作者 notebook 计算口径。独立数据在减力条件下，开启补偿后误差下降 **13.05%**，完成时间缩短 **26.45 s**。使用对齐后的原生偏航率计算，误差也从 **0.052797** 降到 **0.046424**。作者公开数据与独立批次均显示减力条件下的改善趋势。 [原始对照表](results/data/comparison_metrics.csv)

## 8. 归档与迁移交接

| 成果 | 位置 |
| --- | --- |
| 原版四组证据 | 服务器 runs/smoke-v100-long，以及[本地原版轨迹](results/figures/smoke-v100-long_trajectories.png) |
| 正式原始证据 | 服务器 runs/formal-v100-s0 到 runs/formal-v100-s3，各组有配置 CSV、控制台、逐回合主日志和补偿日志 |
| 正式统计 | [作者与独立批次对照](results/data/comparison_metrics.csv)、[正式批次图](results/figures/formal_four_groups.png) |
| 环境追溯 | 服务器 runs/conda-explicit.txt 和[已解析 Python 包](results/provenance/requirements-resolved.txt) |
| 汇报材料 | [汇报 PPT](../../06_reports/flair/report.CN.pptx) · [逐页讲稿](../../06_reports/flair/speech.CN.md) |

### 指标与后续研究的边界

本批次减力组总跟踪误差降幅约 13.0%；作者数据复算的 138.773% 则以健康/减力条件之间的额外误差为分母。两者不是同一指标，具体计算见[指标教材](../../02_learning/flair/03_reproduction_and_metrics.md)。论文的 GVR-Bot 实机比较也不能由六足结果代替。

六足 Chicane 主对照是已经完成的复现范围；Go2-W 迁移、其他六足故障和整篇论文全部实验不在本次完成结论之内。此前迁移设想保存在归档中，当前选题与研究方向以 [STATUS](../../STATUS.CN.md) 为准。

旧执行文档与旧总结已合并到本记录；完整原稿保留在 [history.zip](../../99_archive/history.zip) 的 `organization_20261123/02_learning/flair/`。
