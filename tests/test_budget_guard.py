"""
Tests for budget_guard.py — the daily call-budget circuit breaker that caps
how many live LLM judge calls the bot will make per day, so a spam wave of
triggers can't run up an unbounded API bill. State is persisted to a JSON
file so the cap survives bot restarts, not just in-memory.
"""
from budget_guard import DailyBudgetGuard


def _guard(tmp_path, limit, today="2026-07-18"):
    state_path = tmp_path / "budget_state.json"
    clock = iter([today] * 1000)  # simple fixed-date clock, advanced via next()
    return DailyBudgetGuard(limit=limit, state_path=str(state_path), today_fn=lambda: next(clock))


def test_allows_calls_up_to_the_limit(tmp_path):
    guard = _guard(tmp_path, limit=3)
    assert guard.try_consume() is True
    assert guard.try_consume() is True
    assert guard.try_consume() is True
    assert guard.try_consume() is False  # 4th call, limit exhausted


def test_denied_calls_do_not_consume_budget(tmp_path):
    guard = _guard(tmp_path, limit=1)
    assert guard.try_consume() is True
    assert guard.try_consume() is False
    assert guard.try_consume() is False  # still denied, not decrementing into negatives
    assert guard.remaining() == 0


def test_remaining_reflects_consumption(tmp_path):
    guard = _guard(tmp_path, limit=5)
    assert guard.remaining() == 5
    guard.try_consume()
    guard.try_consume()
    assert guard.remaining() == 3


def test_resets_on_a_new_day(tmp_path):
    state_path = tmp_path / "budget_state.json"
    day = {"value": "2026-07-18"}
    guard = DailyBudgetGuard(limit=2, state_path=str(state_path), today_fn=lambda: day["value"])

    assert guard.try_consume() is True
    assert guard.try_consume() is True
    assert guard.try_consume() is False  # exhausted on day 1

    day["value"] = "2026-07-19"
    assert guard.try_consume() is True  # fresh budget on day 2
    assert guard.remaining() == 1


def test_state_persists_across_new_guard_instances(tmp_path):
    """Simulates a bot restart: a fresh DailyBudgetGuard pointed at the same
    state file must see the already-consumed budget, not reset to full."""
    state_path = tmp_path / "budget_state.json"

    guard1 = DailyBudgetGuard(limit=3, state_path=str(state_path), today_fn=lambda: "2026-07-18")
    guard1.try_consume()
    guard1.try_consume()

    guard2 = DailyBudgetGuard(limit=3, state_path=str(state_path), today_fn=lambda: "2026-07-18")
    assert guard2.remaining() == 1
    assert guard2.try_consume() is True
    assert guard2.try_consume() is False


def test_missing_state_file_starts_with_full_budget(tmp_path):
    state_path = tmp_path / "does_not_exist_yet.json"
    guard = DailyBudgetGuard(limit=10, state_path=str(state_path), today_fn=lambda: "2026-07-18")
    assert guard.remaining() == 10


def test_corrupt_state_file_fails_safe_to_full_budget(tmp_path):
    """A corrupt state file should not crash the bot or silently deny all
    calls — fail safe by starting a fresh budget."""
    state_path = tmp_path / "budget_state.json"
    state_path.write_text("not valid json{{{", encoding="utf-8")
    guard = DailyBudgetGuard(limit=5, state_path=str(state_path), today_fn=lambda: "2026-07-18")
    assert guard.remaining() == 5
    assert guard.try_consume() is True
