import sqlite3
from datetime import datetime

DB_FILE = "tasks.db"

sample_tasks = [
    ("Car travel to office", 12.5, "travel", "Use public transport instead", 0),
    ("Bus travel downtown", 3.0, "travel", "Good choice! Even better if you can walk or cycle", 0),
    ("Beef burger lunch", 27.0, "food", "Try a plant-based burger next time", 0),
    ("Vegetable stir-fry", 2.0, "food", "Excellent low-carbon choice", 0),
    ("Office printing 50 pages", 0.25, "office", "Switch to digital docs where possible", 0),
    ("Laptop usage (8h)", 0.4, "office", "Enable energy-saving mode", 0),
    ("Misc shopping", 5.0, "other", "Look for eco-friendly alternatives", 0),
]

def seed_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # Create table if not exists
    c.execute('''CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    carbon REAL,
                    category TEXT,
                    suggestion TEXT,
                    completed INTEGER DEFAULT 0,
                    created_at TEXT
                )''')

    # Insert sample data
    for name, carbon, category, suggestion, completed in sample_tasks:
        c.execute(
            "INSERT INTO tasks (name, carbon, category, suggestion, completed, created_at) VALUES (?,?,?,?,?,?)",
            (name, carbon, category, suggestion, completed, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )

    conn.commit()
    conn.close()
    print("✅ Sample tasks added successfully!")

if __name__ == "__main__":
    seed_db()
