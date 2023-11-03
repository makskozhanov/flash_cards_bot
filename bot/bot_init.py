"""
This file creates an instance of AsyncTeleBot and defines the storage of states.
"""

import config
from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_storage import StateRedisStorage

state_storage = StateRedisStorage()
bot = AsyncTeleBot(token=config.BOT_TOKEN, state_storage=state_storage)
