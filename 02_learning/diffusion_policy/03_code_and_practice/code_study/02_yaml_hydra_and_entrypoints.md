# 第 2 节：YAML、Hydra 与程序入口

## 本节要回答的问题

1. YAML 如何表示嵌套配置？
2. Hydra 如何组合主配置和任务配置？
3. 程序怎样从 train.py 走到具体 Workspace？
4. _target_、配置插值、hydra.utils.instantiate 各是什么？

## 1. YAML 是带层级的设置表

参考 diffusion_policy/config/train_diffusion_unet_image_workspace.yaml：

~~~yaml
defaults:
  - _self_
  - task: lift_image_abs

name: train_diffusion_unet_image
_target_: diffusion_policy.workspace.train_diffusion_unet_image_workspace.TrainDiffusionUnetImageWorkspace
horizon: 16
n_obs_steps: 2
n_action_steps: 8
~~~

读法：

- name: value 表示一个键值设置。
- 缩进表示层级；缩进下的设置属于上一层。
- 横线 - 表示列表条目。
- true/false 是布尔值；null 表示没有设置值。
- [3, 96, 96] 是数字列表。

例如 policy 下的 horizon 可用 cfg.policy.horizon 读取。缩进错了会改变键的归属，因而可能改变程序含义。

## 2. defaults 组合配置

defaults 是配置组合清单：

~~~yaml
defaults:
  - _self_
  - task: lift_image_abs
~~~

_self_ 表示当前配置本身也参与组合。task: lift_image_abs 表示从 config/task/ 选择 lift_image_abs.yaml，将其作为 task 子配置。任务文件会声明任务名、shape_meta、Dataset 和 EnvRunner 等任务特有设置。

例：config/task/pusht_image.yaml 中的 dataset._target_ 指向 PushTImageDataset；env_runner._target_ 指向 PushTImageRunner。主 Workspace 配置与任务配置组合后，Workspace 就能同时知道“用哪种策略”和“数据/环境由谁提供”。

## 3. _target_ 指定 Python 类或函数

例如：

~~~yaml
_target_: diffusion_policy.workspace.train_diffusion_unet_image_workspace.TrainDiffusionUnetImageWorkspace
~~~

最后一段是类名，前面的点分隔 Python 模块路径。它指向 train_diffusion_unet_image_workspace.py 中定义的 TrainDiffusionUnetImageWorkspace。

train.py 用 hydra.utils.get_class(cfg._target_) 找到最外层 Workspace 类，然后手动调用 cls(cfg)。Workspace 内部常用 hydra.utils.instantiate(cfg.policy)、instantiate(cfg.task.dataset) 等，根据子配置创建策略和数据集对象。

- get_class：找到“类本身”，由调用者再创建对象。
- instantiate：读取配置并直接创建对象。

## 4. 配置插值：引用配置里的其他值

例如主配置中：

~~~yaml
task_name: ${task.name}
shape_meta: ${task.shape_meta}
dataset_obs_steps: ${n_obs_steps}
~~~

${...} 是配置插值语法，表示从已组合的配置中读取某个值。上面的例子分别引用 task.name、task.shape_meta 和 n_obs_steps。这样同一个值可以引用多处，避免重复或不同步。

有些值使用 ${eval:'...'} 做算术，例如动作步数加控制延迟。train.py 注册 eval resolver 后，OmegaConf.resolve(cfg) 会展开配置引用和表达式。对于初学者，先记住插值是引用，eval 插值是计算即可。

## 5. 命令行可以覆盖配置

主配置目录由 train.py 的 hydra.main 指向 diffusion_policy/config。示意命令：

~~~console
python train.py --config-name=train_diffusion_unet_image_workspace task=pusht_image training.seed=42
~~~

- --config-name 选择 config/ 下的主配置名。
- task=pusht_image 替换 defaults 中所选的任务配置。
- training.seed=42 临时覆盖训练随机种子。
- 点号表示 YAML 层级路径。

README 中的复现实验使用另一种形式：

~~~console
python train.py --config-dir=. --config-name=image_pusht_diffusion_policy_cnn.yaml ...
~~~

该命令明确告诉 Hydra 从仓库根目录找配置文件，因为那个示例 YAML 不在 diffusion_policy/config/ 下。配置文件都叫 YAML，但目标 Workspace 和策略可能不同，必须检查 _target_，不能只凭文件名猜。

## 6. train.py 的真实控制流

train.py 中关键部分可以简化为：

~~~python
@hydra.main(config_path="diffusion_policy/config")
def main(cfg):
    OmegaConf.resolve(cfg)
    cls = hydra.utils.get_class(cfg._target_)
    workspace = cls(cfg)
    workspace.run()

if __name__ == "__main__":
    main()
~~~

执行次序：

1. 直接运行脚本，进入 __main__ 判断。
2. main() 被 Hydra 装饰器接管。
3. Hydra 解析命令行参数并组合 YAML，构造 cfg。
4. main(cfg) 展开配置引用。
5. 根据 cfg._target_ 找到 Workspace 类。
6. 创建 Workspace 对象。
7. 调用 workspace.run()。

表面上最后写的是 main()，但装饰器会先准备配置，再把 cfg 传进被包装的 main 函数。Hydra 不是扩散模型；它负责配置管理和对象创建。

## 7. 同一个配置怎样进入 Workspace 内部

进入 TrainDiffusionUnetImageWorkspace.__init__ 后：

- cfg.training.seed 控制随机种子；
- hydra.utils.instantiate(cfg.policy) 创建策略；
- cfg.training.use_ema 为真时，复制一份 EMA 模型；
- instantiate(cfg.optimizer, params=self.model.parameters()) 创建优化器。

进入 run() 后，Workspace 再通过 cfg.task.dataset 和 cfg.task.env_runner 创建数据集与环境运行器。配置像一张施工单，Python 类执行施工。

## 8. YAML 里复用列表的小写法

任务配置有时写：

~~~yaml
image_shape: &image_shape [3, 96, 96]
shape: *image_shape
~~~

&image_shape 定义可复用的 YAML 锚点，*image_shape 在另一处引用它。意思与复制同一份列表相近，目的只是避免重复。

## 本节自测

1. YAML 和 Hydra 各负责什么？
2. _target_ 只是显示文件路径吗？什么时候会创建对象？
3. config/task/pusht_image.yaml 大致提供什么？
4. --config-dir=. 为什么出现在 README 的训练命令里？

答案要点：YAML 写设置；Hydra 组合、解析并创建对象；任务配置提供数据和评估侧组件；根目录示例需要显式指定配置目录。
