#!/usr/bin/env python3
"""
🎮 Game Top-Up Telegram Bot
Qo'llab-quvvatlanadi: PUBG Mobile, Steam Wallet, Free Fire + Boshqalar
Kichik buyurtmalar: Avtomatik | Katta buyurtmalar: Admin tasdiqi
"""

import sqlite3
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes, ConversationHandler
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# ================================================================
#  ⚙️  SOZLAMALAR — shu joyni o'zgartiring
# ================================================================
BOT_TOKEN = "8926329145:AAHnGeLP7IUWZvEyluL2T7v0KHAJEZr7eCY"          # @BotFather dan oling
ADMIN_IDS = [8299430341]                     # Sizning Telegram ID'ingiz
AUTO_THRESHOLD = 500_000                    # So'm — shu summadan past = avtomatik

# To'lov rekvizitlari
CLICK_CARD   = "9860 1401 1838 2781"
Viza_CARD   = "4916 9903 1817 1755"
USDT_WALLET  = "TXxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
USDT_RATE    = 11_979                       # 1 USDT = ... so'm (yangilab turing)
ADMIN_USERNAME = "@otabek_qadamovv"          # Yordam uchun admin

# ================================================================
#  🎮  O'YINLAR VA PAKETLAR
# ================================================================
GAMES = {
    "pubg": {
        "name": "🎮 PUBG Mobile (UC)",
        "id_label": "PUBG Player ID",
        "id_hint": "Misol: 5123456789",
        "packages": [
            {"label": "60 UC",   "price": 17_000},
            {"label": "300 UC",  "price": 78_000},
            {"label": "600 UC",  "price": 142_000},
            {"label": "1500 UC", "price": 345_000},
            {"label": "3000 UC", "price": 665_000},
            {"label": "6000 UC", "price": 1_300_000},
        ],
    },
    "steam": {
        "name": "💚 Steam Wallet",
        "id_label": "Steam Login yoki Email",
        "id_hint": "Misol: username@gmail.com",
        "packages": [
            {"label": "$5",   "price": 65_000},
            {"label": "$10",  "price": 130_000},
            {"label": "$20",  "price": 255_000},
            {"label": "$50",  "price": 635_000},
            {"label": "$100", "price": 1_260_000},
        ],
    },
    "freefire": {
        "name": "💎 Free Fire (Diamonds)",
        "id_label": "Free Fire Player ID",
        "id_hint": "Misol: 1234567890",
        "packages": [
            {"label": "100 💎",  "price": 18_000},
            {"label": "310 💎",  "price": 50_000},
            {"label": "520 💎",  "price": 80_000},
            {"label": "1060 💎", "price": 160_000},
            {"label": "2180 💎", "price": 320_000},
            {"label": "5600 💎", "price": 800_000},
        ],
    },
    "mlbb": {
        "name": "⚔️ Mobile Legends (Diamonds)",
        "id_label": "MLBB User ID",
        "id_hint": "Misol: 123456789 (Server: 1234)",
        "packages": [
            {"label": "86 💎",   "price": 20_000},
            {"label": "172 💎",  "price": 40_000},
            {"label": "257 💎",  "price": 58_000},
            {"label": "706 💎",  "price": 155_000},
            {"label": "2195 💎", "price": 470_000},
            {"label": "5532 💎", "price": 1_150_000},
        ],
    },
    "valorant": {
        "name": "🔫 Valorant (VP)",
        "id_label": "Riot ID",
        "id_hint": "Misol: PlayerName#1234",
        "packages": [
            {"label": "475 VP",  "price": 60_000},
            {"label": "1000 VP", "price": 120_000},
            {"label": "2050 VP", "price": 240_000},
            {"label": "3650 VP", "price": 420_000},
            {"label": "5350 VP", "price": 600_000},
        ],
    },
    "other": {
        "name": "🌐 Boshqa o'yinlar",
        "id_label": "O'yin ID / Username",
        "id_hint": "O'yin ID yoki username",
        "packages": [],
    },
}

