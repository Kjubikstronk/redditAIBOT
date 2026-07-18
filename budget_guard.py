"""
Daily call-budget circuit breaker. Caps how many live LLM calls a process is
allowed to make per day, persisted to a small JSON state file so the cap
survives bot restarts (not just an in-memory counter). Used by ai_judge.py to
stop calling the Anthropic API — falling back to local heuristic scoring
instead — once a spam wave or runaway trigger volume would otherwise run up
an unbounded bill.

This is defense-in-depth alongside (not instead of) setting a hard spend
limit on the API key itself in the Anthropic Console, which is enforced
server-side regardless of any bug here.
"""
import json
import logging
from datetime import datetime, timezone
from typing import Callable, Optional


def _default_today() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


class DailyBudgetGuard:
    def __init__(
        self,
        limit: int,
        state_path: str = ".judge_budget_state.json",
        today_fn: Callable[[], str] = _default_today,
    ):
        self.limit = limit
        self.state_path = state_path
        self.today_fn = today_fn

    def _load_state(self) -> dict:
        try:
            with open(self.state_path, "r", encoding="utf-8") as f:
                state = json.load(f)
            if not isinstance(state, dict) or "date" not in state or "count" not in state:
                raise ValueError("malformed state")
            return state
        except (FileNotFoundError, json.JSONDecodeError, ValueError, OSError):
            return {"date": self.today_fn(), "count": 0}

    def _save_state(self, state: dict) -> None:
        try:
            with open(self.state_path, "w", encoding="utf-8") as f:
                json.dump(state, f)
        except OSError as e:
            logging.error(f"DailyBudgetGuard: could not persist state to {self.state_path}: {e}")

    def _current_count(self) -> int:
        state = self._load_state()
        today = self.today_fn()
        if state["date"] != today:
            return 0
        return state["count"]

    def remaining(self) -> int:
        return max(0, self.limit - self._current_count())

    def try_consume(self) -> bool:
        """Attempts to consume one unit of today's budget. Returns True and
        records the consumption if budget remains; returns False (and does
        not modify state) if the daily limit has already been reached."""
        today = self.today_fn()
        state = self._load_state()
        count = state["count"] if state["date"] == today else 0

        if count >= self.limit:
            return False

        self._save_state({"date": today, "count": count + 1})
        return True
