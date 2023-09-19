# хендлеры отвечают за регистрацию объявления заказчиком
import asyncio
import aiogram
from aiogram import types
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import Dispatcher
import logging

from database.db_commands import DataBase
from forms.validation import validate_mobile_number, validate_email
from keyboards.default.start import get_phone_number
from keyboards.inline.common import generate_category_keyboard, chose_region_keyboard, \
    chose_city_keyboard, is_required, more_docs, skip_email, choose_federal_district_keyboard
from keyboards.inline.customer import skip_price, just_project_link
from api.api_functions import get_categories_data, get_federal_districts, get_regions_by_district, \
    get_cities_by_region, create_user, create_ad

from loader import bot

db = DataBase()

logger = logging.getLogger('app.forms.register_application')


class ApplicationForm(StatesGroup):
    FIO = State()
    PHONE = State()
    EMAIL = State()

    TITLE = State()
    DESCRIPTION = State()
    PRICE = State()
    PHOTO = State()


async def start_app_form(c: types.CallbackQuery, state):
    await bot.edit_message_reply_markup(chat_id=c.message.chat.id,
                                        message_id=c.message.message_id)
    await c.message.edit_text(f"Благодарим за желание разместить заявку в бирже строителей.\n"
                              f"Следуйте инструкциям ниже:")
    async with state.proxy() as data:
        data['registered'] = c.data
    await c.message.answer("Введите ваше имя и фамилию:")
    await ApplicationForm.FIO.set()


async def get_fio(message: types.Message, state):
    async with state.proxy() as data:
        if message.text:
            if len(message.text.split(' ')) > 1:
                data['name'], data['surname'], *_ = message.text.split(' ')
            else:
                await message.answer("Нужно вести и имя и фамилию:")
                return
        else:
            await message.answer("Поле не может быть пустым")
            return
    await message.answer("Отлично! Теперь введите ваш номер телефона:", reply_markup=get_phone_number)
    await ApplicationForm.PHONE.set()


async def get_phone(message: types.Message, state):
    async with state.proxy() as data:
        if message.contact:
            is_valid = await validate_mobile_number(str(message.contact['phone_number']))
        else:
            is_valid = await validate_mobile_number(message.text)
        if is_valid:
            if message.contact:
                data['PHONE'] = str(message.contact['phone_number'])
            else:
                data['PHONE'] = message.text
        else:
            await message.answer("Вы ввели некоректный номер телефона")
            return
    await message.answer(f"мы записали ваш номер:\n{data['PHONE']}", reply_markup=types.ReplyKeyboardRemove())
    await message.answer("Спасибо! Теперь введите вашу почту:", reply_markup=skip_email('app_'))
    await ApplicationForm.EMAIL.set()


async def skip_email_handler(c: types.CallbackQuery, state):
    await c.message.edit_text(f"Регистрация без email.")

    async with state.proxy() as data:
        data['EMAIL'] = '-'
        await state.reset_state()
    await start_ad_form(c, state)


async def get_email(message: types.Message, state):
    async with state.proxy() as data:
        is_valid = await validate_email(message.text)
        if is_valid:
            data['EMAIL'] = message.text
        else:
            await message.answer("Вы ввели некоректный почтовый адрес")
            return
        await state.reset_state()
    await start_ad_form(message.text, state)


async def start_ad_form(c: types.CallbackQuery, state):
    if c.data:
        await c.message.edit_text(f"Благодарим за желание разместить заявку в бирже строителей.\n"
                                  f"Следуйте инструкциям ниже:")
        async with state.proxy() as data:
            data['registered'] = c.data

    federal_districts_list = await get_federal_districts()

    async with state.proxy() as data:
        data['federal_districts'] = federal_districts_list
    await c.message.answer("Выберите ваш федеральный округ:",
                           reply_markup=choose_federal_district_keyboard(federal_districts_list, 'app'))


async def location_federal_district_callback(callback_query: types.CallbackQuery, state):
    region_id = int(callback_query.data.split('_')[-1])
    async with state.proxy() as data:
        location = data['federal_districts']
    await callback_query.message.edit_text(f"Округ выбран - {location[region_id]}")
    regions = await get_regions_by_district(location[region_id])
    async with state.proxy() as data:
        data['regions'] = regions
    await callback_query.message.answer("Выберите ваш регион: ",
                                        reply_markup=chose_region_keyboard(regions, 'app'))


