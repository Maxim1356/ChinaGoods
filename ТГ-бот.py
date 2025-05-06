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
