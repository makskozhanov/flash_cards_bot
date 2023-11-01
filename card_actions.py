from telebot.async_telebot import AsyncTeleBot
from telebot.types import CallbackQuery
from deck_actions import *
from menu.keyboard_layouts import *
from redis_db.cache_actions import SetCardFace, SetCardBack, SetCardId
from redis_db.redis_init import redis_db
from exceptions import EmptyDeckError
from utils import hide_previous_message_keyboard
from random import randint
from bot_message import BotMessages


def save_current_card(user_id, deck_name):
    card_id = redis_db.lpop(f'{user_id}:{deck_name}:cards')

    if card_id is None:
        raise EmptyDeckError

    card = redis_db.hgetall(f'{user_id}:{deck_name}:{card_id}')

    SetCardFace(user_id, card['face']).update_cache()
    SetCardBack(user_id, card['back']).update_cache()
    SetCardId(user_id, object_id=card_id).update_cache()


async def show_card(callback: CallbackQuery, bot: AsyncTeleBot):
    user_id = callback.message.chat.id
    deck_name = redis_db.hget(user_id, 'current_deck')
    deck_mode = redis_db.hget(user_id, 'deck_mode')

    try:
        save_current_card(user_id, deck_name)
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


def create_card_text(user_id, deck_mode):
    card_face = redis_db.hget(user_id, 'card_face')
    card_back = redis_db.hget(user_id, 'card_back')
    if deck_mode == 'back' or (deck_mode == 'random' and randint(0, 1) == 1):
        card_face, card_back = card_back, card_face
    return BotMessages.card_text % (card_face, card_back)
