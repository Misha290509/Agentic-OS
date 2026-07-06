# Loop: research

**Entry criteria:** An open-ended question where the answer isn't known upfront
and needs evidence: "which netcode library fits us?", "why is loading slow on
Windows?", "what do competitors charge?"

**Max iterations:** 4 (each iteration is one question-refinement cycle).

**Checkpoint file:** `state/research-<slug>.md`

```markdown
---
loop: research
question: <the question as currently understood>
started: <ISO timestamp>
iteration: <n>
---
## Findings so far
- <claim> — source: <file/URL/experiment>  — confidence: high/med/low

## Open sub-questions
- <what's still unknown>

## Dead ends
- <line of inquiry> — why abandoned
```

## Per-iteration steps

1. **Checkpoint** — restate the question (it usually sharpens each iteration)
   and pick the 1–3 sub-questions this iteration will attack.
2. **Gather** — search code, docs, the vault (`30-resources` first — past
   research may already answer this), the web, or run a small experiment.
3. **Record findings with sources.** A claim without a source goes in as
   confidence: low.
4. **Verify** — challenge the strongest finding: does a counter-example exist?
   Does a second source agree?
5. **Re-plan** — update open sub-questions; move exhausted lines to Dead ends.

## Exit criteria

- **Success:** the question is answered with ≥2 independent sources for the
  load-bearing claims, or a decision can be made and defended. Write the final
  answer to `vault/30-resources/research/<slug>.md` (frontmatter per
  convention), delete the checkpoint, close the open-loop entry.
- **Abort:** iterations exhausted or the question turns out ill-posed →
  write up partial findings to the same vault location marked `status: partial`.

## Verification step

Before exiting: re-read the final answer and strike any sentence you cannot
point to a source or experiment for.
