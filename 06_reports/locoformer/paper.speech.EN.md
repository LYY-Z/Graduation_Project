# LocoFormer — Presentation Script

Corresponding slides: [English presentation](paper.EN.pptx). Slides 1–12 form the main presentation, planned for approximately 10 minutes. Slides 13–14 are hidden appendices for discussion. The text below matches the spoken portion of each slide's speaker notes; headings and timing labels are not intended to be read aloud.

## Slide 1: LocoFormer — 20 seconds

Today I will present LocoFormer. The paper studies how one policy can control robots with different bodies and adapt its behavior when physical conditions change.

I will cover the control problem, the method and the experiments, focusing on how interaction history informs control and how this ability is learned.

## Slide 2: The Challenge of Cross-Embodiment Control — 45 seconds

First, why is control across different robot bodies difficult?

Robots differ in joint structure, mass and actuation. The same joint target can therefore produce different physical responses. An action that is stable on one robot may not work on another.

The current observation may also be insufficient to explain a deviation. A tilted body could result from a brief disturbance or from reduced actuation in one leg. Earlier actions and responses provide additional evidence.

The paper addresses two connected requirements: controlling diverse bodies and using interaction history to keep adapting. The next slide shows the overall approach.

## Slide 3: Method Overview: Training and Deployment — 50 seconds

The upper row shows training. The authors generate robot bodies and control conditions, then let the policy interact with a simulator. The simulator produces responses and rewards, and the program stores the resulting experience. PPO constructs losses, computes gradients and updates the network. The updated policy then collects new experience.

The lower row shows deployment. Trained weights remain fixed. The network combines the current observation with history to select an action, and the resulting physical response informs subsequent control.

Training changes the weights through rewards. Deployment adapts actions through changing history. To understand this distinction, we first need to examine how training experience is organized.

## Slide 4: Training Tasks: Diverse Bodies and Repeated Trials — 60 seconds

The training experience has two important design choices.

First is task diversity. Procedurally generated bipeds, quadrupeds and wheeled robots vary in joint structure, mass, inertia and control gains. A unified joint representation lets one network handle these different bodies and select the relevant joint outputs.

Second is repeated interaction within a task. One continuous rollout is called a trial. A group of trials in the same task forms an episode. The body can reset between trials while the policy retains history, allowing later attempts to use earlier responses and failures.

In practice, training samples an adaptation time budget, allows trials within it, and then runs a final trial. The formal objective concerns discounted return across the group. Training starts with shorter trials and budgets, then extends both. Next, we examine how the network turns this experience into actions.

## Slide 5: Control Network: Observations, History and Actions — 50 seconds

Following the arrows, an MLP first encodes the current observation. Transformer-XL combines this representation with history to compute the current features.

The network then has two branches. The Actor produces an action distribution and selects an action, yielding joint targets for the current robot. The Critic predicts future return to support training.

Joint targets still pass through the controller and physical body before producing motion. If a joint responds less than expected, this discrepancy can reveal changes in actuation or load. Subsequent observations carry that evidence into history.

History is useful because it retains physical feedback. The next slide explains how the network stores and reads it.

## Slide 6: Historical Memory: Segments and Caching — 65 seconds

A trial is a physical rollout, whereas a segment is a block of network computation along time. Their boundaries do not have to coincide.

During collection, an action must be executed before the next observation becomes available. During training, observations are already stored, so a segment can be processed with parallel computation across positions.

The causal mask prevents this parallel processing from using future information. For example, the second position can read the first and itself, but not the third.

Caches carry features between segments. In attention, Q queries, K matches and V supplies content. Stop-gradient blocks backpropagation into the process that generated old features, but preserves their numerical influence on current computation. The current segment remains trainable.

This allows longer history at a manageable training cost. Rewards must then teach the policy how to use that history.

## Slide 7: Policy Training: Rewards and PPO Updates — 70 seconds

This slide explains the standard PPO mechanism. The paper uses PPO but does not disclose every training detail, so these equations illustrate the underlying logic.

On the left, collected actions are evaluated. The first equation compares a one-step updated evaluation with the previous expectation. The second incorporates later feedback to form an advantage. The third constructs a return target for the Critic.

On the right, these evaluations train the current network. Positive advantage encourages actions of this kind to become more likely; negative advantage encourages the opposite. PPO clipping curbs excessive favorable updates. The Critic learns to predict the constructed return target.

Stored observations are processed again to build the computation graph needed for gradients, not to execute the actions again. Losses are aggregated, gradients are backpropagated and the optimizer updates the weights. A batch can support several optimization epochs before collecting new experience.

After this training, deployment can keep the weights fixed.

## Slide 8: Deployment: Fixed Weights, Growing History — 50 seconds

