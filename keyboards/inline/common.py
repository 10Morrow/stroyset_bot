from aiogram import types


def registration(user_type):
    button = types.InlineKeyboardButton("Зарегистрироваться", callback_data=f"registrate_{user_type}")
    inline_keyboard = types.InlineKeyboardMarkup().add(button)
    return inline_keyboard


def reg_legal_status():
    inline_keyboard = types.InlineKeyboardMarkup(row_width=3)
    buttons = [types.InlineKeyboardButton("ИП", callback_data=f"leg_status_ip"),
            types.InlineKeyboardButton("Юр. Лицо", callback_data=f"leg_status_yur"),
            types.InlineKeyboardButton("Физ. Лицо", callback_data=f"leg_status_fiz")]
    inline_keyboard.row(*buttons)
    return inline_keyboard


# клавиатура устанавливающая кнопки с ценапи покупки
def buy_keyboard(number, app_type):
    inline_keyboard = types.InlineKeyboardMarkup()
    if app_type:
        cost = 30
    else:
        cost = 15
    pay_for = types.InlineKeyboardButton(f"Купить за {cost}", callback_data=f"pay_for_{number}")
    inline_keyboard.add(pay_for)
    return inline_keyboard


def sub_more_or_no(app_type):
    inline_keyboard = types.InlineKeyboardMarkup()
    sub_more_btn = types.InlineKeyboardButton(f"Добавить категорию", callback_data=f"{app_type}_sub_more")
    stop_sub_btn = types.InlineKeyboardButton(f"Закончить", callback_data=f"{app_type}_sub_more_no")
    inline_keyboard.add(sub_more_btn)
    inline_keyboard.add(stop_sub_btn)
    return inline_keyboard


async def pay_for_and_check(pay_url, invoice_id):
    inline_keyboard = types.InlineKeyboardMarkup()
    pay_link = types.InlineKeyboardButton(f"Ссылка на оплату", url=pay_url)
    inline_keyboard.add(pay_link)
    cancel_payment = types.InlineKeyboardButton(f"Отменить", callback_data=f"cancel_pay_for_{invoice_id}")
    inline_keyboard.add(cancel_payment)

    return inline_keyboard


# генерируем клавиатуру прокручивающуюся для категорий
def generate_category_keyboard(categories, prefix, page=0):
    can_go_next = True
    can_go_back = False
    buttons_per_page = 5
    categories_list = [list(region.keys())[0] for region in categories]
    if 5 * page + 5 > len(categories):
        buttons_per_page = len(categories) % 5
        can_go_next = False
    if page > 0:
        can_go_back = True
    buttons = []
    for i in range(buttons_per_page):
        if buttons_per_page == 5:
            button_text = f'{categories_list[page * buttons_per_page + i]}'
            buttons.append(types.InlineKeyboardButton(text=button_text,
                                                      callback_data=f'{prefix}_button_{page * buttons_per_page + i}'))
        else:
            button_text = f'{categories_list[page * 5 + i]}'
            buttons.append(types.InlineKeyboardButton(text=button_text,
                                                      callback_data=f'{prefix}_button_{page * 5 + i}'))

    if can_go_next:
        buttons.append(types.InlineKeyboardButton(text="Ещё категории...", callback_data=f'{prefix}_next_page_{page + 1}'))
    if can_go_back:
        buttons.append(types.InlineKeyboardButton(text="Назад...", callback_data=f'{prefix}_next_page_{page - 1}'))

    return types.InlineKeyboardMarkup(row_width=1).add(*buttons)


# генерируем клавиатуру прокручивающуюся для районов
def choose_federal_district_keyboard(districts, prefix, page=0):
    can_go_next = True
    can_go_back = False
    buttons_per_page = 5
    if 5 * page + 5 > len(districts):
        buttons_per_page = len(districts) % 5
        can_go_next = False
    if page > 0:
        can_go_back = True
    buttons = []
    for i in range(buttons_per_page):
        if buttons_per_page == 5:
            button_text = f'{districts[page * buttons_per_page + i]}'
            buttons.append(types.InlineKeyboardButton(text=button_text,
                                                      callback_data=f'{prefix}_district_button_{page * buttons_per_page + i}'))
        else:
            button_text = f'{districts[page * 5 + i]}'
            buttons.append(types.InlineKeyboardButton(text=button_text,
                                                      callback_data=f'{prefix}_district_button_{page * 5 + i}'))
    if can_go_next:
        buttons.append(types.InlineKeyboardButton(text="Ещё округа...", callback_data=f'{prefix}_next_district_page_{page + 1}'))
    if can_go_back:
        buttons.append(types.InlineKeyboardButton(text="Назад...", callback_data=f'{prefix}_next_district_page_{page - 1}'))

    return types.InlineKeyboardMarkup(row_width=1).add(*buttons)


