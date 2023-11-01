"""
This file describes functions to work with cards.
"""

from telebot.async_telebot import AsyncTeleBot
from telebot.types import CallbackQuery
from redis_db import cache_actions as cache
from menu.keyboard_layouts import *
from redis_db.init import redis_db
from exceptions import EmptyDeckError
from utils.utils import hide_previous_message_keyboard
from random import randint
from bot.bot_message import BotMessages


async def show_card(callback: CallbackQuery, bot: AsyncTeleBot) -> None:
    """
    Shows card to user.
    :param callback:
    :param bot:
    :return: None
    """
    user_id = callback.message.chat.id
    deck_name = redis_db.hget(user_id, 'current_deck')
    card_id = redis_db.lpop(f'{user_id}:{deck_name}:cards')
    deck_mode = redis_db.hget(user_id, 'deck_mode')
    try:
        cache.SetCurrentCard(user_id, deck_name, card_id).update_cache()
    except EmptyDeckError:
        await hide_previous_message_keyboard(user_id, callback.message.chat.id, bot)
        current_message = await bot.send_message(user_id, 'Мы повторили все карточки', reply_markup=end_of_deck_markup)
        cache.SetBotMessageId(user_id, current_message.id).update_cache()
    else:
        reply = create_card_text(user_id, deck_mode)
        await hide_previous_message_keyboard(user_id, callback.message.chat.id, bot)
        current_message = await bot.send_message(user_id, reply, reply_markup=card_markup, parse_mode='html')
        cache.SetBotMessageId(user_id, current_message.id).update_cache()
    finally:
        await bot.answer_callback_query(callback.id)
        return None


def create_card_text(user_id, deck_mode):
    """
    Creates content of card depending on deck mode
    :param user_id: id of the user
    :param deck_mode: defines how to show cards: face-first, back-first or random
    :return:
    """
    card_face = redis_db.hget(user_id, 'card_face')
    card_back = redis_db.hget(user_id, 'card_back')
    if deck_mode == 'back' or (deck_mode == 'random' and randint(0, 1) == 1):
        card_face, card_back = card_back, card_face
    return BotMessages.CARD_TEXT % (card_face, card_back)
