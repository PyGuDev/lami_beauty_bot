import logging

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor
from aiogram_dialog import DialogRegistry, StartMode, DialogManager

from config import BOT_TOKEN, OWNER

# Configure logging
from dialogs import calendar_dialog, MySG
from services.handlers import MainHandler

logging.basicConfig(level=logging.INFO)

# prerequisites
if not BOT_TOKEN:
    exit("No token provided")

storage = MemoryStorage()
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot, storage=storage)
registry = DialogRegistry(dp)
registry.register(calendar_dialog)


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    markup = types.InlineKeyboardMarkup(resize_keyboard=True, row_width=2)
    enroll = types.InlineKeyboardButton('Записаться', callback_data="enroll")
    markup.add(enroll)
    if message.from_user.id == OWNER:
        get_records = types.InlineKeyboardButton('Получить все записи', callback_data="get_records")
        markup.add(get_records)

    await bot.send_message(
        message.chat.id,
        text="Рады приветствовать вас!!!",
        reply_markup=markup)


@dp.callback_query_handler(lambda c: c.data == 'enroll')
async def process_start_command(callback_query: types.CallbackQuery, dialog_manager: DialogManager):
    await dialog_manager.start(MySG.main, mode=StartMode.RESET_STACK)


@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    await message.reply("Запись на ламинирование")


@dp.message_handler(content_types=['text'])
async def process_help_command(message: types.Message):
    logging.warning(message)
    handler = MainHandler(message.bot)
    await handler.message_handler(message)


@dp.callback_query_handler(lambda c: c.data == 'get_records')
async def process_get_records(callback_query: types.CallbackQuery):
    handler = MainHandler(callback_query.bot)
    await handler.get_records()


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
