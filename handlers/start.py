"""
This file defines handler called on user command '/start'.
It defines the first launch of the bot.
"""

from user.user_states import UserStates
from telebot.types import Message
from telebot.async_telebot import AsyncTeleBot
from menu.keyboard_layouts import no_decks_markup

from menu.main_menu import show_main_menu
from user.user_actions import get_user_from_db, get_user_from_cache, create_user
from bot.bot_message import BotMessages


async def start(message: Message, bot: AsyncTeleBot) -> None:
    """
    Shows greeting if user doesn't exist.
    Shows main menu if user exists.
    :param message: telebot.types.Message instance
    :param bot: bot instance
    :return: None
    """

    user_id = message.from_user.id
    user = get_user_from_cache(user_id)
    if user is None:  # There is no user in cache
        user = get_user_from_db(user_id)

        if user is None:  # There is no user in database
            create_user(message.from_user.id)
            bot_message = BotMessages.FIRST_LOGIN % (message.from_user.first_name, message.from_user.last_name)
            await bot.send_message(message.chat.id, bot_message, reply_markup=no_decks_markup)
            return None

    await bot.set_state(message.from_user.id, UserStates.menu)
    await show_main_menu(bot, message)
    return None
