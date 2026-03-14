# database.py
# ---------------------------------------------------------------------------
# MySQL database layer:
#   - init_db()            – bootstrap DB + table (adds new columns safely)
#   - insert_message()     – save message + IP
#   - fetch_all_messages() – return full row dicts
#   - delete_message()     – delete by id
#   - get_stats()          – aggregate stats for the dashboard
# ---------------------------------------------------------------------------

import mysql.connector
from config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME


def get_connection():
    """Return a connection that already points at DB_NAME."""
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )


def init_db():
    """
    Bootstrap the database on every startup (idempotent):
      1. Connect without selecting a database.
      2. CREATE DATABASE IF NOT EXISTS.
      3. CREATE TABLE IF NOT EXISTS (with all columns).
      4. ALTER TABLE to add new columns to any pre-existing table.
    """
    # ── Step 1: connect without specifying a database ──────────────────────
    conn = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD
    )
    cur = conn.cursor()

    # ── Step 2: create database ────────────────────────────────────────────
    cur.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}`")
    cur.execute(f"USE `{DB_NAME}`")

    # ── Step 3: create table with all desired columns ──────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id         INT AUTO_INCREMENT PRIMARY KEY,
            message    TEXT        NOT NULL,
            created_at TIMESTAMP   DEFAULT CURRENT_TIMESTAMP,
            ip_address VARCHAR(45) DEFAULT NULL
        )
    """)

    # ── Step 4: migrate pre-existing tables (works on all MySQL 5.7+) ──────
    # For each new column, check INFORMATION_SCHEMA first, then ALTER TABLE.
    # This avoids relying on "ADD COLUMN IF NOT EXISTS" which needs MySQL 8.0.29+.
    new_columns = [
        ("created_at", "TIMESTAMP   DEFAULT CURRENT_TIMESTAMP"),
        ("ip_address",  "VARCHAR(45) DEFAULT NULL"),
    ]
    for col_name, col_def in new_columns:
        cur.execute("""
            SELECT COUNT(*) AS cnt
            FROM   INFORMATION_SCHEMA.COLUMNS
            WHERE  TABLE_SCHEMA = %s
              AND  TABLE_NAME   = 'messages'
              AND  COLUMN_NAME  = %s
        """, (DB_NAME, col_name))
        exists = cur.fetchone()[0]   # cursor is NOT dictionary=True here, returns tuple
        if not exists:
            cur.execute(f"ALTER TABLE messages ADD COLUMN `{col_name}` {col_def}")
            print(f"[DB] Added column '{col_name}' to messages table.")

    conn.commit()
    cur.close()
    conn.close()
    print(f"[DB] '{DB_NAME}'.messages is ready.")


# ── CRUD helpers ────────────────────────────────────────────────────────────

def insert_message(message: str, ip_address: str = None) -> None:
    """Insert a new message row."""
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute(
        "INSERT INTO messages (message, ip_address) VALUES (%s, %s)",
        (message, ip_address)
    )
    conn.commit()
    cur.close()
    conn.close()


def fetch_all_messages() -> list[dict]:
    """
    Return all messages ordered newest-first.
    Each row is a dict: {id, message, created_at, ip_address}
    """
    conn = get_connection()
    cur  = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT id, message, created_at, ip_address
        FROM   messages
        ORDER  BY id DESC
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def delete_message(message_id: int) -> None:
    """Delete a single message by primary key."""
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("DELETE FROM messages WHERE id = %s", (message_id,))
    conn.commit()
    cur.close()
    conn.close()


def get_stats() -> dict:
    """
    Return aggregate dashboard stats:
      total        – all-time message count
      today        – messages posted today
      this_week    – messages in the last 7 days
      last_activity – datetime of the most recent message (or None)
    """
    conn = get_connection()
    cur  = conn.cursor(dictionary=True)

    cur.execute("SELECT COUNT(*) AS total FROM messages")
    total = cur.fetchone()["total"]

    cur.execute("SELECT COUNT(*) AS cnt FROM messages WHERE DATE(created_at) = CURDATE()")
    today = cur.fetchone()["cnt"]

    cur.execute("SELECT COUNT(*) AS cnt FROM messages WHERE created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)")
    this_week = cur.fetchone()["cnt"]

    cur.execute("SELECT created_at FROM messages ORDER BY id DESC LIMIT 1")
    row = cur.fetchone()
    last_activity = row["created_at"] if row else None

    cur.close()
    conn.close()

    return {
        "total":         total,
        "today":         today,
        "this_week":     this_week,
        "last_activity": last_activity,
    }
