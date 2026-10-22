"""
Smart Travel Planner - Semester V Python Project

    Tab 1 - Plan Trip   : enter trip costs + emergency money, calculate the budget
    Tab 2 - Saved Trips : see, search, edit and delete saved trips (SQLite database)
    Tab 3 - Charts      : graphs of the trip plan (matplotlib)
    Tab 4 - Statistics  : totals, averages, budget summary, expense totals (NumPy)
"""

import tkinter as tk
from tkinter import ttk, messagebox

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from travel_package import (
    Trip, init_database, load_trips, save_trip, update_trip, delete_trip,
    get_destination_names, get_destination_costs, estimate_costs,
    trip_stats, destination_summary,
    draw_message, draw_expense_pie, draw_budget_bar, draw_compare_bar,
)
# these names are made available by travel_package/__init__.py

current_trip = None      # the trip made by the last click on "Calculate"
editing_id = None        # database id of the saved trip being edited (None = new trip)
editing_created = None   # original saved date of that trip


# ---------------------------------------------------------------
#  Small helper functions
# ---------------------------------------------------------------
def show_number(value):
    """5000.0 -> '5000'  (looks nicer inside the input boxes)."""
    if isinstance(value, float) and value == int(value):
        return str(int(value))
    return str(value)


def set_entry(box, value):
    """Put a value into an input box (empty box if value is None)."""
    box.delete(0, tk.END)
    if value is not None:
        box.insert(0, show_number(value))


def leave_edit_mode():
    """Go back to normal 'new trip' mode."""
    global editing_id, editing_created
    editing_id = None
    editing_created = None
    edit_label.config(text="")
    save_button.config(text="Save Trip")


# ---------------------------------------------------------------
#  Plan Trip tab
# ---------------------------------------------------------------
def calculate():
    """Calculate button: read the boxes and show the budget."""
    global current_trip

    try:
        destination = destination_entry.get().strip()
        if destination == "":
            raise ValueError

        days = int(days_entry.get())
        travellers = int(travellers_entry.get())
        travel = float(travel_entry.get())
        hotel = float(hotel_entry.get())
        food = float(food_entry.get())

        misc_text = misc_entry.get().strip()
        if misc_text == "":             # miscellaneous is optional
            misc_text = "0"
        misc = float(misc_text)

        emergency_text = emergency_entry.get().strip()
        if emergency_text == "":        # emergency money is optional
            emergency_text = "0"
        emergency = float(emergency_text)

        limit_text = limit_entry.get().strip()
        if limit_text == "":            # budget limit is optional
            limit = None
        else:
            limit = float(limit_text)

        # values that make no sense
        if days < 1 or travellers < 1:
            raise ValueError
        if travel < 0 or hotel < 0 or food < 0 or misc < 0 or emergency < 0:
            raise ValueError
        if limit is not None and limit < 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter valid values")
        return

    current_trip = Trip(destination, days, travellers, travel, hotel, food,
                        misc, emergency, limit,
                        created=editing_created, trip_id=editing_id)

    status = current_trip.status()
    colour = "black"
    if "Over budget" in status:
        colour = "red"

    result_label.config(fg=colour, text=(
        f"Destination : {current_trip.destination}\n"
        f"Days        : {current_trip.days}\n"
        f"Travellers  : {current_trip.travellers}\n"
        f"Subtotal    : Rs. {current_trip.subtotal():,.2f}\n"
        f"Emergency   : Rs. {current_trip.emergency_amount():,.2f} "
        f"({current_trip.emergency}%)\n"
        f"Total       : Rs. {current_trip.total():,.2f}\n"
        f"Per day     : Rs. {current_trip.per_day():,.2f}\n"
        f"Per person  : Rs. {current_trip.per_person():,.2f}\n"
        f"Status      : {status}"))


def suggest_costs():
    """Suggest Costs button: fill travel, hotel and food from the dataset."""
    name = destination_entry.get().strip()

    try:
        days = int(days_entry.get())
        travellers = int(travellers_entry.get())
        if days < 1 or travellers < 1:
            raise ValueError
    except ValueError:
        messagebox.showerror("Invalid Input",
                             "Enter valid Days and Travellers first.")
        return

    costs = get_destination_costs(name)         # looks in the database
    if costs is None:
        messagebox.showwarning("Not Found",
                               "This destination is not in the dataset.")
        return

    hotel_per_day, food_per_day, travel_per_day = costs
    travel, hotel, food = estimate_costs(hotel_per_day, food_per_day,
                                         travel_per_day, days, travellers)
    set_entry(travel_entry, travel)
    set_entry(hotel_entry, hotel)
    set_entry(food_entry, food)

    messagebox.showinfo("Estimate Ready",
                        "Costs filled from the dataset (approximate).\n"
                        "You can change them before clicking Calculate.")


