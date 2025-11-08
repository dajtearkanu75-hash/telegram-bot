
# full_bot.py
import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram import F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from datetime import datetime, timedelta
import json
import os
import re

# Включаем логирование
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')
ADMIN_CHAT_ID = 5001349759
CHANNEL = "https://t.me/JNDstore24"

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# База данных для заказов и корзин
if os.path.exists('orders.json'):
    with open('orders.json', 'r', encoding='utf-8') as f:
        orders_db = json.load(f)
else:
    orders_db = {}

# Корзины пользователей
carts = {}

def save_orders():
    with open('orders.json', 'w', encoding='utf-8') as f:
        json.dump(orders_db, f, ensure_ascii=False, indent=2)

# Функция для правильного извлечения цены
def extract_price(price_str):
    """Извлекает числовое значение цены из строки"""
    # Убираем все пробелы и находим все цифры
    clean_str = price_str.replace(' ', '')
    numbers = re.findall(r'\d+', clean_str)
    
    if numbers:
        # Берем первое найденное число (основную цену)
        return int(numbers[0])
    return 0

# Полный каталог БЕЗ фото
CATALOG = {
    "👟 Обувь": {
        "Balenciaga": [
            {"name": "Balenciaga Runner 7.0 OK batch", "price": "27 000₸", "sizes": "35-46", "code": "order1"},
            {"name": "Balenciaga Runner 7.0 OK batch - 44 000₸", "price": "44 000₸", "sizes": "35-46", "code": "order2"},
            {"name": "Balenciaga Strike boots", "price": "50 000₸", "sizes": "40-45", "code": "order3"},
        ],
        "Nike": [
            {"name": "Nike AF1 Nocta", "price": "20 000-22 000₸", "sizes": "35.5-48.5", "code": "order4"},
            {"name": "Nike Air Force anniversary edition", "price": "19 000₸", "sizes": "36-45", "code": "order5"},
            {"name": "Nike ACG AirZoom Gaiadome Goretex", "price": "25 000₸", "sizes": "36-45", "code": "order6"},
        ],
        "Maison Margiela": [
            {"name": "Maison Margiela Future", "price": "27 000₸", "sizes": "36-46", "code": "order7"},
            {"name": "Maison Margiela replica", "price": "21 000₸", "sizes": "35-46", "code": "order8"},
        ],
        "Другие": [
            {"name": "Off White be right back", "price": "19 000₸", "sizes": "36-45", "code": "order9"},
            {"name": "React X Rejuven8", "price": "7 000₸", "sizes": "40-45", "code": "order10"},
            {"name": "Palm Angels тапочки", "price": "5 500₸", "sizes": "36-45", "code": "order11"},
        ],
    },
    "👜 Аксессуары": {
        "Часы и очки": [
            {"name": "Часы Alabaster", "price": "10 000₸", "sizes": "-", "code": "order12"},
            {"name": "Очки Chrome Hearts", "price": "4 000₸ (6 000₸ с упаковкой)", "sizes": "-", "code": "order13"},
        ],
        "Браслеты и кошельки": [
            {"name": "Браслет Rick Owens", "price": "5 000₸", "sizes": "-", "code": "order14"},
            {"name": "Браслет Maison Martin Margiela", "price": "5 000₸", "sizes": "17.5/20/23 cm", "code": "order15"},
            {"name": "Браслет Ambush", "price": "6 000₸", "sizes": "16/18/20 cm", "code": "order16"},
            {"name": "Браслет alyx прозрачный", "price": "2 500₸", "sizes": "-", "code": "order17"},
            {"name": "Кошелек доллар", "price": "2 000₸", "sizes": "-", "code": "order18"},
        ],
        "Сумки": [
            {"name": "Sprayground backpack", "price": "32 000₸ (Original)", "sizes": "-", "code": "order19"},
            {"name": "Supreme bag", "price": "8 000₸", "sizes": "-", "code": "order20"},
        ]
    },
    "👕 Одежда": {
        "Верхняя одежда": [
            {"name": "Ветровка Polo Ralph Lauren", "price": "16 000₸", "sizes": "S-XL", "code": "order21"},
            {"name": "Nike ACG Therma-Fit ADV Lunar Lake", "price": "17 000₸", "sizes": "M-2XL", "code": "order22"},
            {"name": "Sp5der hoodie", "price": "14 000-15 000₸", "sizes": "S-XL", "code": "order23"},
            {"name": "Supreme x Corteiz hoodie", "price": "16 000₸", "sizes": "S-XL", "code": "order24"},
            {"name": "Trapstar hoodie", "price": "12 000₸", "sizes": "S-XL", "code": "order25"},
            {"name": "Zip Hoodie crop", "price": "16 000₸", "sizes": "S-XL", "code": "order26"},
            {"name": "Zip hoodie suvene", "price": "7 000₸", "sizes": "M-XL", "code": "order27"},
            {"name": "Zip Gallery Dept.", "price": "14 000₸", "sizes": "S-XL", "code": "order28"},
            {"name": "Nike Hyperwarm", "price": "4 000₸", "sizes": "1-SIZE", "code": "order29"},
            {"name": "Gallery Dept long", "price": "10 000₸", "sizes": "S (рост 160-170)", "code": "order30"},
        ],
        "Футболки": [
            {"name": "Футболка Bape", "price": "6 000₸", "sizes": "S-XL", "code": "order31"},
            {"name": "Футболка Kenzo", "price": "6 000₸", "sizes": "S-XL", "code": "order32"},
            {"name": "Футболка Syna", "price": "10 000₸", "sizes": "S-XL", "code": "order33"},
            {"name": "Футболка Denim Tears", "price": "7 000₸", "sizes": "S-XL", "code": "order34"},
            {"name": "Футболка Al Pacino", "price": "7 000₸", "sizes": "S-XL", "code": "order35"},
            {"name": "Футболка Palm Angels", "price": "7 000₸", "sizes": "S-XL", "code": "order36"},
            {"name": "Футболка Supreme", "price": "7 000₸", "sizes": "S-XL", "code": "order37"},
            {"name": "Футболка CDG", "price": "7 000₸", "sizes": "S-XL", "code": "order38"},
            {"name": "Футболка Lanvin Gallery Dept.", "price": "9 000₸", "sizes": "S-XL", "code": "order39"},
        ],
        "Джинсы и штаны": [
            {"name": "Trapstar pants", "price": "12 000₸", "sizes": "S-XL", "code": "order40"},
            {"name": "Trapstar t costume", "price": "24 000₸", "sizes": "S-XL", "code": "order41"},
            {"name": "Pants suvene", "price": "7 500₸", "sizes": "M-XL", "code": "order42"},
            {"name": "Gallery Dept. Pants", "price": "12 500₸", "sizes": "S-XL", "code": "order43"},
            {"name": "Flared jeans", "price": "10 000₸", "sizes": "S-XL", "code": "order44"},
            {"name": "MM6 shorts", "price": "9 000₸", "sizes": "S-XL", "code": "order45"},
            {"name": "Шорты FOG", "price": "5 000₸", "sizes": "M-XL", "code": "order46"},
            {"name": "Shorts EE", "price": "3 000-3 500₸", "sizes": "M-3XL", "code": "order47"},
            {"name": "PSD боксеры", "price": "3 000₸", "sizes": "S-XXL", "code": "order48"},
            {"name": "Palm Angels (костюм)", "price": "20 000₸", "sizes": "S-2XL", "code": "order49"},
            {"name": "Palm Angels (штаны)", "price": "13 000₸", "sizes": "S-2XL", "code": "order50"},
            {"name": "Palm Angels (кофта)", "price": "11 000₸", "sizes": "S-2XL", "code": "order51"},
            {"name": "Джинсы Purple Brand", "price": "16 000₸", "sizes": "28-38", "code": "order52"},
            {"name": "Gallery Dept jeans", "price": "16 000₸", "sizes": "S-XL", "code": "order53"},
            {"name": "White jeans", "price": "10 000₸", "sizes": "S-XL", "code": "order54"},
            {"name": "True Religion jeans", "price": "10 000₸", "sizes": "S-XL", "code": "order55"},
        ],
    },
    "🧢 Головные уборы": {
        "Головные уборы": [
            {"name": "Термо Балаклава Supreme", "price": "6 000₸", "sizes": "1-SIZE", "code": "order56"},
            {"name": "Supreme OTG", "price": "9 000₸", "sizes": "1-SIZE", "code": "order57"},
            {"name": "Браслет Аlyc 1017 9sm", "price": "4 000₸", "sizes": "-", "code": "order58"},
        ]
    }
}