# генерируем клавиатуру прокручивающуюся для регионов
def chose_region_keyboard(regions, prefix, page=0):
    can_go_next = True
    can_go_back = False
    buttons_per_page = 5
    if 5 * page + 5 > len(regions):
        buttons_per_page = len(regions) % 5
        can_go_next = False
    if page > 0:
        can_go_back = True
    buttons = []
    for i in range(buttons_per_page):
        if buttons_per_page == 5:
            button_text = f'{regions[page * buttons_per_page + i][0]}'
            buttons.append(types.InlineKeyboardButton(text=button_text,
                                                      callback_data=f'{prefix}_region_button_{page * buttons_per_page + i}'))
        else:
            button_text = f'{regions[page * 5 + i][0]}'
            buttons.append(types.InlineKeyboardButton(text=button_text,
                                                      callback_data=f'{prefix}_region_button_{page * 5 + i}'))
    if can_go_next:
        buttons.append(types.InlineKeyboardButton(text="Ещё регионы...", callback_data=f'{prefix}_next_region_page_{page + 1}'))
    if can_go_back:
        buttons.append(types.InlineKeyboardButton(text="Назад...", callback_data=f'{prefix}_next_region_page_{page - 1}'))

    return types.InlineKeyboardMarkup(row_width=1).add(*buttons)


# генерируем клавиатуру прокручивающуюся для городов
def chose_city_keyboard(cities, prefix, page=0):
    can_go_next = True
    can_go_back = False
    buttons_per_page = 5
    if 5 * page + 5 > len(cities):
        buttons_per_page = len(cities) % 5
        can_go_next = False
    if page > 0:
        can_go_back = True
    buttons = []
    for i in range(buttons_per_page):
        if buttons_per_page == 5:
            button_text = f'{cities[page * buttons_per_page + i][0]}'
            buttons.append(types.InlineKeyboardButton(text=button_text,
                                                      callback_data=f'{prefix}_city_button_{page * buttons_per_page + i}'))
        else:
            button_text = f'{cities[page * 5 + i][0]}'
            buttons.append(types.InlineKeyboardButton(text=button_text,
                                                      callback_data=f'{prefix}_city_button_{page * 5 + i}'))
    if can_go_next:
        buttons.append(types.InlineKeyboardButton(text="Ещё города...",
                                                  callback_data=f'{prefix}_next_city_page_{page + 1}'))
    if can_go_back:
        buttons.append(types.InlineKeyboardButton(text="Назад...",
                                                  callback_data=f'{prefix}_next_city_page_{page - 1}'))

    return types.InlineKeyboardMarkup(row_width=1).add(*buttons)


def is_required(prefix):
    inline_keyboard = types.InlineKeyboardMarkup()
    required = types.InlineKeyboardButton("Загрузить", callback_data=f"{prefix}_required_photo_true")
    not_required = types.InlineKeyboardButton("Не требуется", callback_data=f"{prefix}_required_photo_false")

    inline_keyboard.add(required)
    inline_keyboard.add(not_required)

    return inline_keyboard


def skip_description():
    inline_keyboard = types.InlineKeyboardMarkup()
    skip = types.InlineKeyboardButton("Пропустить", callback_data=f"description_skip")
    inline_keyboard.add(skip)

    return inline_keyboard


def skip_email(prefix=''):
    inline_keyboard = types.InlineKeyboardMarkup()
    skip = types.InlineKeyboardButton("Пропустить", callback_data=f"{prefix}email_skip")
    inline_keyboard.add(skip)

    return inline_keyboard


def more_docs(prefix):
    inline_keyboard = types.InlineKeyboardMarkup()
    need_more_docs = types.InlineKeyboardButton("Загрузить", callback_data=f"{prefix}_more_docs_yes")
    stop = types.InlineKeyboardButton("Завершить", callback_data=f"{prefix}_more_docs_no")

    inline_keyboard.add(need_more_docs)
    inline_keyboard.add(stop)

    return inline_keyboard
