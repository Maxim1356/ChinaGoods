import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
import json
import requests
import re


a = int()
b = str()
c = int()
url = ("https://iss.moex.com/iss/engines/currency/markets/selt/securities.jsonp?"
       "iss.only=securities,marketdata&"
       "securities=CETS:CNYRUB_TOM&"
       "lang=ru&iss.meta=off&iss.json=extended&callback=angular.callbacks._gk")
data = requests.get(url)
text = data.text[22:len(data.text) - 1:]
text = re.sub(r'\n', "", text)
json_string = json.loads(text)
for ss in json_string[1]['securities']:
    print(f"Курс валюты {ss['SECNAME'].split(' - ')[1]}: {ss['PREVWAPRICE']} {ss['CURRENCYID']}")
dp = Dispatcher()

@dp.message(Command('start'))
@dp.message(F.text == "<-----")
async def start_command(message: types.Message) -> None:
    kb = [[types.KeyboardButton(text="Актуальный курс"), types.KeyboardButton(text="О нас")],
          [types.KeyboardButton(text="Сроки доставки")], [types.KeyboardButton(text="Расчёт стоимости товара")]]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

    await message.answer('Приветствуем в нашем магазине!', reply_markup=keyboard)

@dp.message(F.text == "Расчёт стоимости товара")
async def about_you_handler(message: types.Message) -> None:
    kb = [[types.KeyboardButton(text="Верхняя одежда"), types.KeyboardButton(text="Нижняя одежда"),
           types.KeyboardButton(text="Обувь")],
          [types.KeyboardButton(text="Бижутерия"), types.KeyboardButton(text="Головные уборы"),
           types.KeyboardButton(text="Акссесуары")], [types.KeyboardButton(text="<-----")]]
    keyboard_2 = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer("Выберите категорию товара", reply_markup=keyboard_2, )

@dp.message(F.text == 'Верхняя одежда')
@dp.message(F.text == 'Нижняя одежда')
@dp.message(F.text == 'Аксессуары')
@dp.message(F.text == 'Головные уборы')
@dp.message(F.text == 'Бижутерия')
@dp.message(F.text == 'Обувь')
async def price_handler_2(message: types.KeyboardButton, bot: Bot) -> None:
    kb = [[types.KeyboardButton(
        text='1) Железнодорожные перевозки. Время в пути — от 15 до 30 дней. Маршруты: через Казахстан или Монголию. Автомобильные перевозки.')],
        [types.KeyboardButton(
            text='2) Среднее время доставки — 10–14 дней. Популярные маршруты: переходы в Забайкальске и Благовещенске. Морские перевозки. Доставка…')],
        [types.KeyboardButton(text='3) Авиаперевозки. Среднее время в пути — 2–4 дня')],
        [types.KeyboardButton(text='<-----')]]
    keyboard_22 = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer('qwe', reply_markup=keyboard_22)

@dp.message(
    F.text == '1) Железнодорожные перевозки. Время в пути — от 15 до 30 дней. Маршруты: через Казахстан или Монголию. Автомобильные перевозки.')
@dp.message(
    F.text == '2) Среднее время доставки — 10–14 дней. Популярные маршруты: переходы в Забайкальске и Благовещенске. Морские перевозки. Доставка…')
@dp.message(F.text == '3) Авиаперевозки. Среднее время в пути — 2–4 дня')
async def price_handler_2(message: types.KeyboardButton, bot: Bot) -> None:
    global b
    if message.text == '1) Железнодорожные перевозки. Время в пути — от 15 до 30 дней. Маршруты: через Казахстан или Монголию. Автомобильные перевозки.':
        b = f"500 *+ 1.05 * "
    if message.text == '2) Среднее время доставки — 10–14 дней. Популярные маршруты: переходы в Забайкальске и Благовещенске. Морские перевозки. Доставка до Владивостока занимает около 30 дней. Порты отправления: Шанхай, Нинбо.':
        b = f"200 *+ 1.02 * "
    if message.text == '3) Авиаперевозки. Среднее время в пути — 2–4 дня':
        b = f"100 *+ 1.01 * "
    await message.answer('Укажите цену в юанях и вес товара через пробел')

@dp.message(F.text == 'Сроки доставки')
async def name_handler(message: types.Message, bot: Bot) -> None:
    await message.answer(
        '1) Железнодорожные перевозки. Время в пути — от 15 до 30 дней. Маршруты: через Казахстан или Монголию. Автомобильные перевозки.\n'
        '2) Среднее время доставки — 10–14 дней. Популярные маршруты: переходы в Забайкальске и Благовещенске. Морские перевозки. Доставка до Владивостока занимает около 30 дней. Порты отправления: Шанхай, Нинбо.\n'
        '3) Авиаперевозки. Среднее время в пути — 2–4 дня')

@dp.message(F.text == 'О нас')
async def portfolio_handler(message: types.Message) -> None:
    await message.answer(
        'Мы команда, целью которой является интгерация вещей из Китая в Россию, в связи с нынешнеми событиями, а именно уходом глобальных брендов с российского рынка')

@dp.message(F.text == 'Актуальный курс')
async def portfolio_handler(message: types.Message) -> None:
    await message.answer("Актуальный курс: " + str(ss['PREVWAPRICE']))

@dp.message(F.text == 'Верхняя одежда')
@dp.message(F.text == 'Нижняя одежда')
@dp.message(F.text == 'Аксессуары')
@dp.message(F.text == 'Головные уборы')
@dp.message(F.text == 'Бижутерия')
@dp.message(F.text == 'Обувь')
async def price_calc(message: types.Message) -> None:
    global a
    if message.text == "Верхняя одежда":
        a = 1
    if message.text == "Нижняя одежда":
        a = 1.2
    if message.text == "Аксессуары":
        a = 1.5
    if message.text == "Головные уборы":
        a = 1.8
    if message.text == "Бижутерия":
        a = 1.9
    if message.text == "Обувь":
        a = 2

@dp.message(F.text)
async def name_handler(message: types.Message) -> None:
    global a, b
    c = int(message.text.split()[1])
    print(message.text)
    ync = round(float(ss['PREVWAPRICE'])) + 2
    await message.answer("Цена заказываемого товара: " + str(
        eval(str(b[:5]) + str(c) + b[5:] + message.text.split()[0] + "*" + str(ync))))

async def main() -> None:
    token = "7675909653:AAGFHoWEjk7Hq94g8ZryoSUewREo3WJEyP8"
    bot = Bot(token)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
