# 03　已有模型如何被加载，并生成一段动作

[教材目录](README.md) · 上一章：[硬件和观察](02_hardware_and_observations.md) · 下一章：[控制和执行](04_control_and_execution.md)

你已经理解 Diffusion Policy 的理论，本章重点补上“公式到代码”的桥梁：Python 怎样创建网络、权重装到哪里、观察怎样进入视觉编码器、去噪循环在哪一层、返回值为何有两份轨迹。代码入口是 [inference/policy.py](../../../03_code/diffusion_policy_ur7e/src/dp_ur7e/inference/policy.py)，算法主体保留在 [原 Transformer 策略](../../../03_code/diffusion_policy_ur7e/third_party/diffusion_policy/diffusion_policy/policy/diffusion_transformer_hybrid_image_policy.py)。

## 1. 先分清文件、对象和一次计算

“checkpoint”是保存模型相关数据的文件，可能包含结构配置、训练权重、EMA 权重、normalizer 以及训练状态。“policy 对象”是程序按结构构造、装入权重后，留在内存或 GPU 上的可调用对象。“一次推理”是给这个对象一组当前观察，返回预测动作。

所以它们的关系是：

```text
文件：checkpoint + 配置
  ↓ 校验来源、字节数与 SHA-256
构造：按保存配置创建原策略对象
  ↓ 严格加载已训练 EMA 权重与 normalizer
准备：移动到指定设备，设评估模式
  ↓ 每轮给新的 observation
调用：policy.predict_action(...)
  ↓
结果：action_pred 和 action
```

模型不需要每轮从磁盘重新加载，权重也不会因为调用了一次预测而自动变化。真正每轮变化的是观察、随机采样状态以及输出轨迹。

## 2. 本工程具体使用哪一个公开模型

| 项目 | 当前选择 |
|---|---|
| 原任务 | 仿真 Push-T 的图像策略 |
| 策略类 | `DiffusionTransformerHybridImagePolicy` |
| checkpoint | `models/pusht_image_transformer.ckpt` |
| 已记录大小 | 412,727,949 字节 |
| SHA-256 | `d68cdbcf9c21df724fb60f2573aa28a22a333f555225a2ec29cb6b7890608c56` |
| 加载分支 | `ema_model` |
| 观察长度 | 2 帧 |
| 完整预测长度 | 10 步 |
| 返回动作段长度 | 8 步 |
| 推理调度器 | `DDPMScheduler`，100 次去噪迭代 |
| 日程 | `squaredcos_cap_v2` |
| 网络预测对象 | `epsilon`，即噪声 |
| 方差类型 | `fixed_small` |
| 本阶段训练 | 无训练、无在线更新 |

原源码固定版本记录在工程清单中；重构移动目录，不应悄悄改成另一套策略实现。允许配置里存在其他模型类别，并不意味着本次真的加载了另一个类别。当前实际讲的是 Transformer checkpoint，不是 CNN+FiLM/一维 U-Net 版本，也不是把论文所有变体同时运行。

文件名中的 `test_mean_score=0.748` 是原仿真评测的分数标记。它不是本机器臂成功率，也不是对真实腕部相机泛化能力的保证。

## 3. 逐步读 `load_policy`

`load_policy(cfg)` 的外部输入是部署配置字典，输出通常包括策略对象和可记录的实际模型详情。它既负责“加载”，也负责“确保没有加载错”。

### 3.1 文件校验先于反序列化

SHA-256 是根据文件全部字节计算的摘要。相同字节得到相同摘要；少了几个字节或被替换的文件通常会得到不同结果。它用于确认“这份文件是否与清单一致”，不是评价模型性能，也不能单独证明下载来源可信。

```python
if file_size != manifest["bytes"] or sha256_file(path) != manifest["sha256"]:
    raise ValueError("checkpoint size or SHA-256 mismatch")
```

`or` 表示只要一项不符就拒绝。大文件按块读取计算哈希，避免先把整个文件又复制一份到内存。校验通过不运行策略、不接机器人，只说明文件匹配。

### 3.2 找到原实现，再读保存的数据

Python 需要能导入 `diffusion_policy...` 里的策略类，部署层将固定的 `third_party/diffusion_policy/` 加入查找路径。`torch.load(..., map_location="cpu", ...)` 先把 checkpoint 数据读到 CPU，随后再按部署设备迁移。

这类 checkpoint 会使用 Python 对象序列化机制，不是任意未知文件都应该直接加载。工程的固定来源和哈希验证是这里的实际依据；不能随便找一个同名 `.ckpt` 替换后关闭检查。

### 3.3 结构契约验证

“契约”是调用双方必须遵守的规定。本模型观察键必须恰好为 `image`、`agent_pos`，每帧形状分别为 `[3,96,96]`、`[2]`，动作维度是 `[2]`；还要检查策略类与时间长度兼容。

