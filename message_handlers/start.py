from user_states import UserStates
from telebot.types import Message
from telebot.async_telebot import AsyncTeleBot
from menu.keyboard_layouts import no_decks_markup

from menu.menu import show_menu
from user_actions import get_user_from_db, get_user_from_cache, create_user
from bot_message import BotMessages


async def start(message: Message, bot: AsyncTeleBot):
    user_id = message.from_user.id
    user = get_user_from_cache(user_id)
    if user is None:  # There is no user in cache
        user = get_user_from_db(user_id)

        if user is None:  # There is no user in database
            create_user(message.from_user.id)
            bot_message = BotMessages.first_login % (message.from_user.first_name, message.from_user.last_name)
            await bot.send_message(message.chat.id, bot_message, reply_markup=no_decks_markup)
        else:  # There is user in database, not in cache
            await bot.set_state(message.from_user.id, UserStates.menu)
            await show_menu(bot, message)

    else:  # There is user in cache
        await bot.set_state(message.from_user.id, UserStates.menu)
        await show_menu(bot, message)