async def next_district_page_callback(callback_query: types.CallbackQuery, state):
    async with state.proxy() as data:
        federal_districts = data['federal_districts']
    page = int(callback_query.data.split('_')[-1])
    new_keyboard = choose_federal_district_keyboard(federal_districts, 'app', page)
    await bot.edit_message_reply_markup(chat_id=callback_query.message.chat.id,
                                        message_id=callback_query.message.message_id,
                                        reply_markup=new_keyboard)


async def next_region_page_callback(callback_query: types.CallbackQuery, state):
    async with state.proxy() as data:
        regions = data['regions']
    page = int(callback_query.data.split('_')[-1])
    new_keyboard = chose_region_keyboard(regions, 'app', page)
    await bot.edit_message_reply_markup(chat_id=callback_query.message.chat.id,
                                        message_id=callback_query.message.message_id,
                                        reply_markup=new_keyboard)


async def location_region_callback(callback_query: types.CallbackQuery, state):
    region_id = int(callback_query.data.split('_')[-1])
    async with state.proxy() as data:
        regions = data['regions']
        data['region_id'] = region_id
    cities_list = await get_cities_by_region(regions[region_id][-1])
    await callback_query.message.edit_text(f"Регион выбран - {regions[region_id][0]}")
    async with state.proxy() as data:
        data['cities'] = cities_list
    await callback_query.message.answer("Выберите город: ",
                                        reply_markup=chose_city_keyboard(cities_list, 'app'))


async def get_location_city(callback_query: types.CallbackQuery, state):
    city_id = int(callback_query.data.split('_')[-1])
    async with state.proxy() as data:
        cities = data['cities']
        data['city_name'] = cities[city_id][0]
        data['city_kladr_id'] = cities[city_id][-1]
        await callback_query.message.edit_text(f"Город выбран - {cities[city_id][0]}")
    loading_message = await callback_query.message.answer("Загружаем список категорий...")
    categories = await get_categories_data()
    await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=loading_message.message_id)

    async with state.proxy() as data:
        data['category_list'] = categories

    await callback_query.message.answer("Выберите категорию:",
                           reply_markup=generate_category_keyboard(categories, 'app'))


async def next_city_page_callback(c: types.CallbackQuery, state):
    async with state.proxy() as data:
        cities = data['cities']
    page = int(c.data.split('_')[-1])
    new_keyboard = chose_city_keyboard(cities, 'app', page)
    await bot.edit_message_reply_markup(chat_id=c.message.chat.id,
                                        message_id=c.message.message_id,
                                        reply_markup=new_keyboard)


async def next_categories_page_callback(callback_query: types.CallbackQuery, state):
    async with state.proxy() as data:
        category_list = data['category_list']
    page = int(callback_query.data.split('_')[-1])
    new_keyboard = generate_category_keyboard(category_list, 'app', page)
    await bot.edit_message_reply_markup(chat_id=callback_query.message.chat.id,
                                        message_id=callback_query.message.message_id,
                                        reply_markup=new_keyboard)


async def process_category_callback(callback_query: types.CallbackQuery, state):
    category_id = int(callback_query.data.split('_')[-1])
    async with state.proxy() as data:
        category_list = data['category_list']
        data['category_id'] = list(category_list[category_id].values())[0]
        data['category'] = list(category_list[category_id].keys())[0]
        await callback_query.message.edit_text(f"Выбрана категория - {data['category']}")
    await callback_query.message.answer("Какой у вас бюджет:\n"
                                        "(Например 250 000₽)", reply_markup=skip_price('app'))
    await ApplicationForm.PRICE.set()


async def get_price(message: types.Message, state):
    price = message.text
    if not price.isdigit():
        await message.answer("Цена должна быть указана числом (в рублях). Пожалуйста, введите цену еще раз.")
        return
    async with state.proxy() as data:
        data['price'] = price
        await message.answer("Введите название объявления:")
    await ApplicationForm.TITLE.set()


