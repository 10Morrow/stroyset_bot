# хендлеры отвечают за регистрацию пользователей любых типов
# здесь происходит как регистрация строителя так и заказчика
import aiogram
from aiogram import types
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import Dispatcher
import logging
from aiogram.dispatcher import filters

from loader import bot
from database.db_commands import DataBase
from .validation import validate_email, validate_inn, validate_mobile_number
from keyboards.default.start import builder_keyboard, customer_keyboard, get_phone_number
from keyboards.inline.common import reg_legal_status, choose_federal_district_keyboard
from keyboards.inline.common import generate_category_keyboard, chose_region_keyboard,\
    chose_city_keyboard, is_required, more_docs, sub_more_or_no, skip_description, skip_email
from keyboards.inline.customer import project_link_and_btn
from api.api_functions import get_federal_districts, get_regions_by_district, get_cities_by_region, create_user, \
    create_ad, create_contractor
from api.api_functions import get_categories_data


db = DataBase()
logger = logging.getLogger('app.forms.registrate_user')


class UserReg(StatesGroup):
    FIO = State()
    PHONE = State()
    EMAIL = State()
    COMPANY_NAME = State()
    INN = State()

    BUILD_DESCRIPTION = State()
    BUILD_PHOTO = State()


async def start_form(c: types.CallbackQuery, state):
    if c.data == "registrate_builder":
        await bot.edit_message_reply_markup(chat_id=c.message.chat.id,
                                            message_id=c.message.message_id)
    async with state.proxy() as data:
        data['USER_STATUS'] = c.data
        logger.info(data['USER_STATUS'])
    await c.message.answer("Давайте начнем процесс регистрации.\nВведите ваше ФИО:")
    await UserReg.FIO.set()


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
    await UserReg.PHONE.set()


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
    await message.answer("Отлично! Теперь введите вашу почту:", reply_markup=skip_email())
    await UserReg.EMAIL.set()


async def get_email(message: types.Message, state):
    async with state.proxy() as data:
        is_valid = await validate_email(message.text)
        if is_valid:
            data['EMAIL'] = message.text
        else:
            await message.answer("Вы ввели некоректный почтовый адрес")
            return
        if data["USER_STATUS"] == "registrate_builder":
            await state.reset_state()
            await message.answer("Отлично! Теперь укажите ваш юридический статус (физ лицо, ИП или юр лицо)",
                                 reply_markup=reg_legal_status())

        elif data["USER_STATUS"] == "registrate_customer":
            await state.reset_state()
            await message.answer("Поздравляю вы зарегистрированы!")
    if data["USER_STATUS"] == "registrate_customer":
        await get_data_done(message, state)


async def skip_email_handler(c: types.CallbackQuery, state):
    await c.message.edit_text(f"Регистрация без email.")

    async with state.proxy() as data:
        data['EMAIL'] = '-'

        if data["USER_STATUS"] == "registrate_builder":
            await state.reset_state()
            await c.message.answer("Отлично! Теперь укажите ваш юридический статус (физ лицо, ИП или юр лицо)",
                                 reply_markup=reg_legal_status())

        elif data["USER_STATUS"] == "registrate_customer":
            await state.reset_state()
            await c.message.answer("Поздравляю вы зарегистрированы!")

    if data["USER_STATUS"] == "registrate_customer":
        await get_data_done(c.message, state)


async def get_legal_status(c: types.CallbackQuery, state):
    async with state.proxy() as data:
        if 'ip' in c.data:
            data['LEGAL_STATUS'] = 'ИП'
            await c.message.edit_text(f"Установлен статус: {data['LEGAL_STATUS']}")
            await c.message.answer("Укажите название вашей компании:")
            await UserReg.COMPANY_NAME.set()
        elif 'yur' in c.data:
            data['LEGAL_STATUS'] = 'ЮР.ЛИЦО'
            await c.message.edit_text(f"Установлен статус: {data['LEGAL_STATUS']}")
            await c.message.answer("Укажите название вашей компании:")
            await UserReg.COMPANY_NAME.set()
        else:
            data['LEGAL_STATUS'] = 'ФИЗ.ЛИЦО'
            await state.reset_state()
            await c.message.edit_text(f"Установлен статус: {data['LEGAL_STATUS']}")
    if data['LEGAL_STATUS'] == 'ФИЗ.ЛИЦО':
        await start_card_form(c.message, state)


