from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from crud_functions import *

# Перед отправкой убрать ключ!
API_TOKEN = 'XXX'

kb = ReplyKeyboardMarkup(resize_keyboard=True)
button = KeyboardButton(text='Рассчитать')
button2 = KeyboardButton(text='Информация')
button3 = KeyboardButton(text='Купить')
kb.add(button)
kb.add(button2)
kb.add(button3)

inline_kb = InlineKeyboardMarkup(resize_keyboard=True)
inline_button = InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='calories')
inline_button2 = InlineKeyboardButton(text='Формулы расчёта', callback_data='formulas')
inline_kb.add(inline_button)
inline_kb.add(inline_button2)

inline_kb_2 = InlineKeyboardMarkup(resize_keyboard=True)
inline_button_1 = InlineKeyboardButton(text='Продукт 1', callback_data='product_buying')
inline_button_2 = InlineKeyboardButton(text='Продукт 2', callback_data='product_buying')
inline_button_3 = InlineKeyboardButton(text='Продукт 3', callback_data='product_buying')
inline_button_4 = InlineKeyboardButton(text='Продукт 4', callback_data='product_buying')
inline_kb_2.add(inline_button_1)
inline_kb_2.add(inline_button_2)
inline_kb_2.add(inline_button_3)
inline_kb_2.add(inline_button_4)


class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()


@dp.message_handler(commands=['start'])
async def start(message):
    await message.answer('Привет! Я бот помогающий твоему здоровью.', reply_markup=kb)


@dp.message_handler(text='Рассчитать')
async def main_menu(message):
    await message.answer('Выберите опцию:', reply_markup=inline_kb)


@dp.message_handler(text='Информация')
async def info(message):
    await message.answer('Формула Миффлина-Сан Жеора – это одна из самых последних формул расчета калорий для '
                         'оптимального похудения или сохранения нормального веса.')


@dp.message_handler(text='Купить')
async def get_buying_list(message):
    db = get_all_products()
    for i in range(0, 4):
        await message.answer(f'Название: {db[i][0]} | Описание: {db[i][1]}| Цена: {db[i][2]}')
        with open(f'img/{i}.jpg', 'rb') as img:
            await message.answer_photo(img)
    await message.answer('Выберите продукт для покупки:', reply_markup=inline_kb_2)


@dp.callback_query_handler(text='product_buying')
async def send_confirm_message(call):
    await call.message.answer('Вы успешно приобрели продукт!')
    await call.answer()


@dp.callback_query_handler(text='formulas')
async def get_formulas(call):
    await call.message.answer('10 х вес (кг) + 6,25 x рост (см) – 5 х возраст (г) + 5')
    await call.answer()


@dp.callback_query_handler(text='calories')
async def set_age(call):
    await call.message.answer('Введите свой возраст:')
    await UserState.age.set()


@dp.message_handler(state=UserState.age)
async def set_growth(message, state):
    await state.update_data(age=message.text)
    await message.answer('Введите свой рост:')
    await UserState.growth.set()


@dp.message_handler(state=UserState.growth)
async def set_weight(message, state):
    await state.update_data(growth=message.text)
    await message.answer('Введите свой вес:')
    await UserState.weight.set()


@dp.message_handler(state=UserState.weight)
async def send_calories(message, state):
    await state.update_data(weight=message.text)
    data = await state.get_data()
    result_man = int(10 * int(data['weight']) + 6.25 * int(data['growth']) - 5 * int(data['age']) + 5)
    # result_women = int(10 * int(data['weight']) + 6.25 * int(data['growth']) - 5 * int(data['age']) - 161)
    await message.answer(f'Ваша норма калорий {result_man} день')
    # await message.answer(f'Ваша норма калорий {result_women} день')
    await state.finish()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
