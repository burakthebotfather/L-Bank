import matplotlib.pyplot as plt


def build_daily_chart(daily_data: dict, user_id: int):
    dates = sorted(daily_data[user_id].keys())
    values = [daily_data[user_id][d] for d in dates]

    if not dates:
        return None

    plt.figure()
    plt.plot(dates, values)
    plt.xticks(rotation=45)
    plt.title("Дневной баланс")
    plt.tight_layout()

    filename = f"daily_{user_id}.png"
    plt.savefig(filename)
    plt.close()

    return filename
