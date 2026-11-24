# 05 疑问归纳、阻塞点与复习索引

本篇按“问题为什么反复出现”归纳当前可见对话中的技术提问。标题保留部分原话，其他为同义归并；重复的“没看懂”表示解释需要进一步拆细，不视为没有内容的新问题。

正文解释在01～04，本篇提供定位与最短解答。提问里上下文不足的地方保留不确定性，避免编造已经明确的答案。

## 1. 最容易反复卡住的六种混淆

| 阻塞点 | 导致的误解 | 复习时先问什么 |
|---|---|---|
| 环境时间与优化时间混在一起 | 重新前向被当成机器人又执行一次 | 现在是在采集、求梯度，还是step更新？ |
| 历史缓存与网络权重混在一起 | 运行中用了历史就被当成在线训练 | 变的是缓存数值还是θ？ |
| Trial、Episode、segment、batch混在一起 | 认为分段就要重置机器人 | 这是物理运行边界、信息边界还是计算边界？ |
| 奖励、回报、价值、优势混在一起 | 正奖励必定应提高动作概率 | 比较的是实际反馈、长期结果还是相对预期？ |
| 目标数值与损失梯度混在一起 | 损失相同或比例1，就认为没有更新方向 | 数值一样与导数为零是否等价？ |
| 论文与参考实现混在一起 | 默认12×256等被当成作者配置 | 结论来自论文、原理说明还是第三方代码？ |

## 2. 全局、任务与交互组织

<a id="q01"></a>
### Q01 鲁棒性和适应性分别是什么意思？

