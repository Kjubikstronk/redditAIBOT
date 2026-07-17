"""
Lightweight production drift check — no ground truth required. Reuses
log_parser.calculate_stats() (the same function the dashboard calls) to get
daily verdict counts from user_log.log, then compares the trailing 7-day
🔴 (Potentially AI-Generated) share against the prior 30-day baseline.

A spike either means a real influx of AI content in the monitored
subreddits, or an accuracy regression (e.g. after a model update or a
prompt edit) — investigate by reading the `[LLM JUDGE] ... Reasoning: ...`
lines in bot_debug.log for recent 🔴 verdicts before re-running the full
eval harness.

Run manually whenever you check the dashboard — no cron/paging needed given
the bot's low, cooldown-gated trigger volume.

Usage:
    python eval/monitor_drift.py
    python eval/monitor_drift.py --threshold 2.5
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import log_parser  # noqa: E402

RED = "🔴 Potentially AI-Generated"
VERDICTS = ["🟢 Likely Human", "🟡 Possibly AI-Generated", RED]


def daily_red_share(trends: dict):
    """Returns a list of (date, total, red_share) for each day with any
    verdicts, oldest first."""
    labels = trends.get("labels", [])
    datasets = trends.get("datasets", {})
    out = []
    for i, date in enumerate(labels):
        total = sum(datasets.get(v, [0] * len(labels))[i] for v in VERDICTS)
        red = datasets.get(RED, [0] * len(labels))[i]
        if total > 0:
            out.append((date, total, red / total))
    return out


def check_drift(daily, recent_days=7, baseline_days=30, threshold=2.0):
    """
    Compares the trailing `recent_days`-window red-share against the
    `baseline_days` window immediately preceding it. Returns a report dict.
    Requires enough history in both windows; otherwise reports as
    insufficient-data rather than guessing.
    """
    if len(daily) < recent_days + 5:
        return {"status": "insufficient_data", "days_available": len(daily)}

    recent = daily[-recent_days:]
    baseline_start = max(0, len(daily) - recent_days - baseline_days)
    baseline = daily[baseline_start:-recent_days]

    if not baseline:
        return {"status": "insufficient_data", "days_available": len(daily)}

    recent_total = sum(t for _, t, _ in recent)
    recent_red = sum(t * s for _, t, s in recent)
    recent_share = recent_red / recent_total if recent_total > 0 else 0.0

    baseline_total = sum(t for _, t, _ in baseline)
    baseline_red = sum(t * s for _, t, s in baseline)
    baseline_share = baseline_red / baseline_total if baseline_total > 0 else 0.0

    ratio = (recent_share / baseline_share) if baseline_share > 0 else (float("inf") if recent_share > 0 else 1.0)
    flagged = ratio >= threshold or ratio <= (1 / threshold if threshold > 0 else 0)

    return {
        "status": "ok",
        "recent_share": recent_share,
        "recent_n": recent_total,
        "baseline_share": baseline_share,
        "baseline_n": baseline_total,
        "ratio": ratio,
        "flagged": flagged,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--recent-days", type=int, default=7)
    parser.add_argument("--baseline-days", type=int, default=30)
    parser.add_argument("--threshold", type=float, default=2.0,
                         help="Flag if the recent/baseline red-share ratio exceeds this (or its inverse)")
    args = parser.parse_args()

    stats = log_parser.calculate_stats()
    daily = daily_red_share(stats.get("verdict_trends", {}))

    if not daily:
        print("No trigger data found in user_log.log yet — nothing to check.")
        return

    result = check_drift(daily, args.recent_days, args.baseline_days, args.threshold)

    if result["status"] == "insufficient_data":
        print(f"Only {result['days_available']} day(s) of trigger data available — "
              f"need at least {args.recent_days + 5} to compare recent vs. baseline. "
              "Check back once the bot has more history.")
        return

    print(f"Recent {args.recent_days}-day 🔴 share: {result['recent_share']:.1%} (n={result['recent_n']})")
    print(f"Baseline {args.baseline_days}-day 🔴 share: {result['baseline_share']:.1%} (n={result['baseline_n']})")
    print(f"Ratio: {result['ratio']:.2f}x")

    if result["flagged"]:
        print(f"\n⚠️  FLAGGED: recent 🔴 share deviates from baseline by >= {args.threshold}x.")
        print("Either a real influx of AI content, or an accuracy regression. Investigate by reading")
        print("recent [LLM JUDGE] reasoning lines in bot_debug.log before re-running eval/run_eval.py.")
    else:
        print("\nNo significant drift detected.")


if __name__ == "__main__":
    main()