# ================================================================
#  🗄️  MA'LUMOTLAR BAZASI (SQLite)
# ================================================================
DB_PATH = "orders.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id      INTEGER NOT NULL,
            username     TEXT,
            game         TEXT NOT NULL,
            package      TEXT NOT NULL,
            price        INTEGER NOT NULL,
            game_acc_id  TEXT NOT NULL,
            payment      TEXT NOT NULL,
            status       TEXT DEFAULT 'pending',
            note         TEXT,
            created_at   TEXT,
            updated_at   TEXT
        )
    """)
    conn.commit()
    conn.close()

def db_save_order(user_id, username, game, package, price, game_acc_id, payment):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("""
        INSERT INTO orders
            (user_id, username, game, package, price, game_acc_id, payment, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (user_id, username, game, package, price, game_acc_id, payment, now, now))
    order_id = c.lastrowid
    conn.commit()
    conn.close()
    return order_id

def db_update_status(order_id, status, note=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute(
        "UPDATE orders SET status=?, note=?, updated_at=? WHERE id=?",
        (status, note, now, order_id)
    )
    conn.commit()
    conn.close()

def db_get_order(order_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM orders WHERE id=?", (order_id,))
    row = c.fetchone()
    conn.close()
    return row

def db_get_pending():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM orders WHERE status='pending' ORDER BY created_at DESC")
    rows = c.fetchall()
    conn.close()
    return rows

def db_get_user_orders(user_id, limit=5):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "SELECT * FROM orders WHERE user_id=? ORDER BY created_at DESC LIMIT ?",
        (user_id, limit)
    )
    rows = c.fetchall()
    conn.close()
    return rows

# ================================================================
#  🛠️  YORDAMCHI FUNKSIYALAR
# ================================================================
def fmt(price: int) -> str:
    """100000 → '100 000 so'm'"""
    return f"{price:,} so'm".replace(",", " ")

def status_emoji(status: str) -> str:
    return {"pending": "⏳", "auto_done": "⚡", "approved": "✅", "rejected": "❌"}.get(status, "❓")

def get_payment_details(method: str, amount: int) -> str:
    if method == "click":
        return (
            f"💳 *Click orqali to'lov:*\n"
            f"Karta raqami: `{CLICK_CARD}`\n"
            f"Summa: *{fmt(amount)}*\n"
            f"Izoh: `GAME TOPUP`"
        )
    elif method == "payme":
        return (
            f"💳 *Payme orqali to'lov:*\n"
            f"Karta raqami: `{PAYME_CARD}`\n"
            f"Summa: *{fmt(amount)}*"
        )
    elif method == "usdt":
        usdt = round(amount / USDT_RATE, 2)
        return (
            f"💰 *USDT (TRC20) orqali to'lov:*\n"
            f"Manzil: `{USDT_WALLET}`\n"
            f"Summa: *{usdt} USDT*\n"
            f"_(Kurs: 1 USDT ≈ {fmt(USDT_RATE)})_"
        )
    return "❓ To'lov ma'lumotlari uchun adminga murojaat qiling."

# ================================================================
#  ⌨️  KLAVIATURALAR
# ================================================================
def kb_main():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🛒 Top-up qilish",     callback_data="topup")],
        [InlineKeyboardButton("📋 Buyurtmalarim",     callback_data="my_orders")],
        [InlineKeyboardButton("❓ Yordam / Bog'lanish", callback_data="help")],
    ])

def kb_games():
    rows = []
    for gid, g in GAMES.items():
        rows.append([InlineKeyboardButton(g["name"], callback_data=f"game_{gid}")])
    rows.append([InlineKeyboardButton("⬅️ Bosh menyu", callback_data="main")])
    return InlineKeyboardMarkup(rows)

