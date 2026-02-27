from fastmcp import FastMCP
import os
import sqlite3
import tempfile
import json

TEMP_DIR = tempfile.gettempdir()
DB_PATH = os.path.join(TEMP_DIR, "expenses.db")

mcp = FastMCP("ExpenseTracker")

def init_db():
    with sqlite3.connect(DB_PATH) as c:
        c.execute("PRAGMA journal_mode=WAL")
        c.execute("""
            CREATE TABLE IF NOT EXISTS expenses(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                subcategory TEXT DEFAULT '',
                note TEXT DEFAULT ''
            )
        """)

init_db()

@mcp.tool()
def add_expense(date: str, amount: float, category: str, subcategory: str = "", note: str = ""):
    """Add a new expense entry to the database."""
    with sqlite3.connect(DB_PATH) as c:
        cur = c.execute(
            "INSERT INTO expenses(date, amount, category, subcategory, note) VALUES (?,?,?,?,?)",
            (date, amount, category, subcategory, note)
        )
        return {"status": "success", "id": cur.lastrowid}

@mcp.tool()
def list_expenses(start_date: str, end_date: str):
    """List expense entries within an inclusive date range."""
    with sqlite3.connect(DB_PATH) as c:
        cur = c.execute(
            "SELECT id, date, amount, category, subcategory, note FROM expenses WHERE date BETWEEN ? AND ? ORDER BY date DESC",
            (start_date, end_date)
        )
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, r)) for r in cur.fetchall()]

@mcp.tool()
def summarize(start_date: str, end_date: str, category: str = None):
    """Summarize expenses by category within an inclusive date range."""
    with sqlite3.connect(DB_PATH) as c:
        query = "SELECT category, SUM(amount) AS total_amount, COUNT(*) as count FROM expenses WHERE date BETWEEN ? AND ?"
        params = [start_date, end_date]
        if category:
            query += " AND category = ?"
            params.append(category)
        query += " GROUP BY category ORDER BY total_amount DESC"
        cur = c.execute(query, params)
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, r)) for r in cur.fetchall()]

@mcp.resource("expense:///categories", mime_type="application/json")
def categories():
    """Return available expense categories."""
    default_categories = {
        "categories": [
            "Food & Dining", "Transportation", "Shopping",
            "Entertainment", "Bills & Utilities", "Healthcare",
            "Travel", "Education", "Business", "Other"
        ]
    }
    return json.dumps(default_categories, indent=2)

if __name__ == "__main__":
    mcp.run()   # ← stdio, no http — required for FastMCP Cloud


# from fastmcp import FastMCP
# import os
# import aiosqlite  # Changed: sqlite3 → aiosqlite
# import tempfile
# # Use temporary directory which should be writable
# TEMP_DIR = tempfile.gettempdir()
# DB_PATH = os.path.join(TEMP_DIR, "expenses.db")
# CATEGORIES_PATH = os.path.join(os.path.dirname(__file__), "categories.json")

# print(f"Database path: {DB_PATH}")

# mcp = FastMCP("ExpenseTracker")

# def init_db():  # Keep as sync for initialization
#     try:
#         # Use synchronous sqlite3 just for initialization
#         import sqlite3
#         with sqlite3.connect(DB_PATH) as c:
#             c.execute("PRAGMA journal_mode=WAL")
#             c.execute("""
#                 CREATE TABLE IF NOT EXISTS expenses(
#                     id INTEGER PRIMARY KEY AUTOINCREMENT,
#                     date TEXT NOT NULL,
#                     amount REAL NOT NULL,
#                     category TEXT NOT NULL,
#                     subcategory TEXT DEFAULT '',
#                     note TEXT DEFAULT ''
#                 )
#             """)
#             # Test write access
#             c.execute("INSERT OR IGNORE INTO expenses(date, amount, category) VALUES ('2000-01-01', 0, 'test')")
#             c.execute("DELETE FROM expenses WHERE category = 'test'")
#             print("Database initialized successfully with write access")
#     except Exception as e:
#         print(f"Database initialization error: {e}")
#         raise

# # Initialize database synchronously at module load
# init_db()

# @mcp.tool()
# async def add_expense(date, amount, category, subcategory="", note=""):  # Changed: added async
#     '''Add a new expense entry to the database.'''
#     try:
#         async with aiosqlite.connect(DB_PATH) as c:  # Changed: added async
#             cur = await c.execute(  # Changed: added await
#                 "INSERT INTO expenses(date, amount, category, subcategory, note) VALUES (?,?,?,?,?)",
#                 (date, amount, category, subcategory, note)
#             )
#             expense_id = cur.lastrowid
#             await c.commit()  # Changed: added await
#             return {"status": "success", "id": expense_id, "message": "Expense added successfully"}
#     except Exception as e:  # Changed: simplified exception handling
#         if "readonly" in str(e).lower():
#             return {"status": "error", "message": "Database is in read-only mode. Check file permissions."}
#         return {"status": "error", "message": f"Database error: {str(e)}"}
    
