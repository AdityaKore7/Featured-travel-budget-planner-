"""
Database handling (SQLite - built into Python, no installation needed).

travel.db has two tables:
    trips        - all saved trips
    destinations - sample cost dataset, loaded from destinations.csv
"""

import csv
import os
import sqlite3

from .models import Trip

project_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_FILE = os.path.join(project_folder, "travel.db")
CSV_FILE = os.path.join(project_folder, "destinations.csv")


def connect():
    return sqlite3.connect(DB_FILE)


def init_database():
    """Create the tables (if needed) and load the dataset from the CSV file."""
    conn = connect()

    conn.execute("""CREATE TABLE IF NOT EXISTS trips (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        destination TEXT, days INTEGER, travellers INTEGER,
                        travel REAL, hotel REAL, food REAL, misc REAL,
                        emergency REAL, budget_limit REAL, created TEXT)""")

    conn.execute("""CREATE TABLE IF NOT EXISTS destinations (
                        name TEXT PRIMARY KEY COLLATE NOCASE,
                        hotel_per_day REAL, food_per_day REAL,
                        travel_per_day REAL)""")

    # reload the dataset every time, so edits in destinations.csv are picked up
    if os.path.exists(CSV_FILE):
        conn.execute("DELETE FROM destinations")
        with open(CSV_FILE, newline="", encoding="utf-8-sig") as file:
            for row in csv.DictReader(file):
                try:
                    conn.execute(
                        "INSERT OR REPLACE INTO destinations "
                        "(name, hotel_per_day, food_per_day, travel_per_day) "
                        "VALUES (?, ?, ?, ?)",
                        (row["destination"].strip(),
                         float(row["hotel_per_day"]),
                         float(row["food_per_day"]),
                         float(row["travel_per_day"])))
                except (KeyError, ValueError, AttributeError):
                    pass        # skip a damaged row

    conn.commit()
    conn.close()


def trip_values(trip):
    # the values of a Trip in the same order as the table columns
    return (trip.destination, trip.days, trip.travellers, trip.travel,
            trip.hotel, trip.food, trip.misc, trip.emergency,
            trip.budget_limit, trip.created)


def load_trips():
    # returns a list of Trip objects (oldest first)
    conn = connect()
    rows = conn.execute(
        "SELECT id, destination, days, travellers, travel, hotel, food, misc, "
        "emergency, budget_limit, created FROM trips ORDER BY id").fetchall()
    conn.close()

    trips = []
    for row in rows:
        trips.append(Trip(destination=row[1], days=row[2], travellers=row[3],
                          travel=row[4], hotel=row[5], food=row[6], misc=row[7],
                          emergency=row[8], budget_limit=row[9],
                          created=row[10], trip_id=row[0]))
    return trips


def save_trip(trip):
    # adds a NEW trip and stores its database id in trip.trip_id
    conn = connect()
    cursor = conn.execute(
        "INSERT INTO trips (destination, days, travellers, travel, hotel, "
        "food, misc, emergency, budget_limit, created) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", trip_values(trip))
    trip.trip_id = cursor.lastrowid
    conn.commit()
    conn.close()


def update_trip(trip_id, trip):
    # changes an already saved trip
    conn = connect()
    conn.execute(
        "UPDATE trips SET destination=?, days=?, travellers=?, travel=?, "
        "hotel=?, food=?, misc=?, emergency=?, budget_limit=?, created=? "
        "WHERE id=?", trip_values(trip) + (trip_id,))
    trip.trip_id = trip_id
    conn.commit()
    conn.close()


def delete_trip(trip_id):
    conn = connect()
    conn.execute("DELETE FROM trips WHERE id=?", (trip_id,))
    conn.commit()
    conn.close()


def get_destination_names():
    # all destination names of the dataset (for the drop-down list)
    conn = connect()
    rows = conn.execute("SELECT name FROM destinations ORDER BY name").fetchall()
    conn.close()
    return [row[0] for row in rows]


def get_destination_costs(name):
    # returns (hotel_per_day, food_per_day, travel_per_day) or None if not found
    conn = connect()
    row = conn.execute(
        "SELECT hotel_per_day, food_per_day, travel_per_day "
        "FROM destinations WHERE name = ?", (name,)).fetchone()
    conn.close()
    return row
