import os
import psycopg2
from datetime import datetime

DATABASE_URL = os.getenv("DATABASE_URL")

def get_connection():
    return psycopg2.connect(DATABASE_URL)


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        telegram_id BIGINT UNIQUE,
        username TEXT,
        first_seen TEXT
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS leads (
        id SERIAL PRIMARY KEY,
        created_at TEXT,
        name TEXT,
        phone TEXT,
        telegram_id BIGINT,
        username TEXT,
        citizenship TEXT,
        term TEXT,
        urgency TEXT,
        status TEXT
    );
    """)

    conn.commit()
    cur.close()
    conn.close()


def add_user(telegram_id, username):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO users (telegram_id, username, first_seen)
    VALUES (%s, %s, %s)
    ON CONFLICT (telegram_id) DO NOTHING;
    """, (
        telegram_id,
        username,
        datetime.now().strftime("%Y-%m-%d %H:%M")
    ))

    conn.commit()
    cur.close()
    conn.close()


def get_all_users():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT telegram_id, username, first_seen
    FROM users
    ORDER BY id DESC
    LIMIT 5;
    """)

    users = cur.fetchall()

    cur.close()
    conn.close()
    return users


def get_all_users_full():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT telegram_id FROM users;
    """)

    users = cur.fetchall()

    cur.close()
    conn.close()
    return users


def add_lead(data):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
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
    ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
    RETURNING id;
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

    lead_id = cur.fetchone()[0]

    conn.commit()
    cur.close()
    conn.close()

    return lead_id


def update_lead_status(lead_id, status):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    UPDATE leads SET status = %s WHERE id = %s;
    """, (status, lead_id))

    conn.commit()
    cur.close()
    conn.close()
