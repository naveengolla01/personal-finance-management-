# Project ID: UY6758GH

# Personal Finance Management Application

## Libraries and Modules to Use
import sqlite3
import os
from datetime import datetime
from getpass import getpass

# Step 1: Database Setup
DB_NAME = "finance_manager.db"

def initialize_database():
    """Initialize the database with required tables."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Create Users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    ''')

    # Create Transactions table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        type TEXT NOT NULL, -- "income" or "expense"
        category TEXT NOT NULL,
        amount REAL NOT NULL,
        date TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    ''')

    # Create Budgets table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS budgets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        category TEXT NOT NULL,
        budget_limit REAL NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    ''')

    conn.commit()
    conn.close()

# Step 2: User Registration and Authentication
def register_user():
    """Register a new user."""
    username = input("Enter a unique username: ").strip()
    password = getpass("Enter a password: ").strip()

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
        print("Registration successful!")
    except sqlite3.IntegrityError:
        print("Username already exists. Please try again.")
    finally:
        conn.close()

def login_user():
    """Authenticate an existing user."""
    username = input("Enter username: ").strip()
    password = getpass("Enter password: ").strip()

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM users WHERE username = ? AND password = ?', (username, password))
    user = cursor.fetchone()
    conn.close()

    if user:
        print("Login successful!")
        return user[0]  # Return user ID
    else:
        print("Invalid username or password.")
        return None

# Step 3: Income and Expense Tracking
def add_transaction(user_id, transaction_type):
    """Add a new income or expense."""
    category = input("Enter category (e.g., Food, Rent): ").strip()
    amount = float(input("Enter amount: ").strip())
    date = input("Enter date (YYYY-MM-DD) or leave blank for today: ").strip()

    if not date:
        date = datetime.now().strftime("%Y-%m-%d")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO transactions (user_id, type, category, amount, date)
    VALUES (?, ?, ?, ?, ?)
    ''', (user_id, transaction_type, category, amount, date))
    conn.commit()
    conn.close()
    print(f"{transaction_type.capitalize()} added successfully!")

def view_transactions(user_id):
    """View all transactions for a user."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT type, category, amount, date FROM transactions WHERE user_id = ?', (user_id,))
    transactions = cursor.fetchall()
    conn.close()

    if transactions:
        print("\nYour Transactions:")
        for trans in transactions:
            print(f"Type: {trans[0]}, Category: {trans[1]}, Amount: {trans[2]}, Date: {trans[3]}")
    else:
        print("No transactions found.")

# Step 4: Financial Reports
def generate_report(user_id):
    """Generate a financial report."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Total income and expenses
    cursor.execute('SELECT SUM(amount) FROM transactions WHERE user_id = ? AND type = "income"', (user_id,))
    total_income = cursor.fetchone()[0] or 0

    cursor.execute('SELECT SUM(amount) FROM transactions WHERE user_id = ? AND type = "expense"', (user_id,))
    total_expenses = cursor.fetchone()[0] or 0

    savings = total_income - total_expenses

    print(f"\nFinancial Report:")
    print(f"Total Income: ${total_income:.2f}")
    print(f"Total Expenses: ${total_expenses:.2f}")
    print(f"Savings: ${savings:.2f}")

    conn.close()

# Step 5: Budgeting
def set_budget(user_id):
    """Set a monthly budget for a category."""
    category = input("Enter category for the budget: ").strip()
    budget_limit = float(input("Enter budget limit: ").strip())

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO budgets (user_id, category, budget_limit) VALUES (?, ?, ?)
    ''', (user_id, category, budget_limit))
    conn.commit()
    conn.close()
    print("Budget set successfully!")

def check_budget(user_id):
    """Check if budgets are exceeded."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('SELECT category, budget_limit FROM budgets WHERE user_id = ?', (user_id,))
    budgets = cursor.fetchall()

    for category, budget_limit in budgets:
        cursor.execute('''
        SELECT SUM(amount) FROM transactions WHERE user_id = ? AND category = ? AND type = "expense"
        ''', (user_id, category))
        total_spent = cursor.fetchone()[0] or 0
        print(f"(Total Spent: ${total_spent:.2f}, Budget Limit: ${budget_limit:.2f})")
        if total_spent > budget_limit:

            print(f"Warning: You have exceeded your budget for {category}! (Spent: ${total_spent:.2f}, Limit: ${budget_limit:.2f})")

    conn.close()

# Step 6: Main Application Loop
def main():
    initialize_database()

    print("Welcome to Personal Finance Manager!")
    while True:
        print("\nOptions:")
        print("1. Register")
        print("2. Login")
        print("3. Exit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            register_user()
        elif choice == "2":
            user_id = login_user()
            if user_id:
                while True:
                    print("\nUser Menu:")
                    print("1. Add Income")
                    print("2. Add Expense")
                    print("3. View Transactions")
                    print("4. Generate Report")
                    print("5. Set Budget")
                    print("6. Check Budget")
                    print("7. Logout")

                    user_choice = input("Choose an option: ").strip()

                    if user_choice == "1":
                        add_transaction(user_id, "income")
                    elif user_choice == "2":
                        add_transaction(user_id, "expense")
                    elif user_choice == "3":
                        view_transactions(user_id)
                    elif user_choice == "4":
                        generate_report(user_id)
                    elif user_choice == "5":
                        set_budget(user_id)
                    elif user_choice == "6":
                        check_budget(user_id)
                    elif user_choice == "7":
                        print("Logged out.")
                        break
                    else:
                        print("Invalid option. Try again.")
        elif choice == "3":
            print("Goodbye!")
            break
        else:
            print("Invalid option. Try again.")

if __name__ == "__main__":
    main()
