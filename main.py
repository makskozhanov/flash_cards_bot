import asyncio
from telebot import asyncio_filters
from bot_init import bot
from message_handlers import start, create_deck, delete_deck, add_card
from button_handlers import create_deck_handler, deck_menu_handler, delete_deck_handler
from user_states import UserStates

bot.register_message_handler(start, commands='start', pass_bot=True)
bot.register_message_handler(create_deck, state=UserStates.create_deck, pass_bot=True)
bot.register_message_handler(delete_deck, state=UserStates.delete_deck, pass_bot=True)
bot.register_message_handler(add_card, state=UserStates.add_card, pass_bot=True)

bot.register_callback_query_handler(create_deck_handler, func=lambda c: c.data == 'create_deck', pass_bot=True)
bot.register_callback_query_handler(delete_deck_handler, func=lambda c: c.data == 'delete_deck', pass_bot=True)
bot.register_callback_query_handler(deck_menu_handler, func=lambda c: True, pass_bot=True)

bot.add_custom_filter(asyncio_filters.StateFilter(bot))
asyncio.run(bot.polling())