```python
expected = {"image": [3, 96, 96], "agent_pos": [2]}
```

这不是最终带 B、T 的完整输入 shape，记录的是每个时刻的单项 shape。两帧和批次轴由观察字典与策略调用约定加上。不要看到这里没写 `[1,2,...]` 就给完整输入删掉轴。

### 3.4 创建结构，装入权重

Hydra 是根据配置实例化对象的工具。`_target_` 中的完整 Python 路径指出该创建哪一个类；其他配置字段变成构造参数。

```python
policy = hydra.utils.instantiate(checkpoint_cfg.policy)
policy.load_state_dict(payload["state_dicts"]["ema_model"], strict=True)
```

第一行建出网络结构；第二行装入已经训练的数值。仅建结构时的参数初始化不能当作已训练策略使用。`state_dict` 是从参数名字到张量的映射；`strict=True` 要求应有的参数名和维度相符。把它改成 `False` 让错误通过，可能留下未加载的随机参数。

EMA 是训练时对模型权重做指数移动平均得到的分支。推理选择保存好的 EMA 权重；这里没有在现场继续做 EMA 更新。normalizer 也保存在状态里，并随严格加载保留，而不是根据两帧现场数据重新估计。

### 3.5 迁移设备和评估模式

```python
policy.to(torch.device(cfg["inference"]["device"]))
policy.eval()
```

设备可能是 CPU 或指定 CUDA GPU。GPU 是执行大量矩阵计算的加速设备，不是另一种模型。设备选择不应改变 checkpoint 任务定义。

`eval()` 切换带训练/评估差异的网络模块行为，例如关闭训练时 dropout。它不等于“执行一次评测”，也不会自动关闭梯度追踪；预测处另有 `torch.inference_mode()`。两者处理不同问题。

## 4. 统一 `predict` 函数怎样接上观察

部署层的观察是 NumPy 数组，PyTorch 网络接收张量。张量也是多维数值容器，但能够使用 GPU 和自动求导等机制。

```python
tensors = {
    name: torch.from_numpy(array).to(device=policy.device, dtype=policy.dtype)
    for name, array in observation.items()
}
with torch.inference_mode():
    result = policy.predict_action(tensors)
```

`observation.items()` 逐项提供键和值；本例保留键名和 shape，只换成匹配设备与类型的张量。`inference_mode()` 表示这段计算不需要训练梯度，减少额外追踪开销。它不负责校验任务语义，也不移除扩散随机性。

预测后常见转换为：

```python
result[name].detach().cpu().numpy()
```

`detach()` 使结果脱离梯度图；`cpu()` 移回主机；`numpy()` 变成后续几何、记录能使用的数组。不能把 CUDA 张量直接当成普通 NumPy 数组。统一这段调用让影子推理和执行流程使用同一入口，减少复制两份推理代码后逐渐不一致的问题。

## 5. 两层归一化到底是谁做的

归一化是把数值变换到模型合适的尺度。重要的不是只记“归一化”三个字，而是明确哪一项在什么时候被转换。

| 阶段 | 输入 | 操作主体 | 结果 |
|---|---|---|---|
| 外部像素处理 | HWC `uint8`、0–255 | `hardware/camera.py` | CHW `float32`、0–1 |
| 策略观察处理 | 0–1 图像及仿真尺度 agent_pos | 保存的 `normalizer.normalize` | 与训练输入一致的网络数值尺度 |
| 生成完成 | 归一化动作轨迹 | `normalizer['action'].unnormalize` | 原任务动作尺度，部署层记作 px |

用一个纯教学的一维线性例子理解：若某变量按 `n=(u-256)/256` 处理，那么 `u=256→n=0`，`u=384→n=0.5`，反变换 `u=256n+256`。**这个公式只帮助理解线性归一化，不声称就是当前 checkpoint 所有字段的实际常数。** 实际系数要从保存的 normalizer 读取。

上游返回动作时已经反归一化。再反一次会把 `[277,215]` 解释错；把真实位置的米直接塞进 `agent_pos`，让 normalizer 自己猜单位也会出错。normalizer 只是按既定数值规律处理，不理解某个坐标是否来自真实相机标定。

外部除以 255 与内部 normalizer 是两层规定，不能因看到“已经缩放过”就删除其中一层，也不能用当前两帧重新拟合训练数据尺度。

## 6. 图像怎样变成 Transformer 的条件

观察编码器把原始图像和低维位置转成较紧凑的特征表示。特征是网络计算得到的数字，不是必然附带“这是杯子”的类别文字。

当前保留上游通过 robomimic 构造的视觉模块。可以按以下顺序理解：

