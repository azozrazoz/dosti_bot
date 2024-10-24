# import asyncio
# import logging
# import sys
# import os


# from aiogram import Bot, Dispatcher, html
# from aiogram.client.default import DefaultBotProperties
# from aiogram.enums import ParseMode
# from aiogram.filters import CommandStart
# from aiogram.types import Message

# # Bot token can be obtained via https://t.me/BotFather
# TOKEN = os.getenv("SECRET_KEY")

# # All handlers should be attached to the Router (or Dispatcher)

# dp = Dispatcher()


# @dp.message(CommandStart())
# async def command_start_handler(message: Message) -> None:
#     """
#     This handler receives messages with `/start` command
#     """
#     # Most event objects have aliases for API methods that can be called in events' context
#     # For example if you want to answer to incoming message you can use `message.answer(...)` alias
#     # and the target chat will be passed to :ref:`aiogram.methods.send_message.SendMessage`
#     # method automatically or call API method directly via
#     # Bot instance: `bot.send_message(chat_id=message.chat.id, ...)`
#     await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!")


# @dp.message()
# async def echo_handler(message: Message) -> None:
#     """
#     Handler will forward receive a message back to the sender

#     By default, message handler will handle all message types (like a text, photo, sticker etc.)
#     """
#     try:
#         # Send a copy of the received message
#         await message.send_copy(chat_id=message.chat.id)
#     except TypeError:
#         # But not all the types is supported to be copied so need to handle it
#         await message.answer("Nice try!")


# async def main() -> None:
#     # Initialize Bot instance with default bot properties which will be passed to all API calls
#     bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

#     # And the run events dispatching
#     await dp.start_polling(bot)


# if __name__ == "__main__":
#     logging.basicConfig(level=logging.INFO, stream=sys.stdout)
#     asyncio.run(main())


import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio

API_TOKEN = "7741078690:AAFiy3jSb9n_k5FXA2X0hXlLEjyOd6nKbE0"

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота, диспетчера и хранилища состояний
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Состояния пользователя для отслеживания школы и класса
class UserState(StatesGroup):
    school_selected = State()
    class_selected = State()

# Данные: школы, классы и учебные материалы
data = {
    "Школа 1": {
        "Класс 1А": "Учебный материал 1А",
        "Класс 1Б": "Учебный материал 1Б"
    },
    "Школа 2": {
        "Класс 2А": "Учебный материал 2А",
        "Класс 2Б": "Учебный материал 2Б"
    },
    "Школа 3": {
        "Класс 3А": "Учебный материал 3А",
        "Класс 3Б": "Учебный материал 3Б"
    }
}

# Обработчик команды /start
@dp.message(CommandStart())
async def start(message: types.Message, state: FSMContext):
    await send_school_keyboard(message)
    await state.set_state(UserState.school_selected)

# Функция для отправки клавиатуры с выбором школы
async def send_school_keyboard(message: types.Message):
    keyboard_builder = ReplyKeyboardBuilder()
    for school in data.keys():
        keyboard_builder.add(types.KeyboardButton(text=school))
    
    keyboard = keyboard_builder.as_markup(resize_keyboard=True)
    await message.answer("Выберите школу:", reply_markup=keyboard)

# Функция для отправки клавиатуры с выбором класса
async def send_class_keyboard(message: types.Message, school: str):
    keyboard_builder = ReplyKeyboardBuilder()
    for class_name in data[school].keys():
        keyboard_builder.add(types.KeyboardButton(text=class_name))
    
    # Добавляем кнопку "Назад"
    keyboard_builder.add(types.KeyboardButton(text="Назад к школам"))
    
    keyboard = keyboard_builder.as_markup(resize_keyboard=True)
    await message.answer(f"Вы выбрали {school}. Выберите класс:", reply_markup=keyboard)

# Функция для отправки учебного материала
async def send_material(message: types.Message, selected_class: str, school: str):
    material = data[school][selected_class]
    await message.answer(f"Учебный материал для {selected_class}: {material}")

    # Добавляем кнопку "Назад"
    keyboard_builder = ReplyKeyboardBuilder()
    keyboard_builder.add(types.KeyboardButton(text="Назад к классам"))
    keyboard = keyboard_builder.as_markup(resize_keyboard=True)
    await message.answer("Выберите действие:", reply_markup=keyboard)

# Обработчик выбора школы
@dp.message(lambda message: message.text in data.keys())
async def select_school(message: types.Message, state: FSMContext):
    school = message.text
    await state.update_data(selected_school=school)
    await send_class_keyboard(message, school)
    await state.set_state(UserState.class_selected)

# Обработчик кнопки "Назад к школам"
@dp.message(lambda message: message.text == "Назад к школам")
async def back_to_schools(message: types.Message, state: FSMContext):
    await send_school_keyboard(message)
    await state.set_state(UserState.school_selected)

# Обработчик выбора класса
@dp.message(lambda message: any(message.text in classes for classes in data.values()))
async def select_class(message: types.Message, state: FSMContext):
    selected_class = message.text
    user_data = await state.get_data()
    school = user_data.get("selected_school")
    await send_material(message, selected_class, school)

# Обработчик кнопки "Назад к классам"
@dp.message(lambda message: message.text == "Назад к классам")
async def back_to_classes(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    school = user_data.get("selected_school")
    await send_class_keyboard(message, school)
    await state.set_state(UserState.class_selected)

# Основная функция для запуска бота
async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())