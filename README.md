# Smart Travel Planner

A Python desktop application that helps you plan a trip budget. Enter your travel, hotel and food costs, add emergency money as a percentage, and the app calculates the total cost, cost per day and cost per person. Trips are saved in a database, can be edited later, and are shown in charts and statistics.

Built as a **Semester V Python Programming** project using Tkinter, SQLite, NumPy and matplotlib.

---

## Features

### Plan Trip
- Choose a destination from a drop-down list (loaded from the dataset) or type your own
- **Suggest Costs** button fills travel, hotel and food costs from the dataset using your days and travellers
- Enter days, travellers, travel, hotel, food and miscellaneous costs
- **Emergency money (%)** is added on top of the costs and included in the total
- Optional **budget limit**: the app tells you if you are within budget or over it (shown in red)
- Shows subtotal, emergency money, total, cost per day and cost per person
- Input validation with clear error messages

### Saved Trips
- All trips are stored in an SQLite database
- Search saved trips by destination
- **Edit** a saved trip: load it back into the form, change values and update it
- **Delete** a saved trip

### Charts
- **Expense split** (pie chart) of the calculated trip
- **Budget vs total** (bar chart) with a red budget-limit line
- **Compare saved trips** (bar chart) with an average line
- A **Show Chart** button on the Plan Trip tab opens the chart of your current plan

### Statistics
- Number of trips, total spending, average and median trip cost
- Cheapest, costliest and longest trip, and the most visited destination
- Total days travelled, average trip length, average cost per day and per person
- Number of trips within budget, over budget and without a limit
- Average emergency money percentage
- Total spent on each expense type with percentages
- Destination-wise summary table (trips, total spent, average cost)

---

## Technologies Used

| Technology | Used for |
|---|---|
| Python 3.8+ | Main programming language |
| Tkinter / ttk | Graphical user interface |
| SQLite (`sqlite3`) | Database for saved trips and the destinations dataset |
| CSV (`csv`) | Destinations dataset file |
| NumPy | Statistics calculations |
| matplotlib | Charts shown inside the app |

## Python Concepts Covered

- Modules and packages (`travel_package`)
- Object Oriented Programming (`Trip` class)
- Database handling with SQLite (create, insert, read, update, delete)
- File handling (reading the CSV dataset)
- Exception handling (`try / except`)
- NumPy arrays and functions
- Data visualization with matplotlib
- GUI programming with Tkinter

---

## Project Structure

```
smart_travel_planner/
├── main.py                  # GUI (all four tabs) - run this file
├── destinations.csv         # Dataset: sample daily costs per destination
├── requirements.txt         # Libraries needed
├── README.md
└── travel_package/
    ├── __init__.py          # Makes the folder a package, exports the functions
    ├── calculation.py       # Budget formulas and statistics (NumPy)
    ├── models.py            # Trip class
    ├── storage.py           # SQLite database functions
    └── charts.py            # matplotlib chart functions
```

`travel.db` is created automatically the first time you run the program.

---

## Installation and Running

**1. Install Python 3.8 or newer** from [python.org](https://www.python.org/downloads/). Tkinter and SQLite are included with the standard installer.

**2. Download the project**
```bash
git clone https://github.com/your-username/smart-travel-planner.git
cd smart-travel-planner
```

**3. Install the required libraries**
```bash
pip install -r requirements.txt
```

**4. Run the application**
```bash
python main.py
```

> Run `main.py` only. The files inside `travel_package` are meant to be imported, and running them directly gives an "attempted relative import" error.

---

## How to Use

1. Open the **Plan Trip** tab.
2. Select or type a destination, then enter the number of days and travellers.
3. Click **Suggest Costs** to fill the costs from the dataset, or type your own.
4. Enter miscellaneous cost, emergency money % and an optional budget limit.
5. Click **Calculate** to see the budget.
6. Click **Save Trip** to store it, or **Show Chart** to see the expense split.
7. Open **Saved Trips** to search, edit or delete trips.
8. Open **Charts** and **Statistics** for graphs and summaries.

To edit a trip: select it in **Saved Trips**, click **Edit Selected**, change the values, click **Calculate**, then **Update Trip**.

---

## How the Calculations Work

```
Subtotal         = Travel + Hotel + Food + Miscellaneous
Emergency money  = Subtotal x Emergency % / 100
Total cost       = Subtotal + Emergency money
Cost per day     = Total / Days
Cost per person  = Total / Travellers
```

**Example:** Goa, 4 days, 2 travellers, travel 5,000, hotel 8,000, food 3,000, miscellaneous 1,000, emergency 10%.

| Item | Amount (Rs.) |
|---|---|
| Subtotal | 17,000 |
| Emergency money (10%) | 1,700 |
| **Total** | **18,700** |
| Per day | 4,675 |
| Per person | 9,350 |

**Suggest Costs** uses the dataset values (per person, per day):
`Hotel = hotel_per_day x days x travellers` (the same formula is used for food and travel).

---

## Database and Dataset

The project uses one SQLite file, `travel.db`, with two tables:

| Table | Purpose |
|---|---|
| `trips` | Every saved trip (destination, days, travellers, costs, emergency %, budget limit, saved date) |
| `destinations` | The dataset used by the drop-down list and **Suggest Costs** |

The dataset comes from `destinations.csv` and is reloaded every time the program starts:

```csv
destination,hotel_per_day,food_per_day,travel_per_day
Goa,1500,700,400
Manali,1200,600,500
```

To add a destination, add a new line to the CSV file and restart the program.

> **Note:** the costs in `destinations.csv` are approximate sample values for demonstration, not verified prices. Replace them with real data if needed.

---

## Screenshots

Add your screenshots to a `screenshots` folder and link them here:

```markdown
![Plan Trip](screenshots/plan_trip.png)
![Saved Trips](screenshots/saved_trips.png)
![Charts](screenshots/charts.png)
![Statistics](screenshots/statistics.png)
```

---

## Troubleshooting

| Problem | Solution |
|---|---|
| `ModuleNotFoundError: matplotlib` or `numpy` | Run `pip install -r requirements.txt` |
| `No module named 'tkinter'` | Reinstall Python and keep "tcl/tk and IDLE" selected |
| `No module named 'travel_package'` | Run `main.py` from the project folder, next to `travel_package` |
| Destination drop-down is empty | Make sure `destinations.csv` is in the same folder as `main.py` |

---

## Future Improvements

- Export a trip report to PDF or text
- Currency conversion for international trips
- Date-based planning with a day-by-day itinerary
- Login for multiple users
- Online price data instead of a fixed dataset

---

## Author

**Aditya Kore**
Computer Science Engineering student
GitHub: [AdityaKore7](https://github.com/AdityaKore7)

This project was created for educational purposes.

