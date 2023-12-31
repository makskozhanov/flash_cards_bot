"""
This file is only used to register all the handlers for user actions.
It starts bot.
"""

import asyncio
from telebot import asyncio_filters
from bot.bot_init import bot
from handlers.message_handlers import *
from handlers.start import start
from handlers.button_handlers import *
from user.user_states import UserStates

bot.register_message_handler(start, commands='start', pass_bot=True)

bot.register_message_handler(create_deck, state=UserStates.create_deck, pass_bot=True)
bot.register_message_handler(rename_deck, state=UserStates.rename_deck, pass_bot=True)

bot.register_message_handler(edit_card, state=UserStates.edit_card, pass_bot=True)


bot.register_message_handler(add_card_face, state=UserStates.add_card_face, pass_bot=True)
bot.register_message_handler(add_card_back, state=UserStates.add_card_back, pass_bot=True)

bot.register_message_handler(delete_user_input, pass_bot=True)

bot.register_callback_query_handler(main_menu_handler, func=lambda c: c.data == 'show_menu', pass_bot=True)

bot.register_callback_query_handler(learn_cards_handler, func=lambda c: c.data == 'learn', pass_bot=True)
bot.register_callback_query_handler(learn_mode_handler, func=lambda c: c.data.startswith('learn_mode'), pass_bot=True)


bot.register_callback_query_handler(deck_mode_handler, func=lambda c: c.data.startswith('deck_mode'), pass_bot=True)


bot.register_callback_query_handler(show_card, func=lambda c: c.data == 'show_card_face', pass_bot=True)

bot.register_callback_query_handler(repeat_card_handler, func=lambda c: c.data.startswith('repeat_card'), pass_bot=True)


bot.register_callback_query_handler(create_deck_handler, func=lambda c: c.data == 'create_deck', pass_bot=True)
bot.register_callback_query_handler(delete_deck_confirmation_handler, func=lambda c: c.data == 'delete_deck_confirmation', pass_bot=True)
bot.register_callback_query_handler(delete_deck_handler, func=lambda c: c.data == 'delete_deck', pass_bot=True)
bot.register_callback_query_handler(rename_deck_handler, func=lambda c: c.data == 'rename_deck', pass_bot=True)

bot.register_callback_query_handler(add_card_face_handler, func=lambda c: c.data == 'add_card', pass_bot=True)
bot.register_callback_query_handler(delete_card_handler, func=lambda c: c.data == 'delete_card', pass_bot=True)
bot.register_callback_query_handler(edit_card_handler, func=lambda c: c.data == 'edit_card', pass_bot=True)


bot.register_callback_query_handler(premium_handler, func=lambda c: c.data == 'premium', pass_bot=True)

bot.register_callback_query_handler(edit_card_content_handler, func=lambda c: c.data.startswith('edit_card:'), pass_bot=True)


bot.register_callback_query_handler(deck_menu_handler, func=lambda c: True, pass_bot=True)

bot.add_custom_filter(asyncio_filters.StateFilter(bot))

if __name__ == '__main__':
    asyncio.run(bot.polling())
