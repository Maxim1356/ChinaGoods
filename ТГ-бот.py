import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
import json
import requests
import re

url = ("https://iss.moex.com/iss/engines/currency/markets/selt/securities.jsonp?"
       "iss.only=securities,marketdata&"
       "securities=CETS:CNYRUB_TOM&"
       "lang=ru&iss.meta=off&iss.json=extended&callback=angular.callbacks._gk")
data = requests.get(url)

# Обрежем лишнее (вызов функции и переводы строк)
text = data.text[22:len(data.text)-1:]
text = re.sub(r'\n', "", text)
json_string = json.loads(text)
for ss in json_string[1]['securities']:
    print(f"Курс валюты {ss['SECNAME'].split(' - ')[1]}: {ss['PREVWAPRICE']} {ss['CURRENCYID']}")
    print()
dp = Dispatcher()


@dp.message(Command('start'))
async def start_command(message: types.Message) -> None:
    kb = [
        [
            types.KeyboardButton(text="Ответы на все вопросы"),
            types.KeyboardButton(text="Сроки доставки")
        ],

        [
            types.KeyboardButton(text="Актуальный курс"),
            types.KeyboardButton(text="О нас")
        ],
        [
            types.KeyboardButton(text="Расчёт стоимости товара"),
            types.KeyboardButton(text="Товары")
        ]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer('Приветствуем в нашем магазине!', reply_markup=keyboard)


@dp.message(F.text == 'Ответы на все вопросы')
async def about_me_handler(message: types.Message) -> None:
    await asyncio.sleep(1.5)
    await message.answer('1. Относитосительно низкий курс закупки.\n2. Доставляем по всей России')


@dp.message(F.text == 'Сроки доставки')
async def name_handler(message: types.Message, bot: Bot) -> None:
    await asyncio.sleep(1.5)
    await message.answer('1) Железнодорожные перевозки. Время в пути — от 15 до 30 дней. Маршруты: через Казахстан или Монголию. Автомобильные перевозки.\n'
                         '2) Среднее время доставки — 10–14 дней. Популярные маршруты: переходы в Забайкальске и Благовещенске. Морские перевозки. Доставка до Владивостока занимает около 30 дней. Порты отправления: Шанхай, Нинбо.\n'
                         '3) Авиаперевозки. Среднее время в пути — 2–4 дня')


@dp.message(F.text == 'О нас')
async def portfolio_handler(message: types.Message) -> None:
    await asyncio.sleep(1.5)
    await message.answer('Мы команда, целью которой является интгерация вещей из Китая в Россию, в связи с нынешнеми событиями, а именно уходом глобальных брендов с российского рынка')


@dp.message(F.text == 'Актуальный курс')
async def about_you_handler(message: types.Message) -> None:
    await asyncio.sleep(1.5)
    await message.answer("Актульный курс юаня: " + str(float(ss['PREVWAPRICE']) + 2))


@dp.message(F.text == 'Расчёт стоимости товара')
async def about_you_handler(message: types.Message) -> None:
    await message.answer("Напишите цену товара в юанях, наш бот рассчитает его цену в рублях")
    a = message.send_copy(chat_id=message.chat.id)
    if a:
        print(1)
    else:
        print(2)
    print(a)

@dp.message(F.text == 'Напишите цену товара в юанях, наш бот рассчитает его цену в рублях')
async def about_you_handler(message: types.Message) -> None:
    await message.answer("123")
    a = message.send_copy(chat_id=message.chat.id)


@dp.message(F.text == 'Товары')
async def about_you_handler(message: types.Message) -> None:
    kb = [
        [
            types.KeyboardButton(text="Тип 1"),
            types.KeyboardButton(text="Тип 2"),
            types.KeyboardButton(text="Тип 3")
        ],
        [
            types.KeyboardButton(text="Тип 4"),
            types.KeyboardButton(text="Тип 5"),
            types.KeyboardButton(text="Тип 6")
        ]
    ]
    product_types_keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer("Выберите категорию товара", reply_markup=product_types_keyboard)
    a = message.send_copy(chat_id=message.chat.id)


async def main() -> None:
    await asyncio.sleep(1.5)
    token = "7675909653:AAGFHoWEjk7Hq94g8ZryoSUewREo3WJEyP8"
    bot = Bot(token)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())