async def get_company_name(message: types.Message, state):
    async with state.proxy() as data:
        data['COMPANY_NAME'] = message.text
    await message.answer("Теперь укажите ИНН вашей компании (организации):")
    await UserReg.INN.set()


async def get_inn(message: types.Message, state):
    async with state.proxy() as data:
        is_valid = await validate_inn(message.text)
        if is_valid:
            data['INN'] = message.text
            await state.reset_state()
        else:
            await message.answer("Вы ввели некоректный ИНН")
            return
    message.text = "Начать карточку"
    await start_card_form(message, state)


async def start_card_form(message: types.Message, state):
    await message.answer(f"Добавим еще немного данных для Карточки строителя, следуйте инстркуциям:")
    loading_message = await message.answer("Загружаем список категорий...")

    categories = await get_categories_data()
    await bot.delete_message(chat_id=message.chat.id, message_id=loading_message.message_id)

    async with state.proxy() as data:
        if not 'category_list' in data:
            data['category_list'] = categories
        logger.info(data)
    await message.answer("Задайте категорию ваших работ:\n"
                         "Выбирите одну или несколько категорий",
                           reply_markup=generate_category_keyboard(data['category_list'], 'card'))


async def next_categories_page_callback(callback_query: types.CallbackQuery, state):
    async with state.proxy() as data:
        category_list = data['category_list']
    page = int(callback_query.data.split('_')[-1])
    new_keyboard = generate_category_keyboard(category_list, 'card', page)
    await bot.edit_message_reply_markup(chat_id=callback_query.message.chat.id,
                                        message_id=callback_query.message.message_id,
                                        reply_markup=new_keyboard)


async def process_category_callback(callback_query: types.CallbackQuery, state):
    category_id = int(callback_query.data.split('_')[-1])
    async with state.proxy() as data:
        category_list = data['category_list']
        data['category'] = list(category_list[category_id].keys())[0]
        my_categories = data.get("my_categories", [])
        my_categories.append(list(category_list[category_id].values())[0])
        data["my_categories"] = my_categories
        data['category_list'].pop(category_id)
        await callback_query.message.edit_text(f"Выбрана категория - {data['category']}")
        await callback_query.message.answer(f"Задать еще одну категорию?",
                                            reply_markup=sub_more_or_no('card'))


async def sub_more_or_not(c: types.CallbackQuery, state):
    if 'no' in c.data:
        async with state.proxy() as data:
            await c.message.edit_text(f'Вы подписались на {len(data["my_categories"])} категорий')

            federal_districts_list = await get_federal_districts()
            data['user_status'] = c.data
            data['federal_districts'] = federal_districts_list
            await state.reset_state()
        await c.message.answer("Выберите ваш федеральный округ:",
                               reply_markup=choose_federal_district_keyboard(federal_districts_list, 'card'))

    else:
        await c.message.edit_text('Задайте еще одну категорию: ')
        c.message.text = "Начать карточку"
        async with state.proxy() as data:
            await c.message.answer("Выберите категорию ваших работ:",
                                 reply_markup=generate_category_keyboard(data['category_list'], 'card'))


async def next_district_page_callback(callback_query: types.CallbackQuery, state):
    async with state.proxy() as data:
        federal_districts = data['federal_districts']
    page = int(callback_query.data.split('_')[-1])
    new_keyboard = choose_federal_district_keyboard(federal_districts, 'card', page)
    await bot.edit_message_reply_markup(chat_id=callback_query.message.chat.id,
                                        message_id=callback_query.message.message_id,
                                        reply_markup=new_keyboard)


async def location_federal_district_callback(callback_query: types.CallbackQuery, state):
    region_id = int(callback_query.data.split('_')[-1])
    async with state.proxy() as data:
        location = data['federal_districts']
    await callback_query.message.edit_text(f"Округ выбран - {location[region_id]}")
    regions = await get_regions_by_district(location[region_id])
    async with state.proxy() as data:
        data['regions'] = regions
    await callback_query.message.answer("Выберите ваш регион: ",
                                        reply_markup=chose_region_keyboard(regions, 'card'))


