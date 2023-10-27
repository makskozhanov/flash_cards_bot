import asyncio
from telebot import asyncio_filters
from bot_init import bot
from message_handlers.message_handlers import *
from message_handlers.start import start
from button_handlers import *
from user_states import UserStates

bot.register_message_handler(start, commands='start', pass_bot=True)

bot.register_message_handler(create_deck, state=UserStates.create_deck, pass_bot=True)
bot.register_message_handler(delete_deck, state=UserStates.delete_deck, pass_bot=True)
bot.register_message_handler(rename_deck, state=UserStates.rename_deck, pass_bot=True)


bot.register_message_handler(add_card_face, state=UserStates.add_card_face, pass_bot=True)
bot.register_message_handler(add_card_back, state=UserStates.add_card_back, pass_bot=True)


bot.register_callback_query_handler(main_menu_handler, func=lambda c: c.data == 'show_menu', pass_bot=True)

bot.register_callback_query_handler(learn_cards_handler, func=lambda c: c.data == 'learn', pass_bot=True)
bot.register_callback_query_handler(learn_mode_handler, func=lambda c: c.data.startswith('learn_mode'), pass_bot=True)


bot.register_callback_query_handler(deck_mode_handler, func=lambda c: c.data.startswith('deck_mode'), pass_bot=True)


bot.register_callback_query_handler(show_card, func=lambda c: c.data == 'show_card_face', pass_bot=True)

bot.register_callback_query_handler(repeat_card_tomorrow, func=lambda c: c.data == 'repeat_tomorrow', pass_bot=True)
bot.register_callback_query_handler(repeat_card_week, func=lambda c: c.data == 'repeat_week', pass_bot=True)
bot.register_callback_query_handler(repeat_card_month, func=lambda c: c.data == 'repeat_month', pass_bot=True)


bot.register_callback_query_handler(create_deck_handler, func=lambda c: c.data == 'create_deck', pass_bot=True)
bot.register_callback_query_handler(delete_deck_handler, func=lambda c: c.data == 'delete_deck', pass_bot=True)
bot.register_callback_query_handler(rename_deck_handler, func=lambda c: c.data == 'rename_deck', pass_bot=True)

bot.register_callback_query_handler(add_card_face_handler, func=lambda c: c.data == 'add_card', pass_bot=True)
bot.register_callback_query_handler(delete_card_handler, func=lambda c: c.data == 'delete_card', pass_bot=True)


bot.register_callback_query_handler(deck_menu_handler, func=lambda c: True, pass_bot=True)

bot.add_custom_filter(asyncio_filters.StateFilter(bot))
asyncio.run(bot.polling())
