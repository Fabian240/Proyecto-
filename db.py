import sqlite3

conn = sqlite3.connect("saas.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS users (
    username TEXT,
    password TEXT,
    expire TEXT,
    status TEXT
)
""")

conn.commit()


def create_user(user, password, expire):
    c.execute(
        "INSERT INTO users VALUES (?, ?, ?, ?)",
        (user, password, expire, "ACTIVE")
    )
    conn.commit()


def get_users():
    c.execute("SELECT * FROM users")
    return c.fetchall()


def suspend_user(user):
    c.execute("UPDATE users SET status='SUSPENDED' WHERE username=?", (user,))
    conn.commit()


def activate_user(user):
    c.execute("UPDATE users SET status='ACTIVE' WHERE username=?", (user,))
    conn.commit()


def delete_user(user):
    c.execute("DELETE FROM users WHERE username=?", (user,))
    conn.commit()