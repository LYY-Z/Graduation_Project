# 从 Diffusion Policy 理论走到可读、可核验的 UR7e 部署代码

这套教材写给这样的你：已经理解“给观察、从噪声逐步生成动作序列”的 Diffusion Policy 思想，但对 Python、工程目录、相机数据、机械臂通信以及真实执行程序还不熟。这里从整个系统怎样流动讲起，再看每个文件负责什么，最后拆开常见代码行。你不需要先把 Python 全部学完，读完也不应只记住几条启动命令。

本教材对应当前模块化工程 [diffusion_policy_ur7e](../../../03_code/diffusion_policy_ur7e/README.CN.md)。重构前工程 [diffusion_policy_ur7e_v1](../../../99_archive/code.zip) 保留既有实现与实机证据；[部署记录](../deployment_record.CN.md)汇总当时的实现、指标与验证依据。

本教材形成于重构阶段，2026-11-02整理时同步了目录名称与链接。后文“本轮验证”“新版当前”等表述均指原重构记录的时间范围，不表示本次重新完成训练、推理或实机验收。当前环境与启动操作以项目[中文README](../../../03_code/diffusion_policy_ur7e/README.CN.md)和[Guide](../../../03_code/diffusion_policy_ur7e/docs/guide.CN.md)为准；`verification/`保留原始证据字段与原项目命名。

## 先知道这项工作已经证明到哪里

原版工程完成过一次受监督的极小范围实机短测：三条 TCP 目标得到控制确认并按反馈到位，留下 132 条运动反馈。累计命令距离约 2.119 mm，第一条之前到最后一条之后的净实测位移约 2.022 mm。这说明当时的图像、状态、原模型推理、受限目标生成及控制反馈链路实际连通。

它没有证明公开 Push-T 权重已学会当前真实任务，也没有得到真实任务成功率。文件名中的 `test_mean_score=0.748` 来自原仿真实验。三条小运动属于同一次链路短测，不能写成三次独立任务全部成功。

本轮新工程的目录、接口和代码组织进行了整理，验证范围是**不连接硬件、不运行模型推理的检查与测试**。原版实机结果不能自动转移成新版实机验收结果。理解这一点，才能正确解释后面出现的“通过”“完成”“预测”和“到位”。

## 六章分别解决什么问题

| 阅读位置 | 要解决的实际困惑 | 读完后应该能做什么 |
|---|---|---|
| [01 工程和 Python](01_project_and_python.md) | 一个文件夹怎么变成可运行程序？函数、类、import 是什么？ | 看懂入口、配置、调用关系、对象、异常与清理结构 |
| [02 硬件和观察](02_hardware_and_observations.md) | 相机和六轴机器人怎样变成两个数组？时间和坐标为什么复杂？ | 逐轴解释形状，手算裁剪、位置映射和因果配对 |
| [03 模型和推理](03_model_and_inference.md) | 权重怎么加载？谁做归一化？100 次去噪和 8 步输出在哪里？ | 区分模型构造、权重、配置、采样与输出切片 |
| [04 控制和执行](04_control_and_execution.md) | 二维输出为什么能驱动六轴？如何限制？怎样确认真的到位？ | 手算限幅，读懂 ready、ACK、反馈、异常和预算 |
| [05 阅读和操作](05_reading_and_operation.md) | 先读哪段？以后怎样分终端运行？保存什么证据？ | 按阶段检查、理解命令、读日志、区分离线测试与实机验收 |
| [06 重构与验证](06_refactoring_and_verification.md) | 到底改了哪里？为什么说离线检查通过，仍不能替代实机复验？ | 对照新旧模块，理解测试、来源清单、审查修复与版本边界 |

每章都包含术语定义、小段代码解释、数值例子、常见问题和带答案的练习。第一次按顺序阅读；第二次可以从问题跳转。遇到不懂的 Python 语法先回第 1 章，遇到数组轴和单位先回第 2 章，遇到真实运动先回第 4 章。

## 一张完整地图：程序到底把什么交给谁

```text
Gemini 335L 单路 RGB 相机
  │ Orbbec ROS 驱动发布 Image 消息
  ▼
系统 Python 3.10：hardware/camera_bridge.py
  │ 校验时间和光学 frame，解码、中心裁剪、缩放
  ▼
.runtime/wrist_rgb.npz：完成后原子替换的最新帧
  │ 独立推理 Python 3.9 读取
  ▼
hardware/observations.py ───── hardware/robot_state.py
  │ 两帧图像及各自配对的状态       ▲ RTDE 只读状态
  │                              │
  ├── geometry.py：把 TCP 位移映射为二维 agent_pos
  ▼
image [1,2,3,96,96]；agent_pos [1,2,2]
  │ inference/policy.py 调用原始策略
  ▼
third_party/diffusion_policy：观察编码 → 100 次 DDPM 去噪
  ▼
action_pred [1,10,2]；action [1,8,2]
  │ pipeline.py 本轮只取 action[0,0]
  ▼
geometry.py 逆映射 → control/safety.py 限幅、平滑、再检查
  │ preview 到这里记录候选；execute 另通过显式现场条件
  ▼
control/robot.py：新鲜状态、TCP、IK、ready 检查 → 私有 moveL
  ▼
UR 控制器协调六个关节 → 实际反馈 → 连续到位确认
  │ 下一轮使用新观察，最多三条目标
  └──────── recording.py 保存元数据、数组与事件
```

