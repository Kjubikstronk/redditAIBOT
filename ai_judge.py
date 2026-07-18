import os
import json
import logging
from typing import Any, Dict, Optional

import anthropic

from budget_guard import DailyBudgetGuard

# Default judge model. Override per-deployment with the JUDGE_MODEL env var —
# e.g. run the live bot on the cheaper claude-haiku-4-5 while eval-testing on
# claude-fable-5, so you pick the cheapest model that's accurate enough.
MODEL = "claude-sonnet-5"

# Defense-in-depth against a spam wave running up an unbounded API bill.
# Also set a hard spend limit on the API key itself in the Anthropic
# Console — that's enforced server-side and doesn't depend on this code.
DEFAULT_DAILY_JUDGE_CALL_LIMIT = 200

VERDICT_MAP = {
    "likely_human": "🟢 Likely Human",
    "uncertain": "🟡 Possibly AI-Generated",
    "likely_ai": "🔴 Potentially AI-Generated",
}

SCHEMA = {
    "type": "object",
    "properties": {
        "verdict": {"type": "string", "enum": list(VERDICT_MAP.keys())},
        "confidence": {"type": "number"},
        "reasoning": {"type": "string"},
    },
    "required": ["verdict", "confidence", "reasoning"],
    "additionalProperties": False,
}

SYSTEM_PROMPT = """You are judging whether a Reddit post was written by a human or generated/heavily assisted by an AI language model.

You will be given the post text and some statistical signals computed from it. The signals are unreliable on their own \
(modern AI writing routinely defeats them) — use them as weak supporting evidence, not the deciding factor. Base your judgment \
primarily on the substance of the text: voice consistency, whether specific details feel lived-in vs generic, narrative \
coherence, and whether the structure and phrasing match typical Reddit writing for this kind of post.

Be conservative. Real people write in every register — terse, rambling, non-native English, neurodivergent, deadpan — and none \
of that alone indicates AI authorship. Only lean toward "likely_ai" when multiple strong, specific signals point that way. When \
unsure, say "uncertain" rather than guessing confidently in either direction.

Respond with a verdict, a confidence from 0 to 1, and a one-to-two-sentence reasoning."""

MAX_TEXT_CHARS = 6000

_client: Optional[anthropic.Anthropic] = None
_client_checked = False
_budget_guard: Optional[DailyBudgetGuard] = None


def get_client() -> Optional[anthropic.Anthropic]:
    """Lazily creates the Anthropic client. Returns None if no API key is configured."""
    global _client, _client_checked
    if not _client_checked:
        _client_checked = True
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if api_key:
            _client = anthropic.Anthropic(api_key=api_key)
    return _client


def get_budget_guard() -> DailyBudgetGuard:
    """Lazily creates the daily call-budget guard. Limit is read from
    MAX_DAILY_JUDGE_CALLS (falls back to DEFAULT_DAILY_JUDGE_CALL_LIMIT)."""
    global _budget_guard
    if _budget_guard is None:
        limit = int(os.getenv("MAX_DAILY_JUDGE_CALLS", DEFAULT_DAILY_JUDGE_CALL_LIMIT))
        state_path = os.getenv("JUDGE_BUDGET_STATE_PATH", ".judge_budget_state.json")
        _budget_guard = DailyBudgetGuard(limit=limit, state_path=state_path)
    return _budget_guard


def judge_text(text: str, heuristic_context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Judges whether `text` is likely AI-generated using Claude as an LLM judge, with
    local heuristic signals passed in as supporting (non-authoritative) context.
    Returns {"verdict": <emoji-labeled string>, "confidence": float, "reasoning": str},
    or None if the judge is unavailable (no API key) or the call fails, so the caller
    can fall back to a local heuristic verdict.
    """
    client = get_client()
    if client is None:
        return None

    if not get_budget_guard().try_consume():
        logging.warning(
            f"Daily judge call budget exhausted ({get_budget_guard().limit}/day) — "
            "falling back to heuristic scoring for the rest of today."
        )
        return None

    context_lines = "\n".join(f"- {k}: {v}" for k, v in heuristic_context.items())
    user_content = (
        f"Statistical signals (weak, supporting evidence only):\n{context_lines}\n\n"
        f"Post text:\n{text[:MAX_TEXT_CHARS]}"
    )

    try:
        response = client.messages.create(
            model=os.getenv("JUDGE_MODEL", MODEL),
            max_tokens=400,
            system=SYSTEM_PROMPT,
            output_config={"format": {"type": "json_schema", "schema": SCHEMA}},
            messages=[{"role": "user", "content": user_content}],
        )
    except Exception as e:
        logging.error(f"LLM judge call failed: {e}")
        return None

    raw = next((block.text for block in response.content if block.type == "text"), None)
    if not raw:
        logging.error("LLM judge returned no text block.")
        return None

    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        logging.error(f"LLM judge returned unparsable JSON: {raw!r}")
        return None

    verdict_key = result.get("verdict")
    if verdict_key not in VERDICT_MAP:
        logging.error(f"LLM judge returned unknown verdict: {verdict_key!r}")
        return None

    return {
        "verdict": VERDICT_MAP[verdict_key],
        "confidence": result.get("confidence"),
        "reasoning": result.get("reasoning", ""),
    }
