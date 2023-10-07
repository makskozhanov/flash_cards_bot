import asyncio
from telebot import asyncio_filters
from bot_init import bot
from message_handlers import start, hello
from user_states import UserStates

bot.register_message_handler(start, commands='start', pass_bot=True)
bot.register_message_handler(hello, state=UserStates.firstLogin, pass_bot=True)

bot.add_custom_filter(asyncio_filters.StateFilter(bot))
asyncio.run(bot.polling())





