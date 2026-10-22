"""
Graphs for the Smart Travel Planner (matplotlib).

Every function receives a matplotlib Figure, clears it and draws on it.
main.py shows the Figure inside the Charts tab.
"""

from .calculation import summarize

COLOURS = ["#4C72B0", "#55A868", "#C44E52", "#8172B2", "#CCB974", "#64B5CD"]


def draw_message(fig, text):
    # shows a plain text message instead of a graph
    fig.clear()
    ax = fig.add_subplot(111)
    ax.axis("off")
    ax.text(0.5, 0.5, text, ha="center", va="center", fontsize=12)


def draw_expense_pie(fig, trip):
    # pie chart: how the total budget is divided
    names = ["Travel", "Hotel", "Food", "Miscellaneous", "Emergency money"]
    values = [trip.travel, trip.hotel, trip.food, trip.misc,
              trip.emergency_amount()]

    labels = []
    sizes = []
    colours = []
    for i in range(len(values)):
        if values[i] > 0:               # skip expenses that are zero
            labels.append(names[i])
            sizes.append(values[i])
            colours.append(COLOURS[i])

    if len(sizes) == 0:
        draw_message(fig, "All expenses are zero - nothing to draw.")
        return

    fig.clear()
    ax = fig.add_subplot(111)
    ax.pie(sizes, labels=labels, colors=colours, autopct="%1.1f%%",
           startangle=90)
    ax.set_title(f"Expense Split - {trip.destination}\n"
                 f"Total: Rs. {trip.total():,.2f}")


def draw_budget_bar(fig, trip):
    # bar chart: every expense, the total, and the budget limit line
    names = ["Travel", "Hotel", "Food", "Misc", "Emergency", "Total"]
    values = [trip.travel, trip.hotel, trip.food, trip.misc,
              trip.emergency_amount(), trip.total()]
    colours = COLOURS[:5] + ["#333333"]

    fig.clear()
    ax = fig.add_subplot(111)
    ax.bar(names, values, color=colours)

    for i in range(len(values)):        # write the amount above each bar
        ax.text(i, values[i], f"{values[i]:,.0f}", ha="center", va="bottom")

    if trip.budget_limit is not None:
        ax.axhline(trip.budget_limit, color="red", linestyle="--",
                   label=f"Budget limit: Rs. {trip.budget_limit:,.0f}")
        ax.legend()

    ax.set_ylabel("Amount (Rs.)")
    ax.set_title(f"Budget vs Total - {trip.destination}")
    fig.tight_layout()


def draw_compare_bar(fig, trips):
    # bar chart: total cost of every saved trip + the average line
    if len(trips) == 0:
        draw_message(fig, "No saved trips yet.")
        return

    labels = []
    totals = []
    for trip in trips:
        labels.append(f"{trip.destination}\n({trip.days} days)")
        totals.append(trip.total())

    average = summarize(totals)["average"]      # NumPy

    fig.clear()
    ax = fig.add_subplot(111)
    ax.bar(range(len(totals)), totals, color=COLOURS[0])
    ax.set_xticks(range(len(totals)))
    ax.set_xticklabels(labels, fontsize=8)

    ax.axhline(average, color="orange", linestyle="--",
               label=f"Average: Rs. {average:,.0f}")
    ax.legend()

    ax.set_ylabel("Total cost (Rs.)")
    ax.set_title("Saved Trips - Total Cost Comparison")
    fig.tight_layout()
