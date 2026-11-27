# 服务器操作入门（零基础版）

这份文档教你从零开始使用实验室的训练服务器：登录、看文件、看显卡、看训练进度、启动和停止训练、评估模型、把结果拷回自己电脑。每一步都给出可以直接复制的命令和"看到什么算正常"。

> **安全约定**
> - 服务器地址、端口和密码**不写进任何文件**，需要时找老师或负责人要，或者看你自己的私人笔记。下文用 `<地址>`、`<端口>`、`<用户名>` 代替。
> - 这台服务器**多人共用**。只在自己的目录里操作，**只停止自己启动的程序**，不要改动别人的文件和环境。
> - 不确定的命令先别运行，问清楚再说。

---

## 目录

1. 先弄清几个概念
2. 第一次登录
3. Linux 命令行基础
4. 我们在服务器上的目录
5. 查看显卡和程序
6. 查看训练进度
7. 启动一次训练
8. 停止训练
9. 评估模型
10. 看训练曲线（TensorBoard）
11. 在服务器和自己电脑之间拷文件
12. 用 tmux 防止断线
13. 常见问题
14. 命令速查表

---

## 1. 先弄清几个概念

| 概念 | 大白话 |
|---|---|
| 服务器 | 一台放在机房的高性能电脑，装了 2 张 RTX PRO 5000 显卡（每张 48 GB 显存）、96 线程 CPU、251 GB 内存。没有屏幕，只能远程用 |
| SSH | 远程登录的方式。登录后你看到的是一个**黑色命令行窗口**，输入的命令在服务器上执行 |
| 终端 / 命令行 | 输入命令、看结果的窗口。Windows 上叫 PowerShell 或命令提示符 |
| Linux | 服务器用的操作系统。命令和 Windows 不一样，下面第 3 节会教 |
| 路径 | 文件的位置。Linux 用 `/` 分隔，例如 `/data3/robotic_dog/lyy_ws`。没有 C 盘、D 盘的说法 |
| 进程 | 正在运行的程序。每个进程有一个编号，叫 PID |
| GPU / 显卡 | 训练用的计算硬件。编号 0 和 1 |
| conda 环境 | 一套独立安装的 Python 和软件包。我们有自己的一套，和别人的互不影响 |

---

## 2. 第一次登录

### 2.1 在 Windows 上打开终端

按 `Win` 键，输入 `PowerShell`，回车。Windows 10/11 自带 SSH，不用另外安装。

### 2.2 登录命令

```powershell
ssh -p <端口> <用户名>@<地址>
```

- `-p <端口>`：服务器通过转发访问，端口不是默认的 22，必须写；
- 第一次连接会问 `Are you sure you want to continue connecting (yes/no)?`，输入 `yes` 回车；
- 然后提示输入密码。**输入密码时屏幕上什么都不显示**，这是正常的，输完直接回车。

### 2.3 登录成功的样子

```
<用户名>@RTXPro5000x2:~$
```

- `RTXPro5000x2` 是服务器的名字；
- `~` 表示你现在在自己的家目录；
- `$` 后面就可以输入命令了。

### 2.4 退出

输入 `exit` 回车，或者直接关掉窗口。**关窗口不会影响已经在后台跑的训练**（原因见第 7 节）。

### 2.5 连接经常断怎么办

这台服务器经过转发访问，空闲一会儿就可能断开。登录时加一个保活参数会好很多：

```powershell
ssh -o ServerAliveInterval=30 -p <端口> <用户名>@<地址>
```

意思是每 30 秒发一次"我还在"的信号。断了也没关系，重新登录即可，后台训练不受影响。

### 2.6 （可选）更方便的工具

| 工具 | 好处 |
|---|---|
| VS Code + Remote-SSH 插件 | 可以像在本地一样浏览、打开服务器上的文件，左边是文件树，下面是终端。**推荐** |
| MobaXterm | 带图形界面的 SSH 工具，可以拖拽上传下载文件 |

---

## 3. Linux 命令行基础

只需要会下面这些。每个命令输完按回车执行。

### 3.1 我在哪、这里有什么

