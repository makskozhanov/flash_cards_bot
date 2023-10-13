from telebot.async_telebot import AsyncTeleBot
from telebot.types import CallbackQuery
from user_states import UserStates


async def create_deck_handler(callback: CallbackQuery, bot: AsyncTeleBot):

    user_id = callback.from_user.id
    await bot.set_state(user_id, UserStates.create_deck)
    await bot.answer_callback_query(callback.id, text='Введи название колоды:', show_alert=True)

