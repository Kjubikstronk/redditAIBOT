"""
Tests for eval/run_eval.py's compute_metrics() — pure logic, no dataset or API
calls needed. Getting this right matters: a bug here would silently misreport
the bot's actual detection accuracy.
"""
from run_eval import compute_metrics


def _result(label, verdict, confidence=None, notes=None, used_fallback=False):
    return {
        "label": label,
        "predicted_verdict": verdict,
        "confidence": confidence,
        "notes": notes or [],
        "used_fallback": used_fallback,
    }


def test_confusion_matrix_counts():
    results = [
        _result("human", "🟢 Likely Human"),
        _result("human", "🟡 Possibly AI-Generated"),
        _result("ai", "🔴 Potentially AI-Generated"),
        _result("ai", "🟢 Likely Human"),
    ]
    cm = compute_metrics(results)["confusion_matrix"]
    assert cm["🟢 Likely Human"]["human"] == 1
    assert cm["🟡 Possibly AI-Generated"]["human"] == 1
    assert cm["🔴 Potentially AI-Generated"]["ai"] == 1
    assert cm["🟢 Likely Human"]["ai"] == 1
    assert cm["🟡 Possibly AI-Generated"]["ai"] == 0


def test_suspicious_framing_precision_recall():
    # 🟡 or 🔴 counts as a positive ("suspicious") prediction.
    results = [
        _result("ai", "🔴 Potentially AI-Generated"),    # TP
        _result("ai", "🟡 Possibly AI-Generated"),        # TP
        _result("ai", "🟢 Likely Human"),                 # FN
        _result("human", "🔴 Potentially AI-Generated"),  # FP
        _result("human", "🟢 Likely Human"),               # TN
    ]
    sf = compute_metrics(results)["suspicious_framing"]
    assert round(sf["precision"], 4) == round(2 / 3, 4)
    assert round(sf["recall"], 4) == round(2 / 3, 4)
    assert sf["f1"] is not None


def test_confident_framing_only_counts_red_as_positive():
    results = [
        _result("ai", "🟡 Possibly AI-Generated"),        # FN in this framing
        _result("ai", "🔴 Potentially AI-Generated"),     # TP
        _result("human", "🔴 Potentially AI-Generated"),  # FP
    ]
    cf = compute_metrics(results)["confident_framing"]
    assert cf["precision"] == 0.5
    assert cf["recall"] == 0.5


def test_precision_and_recall_are_none_when_undefined():
    # No predicted-positive and no true-"ai" examples at all -> both 0/0, so
    # both metrics are undefined (None), not silently coerced to 0.0.
    results = [_result("human", "🟢 Likely Human")]
    sf = compute_metrics(results)["suspicious_framing"]
    assert sf["precision"] is None
    assert sf["recall"] is None


def test_fallback_rate():
    results = [
        _result("human", "🟢 Likely Human", used_fallback=True),
        _result("human", "🟢 Likely Human", used_fallback=False),
    ]
    assert compute_metrics(results)["fallback_rate"] == 0.5


def test_fairness_slice_groups_human_only_by_notes_tag():
    results = [
        _result("human", "🔴 Potentially AI-Generated", notes=["terse"]),  # FP, terse
        _result("human", "🟢 Likely Human", notes=["terse"]),              # correct, terse
        _result("human", "🟢 Likely Human", notes=[]),                     # correct, untagged
        _result("ai", "🔴 Potentially AI-Generated", notes=["terse"]),     # excluded: not human
    ]
    fs = compute_metrics(results)["fairness_slice"]
    assert fs["terse"]["n"] == 2
    assert fs["terse"]["false_positive_rate"] == 0.5
    assert fs["untagged"]["n"] == 1
    assert fs["untagged"]["false_positive_rate"] == 0.0


def test_confidence_buckets_only_include_scored_examples():
    results = [
        _result("ai", "🔴 Potentially AI-Generated", confidence=0.95),
        _result("human", "🟢 Likely Human", confidence=0.1),
        _result("human", "🟢 Likely Human", confidence=None),  # fallback path, excluded
    ]
    buckets = compute_metrics(results)["confidence_buckets"]
    total_bucketed = sum(b["n"] for b in buckets.values())
    assert total_bucketed == 2


def test_empty_results_does_not_crash():
    metrics = compute_metrics([])
    assert metrics["n"] == 0
    assert metrics["suspicious_framing"]["precision"] is None