async def skip_price_handler(c: types.CallbackQuery, state):
    async with state.proxy() as data:
        data['price'] = '-'
        await state.reset_state()
        await c.message.edit_text("Хорошо, профессиональные строители\n"
                               "рассчитают смету для Вас")
        await c.message.answer("Введите название вашего объявления:\n"
                               "Пример: \"Ремонт крыши склада 200 м кв.\"")
        await ApplicationForm.TITLE.set()


async def get_title(message: types.Message, state):
    async with state.proxy() as data:
        if len(message.text) < 10:
            await message.answer("Название должно содержать минимум 10 символов")
            return
        data['title'] = message.text
    await message.answer("Кратко опишите что нужно сделать:")
    await ApplicationForm.DESCRIPTION.set()


async def get_description(message: types.Message, state):
    async with state.proxy() as data:
        data['description'] = message.text
        await state.reset_state()

    await message.answer("Требуется ли вам загрузить какие-то фотографии или документы ?",
                           reply_markup=is_required('app'))


async def required_photo(c:  types.CallbackQuery, state):
    if c.data.split('_')[-1] == 'true':
        await c.message.edit_text("Загрузите данные по одному файлу")
        await ApplicationForm.PHOTO.set()
    else:
        await c.message.edit_text("Загрузка фотографий отклонена")
        await c.message.answer("Вы успешно завершили создание заявки")
        async with state.proxy() as data:
            if 'FIO' in data and 'PHONE' in data and 'EMAIL' in data:
                if data['EMAIL']:
                    email = data['EMAIL']
                else:
                    email = ''
                result = f"Собранные данные:\n" \
                         f"ФИО: {data['name']} {data['surname']}\n" \
                         f"Номер телефона: {data['PHONE']}\n" \
                         f"Почта: {data['EMAIL']}\n" \
                         f"Категория: {data['category']}\n" \
                         f"Название: {data['title']}\n" \
                         f"Описание: {data['description']}\n" \
                         f"Цена: {data['price']}\n" \
                         f"Ваш город: {data['city_name']}\n"
                user = await create_user(data['name'], data['surname'], data['PHONE'], c.message.from_user.id,
                                         email)
                await db.update_website_id(c.message.from_user.id, user['user']['id'])
                user_website_id = user['user']['id']
                await create_ad(user_website_id, data['category_id'], data['description'], data['city_name'],
                                data['city_kladr_id'])
            else:
                result = f"Собранные данные:\n" \
                         f"Категория: {data['category']}\n" \
                         f"Название: {data['title']}\n" \
                         f"Описание: {data['description']}\n" \
                         f"Цена: {data['price']}\n" \
                         f"Ваш город: {data['city_name']}\n"
                if data['price'] == '-':
                    price = 0
                else:
                    price = data['price']
                user_website_id = db.get_website_id(c.message.from_user.id)
                await create_ad(user_website_id, data['category_id'], data['description'], data['city_name'],
                                data['city_kladr_id'], data['title'], price)
        await c.message.answer(result)
        await asyncio.sleep(1)
        await c.message.answer('Спасибо за вашу заявку!\n'
                               'Наши партнеры уже получили оповещение о ней\n'
                               'и скоро с вами свяжутся.\n\n'
                               'А пока можете ознакомиться с нашим проектом на сайте!',
                               reply_markup=just_project_link())
        await state.finish()


async def get_photo(message: types.Message, state):
    if message.content_type == types.ContentType.PHOTO:
        file_id = message.photo[-1].file_id
    else:
        document = message.document
        file_id = document.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    async with state.proxy() as data:
        uploaded_files = data.get("uploaded_files", [])
        uploaded_files.append(file_path)
        data["uploaded_files"] = uploaded_files
        await state.reset_state()
    await message.answer("Желаете загрузть еще документ?", reply_markup=more_docs('app'))


