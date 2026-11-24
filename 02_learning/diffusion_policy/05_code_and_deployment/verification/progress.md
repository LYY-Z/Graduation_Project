# Refactoring ledger — plan: G:/毕设/02_learning/diffusion_policy/05_code_and_deployment/verification/implementation_plan.md

## Scope decisions

- Ruling: use a standalone filesystem copy rather than a linked worktree — the user explicitly requested a copy and the original contains verified uncommitted changes. Original source and Git state were not rewritten; the cost is an independent local repository instead of shared history.
- Ruling: preserve the patched SDK byte-for-byte and retain its original diff as provenance; do not apply the patch twice — minimizes transport behavior changes. A Linux build and hardware revalidation remain required.
- Ruling: no SSH, real model loading/inference, ROS startup or physical commands this turn — user stated those validation conditions are unavailable. Offline results cannot establish target-machine or physical acceptance.
- Ruling: keep the new local branch and do not merge/push/publish — public release is a later project action. Software-license and authorship decisions remain with maintainers.
- Ruling: shadow latency now includes the shared prediction wrapper's conversion/synchronization scope — avoids duplicate inference implementations. Comparisons with historical latency must use matching timing definitions.

## Completed tasks

- Task 1: complete — 1138 non-cache original files hashed and copied; baseline 105 passed, 5 ROS skips.
- Task 2: complete — public-interface tests observed 9 failures before implementation, then green.
- Task 3: complete — grouped 12 business files/17 package Python files; original regression assertions migrated; no legacy module wrappers.
- Task 4: complete — parameterized environment/build/deploy tools; 369 upstream and 339 SDK source files preserved; wheel built and imported independently; 708 locked Git blobs verified. Linux native build/loopback remains unexecuted.
- Task 5: complete — public README/guide/English report plus validation JSON; six Chinese learning chapters and index. Local links and Python examples checked. Copied historical materials moved to G:/毕设/99_archive/ur7e_refactor_legacy_20261026, outside public source.
- Artifact correction: fixed omission of five locked SDK sdist egg-info files from deployment selection. Regression test observed RED then GREEN.
- Final independent review: read-only reviewer, no Critical findings, one Important finding, no Minor findings. Reviewer ran 127 passed, 5 ROS skips before the fix.
- Final fix: candidate backend manifest is import-probed before atomic activation; failed probe preserves an existing manifest or first-build absence. Three transactional tests observed RED then GREEN; candidate-path boundary also tested.
- Task 6: complete — final full suite 131 passed, 5 ROS skips; Ruff clean; critical AST definitions 38 identical; 533 deterministic differential cases matched; wheel built and import/resource probe passed; original 1138 files remain unchanged.
- Final Git: ac98a2b33692afc7cb8b72d713c37f4c66a907fe on refactor/public-layout; no remote configured, no public upload.
- Deferred minors: none from the independent review.
- Deferred execution coverage: ROS lifecycle, Linux dependency solve/native compilation, actual neural inference, physical hardware, hosted CI. These are not reported as passed.

