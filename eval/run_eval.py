"""
Accuracy-evaluation harness for the Reddit AI-detection bot.

Loads a labeled dataset (eval/data/labeled_posts.jsonl by default), runs each
example through bot.format_detection_results — the exact function the live
bot and test_mode use — and reports real precision/recall/F1 against the true
labels, plus a fairness-slice breakdown for false positives on human writers
tagged as "hard" cases (terse, non-native English, formulaic, etc).

This replaces test_mode's old "batch test", which only tallied the bot's own
verdicts against nothing and never compared to a ground-truth label.

Usage:
    python eval/run_eval.py
    python eval/run_eval.py --dataset eval/data/sample_labeled_posts.jsonl
"""
import argparse
import json
import os
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

# Windows consoles default to a legacy codepage (cp1252) that can't encode the
# emoji verdict strings this script prints — reconfigure stdout to UTF-8 so
# `python eval/run_eval.py` doesn't crash mid-report on Windows.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from bot import format_detection_results  # noqa: E402

VERDICT_TO_SUSPICIOUS = {
    "🟢 Likely Human": False,
    "🟡 Possibly AI-Generated": True,
    "🔴 Potentially AI-Generated": True,
}
VERDICT_TO_CONFIDENT_AI = {
    "🟢 Likely Human": False,
    "🟡 Possibly AI-Generated": False,
    "🔴 Potentially AI-Generated": True,
}
ALL_VERDICTS = list(VERDICT_TO_SUSPICIOUS.keys())

CONFIDENCE_BUCKET_EDGES = [(0.0, 0.3), (0.3, 0.6), (0.6, 0.85), (0.85, 1.01)]


def load_dataset(path: str):
    records = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def run(dataset_path: str, skip_account: bool = True):
    """
    Runs every example in the dataset through format_detection_results and
    returns a list of result dicts (input record + prediction fields).
    """
    records = load_dataset(dataset_path)
    results = []
    for record in records:
        text = (record.get("title", "") + "\n" + record.get("selftext", "")).strip()
        report, verdict, confidence = format_detection_results(
            text, author=None, skip_account=skip_account
        )
        used_fallback = "fallback heuristic" in report
        results.append({
            **record,
            "predicted_verdict": verdict,
            "confidence": confidence,
            "used_fallback": used_fallback,
        })
    return results


def _precision_recall_f1(tp: int, fp: int, fn: int):
    precision = tp / (tp + fp) if (tp + fp) > 0 else None
    recall = tp / (tp + fn) if (tp + fn) > 0 else None
    if precision is not None and recall is not None and (precision + recall) > 0:
        f1 = 2 * precision * recall / (precision + recall)
    else:
        f1 = None
    return {"precision": precision, "recall": recall, "f1": f1, "tp": tp, "fp": fp, "fn": fn}


def _framing_metrics(results, positive_map):
    tp = fp = fn = 0
    for r in results:
        predicted_positive = positive_map.get(r["predicted_verdict"], False)
        is_ai = r["label"] == "ai"
        if predicted_positive and is_ai:
            tp += 1
        elif predicted_positive and not is_ai:
            fp += 1
        elif not predicted_positive and is_ai:
            fn += 1
    return _precision_recall_f1(tp, fp, fn)


def _confusion_matrix(results):
    cm = {v: {"human": 0, "ai": 0} for v in ALL_VERDICTS}
    for r in results:
        verdict = r["predicted_verdict"]
        label = r["label"]
        if verdict in cm and label in ("human", "ai"):
            cm[verdict][label] += 1
    return cm


def _confidence_buckets(results):
    buckets = {}
    for lo, hi in CONFIDENCE_BUCKET_EDGES:
        key = f"{lo:.2f}-{hi:.2f}"
        bucket_results = [
            r for r in results
            if r.get("confidence") is not None and lo <= r["confidence"] < hi
        ]
        n = len(bucket_results)
        if n == 0:
            buckets[key] = {"n": 0, "accuracy": None}
            continue
        correct = sum(
            1 for r in bucket_results
            if (r["label"] == "ai") == VERDICT_TO_SUSPICIOUS.get(r["predicted_verdict"], False)
        )
        buckets[key] = {"n": n, "accuracy": correct / n}
    return buckets


