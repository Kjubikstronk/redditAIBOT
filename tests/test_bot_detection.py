"""
Integration tests for bot.py's format_detection_results — the single entry
point shared by the live bot, test_mode, and eval/run_eval.py. Verifies the
judge/fallback branching and that verdict strings never drift from the exact
set log_parser.py depends on.
"""
import re

import bot
import log_parser

CANONICAL_VERDICTS = {"🟢 Likely Human", "🟡 Possibly AI-Generated", "🔴 Potentially AI-Generated"}

LONG_TEXT = (
    "This is a long enough piece of text to clear the fifteen-word short-circuit "
    "and reach the judge-or-fallback branch of format_detection_results, since it "
    "needs to have more than a handful of words in it to count."
)


def test_short_text_always_likely_human():
    report, verdict, confidence = bot.format_detection_results("too short", skip_account=True)
    assert verdict == "🟢 Likely Human"
    assert confidence is None


def test_fallback_used_when_judge_returns_none(monkeypatch):
    monkeypatch.setattr(bot, "judge_text", lambda text, ctx: None)

    report, verdict, confidence = bot.format_detection_results(LONG_TEXT, skip_account=True)

    assert verdict in CANONICAL_VERDICTS
    assert confidence is None
    assert "fallback heuristic" in report


def test_judge_path_used_when_available(monkeypatch):
    monkeypatch.setattr(
        bot, "judge_text",
        lambda text, ctx: {"verdict": "🔴 Potentially AI-Generated", "confidence": 0.9, "reasoning": "looks generated"},
    )

    report, verdict, confidence = bot.format_detection_results(LONG_TEXT, skip_account=True)

    assert verdict == "🔴 Potentially AI-Generated"
    assert confidence == 0.9
    assert "looks generated" in report
    assert "fallback heuristic" not in report


def test_real_fallback_path_with_no_api_key(monkeypatch):
    # No monkeypatching of judge_text here — exercises the real, un-mocked
    # path from get_client() is None all the way to a fallback verdict,
    # which is the actual production behavior when ANTHROPIC_API_KEY is unset.
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    report, verdict, confidence = bot.format_detection_results(LONG_TEXT, skip_account=True)

    assert verdict in CANONICAL_VERDICTS
    assert confidence is None
    assert "fallback heuristic" in report


def test_verdict_string_survives_log_parser_round_trip(monkeypatch):
    """Regression guard: log_parser.py regex-matches a specific verdict-string
    shape out of user_log.log. If the verdict format ever changes, this should
    fail here instead of silently breaking the dashboard."""
    monkeypatch.setattr(bot, "judge_text", lambda text, ctx: None)
    _, verdict, _ = bot.format_detection_results(LONG_TEXT, skip_account=True)

    log_line = (
        f"2026-01-01 00:00:00,000 - User: some_user in r/test (Comment ID: abc123) - Verdict: {verdict}"
    )
    pattern = re.compile(
        r"(\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2},\d{3})\s+-\s+User:\s+(.*?)\s+in\s+r/(\w+)\s+\(Comment\s+ID:\s+\w+\)\s+-\s+Verdict:\s+(.*)"
    )
    match = pattern.search(log_line)
    assert match is not None
    matched_verdict = match.group(4)
    assert matched_verdict == verdict
    cleaned = log_parser.clean_text(matched_verdict)
    assert cleaned  # non-empty ASCII string after stripping emoji
