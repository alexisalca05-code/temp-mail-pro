from flask import Flask, render_template, request, redirect, session
import sqlite3
import os
import time

app = Flask(__name__)
app.secret_key = "azvip_secret"

# ================= HOME =================
@app.route("/")
def home():
    return redirect("/login")

# ================= DB =================
def db():
    return sqlite3.connect("database.db")

# ================= INIT DB (PRO - SIN BORRAR DATOS) =================
def init_db():
    conn = db()

    conn.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        email_temp TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ================= REGISTER =================
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]

        conn = db()

        try:
            conn.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (u, p)
            )
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            return "❌ Usuario ya existe"

        conn.close()
        return redirect("/login")

    return render_template("register.html")

# ================= LOGIN =================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]

        conn = db()

        user = conn.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (u, p)
        ).fetchone()

        conn.close()

        if user:
            session["user"] = user[1]
            return redirect("/dashboard")

        return "❌ Login incorrecto"

    return render_template("login.html")

# ================= DASHBOARD =================
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")

    user = session["user"]

    conn = db()
    email = conn.execute(
        "SELECT email_temp FROM users WHERE username=?",
        (user,)
    ).fetchone()
    conn.close()

    email = email[0] if email and email[0] else "No creado"

    return render_template("dashboard.html", user=user, email=email)

# ================= CREATE EMAIL =================
@app.route("/create_email")
def create_email():

    if "user" not in session:
        return redirect("/login")

    user = session["user"]

    email = f"AZVIP{int(time.time())}@1secmail.com"

    conn = db()
    conn.execute(
        "UPDATE users SET email_temp=? WHERE username=?",
        (email, user)
    )
    conn.commit()
    conn.close()

    return redirect("/dashboard")

# ================= LOGOUT =================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# ================= RUN (RENDER FIX) =================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)