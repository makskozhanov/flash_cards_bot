from telebot.async_telebot import AsyncTeleBot
from telebot.types import CallbackQuery
from user_states import UserStates
from deck_actions import get_deck_name_by_id
from menu.keyboard_layouts import deck_menu_markup
from redis_db.cache_actions import SetCurrentDeck


async def create_deck_handler(callback: CallbackQuery, bot: AsyncTeleBot):
    user_id = callback.from_user.id
    await bot.set_state(user_id, UserStates.create_deck)
    await bot.answer_callback_query(callback.id, text='Введи название колоды:', show_alert=True)


async def delete_deck_handler(callback: CallbackQuery, bot: AsyncTeleBot):
    user_id = callback.from_user.id
    await bot.set_state(user_id, UserStates.delete_deck)
    await bot.answer_callback_query(callback.id, text='Введи слово удалить:', show_alert=True)


async def deck_menu_handler(callback: CallbackQuery, bot: AsyncTeleBot):
    user_id = callback.from_user.id
    deck_name = get_deck_name_by_id(callback.data)
    SetCurrentDeck(user_id, deck_name).update_cache()
    await bot.send_message(callback.message.chat.id, 'Выбрана колода: %s' % deck_name, reply_markup=deck_menu_markup)
    await bot.answer_callback_query(callback.id)

