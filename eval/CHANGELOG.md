# Eval Changelog

One entry per prompt-improvement iteration (see the workflow in the testing
plan) and per monthly production spot-check. Keep entries short: date, what
changed, before/after metrics, decision.

## 2026-07-17 — Eval infrastructure built, baseline sample dataset created

- Built `eval/run_eval.py` (accuracy harness), `eval/build_dataset.py`
  (dataset builder), `eval/monitor_drift.py` (production drift check),
  and the pytest suite in `tests/`.
- Sourced 12 real, pre-2020 human AITA posts from the public
  `Oguzz07/reddit-amitheasshole-dataset` (Hugging Face) as
  `eval/data/human_seed.jsonl` — avoids post-2022 authorship ambiguity.
  Known gap: this source skews long-form (median ~467 words); it has no
  genuinely terse (<80 word) or non-native-English examples, so the
  `terse` and `non_native` fairness tags are currently unrepresented in
  the sample set. Worth sourcing a second, terser source (e.g.
  r/tifu or r/TrueOffMyChest, both of which the bot actually monitors)
  before trusting fairness-slice numbers on those tags.
- Wrote 12 matched AI-authored counterparts by hand (`eval/data/ai_seed.jsonl`)
  since `ANTHROPIC_API_KEY` was not yet set in `.env` at build time — mixed
  6 "generic" (no attempt to sound human) and 6 "well-disguised" (deliberately
  casual/contraction-heavy) style, per the plan's guidance that well-disguised
  AI text is the harder, more realistic case. `eval/build_dataset.py` is
  ready to generate further examples via the real API once the key is set.
- Combined into `eval/data/sample_labeled_posts.jsonl` (24 examples,
  12 human / 12 ai) and committed it (small enough to check in; the full
  local-only dataset stays gitignored per `eval/data/*.jsonl`).

**Baseline run result (fallback heuristic only — no API key set yet):**

| Metric | Value |
|---|---|
| Fallback rate | 100% (expected — no key) |
| Suspicious framing (🟡/🔴 = AI) | precision=0.50, recall=0.75, f1=0.60 |
| Confident framing (only 🔴 = AI) | precision=0.50, recall=0.67, f1=0.57 |
| False-positive rate, formulaic humans | 66.7% |
| False-positive rate, no_contractions humans | 66.7% |
| False-positive rate, untagged humans | 83.3% |

The old hand-tuned heuristic fallback flags **most real human AITA posts as
AI-generated** — barely better than a coin flip on precision, and a false-
positive rate as high as 83% on ordinary human writers. This is the exact
problem the LLM-judge rebuild (`ai_judge.py`, commit `93026ad`) was meant to
fix. **Next step: set a real `ANTHROPIC_API_KEY` in `.env` and re-run
`python eval/run_eval.py` to get the actual judge-based baseline** — this
heuristic-only number is not representative of production behavior once the
key is set, but it's a useful sanity check that the harness and fairness
slicing work correctly end-to-end.

## 2026-07-17 — Closed the terse/non-native gap in the sample dataset

- Added 6 genuine terse human posts (28–73 words) from r/tifu, sourced from
  `dany0407/reddit_tifu_short` on Hugging Face — a mirror of the canonical
  academic `reddit_tifu` dataset (Kim et al. 2019, posts from 2013–2018, so
  definitively pre-LLM). Note: the original preprocessing lowercased all
  text; that's authentic-looking for casual Reddit writing and shouldn't
  bias the judge, but it's worth knowing the casing isn't the authors' own.
  Two of the six carry clear non-native-English markers and are tagged
  `non_native`; all six are tagged `terse`. Files: `human_seed_tifu.jsonl`.
- Wrote 6 matched terse AI counterparts (3 generic LLM-styled, 3 disguised
  casual-lowercase) in `ai_seed_tifu.jsonl`, and rebuilt
  `sample_labeled_posts.jsonl` — now **36 examples (18 human / 18 ai)** with
  every fairness tag represented: terse (6), formulaic (3),
  no_contractions (3), non_native (2).

**Expanded fallback-only baseline (still no API key):**

| Metric | Value |
|---|---|
| Suspicious framing (🟡/🔴 = AI) | precision=0.50, recall=0.72, f1=0.59 |
| Confident framing (only 🔴 = AI) | precision=0.455, recall=0.556, f1=0.50 |
| FP rate: terse humans | 66.7% |
| FP rate: non_native humans | 50.0% |
| FP rate: formulaic humans | 66.7% |
| FP rate: no_contractions humans | 66.7% |
| FP rate: untagged humans | 83.3% |

Same story as the first run, now with the previously-missing writer groups
covered: the heuristic fallback is at coin-flip precision and flags half to
four-fifths of real human writers in every category. The judge-based
baseline (once the key is set) is the number that matters.

---

## Monthly production spot-checks

(Log entries here once the bot has live traffic — see the monitoring section
of the testing plan: pull ~20 recent `user_log.log` entries, manually
re-judge them, compare against the bot's logged verdict.)