鲁棒性描述条件变化后仍能工作；适应性描述获得更多交互信息后控制能够调整。前者是表现性质，后者强调信息积累与调整过程。复习：[01第3节](01_paper_and_full_pipeline.md#robustness)。

<a id="q02"></a>
### Q02 “所以是因为适应性才有鲁棒性吗？”

不是唯一因果。广泛训练可带来初始鲁棒性，利用历史的适应还可改善后续表现。不能将所有初始能力都解释成部署后才学到。复习：[初始鲁棒性](01_paper_and_full_pipeline.md#robustness)。

<a id="q03"></a>
### Q03 最初的鲁棒性怎样实现？

训练让同一策略接触不同身体、动力学与扰动，奖励推动它在这些条件下工作。它提供泛化机会，不是对所有未见变化的保证。复习：[任务与训练](01_paper_and_full_pipeline.md#protocol)。

<a id="q04"></a>
### Q04 网络是不是先识别“走路还是抓东西”？

本文主要讨论运动控制，重点是从交互辨别当前身体控制条件，并非主要做任务名称分类。内部表示不一定输出明确的物理参数标签。复习：[研究问题](01_paper_and_full_pipeline.md#robustness)。

<a id="q05"></a>
### Q05 当前身体信息已经输入了，为什么还要历史？

相近瞬时状态可能来自不同原因。过去的控制与实际响应可帮助区分持续条件变化和短暂偏差。历史不会自动有用，需要训练教策略利用。复习：[01第3节](01_paper_and_full_pipeline.md#robustness)。

<a id="q06"></a>
### Q06 机器人、网络、仿真、强化学习怎么串起来？

选任务→网络据观测选动作→仿真产生真实于该仿真规则的响应与奖励→保存经历→PPO更新网络→继续交互。复习：[完整主线](01_paper_and_full_pipeline.md#overview)。

<a id="q07"></a>
### Q07 任务采样 \(\mathcal M\sim\rho_{\mathcal M}\)有什么作用？

决定当前采集面对哪种身体与控制条件，也决定哪些条件更常贡献训练数据。ρ是采样规则，不自动等概率。复习：[公式（1）的采样](01_paper_and_full_pipeline.md#sampling)。

<a id="q08"></a>
### Q08 抽k次Trial有什么作用？

形式上让一组任务经历包含不同数量的尝试，使历史利用和跨尝试表现进入目标。实际训练又改用时间预算u。复习：[次数与预算](01_paper_and_full_pipeline.md#protocol)。

<a id="q09"></a>
### Q09 “E∼π”为什么也用采样符号？

它表示在选定环境中由策略驱动产生一组随机交互经历。网络选动作，环境产生身体状态和奖励，不是网络一次写出完整真实未来。复习：[轨迹怎样产生](01_paper_and_full_pipeline.md#sampling)。

<a id="q10"></a>
### Q10 为什么目标20°，仿真得到的实际角度可能只有12°？

目标是控制要求，实际响应受到时间、执行器、增益、惯量、接触等约束。仿真负责算响应，不是把状态直接赋值成目标。复习：[单步闭环](01_paper_and_full_pipeline.md#training-deployment)。

<a id="q11"></a>
### Q11 轨迹到底是什么？

按时间排列的状态/观测、动作、奖励和边界记录。它由连续交互产生，保存后可用于训练与分析。复习：[名词表](01_paper_and_full_pipeline.md#concepts)。

<a id="q12"></a>
### Q12 Trial和Episode有什么区别？

Trial是一次运行；论文Episode可包含同任务多个Trial并共享历史。第三方Gym入口的episode编号未必采用这个定义。复习：[四种边界](01_paper_and_full_pipeline.md#concepts)。

<a id="q13"></a>
### Q13 每个Trial前都有适应时间吗？

不是。预算u组织这一组适应交互，期间可发生若干Trial，然后运行最终Trial。复习：[适应预算](01_paper_and_full_pipeline.md#protocol)。

<a id="q14"></a>
### Q14 适应窗口里的Trial是不是不算，只算最终Trial？

评估计分和训练目标要分开。最终评估可以单独计分，形式训练目标累计整组经历；时间预算版本未披露全部损失掩码。复习：[目标与计分](01_paper_and_full_pipeline.md#protocol)。

<a id="q15"></a>
### Q15 所以不再抽Trial次数，只抽时间预算？

原文先用k定义问题，再用u改进实际训练组织。两个层次保留，不能说前面公式失效或两者必须同时独立采样。复习：[公式到实现](01_paper_and_full_pipeline.md#protocol)。

<a id="q16"></a>
### Q16 出现“最终Trial”就一定是部署吗？

不是。训练也可以构造适应尝试加最终尝试；测试也可用类似时间组织。是否更新参数要看当前阶段。复习：[阶段区别](01_paper_and_full_pipeline.md#training-deployment)。

<a id="q17"></a>
### Q17 zero-shot也会交互，和few-shot差在哪？

差在是否给予额外、不计最终成绩的预评估适应预算，以及历史保留规则。Zero-shot当前运行中仍积累历史。复习：[部署协议](01_paper_and_full_pipeline.md#training-deployment)。

<a id="q18"></a>
### Q18 运行过程中每次都会使用历史吗？

网络按当前可用缓存与掩码读取历史。首步可能没有旧历史，容量与Episode规则限制读取范围。并非每一步都重新训练。复习：[历史与权重](02_network_and_memory.md#boundaries)。

<a id="q19"></a>
### Q19 “先短后长”为什么这样训练？

这是全局训练课程，先短Trial/小U，再延长。不要理解成每次部署前都要先运行一个规定短阶段。复习：[课程安排](01_paper_and_full_pipeline.md#protocol)。

## 3. 数字、网络与QKV

<a id="q20"></a>
### Q20 “输入分别是2、3、4、5、6怎么办？”

原提问缺少完整上下文，应先区分是观测维数、关节数还是样本数。论文使用统一关节空间；第三方README还示范多输入MLP与动作selectors，具体维度不能凭数字猜。复习：[数据轴](02_network_and_memory.md#tensors)、[代码配置](04_code_and_reproduction.md#config)。

<a id="q21"></a>
### Q21 网络内部到底是什么？

是线性变换、激活、注意力、归一化等可微数字运算，由代码组合，参数在训练中调整。库提供组件，不会自动替人决定完整任务定义。复习：[数字到模型](02_network_and_memory.md#tensors)。

<a id="q22"></a>
### Q22 64或256个特征是什么意思？

每个时间位置内部向量的长度，不是关节数或未来动作数量。当前入口dim64，教学256不是论文统一值。复习：[内部维度](02_network_and_memory.md#tensors)。

<a id="q23"></a>
### Q23 同一个线性层处理每一行，是同时吗？

同一套权重可通过矩阵运算处理多行，通常能够并行。同层不同时间位置共享权重，不需要各建一层。复习：[张量流](02_network_and_memory.md#forward)。

<a id="q24"></a>
### Q24 位置特征有什么作用？

让注意力区分时间顺序或相对距离。它不提供未来状态，也不是手工告诉网络正确动作。复习：[Transformer层](02_network_and_memory.md#transformer-layer)。

<a id="q25"></a>
### Q25 网络怎样把很多时刻的历史用起来？

每个候选位置提供K/V，当前Q计算一行匹配权重并组合Value；多层继续加工。复习：[QKV完整计算](02_network_and_memory.md#qkv)。

<a id="q26"></a>
### Q26 Actor怎样产生实际动作？

先输出分布参数，再按分布采样或评估时选均值等；连续动作还需尺度和环境控制映射。复习：[模型输出](02_network_and_memory.md#forward)、[Microduck动作](04_code_and_reproduction.md#environment)。

<a id="q27"></a>
### Q27 注意力Value和Critic价值是不是一个东西？

不是。注意力V是传递内容的特征向量；Critic价值是未来回报估计。复习：[QKV角色](02_network_and_memory.md#qkv)、[价值定义](03_reinforcement_learning_and_ppo.md#return)。

<a id="q28"></a>
### Q28 QKV为什么能直接乘权重矩阵得到？

线性投影是可训练的表示变换。输入与W都为数组，乘法得到本次QKV；不同W让同一材料承担匹配与内容职责。复习：[矩阵手算](02_network_and_memory.md#qkv)。

<a id="q29"></a>
### Q29 为什么匹配用Q乘K？

点积是可微、高效的一种匹配设计，W通过任务损失学习有用的匹配空间。它不是未经训练就必然理解语义。复习：[点积](02_network_and_memory.md#qkv)。

<a id="q30"></a>
### Q30 相乘结果怎样变成比例？

先得到分数，缩放与屏蔽后经softmax，变成非负、和为1的系数，再加权V。点积本身不是比例。复习：[softmax数值例](02_network_and_memory.md#qkv)。

<a id="q31"></a>
### Q31 QKV的权重怎样优化，改动会影响什么？

最终损失反传到W_Q/W_K/W_V。前两者影响读取匹配，后者影响传递内容；当前注意力系数是计算结果。复习：[参数与系数](02_network_and_memory.md#qkv)。

<a id="q32"></a>
### Q32 为什么注意力后还要前馈网络？

注意力交换信息，FFN对当前位置的组合结果继续非线性加工。它增加表示能力，不保证某个神经元对应固定物理概念。复习：[FFN](02_network_and_memory.md#transformer-layer)。

<a id="q33"></a>
### Q33 不是已经融合历史了吗，为什么还处理？

读取哪些内容与如何把内容转为适合决策的特征，是不同计算。后续层可继续组合和变换，残差保留原有通路。复习：[一层的分工](02_network_and_memory.md#transformer-layer)。

<a id="q34"></a>
### Q34 是不是没有深度学习基础就无法学论文？

先掌握数组、层、参数、损失、链式求导和训练/推理区别，就可理解主线。实现细节按疑问补充，不必先学完所有网络变体。复习：[02第1节](02_network_and_memory.md#tensors)、[03梯度](03_reinforcement_learning_and_ppo.md#autograd)。

## 4. segment、缓存与梯度边界

<a id="q35"></a>
### Q35 segment是存历史的吗，还是最初输入token？

segment先是时间分段概念；原始token、层表示和KV分别是不同计算阶段的数据。历史缓存通常保留处理后的表示或KV。复习：[缓存对象](02_network_and_memory.md#cache)。

<a id="q36"></a>
### Q36 旧segment留着就行，为什么还缓存？

可以保留原数据，但每次重算全部层更费计算。缓存复用已算结果，减少实时开销。复习：[缓存必要性](02_network_and_memory.md#cache)。

<a id="q37"></a>
### Q37 表示缓存和KV缓存有什么区别？

一个保留投影前某层表示，一个保留已投影K/V。论文方法与本地实现的缓存结构不同，不能假定永远保存所有中间状态。复习：[缓存层级](02_network_and_memory.md#cache)。

<a id="q38"></a>
### Q38 已算出KV，旧段是不是能删？

看后续是否还需要旧表示、是否有梯度/重算需求、当前保留策略。只有不再被使用的临时数据才能释放，不能一概删除。复习：[缓存生命周期](02_network_and_memory.md#cache)。

<a id="q39"></a>
### Q39 为什么能参考同一个segment的数据？

当前段内过去位置也是合法历史，通过因果掩码允许读取；后面位置仍屏蔽。复习：[可读矩阵](02_network_and_memory.md#mask)。

<a id="q40"></a>
### Q40 既然能读取同段，分segment有什么意义？

控制计算长度、缓存边界和反向图范围，同时通过段间递归延续历史。不是为了把相邻时刻强行变成独立样本。复习：[分段与SG](02_network_and_memory.md#sg)。

<a id="q41"></a>
### Q41 segment没满怎么办？

采集当前一步立即计算；训练末段可以较短。当前forward要求一次调用不越过配置窗口边界。复习：[边界规则](02_network_and_memory.md#boundaries)。

<a id="q42"></a>
### Q42 为什么采集不能一次输入未来一段？

未来观测还没产生，必须先执行前一步动作。网络能接收已知历史，与能获得未来输入不同。复习：[采集与训练](02_network_and_memory.md#segment)。

<a id="q43"></a>
### Q43 训练输入的segment到底是什么？

是连续保存观测组成的数组及允许历史；动作、旧概率、优势等同步切片，主要在后面计算损失。复习：[输入内容](02_network_and_memory.md#segment)。

<a id="q44"></a>
### Q44 segment一起进去，网络会一起处理吗？

同层多个时间位置可并行，层之间依次执行。因果掩码限制各行读取范围，所以整段输入不等于读取未来。复习：[并行原因](02_network_and_memory.md#segment)。

<a id="q45"></a>
### Q45 segment为什么可以跨Trial？

计算边界不必对齐身体重置。论文同任务多Trial可保留历史，失败经历有机会影响后续控制。复习：[Trial与段](01_paper_and_full_pipeline.md#concepts)。

<a id="q46"></a>
### Q46 segment跨Episode会串任务吗？

应通过Episode编号与注意力掩码隔离。物理数据可以在一个数组段内相邻，允许读取的连接仍可不同。复习：[掩码](02_network_and_memory.md#mask)。

<a id="q47"></a>
### Q47 只参考上一个segment不就够了吗？

当前可直接读近期缓存，但其表示可能已融合更早段。多层间接传播扩展影响范围，既不是只剩纯上段原始数据，也不是无限完整记忆。复习：[记忆范围](02_network_and_memory.md#context-length)。

<a id="q48"></a>
### Q48 SG到底不让哪条梯度通过？

后段损失不能穿过旧缓存回到旧段生成链；当前段自身计算和读取旧数值的参数仍可训练。复习：[两条梯度路径](02_network_and_memory.md#sg)。

<a id="q49"></a>
### Q49 旧段SG以后，后续参数谁更新？

共享参数从每个当前段的损失获得梯度，窗口结束累计后优化器更新；SG不冻结参数。下一轮用新参数重新处理保存序列。复习：[SG与累积](02_network_and_memory.md#sg)。

<a id="q50"></a>
### Q50 损失平均了，窗口之间为什么还传缓存？

平均决定如何汇总训练贡献；缓存决定当前网络能看到什么历史。只相加损失不能代替历史输入。复习：[网络与损失边界](03_reinforcement_learning_and_ppo.md#segment-loss)。

<a id="q51"></a>
### Q51 下一轮优化沿用上一轮最后缓存吗？

当前代码每次ppo从空缓存开始，按顺序重建。否则会把末尾历史放到开头，并可能混用旧参数表示。复习：[边界表](02_network_and_memory.md#boundaries)。

<a id="q52"></a>
### Q52 18秒历史和255步KV为什么不同？

约18秒是论文例子最大可能间接历史影响；255步约5.1秒是近期直接KV保留范围。复习：[范围计算](02_network_and_memory.md#context-length)。

## 5. PPO、Critic、多条数据与多轮优化

<a id="q53"></a>
### Q53 “这不是强化学习吗，怎么像拿旧数据再训练？”

旧数据就是当前策略刚与环境交互得到的经历。奖励通过优势和目标进入损失，训练只是集中在采集之后执行。复习：[强化学习循环](03_reinforcement_learning_and_ppo.md#rl-loop)。

<a id="q54"></a>
### Q54 观测、网络、动作、环境返回一圈，是完整训练吗？

那是一个交互步。要继续采集并执行损失、反传和优化器更新，才涉及参数学习。复习：[完整时间链](03_reinforcement_learning_and_ppo.md#timeline)。

<a id="q55"></a>
### Q55 PPO是不是在降低回报期望？

目标是最大化期望回报。最小化的是相应设计的代理损失，损失数值不等于真实回报期望。复习：[回报与目标](03_reinforcement_learning_and_ppo.md#return)。

<a id="q56"></a>
### Q56 一批数据多大，和segment一样吗？

当前默认12×256个名义位置；segment长16，每窗12×16位置，共16个时间窗。批次决定数据集合，段决定处理分块。复习：[源码时间线](04_code_and_reproduction.md#timeline)。

<a id="q57"></a>
### Q57 参数没变，为什么还要重新前向？

为了获得求梯度所需的当前中间值与计算图。采集no_grad没有保留这条反向图，不是重新找权重关系。复习：[最关键的重算解释](03_reinforcement_learning_and_ppo.md#recompute)。

<a id="q58"></a>
### Q58 第一轮结果相同、比例等于1，为什么还能求梯度？

固定分母的pθ/p_old不是恒等1的pθ/pθ。数值相同不意味着函数对参数不敏感。复习：[比例](03_reinforcement_learning_and_ppo.md#ratio)。

<a id="q59"></a>
### Q59 新概率旧概率，是机器人又运行一遍吗？

旧概率采集时保存，新概率是把保存观测再送当前网络、评价保存动作的密度。不再执行环境动作。复习：[采集与重算](03_reinforcement_learning_and_ppo.md#collection)。

<a id="q60"></a>
### Q60 同批优化4轮，旧概率怎么选？

四轮分母均来自采集该批数据的θ_old。当前参数更新后分子重算，不把上一轮分子替换为新分母。复习：[四轮时间线](03_reinforcement_learning_and_ppo.md#timeline)。

<a id="q61"></a>
### Q61 PPO公式里的ρ、A、clip、负号各是什么？

ρ量化密度变化，A提供表现方向，clip限制有利推动，负号把最大化目标变为最小化损失。复习：[裁剪四例](03_reinforcement_learning_and_ppo.md#clipping)。

<a id="q62"></a>
### Q62 “为什么取较小的？要讲清楚。”

min比较目标，不是已经求好的损失。它让有利变化过大时停止鼓励，不利变化时仍纠正；只用clip会把错误方向也截平。复习：[min的四种情况](03_reinforcement_learning_and_ppo.md#clipping)。

<a id="q63"></a>
### Q63 PPO裁剪是在限制动作或者权重吗？

它改变训练目标，不是动作限幅，也不直接把权重变化限制20%，不硬性保证所有ρ都在区间内。复习：[裁剪边界](03_reinforcement_learning_and_ppo.md#clipping)。

<a id="q64"></a>
### Q64 正负优势怎样让动作概率变化？

在未裁剪区域，损失−ρA；正A鼓励增大ρ，负A鼓励减小ρ。共享参数可能让样本相互影响，不能保证每条都按单独预期改善。复习：[两样本Actor计算](03_reinforcement_learning_and_ppo.md#numerical)。

<a id="q65"></a>
### Q65 一批PPO是不是把所有损失相加？

各有效位置先算，再按N平均；动作维还需按实现归并。不是先平均ρ和A再套min。复习：[损失汇总](03_reinforcement_learning_and_ppo.md#batch)。

<a id="q66"></a>
### Q66 一次到底有多少个损失，跟采集还是segment有关？

数据选择和有效位置数决定监督条目；segment决定分块计算。名义3072不保证全部有效，每位置有Actor、Critic等贡献。复习：[分段平均](03_reinforcement_learning_and_ppo.md#segment-loss)。

<a id="q67"></a>
### Q67 每段backward是不是每段更新参数？

当前入口不是。backward累积梯度，全部窗口后才Adam.step一次；这套说法不能无条件套到别的mini-batch入口。复习：[代码顺序](04_code_and_reproduction.md#ppo-functions)。

<a id="q68"></a>
### Q68 多个关节、多组动作怎样算？

每时间位置一组多维动作。当前默认各维分别算新旧密度比与裁剪，再平均动作维，最后平均有效时间位置。复习：[多维动作](03_reinforcement_learning_and_ppo.md#batch)。

<a id="q69"></a>
### Q69 δ为什么是r＋γV_next−V？

走一步后用实际奖励加下一位置预测估计总结果，再与走前预期比较。下一位置与下一轮更新不是一回事。复习：[TD推导](03_reinforcement_learning_and_ppo.md#td)。

<a id="q70"></a>
### Q70 A_t为什么还加γλA_next？

GAE综合后续TD修正；把展开式的后半段提取出来就得到递推。不是凭空把另一个动作奖励直接混进来。复习：[GAE展开与手算](03_reinforcement_learning_and_ppo.md#gae)。

<a id="q71"></a>
### Q71 R_hat为什么等于A_hat＋旧V，减完又加？

优势是对原预期的修正，修正加回旧预期形成训练目标。λ=1的手算中中间V相消，可直接看见累计奖励。复习：[抵消推导](03_reinforcement_learning_and_ppo.md#value-target)。

<a id="q72"></a>
### Q72 Critic预测是怎么得到的？

当前隐藏表示通过价值分支计算。当前实现先输出回报区间分布，必要时转换成标量估计，不是环境直接给它答案。复习：[Critic两条路径](03_reinforcement_learning_and_ppo.md#critic)。

<a id="q73"></a>
### Q73 Critic怎样用这批数据训练？

保存的奖励与旧V构造固定returns；当前价值输出与其比较，计算HLGauss损失并反传。教学平方误差不能冒充实际调用。复习：[实际Critic](03_reinforcement_learning_and_ppo.md#critic)。

<a id="q74"></a>
### Q74 “收集完经历后修改参数”，具体怎么算？

按计算图用链式法则求各权重梯度，再由优化器更新。两条数据两轮的Actor和Critic数值均在正文算出。复习：[完整手算](03_reinforcement_learning_and_ppo.md#numerical)。

<a id="q75"></a>
### Q75 backward、step、zero_grad有什么区别？

分别计算/累积梯度、更新参数、清空已用梯度。zero_grad不会把训练后的权重清零。复习：[三个操作](03_reinforcement_learning_and_ppo.md#autograd)。

<a id="q76"></a>
### Q76 只有Actor/Critic头更新吗？

共享主干可收到两种损失的梯度，输入编码器也可参与训练。SG只限制旧缓存生成链，不等于冻结主干。复习：[共享梯度](03_reinforcement_learning_and_ppo.md#autograd)。

<a id="q77"></a>
### Q77 损失相加抵消或平均为0，就没有学习了吗？

损失数值与各参数导数不同。即使数值为0，也可能梯度非零；不同样本的梯度也可能部分抵消。复习：[数值与导数](03_reinforcement_learning_and_ppo.md#autograd)。

<a id="q78"></a>
### Q78 “一次所有损失是多少，怎么确定？”

配置确定计算方法、权重与数据组织，具体值由当前网络对当前批次实际计算得出，不能预先由segment长度决定。复习：[损失与数据量](03_reinforcement_learning_and_ppo.md#segment-loss)。

<a id="q79"></a>
### Q79 从最初采集到最后更新的完整时间链？

θ0采D→同D优化4轮θ0至θ4→θ4采D2。每轮16窗累计梯度再一次step，四轮分母都来自θ0。复习：[完整时间线](03_reinforcement_learning_and_ppo.md#timeline)。

<a id="q80"></a>
### Q80 terminal、truncation、segment结束是不是都把未来设0？

不是统一规则。真正终止、采集截断、Trial与Episode边界需分别定义。当前代码合并term/trunc并用~done筛loss，需按实现核验。复习：[实现边界](04_code_and_reproduction.md#audit)。

## 6. 论文证据、代码与下一步

<a id="q81"></a>
### Q81 给出的locoformer就是作者源码吗？

本地元数据与Git来源显示它是lucidrains的第三方实现。可以学习和实验，但不能把其中扩展当作者方法。复习：[来源](04_code_and_reproduction.md#provenance)。

<a id="q82"></a>
### Q82 应先读哪些代码，函数怎样串起来？

train默认值→模型构造→采集→ppo→forward→TransformerXL/Attention。复习：[文件地图](04_code_and_reproduction.md#files)。

<a id="q83"></a>
### Q83 checkpoint中的数字放到哪里？

先按配置建模型，再load_state_dict写到对应参数。当前入口恢复部分统计，未恢复完整Adam、RNG和环境轨迹。复习：[checkpoint边界](04_code_and_reproduction.md#audit)。

<a id="q84"></a>
### Q84 看懂这些是否就能完整复现论文？

还需任务生成范围、奖励权重、统一表示映射、多Trial协议、训练资源与正式评估。能跑示例不等于复现所有论文结果。复习：[复现层级](04_code_and_reproduction.md#reproduction)。

<a id="q85"></a>
### Q85 消融实验是干什么？

在其他条件尽量一致时移除或改变某个因素，检验它的贡献。输入与上下文同时变化的比较不能完全隔离单个原因。复习：[基线解释](01_paper_and_full_pipeline.md#experiments)。

<a id="q86"></a>
### Q86 哪些细节可以先不深挖？

先掌握全流程、边界、输入输出、PPO目标和有效数据；高级缓存扩展、其他PG变体可后置。实际复现时，掩码和重置规则不能因为“属于细节”就跳过。复习：[复现检查](04_code_and_reproduction.md#reproduction)。

<a id="q87"></a>
### Q87 表格0.96是成功率吗？Few-shot每次都更好吗？

不是成功率，是归一化朝目标位移的均值。Spot均值保持1.00，群体均值提升也不保证每次运行改善。复习：[指标](01_paper_and_full_pipeline.md#experiments)。

<a id="q88"></a>
### Q88 怎么把理解转成科研问题？

独立控制任务多样性、上下文长度和跨Trial保留，匹配预算，再比较恢复时间与泛化。不要只重复“模型更强”。复习：[研究问题](01_paper_and_full_pipeline.md#limits)。

<a id="q89"></a>
### Q89 下面所有扩展都必须学完吗？

不需要把参考仓库的所有辅助模型、SPO等扩展当论文先修课。先完成本手册主线，再围绕具体复现需求深入。复习：[入口范围](04_code_and_reproduction.md#ppo-functions)。

<a id="q90"></a>
### Q90 如何以后不再把所有流程搅在一起？

每次先标当前阶段、数据形状、历史边界和参数版本，再解释计算。公式按“要得到什么→输入是什么→每项为何出现→结果给谁用”复习，不从系数背起。见下一节。

## 7. 十分钟快速恢复路线

1. **第1～2分钟**：画01中的训练/部署双流程，说清参数与缓存。
2. **第3～4分钟**：画两个Trial与两个segment，不强行对齐边界。
3. **第5～6分钟**：写出δ、GAE与returns，指出old来自哪次采集。
4. **第7～8分钟**：手算min四例中的一个正优势和一个负优势。
5. **第9～10分钟**：复述12×256采集、16窗、4轮更新，并说出这是第三方默认值。

## 8. 三个必须能脱稿回答的流程题

### 流程题一：为什么采集逐步输入，训练整段输入？

采集未来观测尚未产生，要先执行当前动作；训练数据已保存，可以并行处理同层多个位置，因果掩码限制未来读取。缓存连接段间历史。

### 流程题二：奖励怎样改动一个权重？

环境奖励→旧价值构造优势/回报目标→当前网络重新前向→Actor/Critic损失→链式法则得到各权重梯度→优化器更新。环境不用可微，奖励也不是正确角度标签。

### 流程题三：SG后为什么仍能适应和学习？

旧缓存数值仍影响当前输出，所以可利用历史；当前段计算与共享权重仍有梯度，所以可训练。SG截断的是穿过旧生成链的反传。

## 9. 论文与汇报页对应

| 汇报部分 | 学习文档 | 最应讲清的理解 |
|---|---|---|
| 问题与总流程 | 01第1～3、7节 | 训练改参数，部署利用历史 |
| 任务和跨Trial组织 | 01第4～6节 | 身体重置与信息边界不同 |
| 网络与段间记忆 | 02 | 并行、因果掩码与SG分工 |
| PPO | 03 | 旧参照固定、重算求梯度 |
| 实验与局限 | 01第8～10节 | 指标含义、比较边界、可检验问题 |
| 代码补充 | 04 | 参考实现与原论文配置不能混用 |

复习时先找到Q编号，再回正文核对一个例子。若仍无法解释，不必从整套资料重读，应定位究竟混淆了数据、历史、目标还是参数。
