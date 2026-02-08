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


# 🔥 НОВОЕ — получить последние заявки
def get_all_leads(limit=20):
    conn = sqlite3.connect("leads.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, created_at, name, phone, status
    FROM leads
    ORDER BY id DESC
    LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()
    conn.close()
    return rows


# 🔥 НОВОЕ — статистика за сегодня
def get_today_stats():
    conn = sqlite3.connect("leads.db")
    cursor = conn.cursor()

    today = datetime.now().strftime("%Y-%m-%d")

    cursor.execute("""
    SELECT COUNT(*) FROM leads
    WHERE created_at LIKE ?
    """, (f"{today}%",))

    count = cursor.fetchone()[0]
    conn.close()
    return count
