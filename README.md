# 🎮 Game Top-Up Telegram Bot

PUBG Mobile, Steam, Free Fire, MLBB, Valorant va boshqa o'yinlar uchun
avtomatik pul yuklash boti.

---

## ⚙️ O'rnatish

### 1. Python o'rnating (3.10+)
```bash
python --version  # tekshirish
```

### 2. Kutubxonalarni o'rnating
```bash
pip install -r requirements.txt
```

### 3. `bot.py` ni oching va sozlamalarni to'ldiring

```python
BOT_TOKEN      = "YOUR_BOT_TOKEN_HERE"   # @BotFather dan oling
ADMIN_IDS      = [123456789]             # Sizning Telegram ID (@userinfobot ga yozing)
AUTO_THRESHOLD = 500_000                 # Avtomatik limit (so'm)

CLICK_CARD     = "8600 xxxx xxxx xxxx"  # Karta raqamingiz
PAYME_CARD     = "8600 xxxx xxxx xxxx"
USDT_WALLET    = "Txxxxxxxxxxxxxxxxxxx"
USDT_RATE      = 12_700                  # 1 USDT narxi (so'mda)
ADMIN_USERNAME = "@sizning_username"
```

### 4. Botni ishga tushiring
```bash
python bot.py
```

---

## 🤖 Bot imkoniyatlari

| Xususiyat | Tavsif |
|-----------|--------|
| 🎮 O'yinlar | PUBG, Steam, Free Fire, MLBB, Valorant |
| ⚡ Avtomatik | 500 000 so'm gacha buyurtmalar avtomatik |
| 🔍 Manuel | Katta summalar admin tasdiqi bilan |
| 💳 To'lovlar | Click, Payme, USDT (TRC20) |
| 📋 Tarix | Foydalanuvchi o'z buyurtmalarini ko'ra oladi |
| 📊 Statistika | Admin buyurtmalar va daromad statistikasini ko'radi |

---

## 👑 Admin buyruqlari

| Buyruq | Vazifasi |
|--------|----------|
| `/orders` | Kutilayotgan buyurtmalar ro'yxati |
| `/stats` | Bot statistikasi (jami, bugungi) |

---

## 🔄 Bot ish jarayoni

```
Foydalanuvchi:
  /start → O'yin tanlash → Paket tanlash
         → Game ID kiriting → To'lov usuli
         → Tasdiqlash → Buyurtma yuborildi

Agar narx ≤ 500 000 so'm:
  → ⚡ Avtomatik — To'lov rekvizitlari ko'rinadi
  → Foydalanuvchi to'laydi → Admin tekshiradi → UC/Diamonds yuklanadi

Agar narx > 500 000 so'm:
  → 🔍 Admin ga bildirishnoma ketadi
  → Admin ✅ Tasdiqlaydi yoki ❌ Rad etadi
  → Foydalanuvchiga xabar ketadi
```

---

## 📦 Yangi o'yin qo'shish

`bot.py` faylida `GAMES` lug'atiga qo'shing:

```python
"roblox": {
    "name": "🟡 Roblox (Robux)",
    "id_label": "Roblox Username",
    "id_hint": "Misol: CoolPlayer123",
    "packages": [
        {"label": "400 Robux",  "price": 50_000},
        {"label": "800 Robux",  "price": 95_000},
        {"label": "1700 Robux", "price": 190_000},
    ],
},
```

---

## 🖥️ Server (24/7 ishlashi uchun)

### Systemd (Linux server)
```bash
sudo nano /etc/systemd/system/gamebot.service
```

```ini
[Unit]
Description=Game Top-Up Bot
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/gamebot
ExecStart=/usr/bin/python3 bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable gamebot
sudo systemctl start gamebot
sudo systemctl status gamebot
```

---

## ❓ Savol bo'lsa
Bot kodini o'zgartirish yoki yangi xususiyat qo'shish kerak bo'lsa,
Claude bilan suhbatni davom ettiring! 😊
