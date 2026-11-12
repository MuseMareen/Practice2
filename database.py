import sqlite3

DB_NAME = "beauty_studio.db"


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT,
            last_name TEXT,
            service TEXT,
            visit_time TEXT,
            phone TEXT
        )
    ''')
    conn.commit()
    conn.close()


def add_appointment(first_name, last_name, service, visit_time, phone):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO appointments (first_name, last_name, service, visit_time, phone) VALUES (?, ?, ?, ?, ?)",
        (first_name, last_name, service, visit_time, phone)
    )
    conn.commit()
    conn.close()


def get_recent_appointments(limit=5):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM appointments ORDER BY id DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_all_appointments():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM appointments ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows


def search_by_phone(phone):
    conn = get_connection()
    cursor = conn.cursor()

    # УЯЗВИМОСТЬ 2 (SQL Injection): Прямая подстановка пользовательского ввода в SQL-запрос
    query = "SELECT * FROM appointments WHERE phone = '{phone}'"
    cursor.execute(query)

    results = cursor.fetchall()
    conn.close()
    return results