async def load_document(c: types.CallbackQuery, state):
    if c.data.split('_')[-1] == 'yes':
        await c.message.edit_text(f"Загрузите еще один файл")
        await ApplicationForm.PHOTO.set()
    else:
        async with state.proxy() as data:
            if 'FIO' in data and 'PHONE' in data and 'EMAIL' in data:
                result = f"Собранные данные:\n" \
                         f"ФИО: {data['FIO']}\n" \
                         f"Номер телефона: {data['PHONE']}\n" \
                         f"Почта: {data['EMAIL']}\n" \
                         f"Категория: {data['category']}\n" \
                         f"Название: {data['title']}\n" \
                         f"Описание: {data['description']}\n" \
                         f"Цена: {data['price']}\n" \
                         f"Ваш город: {data['city_name']}\n" \
                         f"Загружено {len(data['uploaded_files'])} файлов\n"
                if data['EMAIL']:
                    email = data['EMAIL']
                else:
                    email = ''

                user = await create_user(data['name'], data['surname'], data['PHONE'], c.message.from_user.id,
                                         email)
                await db.update_website_id(c.message.from_user.id, user['user']['id'])
                user_website_id = user['user']['id']
                await create_ad(user_website_id, data['category_id'], data['description'], data['city_name'],
                                data['city_kladr_id'])
            else:
                result = f"Собранные данные:\n" \
                         f"Категория: {data['category']}\n" \
                         f"Название: {data['title']}\n" \
                         f"Описание: {data['description']}\n" \
                         f"Цена: {data['price']}\n" \
                         f"Ваш город: {data['city_name']}\n" \
                         f"Загружено {len(data['uploaded_files'])} файлов\n"
                if data['price'] == '-':
                    price = 0
                else:
                    price = data['price']
                user_website_id = db.get_website_id(c.message.from_user.id)
                await create_ad(user_website_id, data['category_id'], data['description'], data['city_name'],
                                data['city_kladr_id'], data['title'], price)

        await c.message.edit_text(result)
        await c.message.answer('Спасибо за вашу заявку!\n'
                               'Наши партнеры уже получили оповещение о ней\n'
                               'и скоро с вами свяжутся.\n\n'
                               'А пока можете ознакомиться с нашим проектом на сайте!',
                               reply_markup=just_project_link())
        await state.finish()


def registrate_app_form(dp: Dispatcher):
    dp.register_callback_query_handler(start_app_form, lambda c: c.data.startswith('create_application_'))
    dp.register_message_handler(get_fio, state=ApplicationForm.FIO)
    dp.register_message_handler(get_phone, state=ApplicationForm.PHONE)
    dp.register_message_handler(get_email, state=ApplicationForm.EMAIL)
    dp.register_callback_query_handler(skip_email_handler, lambda c: c.data.startswith('app_email_skip'),
                                       state=aiogram.filters.state.any_state)
    dp.register_callback_query_handler(start_ad_form, lambda c: c.data.startswith('in_app_create_application_'))
    dp.register_callback_query_handler(next_categories_page_callback, lambda c: c.data.startswith('app_next_page_'))
    dp.register_callback_query_handler(process_category_callback, lambda c: c.data.startswith('app_button_'))
    dp.register_message_handler(get_title, state=ApplicationForm.TITLE)
    dp.register_message_handler(get_description, state=ApplicationForm.DESCRIPTION)
    dp.register_callback_query_handler(location_federal_district_callback,
                                       lambda c: c.data.startswith('app_district_button_'))
    dp.register_callback_query_handler(next_district_page_callback,
                                       lambda c: c.data.startswith('app_next_district_page_'))
    dp.register_callback_query_handler(location_region_callback, lambda c: c.data.startswith('app_region_button_'))
    dp.register_callback_query_handler(next_region_page_callback, lambda c: c.data.startswith('app_next_region_page_'))
    dp.register_callback_query_handler(get_location_city, lambda c: c.data.startswith('app_city_button_'))
    dp.register_callback_query_handler(next_city_page_callback, lambda c: 'app_next_city_page_' in c.data)
    dp.register_message_handler(get_price, state=ApplicationForm.PRICE)
    dp.register_callback_query_handler(skip_price_handler, lambda c: 'app_skip_price' in c.data,
                                       state=aiogram.filters.state.any_state)
    dp.register_callback_query_handler(required_photo, lambda c: c.data.startswith('app_required_photo_'))
    dp.register_message_handler(get_photo, content_types=[*types.ContentTypes.DOCUMENT,
                                                          *types.ContentTypes.PHOTO],
                                state=ApplicationForm.PHOTO)
    dp.register_callback_query_handler(load_document, lambda c: c.data.startswith('app_more_docs_'))