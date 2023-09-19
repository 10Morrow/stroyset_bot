# хендлеры обработчики действий строителя
from aiogram import types, Dispatcher
from aiogram.dispatcher import filters
import aiogram
from .privileges import UserIsBuilder
from database.db_commands import DataBase
from keyboards.inline.builder import choose_app, sub_to_categories_start
from keyboards.default.start import customer_keyboard, builder_keyboard

db = DataBase()


async def builder_menu(message: types.Message, state):
    """обрабатываем действия строителя"""
    if state:
        cur_state = await state.get_state()
        if cur_state:
            await message.answer("Вы прервали заполнение данных...")
        await state.finish()
    if message.text == "Купить / Выбрать заявку":
        await message.answer("Нажмите кпопку чтобы ознакомиться со списком заказчиков", reply_markup=choose_app())

    elif message.text == "Подписаться на рассылку":
        await message.answer("Нажмите кнопку чтобы ознакомиться со списком категорий на подписку",
                             reply_markup=sub_to_categories_start())

    elif message.text == "Сменить свой статус":
        user_type = await db.get_user_status(message.from_user.id)
        if user_type == 0:
            await db.update_user_type(1, message.from_user.id)
            await message.answer('Ваш статус был изменен\n'
                                 'Теперь вы строитель', reply_markup=builder_keyboard)
        else:
            await db.update_user_type(0, message.from_user.id)
            await message.answer('Ваш статус был изменен\n'
                                 'Теперь вы заказчик', reply_markup=customer_keyboard)


def register_builders_handlers(dp: Dispatcher):
    dp.filters_factory.bind(UserIsBuilder)
    dp.register_message_handler(builder_menu, filters.Text(contains=["Купить", "/", "Выбрать", "заявку"]) |
                                filters.Text(contains=["Подписаться", "на", "рассылку"]) |
                                filters.Text(contains=["Сменить", "свой", "статус"]),
                                UserIsBuilder(), content_types=types.ContentTypes.TEXT,
                                state=aiogram.filters.state.any_state)
#                               state=aiogram.filters.state.any_state отвечает за то чтобы любые
#                               состояния форм (из forms) могли быть прерваны, пользователем.
