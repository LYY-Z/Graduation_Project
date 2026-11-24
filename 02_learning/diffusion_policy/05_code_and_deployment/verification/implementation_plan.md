# Public Repository Refactoring Implementation Plan

> Execution: inline implementation with focused parallel documentation and a final independent review. User explicitly authorized copying and executing the already discussed design; no further design approval is required.

**Goal:** preserve the verified original project, refactor a separately copied project, and deliver public-facing documentation plus detailed Chinese learning material.
**Architecture:** hardware, inference and control subpackages; shared config/geometry/recording and pipeline; original upstream and private SDK retained with provenance.
**Tech stack:** Python 3.9, NumPy, PyYAML, ROS 2 system Python, original PyTorch 1.12.1 inference stack, ur_rtde 1.6.5.
**Spec:** G:/毕设/02_learning/diffusion_policy/05_deployment/05_code_organization_plan.md and latest user-approved three-subpackage structure.

## Global constraints
- Preserve G:/毕设/03_code/diffusion_policy_ur7e byte-for-byte; target G:/毕设/03_code/diffusion_policy_ur7e_refactored.
- No SSH, no server changes, no robot commands, no model inference on the local computer.
- Keep original model architecture, checkpoint, EMA, normalizer, sampling schedule, action indexing, image processing, coordinate semantics and numeric control limits.
- Default/help/inspect/tests must not initialize robot control. Execute requires explicit site/TCP declarations.
- Preserve ROS/inference process separation, causal timestamp logic, bounded non-retrying private backend semantics and cleanup.
- Project-facing docs objective and self-contained; personal learning notes remain outside the public repository.
- No invented hardware validation, task success, authorship, publication metadata or software license choice.

## Review focus
- Relocated root calculations and private binary/source manifest paths.
- Read-only commands accidentally importing or creating control SDK clients.
- Merged modules/circular imports changing image handling or controller readout.
- CLI flags silently bypassing physical execution prerequisites.
- Public data/configuration leaking local paths/credentials or claiming unverified task performance.

## Tasks
- [x] 1. Snapshot source, verify copy, run preserved tests in copy and record baseline.
- [x] 2. Add failing tests for target module layout, public configuration, command dispatch, backend manifest relocation, and hardware-free behavior.
- [x] 3. Reorganize sources, use one shared prediction wrapper, unify dispatch, relocate upstream/SDK with checks; run old and new tests.
- [x] 4. Parameterize preparation/build/deployment tools and provenance; retain original SDK patch. Verify packaging, syntax, private backend behavior and source/functional equivalence.
- [x] 5. Write public README/technical guide/report and detailed Chinese learning chapters; verify commands, links, terminology and evidence.
- [x] 6. Independent review; fix material findings with regression tests. Rehash original, record acceptance and hardware/model checks not run. No publishing.

## Validation commands
- Baseline and final: Python 3.9 + isolated existing local dependency directory; pytest -q -p no:cacheprovider.
- Changed Python: compileall without hardware/model imports; package wheel/sdist when build tools available.
- Equivalence: normalized AST for unmodified critical methods and deterministic differential camera/observations/mapping/filter fixtures against original.
- Public CLI: subprocess help/inspect/preflight failures with network/model/control import guards.
- Native control: preserve SDK source hashes/patch; compile and run loopback transport test only if local compiler/Boost permits, otherwise explicitly mark not run.
- Documentation: resolve local links; commands checked against parser; no unsupported task-success claim.


