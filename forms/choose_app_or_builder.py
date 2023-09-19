# здесь представленны хендлеры отвечающие за
# обработку и предоставление выборки списка объявлений
# или же списка строителей.


import asyncio
from aiogram import types
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import Dispatcher
import logging

from loader import bot
from database.db_commands import DataBase
from keyboards.inline.common import buy_keyboard, chose_region_keyboard, chose_city_keyboard, pay_for_and_check, \
    choose_federal_district_keyboard
from payment.pay_keeper import check_status, create_bill, cancel_payment
from api.api_functions import get_federal_districts, get_regions_by_district, get_cities_by_region, get_contractors

db = DataBase()
logger = logging.getLogger('app.forms.choose_app_or_builder')


class ChooseForm(StatesGroup):
    client = State()


async def start_choosing(c: types.CallbackQuery, state):
    """обрабатывает хендлер содержащий 'choose_type_' в c.data"""
    if "Найти " in c.message.reply_markup.inline_keyboard[0][0].text:
        await bot.edit_message_reply_markup(chat_id=c.message.chat.id,
                                            message_id=c.message.message_id)
    await bot.answer_callback_query(c.id, text=None, show_alert=False, url=None)
    federal_districts_list = await get_federal_districts()

    async with state.proxy() as data:
        data['user_status'] = c.data
        data['federal_districts'] = federal_districts_list
    await c.message.answer("Выберите ваш федеральный округ:",
                           reply_markup=choose_federal_district_keyboard(federal_districts_list, 'choose'))


async def next_district_page_callback(callback_query: types.CallbackQuery, state):
    async with state.proxy() as data:
        federal_districts = data['federal_districts']
    page = int(callback_query.data.split('_')[-1])
    new_keyboard = choose_federal_district_keyboard(federal_districts, 'choose', page)
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
                                        reply_markup=chose_region_keyboard(regions, 'choose'))


async def next_region_page_callback(callback_query: types.CallbackQuery, state):
    async with state.proxy() as data:
        regions = data['regions']
    page = int(callback_query.data.split('_')[-1])
    new_keyboard = chose_region_keyboard(regions, 'choose', page)
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
                                        reply_markup=chose_city_keyboard(cities_list, 'choose'))


async def next_city_page_callback(c: types.CallbackQuery, state):
    async with state.proxy() as data:
        cities = data['cities']
    page = int(c.data.split('_')[-1])
    new_keyboard = chose_city_keyboard(cities, 'choose', page)
    await bot.edit_message_reply_markup(chat_id=c.message.chat.id,
                                        message_id=c.message.message_id,
                                        reply_markup=new_keyboard)


async def get_location_city(callback_query: types.CallbackQuery, state):
    city_id = int(callback_query.data.split('_')[-1])
    async with state.proxy() as data:
        cities = data['cities']
        await callback_query.message.edit_text(f"Город выбран - {cities[city_id][0]}")
        city_kladr_id = cities[city_id][-1]
        if 'app' in data['user_status']:
            # user_list = get_user_list_by_city_id(city_id)
            user_list = [{'id': 10921,
                          'app_name': 'Требуется ремонт дачи',
                          'app_description':'требуется колосальный ремонт дачи',
                          'number': '89031248134',
                          'extra_cost': True},
                         {'id': 10922,
                          'app_name': 'Требуется ремонт',
                          'app_description': 'требуется колосальный ремонт',
                          'number': '89933444334',
                          'extra_cost': False},
                         {'id': 10923,
                          'app_name': 'Требуется косметический ремонт',
                          'app_description': 'требуется косметический ремонт дачи',
                          'number': '89831381221',
                          'extra_cost': True}
                         ]
            data['user_list'] = user_list
            await callback_query.message.edit_text(f"Список клиентов в городе {cities[city_id][0]}:")
            for i, user in enumerate(user_list):
                result = f"Название: {user['app_name']}\n" \
                         f"Описание: {user['app_description']}"
                await callback_query.message.answer(result,
                                                   reply_markup=buy_keyboard(i, user['extra_cost']))
        else:
            user_list = await get_contractors()
            await callback_query.message.edit_text(f"Список строитель в городе {cities[city_id][0]}")
            for user in user_list:
                if user[1] == 'ip':
                    status = 'ИП'
                elif user[1] == 'ul':
                    status = 'ЮР.ЛИЦО'
                else:
                    status = 'ФИЗ.ЛИЦО'

                result = f"Имя: {user[0]}\n" \
                         f"Статус: {status}\n"\
                         f"Описание: {user[2]}\n" \
                         f"Контакты: {user[3]}\n"
                await callback_query.message.answer(result)


