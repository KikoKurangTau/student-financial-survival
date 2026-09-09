import random
from modules.economy import apply_daily_food, create_state
from modules.events import apply_choice

def test_daily_food_has_valid_range():
    state=create_state("Normal",{"Food":1},300000,500000)
    amount=apply_daily_food(state, rng=random.Random(1))
    assert 25000 <= amount <= 45000

def test_event_consequences_apply():
    state=create_state("Normal",{"Food":1},300000,500000)
    event={"title":"Gig","choices":[{"label":"work","income":100000,"stress":10,"academic":-3}]}
    apply_choice(state,event,0)
    assert state.balance == 2600000 and state.stress == 40 and state.academic_performance == 77
