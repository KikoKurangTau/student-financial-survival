from modules.finance import PlayerState, add_transaction, deposit_savings, totals
import pytest

def test_adding_expense_reduces_balance():
    state=PlayerState(balance=100)
    add_transaction(state,category="Food",description="Meal",amount=25,transaction_type="expense",need_or_want="Need")
    assert state.balance == 75 and totals(state)["needs"] == 25

def test_adding_income_increases_balance():
    state=PlayerState(balance=100)
    add_transaction(state,category="Other",description="Gig",amount=50,transaction_type="income",need_or_want="Need")
    assert state.balance == 150 and state.income == 50

def test_debt_when_expense_exceeds_cash():
    state=PlayerState(balance=50)
    add_transaction(state,category="Emergency",description="Repair",amount=80,transaction_type="expense",need_or_want="Need")
    assert state.balance == 0 and state.debt == 30

def test_savings_calculation():
    state=PlayerState(balance=100); deposit_savings(state,40)
    assert state.balance == 60 and state.savings == 40

def test_reject_negative_transaction():
    with pytest.raises(ValueError): add_transaction(PlayerState(),category="Food",description="x",amount=-1,transaction_type="expense",need_or_want="Need")