During deployment, each observation is processed with the available history. Previously computed keys and values are cached for efficient continuous control. The weights stay fixed, but changing history allows the actions to change with the body's responses.

Zero-shot evaluation begins directly, while history still accumulates within the trial. Few-shot evaluation allows extra interaction first: five seconds in this simulation comparison. Later trials can retain the preceding experience.

The two memory ranges on the right describe different things. Recent directly retained KV covers about 5.1 seconds. Earlier information can also pass indirectly through layers, giving a maximum possible influence span of about 18 seconds in the paper's example. This does not guarantee complete recall.

Next, we test transfer to robots absent from training.

## Slide 9: Simulation: Transfer to Unseen Robots — 50 seconds

The authors evaluate ten unseen robots, with one thousand randomized environments for each. The metric is normalized displacement toward a goal, so a score of 0.96 is not a 96 percent success rate.

LocoFormer scores 0.96 in zero-shot evaluation and 0.98 after five seconds of interaction, close to the specialist policy's 0.99.

The baselines need to be interpreted with their settings. GRU uses the same training setup and performs worse, supporting the importance of memory architecture. Conditioning receives privileged body information but uses only 64 history steps, so that comparison changes both inputs and context length.

These results show transfer performance. We next examine whether additional interaction produces adaptation benefits.

## Slide 10: Adaptation: What Does Interaction Improve? — 50 seconds

These figures examine adaptation through behavior and internal features.

On the left, randomization ranges are doubled. Different adaptation budgets are followed by a six-second survival evaluation. More interaction generally improves survival, although the curves fluctuate and gains can saturate.

On the right, features from four body variants begin close together and progressively separate, forming clearer groups after about five seconds. This supports the presence of body-related information in the features, but does not establish exact identification of mass or inertia.

Together, the figures support the policy's use of interaction information. The final experimental question is whether this ability transfers to real robots.

## Slide 11: Real Robots: Adapting to Body Changes — 50 seconds

The same model is deployed on G1, H1, Go2 and Go2-W without target-platform fine-tuning.

The examples include locked joints or legs, changed wheel actuation, added payloads and altered leg lengths. These changes affect support, dynamics or actuation, requiring control to adjust.

Example B most directly illustrates memory across trials. After retaining earlier failed-trial experience, control improves and stable walking is achieved on the third attempt in this example. It does not mean every failure can be resolved within three trials.

These demonstrations show practical potential. Recovery rates and times across different changes still require systematic evaluation. I will finish with the method's main contributions and follow-up questions.

## Slide 12: Conclusions and Further Evaluation — 40 seconds

The paper connects three designs. Diverse tasks expose different control conditions. Long history retains physical responses and failed-trial experience. PPO trains the policy to use that information when choosing actions.

Further evaluation could compare memory lengths under matched data and compute budgets. It could also retain or clear history between trials and measure recovery time and failure rate.

Reproducing the method therefore requires task generation, history organization and the training procedure, rather than only implementing a Transformer network.

Thank you. I welcome your comments.

---

## Slide 13: Appendix A: PPO Clipping and Batch Loss — discussion, approximately 60 seconds

This slide explains the new-to-old likelihood ratio and the minimum in PPO.

The ratio compares the probability density of the same collected action under the current policy and the collection policy. The stored old density stays fixed during batch optimization, while the current density changes with the weights.

In the first row, positive advantage indicates a result above the previous expectation. At a ratio of 1.4, the raw objective keeps increasing, while the clipped objective stops at 1.2. Taking the minimum stops rewarding further increase for this sample.

In the second row, the favorable action has instead become less likely. The minimum retains the raw objective, preserving a corrective gradient. The negative-advantage rows follow the same principle. The leading minus sign converts the maximization objective into a loss to minimize.

Losses are averaged over valid positions. Clipping acts on the training objective; it is not a physical safety limit and does not strictly bound every likelihood ratio.

## Slide 14: Appendix B: Collection and Update Timeline — discussion, approximately 60 seconds

This slide uses the third-party Microduck example to illustrate implementation, not the authors' complete training configuration.

Twelve environments each collect 256 steps, producing 3,072 time positions. Training uses segments of 16 steps across all twelve environments, giving sixteen segments along time.

Within an optimization epoch, weights remain unchanged while each segment computes outputs, losses and accumulated gradients. One optimizer update follows all segments. These segments organize computation; they do not represent sixteen new physical rollouts.

The same batch is optimized for four epochs. Old action densities always come from the original collection policy; current densities change after updates. The new policy then collects the next batch.

This implementation uses Beta actions and an HLGauss value loss. The actual loss count depends on validity masks, rather than automatically including all 3,072 positions.
