"""Achievement evaluation."""
from __future__ import annotations
import json
from pathlib import Path
from .finance import PlayerState, totals
from .scoring import calculate_financial_health

def load_achievements(path: str | Path) -> list[dict]:
    try: return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc: raise ValueError(f"Unable to load achievements: {exc}") from exc

def check_achievements(state: PlayerState, definitions: list[dict]) -> list[str]:
    data = totals(state); unlocked = []
    rules = {"survived": state.day > 30 or state.game_completed, "zero_debt": state.debt == 0, "reserve": state.balance >= state.emergency_reserve,
             "frugal": data["wants"] <= data["expenses"]*.15 if data["expenses"] else False, "master": calculate_financial_health(state) >= 90,
             "no_wants": data["wants"] == 0 and data["expenses"] > 0, "saver": state.savings >= state.savings_target, "perfect": state.academic_performance >= 90 and state.stress <= 25}
    for item in definitions:
        if rules.get(item.get("rule")) and item["id"] not in state.achievements:
            state.achievements.append(item["id"]); unlocked.append(item["id"])
    return unlocked
