#!/usr/bin/env python3
"""
SpendSense - Smart Budget Monitoring System with Threshold Alerts
Run:  python spendsense.py
Data is saved in spendsense_data.json (same folder), so it persists between runs.
"""

import csv
import json
import os
from datetime import date, datetime

DATA_FILE = "spendsense_data.json"
WARN_AT = 0.80   # 80 percent
LIMIT_AT = 1.00  # 100 percent


# ---------------------------------------------------------------- storage
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            print("Could not read data file, starting fresh.")
    return {"budgets": {}, "expenses": []}


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


# ---------------------------------------------------------------- helpers
def month_key(d):
    """'2026-11-16' -> '2026-11'"""
    return d[:7]


def prev_month(key):
    y, m = map(int, key.split("-"))
    m -= 1
    if m == 0:
        y, m = y - 1, 12
    return f"{y:04d}-{m:02d}"


def ask_date(prompt):
    while True:
        raw = input(prompt).strip()
        if raw == "":
            return date.today().isoformat()
        try:
            return datetime.strptime(raw, "%Y-%m-%d").date().isoformat()
        except ValueError:
            print("  Invalid date. Use YYYY-MM-DD (or press Enter for today).")


def ask_month(prompt):
    while True:
        raw = input(prompt).strip()
        if raw == "":
            return date.today().strftime("%Y-%m")
        try:
            return datetime.strptime(raw, "%Y-%m").strftime("%Y-%m")
        except ValueError:
            print("  Invalid month. Use YYYY-MM (or press Enter for current month).")


def ask_amount(prompt):
    while True:
        raw = input(prompt).strip()
        try:
            value = round(float(raw), 2)
            if value <= 0:
                raise ValueError
            return value
        except ValueError:
            print("  Enter a positive number.")


def ask_category(prompt):
    while True:
        cat = input(prompt).strip().title()
        if cat:
            return cat
        print("  Category cannot be empty.")


def spent_by_category(data, month):
    totals = {}
    for e in data["expenses"]:
        if month_key(e["date"]) == month:
            totals[e["category"]] = totals.get(e["category"], 0) + e["amount"]
    return totals


def status_label(spent, budget):
    if budget is None or budget <= 0:
        return "no budget"
    ratio = spent / budget
    if ratio >= LIMIT_AT:
        return "OVER BUDGET"
    if ratio >= WARN_AT:
        return "WARNING"
    return "ok"


# ---------------------------------------------------------------- features
def add_expense(data):
    print("\n--- Add Expense ---")
    d = ask_date("Date (YYYY-MM-DD, Enter = today): ")
    cat = ask_category("Category: ")
    amount = ask_amount("Amount: ")
    note = input("Short note: ").strip()

    month = month_key(d)
    before = spent_by_category(data, month).get(cat, 0)

    data["expenses"].append(
        {"date": d, "category": cat, "amount": amount, "note": note}
    )
    save_data(data)
    print(f"Saved: {d} | {cat} | {amount:.2f} | {note}")

    check_alerts(data, cat, month, before, before + amount)


def check_alerts(data, cat, month, before, after):
    budget = data["budgets"].get(cat)
    if not budget:
        print(f"(No budget set for '{cat}'. Use option 2 to set one.)")
        return

    pct_before = before / budget
    pct_after = after / budget

    if pct_after >= LIMIT_AT:
        if pct_before < LIMIT_AT:
            print(f"!!! ALERT: '{cat}' has crossed 100% of its budget "
                  f"({after:.2f} / {budget:.2f}) for {month}.")
        else:
            over = after - budget
            print(f"!!! '{cat}' is still over budget by {over:.2f} "
                  f"({pct_after * 100:.0f}% used).")
    elif pct_after >= WARN_AT:
        if pct_before < WARN_AT:
            print(f"** WARNING: '{cat}' has crossed 80% of its budget "
                  f"({after:.2f} / {budget:.2f}) for {month}.")
        else:
            print(f"** Reminder: '{cat}' is at {pct_after * 100:.0f}% of budget.")


