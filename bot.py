import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

# --- KONFIGURATSIYA ---
TOKEN = "8051062383:AAFmuhDvy79xDXAJnnJ_pPt9h-u0DXwh3mU"
ADMIN_ID = 7533307925  

CHANNELS_DATA = [
    {"name": "1-kanal", "id": "@webnora", "url": "https://t.me/webnora"},
    {"name": "2-kanal", "id": "@webnoragroup", "url": "https://t.me/webnoragroup"}
]

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- FOYDALANUVCHILARNI BAZAGA SAQLASH ---
def save_user(user_id, username, full_name):
    if not os.path.exists("users.txt"):
        with open("users.txt", "w", encoding="utf-8") as f: f.write("")
    
    with open("users.txt", "r", encoding="utf-8") as f:
        users = f.read().splitlines()
    
    user_data = f"{user_id}|@{username if username else 'yoq'}|{full_name}"
    
    exists = False
    for line in users:
        if line.startswith(str(user_id)):
            exists = True
            break
            
    if not exists:
        with open("users.txt", "a", encoding="utf-8") as f:
            f.write(user_data + "\n")

# --- OBUNA TEKSHIRISH ---
async def get_subscription_keyboard(user_id):
    unsubscribed = []
    for channel in CHANNELS_DATA:
        try:
            member = await bot.get_chat_member(chat_id=channel["id"], user_id=user_id)
            if member.status in ["left", "kicked"]:
                unsubscribed.append(channel)
        except:
            unsubscribed.append(channel)
    
    if not unsubscribed:
        return None

    buttons = [[InlineKeyboardButton(text=f"➕ {ch['name']}ga a'zo bo'lish", url=ch['url'])] for ch in unsubscribed]
    buttons.append([InlineKeyboardButton(text="Obunani tekshirish ✅", callback_data="check")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# --- START BUYRUG'I ---
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    save_user(message.from_user.id, message.from_user.username, message.from_user.full_name)
    
    admin_btn = None
    if message.from_user.id == ADMIN_ID:
        admin_btn = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="📢 Reklama yuborish")]], resize_keyboard=True)

    keyboard = await get_subscription_keyboard(message.from_user.id)
    if keyboard is None:
        await message.answer(f"Assalomu alaykum, {message.from_user.first_name}! 😊\nSiz barcha kanallarga a'zosiz. Kod kiritishingiz mumkin.", reply_markup=admin_btn)
    else:
        await message.answer(f"Assalomu alaykum, {message.from_user.first_name}! ✨\nBotdan foydalanish uchun avval obuna bo'ling:", reply_markup=keyboard)

# --- REKLAMA TARQATISH (ADMIN) ---
@dp.message(F.text == "📢 Reklama yuborish", F.from_user.id == ADMIN_ID)
async def start_broadcast(message: types.Message):
    await message.answer("Barcha foydalanuvchilarga yubormoqchi bo'lgan xabaringizni yuboring:")

@dp.message(F.from_user.id == ADMIN_ID, ~F.text.in_(["1510", "📢 Reklama yuborish"]), ~F.command)
async def broadcast_handler(message: types.Message):
    if not os.path.exists("users.txt"): return
    
    with open("users.txt", "r", encoding="utf-8") as f:
        users = f.read().splitlines()
    
    count = 0
    status_msg = await message.answer(f"⏳ Reklama {len(users)} kishiga yuborilmoqda...")
    
    for line in users:
        u_id = line.split("|")[0]
        try:
            await message.copy_to(chat_id=int(u_id))
            count += 1
            await asyncio.sleep(0.05)
        except: pass
    
    report_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👤 Foydalanuvchilar ro'yxati", callback_data="show_users")]
    ])
    
    await status_msg.edit_text(f"✅ Reklama yakunlandi!\nJami: {count} kishiga yuborildi.", reply_markup=report_kb)

# --- FOYDALANUVCHILAR RO'YXATI CALLBACK ---
@dp.callback_query(F.data == "show_users", F.from_user.id == ADMIN_ID)
async def show_users_callback(call: types.CallbackQuery):
    if not os.path.exists("users.txt"):
        await call.answer("Baza bo'sh!")
        return

    with open("users.txt", "r", encoding="utf-8") as f:
        users = f.read().splitlines()
    
    text = "📂 **Bot foydalanuvchilari:**\n\n"
    for line in users:
        parts = line.split("|")
        text += f"🆔 `{parts[0]}` — {parts[1]} ({parts[2]})\n"
    
    if len(text) > 4000:
        with open("users_list.txt", "w", encoding="utf-8") as f:
            f.write(text.replace("`", ""))
        await call.message.answer_document(types.FSInputFile("users_list.txt"), caption="Foydalanuvchilar ro'yxati")
    else:
        await call.message.answer(text, parse_mode="Markdown")
    await call.answer()

# --- OBUNA TEKSHIRISH CALLBACK ---
@dp.callback_query(F.data == "check")
async def check_callback(call: types.CallbackQuery):
    keyboard = await get_subscription_keyboard(call.from_user.id)
    if keyboard is None:
        await call.message.edit_text("Rahmat! Obuna tasdiqlandi. ✅\nEndi kod kiritishingiz mumkin.")
    else:
        await call.answer("Siz hali barcha kanallarga obuna bo'lmadingiz! ❌", show_alert=True)
        await call.message.edit_reply_markup(reply_markup=keyboard)

# --- 1510 KODI (HAR XIL VIDEOLAR) ---
@dp.message(F.text == "1510")
async def send_protected_videos(message: types.Message):
    keyboard = await get_subscription_keyboard(message.from_user.id)
    if keyboard:
        await message.answer("Koddan foydalanish uchun avval obuna bo'ling! ⚠️", reply_markup=keyboard)
        return

    await message.answer("Marhamat, videolar tayyorlanmoqda... 🔒")
    
    album = MediaGroupBuilder(caption="")
    
    # BU YERGA 5 TA HAR XIL FILE_ID QO'YING
    video_ids = [
        "BQACAgIAAxkBAAIFQWm4FZI71U9io7H5AeDL9xHgUJ7AAAJJnQACSgHBSefbmaiQ5dy_OgQ", 
        "BQACAgIAAxkBAAID0Wm36WohApmBrhhDsvImwfk8E0e1AAIimgAC2xkxSUj4uGkDuM8wOgQ", 
        "BQACAgIAAxkBAAID02m36aXmWC1_3JA_w7vfvj2eWrP5AALAoQACKo25SefrlnyOcvWmOgQ", 
        "BQACAgIAAxkBAAIFVWm4Hsmvmp5P9np5-yCd5wNNTjhgAAOeAAJKAcFJ9vzADsjl9f86BA", 
        "BQACAgIAAxkBAAIFV2m4HtnflDyiuY33zCwVEDbNdYebAAImmgAC2xkxScPOV5Xb2ECuOgQ"
    ]
    
    for v_id in video_ids:
        album.add_video(media=v_id)

    await message.answer_media_group(media=album.build(), protect_content=True)

# --- NOTOG'RI KOD ---
@dp.message(F.text)
async def wrong_code(message: types.Message):
    await message.answer("Bunday kod mavjud emas. 🧐")

async def run_bot():
    print("Bot muvaffaqiyatli ishga tushdi!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(run_bot())
