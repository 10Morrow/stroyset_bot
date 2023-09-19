from aiogram import types


def choose_builder():
    inline_keyboard = types.InlineKeyboardMarkup()
    choose_button = types.InlineKeyboardButton("Найти исполнителя", callback_data=f"choose_type_builder")
    inline_keyboard.add(choose_button)

    return inline_keyboard


def skip_price(app_type):
    inline_keyboard = types.InlineKeyboardMarkup()
    skip_price_btn = types.InlineKeyboardButton("Не знаю", callback_data=f"{app_type}_skip_price")
    inline_keyboard.add(skip_price_btn)

    return inline_keyboard


def project_link_and_btn():
    inline_keyboard = types.InlineKeyboardMarkup()
    choose_app_btn = types.InlineKeyboardButton("Выбрать заявку", callback_data="choose_type_app")
    project_link_btn = types.InlineKeyboardButton("Ознакомиться с проектом", url="https://stroyset.pro/")
    inline_keyboard.add(choose_app_btn)
    inline_keyboard.add(project_link_btn)
    return inline_keyboard


def just_project_link():
    inline_keyboard = types.InlineKeyboardMarkup()
    project_link_btn = types.InlineKeyboardButton("Ознакомиться с проектом", url="https://stroyset.pro/")
    inline_keyboard.add(project_link_btn)
    return inline_keyboard


def chose_how_create_application():
    inline_keyboard = types.InlineKeyboardMarkup()
    registrate_cust = types.InlineKeyboardButton("Воспользоваться услугой", callback_data=f"registrate_customer")
    create_app = types.InlineKeyboardButton("Беру ответственность на себя", callback_data=f"create_application_no")

    inline_keyboard.add(registrate_cust)
    inline_keyboard.add(create_app)

    return inline_keyboard


def create_app_like_reg_user(prefix=''):
    inline_keyboard = types.InlineKeyboardMarkup()
    create_app_agree = types.InlineKeyboardButton("Да, продолжить.", callback_data=f"{prefix}create_application_yes")
    create_app_disagree = types.InlineKeyboardButton("Нет, беру ответственность на себя",
                                                     callback_data=f"{prefix}create_application_no")

    inline_keyboard.add(create_app_agree)
    inline_keyboard.add(create_app_disagree)

    return inline_keyboard