async def next_region_page_callback(callback_query: types.CallbackQuery, state):
    async with state.proxy() as data:
        regions = data['regions']
    page = int(callback_query.data.split('_')[-1])
    new_keyboard = chose_region_keyboard(regions, 'card', page)
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
                                        reply_markup=chose_city_keyboard(cities_list, 'card'))


async def get_location_city(callback_query: types.CallbackQuery, state):
    city_id = int(callback_query.data.split('_')[-1])
    async with state.proxy() as data:
        cities = data['cities']
        data['city_name'] = cities[city_id][0]
        data['city_kladr_id'] = cities[city_id][-1]
        await callback_query.message.edit_text(f"Город выбран - {cities[city_id][0]}")
        await state.reset_state()
    await callback_query.message.answer("Здесь вы можете дополнить описание:\n"
                           "Ваш опыт работ, на чем\n"
                           "специализируетесь и тд.", reply_markup=skip_description())
    await UserReg.BUILD_DESCRIPTION.set()


async def get_description(message: types.Message, state):
    async with state.proxy() as data:
        data['description'] = message.text
        await state.reset_state()
    await message.answer("Требуется ли вам загрузить какие-то фотографии или документы ваших работ ?",
                           reply_markup=is_required('card'))


async def skip_description_handler(c: types.CallbackQuery, state):
    await c.message.edit_text(f"Установлено без описания.")

    async with state.proxy() as data:
        data['description'] = '-'
        await state.reset_state()
    await c.message.answer("Требуется ли вам загрузить какие-то фотографии или документы ваших работ ?",
                         reply_markup=is_required('card'))


async def next_city_page_callback(c: types.CallbackQuery, state):
    async with state.proxy() as data:
        cities = data['cities']
    page = int(c.data.split('_')[-1])
    new_keyboard = chose_city_keyboard(cities, 'card', page)
    await bot.edit_message_reply_markup(chat_id=c.message.chat.id,
                                        message_id=c.message.message_id,
                                        reply_markup=new_keyboard)


async def required_photo(c:  types.CallbackQuery, state):
    if c.data.split('_')[-1] == 'true':
        await c.message.answer('Загрузите данные по одному файлу')
        await UserReg.BUILD_PHOTO.set()
    else:
        await c.message.edit_text("Загрузка фотографий отклонена")
        await c.message.answer("Вы успешно завершили процесс регистрации")
        c.message.text = "Начать карточку"
        await get_data_done(c.message, state)


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
    await message.answer("Желаете загрузить еще документ?", reply_markup=more_docs('card'))


async def load_document(c: types.CallbackQuery, state):
    if c.data.split('_')[-1] == 'yes':
        await c.message.edit_text(f"Загрузите еще один файл")
        await UserReg.BUILD_PHOTO.set()
    else:
        await c.message.edit_text('файлы загружены')
    c.message.text = "Начать карточку"
    await get_data_done(c.message, state)


