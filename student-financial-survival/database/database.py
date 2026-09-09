"""Small, resilient SQLite repository."""
from __future__ import annotations
import sqlite3
from pathlib import Path
from typing import Any

SCHEMA = """CREATE TABLE IF NOT EXISTS games (id INTEGER PRIMARY KEY, created_at TEXT DEFAULT CURRENT_TIMESTAMP, difficulty TEXT, final_balance REAL, final_health REAL);
CREATE TABLE IF NOT EXISTS transactions (id INTEGER PRIMARY KEY, game_id INTEGER, day INTEGER, category TEXT, description TEXT, amount REAL, type TEXT, need_or_want TEXT);
CREATE TABLE IF NOT EXISTS daily_status (id INTEGER PRIMARY KEY, game_id INTEGER, day INTEGER, balance REAL, savings REAL, debt REAL, health REAL, stress INTEGER, happiness INTEGER, academic INTEGER);
CREATE TABLE IF NOT EXISTS achievements (id INTEGER PRIMARY KEY, game_id INTEGER, achievement_id TEXT);"""

def connect(path: str | Path = Path(__file__).parent / "simulator.db") -> sqlite3.Connection:
    try:
        conn = sqlite3.connect(path); conn.executescript(SCHEMA); return conn
    except sqlite3.Error as exc: raise RuntimeError(f"Database error: {exc}") from exc

def save_game_summary(difficulty: str, balance: float, health: float) -> int:
    with connect() as conn:
        cursor = conn.execute("INSERT INTO games (difficulty, final_balance, final_health) VALUES (?, ?, ?)", (difficulty, balance, health)); return int(cursor.lastrowid)

def save_transactions(game_id: int, transactions: list[dict[str, Any]]) -> None:
    with connect() as conn:
        conn.executemany("INSERT INTO transactions (game_id,day,category,description,amount,type,need_or_want) VALUES (?,?,?,?,?,?,?)", [(game_id,t["day"],t["category"],t["description"],t["amount"],t["type"],t["need_or_want"]) for t in transactions])

def save_daily_status(game_id: int, state: Any) -> None:
    """Persist the recorded daily snapshots for an end-of-game audit."""
    with connect() as conn:
        conn.executemany("INSERT INTO daily_status (game_id,day,balance,savings,debt,health,stress,happiness,academic) VALUES (?,?,?,?,?,?,?,?,?)", [(game_id, entry["day"], entry["balance"], state.savings, state.debt, state.health_history[min(max(entry["day"]-1, 0), len(state.health_history)-1)] if state.health_history else state.financial_health, state.stress, state.happiness, state.academic_performance) for entry in state.balance_history])
        conn.executemany("INSERT INTO achievements (game_id,achievement_id) VALUES (?,?)", [(game_id, achievement) for achievement in state.achievements])
