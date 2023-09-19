# -*- coding: utf-8 -*-
from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from config import BOT_TOKEN
from logs.logger_app import get_logger
from database.db_commands import DataBase

logger = get_logger('app')

bot = Bot(token=BOT_TOKEN)

dp = Dispatcher(bot, storage=MemoryStorage())


async def create_table():
    """инициализация соединения, создание таблиц"""
    user_table = DataBase()
    await user_table.create_table()