def save():
    """Save / Update button: store the trip in the database."""
    if current_trip is None:
        messagebox.showwarning("No Data", "Calculate the budget first.")
        return

    if current_trip.trip_id is None:
        save_trip(current_trip)                     # new trip
        messagebox.showinfo("Success", "Trip saved!")
    else:
        update_trip(current_trip.trip_id, current_trip)    # existing trip
        messagebox.showinfo("Success", "Trip updated!")

    leave_edit_mode()
    show_saved()


def clear():
    """Clear button: empty all boxes (also cancels editing)."""
    global current_trip

    for box in all_entries:
        box.delete(0, tk.END)

    current_trip = None
    leave_edit_mode()
    result_label.config(text="Enter trip details and click Calculate", fg="black")


# ---------------------------------------------------------------
#  Saved Trips tab
# ---------------------------------------------------------------
def show_saved(*args):
    """Fill the table with the saved trips that match the search text."""
    for row in table.get_children():
        table.delete(row)

    keyword = search_var.get().strip().lower()

    for trip in load_trips():
        if keyword in trip.destination.lower():
            # row id = the trip's id in the database (used for edit and delete)
            table.insert("", "end", iid=str(trip.trip_id), values=(
                trip.destination, trip.days, trip.travellers,
                f"{trip.total():,.2f}", trip.created))


def edit_selected():
    """Edit Selected button: load the chosen trip into the Plan Trip tab."""
    global editing_id, editing_created, current_trip

    selected = table.selection()
    if not selected:
        messagebox.showwarning("No Selection", "Select a trip to edit.")
        return

    trip_id = int(selected[0])
    chosen = None
    for trip in load_trips():
        if trip.trip_id == trip_id:
            chosen = trip
    if chosen is None:
        return

    # fill the boxes (same order as the boxes on the screen)
    values = [chosen.destination, chosen.days, chosen.travellers, chosen.travel,
              chosen.hotel, chosen.food, chosen.misc, chosen.emergency,
              chosen.budget_limit]
    for i in range(len(all_entries)):
        set_entry(all_entries[i], values[i])

    editing_id = trip_id
    editing_created = chosen.created
    current_trip = None         # must click Calculate again before updating

    edit_label.config(text=f"Editing saved trip: {chosen.destination}  "
                           f"(change values, Calculate, then Update Trip)")
    save_button.config(text="Update Trip")
    result_label.config(text="Change the values and click Calculate", fg="black")
    tabs.select(plan_tab)


def delete_selected():
    """Delete Selected button: remove the chosen trip."""
    selected = table.selection()

    if not selected:
        messagebox.showwarning("No Selection", "Select a trip to delete.")
        return

    trip_id = int(selected[0])
    delete_trip(trip_id)
    if editing_id == trip_id:
        leave_edit_mode()
    show_saved()


# ---------------------------------------------------------------
#  Charts tab
# ---------------------------------------------------------------
def show_expense_chart():
    """Pie chart of the calculated trip."""
    if current_trip is None:
        messagebox.showwarning("No Data", "Calculate the budget first.")
        return
    draw_expense_pie(figure, current_trip)
    canvas.draw()


def show_budget_chart():
    """Bar chart of the calculated trip with the budget limit line."""
    if current_trip is None:
        messagebox.showwarning("No Data", "Calculate the budget first.")
        return
    draw_budget_bar(figure, current_trip)
    canvas.draw()


def show_compare_chart():
    """Bar chart comparing all saved trips."""
    draw_compare_bar(figure, load_trips())
    canvas.draw()


def show_chart_from_plan():
    """Show Chart button on the Plan Trip tab: open the pie chart."""
    if current_trip is None:
        messagebox.showwarning("No Data", "Calculate the budget first.")
        return
    show_expense_chart()
    tabs.select(charts_tab)


