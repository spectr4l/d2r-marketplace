import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "d2r_marketplace.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            username TEXT DEFAULT 'Jogador',
            token_balance INTEGER DEFAULT 1000
        )
    """)

    cursor.execute("""
        INSERT OR IGNORE INTO user (id, username, token_balance)
        VALUES (1, 'Jogador', 1000)
    """)

    cursor.execute("""
            CREATE TABLE IF NOT EXISTS virtual_items (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                item_type TEXT,
                quality TEXT,
                level INTEGER,
                attributes TEXT,
                source TEXT,
                exported_from TEXT,
                purchased_at TIMESTAMP,
                token_price INTEGER DEFAULT 0,
                status TEXT DEFAULT 'available'
            )
        """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT,
            item_id TEXT,
            token_amount INTEGER,
            description TEXT,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (item_id) REFERENCES virtual_items(id)
        )
    """)

    conn.commit()
    conn.close()
    print("Banco de dados inicializado!")


def get_token_balance():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT token_balance FROM user WHERE id = 1")
    result = cursor.fetchone()
    conn.close()
    return result["token_balance"] if result else 1000


def update_token_balance(amount):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE user SET token_balance = token_balance + ? WHERE id = 1",
        (amount,)
    )
    conn.commit()
    conn.close()


def add_virtual_item(item_id, name, item_type, quality, attributes, source, exported_from=None, token_price=0):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO virtual_items (
            id, name, item_type, quality, attributes, source, exported_from, purchased_at, token_price
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        item_id,
        name,
        item_type,
        quality,
        attributes,
        source,
        exported_from,
        datetime.now(),
        token_price
    ))

    conn.commit()
    conn.close()


def get_virtual_items(status="available"):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM virtual_items WHERE status = ?", (status,))
    items = cursor.fetchall()

    result = []
    for item in items:
        result.append({
            "id": item["id"],
            "name": item["name"],
            "item_type": item["item_type"],
            "quality": item["quality"],
            "attributes": item["attributes"],
            "status": item["status"],
            "token_price": item["token_price"],
        })

    conn.close()
    return result


def mark_item_as_sold(item_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE virtual_items SET status = "sold" WHERE id = ?',
        (item_id,)
    )
    conn.commit()
    conn.close()


def mark_item_as_imported(item_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE virtual_items SET status = "imported" WHERE id = ?',
        (item_id,)
    )
    conn.commit()
    conn.close()


def add_transaction(type, item_id, token_amount, description):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO transactions (type, item_id, token_amount, description)
        VALUES (?, ?, ?, ?)
    """, (type, item_id, token_amount, description))
    conn.commit()
    conn.close()