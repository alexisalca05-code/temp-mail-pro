from flask import Flask, render_template, request, redirect, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "azvip_secret"

@app.route("/")
def home():
    return redirect("/login")

# ================= DB =================
def db():
    return sqlite3.connect("database.db")

# ================= INIT =================
def init_db():
    conn = db()

    # BORRA TABLA ANTERIOR
    conn.execute("DROP TABLE IF EXISTS users")

    # CREA TABLA NUEVA
    conn.execute("""
    CREATE TABLE users (
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
            return "Usuario ya existe"

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

        return "Login incorrecto"

    return render_template("login.html")

# ================= # ================= LOGOUT ================= =================
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

    email = email[0] if email else "No creado"

    return render_template("dashboard.html", user=user, email=email)
# ================= LOGOUT =================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# ================= RUN =================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )