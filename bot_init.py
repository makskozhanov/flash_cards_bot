import config
from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_storage import StateRedisStorage

state_storage = StateRedisStorage()
bot = AsyncTeleBot(token=config.BOT_TOKEN, state_storage=state_storage)
