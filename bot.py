from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import sqlite3
import random

TOKEN = "8885922629:AAEkekZPheAaKdu4hzhTTKjQl3s5AVYnp_Q"

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

# ---------------- START ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 AZVIP Bot activo\n\n/newmail → crear correo\n/mails → ver correos"
    )

# ---------------- NEWMAIL ----------------
async def newmail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_id = str(update.effective_user.id)

    code = random.randint(10000, 99999)
    email = f"AZVIP-{code}@1secmail.com"

    conn = db()
    conn.execute(
        "INSERT INTO users (tg_id, email) VALUES (?,?)",
        (tg_id, email)
    )
    conn.commit()
    conn.close()

    await update.message.reply_text(f"📧 Correo creado:\n{email}")

# ---------------- MAILS ----------------
async def mails(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_id = str(update.effective_user.id)

    conn = db()
    data = conn.execute(
        "SELECT email FROM users WHERE tg_id=?",
        (tg_id,)
    ).fetchall()
    conn.close()

    if not data:
        await update.message.reply_text("❌ No tienes correos")
        return

    text = "📬 Tus correos:\n\n"

    for i, e in enumerate(data):
        text += f"{i+1}. {e[0]}\n"

    await update.message.reply_text(text)

# ---------------- APP ----------------
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("newmail", newmail))
app.add_handler(CommandHandler("mails", mails))

print("🚀 Sistema AZVIP activo...")

app.run_polling()