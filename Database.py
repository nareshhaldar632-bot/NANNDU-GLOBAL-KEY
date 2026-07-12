import sqlite3

DB_NAME = "store.db"


def create_tables():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        first_name TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS orders(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id TEXT,
        user_id INTEGER,
        product TEXT,
        duration TEXT,
        amount INTEGER,
        utr TEXT,
        status TEXT
    )
    """)

    conn.commit()
    conn.close()


def add_user(user_id, username, first_name):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute(
        "INSERT OR REPLACE INTO users VALUES(?,?,?)",
        (user_id, username, first_name)
    )

    conn.commit()
    conn.close()


def add_order(order_id, user_id, product, duration, amount, utr):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO orders
        (order_id,user_id,product,duration,amount,utr,status)
        VALUES(?,?,?,?,?,?,?)
        """,
        (order_id,user_id,product,duration,amount,utr,"Pending")
    )

    conn.commit()
    conn.close()
