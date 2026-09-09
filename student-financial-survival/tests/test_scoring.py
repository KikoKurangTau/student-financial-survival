from modules.finance import PlayerState, add_transaction, totals
from modules.scoring import calculate_financial_health, final_rank

def test_financial_health_is_bounded():
    state=PlayerState(balance=500000,savings=500000,budgets={"Food":1000000},savings_target=500000)
    assert 0 <= calculate_financial_health(state) <= 100

def test_expense_ratio_and_wants():
    state=PlayerState(balance=1000)
    add_transaction(state,category="Entertainment",description="movie",amount=100,transaction_type="expense",need_or_want="Want")
    assert totals(state)["wants"] / totals(state)["expenses"] == 1

def test_final_ranking():
    state=PlayerState(balance=2_000_000,savings=500_000,budgets={"Food":1_000_000},savings_target=500_000,emergency_reserve=300_000)
    assert final_rank(state)[0] in {"S","A","B","C","D","F"}
