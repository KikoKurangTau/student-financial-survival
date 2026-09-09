"""Difficulty and daily economy mechanics."""
from __future__ import annotations
import random
from .finance import PlayerState, add_transaction

DIFFICULTIES = {
    "Easy": {"starting": 3_000_000, "event_multiplier": .55, "expense_multiplier": .85},
    "Normal": {"starting": 2_500_000, "event_multiplier": 1.0, "expense_multiplier": 1.0},
    "Hard": {"starting": 2_000_000, "event_multiplier": 1.35, "expense_multiplier": 1.2},
    "Nightmare": {"starting": 1_500_000, "event_multiplier": 1.7, "expense_multiplier": 1.45},
}

def create_state(difficulty: str, budgets: dict[str, float], emergency_reserve: float, savings_target: float, income: float = 0) -> PlayerState:
    if difficulty not in DIFFICULTIES or any(value < 0 for value in budgets.values()) or emergency_reserve < 0:
        raise ValueError("Invalid game setup.")
    return PlayerState(balance=DIFFICULTIES[difficulty]["starting"], budgets=budgets, emergency_reserve=emergency_reserve, savings_target=savings_target, income=income)

def apply_daily_food(state: PlayerState, multiplier: float = 1.0, rng: random.Random | None = None) -> float:
    rng = rng or random
    amount = round(rng.randint(25_000, 45_000) * multiplier)
    add_transaction(state, category="Food", description="Daily meal", amount=amount, transaction_type="expense", need_or_want="Need")
    return amount
