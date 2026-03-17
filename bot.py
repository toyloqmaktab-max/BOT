import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

# --- KONFIGURATSIYA ---
TOKEN = os.getenv("8051062383:AAFmuhDvy79xDXAJnnJ_pPt9h-u0DXwh3mU")  # 🔥 MUHIM (Railway uchun)
ADMIN_ID = 7533307925  

CHANNELS_DATA = [
    {"name": "1-kanal", "id": "@webnora", "url": "https://t.me/webnora"},
    {"name": "2-kanal", "id": "@webnoragroup", "url": "https://t.me/webnoragroup"}
]

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- FOYDALANUVCHI SAQLASH ---
def save_user(user_id, username, full_name):
    if not os.path.exists("users.txt"):
        open("users.txt", "w").close()

    with open("users.txt", "r", encoding="utf-8") as f:
        users = f.read().splitlines()

    user_data = f"{user_id}|@{username if username else 'yoq'}|{full_name}"

    if not any(line.startswith(str(user_id)) for line in users):
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

    buttons = [
        [InlineKeyboardButton(text=f"➕ {ch['name']}ga a'zo bo'lish", url=ch['url'])]
        for ch in unsubscribed
    ]

    buttons.append([InlineKeyboardButton(text="Obunani tekshirish ✅", callback_data="check")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)

# --- START ---
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    save_user(message.from_user.id, message.from_user.username, message.from_user.full_name)

    admin_btn = None
    if message.from_user.id == ADMIN_ID:
        admin_btn = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="📢 Reklama yuborish")]],
            resize_keyboard=True
        )

    keyboard = await get_subscription_keyboard(message.from_user.id)

    if keyboard is None:
        await message.answer(
            f"Assalomu alaykum, {message.from_user.first_name}! 😊\nKod kiritishingiz mumkin.",
            reply_markup=admin_btn
        )
    else:
        await message.answer(
            f"Botdan foydalanish uchun avval obuna bo'ling:",
            reply_markup=keyboard
        )

# --- REKLAMA ---
@dp.message(F.text == "📢 Reklama yuborish", F.from_user.id == ADMIN_ID)
async def start_broadcast(message: types.Message):
    await message.answer("Xabar yuboring:")

@dp.message(F.from_user.id == ADMIN_ID)
async def broadcast_handler(message: types.Message):
    if not os.path.exists("users.txt"):
        return

    with open("users.txt", "r", encoding="utf-8") as f:
        users = f.read().splitlines()

    count = 0

    for line in users:
        try:
            await message.copy_to(chat_id=int(line.split("|")[0]))
            count += 1
            await asyncio.sleep(0.05)
        except:
            pass

    await message.answer(f"✅ {count} kishiga yuborildi")

# --- CHECK ---
@dp.callback_query(F.data == "check")
async def check_callback(call: types.CallbackQuery):
    keyboard = await get_subscription_keyboard(call.from_user.id)

    if keyboard is None:
        await call.message.edit_text("✅ Obuna tasdiqlandi!")
    else:
        await call.answer("Hali obuna bo‘lmagansiz ❌", show_alert=True)

# --- KOD ---
@dp.message(F.text == "1510")
async def send_videos(message: types.Message):
    keyboard = await get_subscription_keyboard(message.from_user.id)

    if keyboard:
        await message.answer("Avval obuna bo‘ling ⚠️", reply_markup=keyboard)
        return

    album = MediaGroupBuilder()

    video_ids = [
        "BQACAgIAAxkBAAIFQWm4FZI71U9io7H5AeDL9xHgUJ7AAAJJnQACSgHBSefbmaiQ5dy_OgQ",
        "BQACAgIAAxkBAAID0Wm36WohApmBrhhDsvImwfk8E0e1AAIimgAC2xkxSUj4uGkDuM8wOgQ"
    ]

    for v in video_ids:
        album.add_video(media=v)

    await message.answer_media_group(media=album.build(), protect_content=True)

# --- RUN ---
async def main():
    print("Bot ishga tushdi 🚀")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
