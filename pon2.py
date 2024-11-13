import sqlite3
from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

qw = 'dlodcsod'

bot = Bot(token="6368169284:AAE_8sfGeJHfMguXa7LvRBjejW_ltxmns9k")
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

qw = sqlite3.connect('bron3.db')
cursor = qw.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS restoran (
        id INTEGER PRIMARY KEY,
        name TEXT,
        phone_number INTEGER
    )''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS products_LES (
        id INTEGER PRIMARY KEY,
        name TEXT,
        price INTEGER
    )''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS products_Italy_Kvartal (
        id INTEGER PRIMARY KEY,
        name TEXT,
        price INTEGER
    )''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS time (
        id INTEGER PRIMARY KEY,
        name INTEGER
    )''')

cursor.execute('''
    INSERT OR IGNORE INTO restoran (id, name, phone_number)
    VALUES
        (1, 'LES', 380977614304),
        (2, 'Italy Kvartal', 380965143166)
''')

cursor.executemany('''
    INSERT INTO products_LES (name, price)
    VALUES (?, ?)
''', [
    ('Борщ', 95),
    ('Шашлик', 120),
    ('Кортопля по селянскі', 60),
    ('Кортопля фрі', 55),
    ('Піца Класична', 140),
    ('Паста Карбонара', 160),
    ('Паста Нейро', 180),
    ('Салат Грецький', 85),
    ('Салат Цезарь', 85),
    ('Шарлотка з яблуком', 130),
    ('Торт Напалеон', 150),
    ('Кока Кола', 30),
    ('Фанта', 30),
    ('Пиво', 45),
    ('Біле вино', 90)
])

cursor.executemany('''
    INSERT INTO products_Italy_Kvartal (name, price)
    VALUES (?, ?)
''', [
    ('Зелений борщ', 95),
    ('Шашлик', 120),
    ('Кортопля по селянскі', 60),
    ('Кортопля фрі', 55),
    ('Піца Класична', 140),
    ('Паста Карбонара', 160),
    ('Паста Нейро', 180),
    ('Салат Грецький', 85),
    ('Салат Цезарь', 85),
    ('Тістечко з заварним кремом', 130),
    ('Брауні', 150),
    ('Кока Кола', 30),
    ('Фанта', 30),
    ('Пиво', 45),
    ('Червоне вино', 90)
])
# ------------------------------------------------------------------------------------------------------------------------------------
@dp.message_handler(Command("start"))
async def start(message: types.Message):
    await message.answer(text='Привіт! Я - бот, який бронює, напишіть /bron щоб забронювати або /menu щоб переглянути меню')

@dp.message_handler(commands='menu')
async def check_menu(message: types.Message, state: FSMContext):
    menu_choice = InlineKeyboardMarkup()
    
    cursor.execute('SELECT name FROM restoran')
    restoran = cursor.fetchall()

    for row in restoran:
        restoran_name = row[0]
        button = InlineKeyboardButton(text=restoran_name, callback_data=f'restaurant_{restoran_name}')
        menu_choice.add(button)

    await message.answer(text='Выберите ресторан:', reply_markup=menu_choice)


# ------------------------------------------------------------------------------------------------------------------------------------



@dp.callback_query_handler(lambda query: query.data.startswith('restaurant_'))
async def handle_restaurant_selection(query: types.CallbackQuery):
    restaurant_name = query.data.replace('restaurant_', '')
    product_query = ''

    if restaurant_name == 'Italy_Kvartal':
        product_query = 'SELECT name, price FROM products_Italy_Kvartal'
    elif restaurant_name == 'LES':
        product_query = 'SELECT name, price FROM products_LES'

    products = cursor.execute(product_query).fetchall()
    
    menu_choice = InlineKeyboardMarkup()

    for row in products:
        menu_name = row[0]
        button = InlineKeyboardButton(text=menu_name, callback_data=f'product_{menu_name}')
        menu_choice.add(button)
        
    await query.message.answer(f'Це продукти в ресторані {menu_name}:')


# ------------------------------------------------------------------------------------------------------------------------------------


@dp.message_handler(commands='bron')
async def bron_restoran(message: types.Message):
    bron_choice = InlineKeyboardMarkup()
    
    cursor.execute('''SELECT name FROM restoran''')
    restoran_choice = cursor.fetchall()

    for i in restoran_choice:
        restoran_name = i[0]
        button = InlineKeyboardButton(text=restoran_name, callback_data=f'bron_{restoran_name}')
        bron_choice.add(button)
    
    await message.answer(text="Виберіть ресторан, в якому хочете забронювати місце:", reply_markup=bron_choice)
# ------------------------------------------------------------------------------------------------------------------------------------


@dp.callback_query_handler(lambda query: query.data.startswith('bron_'))
async def handle_bron_restaurant(query: types.CallbackQuery):
    restaurant_name = query.data.replace('bron_', '')
    
    time_choice = InlineKeyboardMarkup()
    
    time_variants = ['9.00', '12.00', '15.00', '18.00', '21.00']
    for time in time_variants:
        button = InlineKeyboardButton(text=time, callback_data=f'booking_{restaurant_name}_{time}')
        time_choice.add(button)
    
    await query.message.answer(text=f'Оберіть час на коли ви хочете забронювати {restaurant_name}:', reply_markup=time_choice)
# ------------------------------------------------------------------------------------------------------------------------------------
@dp.callback_query_handler(lambda query: query.data.startswith('booking_'))
async def handle_booking(query: types.CallbackQuery):
    data_parts = query.data.split('_')
    if len(data_parts) == 3:
        restaurant_name = data_parts[1]
        selected_time = data_parts[2]

        cursor.execute("INSERT INTO time (name) VALUES(?)", (selected_time,))
        qw.commit()
        qw.close()
        
        b = cursor.execute('SELECT name FROM time').fetchall()

        if (selected_time,) in b:
            await query.message.answer('Місце на такий час вже забрано')
        else:
            await query.message.answer('ERROR1')
            
        await query.message.answer(f'Ви забронювали місце в {restaurant_name} на {selected_time}.')
    else:
        await query.message.answer('ERROR2')





# ------------------------------------------------------------------------------------------------------------------------------------

async def set_default_commands(dp, bot):
    await bot.set_my_commands(
        [
            types.BotCommand('start', 'Запустити бота'),
            types.BotCommand('bron', 'Забронювати'),
            types.BotCommand('menu', 'Подивитися меню'),
            types.BotCommand('check', 'Подивитися на коли заброньовані місця')
        ]
    )

async def on_startup(dp):
    await set_default_commands(dp, bot)

async def on_shutdown(dp):
    await bot.close()
    await qw.close()

if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown)
