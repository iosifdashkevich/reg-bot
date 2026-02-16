import sqlite3
from datetime import datetime


# ================= СОЗДАНИЕ БАЗЫ =================

def init_db():
    conn = sqlite3.connect("leads.db")
    cursor = conn.cursor()

    # заявки
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

    # пользователи
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER UNIQUE,
        username TEXT,
        first_seen TEXT
    )
    """)

    conn.commit()
    conn.close()


# ================= ДОБАВИТЬ ПОЛЬЗОВАТЕЛЯ =================

def add_user(telegram_id: int, username: str):
    conn = sqlite3.connect("leads.db")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT OR IGNORE INTO users (
        telegram_id,
        username,
        first_seen
    ) VALUES (?, ?, ?)
    """, (
        telegram_id,
        username,
        datetime.now().strftime("%Y-%m-%d %H:%M")
    ))

    conn.commit()
    conn.close()


# ================= ДОБАВИТЬ ЗАЯВКУ =================

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

    lead_id = cursor.lastrowid  # 🔥 ВАЖНО

    conn.commit()
    conn.close()

    return lead_id  # 🔥 ВОЗВРАЩАЕМ ID


# ================= ВСЕ ЗАЯВКИ =================

def get_all_leads():
    conn = sqlite3.connect("leads.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, created_at, name, phone, username, telegram_id, status
    FROM leads
    ORDER BY id DESC
    LIMIT 20
    """)

    rows = cursor.fetchall()
    conn.close()
    return rows


# ================= НОВЫЕ ЗАЯВКИ =================

def get_new_leads():
    conn = sqlite3.connect("leads.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, created_at, name, phone, username, telegram_id
    FROM leads
    WHERE status = 'new'
    ORDER BY id DESC
    """)

    rows = cursor.fetchall()
    conn.close()
    return rows


# ================= ИЗМЕНИТЬ СТАТУС =================

def update_lead_status(lead_id: int, status: str):
    conn = sqlite3.connect("leads.db")
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE leads
    SET status = ?
    WHERE id = ?
    """, (status, lead_id))

    conn.commit()
    conn.close()


# ================= ВСЕ ПОЛЬЗОВАТЕЛИ =================

def get_all_users():
    conn = sqlite3.connect("leads.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT telegram_id, username, first_seen
    FROM users
    ORDER BY id DESC
    LIMIT 30
    """)

    rows = cursor.fetchall()
    conn.close()
    return rows