| 命令 | 作用 | 例子 |
|---|---|---|
| `pwd` | 显示当前所在目录 | `pwd` → `/home/<用户名>` |
| `ls` | 列出当前目录的文件 | `ls` |
| `ls -lh` | 列出详细信息（大小、时间） | `ls -lh` |
| `cd 目录` | 进入某个目录 | `cd /data3/robotic_dog/lyy_ws/gram_repro` |
| `cd ..` | 回到上一级 | |
| `cd ~` | 回到家目录 | |

**小技巧**：
- 输路径时按 `Tab` 键会**自动补全**，输几个字母再按 Tab，能省很多事，也能避免拼错；
- 按 `↑` 键可以调出上一条命令；
- 按 `Ctrl+C` 可以**中断当前正在屏幕上运行的命令**（例如停止查看日志）。

### 3.2 看文件内容

| 命令 | 作用 |
|---|---|
| `cat 文件` | 把整个文件打印出来（适合短文件） |
| `less 文件` | 分页查看长文件。空格翻页，`/关键词` 搜索，`q` 退出 |
| `head -n 20 文件` | 看前 20 行 |
| `tail -n 20 文件` | 看最后 20 行 |
| `tail -f 文件` | **实时跟踪**文件末尾，有新内容就显示（看训练日志常用）。`Ctrl+C` 退出，**不会停止训练** |
| `grep 关键词 文件` | 找出包含关键词的行 |

### 3.3 文件操作（小心使用）

| 命令 | 作用 | 注意 |
|---|---|---|
| `mkdir 目录名` | 新建目录 | |
| `cp 源 目标` | 复制 | 复制目录要加 `-r` |
| `mv 源 目标` | 移动或改名 | |
| `rm 文件` | 删除文件 | **Linux 没有回收站，删了就找不回来** |

> **不要在别人的目录里用 `rm`。不要用 `rm -rf` 加通配符（`*`）。** 删除前先用 `ls` 确认要删的是什么。

### 3.4 看磁盘空间

| 命令 | 作用 |
|---|---|
| `df -h /data3` | 数据盘还剩多少空间 |
| `du -sh 目录` | 某个目录占了多大 |

### 3.5 一行里的特殊符号

| 符号 | 意思 | 例子 |
|---|---|---|
| `\|` | 把前一个命令的输出交给后一个命令 | `grep reward log.txt \| tail -3`：找出含 reward 的行，只看最后 3 行 |
| `>` | 把输出写进文件（覆盖） | `ls > list.txt` |
| `&` | 放到后台运行 | |
| `\` | 命令太长时换行接着写 | |

---

## 4. 我们在服务器上的目录

所有东西都在个人工作区 `/data3/robotic_dog/lyy_ws/` 下：

```
/data3/robotic_dog/lyy_ws/
├── gram_compatibility/          兼容性试运行（存档，不再改动）
│   ├── envs/lyy_gram_smoke_py311/   ★ 我们独立的 Python 环境（复现也用它）
│   ├── cache/                       缓存
│   └── work/IsaacLab/               安装好的 Isaac Lab 2.3.2
└── gram_repro/                  ★ GRAM 正式复现（日常主要在这里）
    ├── code/gram/                   GRAM 代码（git 管理）
    ├── scripts/
    │   ├── run_gram.sh              启动训练的脚本
    │   ├── run_eval.sh              评估模型的脚本
    │   └── parity_patch.py          把配置改回论文版本的补丁（已应用）
    ├── runs/                        ★ 所有训练结果
    │   ├── _console/                    每次训练/评估的控制台日志（看进度看这里）
    │   └── unitree_go2_custom/          每次训练一个文件夹：模型、配置、曲线
    ├── cache/  tmp/                 缓存和临时文件
    └── results/  notes/             整理后的结果和笔记
