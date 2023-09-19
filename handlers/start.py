# базовые хендлеры обработки сообщений после /start
import logging
from aiogram import types, Dispatcher
from aiogram.dispatcher import filters
from database.db_commands import DataBase
from keyboards.default.start import choose_user_type, customer_keyboard, builder_keyboard
from keyboards.inline.common import registration
db = DataBase()

logger = logging.getLogger('app.handlers.start')


async def start(message: types.Message):
	"""приветствуем и направляем по клавиатуре пользователя"""
	exist = await db.check_user(message.from_user.id)
	if message.from_user.first_name:
		name = message.from_user.first_name
	else:
		name = "сэр"
	if not exist:
		await message.answer(f'Здравствуйте, {name}!\n'
							f'Добро пожаловать в компанию [СтройСеть](https://stroyset.pro/)!',
							parse_mode=types.ParseMode.MARKDOWN)

		await message.answer('Вы строитель или заказчик?', reply_markup=choose_user_type)
	else:
		if exist[0]:
			registered = await db.user_registered(message.from_user.id)
			if registered:
				await message.answer(f'Рад вас снова видеть {name}'
									f'\nВаша роль на платформе: Строитель', reply_markup=builder_keyboard)
			else:
				await message.answer('Вы строитель или заказчик?', reply_markup=choose_user_type)
		else:
			await message.answer(f'Рад вас снова видеть {name}'
								f'\nВаша роль на платформе: Заказчик', reply_markup=customer_keyboard)


async def choose_user_type_handler(message: types.Message):
	user_type = message.text
	user_id = message.from_user.id
	exist = await db.check_user(user_id)
	registered = await db.user_registered(user_id)

	if not exist:
		if 'Я строитель' in user_type:
			await db.add_user(user_id, 1)
			await message.answer(f'Вы выбрали роль строителя', reply_markup=types.ReplyKeyboardRemove())
			await message.answer(f'Пройдите обязательную регистрацию', reply_markup=registration("builder"))

		else:
			await db.add_user(user_id, 0)
			await message.answer(f'Вы выбрали роль заказчика', reply_markup=customer_keyboard)
	else:
		if exist[0] and registered:
			await message.answer(f'Вы уже были зарегистрированы как строитель.', reply_markup=builder_keyboard)
		elif exist[0] and not registered:
			if 'Я строитель' in user_type:
				await message.answer(f'Вы выбрали роль строителя', reply_markup=types.ReplyKeyboardRemove())
				await message.answer(f'Пройдите обязательную регистрацию', reply_markup=registration("builder"))
			else:
				await message.answer(f'Вы уже были зарегистрированы как заказчик.', reply_markup=customer_keyboard)
		elif exist[0] == 0:
			await message.answer(f'Вы уже были зарегистрированы как заказчик.', reply_markup=customer_keyboard)


def register_start_handlers(dp: Dispatcher):
	dp.register_message_handler(start, commands=["start"])
	dp.register_message_handler(choose_user_type_handler, filters.Text(contains=["Я", "строитель"]) |
								filters.Text(contains=["Я", "заказчик"]),
								content_types=types.ContentTypes.TEXT)
