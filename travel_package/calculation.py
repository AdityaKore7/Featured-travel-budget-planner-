"""Simple calculations (NumPy is used for the statistics)."""

import numpy as np


def percent_of(amount, percent):
    # example: percent_of(17000, 10) = 1700  (used for emergency money)
    return amount * percent / 100


def cost_per_day(total, days):
    if days > 0:
        return total / days
    return 0.0


def cost_per_person(total, travellers):
    if travellers > 0:
        return total / travellers
    return 0.0


def estimate_costs(hotel_per_day, food_per_day, travel_per_day, days, travellers):
    # costs in the dataset are "per person per day"
    # returns (travel, hotel, food) for the whole trip
    travel = travel_per_day * days * travellers
    hotel = hotel_per_day * days * travellers
    food = food_per_day * days * travellers
    return travel, hotel, food


def summarize(totals):
    # count, average, minimum and maximum of a list of trip totals
    numbers = np.array(totals)
    return {
        "count": len(numbers),
        "average": float(np.mean(numbers)),
        "minimum": float(np.min(numbers)),
        "maximum": float(np.max(numbers)),
    }


def trip_stats(trips):
    # all numbers shown on the Statistics tab (trips = list of Trip objects)
    totals = np.array([t.total() for t in trips])
    days = np.array([t.days for t in trips])

    # cheapest, costliest and longest trip
    cheapest = trips[0]
    costliest = trips[0]
    longest = trips[0]
    for trip in trips:
        if trip.total() < cheapest.total():
            cheapest = trip
        if trip.total() > costliest.total():
            costliest = trip
        if trip.days > longest.days:
            longest = trip

    # how many trips are inside / over the budget limit
    within = 0
    over = 0
    no_limit = 0
    for trip in trips:
        if trip.budget_limit is None:
            no_limit += 1
        elif trip.total() <= trip.budget_limit:
            within += 1
        else:
            over += 1

    # most visited destination ("goa" and "Goa" count as the same place)
    counts = {}
    for trip in trips:
        name = trip.destination.strip().title()
        counts[name] = counts.get(name, 0) + 1
    top_name = max(counts, key=counts.get)

    # money spent on each kind of expense in all trips
    category_totals = {
        "Travel": float(np.sum([t.travel for t in trips])),
        "Hotel": float(np.sum([t.hotel for t in trips])),
        "Food": float(np.sum([t.food for t in trips])),
        "Miscellaneous": float(np.sum([t.misc for t in trips])),
        "Emergency money": float(np.sum([t.emergency_amount() for t in trips])),
    }

    total_spending = float(np.sum(totals))
    total_days = int(np.sum(days))

    return {
        "count": len(trips),
        "total": total_spending,
        "average": float(np.mean(totals)),
        "median": float(np.median(totals)),
        "minimum": float(np.min(totals)),
        "maximum": float(np.max(totals)),
        "cheapest": cheapest,
        "costliest": costliest,
        "longest": longest,
        "top_destination": top_name,
        "top_count": counts[top_name],
        "total_days": total_days,
        "average_days": float(np.mean(days)),
        "cost_per_day": total_spending / total_days,
        "average_per_person": float(np.mean([t.per_person() for t in trips])),
        "within": within,
        "over": over,
        "no_limit": no_limit,
        "average_emergency": float(np.mean([t.emergency for t in trips])),
        "categories": category_totals,
    }


def destination_summary(trips):
    # one row per destination: (name, number of trips, total cost, average cost)
    groups = {}
    for trip in trips:
        name = trip.destination.strip().title()
        if name not in groups:
            groups[name] = []
        groups[name].append(trip.total())

    rows = []
    for name in groups:
        costs = groups[name]
        rows.append((name, len(costs), float(np.sum(costs)), float(np.mean(costs))))

    rows.sort(key=lambda row: row[2], reverse=True)     # biggest spending first
    return rows