```

最常用的三个位置：

| 想做什么 | 去哪里 |
|---|---|
| 看训练进度 | `gram_repro/runs/_console/<训练名>.log` |
| 找训练好的模型 | `gram_repro/runs/unitree_go2_custom/<日期_训练名>/model_*.pt` |
| 启动训练或评估 | `gram_repro/scripts/` |

**不要动的地方**：其他用户的目录（比如 `/home/` 下别人的文件夹）、系统目录、`gram_compatibility` 里的环境（删了要重装好几个小时）。

---

## 5. 查看显卡和程序

### 5.1 显卡状态：`nvidia-smi`

```bash
nvidia-smi
```

会看到一张表，关键看三列：

| 列 | 含义 |
|---|---|
| `Memory-Usage` | 显存用了多少 / 总共多少，例如 `40424MiB / 48935MiB` |
| `GPU-Util` | 显卡忙碌程度，0–100% |
| 下方 `Processes` | 哪些进程在用这张卡，各占多少显存 |

简洁版（只看数字）：

```bash
nvidia-smi --query-gpu=index,memory.used,memory.total,utilization.gpu --format=csv
```

**判断能不能再开一个训练**：GRAM 一个训练约占 **8.5 GB** 显存。某张卡剩余显存（总量减已用）大于约 10 GB，才考虑在这张卡上再开。

**注意**：服务器上有另一位同学的程序常驻在两张卡上，每张卡约占 25 GB，这是正常的，**不要动它**。

### 5.2 看进程

| 命令 | 作用 |
|---|---|
| `pgrep -af source.train` | 列出所有正在训练的 GRAM 程序（显示进程号和完整命令） |
| `pgrep -af source.eval` | 列出正在评估的程序 |
| `ps -u $USER -o pid,etime,cmd \| grep source` | 只看自己的，`etime` 是已经运行了多久 |
| `htop` | 图形化的进程和 CPU 查看器，`q` 退出 |

---

## 6. 查看训练进度

### 6.1 最简单的方法：看日志最后几行

```bash
cd /data3/robotic_dog/lyy_ws/gram_repro/runs/_console
ls
```

会看到每个训练一个日志，例如 `gram_default_s1.log`。查看最新进度：

```bash
grep -E "Learning iteration|Mean reward|Iteration time" gram_default_s1.log | tail -3
```

正常输出：

```
                       Learning iteration 448/15000
                       Mean reward: 6.99
                    Iteration time: 3.20s
