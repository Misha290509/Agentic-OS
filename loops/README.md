# Loops

Loop specs are behavioral contracts for iterative work. Every spec defines:
**entry criteria** (when to use it), **per-iteration steps**, a **verification
step** (every iteration ends by checking reality, not by assuming), **exit
criteria** (success and abort), **max iterations**, and **checkpointing**
(where state lives between iterations so any session can resume).

| Loop | Use for | Max iters |
|---|---|---|
| [`build-test-fix-loop.md`](build-test-fix-loop.md) | Getting code to green | 5 |
| [`research-loop.md`](research-loop.md) | Open-ended questions needing sources | 4 |
| [`draft-review-revise-loop.md`](draft-review-revise-loop.md) | Writing that matters | 3 |
| [`triage-loop.md`](triage-loop.md) | Classifying a pile of unstructured items | batch-based |

## Rules common to all loops

1. **Checkpoint before you act, not after.** Each iteration starts by writing
   its intent to the checkpoint file — a crash mid-iteration then loses work,
   not knowledge.
2. **Register the loop** in `state/open-loops.json` on entry; remove it on
   clean exit. Schema in `state/open-loops.example.json`.
3. **Never repeat a failed attempt unchanged.** The checkpoint file's attempt
   log exists to prevent thrashing.
4. **Hitting max iterations is a result, not a failure to hide.** Stop, leave
   the checkpoint, report what was tried and what remains.
