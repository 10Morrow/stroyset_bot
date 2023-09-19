from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# клавиатура выбора будущего статуса пользователя
choose_user_type = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Я заказчик")],
        [KeyboardButton(text="Я строитель")],
    ],
    resize_keyboard=True
)


# клавиатура доступных действий заказчику
customer_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Разместить заявку")],
        [KeyboardButton(text="Выбрать исполнителя")],
        [KeyboardButton(text="Сменить свой статус")]
    ],
    resize_keyboard=True
)


# клавиатура доступных действий строителю
builder_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Купить / Выбрать заявку")],
        [KeyboardButton(text="Подписаться на рассылку")],
        [KeyboardButton(text="Сменить свой статус")]
    ],
    resize_keyboard=True
)


# клавиатура для отправки своего текущего номера телефона
get_phone_number = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Отправить текущий номер телефона", request_contact=True)]
    ],
    resize_keyboard=True
)