```

| 项目 | 含义 | 怎么判断正常 |
|---|---|---|
| `Learning iteration 448/15000` | 第几次 / 一共几次 | 数字在增加 |
| `Mean reward` | 平均奖励 | 前期整体上升，后期趋于平稳；偶尔下降正常 |
| `Iteration time` | 这一次用了几秒 | GRAM 约 2–3.5 秒，与别人共用显卡时会波动 |

估算剩余时间：`(总次数 − 当前次数) × 每次秒数 ÷ 3600` 小时。例如 `(15000 − 448) × 3.2 ÷ 3600 ≈ 13` 小时。

### 6.2 一次看完所有训练

```bash
cd /data3/robotic_dog/lyy_ws/gram_repro/runs/_console
for f in *.log; do echo "$f  $(grep -oE 'Learning iteration [0-9]+/[0-9]+' $f | tail -1)  报错数:$(grep -c Traceback $f)"; done
```

`报错数` 应该是 0。

### 6.3 实时盯着看

```bash
tail -f gram_default_s1.log
```

屏幕会持续滚动显示新输出。看够了按 `Ctrl+C` 退出。**这只是停止查看，训练继续运行。**

### 6.4 怎么判断训练结束了

1. `pgrep -af "run_name gram_default_s1"` 没有输出，说明程序已经结束；
2. 日志最后几行出现 `Collecting validation data`，并且没有 `Traceback`（报错）；
3. 训练文件夹里出现最后一个模型 `model_14999.pt`（或类似编号）：

```bash
ls /data3/robotic_dog/lyy_ws/gram_repro/runs/unitree_go2_custom/*gram_default_s1/
```

### 6.5 日志里出现报错怎么办

```bash
grep -n -A 20 Traceback gram_default_s1.log | head -40
```

把输出复制下来，再来问。不要自己尝试修改代码。

---

## 7. 启动一次训练

### 7.1 启动前检查（每次都做）

1. **显存够不够**：`nvidia-smi`，目标显卡剩余显存大于 10 GB；
2. **同一个名字是否已经在跑**：`pgrep -af "run_name 你要起的名字"` 应该没有输出；
3. **硬盘空间**：`df -h /data3`，剩余空间应远大于 10 GB。

### 7.2 启动命令

```bash
/data3/robotic_dog/lyy_ws/gram_repro/scripts/run_gram.sh <显卡号> <训练名> <超时小时> <训练参数...>
```

例子：在 0 号卡上训练 GRAM，种子 2：

```bash
/data3/robotic_dog/lyy_ws/gram_repro/scripts/run_gram.sh 0 gram_default_s2 30 \
    --alg_name gram --id_context default --num_envs 4096 --seed 2
```

各部分含义：

| 部分 | 含义 |
|---|---|
| `0` | 用 0 号显卡 |
| `gram_default_s2` | 训练名。**建议格式：方法_训练范围_s种子**，不要和已有的重名 |
| `30` | 最多运行 30 小时，超时自动停止，防止卡死后一直占着显卡 |
| `--alg_name` | 训练哪种方法，见下表 |
| `--id_context` | `default`（论文默认范围）或 `wide`（负载加宽到 9 kg，对应论文图 5） |
| `--num_envs 4096` | 同时模拟 4096 只机器狗（论文设置） |
| `--seed 2` | 随机种子。同一方法换不同种子 = 重复实验 |

`--alg_name` 可选的值：

| 值 | 方法 | 迭代次数 | 预计时长 |
|---|---|---|---|
| `gram` | GRAM（论文方法） | 10000 + 5000 微调 | 约 10–13 小时 |
| `robust_rl` | 鲁棒 RL | 10000 | 约 5–7 小时 |
| `contextual_rl` | 情境 RL（教师—学生） | 10000 + 5000 微调 | 约 10–13 小时 |
| `domain_rand` | 域随机化 | 10000 | 约 5–7 小时 |
| `gram_separate` | 消融：分开采集数据 | 10000 + 5000 | 约 10–13 小时 |
| `gram_modular` | 消融：两个独立网络硬切换 | 10000 + 5000 | 约 10–13 小时 |

启动成功会显示：

```
launched pid=1028050 tag=gram_default_s2 log=/data3/robotic_dog/lyy_ws/gram_repro/runs/_console/gram_default_s2.log
```

一两分钟后按第 6 节查看日志，确认开始打印 `Learning iteration`。

### 7.3 这个脚本帮你做了什么

你不需要记，但了解一下：
1. 使用我们独立的 Python 环境，不碰服务器上其他环境；
2. 把缓存、临时文件都放在我们自己的目录里；
3. 指定显卡；
4. 用 `setsid nohup` 让训练**在后台运行，断线、关窗口都不会停**；
5. 用 `timeout` 设置最长运行时间；
6. 把所有输出写进 `runs/_console/<训练名>.log`。

### 7.4 一次能同时跑几个

每个训练约占 8.5 GB 显存，还要和另一位同学共用。建议：
- **每张卡最多同时跑 2 个**；
- 同一张卡跑 2 个时，每个都会变慢约 30–50%；
- 跑之前看一眼 `nvidia-smi`，别把显存占满，否则可能影响别人的程序。

---

## 8. 停止训练

### 8.1 找到进程号

```bash
pgrep -af "run_name gram_default_s2"
```

输出类似：

```
1028052 /data3/.../python -u -m source.train --run_name gram_default_s2 ...
```

第一个数字 `1028052` 就是进程号。可能还会有一行 `timeout ...`，那是外面的计时器。

### 8.2 停止

```bash
pkill -INT -f "run_name gram_default_s2"
```

- `-INT` 相当于按 `Ctrl+C`，让程序正常收尾；
- `-f "run_name gram_default_s2"` 只匹配这一个训练，**不会误停别人的程序**。

等十几秒再检查：`pgrep -af "run_name gram_default_s2"` 没有输出，就是停了。如果还在，再用：

```bash
pkill -TERM -f "run_name gram_default_s2"
```

> **绝对不要** `kill` 你不认识的进程号，也不要用 `pkill python` 这种会匹配所有人程序的命令。

---

## 9. 评估模型

训练结束后，要在论文的测试场景下评估，才能和论文表 III 对比。

### 9.1 找到训练文件夹名

```bash
ls /data3/robotic_dog/lyy_ws/gram_repro/runs/unitree_go2_custom/
```

输出类似：

```
2026-11-26_22-44-37_gram_default_s1
2026-11-26_22-44-37_robust_rl_default_s1
```

### 9.2 评估命令

```bash
/data3/robotic_dog/lyy_ws/gram_repro/scripts/run_eval.sh <显卡号> <评估名> <训练文件夹名> <评估参数...>
```

评估在**前台**运行，几分钟就结束，结果直接打印在屏幕上，同时保存到 `runs/_console/eval_<评估名>.log`。

### 9.3 论文的测试场景对应的参数

以评估 GRAM 种子 1 为例（训练文件夹名换成你自己的）：

| 场景 | 类别 | 加在命令后面的参数 |
|---|---|---|
| 正常（训练范围内） | ID | （不加参数） |
| 加 6 kg | 近 OOD | `--base_mass_min 6 --base_mass_max 6` |
| 加 9 kg | 远 OOD | `--base_mass_min 9 --base_mass_max 9` |
| 5° 坡 | 近 OOD | `--terrain_slope_degrees 5` |
| 10° 坡 | 远 OOD | `--terrain_slope_degrees 10` |
| 5 cm 粗糙地面 | 近 OOD | `--terrain_roughness_cm 5` |
| 10 cm 粗糙地面 | 远 OOD | `--terrain_roughness_cm 10` |
| 随机关节冻结 | 远 OOD | `--frozen_joint_type all` |

完整例子（加 9 kg）：

```bash
/data3/robotic_dog/lyy_ws/gram_repro/scripts/run_eval.sh 0 gram_s1_mass9 \
    2026-11-26_22-44-37_gram_default_s1 \
    --alg_name gram --id_context default --base_mass_min 9 --base_mass_max 9
```

注意：
- `--alg_name` 要和训练时一致（训练的是 robust_rl，评估也写 robust_rl）；
- "后髋关节冻结"的具体参数还需要从代码里确认，确认后补进这里。

### 9.4 评估结果怎么看

屏幕最后会打印一段统计。GRAM 还会额外打印 α（可信度）和不确定性的分布：

```
Alpha:            ← α 的分布：越接近 1 越"有把握"，越接近 0 越在"退回保守"
Mean:   0.9xx
...
Uncertainty Metric:
Mean:   ...
```

回报（跟踪速度的得分）是和论文表 III 对比的主要指标。具体换算方式会写进复现记录 `05_experiments/gram_reproduction.CN.md`。

---

## 10. 看训练曲线（TensorBoard）

TensorBoard 能把奖励、损失随训练变化的曲线画出来。服务器没有屏幕，需要用"端口转发"在自己电脑的浏览器里看。

### 10.1 在服务器上启动 TensorBoard

```bash
cd /data3/robotic_dog/lyy_ws/gram_repro
/data3/robotic_dog/lyy_ws/gram_compatibility/envs/lyy_gram_smoke_py311/bin/tensorboard \
    --logdir runs/unitree_go2_custom --port 6106 --bind_all
```

看到 `TensorBoard ... at http://...:6106/` 就是启动了。**这个窗口不要关。**

### 10.2 在自己电脑上新开一个 PowerShell，建立转发

```powershell
ssh -N -L 6106:localhost:6106 -p <端口> <用户名>@<地址>
```

输入密码后，窗口看起来"卡住"不动，这是正常的，表示转发已建立。

### 10.3 打开浏览器

访问 `http://localhost:6106`，就能看到曲线。左侧可以勾选不同的训练进行对比。

### 10.4 看完后

- 两个窗口都按 `Ctrl+C` 关闭；
- 端口 `6106` 是随便选的，如果提示被占用，换一个数字（例如 6107），两边要一致。

---

## 11. 在服务器和自己电脑之间拷文件

在**自己电脑**的 PowerShell 里运行（不要先登录服务器）。

### 11.1 从服务器下载到本地

```powershell
scp -P <端口> <用户名>@<地址>:/data3/robotic_dog/lyy_ws/gram_repro/runs/_console/gram_default_s1.log D:\LYY\
```

下载整个文件夹加 `-r`：

```powershell
scp -r -P <端口> <用户名>@<地址>:/data3/robotic_dog/lyy_ws/gram_repro/results D:\LYY\
```

注意 `scp` 的端口参数是**大写** `-P`，`ssh` 是小写 `-p`。

### 11.2 从本地上传到服务器

```powershell
scp -P <端口> D:\LYY\某文件.txt <用户名>@<地址>:/data3/robotic_dog/lyy_ws/gram_repro/notes/
```

> 模型文件（`.pt`）每个约 7 MB，可以下载；但**不要把模型、日志提交到 GitHub 仓库**。

---

## 12. 用 tmux 防止断线

如果你要在前台做一件比较久的事（比如连续评估很多场景），断线会中断它。`tmux` 可以开一个"不会因断线而关闭的窗口"。

| 操作 | 命令 |
|---|---|
| 新建一个叫 `eval` 的窗口 | `tmux new -s eval` |
| 暂时离开（窗口里的程序继续跑） | 先按 `Ctrl+B`，松开，再按 `D` |
| 回到窗口 | `tmux attach -t eval` |
| 看有哪些窗口 | `tmux ls` |
| 关闭窗口 | 在窗口里输入 `exit` |

断线后重新登录，用 `tmux attach -t eval` 就能回到原来的地方，程序还在跑。

> 训练用 `run_gram.sh` 启动就够了，它本身就是后台运行，不需要 tmux。

---

## 13. 常见问题

| 问题 | 原因与处理 |
|---|---|
| 输密码时屏幕没反应 | 正常，Linux 输密码不显示，输完回车 |
| `Connection closed by ... port` | 转发连接断了，重新登录即可，后台训练不受影响 |
| `Permission denied (publickey,password)` | 密码输错，重试 |
| `No such file or directory` | 路径写错。用 `Tab` 自动补全，或先 `ls` 看看 |
| `command not found` | 命令拼错，或者这个命令要用我们环境里的完整路径（如 tensorboard） |
| 训练日志里有 `Traceback` | 程序报错了。按 6.5 节把报错复制下来再问 |
| 训练日志里有 `CUDA out of memory` | 显存不够。先看 `nvidia-smi`，换一张空闲的卡，或者等别的训练结束 |
| 训练特别慢（每次 > 5 秒） | 显卡上同时跑的程序太多，看 `nvidia-smi` 的 GPU-Util |
| `tail -f` 后屏幕一直滚动退不出来 | 按 `Ctrl+C`，只是退出查看，训练不会停 |
| 不小心关了窗口 | 后台训练不受影响；前台运行的评估会中断，重新运行即可 |

---

## 14. 命令速查表

```bash
# ---- 登录（在自己电脑的 PowerShell 里）----
ssh -o ServerAliveInterval=30 -p <端口> <用户名>@<地址>

# ---- 进入复现目录 ----
cd /data3/robotic_dog/lyy_ws/gram_repro

# ---- 看显卡 ----
nvidia-smi --query-gpu=index,memory.used,memory.total,utilization.gpu --format=csv

# ---- 看有哪些训练在跑 ----
pgrep -af source.train

# ---- 看所有训练的进度 ----
cd /data3/robotic_dog/lyy_ws/gram_repro/runs/_console
for f in *.log; do echo "$f  $(grep -oE 'Learning iteration [0-9]+/[0-9]+' $f | tail -1)  报错数:$(grep -c Traceback $f)"; done

# ---- 看某个训练最新的奖励和速度 ----
grep -E "Learning iteration|Mean reward|Iteration time" gram_default_s1.log | tail -3

# ---- 实时跟踪日志（Ctrl+C 退出，不影响训练）----
tail -f gram_default_s1.log

# ---- 启动训练（例：0 号卡，GRAM，种子 2）----
/data3/robotic_dog/lyy_ws/gram_repro/scripts/run_gram.sh 0 gram_default_s2 30 \
    --alg_name gram --id_context default --num_envs 4096 --seed 2

# ---- 停止某个训练（只停这一个）----
pkill -INT -f "run_name gram_default_s2"

# ---- 评估（例：加 9 kg）----
/data3/robotic_dog/lyy_ws/gram_repro/scripts/run_eval.sh 0 gram_s1_mass9 \
    <训练文件夹名> --alg_name gram --id_context default --base_mass_min 9 --base_mass_max 9

# ---- 看硬盘空间 ----
df -h /data3
du -sh /data3/robotic_dog/lyy_ws/gram_repro
```

---

## 相关文档

- GRAM 复现记录（训练任务表、参数核对、结果）：[05_experiments/gram_reproduction.CN.md](../../05_experiments/gram_reproduction.CN.md)
- 服务器环境核查与复现计划：[02_learning/gram/07_server_and_reproduction.CN.md](../gram/07_server_and_reproduction.CN.md)
- 远程桌面（VNC）：[vnc.md](vnc.md)
