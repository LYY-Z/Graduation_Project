# 第 10 节：评估入口与配置变体

## 本节要回答的问题

训练命令和评估命令有什么差别？为什么仓库里有很多 YAML？选错配置会发生什么？本节从 eval.py 入口解释实验如何加载一个检查点并在任务上运行。

## 1. 训练与评估入口

训练入口 train.py 通常由 Hydra 读取一份训练配置，创建对应 Workspace 并调用 run()。评估入口 eval.py 则接收 checkpoint 路径、结果目录和设备等参数，读取 checkpoint 保存的配置及模型状态，再由配置建立环境 runner。

简化为：

~~~text
训练：配置 + 演示数据 → Workspace → 学得策略 → checkpoint
评估：checkpoint → 恢复配置/策略 → EnvRunner → 指标/视频
~~~

评估不是“把训练重新跑一次”。它加载已有权重，只在环境中推理和记录结果。

## 2. 为什么配置拆成很多 YAML

配置文件把实验中常变化的选择写成数据，而不是散落在代码里。常见层次包括：

| 配置层 | 决定什么 | 例子 |
|---|---|---|
| 方法/训练配置 | 用哪种 Workspace、策略、优化器、训练轮数 | image diffusion、低维 diffusion |
| 任务配置 | 观测有哪些键、动作形状、数据文件、环境 runner | Push-T、Lift |
| 模型配置 | 网络结构、视觉骨干、scheduler、扩散步数 | ResNet、U-Net、DDPM |
| 实验覆盖项 | 改随机种子、数据路径、设备、日志名称等 | 命令行覆盖字段 |

Hydra 的 defaults 能把这些配置组合起来。阅读时从实际运行的顶层 YAML 进入，沿 defaults 找任务配置和模型配置，不要假设同名任务一定使用同一策略。

## 3. 仓库里相似名字的配置可能不是同一种实验

仓库里存在 image、low-dimensional、hybrid、Transformer 等配置族。名称相似不代表输入完全相同。

- image policy：主要以图像作为观测条件。
- lowdim policy：使用位置、速度等数值状态，不处理图像。
- hybrid policy：同时编码图像和低维机器人状态。
- U-Net / Transformer：是不同的动作序列去噪网络结构。
- DDPM / DDIM sampler：是推理采样规则的不同选择；它不是输入表示或任务本身。
- Diffusion Policy / BET / IBC / Robomimic：是不同策略方法或基线，不要把它们当作同一个模型的开关细节。

一个容易产生误读的例子：某个内置 train_diffusion_unet_image_workspace.yaml 的任务配置、策略类型，与仓库根目录另一份 Push-T hybrid 配置可能并不相同。应逐项看 defaults、_target_、shape_meta 和 task，而不是仅凭文件名判断。

## 4. 读取配置的检查顺序

拿到一份 YAML，可按以下顺序读：

1. defaults：它继承/拼接了哪些配置？
2. 顶层 _target_：实例化哪个 Workspace？
3. task：任务名称、数据路径、观测键和动作维度是什么？
4. policy：实例化哪个策略，观察和动作 horizon 是多少？
5. shape_meta：每个输入/输出字段的 shape 和类型是什么？
6. optimizer、training：学习率、epoch、batch size、EMA、设备等是什么？
7. checkpoint、logging：何时保存、记录到哪里？

_target_ 是 Hydra 的对象路径；例如 some.package.ClassName 表示“导入这个 Python 类并创建它”。参数一般与该类的构造函数匹配。

## 5. 检查点中的配置为何重要

训练配置不只是启动命令的文本。策略权重只有和正确的网络结构、观测规范、normalizer、任务配置配在一起，才能正确解释。

所以评估程序会使用检查点中的配置建立匹配模型，并按代码逻辑选择在线模型或 EMA 模型。仅把一份权重文件放到不同任务配置下，可能出现字段不匹配、张量尺寸不匹配，或“能运行但结果无意义”。

## 6. 命令行覆盖配置的含义

Hydra 常允许命令行覆盖 YAML 字段。概念上：

~~~text
基础 YAML + 命令行改动项 → 本次真正生效的配置
~~~

例如只换输出目录，不一定需要复制整份 YAML；但若改任务、shape 或策略类型，就要确认这些设置彼此兼容。修改 horizon、数据路径、相机键等字段，也可能要求 Dataset、shape metadata 和策略配置一起匹配。

本节只解释配置阅读，不要求运行实验。仓库当前版本的命令行参数以 train.py --help、eval.py --help 和 README 为准。

## 本节自测

1. 训练入口与评估入口分别负责什么？
2. _target_ 指向什么？
3. 为什么不能只看 YAML 文件名就判断观测模态？
4. 换了 horizon 可能还需要检查哪些部分？
5. 评估时为什么应使用和 checkpoint 匹配的配置？

下一节：[真实机器人代码路径](11_real_robot_code_path.md)。
