import sqlite3
import os
import json
from datetime import datetime, UTC

DB_PATH = os.path.join(os.path.dirname(__file__), "d2r_marketplace.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH, timeout=10)
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
            item_code TEXT,
            item_kind TEXT,
            item_type TEXT,
            quality TEXT,
            level INTEGER,
            attributes TEXT,
            source TEXT,
            exported_from TEXT,
            purchased_at TIMESTAMP,
            token_price INTEGER DEFAULT 0,
            status TEXT DEFAULT 'available',
            quantity INTEGER DEFAULT 1,
            unit_price INTEGER DEFAULT 0,
            listed_at TIMESTAMP,
            sell_after_seconds INTEGER
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

def get_listed_items():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, quantity, unit_price, listed_at, sell_after_seconds, status
        FROM virtual_items
        WHERE status = 'listed'
        ORDER BY listed_at ASC
    """)

    rows = cursor.fetchall()
    conn.close()

    items = []
    for row in rows:
        items.append({
            "id": row[0],
            "name": row[1],
            "quantity": row[2] or 1,
            "unit_price": row[3] or 0,
            "listed_at": row[4],
            "sell_after_seconds": row[5] or 0,
            "status": row[6],
        })

    return items


def get_listed_item_by_id(item_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, item_code, item_kind, quantity, unit_price, listed_at, sell_after_seconds, status
        FROM virtual_items
        WHERE id = ?
    """, (item_id,))

    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return {
        "id": row[0],
        "name": row[1],
        "item_code": row[2],
        "item_kind": row[3],
        "quantity": row[4] or 1,
        "unit_price": row[5] or 0,
        "listed_at": row[6],
        "sell_after_seconds": row[7] or 0,
        "status": row[8],
    }


def mark_listing_cancelled(item_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE virtual_items
        SET status = 'cancelled'
        WHERE id = ? AND status = 'listed'
    """, (item_id,))

    conn.commit()
    affected = cursor.rowcount
    conn.close()
    return affected > 0


def mark_listing_sold(item_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE virtual_items
        SET status = 'sold', purchased_at = ?
        WHERE id = ? AND status = 'listed'
    """, (datetime.now(UTC).isoformat(), item_id))

    conn.commit()
    affected = cursor.rowcount
    conn.close()
    return affected > 0


def process_due_listings():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, quantity, unit_price, listed_at, sell_after_seconds
        FROM virtual_items
        WHERE status = 'listed'
    """)

    rows = cursor.fetchall()
    sold_items = []

    now = datetime.now(UTC)

    for row in rows:
        item_id, name, quantity, unit_price, listed_at, sell_after_seconds = row

        if not listed_at:
            continue

        listed_dt = datetime.fromisoformat(listed_at)

        if listed_dt.tzinfo is None:
            listed_dt = listed_dt.replace(tzinfo=UTC)

        elapsed = (now - listed_dt).total_seconds()

        if elapsed >= (sell_after_seconds or 0):
            total_tokens = (quantity or 1) * (unit_price or 0)

            cursor.execute("""
                UPDATE virtual_items
                SET status = 'sold', purchased_at = ?
                WHERE id = ? AND status = 'listed'
            """, (now.isoformat(), item_id))

            if cursor.rowcount > 0:
                cursor.execute("""
                    UPDATE user
                    SET token_balance = token_balance + ?
                    WHERE id = 1
                """, (total_tokens,))

                cursor.execute("""
                    INSERT INTO transactions (type, item_id, token_amount, description, date)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    "sale_credit",
                    item_id,
                    total_tokens,
                    f"Venda automática de {name} x{quantity}",
                    now.isoformat()
                ))

                sold_items.append({
                    "id": item_id,
                    "name": name,
                    "quantity": quantity,
                    "unit_price": unit_price,
                    "total_tokens": total_tokens,
                })

    conn.commit()
    conn.close()
    return sold_items

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
        datetime.now(UTC).isoformat(),
        token_price
    ))

    conn.commit()
    conn.close()

def get_virtual_item_by_id(item_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM virtual_items WHERE id = ?", (item_id,))
    item = cursor.fetchone()
    conn.close()

    if not item:
        return None

    return {
        "id": item["id"],
        "name": item["name"],
        "item_type": item["item_type"],
        "quality": item["quality"],
        "attributes": item["attributes"],
        "status": item["status"],
        "token_price": item["token_price"],
        "source": item["source"],
        "exported_from": item["exported_from"],
    }

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