```text
每帧 RGB 图像
  ↓ checkpoint 内部固定评估裁剪，96×96 → 84×84
ResNet-18 卷积骨干
  ↓ 空间特征图
Spatial Softmax 等视觉表示层
  ↓ 视觉特征向量
与当前帧 agent_pos 的低维表示组合
  ↓ 一个时刻的观察特征
两帧重新排为 [B,To,Do] → cond
```

ResNet-18 是多层卷积网络；卷积利用局部图像区域计算特征，层次加深后形成更抽象的响应。Spatial Softmax 用空间响应提取紧凑、保留位置信息的表示。它与“相机像素到机器臂坐标标定”是不同计算。

外部仍必须给 96×96。内部 `crop_shape=[84,84]`、`eval_fixed_crop=true` 属于已保存的模型配置，评估时使用固定中心裁剪。不能在桥接先改成 84×84，然后声称仍满足 96×96 checkpoint 契约。

上游会临时把批次与时间合并，让两帧使用同一编码器，随后还原：

```text
[B,To,3,96,96] → [B×To,3,96,96]
     每帧编码 → [B×To,Do]
     还原时间 → [B,To,Do]
```

B 是批次数，To 是观察帧数，Do 是编码器特征维度。对本工程 B=1、To=2。Do 不是物体种类数，不应把某个通道直接解释成“杯子概率”。在相机视角发生大变化时，输出有限不代表特征仍正确对应任务。

## 7. 理论里的条件去噪在代码哪几行

原策略的 `predict_action` 先做观察归一化和编码，得到 `cond`；再构建目标 shape 为 `[1,10,2]` 的条件容器，把实际采样交给 `conditional_sample`。

```python
trajectory = torch.randn(
    size=condition_data.shape,
    dtype=condition_data.dtype,
    device=condition_data.device,
)
scheduler.set_timesteps(self.num_inference_steps)
for t in scheduler.timesteps:
    model_output = model(trajectory, t, cond)
    trajectory = scheduler.step(model_output, t, trajectory).prev_sample
```

逐行解释：

1. `randn` 生成正态随机数，建立十个二维动作候选的初始噪声张量。它处于归一化动作空间。
2. `set_timesteps(100)` 为本次采样设置扩散级序列，不是在机械臂上运行 100 条动作。
3. 每个 `t` 表示当前扩散噪声级；Transformer 同时看当前轨迹、扩散级和观察条件。
4. `model_output` 在当前配置下是噪声估计。
5. 调度器按 DDPM 系数和相应随机项计算上一级样本，`.prev_sample` 取更新后的轨迹。

你熟悉的均值形式可以对应为：

$$\mu_\theta(A^k,O,k)=\frac{1}{\sqrt{\alpha_k}}
\left(A^k-\frac{\beta_k}{\sqrt{1-\bar\alpha_k}}
\epsilon_\theta(A^k,O,k)\right).$$

理论符号 `A^k` 对应循环中的 `trajectory`，噪声网络对应 `model(...)`，DDPM 反向计算由 `scheduler.step(...)` 实现。适配层不再手写一套系数，也不把论文中便于说明的简写当作这里的逐行实现。

本配置的 `obs_as_cond=true` 表示观察作为条件输入；`pred_action_steps_only=false` 表示先生成完整十步再切片。代码里还有其他分支，但阅读当前运行时先沿这两个实际布尔值走，避免把所有可能分支同时想象成发生了。

### 一个循环内固定的是什么

同一次推理的两帧观察固定，`cond` 固定。100 次去噪不会每次重新拍一张图，也不会每去噪一步就运动一下。只有完成这一轮、通过执行与反馈后，下一轮才取新的观察。

当前没有 DDIM 加速、没有缩减为十次去噪，没有 warm-start 历史轨迹。每次采样仍从新噪声开始。运行开始设置随机种子有助于控制随机序列，但随机数状态会继续前进，不是每轮把种子重置成同一值。

注意“模型预热”和“warm-start”不是同义词。预热是在正式候选之前先调用一次，让初始化开销暴露出来，并丢弃那次输出；warm-start 则是用历史轨迹初始化本轮去噪。当前有前者，没有后者。

## 8. 为什么有十步预测，却只返回八步动作段

上游得到反归一化的完整 `action_pred` 后，执行：

```python
start = n_obs_steps - 1       # 2 - 1 = 1
end = start + n_action_steps # 1 + 8 = 9
action = action_pred[:, start:end]
```

冒号前的 `:` 表示保留所有批次；第二轴取 `[1:9]`，包含索引 1 至 8，不包含 9。于是：

```text
action_pred  [1,10,2]：完整索引 0 1 2 3 4 5 6 7 8 9
action       [1, 8,2]：取完整索引   1 2 3 4 5 6 7 8
本轮候选 action[0,0]：完整轨迹的 action_pred[0,1]
```

