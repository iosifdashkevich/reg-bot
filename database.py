import sqlite3
from datetime import datetime


def init_db():
    conn = sqlite3.connect("leads.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS leads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TEXT,
        name TEXT,
        phone TEXT,
        telegram_id INTEGER,
        username TEXT,
        citizenship TEXT,
        term TEXT,
        urgency TEXT,
        status TEXT
    )
    """)

    conn.commit()
    conn.close()


def add_lead(data: dict):
    conn = sqlite3.connect("leads.db")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO leads (
        created_at,
        name,
        phone,
        telegram_id,
        username,
        citizenship,
        term,
        urgency,
        status
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().strftime("%Y-%m-%d %H:%M"),
        data["name"],
        data["phone"],
        data["telegram_id"],
        data["username"],
        data["citizenship"],
        data["term"],
        data["urgency"],
        "new"
    ))

    conn.commit()
    conn.close()
