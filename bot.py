import logging
import uuid
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pymongo import MongoClient

# ================= CONFIG =================
BOT_TOKEN = "8305203190:AAGWvX2wfF177WRqOH-VqvH-RXAj3tz5Ojs"     # <-- put NEW token here
ADMIN_ID = 7579033502                     # <-- your admin ID
SUPPORT_USERNAME = "@qwallethelperbot"    # <-- support contact
MONGO_URI = "mongodb+srv://hdnfaer:6rcwEsRoRUyY5URP@qwallet1.regstjp.mongodb.net/Qwallet1"       # <-- your MongoDB URI
# =========================================

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)

mongo = MongoClient(MONGO_URI)
db = mongo["qwallet"]
users = db["users"]
withdraws = db["withdraws"]

# ============ HELPERS ============
def get_or_create_user(tg_user):
    user = users.find_one({"tg_id": tg_user.id})
    if not user:
        user = {
            "tg_id": tg_user.id,
            "username": tg_user.username or "NoUsername",
            "uid": f"UQ-{str(uuid.uuid4())[:6].upper()}",
            "balance": 0,
            "status": "active",
            "total_withdraw": 0
        }
        users.insert_one(user)
    return user


def main_menu():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("💰 Balance", callback_data="balance"),
        InlineKeyboardButton("💸 Withdraw", callback_data="withdraw"),
        InlineKeyboardButton("👤 Profile", callback_data="profile"),
        InlineKeyboardButton("🆘 Support", callback_data="support"),
    )
    return kb


def back_button():
    return InlineKeyboardMarkup().add(
        InlineKeyboardButton("⬅️ Back", callback_data="back")
    )

# ============ START ============
@dp.message_handler(commands=["start"])
async def start(msg: types.Message):
    user = get_or_create_user(msg.from_user)
    text = (
        "💼 <b>Q Wallet</b>\n\n"
        f"💰 Balance: <b>{user['balance']} Q</b>\n"
        "💱 Rate: <b>1 Q = 1 USDT</b>\n\n"
        "Use the buttons below 👇"
    )
    await msg.answer(text, reply_markup=main_menu())

# ============ CALLBACKS ============
@dp.callback_query_handler(lambda c: True)
async def callbacks(call: types.CallbackQuery):
    user = users.find_one({"tg_id": call.from_user.id})

    # BALANCE
    if call.data == "balance":
        text = (
            "💰 <b>Your Balance</b>\n\n"
            f"Available: <b>{user['balance']} Q</b>\n"
            "💱 1 Q = 1 USDT"
        )
        await call.message.edit_text(text, reply_markup=back_button())

    # PROFILE
    elif call.data == "profile":
        text = (
            "👤 <b>Your Profile</b>\n\n"
            f"🆔 UID: <code>{user['uid']}</code>\n"
            f"👤 Username: @{user['username']}\n"
            f"💰 Balance: {user['balance']} Q\n"
            f"📊 Status: {user['status']}\n"
            f"💸 Total Withdraw: {user['total_withdraw']} USDT"
        )
        await call.message.edit_text(text, reply_markup=back_button())

    # WITHDRAW
    elif call.data == "withdraw":
        text = (
            "💸 <b>Withdraw USDT</b>\n\n"
            "• Minimum withdraw: <b>100 Q</b>\n"
            "• Rate: <b>1 Q = 1 USDT</b>\n"
            "• Network: TRC20 / BEP20\n"
            "• Manual approval\n\n"
            "📩 Send withdraw details to admin."
        )
        await call.message.edit_text(text, reply_markup=back_button())

    # SUPPORT
    elif call.data == "support":
        text = (
            "🆘 <b>Support</b>\n\n"
            f"Contact here:\n{SUPPORT_USERNAME}"
        )
        await call.message.edit_text(text, reply_markup=back_button())

    # BACK TO HOME
    elif call.data == "back":
        text = (
            "💼 <b>Q Wallet</b>\n\n"
            f"💰 Balance: <b>{user['balance']} Q</b>\n"
            "💱 Rate: <b>1 Q = 1 USDT</b>\n\n"
            "Use the buttons below 👇"
        )
        await call.message.edit_text(text, reply_markup=main_menu())

    await call.answer()

# ============ RUN ============
if __name__ == "__main__":
    executor.start_polling(dp)
