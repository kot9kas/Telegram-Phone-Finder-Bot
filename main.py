from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from config import API_TOKEN
import database

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


user_states = {}


button_add = KeyboardButton('Добавить телефон')
button_search_custom = KeyboardButton('Поиск по параметрам')
button_all_phones = KeyboardButton('Все телефоны')
button_delete = KeyboardButton('Удалить телефон')
menu = ReplyKeyboardMarkup(resize_keyboard=True).add(button_add, button_search_custom, button_all_phones, button_delete)


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("Привет! Я бот для поиска самых дешевых телефонов.", reply_markup=menu)

@dp.message_handler(lambda message: message.text == 'Добавить телефон')
async def request_phone_data(message: types.Message):
    user_states[message.from_user.id] = 'adding_phone'
    await message.reply("Введите данные телефонов, каждый с новой строки, например:\n'13 128GB Blue 56500 🇯🇵'\n'14 256GB Black 80000 🇺🇸'")

@dp.message_handler(lambda message: user_states.get(message.from_user.id) == 'adding_phone')
async def process_phone(message: types.Message):
    lines = message.text.strip().split('\n')
    added_count = 0
    for line in lines:
        parts = line.split()
        if len(parts) == 5:
            try:
                await database.add_telephone(parts[0], parts[1], parts[2], int(parts[3]), parts[4])
                added_count += 1
            except ValueError:
                await message.reply(f"Ошибка в строке: {line}. Неверный формат цены.")
    user_states.pop(message.from_user.id, None)
    await message.reply(f"Добавлено {added_count} телефонов.")


@dp.message_handler(lambda message: message.text == 'Поиск по параметрам')
async def request_search_details(message: types.Message):
    user_states[message.from_user.id] = 'searching_phone'
    await message.reply("Введите марку и параметры телефона, например:\n'13 Black' или '14 Black 🇺🇸' или '14 256GB Black'")

@dp.message_handler(lambda message: message.text == 'Все телефоны')
async def show_all_phones(message: types.Message):
    phones = await database.get_all_telephones()
    if phones:
        reply_message = "\n".join([f"Модель: {phone[0]}, Память: {phone[1]}, Цвет: {phone[2]}, Цена: {phone[3]}, Страна: {phone[4]}" for phone in phones])
        await message.reply(reply_message)
    else:
        await message.reply("В базе данных нет телефонов.")

@dp.message_handler(lambda message: user_states.get(message.from_user.id) == 'searching_phone')
async def search_telephone(message: types.Message):
    parts = message.text.split(maxsplit=3)
    if len(parts) < 2 or len(parts) > 4:
        await message.reply("Неправильный формат запроса. Попробуйте еще раз.")
        return

    model, color = parts[:2]
    flag = parts[2] if len(parts) == 3 else None
    storage = None
    if 'GB' in model:
        model, storage = model.split(maxsplit=1)

    phones = await database.get_telephone_by_details(model, storage, color, flag)
    if phones:
        reply_message = "\n".join([f"Модель: {phone[0]}, Память: {phone[1]}, Цвет: {phone[2]}, Цена: {phone[3]}, Страна: {phone[4]}" for phone in phones])
        await message.reply(reply_message)
    else:
        await message.reply("Телефоны не найдены.")
    
    user_states.pop(message.from_user.id, None)

@dp.message_handler(lambda message: message.text == 'Удалить телефон')
async def request_phone_deletion(message: types.Message):
    user_states[message.from_user.id] = 'deleting_phone'
    await message.reply("Введите данные телефона для удаления, например:\n'13 128GB Green'")

@dp.message_handler(lambda message: user_states.get(message.from_user.id) == 'deleting_phone')
async def delete_phone(message: types.Message):
    parts = message.text.strip().split()
    if len(parts) >= 2:
        model = parts[0]
        storage = parts[1]
        await database.delete_telephone(model, storage)
        await message.reply(f"Телефон {model} {storage} удален.")
    else:
        await message.reply("Неправильный формат. Попробуйте еще раз.")
    user_states.pop(message.from_user.id, None)
async def default_handler(message: types.Message):
    await message.reply("Извините, я не понимаю эту команду. Пожалуйста, используйте кнопки меню для взаимодействия с ботом.")

async def on_startup(_):
    await database.create_table()

if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup)