# хендлеры отвечают за подписку строителя на категории
# на данный момент метод подписки через апи еще не реализован
from aiogram import types
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import Dispatcher
import logging

from api.api_functions import get_categories_data, subscribe_to_category
from loader import bot
from database.db_commands import DataBase
from keyboards.inline.common import generate_category_keyboard, sub_more_or_no


db = DataBase()
logger = logging.getLogger('app.forms.sub_to_category')


class ChooseForm(StatesGroup):
    client = State()


async def start_subscribe(c: types.CallbackQuery, state):
    await bot.edit_message_reply_markup(chat_id=c.message.chat.id,
                                        message_id=c.message.message_id)
    loading_message = await c.message.answer("Загружаем список категорий...")
    categories = await get_categories_data()
    await bot.delete_message(chat_id=c.message.chat.id, message_id=loading_message.message_id)
    async with state.proxy() as data:
        if not 'category_list' in data:
            data['category_list'] = categories
    await c.message.answer("Выберите категорию:",
                           reply_markup=generate_category_keyboard(data['category_list'], 'sub'))


async def next_categories_page_callback(callback_query: types.CallbackQuery, state):
    async with state.proxy() as data:
        category_list = data['category_list']
    page = int(callback_query.data.split('_')[-1])
    new_keyboard = generate_category_keyboard(category_list, 'sub', page)
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
        await callback_query.message.edit_text(f"Вы подписались на - \"{data['category']}\"")
        await callback_query.message.answer(f"Подписаться на еще одну категорию?", reply_markup=sub_more_or_no('sub'))


async def sub_more_or_not(c: types.CallbackQuery, state):
    if 'no' in c.data:
        async with state.proxy() as data:
            await c.message.edit_text(f'Вы подписались на {len(data["my_categories"])} категорий')
            web_site_id = await db.get_website_id(c.message.from_user.id)
            await subscribe_to_category(web_site_id, data["my_categories"])
    else:
        await start_subscribe(c, state)


def sub_to_category_form(dp: Dispatcher):
    dp.register_callback_query_handler(start_subscribe, lambda c: c.data.startswith('sub_categories'))
    dp.register_callback_query_handler(next_categories_page_callback, lambda c: c.data.startswith('sub_next_page_'))
    dp.register_callback_query_handler(process_category_callback, lambda c: c.data.startswith('sub_button_'))
    dp.register_callback_query_handler(sub_more_or_not, lambda c: c.data.startswith('sub_sub_more'))
