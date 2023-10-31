from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_helper import ApiTelegramException
from redis_db.redis_init import redis_db


async def hide_previous_message_keyboard(user_id, chat_id, bot: AsyncTeleBot):
    message_to_edit = redis_db.hget(user_id, 'bot_message_id')
    if message_to_edit is not None:
        try:
            await bot.edit_message_reply_markup(chat_id, int(message_to_edit), reply_markup=None)
        except ApiTelegramException:
            pass
