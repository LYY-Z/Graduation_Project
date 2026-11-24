# 第 1 节：仓库地图与读代码所需的 Python 基础

## 本节要回答的问题

1. 这个项目从哪些文件开始运行？
2. 哪些目录实现了数据、策略、模型和环境？
3. 读代码时，class、object、self、method、dict 各是什么意思？

## 1. 仓库不是一个大脚本

官方仓库把机器人任务、策略算法和训练工程拆成许多模块。根目录最重要的入口大致如下：

| 文件 | 用途 |
|---|---|
| train.py | 训练入口：读取配置，创建 Workspace 并启动它 |
| eval.py | 加载训练检查点，在配置指定的环境中评估策略 |
| demo_pusht.py | 在 Push-T 模拟环境中运行演示 |
| demo_real_robot.py | 使用实体设备采集演示数据 |
| eval_real_robot.py | 将训练得到的策略接入真实机器人评估流程 |
| ray_train_multirun.py | 管理多组种子并行训练 |

主要实现位于 diffusion_policy/：

| 目录 | 责任 |
|---|---|
| config/ | 训练 Workspace 配置和任务配置 |
| dataset/ | 将存储中的演示转成训练样本 |
| policy/ | 策略的训练损失和动作预测接口 |
| model/ | 视觉编码器、扩散 U-Net、Transformer 等网络 |
| workspace/ | 组织模型、数据、优化、评估和检查点 |
| env_runner/ | 在环境中执行策略并收集分数和视频 |
| env/ | Push-T、Robomimic、Kitchen 等环境封装 |
| common/ | 回放缓冲、时间序列采样、归一化、日志等通用工具 |
| gym_util/ | 多步封装、异步环境和视频记录工具 |
| real_world/ | 相机、RealEnv、时间戳、真实控制器 |
| shared_memory/ | 多进程共享数组、队列和环形缓冲区 |
| scripts/ | 数据转换、指标计算等辅助脚本 |

## 2. 项目把“任务”和“方法”拆开

可以把一次实验想成两类东西被配置接在一起：

~~~text
任务：数据集 + 环境 + 评估运行器
方法：策略 + 神经网络 + 训练工作区
~~~

任务侧回答“做什么任务、示范数据在哪里、怎样评测”；方法侧回答“怎样从观察预测动作、怎样训练模型”。这样同一个任务可比较多种方法，同一种方法也能用于不同任务。配置文件承担选择和连接的工作。

## 3. Python 函数：一个有名字的工作步骤

用 def 定义函数。输入写在括号里，return 表示把结果交回调用它的地方：

~~~python
def add_one(number):
    result = number + 1
    return result
~~~

在项目里，函数名常直接暗示职责，例如 run、predict_action、compute_loss、get_normalizer。读函数时先问：它接收什么？返回什么？它改变了哪些对象？

## 4. 类、对象、属性和方法

见 diffusion_policy/workspace/base_workspace.py：

~~~python
class BaseWorkspace:
    def __init__(self, cfg, output_dir=None):
        self.cfg = cfg
        self._output_dir = output_dir

    def run(self):
        pass
~~~

- class BaseWorkspace：定义一种对象的设计。
- __init__：对象创建时运行的初始化函数。
- cfg：创建对象时传入的配置。
- self.cfg：把 cfg 保存到当前对象上，以后其他方法可访问。
- run：属于这个类的一项工作，叫方法。
- pass：此处暂时不做事；基类给出通用接口，具体工作由子类实现。

类是设计，对象是按这份设计创建出来、正在被使用的实例。train.py 的 workspace = cls(cfg) 就创建一个对象；workspace.run() 调用该对象的方法。

## 5. self 与继承

见 diffusion_policy/workspace/train_diffusion_unet_image_workspace.py：

~~~python
class TrainDiffusionUnetImageWorkspace(BaseWorkspace):
    def __init__(self, cfg, output_dir=None):
        super().__init__(cfg, output_dir=output_dir)
        self.model = ...
~~~

类名后面的括号表示继承：TrainDiffusionUnetImageWorkspace 拥有 BaseWorkspace 提供的通用能力，也可以增加自己的能力。super().__init__(...) 调用父类初始化，让父类保存通用字段。self 始终表示“当前这个 Workspace 对象”。

子类也可以重新实现父类方法。例如基类的 run 只有 pass，训练子类实现了 run 后，调用具体 Workspace 对象的 run，就运行子类版本。

## 6. 字典和 Tensor

Python 字典用键值对给数据命名：

~~~python
batch = {
    "obs": observation,
    "action": action
}
observation = batch["obs"]
~~~

视觉任务的 obs 也可为字典，例如 image 和 agent_pos 各占一个字段。Tensor 是 PyTorch 中的多维数字数组；图片、动作、状态以及网络输出都会以 Tensor 传递。

项目中的接口常写成：

~~~python
def predict_action(self, obs_dict: Dict[str, torch.Tensor]) -> Dict[str, torch.Tensor]:
    ...
~~~

冒号后的类型提示是给读代码的人和开发工具看的：输入/输出预期是字符串键、Tensor 值的字典。它不会自动把不正确的数据修成 Tensor。

## 7. 常见 Python 语法标记

| 写法 | 初学者读法 |
|---|---|
| self.model | 当前对象的 model 属性 |
| cfg.training.seed | 从配置对象逐层读取 training 下的 seed |
| return result | 把 result 返回给调用方 |
| raise NotImplementedError() | 明确告诉调用方：基类方法需由子类实现 |
| assert condition | 条件不成立时立即报错，用来检查假设 |
| __len__ / __getitem__ | Python 特殊方法，允许 len(dataset)、dataset[index] |
| @decorator | 用装饰器包装函数；本项目的 Hydra 入口会用到，下一节细讲 |

## 8. 本节小结

先把仓库理解为一条流水线：Dataset 交付训练样本，Policy 规定输入输出，Model 实现网络，Workspace 管训练，EnvRunner 管评估。读类时找它的初始化函数和主要方法；读方法时看输入、输出和 self 上保存的状态。

### 自测

1. train.py 和 Workspace 的区别是什么？
2. self.cfg 是哪来的？
3. 继承父类后，为什么子类还能实现自己的 run？
4. batch["obs"] 与 batch["action"] 分别通常存什么？

答案要点：train.py 负责启动与分派；self 是当前对象；子类沿用父类能力并可覆盖方法；batch 的键给观察和动作命名。
