from collections import defaultdict
from datetime import date

balances = defaultdict(float)
daily_stats = defaultdict(lambda: defaultdict(float))
monthly_stats = defaultdict(lambda: defaultdict(float))

def update_balance(user_id: int, amount: float):
    today = date.today().isoformat()
    month = today[:7]

    balances[user_id] += amount
    daily_stats[user_id][today] += amount
    monthly_stats[user_id][month] += amount
