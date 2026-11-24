# 第 6 节：Policy 与视觉编码器

## 本节要回答的问题

1. Policy 和神经网络 Model 的关系是什么？
2. 图片怎样转成网络可用的特征？
3. 视觉编码器如何处理图像与低维状态？
4. 模型怎样接收观察条件并输出动作计划？

## 1. Policy 是输入输出约定加实现

策略类定义模型如何训练和推理。基类 BaseImagePolicy 规定 predict_action(obs_dict) 这样的接口；具体 DiffusionUnetImagePolicy 再实现它。

从调用者角度：

~~~text
输入: obs 字典，包含图像/状态等张量
输出: action 字典，包含可执行动作片段，也可附带完整预测计划
~~~

EnvRunner 不需要知道 U-Net 每层如何计算，只要按统一接口把观察交给策略，并拿回动作。

## 2. 图片不能直接告诉网络“这是一只手/杯子”

相机给出的是像素数字。视觉编码器通过大量训练样本，把像素变成特征向量。训练目标来自动作扩散损失：如果视觉特征有助于把专家动作中的噪声预测准确，反向传播就会调整视觉编码器参数。

因此模型不是在每张图上先输出人类可读标签“杯子”“机械臂”，除非另有分类目标。它学习的是与当前任务动作有关的视觉线索，例如物体位置、相对关系、接触和场景变化。

## 3. MultiImageObsEncoder 的实际工作

见 diffusion_policy/model/vision/multi_image_obs_encoder.py。它从 shape_meta 读取每个观测字段的 type：

- type: rgb 的字段进入视觉网络；
- type: low_dim 的字段按数值特征处理；
- 每个图像键可先 resize、crop，再做图像归一化；
- RGB 通过配置指定的 ResNet 等模型成为特征；
- 低维状态本身作为向量特征；
- 最后沿特征维 torch.cat 拼接。

“拼接”是把向量接在一起，不是把图像直接像素相加。假如 RGB 编码成 512 维，状态是 2 维，合并后是 514 维特征向量。

图像会从 [B,C,H,W] 输入编码器。在策略中，最近 To 帧会先把 B 和 To 合并为 B×To 张图片，逐帧编码，再恢复成 [B,To,Df]，以保留每帧特征和时间关系。

## 4. ResNet 配置里几个易误解字段

在图像 Workspace 配置中，obs_encoder 的 _target_ 是 MultiImageObsEncoder，rgb_model 指向 get_resnet，name 为 resnet18。配置中 weights: null 表示这里没有请求加载预训练权重；是否预训练要以实际权重配置和模型构造代码为准。

crop_shape 指定裁剪尺寸，random_crop 控制训练期间是否随机裁剪；imagenet_norm 控制是否使用常见的图像均值/标准差变换。GroupNorm 的选项会把 ResNet 中某些 BatchNorm 替换为 GroupNorm，以便与训练所用 EMA 模型配合。

## 5. 策略如何把观察变成扩散条件

DiffusionUnetImagePolicy.predict_action 大致执行：

1. 用保存的 normalizer 归一化 obs。
2. 选取最近 n_obs_steps 帧。
3. 将图像/状态输入 obs_encoder，得到每帧特征。
4. 将这些特征组织成全局条件 global_cond，或作为逐时刻局部条件。
5. 创建动作形状的初始噪声计划。
6. 调用 conditional_sample 反复去噪。
7. 取出动作部分并反归一化。
8. 返回本轮要执行的动作切片，以及完整 action_pred。

## 6. 观察条件与动作去噪对象

论文层面的任务是根据观察 O_t 生成条件动作计划 A_t。代码里图像通常只负责产生条件特征；真正被 scheduler 加噪和更新的主张量是动作轨迹 [B,Tp,Da]。

obs_as_global_cond=True 时，观察编码成一个全局条件向量，U-Net 在整个动作序列上利用它。另一种实现可以把观察特征与动作沿特征维连接，再通过 mask 固定条件部分，这类方式常称 inpainting-style conditioning。配置与 Policy 决定采用哪条路。

## 本节自测

1. Policy 相比单独的神经网络多承担了什么职责？
2. 视觉编码器输出的是标签还是特征？训练信号从哪来？
3. RGB 与 agent_pos 最后是相加还是拼接？
4. 推理时真正逐步去噪的主要张量是什么？

答案要点：Policy 实现任务接口、归一化和采样；输出特征并由动作损失间接学习；特征沿维度拼接；动作计划是主要去噪对象。