# ---------------------------------------------------------------
#  Statistics tab
# ---------------------------------------------------------------
def show_stats():
    """Fill the Statistics tab (numbers are calculated by trip_stats with NumPy)."""
    trips = load_trips()

    for row in stats_table.get_children():      # clear the destination table
        stats_table.delete(row)

    if len(trips) == 0:
        stats_left.config(text="No saved trips yet.")
        stats_right.config(text="")
        return

    s = trip_stats(trips)

    stats_left.config(text=(
        "OVERVIEW\n"
        f"Trips saved          : {s['count']}\n"
        f"Total spending       : Rs. {s['total']:,.2f}\n"
        f"Average trip cost    : Rs. {s['average']:,.2f}\n"
        f"Median trip cost     : Rs. {s['median']:,.2f}\n"
        f"Cheapest trip        : {s['cheapest'].destination} (Rs. {s['minimum']:,.2f})\n"
        f"Costliest trip       : {s['costliest'].destination} (Rs. {s['maximum']:,.2f})\n"
        f"Longest trip         : {s['longest'].destination} ({s['longest'].days} days)\n"
        f"Most visited         : {s['top_destination']} ({s['top_count']} trips)\n"
        "\n"
        "DAYS AND PEOPLE\n"
        f"Total days travelled : {s['total_days']}\n"
        f"Average trip length  : {s['average_days']:.1f} days\n"
        f"Average cost per day : Rs. {s['cost_per_day']:,.2f}\n"
        f"Average per person   : Rs. {s['average_per_person']:,.2f}"))

    # percentage of every expense type in the total spending
    expense_text = ""
    for name in s["categories"]:
        amount = s["categories"][name]
        percent = amount / s["total"] * 100
        expense_text += f"{name:<16}: Rs. {amount:>11,.2f} ({percent:.1f}%)\n"

    stats_right.config(text=(
        "BUDGET\n"
        f"Within budget : {s['within']} trips\n"
        f"Over budget   : {s['over']} trips\n"
        f"No limit set  : {s['no_limit']} trips\n"
        "\n"
        "EMERGENCY MONEY\n"
        f"Average set aside : {s['average_emergency']:.1f}%\n"
        "\n"
        "EXPENSE TOTALS (all trips)\n" + expense_text))

    for name, count, total, average in destination_summary(trips):
        stats_table.insert("", "end", values=(
            name, count, f"{total:,.2f}", f"{average:,.2f}"))


def tab_changed(event):
    """Refresh the data when the user opens a tab."""
    tab_name = tabs.tab(tabs.select(), "text")

    if tab_name == "Saved Trips":
        show_saved()
    elif tab_name == "Statistics":
        show_stats()


# ---------------------------------------------------------------
#  Window
# ---------------------------------------------------------------
init_database()         # create the tables and load destinations.csv

root = tk.Tk()
root.title("Smart Travel Planner")
root.geometry("900x720")

tk.Label(root, text="SMART TRAVEL PLANNER",
         font=("Arial", 18, "bold")).pack(pady=10)

tabs = ttk.Notebook(root)
tabs.pack(fill="both", expand=True, padx=10, pady=5)

plan_tab = tk.Frame(tabs)
saved_tab = tk.Frame(tabs)
charts_tab = tk.Frame(tabs)
stats_tab = tk.Frame(tabs)

tabs.add(plan_tab, text="Plan Trip")
tabs.add(saved_tab, text="Saved Trips")
tabs.add(charts_tab, text="Charts")
tabs.add(stats_tab, text="Statistics")
tabs.bind("<<NotebookTabChanged>>", tab_changed)


# ---- Plan Trip tab screen ----
edit_label = tk.Label(plan_tab, text="", fg="blue", font=("Arial", 10, "bold"))
edit_label.pack(pady=(8, 0))

form = tk.Frame(plan_tab)
form.pack(pady=8)

labels = ["Destination", "Days", "Travellers", "Travel Cost (Rs.)",
          "Hotel Cost (Rs.)", "Food Cost (Rs.)", "Miscellaneous (Rs.)",
          "Emergency Money (%)", "Budget Limit (optional)"]
all_entries = []

for row in range(len(labels)):      # one label and one input box per row
    tk.Label(form, text=labels[row], width=20, anchor="w").grid(row=row, column=0, pady=4)
    if row == 0:
        # destination: drop-down list filled from the database (you can also type)
        box = ttk.Combobox(form, width=23, values=get_destination_names())
    else:
        box = tk.Entry(form, width=25)
    box.grid(row=row, column=1, pady=4)
    all_entries.append(box)

