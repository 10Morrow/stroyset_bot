# хендлеры отвечающие за действия пользователя
from aiogram import types, Dispatcher
from aiogram.dispatcher import filters
import aiogram

from keyboards.inline.common import registration
from keyboards.inline.customer import chose_how_create_application, create_app_like_reg_user, choose_builder
from keyboards.default.start import customer_keyboard, builder_keyboard
from .privileges import UserIsCustomer
from database.db_commands import DataBase

db = DataBase()


async def customer_menu(message: types.Message, state=None):
    """обрабатываем действия заказчика"""
    if state:
        cur_state = await state.get_state()
        if cur_state:
            await message.answer("Вы прервали заполнение данных...")
        await state.finish()
    if message.text == "Разместить заявку":
        registered = await db.user_registered(message.from_user.id)
        if registered:
            await message.answer('Вы оставите заявку как зарегистрированный пользователь, '
                                 'сделка будет оформлена в безопасном режиме.', reply_markup=create_app_like_reg_user('in_app_'))
        else:
            await message.answer("С целью избежать рисков потери своих денег "
                                 "предлагаем Вам воспользоваться услугой Безопасная сделка, "
                                 "аналог  эскроу счета в банках. Вы разместите свой заказ, "
                                 "затем  выберете себе исполнителя и сформируете сделку "
                                 "и внесете средства на свой счёт  на платформе [СтройСеть](https://stroyset.pro/). "
                                 "Средства будут хранится на вашем специальном счёте до полной сдачи объекта, "
                                 "затем уйдут вашему подрядчику.\n"
                                 "Комиссия составит 1%.\n"
                                 "Можно отказаться, если передумаете.", reply_markup=chose_how_create_application()
                                 , parse_mode=types.ParseMode.MARKDOWN)
    elif message.text == "Выбрать исполнителя":
        await message.answer("Нажмите кнопку чтобы ознакомиться со списком строителей", reply_markup=choose_builder())

    elif message.text == "Сменить свой статус":
        user_type = await db.get_user_status(message.from_user.id)
        if user_type == 0:
            registered = await db.user_registered(message.from_user.id)
            if registered:
                await db.update_user_type(1, message.from_user.id)
                await message.answer('Выш статус был изменен\n'
                                     'Теперь вы строитель', reply_markup=builder_keyboard)
            else:
                await message.answer(f'Если вы хотите вырбать роль строителя', reply_markup=types.ReplyKeyboardRemove())
                await message.answer(f'Пройдите обязательную регистрацию', reply_markup=registration("builder"))
        else:
            await db.update_user_type(0, message.from_user.id)
            await message.answer('Выш статус был изменен\n'
                                 'Теперь вы заказчик', reply_markup=customer_keyboard)


def register_customer_handlers(dp: Dispatcher):
    dp.filters_factory.bind(UserIsCustomer)
    dp.register_message_handler(customer_menu, filters.Text(contains=["Разместить", "заявку"]) |
                                filters.Text(contains=["Выбрать", "исполнителя"]) |
                                filters.Text(contains=["Сменить", "свой", "статус"]),
                                UserIsCustomer(), content_types=types.ContentTypes.TEXT,
                                state=aiogram.filters.state.any_state)