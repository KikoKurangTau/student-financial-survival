"""Financial-health scoring and endings."""
from __future__ import annotations
from .finance import PlayerState, totals, spending_by_category

def calculate_financial_health(state: PlayerState) -> float:
    total = totals(state)["expenses"]
    income_base = max(state.income + state.balance + state.savings, 1)
    savings_ratio = min(state.savings / max(state.savings_target, 1), 1) * 100
    spent = spending_by_category(state)
    budget_total = max(sum(state.budgets.values()), 1)
    expense_control = max(0, 100 * (1 - max(0, total - budget_total) / budget_total))
    reserve = min(state.balance / max(state.emergency_reserve, 1), 1) * 100
    debt = max(0, 100 * (1 - state.debt / income_base))
    cash = min(state.balance / max(300_000, income_base * .1), 1) * 100
    return round(.25*savings_ratio + .25*expense_control + .20*reserve + .20*debt + .10*cash, 1)

def health_label(score: float) -> str:
    return "Excellent" if score >= 90 else "Healthy" if score >= 75 else "Stable" if score >= 60 else "Risky" if score >= 40 else "Critical" if score >= 20 else "Financial Crisis"

def final_rank(state: PlayerState) -> tuple[str, str]:
    score = calculate_financial_health(state)
    rank = "S" if score >= 90 else "A" if score >= 75 else "B" if score >= 60 else "C" if score >= 40 else "D" if score >= 20 else "F"
    names = {"S":"Financial Master", "A":"Excellent", "B":"Healthy", "C":"Survivor", "D":"Risky", "F":"Financial Crisis"}
    return rank, names[rank]

def ending(state: PlayerState) -> str:
    if state.game_over: return "Game Over"
    rank, _ = final_rank(state)
    return {"S":"Financial Master", "A":"Excellent Student", "B":"Survivor", "C":"Barely Survived", "D":"Barely Survived", "F":"Financial Crisis"}[rank]