# @mcp.tool()
# async def list_expenses(start_date, end_date):  # Changed: added async
#     '''List expense entries within an inclusive date range.'''
#     try:
#         async with aiosqlite.connect(DB_PATH) as c:  # Changed: added async
#             cur = await c.execute(  # Changed: added await
#                 """
#                 SELECT id, date, amount, category, subcategory, note
#                 FROM expenses
#                 WHERE date BETWEEN ? AND ?
#                 ORDER BY date DESC, id DESC
#                 """,
#                 (start_date, end_date)
#             )
#             cols = [d[0] for d in cur.description]
#             return [dict(zip(cols, r)) for r in await cur.fetchall()]  # Changed: added await
#     except Exception as e:
#         return {"status": "error", "message": f"Error listing expenses: {str(e)}"}

# @mcp.tool()
# async def summarize(start_date, end_date, category=None):  # Changed: added async
#     '''Summarize expenses by category within an inclusive date range.'''
#     try:
#         async with aiosqlite.connect(DB_PATH) as c:  # Changed: added async
#             query = """
#                 SELECT category, SUM(amount) AS total_amount, COUNT(*) as count
#                 FROM expenses
#                 WHERE date BETWEEN ? AND ?
#             """
#             params = [start_date, end_date]

#             if category:
#                 query += " AND category = ?"
#                 params.append(category)

#             query += " GROUP BY category ORDER BY total_amount DESC"

#             cur = await c.execute(query, params)  # Changed: added await
#             cols = [d[0] for d in cur.description]
#             return [dict(zip(cols, r)) for r in await cur.fetchall()]  # Changed: added await
#     except Exception as e:
#         return {"status": "error", "message": f"Error summarizing expenses: {str(e)}"}

# @mcp.resource("expense:///categories", mime_type="application/json")  # Changed: expense:// → expense:///
# def categories():
#     try:
#         # Provide default categories if file doesn't exist
#         default_categories = {
#             "categories": [
#                 "Food & Dining",
#                 "Transportation",
#                 "Shopping",
#                 "Entertainment",
#                 "Bills & Utilities",
#                 "Healthcare",
#                 "Travel",
#                 "Education",
#                 "Business",
#                 "Other"
#             ]
#         }
        
#         try:
#             with open(CATEGORIES_PATH, "r", encoding="utf-8") as f:
#                 return f.read()
#         except FileNotFoundError:
#             import json
#             return json.dumps(default_categories, indent=2)
#     except Exception as e:
#         return f'{{"error": "Could not load categories: {str(e)}"}}'

# Start the server
if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)
    # mcp.run()


# import os
# from fastmcp import FastMCP
# import sqlite3

# # Path to create the database at
# DB_PATH = os.path.join(os.path.dirname(__file__), "expense.db")
# CATEGORIES_PATH = os.path.join(os.path.dirname(__file__), "categories.json")


# mcp = FastMCP("Expense Tracker")

# # Creating a table in our database
# def db_init():
#     with sqlite3.connect(DB_PATH) as c:
#         c.execute(
#             """
#             CREATE TABLE IF NOT EXISTS expense(
#                 id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 date DATE NOT NULL,
#                 amount DECIMAL(12, 2) NOT NULL,
#                 category VARCHAR(50) NOT NULL,
#                 subcategory VARCHAR(50) DEFAULT '',
#                 note TEXT DEFAULT ''
#             )
#             """
#         )

# db_init()

# # creating the tools
# @mcp.tool()
# def add_expense(date, amount, category, subcategory="", note=""):
#     """Adding the expense to the table"""
#     with sqlite3.connect(DB_PATH) as c:
#         cur = c.execute(
#             """
#             INSERT INTO expense(date, amount, category, subcategory, note) VALUES (?,?,?,?,?)
#             """,
#             (date, amount, category, subcategory, note)
#         )
#         return {"status": "ok", "id": cur.lastrowid}
    
# @mcp.tool()
# def list_expenses(start_date, end_date):
#     """Fetching the expense from the table"""
#     with sqlite3.connect(DB_PATH) as c:
#         cur = c.execute(
#             """
#             SELECT * 
#             FROM expense
#             WHERE date BETWEEN ? AND ?
#             ORDER BY id ASC
#             """,
#             (start_date, end_date)
#         )
#         cols = [d[0] for d in cur.description]
#         return [dict(zip(cols, r)) for r in cur.fetchall()]
    
# # the claude is not giving any subcategory to our expense so we are adding resourses to the claude
# # so that it can choose from that resource
# @mcp.resource("resource://categories")
# def categories():
#     with open(CATEGORIES_PATH, "r", encoding="utf-8") as f:
#         return f.read()


# if __name__ == "__main__":
#     mcp.run(transport="http", host="0.0.0.0", port=8000)