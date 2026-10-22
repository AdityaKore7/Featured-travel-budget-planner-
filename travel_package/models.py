"""Trip class (Object Oriented Programming)."""

from datetime import datetime

from .calculation import percent_of, cost_per_day, cost_per_person


class Trip:
    def __init__(self, destination, days, travellers, travel, hotel, food,
                 misc=0.0, emergency=0.0, budget_limit=None,
                 created=None, trip_id=None):
        self.destination = destination
        self.days = days
        self.travellers = travellers
        self.travel = travel
        self.hotel = hotel
        self.food = food
        self.misc = misc
        self.emergency = emergency          # emergency money in PERCENT
        self.budget_limit = budget_limit    # None means no limit
        self.created = created or datetime.now().strftime("%d-%m-%Y %H:%M")
        self.trip_id = trip_id              # id in the database (None = not saved)

    def subtotal(self):
        # all costs before emergency money
        return self.travel + self.hotel + self.food + self.misc

    def emergency_amount(self):
        # emergency percent converted into rupees
        return round(percent_of(self.subtotal(), self.emergency), 2)

    def total(self):
        # subtotal + emergency money
        return round(self.subtotal() + self.emergency_amount(), 2)

    def per_day(self):
        return round(cost_per_day(self.total(), self.days), 2)

    def per_person(self):
        return round(cost_per_person(self.total(), self.travellers), 2)

    def status(self):
        # tells if the trip is inside the budget limit
        if self.budget_limit is None:
            return "No budget limit set"
        difference = self.budget_limit - self.total()
        if difference >= 0:
            return f"Within budget (Rs. {difference:,.2f} left)"
        return f"Over budget (by Rs. {-difference:,.2f})"