def kb_packages(game_id):
    pkgs = GAMES[game_id]["packages"]
    rows = []
    for i, p in enumerate(pkgs):
        rows.append([InlineKeyboardButton(
            f"{p['label']}  —  {fmt(p['price'])}",
            callback_data=f"pkg_{game_id}_{i}"
        )])
    rows.append([InlineKeyboardButton("⬅️ Orqaga", callback_data="topup")])
    return InlineKeyboardMarkup(rows)

def kb_payment():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💳 Click",        callback_data="pay_click")],
        [InlineKeyboardButton("💳 Payme",        callback_data="pay_payme")],
        [InlineKeyboardButton("💰 USDT (TRC20)", callback_data="pay_usdt")],
        [InlineKeyboardButton("⬅️ Orqaga",       callback_data="topup")],
    ])

def kb_confirm():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Tasdiqlash",    callback_data="confirm")],
        [InlineKeyboardButton("❌ Bekor qilish",  callback_data="main")],
    ])

def kb_admin(order_id, user_id):
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"adm_ok_{order_id}_{user_id}"),
        InlineKeyboardButton("❌ Rad etish",  callback_data=f"adm_no_{order_id}_{user_id}"),
    ]])

def kb_back_main():
    return InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Bosh menyu", callback_data="main")]])

# ================================================================
#  📝  CONVERSATION STATES
# ================================================================
MAIN, SELECT_GAME, SELECT_PKG, ENTER_ID, SELECT_PAY, CONFIRM = range(6)

# ================================================================
#  🤖  HANDLERLAR
# ================================================================
async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"Salom, *{user.first_name}*! 👋\n\n"
        "🎮 *Game Top-Up Bot*\n"
        "PUBG, Steam, Free Fire, MLBB, Valorant\n"
        "va boshqa o'yinlarga tez va xavfsiz pul yuklash.\n\n"
        f"⚡ _{fmt(AUTO_THRESHOLD)}_ gacha — avtomatik\n"
        f"🔍 Undan yuqori — admin tasdiqlaydi\n\n"
        "Boshlash uchun pastdagi tugmani bosing:",
        parse_mode="Markdown",
        reply_markup=kb_main()
    )
    return MAIN


