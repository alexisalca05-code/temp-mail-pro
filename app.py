from flask import Flask, request, render_template
import sqlite3
import requests

app = Flask(__name__)

# ---------------- DB ----------------
def db():
    conn = sqlite3.connect("database.db")
    conn.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tg_id TEXT,
        email TEXT
    )
    """)
    conn.commit()
    return conn

# ---------------- HOME ----------------
@app.route("/")
def home():
    return """
    <h1>📧 AZVIP Temp Mail SaaS</h1>
    <p>Sistema activo</p>
    """

# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    tg_id = request.args.get("tg_id")

    conn = db()
    data = conn.execute(
        "SELECT email FROM users WHERE tg_id=?",
        (tg_id,)
    ).fetchall()
    conn.close()

    html = "<h2>📬 Tus correos</h2>"

    if not data:
        return html + "<p>No tienes correos aún</p>"

    for e in data:
        email = e[0]
        html += f"""
        <div style="border:1px solid #ccc; padding:10px; margin:10px">
            <b>{email}</b><br>
            <a href="/inbox?email={email}">Ver inbox</a>
        </div>
        """

    return html

# ---------------- INBOX ----------------
@app.route("/inbox")
def inbox():
    email = request.args.get("email")

    login, domain = email.split("@")

    url = f"https://www.1secmail.com/api/v1/?action=getMessages&login={login}&domain={domain}"

    try:
        res = requests.get(url, timeout=10)

        if res.status_code == 200:
            try:
                messages = res.json()
            except:
                messages = []
        else:
            messages = []

    except:
        messages = []

    html = f"<h2>📬 Inbox: {email}</h2>"

    if not messages:
        return html + "<p>📭 Sin mensajes</p>"

    for m in messages:
        html += f"""
        <div style="border:1px solid #ccc; margin:10px; padding:10px">
            <b>De:</b> {m.get('from','N/A')}<br>
            <b>Asunto:</b> {m.get('subject','Sin asunto')}<br>
        </div>
        """

    return html

# ---------------- RUN ----------------
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)