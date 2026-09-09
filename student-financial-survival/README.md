# Student Financial Survival Simulator

## Overview

**Can you survive 30 days without going broke?** This interactive Streamlit game puts students in charge of a monthly budget. Balance essentials, unexpected events, academic performance, stress, and happiness to finish the month financially healthy.

## Features

- 30-day playable financial simulation with four difficulty levels
- Budget planning, daily food costs, debt, savings, emergency reserve, and needs-vs-wants tracking
- 20 JSON-powered random events with consequential choices
- Financial-health score built from savings, spending control, emergency readiness, debt, and cash stability
- Academic performance, stress, happiness, six endings, and ten achievements
- SQLite persistence, CSV transaction export, Plotly dashboard, and pytest tests

## Gameplay

Choose a difficulty and set your category budgets. Each day, pay a variable food cost, make an event decision when one appears, and protect your cash. Reaching day 30 produces a detailed report; running out of cash and taking debt ends the game.

Example: on day 8, accept a Rp100,000 freelance gig. You gain money, but stress rises by 10 and academic performance drops by 3. Is it worth it?

## Tech Stack

Python 3.11+, Streamlit, SQLite, Pandas, Plotly, and pytest.

## Project Structure

```
student-financial-survival/
├── app.py                 # Streamlit UI
├── modules/               # Domain/game rules
├── database/              # SQLite repository
├── data/                  # Events and achievements
├── utils/                 # Formatting helpers
└── tests/                 # Unit tests
```

## How It Works

The UI stores a `PlayerState` in Streamlit session state. Reusable modules apply transactions and events, calculate health and endings, then send completed-game data to SQLite. Events and achievements live in editable JSON files.

## Installation

```bash
git clone <your-repository-url>
cd student-financial-survival
python -m venv .venv
```

Activate the virtual environment, then run:

```bash
pip install -r requirements.txt
```

## How to Run

```bash
streamlit run app.py
```

## Screenshots

_Add dashboard and final-report screenshots here._

## Testing

```bash
pytest
```

## Future Improvements

- User profiles and a leaderboard
- More localised scenarios and events
- Cloud deployment and saved-game continuation

## License

Released under the [MIT License](LICENSE).