async def btn(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    d = q.data
    uid = q.from_user.id

    # ---------- Bosh menyu ----------
    if d == "main":
        await q.edit_message_text(
            "🏠 *Bosh menyu*\nNima qilmoqchisiz?",
            parse_mode="Markdown", reply_markup=kb_main()
        )
        return MAIN

    elif d == "help":
        await q.edit_message_text(
            "❓ *Yordam*\n\n"
            "1️⃣ \"Top-up qilish\" tugmasini bosing\n"
            "2️⃣ O'yinni tanlang\n"
            "3️⃣ Paketni tanlang\n"
            "4️⃣ Game ID / login kiriting\n"
            "5️⃣ To'lov usulini tanlang\n"
            "6️⃣ Tasdiqlang va to'lovni amalga oshiring\n\n"
            f"⚡ *{fmt(AUTO_THRESHOLD)} gacha* — avtomatik (1-5 daqiqa)\n"
            f"🔍 *Katta summalar* — admin tasdiqlaydi (5-30 daqiqa)\n\n"
            f"📞 *Admin:* {ADMIN_USERNAME}",
            parse_mode="Markdown", reply_markup=kb_back_main()
        )
        return MAIN

    elif d == "my_orders":
        orders = db_get_user_orders(uid)
        if not orders:
            txt = "📋 Sizda hali buyurtmalar yo'q.\n\nBirinchi buyurtmangizni bering! 🎮"
        else:
            txt = "📋 *So'nggi buyurtmalaringiz:*\n\n"
            for o in orders:
                # id, user_id, username, game, package, price, game_acc_id, payment, status, note, created_at, updated_at
                em = status_emoji(o[8])
                txt += f"{em} *#{o[0]}* | {GAMES.get(o[3],{}).get('name', o[3])} | {o[4]} | {fmt(o[5])}\n"
                txt += f"    🕐 {o[10][:16]}\n\n"
        await q.edit_message_text(txt, parse_mode="Markdown", reply_markup=kb_back_main())
        return MAIN

    # ---------- O'yin tanlash ----------
    elif d == "topup":
        await q.edit_message_text(
            "🎮 *O'yinni tanlang:*",
            parse_mode="Markdown", reply_markup=kb_games()
        )
        return SELECT_GAME

    elif d.startswith("game_"):
        gid = d[5:]
        g = GAMES.get(gid)
        if not g:
            await q.edit_message_text("❌ O'yin topilmadi.", reply_markup=kb_back_main())
            return MAIN

        if gid == "other":
            await q.edit_message_text(
                "🌐 *Boshqa o'yinlar*\n\n"
                f"Iltimos, admin bilan bog'laning:\n{ADMIN_USERNAME}\n\n"
                "O'yin nomi, kerakli miqdor va game ID'ingizni yuboring.",
                parse_mode="Markdown", reply_markup=kb_back_main()
            )
            return MAIN

        ctx.user_data["game_id"] = gid
        await q.edit_message_text(
            f"{g['name']} uchun *paket tanlang:*",
            parse_mode="Markdown", reply_markup=kb_packages(gid)
        )
        return SELECT_PKG

    # ---------- Paket tanlash ----------
    elif d.startswith("pkg_"):
        _, gid, idx = d.split("_")
        pkg = GAMES[gid]["packages"][int(idx)]
        ctx.user_data["game_id"] = gid
        ctx.user_data["package"] = pkg

        await q.edit_message_text(
            f"✅ Tanlandi: *{pkg['label']}* — {fmt(pkg['price'])}\n\n"
            f"📝 *{GAMES[gid]['id_label']}* kiriting:\n"
            f"_{GAMES[gid]['id_hint']}_",
            parse_mode="Markdown"
        )
        return ENTER_ID

    # ---------- To'lov usuli ----------
    elif d.startswith("pay_"):
        method = d[4:]
        ctx.user_data["payment"] = method

        gid  = ctx.user_data["game_id"]
        pkg  = ctx.user_data["package"]
        gacc = ctx.user_data["game_acc"]
        g    = GAMES[gid]
        m_names = {"click": "Click 💳", "payme": "Payme 💳", "usdt": "USDT (TRC20) 💰"}

        await q.edit_message_text(
            f"📋 *Buyurtmani tasdiqlang*\n\n"
            f"🎮 O'yin:     {g['name']}\n"
            f"📦 Paket:     {pkg['label']}\n"
            f"💰 Narx:      {fmt(pkg['price'])}\n"
            f"🆔 Game ID:   `{gacc}`\n"
            f"💳 To'lov:    {m_names.get(method, method)}\n\n"
            f"Hamma ma'lumot to'g'rimi?",
            parse_mode="Markdown", reply_markup=kb_confirm()
        )
        return CONFIRM

    # ---------- Tasdiqlash ----------
    elif d == "confirm":
        user  = q.from_user
        gid   = ctx.user_data["game_id"]
        pkg   = ctx.user_data["package"]
        gacc  = ctx.user_data["game_acc"]
        pay   = ctx.user_data["payment"]
        g     = GAMES[gid]
        price = pkg["price"]

        order_id = db_save_order(
            user.id, user.username or user.first_name,
            gid, pkg["label"], price, gacc, pay
        )

        if price <= AUTO_THRESHOLD:
            # ⚡ Avtomatik
            db_update_status(order_id, "auto_done", "Avtomatik bajarildi")
            pay_info = get_payment_details(pay, price)
            await q.edit_message_text(
                f"⚡ *Buyurtma #{order_id} — Avtomatik*\n\n"
                f"{pay_info}\n\n"
                f"───────────────────\n"
                f"✅ To'lov qilinganidan so'ng *1–5 daqiqa* ichida\n"
                f"{g['name']} hisobingizga *{pkg['label']}* yuklanadi!\n\n"
                f"Savol bo'lsa: {ADMIN_USERNAME}",
                parse_mode="Markdown", reply_markup=kb_back_main()
            )
        else:
            # 🔍 Manuel — adminga yuborish
            await q.edit_message_text(
                f"✅ *Buyurtma #{order_id} qabul qilindi*\n\n"
                f"🔍 Bu buyurtma admin tomonidan\n"
                f"ko'rib chiqiladi *(5–30 daqiqa)*.\n\n"
                f"Tasdiqlanganda sizga xabar keladi! 📲\n\n"
                f"Savol bo'lsa: {ADMIN_USERNAME}",
                parse_mode="Markdown", reply_markup=kb_back_main()
            )
            # Adminga xabar
            m_names = {"click": "Click 💳", "payme": "Payme 💳", "usdt": "USDT (TRC20) 💰"}
            admin_txt = (
                f"🔔 *Yangi buyurtma #{order_id}* _(katta summa)_\n\n"
                f"👤 @{user.username or '—'} (ID: `{user.id}`)\n"
                f"🎮 O'yin:   {g['name']}\n"
                f"📦 Paket:   {pkg['label']}\n"
                f"💰 Narx:    {fmt(price)}\n"
                f"🆔 Game ID: `{gacc}`\n"
                f"💳 To'lov:  {m_names.get(pay, pay)}\n"
                f"🕐 Vaqt:    {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            )
            for aid in ADMIN_IDS:
                try:
                    await ctx.bot.send_message(
                        aid, admin_txt,
                        parse_mode="Markdown",
                        reply_markup=kb_admin(order_id, user.id)
                    )
                except Exception as e:
                    logging.warning(f"Admin {aid} ga yuborib bo'lmadi: {e}")

        ctx.user_data.clear()
        return MAIN

    # ---------- Admin tugmalari ----------
    elif d.startswith("adm_ok_") or d.startswith("adm_no_"):
        if uid not in ADMIN_IDS:
            await q.answer("❌ Ruxsat yo'q!", show_alert=True)
            return MAIN

        parts    = d.split("_")
        action   = parts[1]          # ok yoki no
        order_id = int(parts[2])
        cust_id  = int(parts[3])
        order    = db_get_order(order_id)

        if not order:
            await q.edit_message_text("❌ Buyurtma topilmadi.")
            return MAIN

        if action == "ok":
            db_update_status(order_id, "approved", f"Admin {uid} tomonidan tasdiqlandi")
            await q.edit_message_text(
                f"✅ Buyurtma *#{order_id}* tasdiqlandi va bajarildi!\n\n"
                f"O'yin: {GAMES.get(order[3],{}).get('name', order[3])}\n"
                f"Paket: {order[4]} | {fmt(order[5])}\n"
                f"Game ID: `{order[6]}`",
                parse_mode="Markdown"
            )
            try:
                await ctx.bot.send_message(
                    cust_id,
                    f"🎉 *Buyurtma #{order_id} bajarildi!*\n\n"
                    f"Hisobingizga *{order[4]}* yuklandi!\n"
                    f"Xarid uchun rahmat! 🙏",
                    parse_mode="Markdown"
                )
            except:
                pass
        else:
            db_update_status(order_id, "rejected", f"Admin {uid} tomonidan rad etildi")
            await q.edit_message_text(f"❌ Buyurtma #{order_id} rad etildi.")
            try:
                await ctx.bot.send_message(
                    cust_id,
                    f"❌ *Buyurtma #{order_id} rad etildi.*\n\n"
                    f"Muammo bo'lsa admin bilan bog'laning:\n{ADMIN_USERNAME}",
                    parse_mode="Markdown"
                )
            except:
                pass

        return MAIN

    return MAIN


async def handle_text(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """ENTER_ID holatida game account ID qabul qilish"""
    text = update.message.text.strip()
    if not text:
        await update.message.reply_text("❌ Bo'sh qiymat kiritdingiz. Qayta kiriting:")
        return ENTER_ID

    ctx.user_data["game_acc"] = text
    gid = ctx.user_data.get("game_id", "")
    g   = GAMES.get(gid, {})

    await update.message.reply_text(
        f"✅ *{g.get('id_label', 'Game ID')}:* `{text}`\n\n"
        f"💳 *To'lov usulini tanlang:*",
        parse_mode="Markdown",
        reply_markup=kb_payment()
    )
    return SELECT_PAY


# ================================================================
#  👑  ADMIN BUYRUQLARI
# ================================================================
async def cmd_orders(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Admin: /orders — kutilayotgan buyurtmalarni ko'rish"""
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("❌ Bu buyruq faqat admin uchun.")
        return

    orders = db_get_pending()
    if not orders:
        await update.message.reply_text("✅ Hozirda kutilayotgan buyurtmalar yo'q.")
        return

    await update.message.reply_text(f"⏳ *Kutilayotgan buyurtmalar: {len(orders)} ta*", parse_mode="Markdown")
    for o in orders[:15]:
        txt = (
            f"📋 *Buyurtma #{o[0]}*\n"
            f"👤 @{o[2]} (ID: `{o[1]}`)\n"
            f"🎮 {GAMES.get(o[3],{}).get('name', o[3])} | {o[4]}\n"
            f"💰 {fmt(o[5])}\n"
            f"🆔 `{o[6]}`\n"
            f"💳 {o[7]}\n"
            f"🕐 {o[10]}"
        )
        await update.message.reply_text(
            txt, parse_mode="Markdown",
            reply_markup=kb_admin(o[0], o[1])
        )

async def cmd_stats(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Admin: /stats — statistika"""
    if update.effective_user.id not in ADMIN_IDS:
        return

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(*), SUM(price) FROM orders WHERE status != 'rejected'")
    total_count, total_sum = c.fetchone()
    c.execute("SELECT COUNT(*) FROM orders WHERE status = 'pending'")
    pending = c.fetchone()[0]
    c.execute("SELECT COUNT(*), SUM(price) FROM orders WHERE DATE(created_at) = DATE('now')")
    today_count, today_sum = c.fetchone()
    conn.close()

    await update.message.reply_text(
        f"📊 *Bot statistikasi*\n\n"
        f"📦 Jami buyurtmalar: *{total_count or 0}*\n"
        f"💰 Jami summa: *{fmt(total_sum or 0)}*\n"
        f"⏳ Kutilayotgan: *{pending}*\n\n"
        f"🗓 *Bugun:*\n"
        f"   Buyurtmalar: *{today_count or 0}*\n"
        f"   Summa: *{fmt(today_sum or 0)}*",
        parse_mode="Markdown"
    )

# ================================================================
#  🚀  ISHGA TUSHIRISH
# ================================================================
def main():
    init_db()
    print("✅ Ma'lumotlar bazasi tayyor")

    app = Application.builder().token(BOT_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", cmd_start)],
        states={
            MAIN:        [CallbackQueryHandler(btn)],
            SELECT_GAME: [CallbackQueryHandler(btn)],
            SELECT_PKG:  [CallbackQueryHandler(btn)],
            ENTER_ID:    [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text),
                CallbackQueryHandler(btn),
            ],
            SELECT_PAY:  [CallbackQueryHandler(btn)],
            CONFIRM:     [CallbackQueryHandler(btn)],
        },
        fallbacks=[CommandHandler("start", cmd_start)],
        allow_reentry=True,
        per_message=False,
    )

    app.add_handler(conv)
    app.add_handler(CommandHandler("orders", cmd_orders))
    app.add_handler(CommandHandler("stats",  cmd_stats))
    # Admin tugmalari conversation tashqarisida ham ishlashi uchun:
    app.add_handler(CallbackQueryHandler(btn, pattern=r"^adm_"))

    print("🤖 Bot ishga tushdi! Ctrl+C bilan to'xtatish mumkin.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
