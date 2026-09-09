"""Student Financial Survival Simulator Streamlit application."""
from __future__ import annotations
import json
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st
from database.database import save_daily_status, save_game_summary, save_transactions
from modules.achievements import check_achievements, load_achievements
from modules.economy import DIFFICULTIES, apply_daily_food, create_state
from modules.events import apply_choice, load_events, pick_event
from modules.finance import CATEGORIES, PlayerState, deposit_savings, spending_by_category, totals
from modules.scoring import calculate_financial_health, ending, final_rank, health_label
from utils.formatting import rupiah

ROOT = Path(__file__).parent
DEFAULT_BUDGETS = {"Food": 1_000_000, "Transportation": 300_000, "Education": 200_000, "Living": 200_000, "Entertainment": 200_000, "Emergency": 300_000, "Other": 0}

st.set_page_config(page_title="Student Financial Survival", page_icon="💸", layout="wide")

def initialize_game(difficulty: str, budgets: dict[str, float], reserve: float, target: float, income: float) -> None:
    state = create_state(difficulty, budgets, reserve, target, income)
    if income:
        state.balance += income
    state.financial_health = calculate_financial_health(state)
    state.balance_history.append({"day": 0, "balance": state.balance})
    st.session_state.game, st.session_state.difficulty, st.session_state.pending_event = state, difficulty, None

def show_setup() -> None:
    st.title("🎓 Student Financial Survival Simulator")
    st.caption("Can you survive 30 days without going broke?")
    with st.form("setup"):
        difficulty = st.selectbox("Difficulty", list(DIFFICULTIES))
        st.info(f"Starting money: {rupiah(DIFFICULTIES[difficulty]['starting'])}")
        income = st.number_input("Monthly income / allowance", min_value=0, value=0, step=50_000)
        columns = st.columns(2); budgets = {}
        for index, category in enumerate(CATEGORIES):
            with columns[index % 2]: budgets[category] = st.number_input(f"{category} budget", min_value=0, value=DEFAULT_BUDGETS[category], step=25_000, key=category)
        reserve = st.number_input("Emergency reserve", min_value=0, value=300_000, step=25_000)
        target = st.number_input("Savings target", min_value=0, value=500_000, step=25_000)
        if st.form_submit_button("Start 30-Day Challenge", type="primary"):
            try: initialize_game(difficulty, budgets, reserve, target, income); st.rerun()
            except ValueError as exc: st.error(str(exc))

def metric_dashboard(state: PlayerState) -> None:
    state.financial_health = calculate_financial_health(state)
    cols = st.columns(4)
    values = [("DAY", f"{state.day} / 30"), ("Balance", rupiah(state.balance)), ("Financial Health", f"{state.financial_health:.0f} / 100"), ("Savings", rupiah(state.savings)), ("Debt", rupiah(state.debt)), ("Stress", f"{state.stress} / 100"), ("Happiness", f"{state.happiness} / 100"), ("Academic Performance", f"{state.academic_performance} / 100")]
    for i, (label, value) in enumerate(values): cols[i % 4].metric(label, value)
    st.progress(state.financial_health / 100, text=f"Financial health: {health_label(state.financial_health)}")

def budget_table(state: PlayerState) -> None:
    spent = spending_by_category(state); rows=[]
    for category, budget in state.budgets.items():
        use = spent.get(category, 0); pct = (use / budget * 100) if budget else 0
        rows.append({"Category":category,"Budget":rupiah(budget),"Spent":rupiah(use),"Remaining":rupiah(budget-use),"Used":f"{pct:.0f}%"})
        if budget and pct > 100: st.error(f"Critical: {category} is over budget ({pct:.0f}%).")
        elif budget and pct > 80: st.warning(f"Warning: {category} is nearly exhausted ({pct:.0f}%).")
    st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)

def advance_day(state: PlayerState) -> None:
    multiplier = DIFFICULTIES[st.session_state.difficulty]["expense_multiplier"]
    apply_daily_food(state, multiplier)
    events = load_events(ROOT / "data/events.json")
    st.session_state.pending_event = pick_event(events, DIFFICULTIES[st.session_state.difficulty]["event_multiplier"])
    if not st.session_state.pending_event: finish_day(state)

def finish_day(state: PlayerState) -> None:
    state.financial_health = calculate_financial_health(state)
    state.health_history.append(state.financial_health); state.balance_history.append({"day": state.day, "balance": state.balance})
    if state.debt > 0 and state.balance == 0: state.game_over = True
    elif state.day >= 30: state.game_completed = True
    else: state.day += 1
    check_achievements(state, load_achievements(ROOT / "data/achievements.json"))

