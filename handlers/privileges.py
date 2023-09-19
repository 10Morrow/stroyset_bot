from aiogram import types
from aiogram.dispatcher.filters import BoundFilter

from database.db_commands import DataBase

db = DataBase()


class UserIsBuilder(BoundFilter):
    # проверяет что человек зарегистрирован в ДБ как строитель (это запрещает ему использовать функции заказчика)
    async def check(self, message: types.Message) -> bool:
        user_id = message.from_user.id
        registered = await db.user_registered(user_id)
        user_exist = await db.check_user(user_id)
        if user_exist:
            status = await db.get_user_status(user_id)
            result = status and registered
            return True if result else False
        else:
            return False


class UserIsCustomer(BoundFilter):
    # проверяет что человек зарегистрирован в ДБ как заказчик (это запрещает ему использовать функции строителя)
    async def check(self, message: types.Message) -> bool:
        user_id = message.from_user.id
        user_exist = await db.check_user(user_id)
        if user_exist:
            status = await db.get_user_status(user_id)
            return False if status else True
        else:
            return False