async def get_data_done(message: types.Message, state):
    await db.update_registered_state(message.chat.id, 1)
    legal_status, company_name, inn, email = '', '', '', ''
    async with state.proxy() as data:
        result = f"ФИО: {data['name'] } {data['surname']}\n" \
                 f"Номер телефона: {data['PHONE']}\n" \
                 f"Почта: {data['EMAIL']}\n"

        if "LEGAL_STATUS" in data:
            result += f"Юридический статус: {data['LEGAL_STATUS']}\n"
            if 'ФИЗ' in data["LEGAL_STATUS"]:
                legal_status = 'fl'
            elif 'ЮР' in data["LEGAL_STATUS"]:
                legal_status = 'ul'
            else:
                legal_status = 'ip'
        if data['EMAIL'] != '-':
            email = data['EMAIL']
        if 'COMPANY_NAME' in data:
            company_name = data['COMPANY_NAME']
            result += f"Название компании: {data['COMPANY_NAME']}\n"
        if 'INN' in data:
            inn = data['INN']
            result += f"ИНН: {data['INN']}\n"
        if 'uploaded_files' in data:
            result += f"Загружено {len(data['uploaded_files'])} файлов\n"
        if data["USER_STATUS"] == "registrate_builder":
            user = await create_user(data['name'], data['surname'], data['PHONE'], message.from_user.id,
                              email, legal_status, company_name, inn)
            await db.update_website_id(message.from_user.id, user['user']['id'])
            user_website_id = user['user']['id']
            await create_contractor(user_website_id, data['description'], data['my_categories'][0],
                                    data['city_kladr_id'])
            result_message = "Ваша карточка строителя:\n"
            result += f"Установлено(-а) {len(data['my_categories'])} категория(-й)\n" \
                      f"Описание: {data['description']}\n" \
                      f"Ваш город: {data['city_name']}\n"
            result_message += result
            await message.answer(result_message, reply_markup=builder_keyboard)
            await message.answer("Ура 🎉\n"
                                 "Ваши данные уже доступны для заказчиков Биржи СтройСеть\n"
                                 "Спасибо за доверие!\n"
                                 "Теперь вы можете выбрать подходящую заявку\n"
                                 "И ознакомиться с нашим проектом", reply_markup=project_link_and_btn())
        else:
            result_message = "Данные вашей регистрации:\n"
            result_message += result
            await message.answer(result_message, reply_markup=customer_keyboard)
            user = await create_user(data['name'], data['surname'], data['PHONE'], message.from_user.id, email)
        await state.finish()


def registration_form(dp: Dispatcher):
    dp.register_callback_query_handler(start_form, lambda c: c.data.startswith('registrate_'))
    dp.register_message_handler(get_fio, state=UserReg.FIO)
    dp.register_message_handler(get_phone, state=UserReg.PHONE, content_types=[types.ContentType.CONTACT,
                                                                               types.ContentType.TEXT])
    dp.register_message_handler(get_email, state=UserReg.EMAIL)
    dp.register_callback_query_handler(get_legal_status, lambda c: c.data.startswith('leg_status_'))
    dp.register_message_handler(get_company_name, state=UserReg.COMPANY_NAME)
    dp.register_message_handler(get_inn, state=UserReg.INN)

    dp.register_message_handler(start_card_form, filters.Text(contains=["Начать", "карточку"]))
    dp.register_callback_query_handler(next_categories_page_callback, lambda c: c.data.startswith('card_next_page_'))
    dp.register_callback_query_handler(process_category_callback, lambda c: c.data.startswith('card_button_'))
    dp.register_callback_query_handler(sub_more_or_not, lambda c: c.data.startswith('card_sub_more'))
    dp.register_message_handler(get_description, state=UserReg.BUILD_DESCRIPTION)
    dp.register_callback_query_handler(skip_description_handler, lambda c: c.data.startswith('description_skip'),
                                       state=aiogram.filters.state.any_state)
    dp.register_callback_query_handler(skip_email_handler, lambda c: c.data.startswith('email_skip'),
                                       state=aiogram.filters.state.any_state)
    dp.register_callback_query_handler(location_federal_district_callback,
                                       lambda c: c.data.startswith('card_district_button_'))
    dp.register_callback_query_handler(next_district_page_callback,
                                       lambda c: c.data.startswith('card_next_district_page_'))
    dp.register_callback_query_handler(location_region_callback, lambda c: c.data.startswith('card_region_button_'))
    dp.register_callback_query_handler(next_region_page_callback, lambda c: c.data.startswith('card_next_region_page_'))
    dp.register_callback_query_handler(get_location_city, lambda c: c.data.startswith('card_city_button_'))
    dp.register_callback_query_handler(next_city_page_callback, lambda c: 'card_next_city_page_' in c.data)
    dp.register_callback_query_handler(required_photo, lambda c: c.data.startswith('card_required_photo_'))
    dp.register_message_handler(get_photo, content_types=[*types.ContentTypes.DOCUMENT,
                                                          *types.ContentTypes.PHOTO],
                                state=UserReg.BUILD_PHOTO)
    dp.register_callback_query_handler(load_document, lambda c: c.data.startswith('card_more_docs_'))
