import sqlite3

DB_NAME = "store.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def create_tables():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        first_name TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS products(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_name TEXT,
        duration TEXT,
        price INTEGER,
        stock INTEGER DEFAULT 0
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
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "INSERT OR REPLACE INTO users VALUES(?,?,?)",
        (user_id, username, first_name)
    )

    conn.commit()
    conn.close()

def add_order(order_id, user_id, product, duration, amount, utr):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO orders
        (order_id, user_id, product, duration, amount, utr, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            order_id,
            user_id,
            product,
            duration,
            amount,
            utr,
            "Pending"
        )
    )

    conn.commit()
    conn.close()


def update_order_status(order_id, status):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "UPDATE orders SET status=? WHERE order_id=?",
        (status, order_id)
    )

    conn.commit()
    conn.close()
def add_order(order_id, user_id, product, duration, amount, utr):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO orders
        (order_id, user_id, product, duration, amount, utr, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            order_id,
            user_id,
            product,
            duration,
            amount,
            utr,
            "Pending"
        )
    )

    conn.commit()
    conn.close()