def set_budget(data):
    print("\n--- Set Monthly Budget ---")
    cat = ask_category("Category: ")
    amount = ask_amount("Monthly budget: ")
    data["budgets"][cat] = amount
    save_data(data)
    print(f"Budget for {cat} set to {amount:.2f} per month.")


def month_summary(data):
    print("\n--- Month Summary ---")
    month = ask_month("Month (YYYY-MM, Enter = current): ")
    spent = spent_by_category(data, month)
    cats = sorted(set(spent) | set(data["budgets"]))

    if not cats:
        print("No budgets or expenses yet.")
        return

    print(f"\nSummary for {month}")
    print(f"{'Category':<15}{'Spent':>10}{'Budget':>10}{'Used':>8}  Status")
    print("-" * 56)
    total_spent = total_budget = 0
    for c in cats:
        s = spent.get(c, 0)
        b = data["budgets"].get(c)
        pct = f"{s / b * 100:.0f}%" if b else "-"
        b_txt = f"{b:.2f}" if b else "-"
        print(f"{c:<15}{s:>10.2f}{b_txt:>10}{pct:>8}  {status_label(s, b)}")
        total_spent += s
        total_budget += b or 0
    print("-" * 56)
    print(f"{'TOTAL':<15}{total_spent:>10.2f}{total_budget:>10.2f}")


def top_expenses(data):
    print("\n--- Top 5 Expenses ---")
    month = ask_month("Month (YYYY-MM, Enter = current): ")
    items = [e for e in data["expenses"] if month_key(e["date"]) == month]
    if not items:
        print(f"No expenses recorded for {month}.")
        return
    items.sort(key=lambda e: e["amount"], reverse=True)
    print(f"\nLargest expenses in {month}")
    print(f"{'#':<3}{'Date':<12}{'Category':<15}{'Amount':>10}  Note")
    print("-" * 56)
    for i, e in enumerate(items[:5], 1):
        print(f"{i:<3}{e['date']:<12}{e['category']:<15}{e['amount']:>10.2f}  {e['note']}")


def compare_months(data):
    print("\n--- Compare With Last Month ---")
    month = ask_month("Month (YYYY-MM, Enter = current): ")
    last = prev_month(month)
    now_s = spent_by_category(data, month)
    old_s = spent_by_category(data, last)
    cats = sorted(set(now_s) | set(old_s))
    if not cats:
        print("No data for these months.")
        return
    print(f"\n{month} vs {last}")
    print(f"{'Category':<15}{last:>10}{month:>10}{'Change':>10}")
    print("-" * 45)
    for c in cats:
        a, b = old_s.get(c, 0), now_s.get(c, 0)
        diff = b - a
        sign = "+" if diff > 0 else ""
        print(f"{c:<15}{a:>10.2f}{b:>10.2f}{sign + format(diff, '.2f'):>10}")


def export_csv(data):
    print("\n--- Export To CSV ---")
    month = ask_month("Month (YYYY-MM, Enter = current): ")
    items = sorted(
        (e for e in data["expenses"] if month_key(e["date"]) == month),
        key=lambda e: e["date"],
    )
    if not items:
        print(f"No expenses recorded for {month}.")
        return
    filename = f"expenses_{month}.csv"
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["date", "category", "amount", "note"])
        writer.writeheader()
        writer.writerows(items)
    print(f"Exported {len(items)} expenses to {filename}")


# ---------------------------------------------------------------- main loop
MENU = """
=========== SpendSense ===========
1. Add expense
2. Set monthly budget for a category
3. Month summary (spent vs budget)
4. Top 5 largest expenses of the month
5. Compare with last month
6. Export month to CSV
0. Exit
"""


def main():
    data = load_data()
    actions = {
        "1": add_expense,
        "2": set_budget,
        "3": month_summary,
        "4": top_expenses,
        "5": compare_months,
        "6": export_csv,
    }
    while True:
        print(MENU)
        choice = input("Choose an option: ").strip()
        if choice == "0":
            print("Goodbye! Spend wisely.")
            break
        action = actions.get(choice)
        if action:
            action(data)
        else:
            print("Invalid choice, try again.")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nGoodbye!")
