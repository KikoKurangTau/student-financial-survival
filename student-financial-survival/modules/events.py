"""JSON-backed random event handling."""
from __future__ import annotations
import json, random
from pathlib import Path
from typing import Any
from .finance import PlayerState, add_transaction

def load_events(path: str | Path) -> list[dict[str, Any]]:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        if not isinstance(data, list): raise ValueError("Events must be a list.")
        return data
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        raise ValueError(f"Unable to load events: {exc}") from exc

def pick_event(events: list[dict[str, Any]], multiplier: float = 1, rng: random.Random | None = None) -> dict[str, Any] | None:
    rng = rng or random
    candidates = [event for event in events if rng.random() < min(1, event.get("probability", 0) * multiplier)]
    return rng.choice(candidates) if candidates else None

def apply_choice(state: PlayerState, event: dict[str, Any], choice_index: int) -> None:
    choices = event.get("choices", [])
    if not 0 <= choice_index < len(choices): raise ValueError("Invalid event choice.")
    choice = choices[choice_index]
    cost, income = float(choice.get("cost", 0)), float(choice.get("income", 0))
    if cost: add_transaction(state, category=choice.get("category", "Other"), description=event["title"], amount=cost, transaction_type="expense", need_or_want=choice.get("need_or_want", "Need"))
    if income: add_transaction(state, category="Other", description=event["title"], amount=income, transaction_type="income", need_or_want="Need")
    state.stress += int(choice.get("stress", 0)); state.happiness += int(choice.get("happiness", 0)); state.academic_performance += int(choice.get("academic", 0)); state.clamp_wellbeing()
