# -*- coding: utf-8 -*-
import logging

from api.api_functions import get_contractors
from loader import bot, dp, create_table
from aiogram.utils import executor
from handlers import start, customer, builder
from forms import registrate_user, register_application,\
	choose_app_or_builder, sub_to_category

logger = logging.getLogger('app.bot')


async def on_startup(dp):
	"""запускает функции ниже при старте"""
	await create_table()
	logger.info('the bot started working.')


async def on_shutdown(dp):
	"""запускает функции ниже в момент прекращения работы робота"""
	logger.info('the bot stopped working.')
	await bot.close()


start.register_start_handlers(dp)
customer.register_customer_handlers(dp)
builder.register_builders_handlers(dp)
registrate_user.registration_form(dp)
register_application.registrate_app_form(dp)
choose_app_or_builder.choose_app_or_customer_form(dp)
sub_to_category.sub_to_category_form(dp)

if __name__ == "__main__":
	"""условие запуска бота"""
	executor.start_polling(dp, skip_updates=True, on_startup=on_startup, on_shutdown=on_shutdown)