destination_entry = all_entries[0]
days_entry = all_entries[1]
travellers_entry = all_entries[2]
travel_entry = all_entries[3]
hotel_entry = all_entries[4]
food_entry = all_entries[5]
misc_entry = all_entries[6]
emergency_entry = all_entries[7]
limit_entry = all_entries[8]

buttons = tk.Frame(plan_tab)
buttons.pack(pady=8)

tk.Button(buttons, text="Suggest Costs", width=13, command=suggest_costs).grid(row=0, column=0, padx=4)
tk.Button(buttons, text="Calculate", width=13, command=calculate).grid(row=0, column=1, padx=4)
save_button = tk.Button(buttons, text="Save Trip", width=13, command=save)
save_button.grid(row=0, column=2, padx=4)
tk.Button(buttons, text="Show Chart", width=13, command=show_chart_from_plan).grid(row=0, column=3, padx=4)
tk.Button(buttons, text="Clear", width=13, command=clear).grid(row=0, column=4, padx=4)

result_label = tk.Label(plan_tab, text="Enter trip details and click Calculate",
                        justify="left", font=("Consolas", 11), anchor="nw")
result_label.pack(fill="both", expand=True, padx=20, pady=8)


# ---- Saved Trips tab screen ----
search_frame = tk.Frame(saved_tab)
search_frame.pack(fill="x", padx=8, pady=8)

tk.Label(search_frame, text="Search destination:").pack(side="left")

search_var = tk.StringVar()
search_var.trace_add("write", show_saved)       # runs when the text changes
tk.Entry(search_frame, textvariable=search_var, width=25).pack(side="left", padx=6)

table = ttk.Treeview(
    saved_tab, columns=("destination", "days", "people", "total", "date"),
    show="headings", height=14)

table.heading("destination", text="Destination")
table.heading("days", text="Days")
table.heading("people", text="People")
table.heading("total", text="Total (Rs.)")
table.heading("date", text="Saved On")

table.column("days", width=60, anchor="center")
table.column("people", width=60, anchor="center")
table.pack(fill="both", expand=True, padx=8, pady=8)

table_buttons = tk.Frame(saved_tab)
table_buttons.pack(pady=5)
tk.Button(table_buttons, text="Edit Selected", width=15, command=edit_selected).grid(row=0, column=0, padx=5)
tk.Button(table_buttons, text="Delete Selected", width=15, command=delete_selected).grid(row=0, column=1, padx=5)


# ---- Charts tab screen ----
chart_buttons = tk.Frame(charts_tab)
chart_buttons.pack(pady=8)

tk.Button(chart_buttons, text="Expense Split (Pie)", width=20, command=show_expense_chart).grid(row=0, column=0, padx=4)
tk.Button(chart_buttons, text="Budget vs Total (Bar)", width=20, command=show_budget_chart).grid(row=0, column=1, padx=4)
tk.Button(chart_buttons, text="Compare Saved Trips", width=20, command=show_compare_chart).grid(row=0, column=2, padx=4)

figure = Figure(figsize=(6, 4.5), dpi=100)      # the drawing area
canvas = FigureCanvasTkAgg(figure, master=charts_tab)
canvas.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=8)

draw_message(figure, "Calculate a trip on the Plan Trip tab,\nthen choose a chart.")
canvas.draw()


# ---- Statistics tab screen ----
stats_top = tk.Frame(stats_tab)
stats_top.pack(fill="x", padx=15, pady=10)

stats_left = tk.Label(stats_top, justify="left", font=("Consolas", 10), anchor="nw")
stats_left.pack(side="left", anchor="n", padx=(0, 30))

stats_right = tk.Label(stats_top, justify="left", font=("Consolas", 10), anchor="nw")
stats_right.pack(side="left", anchor="n")

tk.Label(stats_tab, text="DESTINATION-WISE SUMMARY",
         font=("Consolas", 10, "bold")).pack(anchor="w", padx=15)

stats_table = ttk.Treeview(
    stats_tab, columns=("destination", "trips", "total", "average"),
    show="headings", height=6)

stats_table.heading("destination", text="Destination")
stats_table.heading("trips", text="Trips")
stats_table.heading("total", text="Total Spent (Rs.)")
stats_table.heading("average", text="Average Cost (Rs.)")

stats_table.column("trips", width=60, anchor="center")
stats_table.pack(fill="both", expand=True, padx=15, pady=(4, 10))


root.mainloop()
