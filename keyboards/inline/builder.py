from aiogram import types


# инлайн (в чате под сообщением) клавиатура для старта поиска клиентов
def choose_app():
    inline_keyboard = types.InlineKeyboardMarkup()
    choose_button = types.InlineKeyboardButton("Найти клиентов", callback_data=f"choose_type_app")
    inline_keyboard.add(choose_button)

    return inline_keyboard


# инлайн (в чате под сообщением) клавиатура для старта выбора категорий для подписки
def sub_to_categories_start():
    inline_keyboard = types.InlineKeyboardMarkup()
    choose_button = types.InlineKeyboardButton("Выбрать категории для подписки",
                                               callback_data=f"sub_categories")
    inline_keyboard.add(choose_button)

    return inline_keyboard
