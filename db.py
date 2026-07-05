import sqlite3

conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    username TEXT,
    password TEXT,
    expire TEXT
)
""")
conn.commit()

def create_user(username, password, expire):
    cursor.execute(
        "INSERT INTO users VALUES (?, ?, ?)",
        (username, password, expire),
    )
    conn.commit()

def get_users():
    cursor.execute("SELECT * FROM users")
    return cursor.fetchall()