import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

def run_health_check():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    server.serve_forever()

# Запускаем фоновый веб-сервер для Render
threading.Thread(target=run_health_check, daemon=True).start()

import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# ⚠️ ВСТАВЬТЕ ВАШ ТОКЕН ОТ @BotFather ВНУТРИ КАВЫЧЕК:
BOT_TOKEN = "8372017983:AAHP89KqKsrxTws3cjrTc_cmNI4nUAIgi4U"

# Ваш ID группы (уже подставлен):
ADMIN_CHAT_ID = -1004459967684

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

class AdminReturn(StatesGroup):
    static_id = State()
    check_link = State()
    admin_level = State()

class DPReturn(StatesGroup):
    static_id = State()
    check_link = State()

def main_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛡 Вернуть админку", callback_data="btn_admin")],
        [InlineKeyboardButton(text="💎 Вернуть DP", callback_data="btn_dp")]
    ])

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer(
        "Выберите категорию для подачи обращения:",
        reply_markup=main_keyboard()
    )

# --- Форма: Вернуть админку ---
@dp.callback_query(F.data == "btn_admin")
async def start_admin_return(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(AdminReturn.static_id)
    await callback.message.answer("1/3. Введите ваш Статик:")
    await callback.answer()

@dp.message(AdminReturn.static_id)
async def process_admin_static(message: types.Message, state: FSMContext):
    await state.update_data(static_id=message.text)
    await state.set_state(AdminReturn.check_link)
    await message.answer("2/3. Отправьте ссылку на чек:")

@dp.message(AdminReturn.check_link)
async def process_admin_check(message: types.Message, state: FSMContext):
    await state.update_data(check_link=message.text)
    await state.set_state(AdminReturn.admin_level)
    await message.answer("3/3. Укажите уровень админки:")

@dp.message(AdminReturn.admin_level)
async def process_admin_level(message: types.Message, state: FSMContext):
    await state.update_data(admin_level=message.text)
    data = await state.get_data()
    
    user_mention = f"@{message.from_user.username}" if message.from_user.username else message.from_user.full_name
    
    text = (
        "🛡 ЗАЯВКА: ВОЗВРАТ АДМИНКИ\n\n"
        f"👤 Отправитель: {user_mention} (ID: {message.from_user.id})\n"
        f"🆔 Статик: {data['static_id']}\n"
        f"📊 Лвл админки: {data['admin_level']}\n"
        f"🧾 Ссылка на чек: {data['check_link']}"
    )
    
    try:
        await bot.send_message(chat_id=ADMIN_CHAT_ID, text=text)
        await message.answer("✅ Ваша заявка успешно отправлена!", reply_markup=main_keyboard())
    except Exception as e:
        await message.answer(f"❌ Ошибка отправки в группу: {e}")
    
    await state.clear()

# --- Форма: Вернуть DP ---
@dp.callback_query(F.data == "btn_dp")
async def start_dp_return(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(DPReturn.static_id)
    await callback.message.answer("1/2. Введите ваш Статик:")
    await callback.answer()

@dp.message(DPReturn.static_id)
async def process_dp_static(message: types.Message, state: FSMContext):
    await state.update_data(static_id=message.text)
    await state.set_state(DPReturn.check_link)
    await message.answer("2/2. Отправьте ссылку на чек:")

@dp.message(DPReturn.check_link)
async def process_dp_check(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_mention = f"@{message.from_user.username}" if message.from_user.username else message.from_user.full_name
    
    text = (
        "💎 ЗАЯВКА: ВОЗВРАТ DP\n\n"
        f"👤 Отправитель: {user_mention} (ID: {message.from_user.id})\n"
        f"🆔 Статик: {data['static_id']}\n"
        f"🧾 Ссылка на чек: {message.text}"
    )
    
    try:
        await bot.send_message(chat_id=ADMIN_CHAT_ID, text=text)
        await message.answer("✅ Ваша заявка успешно отправлена!", reply_markup=main_keyboard())
    except Exception as e:
        await message.answer(f"❌ Ошибка отправки в группу: {e}")
            
    await state.clear()

async def main():
    logging.basicConfig(level=logging.INFO)
    print("\n==================================================")
    print(">>> БОТ УСПЕШНО ЗАПУЩЕН! НЕ ЗАКРЫВАЙТЕ ЭТО ОКНО. <<<")
    print("==================================================\n")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as err:
        print(f"\n❌ ОШИБКА ЗАПУСКА: {err}\n")
        input("Нажмите Enter, чтобы закрыть окно...")
