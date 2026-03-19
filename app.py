import sqlite3
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
DB_NAME = "tickets.db"


def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            issue TEXT NOT NULL,
            priority TEXT NOT NULL,
            status TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


@app.route("/")
def home():
    conn = get_db_connection()

    tickets = conn.execute("SELECT * FROM tickets ORDER BY id DESC").fetchall()

    total_tickets = conn.execute("SELECT COUNT(*) FROM tickets").fetchone()[0]
    open_tickets = conn.execute("SELECT COUNT(*) FROM tickets WHERE status = 'Open'").fetchone()[0]
    resolved_tickets = conn.execute("SELECT COUNT(*) FROM tickets WHERE status = 'Resolved'").fetchone()[0]
    high_priority_tickets = conn.execute("SELECT COUNT(*) FROM tickets WHERE priority = 'High' AND status = 'Open'").fetchone()[0]

    conn.close()

    return render_template(
        "index.html",
        tickets=tickets,
        total_tickets=total_tickets,
        open_tickets=open_tickets,
        resolved_tickets=resolved_tickets,
        high_priority_tickets=high_priority_tickets
    )


@app.route("/submit", methods=["POST"])
def submit_ticket():
    name = request.form.get("name")
    issue = request.form.get("issue")
    priority = request.form.get("priority")

    if name and issue and priority:
        conn = get_db_connection()
        conn.execute(
            "INSERT INTO tickets (name, issue, priority, status) VALUES (?, ?, ?, ?)",
            (name, issue, priority, "Open")
        )
        conn.commit()
        conn.close()

    return redirect(url_for("home"))


@app.route("/resolve/<int:ticket_id>")
def resolve_ticket(ticket_id):
    conn = get_db_connection()
    conn.execute(
        "UPDATE tickets SET status = ? WHERE id = ?",
        ("Resolved", ticket_id)
    )
    conn.commit()
    conn.close()
    return redirect(url_for("home"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True)