def charts(state: PlayerState) -> None:
    tx = pd.DataFrame(state.transactions)
    if tx.empty: return
    expenses = tx[tx.type == "expense"]
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(px.line(pd.DataFrame(state.balance_history), x="day", y="balance", title="Balance over time", markers=True), use_container_width=True)
        st.plotly_chart(px.pie(expenses, names="need_or_want", values="amount", title="Needs vs Wants"), use_container_width=True)
    with col2:
        st.plotly_chart(px.bar(expenses.groupby("category", as_index=False).amount.sum(), x="category", y="amount", title="Expenses by category"), use_container_width=True)
        budget = pd.DataFrame({"Category": list(state.budgets), "Budget": list(state.budgets.values()), "Spent": [spending_by_category(state)[x] for x in state.budgets]}).melt("Category", var_name="Metric", value_name="Amount")
        st.plotly_chart(px.bar(budget, x="Category", y="Amount", color="Metric", barmode="group", title="Spending vs budget"), use_container_width=True)
    if state.health_history: st.plotly_chart(px.line(x=list(range(1,len(state.health_history)+1)), y=state.health_history, title="Financial health over time", labels={"x":"Day","y":"Health"}, markers=True), use_container_width=True)

def final_report(state: PlayerState) -> None:
    st.title(f"🏁 {ending(state)}")
    rank, label = final_rank(state); data = totals(state)
    st.success(f"Final Rank: {rank} — {label}")
    st.write("You survived the month with a healthy savings rate and controlled discretionary spending." if state.financial_health >= 60 else "Your month revealed where a tighter budget, lower debt, and a stronger emergency reserve would help.")
    report = {"Total income":state.income,"Total expenses":data["expenses"],"Total savings":state.savings,"Total debt":state.debt,"Total needs":data["needs"],"Total wants":data["wants"],"Expense ratio":data["expenses"]/max(state.income+state.balance+state.savings,1),"Savings ratio":state.savings/max(state.income+state.balance+state.savings,1),"Emergency reserve":state.emergency_reserve,"Academic performance":state.academic_performance,"Happiness":state.happiness,"Stress":state.stress,"Final financial health":state.financial_health}
    st.dataframe(pd.DataFrame(report.items(), columns=["Metric","Value"]), hide_index=True, use_container_width=True)
    charts(state)
    st.download_button("Export Transactions", pd.DataFrame(state.transactions).to_csv(index=False).encode(), "transactions.csv", "text/csv")
    if st.button("Restart Game / Play Again", type="primary"): st.session_state.clear(); st.rerun()

def game_view(state: PlayerState) -> None:
    metric_dashboard(state)
    total = totals(state); expense_total=max(total["expenses"],1)
    st.caption(f"Needs: {rupiah(total['needs'])} ({total['needs']/expense_total:.0%}) · Wants: {rupiah(total['wants'])} ({total['wants']/expense_total:.0%})")
    if total["wants"] / expense_total > .30: st.warning("Wants spending is high—consider protecting your essentials and savings.")
    with st.expander("Budget tracker", expanded=True): budget_table(state)
    pending = st.session_state.pending_event
    if pending:
        st.subheader(f"⚡ {pending['title']}"); st.write(pending["description"])
        for index, choice in enumerate(pending["choices"]):
            if st.button(choice["label"], key=f"choice_{index}"):
                try: apply_choice(state, pending, index); st.session_state.pending_event=None; finish_day(state); st.rerun()
                except ValueError as exc: st.error(str(exc))
    else:
        if st.button("Complete Today", type="primary"):
            try: advance_day(state); st.rerun()
            except ValueError as exc: st.error(f"Could not advance day: {exc}")
    with st.expander("Save money / transaction history"):
        amount=st.number_input("Move balance into savings", min_value=0, value=0, step=25_000)
        if st.button("Deposit savings") and amount:
            try: deposit_savings(state, amount); st.rerun()
            except ValueError as exc: st.error(str(exc))
        tx=pd.DataFrame(state.transactions)
        if not tx.empty: st.dataframe(tx.sort_values("day", ascending=False)[["day","category","description","amount","need_or_want"]], hide_index=True, use_container_width=True)
    charts(state)

if "game" not in st.session_state: show_setup()
else:
    state=st.session_state.game
    if state.game_over or state.game_completed:
        try:
            if not st.session_state.get("game_saved"):
                game_id = save_game_summary(st.session_state.difficulty,state.balance,state.financial_health)
                save_transactions(game_id,state.transactions); save_daily_status(game_id,state)
                st.session_state.game_saved = True
        except RuntimeError as exc: st.warning(str(exc))
        final_report(state)
    else: game_view(state)