箭头表示数据或调用方向，不代表每一步都在一个线程里，也不代表所有模式都会走到最下面。`inspect` 只检查文件与契约；`capture` 采集；`shadow` 推理；`preview` 加入受限目标生成；只有明确选择 `execute` 并通过检查，才会创建真实控制通道。相机桥接需要单独运行，它不会顺便启动相机驱动。

## 新工程的 12 个业务文件

“业务文件”指承担部署功能的代码，不把普通的 `__init__.py` 和 `__main__.py` 包装入口算进去。

| 文件 | 用一句具体的话概括 |
|---|---|
| [cli.py](../../../03_code/diffusion_policy_ur7e/src/dp_ur7e/cli.py) | 把终端里的子命令分配到相应功能 |
| [config.py](../../../03_code/diffusion_policy_ur7e/src/dp_ur7e/config.py) | 读取 YAML，校验数值、路径和接口契约 |
| [pipeline.py](../../../03_code/diffusion_policy_ur7e/src/dp_ur7e/pipeline.py) | 按顺序组织采集、推理、预演或执行以及退出 |
| [geometry.py](../../../03_code/diffusion_policy_ur7e/src/dp_ur7e/geometry.py) | 做 TCP 几何和仿真二维位置的正逆映射 |
| [recording.py](../../../03_code/diffusion_policy_ur7e/src/dp_ur7e/recording.py) | 把每次运行的输入、配置和事件保存到独立目录 |
| [hardware/camera.py](../../../03_code/diffusion_policy_ur7e/src/dp_ur7e/hardware/camera.py) | 处理图像数组，原子读写最新帧 |
| [hardware/camera_bridge.py](../../../03_code/diffusion_policy_ur7e/src/dp_ur7e/hardware/camera_bridge.py) | 接 ROS 图像话题，把消息交给图像与帧交换代码 |
| [hardware/robot_state.py](../../../03_code/diffusion_policy_ur7e/src/dp_ur7e/hardware/robot_state.py) | 建立只读 RTDE 连接并读取一致的状态快照 |
| [hardware/observations.py](../../../03_code/diffusion_policy_ur7e/src/dp_ur7e/hardware/observations.py) | 持续采集、维护历史，并构造有效的两帧观察 |
| [inference/policy.py](../../../03_code/diffusion_policy_ur7e/src/dp_ur7e/inference/policy.py) | 校验 checkpoint，严格加载原策略，统一预测调用 |
| [control/safety.py](../../../03_code/diffusion_policy_ur7e/src/dp_ur7e/control/safety.py) | 只用数字计算运动限制，不负责发网络命令 |
| [control/robot.py](../../../03_code/diffusion_policy_ur7e/src/dp_ur7e/control/robot.py) | 检查控制后端、发送小目标、监测反馈并清理 |

包内只分 `hardware/`、`inference/`、`control/` 三个子目录。每个目录名对应一个现实职责，避免初学者必须穿过很多只有一个函数的小层级。

## 哪些资料应该放在什么地方

新代码仓库里的公开说明面向“陌生读者怎样安装、理解和复现”，需要准确、简洁、没有凭据。本目录面向你个人的学习，允许用更多篇幅解释 Python、数组、日志和阅读方法。原始运行证据则负责支持“当时发生了什么”。三者相互引用，不相互替代。

这套教材没有保存密码、私钥或登录口令。示例机器人地址统一写为文档地址 `192.0.2.1`，它只是占位符。真实地址、相机选择和机器相关声明放在本地 `config.yaml`；从 `config.example.yaml` 复制后填写，并按工程忽略规则留在本机。不要把“配置里写了已核对”当成完成了实际核对。

模型副本在 `third_party/diffusion_policy/`，私有控制 SDK 源码在 `third_party/ur_rtde_guarded/source/`；私有原生模块和清单属于 `.runtime/control_backend/`。原子帧文件 `.runtime/wrist_rgb.npz` 会不断覆盖，长期记录位于每次运行新建的 `runs/` 子目录。后两者用途不同：前者交换当前帧，后者保存可回看的证据。

## 学习时先完成的三件事

1. 能不看正文，口头说清“相机消息→观察字典→原模型→小目标→反馈”的顺序，并指出谁使用哪个 Python。
2. 在纸上解释 `image[0,1,2,10,20]` 与 `action[0,0]` 的每个索引，分别写出单位。
3. 打开代码但不连接设备，找到“实际创建控制连接”的位置，并说清它前面有哪些条件。

这三件事做不到时，继续读教材和运行不涉及硬件的小例子；不需要靠启动机器人来弥补对代码的陌生。

继续：[01 工程和 Python](01_project_and_python.md)。
