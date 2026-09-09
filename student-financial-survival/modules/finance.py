"""Player state and transaction operations."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any

CATEGORIES = ("Food", "Transportation", "Education", "Living", "Entertainment", "Emergency", "Other")

@dataclass
class PlayerState:
    day: int = 1
    balance: float = 2_500_000
    savings: float = 0
    debt: float = 0
    income: float = 0
    stress: int = 30
    happiness: int = 65
    academic_performance: int = 80
    financial_health: float = 0
    transactions: list[dict[str, Any]] = field(default_factory=list)
    achievements: list[str] = field(default_factory=list)
    game_over: bool = False
    game_completed: bool = False
    budgets: dict[str, float] = field(default_factory=dict)
    emergency_reserve: float = 300_000
    savings_target: float = 500_000
    health_history: list[float] = field(default_factory=list)
    balance_history: list[dict[str, float]] = field(default_factory=list)

    def clamp_wellbeing(self) -> None:
        self.stress = max(0, min(100, self.stress))
        self.happiness = max(0, min(100, self.happiness))
        self.academic_performance = max(0, min(100, self.academic_performance))

def validate_amount(amount: float) -> float:
    if amount < 0:
        raise ValueError("Transaction amount cannot be negative.")
    return float(amount)

def add_transaction(state: PlayerState, *, category: str, description: str, amount: float,
                    transaction_type: str, need_or_want: str, day: int | None = None) -> dict[str, Any]:
    """Record a validated transaction and update cash. Expenses beyond cash become debt."""
    if category not in CATEGORIES or need_or_want not in {"Need", "Want"}:
        raise ValueError("Invalid category or need/want value.")
    if transaction_type not in {"income", "expense"}:
        raise ValueError("Transaction type must be income or expense.")
    amount = validate_amount(amount)
    record = {"day": day or state.day, "category": category, "description": description,
              "amount": amount, "type": transaction_type, "need_or_want": need_or_want}
    if record in state.transactions:
        raise ValueError("Duplicate transaction.")
    state.transactions.append(record)
    if transaction_type == "income":
        state.balance += amount
        state.income += amount
    else:
        state.balance -= amount
        if state.balance < 0:
            state.debt += -state.balance
            state.balance = 0
    return record

def deposit_savings(state: PlayerState, amount: float) -> None:
    amount = validate_amount(amount)
    if amount > state.balance:
        raise ValueError("Savings deposit exceeds available balance.")
    state.balance -= amount
    state.savings += amount

def totals(state: PlayerState) -> dict[str, float]:
    expenses = [t for t in state.transactions if t["type"] == "expense"]
    return {"expenses": sum(t["amount"] for t in expenses), "needs": sum(t["amount"] for t in expenses if t["need_or_want"] == "Need"),
            "wants": sum(t["amount"] for t in expenses if t["need_or_want"] == "Want")}

def spending_by_category(state: PlayerState) -> dict[str, float]:
    result = {category: 0.0 for category in CATEGORIES}
    for item in state.transactions:
        if item["type"] == "expense": result[item["category"]] += item["amount"]
    return result
