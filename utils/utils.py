"""
This file defines auxiliary functions.
"""

from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_helper import ApiTelegramException
from redis_db.init import redis_db
from user.user_states import UserStates
from redis_db.cache_actions import SetBotMessageId


async def hide_previous_message_keyboard(user_id, chat_id, bot: AsyncTeleBot):
    message_to_edit = redis_db.hget(user_id, 'bot_message_id')
    if message_to_edit is not None:
        try:
            await bot.edit_message_reply_markup(chat_id, int(message_to_edit), reply_markup=None)
        except ApiTelegramException:
            pass


def message_too_long(message: str) -> bool:
    return len(message) > 3000


async def stop_handling_message(bot, message):
    await bot.set_state(message.from_user.id, UserStates.menu)
    await hide_previous_message_keyboard(message.from_user.id, message.chat.id, bot)
    current_message = await bot.send_message(message.chat.id, 'Текст должен быть не длиннее 3000 символов.')
    SetBotMessageId(message.from_user.id, current_message.id).update_cache()
