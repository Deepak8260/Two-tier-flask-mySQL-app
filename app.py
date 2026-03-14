# app.py
# ---------------------------------------------------------------------------
# Flask routes:
#   GET  /              – homepage (messages + stats)
#   POST /add           – submit a new message
#   POST /delete/<id>   – delete a message by id
# ---------------------------------------------------------------------------

from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
from database import (
    init_db,
    insert_message,
    fetch_all_messages,
    delete_message,
    get_stats
)

app = Flask(__name__)


# ── Helper ──────────────────────────────────────────────────────────────────

def time_ago(dt: datetime | None) -> str:
    """Convert a datetime to a human-readable relative string."""
    if dt is None:
        return "never"
    seconds = int((datetime.now() - dt).total_seconds())
    if seconds < 10:
        return "just now"
    if seconds < 60:
        return f"{seconds}s ago"
    if seconds < 3600:
        return f"{seconds // 60}m ago"
    if seconds < 86400:
        return f"{seconds // 3600}h ago"
    days = seconds // 86400
    return f"{days}d ago"


# ── Routes ───────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    """Fetch messages + stats and render the dashboard."""
    raw_messages = fetch_all_messages()
    stats        = get_stats()

    # Enrich each message with derived fields
    messages = []
    for row in raw_messages:
        dt = row["created_at"]
        messages.append({
            "id":          row["id"],
            "message":     row["message"],
            "char_count":  len(row["message"]),
            "ip_address":  row["ip_address"] or "—",
            "time_ago":    time_ago(dt),
            "created_str": dt.strftime("%d %b %Y · %I:%M %p") if dt else "Unknown",
        })

    stats["last_activity_str"] = time_ago(stats["last_activity"])

    return render_template("index.html", messages=messages, stats=stats)


@app.route("/add", methods=["POST"])
def add_message():
    """Save a new message (with the requester's IP) then redirect."""
    message = request.form.get("message", "").strip()
    if message:
        ip = request.remote_addr
        insert_message(message, ip)
    return redirect(url_for("index"))


@app.route("/delete/<int:message_id>", methods=["POST"])
def delete(message_id):
    """Delete a message by its id then redirect back."""
    delete_message(message_id)
    return redirect(url_for("index"))


# ── Entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