PAYMENT_INFO = {
    "cards": ["4400 4302 4961 9419", "4003 0351 5537 1177"],
    "name": "Jangir"
}

class OrderStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_city = State()
    waiting_for_size = State()
    waiting_for_screenshot = State()

class AdminStates(StatesGroup):
    waiting_tracking = State()
    waiting_delivery_date = State()

def main_menu_kb():
    buttons = [
        [InlineKeyboardButton(text="🛍 Каталог", callback_data="catalog")],
        [InlineKeyboardButton(text="🛒 Корзина", callback_data="cart")],
        [InlineKeyboardButton(text="📦 Мои заказы", callback_data="my_orders")],
        [InlineKeyboardButton(text="ℹ️ Как заказать", callback_data="help")],
        [InlineKeyboardButton(text="📞 Наш канал", url=CHANNEL)]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def categories_kb():
    buttons = []
    for category in CATALOG.keys():
        buttons.append([InlineKeyboardButton(text=category, callback_data=f"category_{category}")])
    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="main_menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def brands_kb(category):
    buttons = []
    for brand in CATALOG[category].keys():
        buttons.append([InlineKeyboardButton(text=brand, callback_data=f"brand_{category}_{brand}")])
    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="catalog")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def products_kb(category, brand, user_id=None):
    buttons = []
    products = CATALOG[category][brand]
    
    for product in products:
        in_cart = False
        if user_id and user_id in carts:
            in_cart = any(item["code"] == product["code"] for item in carts[user_id])
        
        cart_text = " ✅ В корзине" if in_cart else " 🛒"
        buttons.append([InlineKeyboardButton(
            text=f"{product['name']} - {product['price']}{cart_text}", 
            callback_data=f"product_{product['code']}"
        )])
    
    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data=f"category_{category}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def product_detail_kb(product_code, user_id=None):
    buttons = []
    
    # Проверяем есть ли товар в корзине
    in_cart = False
    if user_id and user_id in carts:
        in_cart = any(item["code"] == product_code for item in carts[user_id])
    
    # Кнопка "Купить сейчас" для быстрого заказа
    buttons.append([InlineKeyboardButton(text="🛒 Купить сейчас", callback_data=f"buy_now_{product_code}")])
    
    if in_cart:
        buttons.append([InlineKeyboardButton(text="❌ Удалить из корзины", callback_data=f"remove_{product_code}")])
    else:
        buttons.append([InlineKeyboardButton(text="➕ Добавить в корзину", callback_data=f"add_{product_code}")])
    
    buttons.append([InlineKeyboardButton(text="⬅️ Назад к товарам", callback_data=f"product_{product_code}_back")])
    buttons.append([InlineKeyboardButton(text="🛒 Перейти в корзину", callback_data="cart")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def cart_kb():
    buttons = [
        [InlineKeyboardButton(text="✅ Оформить заказ", callback_data="checkout")],
        [InlineKeyboardButton(text="🗑 Очистить корзину", callback_data="clear_cart")],
        [InlineKeyboardButton(text="⬅️ Продолжить покупки", callback_data="catalog")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def admin_order_kb(order_id):
    buttons = [
        [InlineKeyboardButton(text="✅ Принять заказ", callback_data=f"accept_{order_id}")],
        [InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject_{order_id}")],
        [InlineKeyboardButton(text="🚚 Добавить трекинг", callback_data=f"track_{order_id}")],
        [InlineKeyboardButton(text="📅 Срок доставки", callback_data=f"delivery_{order_id}")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "👋 Добро пожаловать в JND Store!\n"
        "🔥 Оригинальная одежда и обувь от лучших брендов\n\n"
        "Выберите действие:",
        reply_markup=main_menu_kb()
    )

@dp.callback_query(F.data == "main_menu")
async def main_menu(cb: types.CallbackQuery):
    await cb.message.edit_text("Главное меню:", reply_markup=main_menu_kb())
    await cb.answer()

@dp.callback_query(F.data == "catalog")
async def show_catalog(cb: types.CallbackQuery):
    await cb.message.edit_text("🏪 Каталог товаров:", reply_markup=categories_kb())
    await cb.answer()

@dp.callback_query(F.data.startswith("category_"))
async def show_brands(cb: types.CallbackQuery):
    category = cb.data.replace("category_", "")
    await cb.message.edit_text(f"📂 Категория: {category}", reply_markup=brands_kb(category))
    await cb.answer()

@dp.callback_query(F.data.startswith("brand_"))
async def show_products(cb: types.CallbackQuery):
    data = cb.data.replace("brand_", "").split("_")
    category = data[0]
    brand = data[1]
    
    await cb.message.edit_text(
        f"🏷️ Бренд: {brand}\n\n"
        "✅ - товар уже в корзине",
        reply_markup=products_kb(category, brand, cb.from_user.id)
    )
    await cb.answer()

@dp.callback_query(F.data.startswith("product_"))
async def show_product(cb: types.CallbackQuery):
    if cb.data.endswith("_back"):
        product_code = cb.data.replace("product_", "").replace("_back", "")
        for category, brands in CATALOG.items():
            for brand, products in brands.items():
                for product in products:
                    if product["code"] == product_code:
                        await cb.message.edit_text(
                            f"🏷️ Бренд: {brand}\n\n"
                            "✅ - товар уже в корзине",
                            reply_markup=products_kb(category, brand, cb.from_user.id)
                        )
                        await cb.answer()
                        return
    else:
        product_code = cb.data.replace("product_", "")
        for category, brands in CATALOG.items():
            for brand, products in brands.items():
                for product in products:
                    if product["code"] == product_code:
                        # Проверяем есть ли товар в корзине
                        in_cart = False
                        if cb.from_user.id in carts:
                            in_cart = any(item["code"] == product_code for item in carts[cb.from_user.id])
                        
                        cart_status = "✅ В корзине" if in_cart else "🛒 Не в корзине"
                        
                        await cb.message.edit_text(
                            f"🛍 {product['name']}\n"
                            f"💵 Цена: {product['price']}\n"
                            f"📏 Размеры: {product['sizes']}\n"
                            f"🆔 Код: {product['code']}\n"
                            f"📦 Статус: {cart_status}\n\n"
                            f"Выберите действие:",
                            reply_markup=product_detail_kb(product_code, cb.from_user.id)
                        )
                        await cb.answer()
                        return

# Функция быстрого заказа (купить сейчас)
@dp.callback_query(F.data.startswith("buy_now_"))
async def buy_now(cb: types.CallbackQuery, state: FSMContext):
    product_code = cb.data.replace("buy_now_", "")
    
    # Находим товар
    product = None
    for category, brands in CATALOG.items():
        for brand, products in brands.items():
            for p in products:
                if p["code"] == product_code:
                    product = p.copy()
                    break
    
    if product:
        # Сохраняем товар для оформления заказа
        await state.update_data(cart_items=[product])
        await cb.message.answer("📝 Для оформления заказа введите ваше имя:")
        await state.set_state(OrderStates.waiting_for_name)
        await cb.answer(f"🛒 Оформляем заказ: {product['name']}")

@dp.callback_query(F.data.startswith("add_"))
async def add_to_cart(cb: types.CallbackQuery):
    product_code = cb.data.replace("add_", "")
    
    # Находим товар
    product = None
    for category, brands in CATALOG.items():
        for brand, products in brands.items():
            for p in products:
                if p["code"] == product_code:
                    product = p.copy()  # Делаем копию товара
                    break
    
    if product:
        user_id = cb.from_user.id
        if user_id not in carts:
            carts[user_id] = []
        
        # Добавляем товар в корзину
        carts[user_id].append(product)
        
        await cb.answer(f"✅ {product['name']} добавлен в корзину!")
        
        # Обновляем сообщение
        in_cart = True
        cart_status = "✅ В корзине" if in_cart else "🛒 Не в корзине"
        
        await cb.message.edit_text(
            f"🛍 {product['name']}\n"
            f"💵 Цена: {product['price']}\n"
            f"📏 Размеры: {product['sizes']}\n"
            f"🆔 Код: {product['code']}\n"
            f"📦 Статус: {cart_status}\n\n"
            f"Выберите действие:",
            reply_markup=product_detail_kb(product_code, cb.from_user.id)
        )

@dp.callback_query(F.data.startswith("remove_"))
async def remove_from_cart(cb: types.CallbackQuery):
    product_code = cb.data.replace("remove_", "")
    
    user_id = cb.from_user.id
    if user_id in carts:
        # Удаляем товар из корзины
        carts[user_id] = [item for item in carts[user_id] if item["code"] != product_code]
        
        # Находим товар для сообщения
        product_name = "Товар"
        product_price = ""
        product_sizes = ""
        for category, brands in CATALOG.items():
            for brand, products in brands.items():
                for p in products:
                    if p["code"] == product_code:
                        product_name = p["name"]
                        product_price = p["price"]
                        product_sizes = p["sizes"]
                        break
        
        await cb.answer(f"❌ {product_name} удален из корзины")
        
        # Обновляем сообщение
        in_cart = False
        cart_status = "✅ В корзине" if in_cart else "🛒 Не в корзине"
        
        await cb.message.edit_text(
            f"🛍 {product_name}\n"
            f"💵 Цена: {product_price}\n"
            f"📏 Размеры: {product_sizes}\n"
            f"🆔 Код: {product_code}\n"
            f"📦 Статус: {cart_status}\n\n"
            f"Выберите действие:",
            reply_markup=product_detail_kb(product_code, cb.from_user.id)
        )

@dp.callback_query(F.data == "cart")
async def show_cart(cb: types.CallbackQuery):
    user_id = cb.from_user.id
    
    if user_id not in carts or not carts[user_id]:
        await cb.message.edit_text(
            "🛒 Ваша корзина пуста\n\n"
            "Добавьте товары из каталога!",
            reply_markup=main_menu_kb()
        )
        await cb.answer()
        return
    
    # Формируем сообщение с корзиной
    total = 0
    cart_text = "🛒 Ваша корзина:\n\n"
    
    for i, item in enumerate(carts[user_id], 1):
        cart_text += f"{i}. {item['name']}\n"
        cart_text += f"   💵 {item['price']}\n"
        cart_text += f"   📏 {item['sizes']}\n"
        cart_text += f"   🆔 {item['code']}\n\n"
        
        # Используем правильную функцию для извлечения цены
        price_num = extract_price(item['price'])
        total += price_num
    
    cart_text += f"💰 Общая сумма: {total:,}₸".replace(",", " ")
    
    await cb.message.edit_text(cart_text, reply_markup=cart_kb())
    await cb.answer()

@dp.callback_query(F.data == "clear_cart")
async def clear_cart(cb: types.CallbackQuery):
    user_id = cb.from_user.id
    if user_id in carts:
        carts[user_id] = []
    
    await cb.message.edit_text(
        "🗑 Корзина очищена!",
        reply_markup=main_menu_kb()
    )
    await cb.answer("Корзина очищена!")

@dp.callback_query(F.data == "checkout")
async def start_checkout(cb: types.CallbackQuery, state: FSMContext):
    user_id = cb.from_user.id
    
    if user_id not in carts or not carts[user_id]:
        await cb.answer("Корзина пуста!")
        return
    
    await state.update_data(cart_items=carts[user_id])
    await cb.message.answer("📝 Для оформления заказа введите ваше имя:")
    await state.set_state(OrderStates.waiting_for_name)
    await cb.answer()

@dp.message(OrderStates.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(customer_name=message.text)
    await message.answer("🏙️ Введите ваш город:")
    await state.set_state(OrderStates.waiting_for_city)

@dp.message(OrderStates.waiting_for_city)
async def process_city(message: types.Message, state: FSMContext):
    await state.update_data(city=message.text)
    await message.answer("📏 Введите нужные размеры или комментарий к заказу:")
    await state.set_state(OrderStates.waiting_for_size)

@dp.message(OrderStates.waiting_for_size)
async def process_size(message: types.Message, state: FSMContext):
    await state.update_data(size_comment=message.text)
    data = await state.get_data()
    
    # Формируем список товаров
    cart_items = data["cart_items"]
    products_text = "\n".join([f"• {item['name']} - {item['price']} ({item['sizes']})" for item in cart_items])
    
    # Подсчитываем общую сумму правильно
    total = sum(extract_price(item['price']) for item in cart_items)
    
    await message.answer(
        f"📦 Ваш заказ:\n{products_text}\n\n"
        f"💰 Общая сумма: {total:,}₸\n\n".replace(",", " ") +
        "📸 Теперь отправьте скриншот или фото квитанции об оплате:\n\n"
        "💳 Реквизиты для оплаты:\n" + 
        "\n".join([f"• {card}" for card in PAYMENT_INFO['cards']]) +
        f"\n👤 Получатель: {PAYMENT_INFO['name']}"
    )
    await state.set_state(OrderStates.waiting_for_screenshot)

@dp.message(OrderStates.waiting_for_screenshot, F.photo | F.document)
async def process_screenshot(message: types.Message, state: FSMContext):
    data = await state.get_data()
    cart_items = data["cart_items"]
    
    # Создаем ID заказа
    order_id = f"order_{int(datetime.now().timestamp())}"
    
    # Подсчитываем общую сумму правильно
    total = sum(extract_price(item['price']) for item in cart_items)
    
    orders_db[order_id] = {
        "products": cart_items,
        "customer_name": data["customer_name"],
        "city": data["city"],
        "size_comment": data["size_comment"],
        "user_id": message.from_user.id,
        "username": message.from_user.username,
        "status": "pending",
        "total_amount": total,
        "created_at": datetime.now().isoformat()
    }
    save_orders()
    
    # Формируем текст заказа
    products_text = "\n".join([f"• {item['name']} - {item['price']} ({item['sizes']})" for item in cart_items])
    
    # Отправляем заказ админу с фото
    order_text = (
        "🆕 НОВЫЙ ЗАКАЗ!\n\n"
        f"📦 Товары:\n{products_text}\n\n"
        f"💰 Общая сумма: {total:,}₸\n\n".replace(",", " ") +
        f"👤 Имя: {data['customer_name']}\n"
        f"🏙️ Город: {data['city']}\n"
        f"📏 Размер/Комментарий: {data['size_comment']}\n"
        f"📱 Username: @{message.from_user.username or 'не указан'}\n"
        f"🆔 User ID: {message.from_user.id}\n"
        f"🆔 Order ID: {order_id}"
    )
    
    try:
        if message.photo:
            await bot.send_photo(
                ADMIN_CHAT_ID, 
                message.photo[-1].file_id,
                caption=order_text,
                reply_markup=admin_order_kb(order_id)
            )
        else:
            await bot.send_document(
                ADMIN_CHAT_ID,
                message.document.file_id,
                caption=order_text,
                reply_markup=admin_order_kb(order_id)
            )
        logger.info(f"Order {order_id} sent to admin")
    except Exception as e:
        logger.error(f"Failed to send order: {e}")
        await message.answer("❌ Ошибка при отправке заказа. Свяжитесь с администратором.")
        await state.clear()
        return
    
    # Очищаем корзину пользователя (если заказ из корзины)
    user_id = message.from_user.id
    if user_id in carts and len(cart_items) == len(carts[user_id]):
        carts[user_id] = []
    
    # Отправляем подтверждение клиенту
    await message.answer(
        f"✅ Заказ оформлен, {data['customer_name']}!\n\n"
        f"🆔 Номер заказа: {order_id}\n"
        f"💰 Сумма: {total:,}₸\n".replace(",", " ") +
        "📞 Ваш заказ передан менеджеру. Ожидайте подтверждения в течение 24 часов.\n"
        "💬 Для связи: @JND_esil",
        reply_markup=main_menu_kb()
    )
    
    await state.clear()

# Функция "Как заказать"
@dp.callback_query(F.data == "help")
async def show_help(cb: types.CallbackQuery):
    help_text = (
        "ℹ️ КАК ЗАКАЗАТЬ:\n\n"
        "1. 🛍 Выберите товар в каталоге\n"
        "2. 🛒 Нажмите 'Купить сейчас' для быстрого заказа или 'Добавить в корзину'\n"
        "3. 💳 Оплатите заказ по реквизитам:\n"
        f"   • {PAYMENT_INFO['cards'][0]}\n"
        f"   • {PAYMENT_INFO['cards'][1]}\n"
        f"   👤 {PAYMENT_INFO['name']}\n"
        "4. 📸 Отправьте скриншот оплаты\n"
        "5. ✅ Получите подтверждение заказа\n"
        "6. 📦 Ожидайте доставки\n\n"
        "🚚 Доставка по всему Казахстану!\n"
        "⏱ Срок доставки: 14-17 дней\n"
        "💬 Поддержка: @JND_esil"
    )
    await cb.message.edit_text(help_text, reply_markup=main_menu_kb())
    await cb.answer()

# Функция "Мои заказы"
@dp.callback_query(F.data == "my_orders")
async def show_my_orders(cb: types.CallbackQuery):
    user_id = cb.from_user.id
    user_orders = {k: v for k, v in orders_db.items() if v.get("user_id") == user_id}
    
    if not user_orders:
        await cb.message.edit_text(
            "📦 У вас пока нет заказов.\n\n"
            "🛍 Перейдите в каталог, чтобы сделать первый заказ!",
            reply_markup=main_menu_kb()
        )
        await cb.answer()
        return
    
    orders_text = "📦 ВАШИ ЗАКАЗЫ:\n\n"
    for order_id, order in user_orders.items():
        status_emoji = {
            "pending": "⏳",
            "accepted": "✅", 
            "rejected": "❌",
            "shipped": "🚚",
            "delivered": "📦"
        }.get(order.get("status", "pending"), "⏳")
        
        total_amount = order.get('total_amount', 0)
        
        orders_text += f"{status_emoji} Заказ {order_id}\n"
        orders_text += f"💰 Сумма: {total_amount:,}₸\n".replace(",", " ")
        orders_text += f"📅 {order.get('created_at', '')[:10]}\n"
        orders_text += f"📦 Статус: {order.get('status', 'pending')}\n"
        
        if order.get('tracking_number'):
            orders_text += f"🚚 Трек: {order['tracking_number']}\n"
        if order.get('delivery_date'):
            orders_text += f"📅 Доставка: {order['delivery_date']}\n"
            
        orders_text += "\n"
    
    await cb.message.edit_text(orders_text, reply_markup=main_menu_kb())
    await cb.answer()

# Админские функции
@dp.callback_query(F.data.startswith("accept_"))
async def accept_order(cb: types.CallbackQuery):
    order_id = cb.data.replace("accept_", "")
    
    if order_id in orders_db:
        orders_db[order_id]["status"] = "accepted"
        orders_db[order_id]["accepted_at"] = datetime.now().isoformat()
        save_orders()
        
        # Уведомляем пользователя
        user_id = orders_db[order_id]["user_id"]
        try:
            await bot.send_message(
                user_id,
                f"✅ Ваш заказ {order_id} принят!\n\n"
                "📦 Заказ передан на сборку и отправку.\n"
                "⏱ Ожидайте уведомление об отправке в течение 1-2 дней."
            )
        except Exception as e:
            logger.error(f"Failed to notify user: {e}")
        
        await cb.message.edit_reply_markup(reply_markup=None)
        await cb.answer(f"✅ Заказ {order_id} принят!")
    else:
        await cb.answer("❌ Заказ не найден")

@dp.callback_query(F.data.startswith("reject_"))
async def reject_order(cb: types.CallbackQuery):
    order_id = cb.data.replace("reject_", "")
    
    if order_id in orders_db:
        orders_db[order_id]["status"] = "rejected"
        orders_db[order_id]["rejected_at"] = datetime.now().isoformat()
        save_orders()
        
        # Уведомляем пользователя
        user_id = orders_db[order_id]["user_id"]
        try:
            await bot.send_message(
                user_id,
                f"❌ Ваш заказ {order_id} отклонен.\n\n"
                "💬 Для выяснения причин свяжитесь с менеджером: @JND_esil"
            )
        except Exception as e:
            logger.error(f"Failed to notify user: {e}")
        
        await cb.message.edit_reply_markup(reply_markup=None)
        await cb.answer(f"❌ Заказ {order_id} отклонен")
    else:
        await cb.answer("❌ Заказ не найден")

@dp.callback_query(F.data.startswith("track_"))
async def add_tracking(cb: types.CallbackQuery, state: FSMContext):
    order_id = cb.data.replace("track_", "")
    
    if order_id in orders_db:
        await state.update_data(order_id=order_id)
        await cb.message.answer("📮 Введите трек-номер для отслеживания:")
        await state.set_state(AdminStates.waiting_tracking)
        await cb.answer()
    else:
        await cb.answer("❌ Заказ не найден")

@dp.message(AdminStates.waiting_tracking)
async def process_tracking(message: types.Message, state: FSMContext):
    data = await state.get_data()
    order_id = data["order_id"]
    
    if order_id in orders_db:
        orders_db[order_id]["tracking_number"] = message.text
        orders_db[order_id]["status"] = "shipped"
        orders_db[order_id]["shipped_at"] = datetime.now().isoformat()
        save_orders()
        
        # Уведомляем пользователя
        user_id = orders_db[order_id]["user_id"]
        try:
            await bot.send_message(
                user_id,
                f"🚚 Ваш заказ {order_id} отправлен!\n\n"
                f"📮 Трек-номер для отслеживания: {message.text}\n"
                "📦 Отслеживайте посылку в приложении почты."
            )
        except Exception as e:
            logger.error(f"Failed to notify user: {e}")
        
        await message.answer(f"✅ Трек-номер добавлен к заказу {order_id}")
        await state.clear()
    else:
        await message.answer("❌ Заказ не найден")
        await state.clear()

@dp.callback_query(F.data.startswith("delivery_"))
async def set_delivery_date(cb: types.CallbackQuery, state: FSMContext):
    order_id = cb.data.replace("delivery_", "")
    
    if order_id in orders_db:
        await state.update_data(order_id=order_id)
        await cb.message.answer("📅 Введите срок доставки (например: '3-5 дней' или '15.12.2024'):")
        await state.set_state(AdminStates.waiting_delivery_date)
        await cb.answer()
    else:
        await cb.answer("❌ Заказ не найден")

@dp.message(AdminStates.waiting_delivery_date)
async def process_delivery_date(message: types.Message, state: FSMContext):
    data = await state.get_data()
    order_id = data["order_id"]
    
    if order_id in orders_db:
        orders_db[order_id]["delivery_date"] = message.text
        save_orders()
        
        # Уведомляем пользователя
        user_id = orders_db[order_id]["user_id"]
        try:
            await bot.send_message(
                user_id,
                f"📅 По вашему заказу {order_id} установлен срок доставки:\n\n"
                f"⏱ {message.text}"
            )
        except Exception as e:
            logger.error(f"Failed to notify user: {e}")
        
        await message.answer(f"✅ Срок доставки установлен для заказа {order_id}")
        await state.clear()
    else:
        await message.answer("❌ Заказ не найден")
        await state.clear()

async def main():
    print("=== JND Store Bot ===")
    
    try:
        me = await bot.get_me()
        print(f"✅ Бот: @{me.username}")
        print("✅ База заказов загружена")
        print("✅ Система корзины активирована")
        print("✅ Бот запущен и готов к работе!")
        print("✅ Отправьте /start в Telegram")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return
    
    try:
        await dp.start_polling(bot)
    except Exception as e:
        print(f"❌ Бот упал: {e}")

if __name__ == "__main__":
    asyncio.run(main())