async def payment(c: types.CallbackQuery, state):
    invoice_id = None
    async with state.proxy() as data:
        goal_id = int(c.data.split('_')[-1])
        if not 'invoice_id' in data:
            data['goal_id'] = goal_id
            user_data = data['user_list'][goal_id]
            data['current_user'] = user_data
            if user_data['extra_cost']:
                cost = 30
            else:
                cost = 15
            pay_url, invoice_id = await create_bill(cost)
            data['invoice_id'] = invoice_id
            new_keyboard = await pay_for_and_check(pay_url, invoice_id)
            await bot.edit_message_reply_markup(chat_id=c.message.chat.id,
                                                message_id=c.message.message_id,
                                                reply_markup=new_keyboard)
        else:
            keyboard = c.message.reply_markup
            await c.message.edit_text(f'{c.message.text}\n\nИзвините, вы не можете оплатить эту заявку,'
                                      f'пока не оплатите или не отмените предыдущуюю.', reply_markup=keyboard)
    if invoice_id:
        await check_payment(c, state)


async def check_payment(c: types.CallbackQuery, state):
    async with state.proxy() as data:
        if not 'invoice_id' in data:
            return None
        invoice_id = data['invoice_id']
        goal_id = data['goal_id']
    status = await check_status(invoice_id)
    if status == 'paid':
        async with state.proxy() as data:
            user = data['user_list'][goal_id]
        await c.message.answer('Вы успешно оплатили заказ!\n'
                               f'{c.message.text}\n'
                               f'Номер клиента : {user["number"]}')
    elif status == 'expired':
        await c.message.answer('Время ожидания истекло...')
    else:
        await asyncio.sleep(20)
        await check_payment(c, state)


async def cancel_payment_callback(c: types.CallbackQuery, state):
    async with state.proxy() as data:
        user = data['current_user']
        invoice_id = data['invoice_id']
        goal_id = data['goal_id']
        del data['invoice_id']
        del data['goal_id']
        del data['current_user']
    await cancel_payment(invoice_id=invoice_id)
    result = f"Название: {user['app_name']}\n" \
             f"Описание: {user['app_description']}"
    await c.message.edit_text(result, reply_markup=buy_keyboard(goal_id, user['extra_cost']))


def choose_app_or_customer_form(dp: Dispatcher):
    dp.register_callback_query_handler(start_choosing, lambda c: c.data.startswith('choose_type_'))

    dp.register_callback_query_handler(location_federal_district_callback,
                                       lambda c: c.data.startswith('choose_district_button_'))
    dp.register_callback_query_handler(next_district_page_callback,
                                       lambda c: c.data.startswith('choose_next_district_page_'))

    dp.register_callback_query_handler(location_region_callback,
                                       lambda c: c.data.startswith('choose_region_button_'))
    dp.register_callback_query_handler(next_region_page_callback,
                                       lambda c: c.data.startswith('choose_next_region_page_'))
    dp.register_callback_query_handler(get_location_city, lambda c: c.data.startswith('choose_city_button_'))
    dp.register_callback_query_handler(next_city_page_callback, lambda c: c.data.startswith('choose_next_city_page_'))
    dp.register_callback_query_handler(payment, lambda c: c.data.startswith('pay_for_'))
    dp.register_callback_query_handler(check_payment, lambda c: c.data.startswith('_payment_'))
    dp.register_callback_query_handler(cancel_payment_callback, lambda c: c.data.startswith('cancel_pay_for_'))