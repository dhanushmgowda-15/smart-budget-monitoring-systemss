# SpendSense: Smart Budget Monitoring System with Threshold Alerts

**Project ID:** CP-002 | **Level:** Foundation | **Domain:** Banking and FinTech

A command-line expense tracker that warns you *before* a budget is crossed. Most students and young professionals run out of money before month-end without knowing where it went. SpendSense lets you set a budget for each category, log expenses as they happen, and get alerts at 80% and 100% of every budget.

## Features

### Core (all 5 implemented)

| # | Feature | Where in the menu |
|---|---------|-------------------|
| 1 | Add an expense with date, category, amount and a short note | Option 1 |
| 2 | Set a monthly budget for each category | Option 2 |
| 3 | Warn when a category crosses 80% of its budget, and again at 100% | Automatic after every expense |
| 4 | Month summary: total spent per category against budget | Option 3 |
| 5 | List the 5 largest expenses of the month | Option 4 |

### Stretch (both implemented)

- **Month-over-month comparison:** category-by-category change versus last month (Option 5)
- **CSV export:** save any month's expenses to `expenses_YYYY-MM.csv` (Option 6)

## Requirements

- Python 3.8 or newer
- No external libraries (standard library only: `json`, `csv`, `datetime`, `os`)

## How to Run

```bash
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>
python spendsense.py
```

On Windows, use `py spendsense.py` if `python` is not recognised. Run it from a terminal, not from an output pane, because the app needs keyboard input.

## Usage

```
=========== SpendSense ===========
1. Add expense
2. Set monthly budget for a category
3. Month summary (spent vs budget)
4. Top 5 largest expenses of the month
5. Compare with last month
6. Export month to CSV
0. Exit
```

Typical flow: set budgets with option 2, then log expenses with option 1 as you spend. Dates use `YYYY-MM-DD` (press Enter for today) and months use `YYYY-MM` (press Enter for the current month). Category names are case-insensitive, so `food` and `Food` are the same category.

## Sample Output

**Threshold alerts (shown right after adding an expense):**

```
Saved: 2026-11-05 | Food | 150.00 | Snacks
** WARNING: 'Food' has crossed 80% of its budget (850.00 / 1000.00) for 2026-11.

Saved: 2026-11-09 | Transport | 520.00 | Metro pass
!!! ALERT: 'Transport' has crossed 100% of its budget (520.00 / 500.00) for 2026-11.
```

**Month summary:**

```
Summary for 2026-11
Category            Spent    Budget    Used  Status
--------------------------------------------------------
Food               850.00   1000.00     85%  WARNING
Transport          520.00    500.00    104%  OVER BUDGET
--------------------------------------------------------
TOTAL             1370.00   1500.00
```

**Top expenses:**

```
Largest expenses in 2026-11
#  Date        Category           Amount  Note
--------------------------------------------------------
1  2026-11-02  Food               700.00  Lunch with team
2  2026-11-09  Transport          520.00  Metro pass
3  2026-11-05  Food               150.00  Snacks
```

## How It Works

- **Aggregation by category:** `spent_by_category()` walks the expense list for a month and builds a dictionary of running totals per category.
- **Threshold alerts:** `check_alerts()` compares the category total *before* and *after* the new expense. Each threshold fires exactly once, at the moment it is crossed. If you stay over budget, later expenses show a reminder instead of repeating the original alert.
- **Sorting by amount:** the top 5 list uses `list.sort(key=..., reverse=True)` on the month's expenses.
- **Date handling:** dates are validated with `datetime.strptime`. Expenses are grouped by a `YYYY-MM` month key, and `prev_month()` handles the January to December rollover for the comparison feature.
- **Persistence:** all data is stored in `spendsense_data.json` (created automatically in the working directory), so budgets and expenses survive between runs.

## Project Structure

```
.
├── spendsense.py            # the whole application
├── spendsense_data.json     # created on first run (budgets + expenses)
├── expenses_YYYY-MM.csv     # created when you export a month
└── README.md
```

## Data Format

```json
{
  "budgets": { "Food": 1000.0, "Transport": 500.0 },
  "expenses": [
    { "date": "2026-11-02", "category": "Food", "amount": 700.0, "note": "Lunch with team" }
  ]
}
```

## Possible Improvements

- Edit and delete expenses
- Recurring expenses such as rent and subscriptions
- Configurable alert thresholds
- Charts of spending by category
- A simple GUI or web front end

## Author

Your Name | Your College / Institute

## License

Add a license of your choice (for example MIT) before publishing.
