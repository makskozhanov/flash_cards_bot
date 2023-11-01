"""
This file defines message handlers.
Message handler is a function that is called on user input.
"""

from user_states import UserStates
from telebot.types import Message
from telebot.async_telebot import AsyncTeleBot
from menu.keyboard_layouts import *
from deck_actions import *
from menu.menu import show_menu
from redis_db.redis_init import redis_db
from redis_db.cache_actions import SetCardFace, SetCardBack
from button_handlers import create_card_text
from utils import hide_previous_message_keyboard


async def delete_user_input(message: Message, bot: AsyncTeleBot):
    await bot.delete_message(message.chat.id, message.id)


async def create_deck(message: Message, bot: AsyncTeleBot):
    action = CreateDeck(message.from_user.id, message.text)
    action.perform()
    await bot.set_state(message.from_user.id, UserStates.menu)
    await show_menu(bot, message)


async def rename_deck(message: Message, bot: AsyncTeleBot):
    user_id = message.from_user.id
    deck_name = redis_db.hget(user_id, 'current_deck')
    new_name = message.text
    action = RenameDeck(user_id, deck_name, new_name=new_name)
    action.perform()
    await bot.set_state(user_id, UserStates.menu)
    await show_menu(bot, message)


async def add_card_face(message: Message, bot: AsyncTeleBot):
    user_id = message.from_user.id
    SetCardFace(user_id, message.text).update_cache()
    await bot.set_state(user_id, UserStates.add_card_back)

    await hide_previous_message_keyboard(user_id, message.chat.id, bot)
    current_message = await bot.send_message(message.chat.id, 'Теперь введи оборотную сторону:')
    cache.SetBotMessageId(user_id, current_message.id).update_cache()


async def add_card_back(message: Message, bot: AsyncTeleBot):
    user_id = message.from_user.id
    deck_name = redis_db.hget(user_id, 'current_deck')

    SetCardBack(user_id, message.text).update_cache()
    action = AddCard(user_id, deck_name)
    action.perform()

    await bot.set_state(user_id, UserStates.add_card_face)

    await hide_previous_message_keyboard(user_id, message.chat.id, bot)
    current_message = await bot.send_message(message.chat.id, 'Карточка добавлена', reply_markup=card_add_markup)
    cache.SetBotMessageId(user_id, current_message.id).update_cache()


async def edit_card(message: Message, bot: AsyncTeleBot):
    print(message.id)
    user_id = message.from_user.id
    deck_name = redis_db.hget(user_id, 'current_deck')
    deck_mode = redis_db.hget(user_id, 'deck_mode')
    card_id = redis_db.hget(user_id, 'id')
    side_to_edit = redis_db.hget(user_id, 'edit')
    message_to_edit = redis_db.hget(user_id, 'message_id')

    if side_to_edit == 'face':
        cache.SetCardFace(user_id, message.text).update_cache()
        action = EditCardFace(user_id, deck_name, card_id)
    else:
        cache.SetCardBack(user_id, message.text).update_cache()
        action = EditCardBack(user_id, deck_name, card_id)
    action.perform()

    reply = create_card_text(user_id, deck_mode)
    await bot.edit_message_text('<b>Карточка изменена:</b>\n' + reply, message.chat.id, message_to_edit, parse_mode='html', reply_markup=card_markup)