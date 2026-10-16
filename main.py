import os, sqlite3, json, logging
from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, filters, ContextTypes, CallbackQueryHandler

TOKEN = os.environ.get("TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "8343589720"))
logging.basicConfig(level=logging.INFO)

def get_db():
    c = sqlite3.connect("bot.db", check_same_thread=False, timeout=30)
    c.execute("PRAGMA journal_mode=WAL;")
    return c

db = get_db()
db.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, points REAL DEFAULT 17.5)")
db.execute("CREATE TABLE IF NOT EXISTS menus (key TEXT PRIMARY KEY, layout TEXT)")
layout = [[{"text":"خدمات الرشق","type":"s"}],[{"text":"الخدمات","type":"a"},{"text":"طلباتي","type":"b"}],[{"text":"شحن البوت","type":"c"},{"text":"رصيدي","type":"d"}]]
db.execute("INSERT OR IGNORE INTO menus VALUES (?,?)", ("main", json.dumps(layout, ensure_ascii=False)))
db.commit(); db.close()

def is_admin(uid): return uid == ADMIN_ID

async def all_msg(update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        await update.callback_query.answer()
        return
    txt = update.message.text if update.message else ""
    uid = update.effective_user.id

    if txt.startswith("/start"):
        if is_admin(uid):
            kb = [["ادارة القوائم والازرار","الاحصائيات"],["ضبط رصيد"]]
            await update.message.reply_text("لوحة الادمن:", reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))
        else:
            db = get_db()
            ly = json.loads(db.execute("SELECT layout FROM menus WHERE key='main'").fetchone()[0])
            db.close()
            kb = [[b['text'] for b in r] for r in ly]
            await update.message.reply_text("مرحبا بك", reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))
        return

    if is_admin(uid) and txt == "ادارة القوائم والازرار":
        db = get_db()
        ly = json.loads(db.execute("SELECT layout FROM menus WHERE key='main'").fetchone()[0])
        db.close()
        t = "القائمة الحالية:\n"
        for r in ly: t += " - ".join([b['text'] for b in r]) + "\n"
        await update.message.reply_text(t + "\nتقدر تعدلها بعدين من البوت نفسه")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT, all_msg))
    app.add_handler(CallbackQueryHandler(all_msg))
    print("Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