def _fairness_slice(results):
    """False-positive rate on true-human examples, grouped by `notes` tag.
    Untagged human examples are reported separately under "untagged"."""
    groups = defaultdict(lambda: {"n": 0, "false_positives": 0})
    for r in results:
        if r["label"] != "human":
            continue
        tags = r.get("notes") or []
        keys = tags if tags else ["untagged"]
        is_fp = VERDICT_TO_SUSPICIOUS.get(r["predicted_verdict"], False)
        for key in keys:
            groups[key]["n"] += 1
            if is_fp:
                groups[key]["false_positives"] += 1
    return {
        key: {
            "n": g["n"],
            "false_positive_rate": g["false_positives"] / g["n"] if g["n"] > 0 else None,
        }
        for key, g in groups.items()
    }


def compute_metrics(results):
    n = len(results)
    fallback_count = sum(1 for r in results if r.get("used_fallback"))
    return {
        "n": n,
        "confusion_matrix": _confusion_matrix(results),
        "suspicious_framing": _framing_metrics(results, VERDICT_TO_SUSPICIOUS),
        "confident_framing": _framing_metrics(results, VERDICT_TO_CONFIDENT_AI),
        "confidence_buckets": _confidence_buckets(results),
        "fallback_rate": (fallback_count / n) if n > 0 else None,
        "fairness_slice": _fairness_slice(results),
    }


def print_report(metrics: dict):
    print(f"\n=== Eval run: {metrics['n']} examples ===\n")

    if metrics["fallback_rate"]:
        print(f"⚠️  Fallback-heuristic rate: {metrics['fallback_rate']:.1%} "
              f"(should be ~0% with a valid ANTHROPIC_API_KEY — non-zero is a bug signal)\n")

    print("Confusion matrix (predicted x true):")
    for verdict, counts in metrics["confusion_matrix"].items():
        print(f"  {verdict}: human={counts['human']}, ai={counts['ai']}")

    def fmt(m):
        def f(x):
            return f"{x:.3f}" if x is not None else "n/a"
        return f"precision={f(m['precision'])} recall={f(m['recall'])} f1={f(m['f1'])} " \
               f"(tp={m['tp']} fp={m['fp']} fn={m['fn']})"

    print(f"\nSuspicious framing (🟡 or 🔴 = predicted AI): {fmt(metrics['suspicious_framing'])}")
    print(f"Confident framing (only 🔴 = predicted AI):   {fmt(metrics['confident_framing'])}")

    print("\nConfidence-bucketed accuracy:")
    for bucket, stats in metrics["confidence_buckets"].items():
        acc = f"{stats['accuracy']:.1%}" if stats["accuracy"] is not None else "n/a"
        print(f"  {bucket}: n={stats['n']}, accuracy={acc}")

    print("\nFairness slice — false-positive rate on true-human examples by notes tag:")
    for tag, stats in sorted(metrics["fairness_slice"].items()):
        rate = f"{stats['false_positive_rate']:.1%}" if stats["false_positive_rate"] is not None else "n/a"
        print(f"  {tag}: n={stats['n']}, false_positive_rate={rate}")
    print()


def main():
    parser = argparse.ArgumentParser(description="Evaluate the bot's detection accuracy against a labeled dataset.")
    parser.add_argument("--dataset", default="eval/data/labeled_posts.jsonl")
    parser.add_argument("--out", default=None, help="Output results JSON path (default: eval/results/<timestamp>.json)")
    args = parser.parse_args()

    if not os.path.exists(args.dataset):
        print(f"Dataset not found: {args.dataset}")
        print("Build one first (see eval/build_dataset.py), or point --dataset at eval/data/sample_labeled_posts.jsonl.")
        sys.exit(1)

    results = run(args.dataset)
    metrics = compute_metrics(results)
    print_report(metrics)

    out_path = args.out
    if out_path is None:
        os.makedirs("eval/results", exist_ok=True)
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M%S")
        out_path = f"eval/results/{timestamp}.json"
    else:
        os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"metrics": metrics, "results": results}, f, indent=2, ensure_ascii=False)
    print(f"Results written to {out_path}")


if __name__ == "__main__":
    main()
