from telebot.async_telebot import AsyncTeleBot
from telebot.types import CallbackQuery
from user_states import UserStates
from deck_actions import get_deck_name_by_id, GetCards
from menu.keyboard_layouts import deck_menu_markup, learn_mode_markup, card_learn_markup, next_card_markup, empty_deck_markup
from redis_db.cache_actions import SetCurrentDeck, SetCardFace, SetCardBack
from redis_db.redis_init import redis_db
from menu.menu import show_menu
from exceptions import EmptyDeckError


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


async def add_card_face_handler(callback: CallbackQuery, bot: AsyncTeleBot):
    user_id = callback.from_user.id
    await bot.set_state(user_id, UserStates.add_card_face)
    await bot.answer_callback_query(callback.id, text='Введи текст лицевой стороны карточки:', show_alert=True)


async def show_menu_handler(callback: CallbackQuery, bot: AsyncTeleBot):
    await bot.answer_callback_query(callback.id)
    await show_menu(bot, callback.message)


async def learn_cards_handler(callback: CallbackQuery, bot: AsyncTeleBot):
    await bot.answer_callback_query(callback.id)
    await bot.send_message(callback.message.chat.id, 'Выбери режим повторения', reply_markup=learn_mode_markup)


async def learn_all_handler(callback: CallbackQuery, bot: AsyncTeleBot):
    user_id = callback.message.chat.id
    deck_name = redis_db.hget(user_id, 'current_deck')
    action = GetCards(user_id, deck_name, bot)
    action.perform()

    save_current_card(user_id, deck_name)

    await show_card_face(callback, bot)
    await bot.answer_callback_query(callback.id)


def save_current_card(user_id, deck_name):
    card_id = redis_db.lpop(f'{user_id}:{deck_name}:cards')
    if card_id is None:
        raise EmptyDeckError
    card = redis_db.hgetall(f'{user_id}:{deck_name}:{card_id}')
    SetCardFace(user_id, card['face']).update_cache()
    SetCardBack(user_id, card['back']).update_cache()


async def show_card_face(callback: CallbackQuery, bot: AsyncTeleBot):
    user_id = callback.message.chat.id
    card_face = redis_db.hget(user_id, 'card_face')
    await bot.send_message(user_id, card_face, reply_markup=card_learn_markup)
    await bot.answer_callback_query(callback.id)


async def show_card_back(callback: CallbackQuery, bot: AsyncTeleBot):
    await bot.answer_callback_query(callback.id)
    user_id = callback.message.chat.id
    deck_name = redis_db.hget(user_id, 'current_deck')
    card_back = redis_db.hget(user_id, 'card_back')

    try:
        save_current_card(user_id, deck_name)
    except EmptyDeckError:
        await bot.send_message(user_id, 'Мы повторили все карточки', reply_markup=empty_deck_markup)
    else:
        await bot.send_message(user_id, card_back, reply_markup=next_card_markup)

