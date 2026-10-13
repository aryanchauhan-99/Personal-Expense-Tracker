import os
import sqlite3
from flask import Flask, request, redirect, render_template_string

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "expenses.db")

HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>My Expense Tracker</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #f1f5f9;
            margin: 0;
            padding: 20px;
            color: #172033;
        }
        .container {
            max-width: 600px;
            margin: auto;
        }
        h1 { color: #4338ca; }
        .card {
            background: white;
            padding: 20px;
            margin: 15px 0;
            border-radius: 15px;
            box-shadow: 0 4px 15px #0001;
        }
        input, button {
            box-sizing: border-box;
            width: 100%;
            padding: 12px;
            margin: 7px 0;
            border-radius: 8px;
            border: 1px solid #ddd;
            font-size: 16px;
        }
        button {
            background: #4338ca;
            color: white;
            border: 0;
        }
        .amount { font-size: 27px; font-weight: bold; }
        .item {
            border-bottom: 1px solid #eee;
            padding: 12px 0;
        }
        .delete {
            background: #dc2626;
            width: auto;
            padding: 8px 12px;
        }
    </style>
</head>
<body>
<div class="container">
    <h1>My Expense Tracker</h1>
    <p>Manage your daily expenses easily.</p>

    <div class="card">
        <p>Total Expenses</p>
        <div class="amount">₹{{ total }}</div>
    </div>

    <div class="card">
        <h2>Add Expense</h2>
        <form method="POST" action="/add">
            <input name="title" placeholder="Expense name"
                   maxlength="100" required>
            <input name="amount" type="number" min="0.01"
                   step="0.01" placeholder="Amount in rupees" required>
            <input name="category" placeholder="Category"
                   maxlength="50" required>
            <button type="submit">Add Expense</button>
        </form>
    </div>

    <div class="card">
        <h2>Recent Expenses</h2>
        {% if expenses %}
            {% for expense in expenses %}
            <div class="item">
                <strong>{{ expense[1] }}</strong><br>
                {{ expense[3] }} · ₹{{ "%.2f"|format(expense[2]) }}
                <form method="POST" action="/delete/{{ expense[0] }}">
                    <button class="delete" type="submit">Delete</button>
                </form>
            </div>
            {% endfor %}
        {% else %}
            <p>No expenses added yet.</p>
        {% endif %}
    </div>
</div>
</body>
</html>
"""

def setup_database():
    with sqlite3.connect(DB_PATH) as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL
            )
        """)

@app.route("/")
def home():
    with sqlite3.connect(DB_PATH) as con:
        expenses = con.execute(
            "SELECT id, title, amount, category "
            "FROM expenses ORDER BY id DESC"
        ).fetchall()
        total = con.execute(
            "SELECT COALESCE(SUM(amount), 0) FROM expenses"
        ).fetchone()[0]

    return render_template_string(
        HTML, expenses=expenses, total=f"{total:.2f}"
    )

@app.route("/add", methods=["POST"])
def add_expense():
    title = request.form.get("title", "").strip()
    category = request.form.get("category", "").strip()

    try:
        amount = float(request.form.get("amount", ""))
    except ValueError:
        return "Please enter a valid amount.", 400

    if not title or not category or amount <= 0:
        return "Please enter valid expense details.", 400

    with sqlite3.connect(DB_PATH) as con:
        con.execute(
            "INSERT INTO expenses (title, amount, category) "
            "VALUES (?, ?, ?)",
            (title, amount, category)
        )

    return redirect("/")

@app.route("/delete/<int:expense_id>", methods=["POST"])
def delete_expense(expense_id):
    with sqlite3.connect(DB_PATH) as con:
        con.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    return redirect("/")

if __name__ == "__main__":
    setup_database()
    print("Expense Tracker is starting...")
    print("Open http://127.0.0.1:5000 in your browser")
    app.run(host="127.0.0.1", port=5000, debug=False)
 