`action[0,0]` 第一个 0 是批次，第二个 0 是返回动作段的第一步；取出后剩一个长度二的向量，比如 `[277.4,214.8]`。它仍是仿真任务平面坐标，不是 `[速度,加速度]`、两个关节角或真实图片像素。

模型生成十步、上游返回八步、执行器最多发三条，是三个独立层次。当前执行流程每轮只使用返回动作段第一项，完成一个小目标后重新采集与推理。它没有开环依次执行那八个点。

## 9. 从输出到候选，先看一段真实数值

原版成功短测第一轮返回动作段首项约为 `[277.403442,214.829193]`。按该会话的工程映射逆变换，得到候选 base 位置约 `[0.274339,0.381804,0.697228] m`，当时实际 TCP 约 `[0.252929,0.422986,0.697230] m`。

两者平面距离约 46.4 mm。这个数远超当时允许的一步运动，因此后面执行层只保留候选方向，先把位移范数限制到 1 mm，再做 0.5 平滑。首条平面目标约 0.5 mm，实际首条起止位移约 0.495 mm。

这段例子有三个作用：让你看到模型数值的单位；看到逆映射还不是命令；看到限制真正切断了原始大候选。它不能证明这条方向是任务正确方向，也不意味着现在可以将限幅放宽到 46.4 mm。

输出验证还要求 `action` 和 `action_pred` 形状准确、每项有限。形状正常只是进入后续检查的必要条件之一，不是任务成功。`clip_sample=true` 是 DDPM 在归一化采样中的裁剪，也不能替代米单位的实体执行限制。

## 10. 推理时没有发生的训练步骤

原仓库里同时包含训练和推理方法，所以你会看到 `compute_loss`、`get_optimizer`、反向传播相关代码。但部署调用的是 `predict_action`，没有因为导入一个策略类就自动调用训练方法。

训练阶段会用演示动作生成噪声学习目标、计算损失、反传梯度、更新参数。当前部署阶段不提供训练批次，不创建训练优化器，不计算奖励，不做策略梯度，也不会把三条真实运动反馈自动变成学习更新。

“端到端链路连通”描述外部相机一直到反馈的工程路线；“端到端学习”描述训练时视觉编码器与策略如何共同学习；“任务学会”还需要真实任务定义和评测。三个说法不能互相替代。

## 常见问题

**权重本来在仿真训练，为什么能在真实图像上输出？** 网络对合法数字输入总能进行数值计算，输出存在不等于分布匹配或任务正确。真实视角与视觉分布的差异正是后续任务适配需要研究的问题。

**把模型文件改名成 UR7e，能算真实机械臂模型吗？** 不能。名称不改变训练数据、动作语义和权重。

**为什么不直接修改 `transformer_config.yaml` 的 horizon？** sidecar 便于人审阅；实际构造以 checkpoint 内配置为核心。结构与参数不匹配会严格拒绝。即便能构造，也不代表改动得到训练支持。

**100 次循环中的 t 与动作序列中的十步 T 相同吗？** 不同。t 是扩散噪声级，T 是预测时间轴长度。一次扩散更新会同时更新整个十步轨迹。

**为什么 GPU 利用率低也可能很慢？** 小批次、初始化、数据搬运、CPU 操作与其他负载都可能影响耗时。推理计时也不同于从采集到到位的总周期，应先看具体记录，不能只凭一个利用率百分比判断。

## 练习与答案

1. `[1,10,2]` 中每个数是什么意思？一共包含几个动作数值？
2. 返回动作段的第 3 步 `action[0,2]` 对应完整轨迹哪一步？
3. 预测后看到 `[300,250]`，还需要再做一次保存 normalizer 的反归一化吗？
4. `eval()` 能否让每次扩散输出完全一样？
5. 模型先预热一次并丢弃结果，是否证明本轮使用历史轨迹 warm-start？
6. 哪两个事实可以说明这次只是推理而非在线训练？

答案：

1. 一个批次、十步预测、每步二维动作；共有 20 个数值。
2. `action_pred[0,3]`，因为动作段从完整索引 1 开始。
3. 不需要。上游已经反归一化，它仍需逆工程映射、限幅和完整执行检查。
4. 不能。它切换网络评估行为，DDPM 的随机采样仍存在。
5. 不证明。预热处理初始化开销；当前下一轮仍从随机噪声开始，没有历史轨迹初始化。
6. 没有损失反传与优化器更新；权重和 normalizer 从 checkpoint 加载后保持不变。运动反馈用于核验执行，不自动更新网络。

[返回目录](README.md) · [下一章：控制和执行](04_control_and_execution.md)
