from telebot.async_telebot import AsyncTeleBot
from telebot.types import CallbackQuery
from user_states import UserStates
from deck_actions import *
from menu.keyboard_layouts import deck_menu_markup, learn_mode_markup, card_markup, empty_deck_markup
from redis_db.cache_actions import SetCurrentDeck, SetCardFace, SetCardBack, SetCardId
from redis_db.redis_init import redis_db
from menu.menu import show_menu
from exceptions import EmptyDeckError
from telebot.asyncio_helper import ApiTelegramException


# ======================================================================================================================
# Deck Handlers

async def create_deck_handler(callback: CallbackQuery, bot: AsyncTeleBot):
    user_id = callback.from_user.id
    await bot.set_state(user_id, UserStates.create_deck)
    await bot.answer_callback_query(callback.id, text='Введи название колоды:', show_alert=True)


async def delete_deck_handler(callback: CallbackQuery, bot: AsyncTeleBot):
    user_id = callback.from_user.id
    await bot.set_state(user_id, UserStates.delete_deck)
    await bot.answer_callback_query(callback.id, text='Введи слово удалить:', show_alert=True)


# ======================================================================================================================
# Menu Handlers

async def deck_menu_handler(callback: CallbackQuery, bot: AsyncTeleBot):
    user_id = callback.from_user.id
    deck_name = get_deck_name_by_id(callback.data)
    SetCurrentDeck(user_id, deck_name).update_cache()
    await bot.send_message(callback.message.chat.id, 'Выбрана колода: %s' % deck_name, reply_markup=deck_menu_markup)
    await bot.delete_message(callback.message.chat.id, callback.message.id)
    await bot.answer_callback_query(callback.id)


async def show_menu_handler(callback: CallbackQuery, bot: AsyncTeleBot):
    await bot.delete_message(callback.message.chat.id, callback.message.id)
    await bot.answer_callback_query(callback.id)
    await show_menu(bot, callback.message)


# ======================================================================================================================
# Card Handlers

async def add_card_face_handler(callback: CallbackQuery, bot: AsyncTeleBot):
    user_id = callback.from_user.id
    await bot.set_state(user_id, UserStates.add_card_face)
    await bot.delete_message(callback.message.chat.id, callback.message.id)
    await bot.answer_callback_query(callback.id, text='Введи текст лицевой стороны карточки:', show_alert=True)


async def learn_cards_handler(callback: CallbackQuery, bot: AsyncTeleBot):
    await bot.delete_message(callback.message.chat.id, callback.message.id)
    await bot.answer_callback_query(callback.id)
    await bot.send_message(callback.message.chat.id, 'Выбери режим повторения', reply_markup=learn_mode_markup)


async def learn_all_words_handler(callback: CallbackQuery, bot: AsyncTeleBot):
    user_id = callback.message.chat.id
    deck_name = redis_db.hget(user_id, 'current_deck')
    action = GetCards(user_id, deck_name, bot)
    action.perform()

    await show_card(callback, bot)
    await bot.answer_callback_query(callback.id)


async def learn_new_words_handler(callback: CallbackQuery, bot: AsyncTeleBot):
    user_id = callback.message.chat.id
    deck_name = redis_db.hget(user_id, 'current_deck')
    action = GetNewCards(user_id, deck_name, bot)
    action.perform()

    await show_card(callback, bot)
    await bot.answer_callback_query(callback.id)


async def delete_card_handler(callback: CallbackQuery, bot: AsyncTeleBot):
    user_id = callback.message.chat.id
    deck_name = redis_db.hget(user_id, 'current_deck')
    card_id = redis_db.hget(user_id, 'id')
    action = DeleteCard(user_id, deck_name, bot, card_id=card_id)
    action.perform()
    await bot.answer_callback_query(callback.id, text='Карточка удалена')


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

    try:
        save_current_card(user_id, deck_name)
    except EmptyDeckError:
        await bot.send_message(user_id, 'Мы повторили все карточки', reply_markup=empty_deck_markup)
    else:
        card_face = redis_db.hget(user_id, 'card_face')
        card_back = redis_db.hget(user_id, 'card_back')
        await bot.send_message(user_id, f'{card_face}\n\n<tg-spoiler>{card_back}</tg-spoiler>', reply_markup=card_markup, parse_mode='html')
    finally:
        await bot.answer_callback_query(callback.id)
        try:
            await bot.edit_message_reply_markup(user_id, callback.message.id, reply_markup=None)
        except ApiTelegramException:
            pass


async def repeat_card_tomorrow(callback: CallbackQuery, bot: AsyncTeleBot):
    await repeat_card(callback, bot, RepetitionPeriods.DAY)
    await bot.answer_callback_query(callback.id, 'Повторим карточку завтра')
    await show_card(callback, bot)


async def repeat_card_week(callback: CallbackQuery, bot: AsyncTeleBot):
    await repeat_card(callback, bot, RepetitionPeriods.WEEK)
    await bot.answer_callback_query(callback.id, 'Повторим карточку через неделю')
    await show_card(callback, bot)


async def repeat_card_month(callback: CallbackQuery, bot: AsyncTeleBot):
    await repeat_card(callback, bot, RepetitionPeriods.MONTH)
    await bot.answer_callback_query(callback.id, 'Повторим карточку через месяц')
    await show_card(callback, bot)


async def repeat_card(callback: CallbackQuery, bot: AsyncTeleBot, period):
    user_id = str(callback.message.chat.id)
    card_id = redis_db.hget(user_id, 'id')
    deck_name = redis_db.hget(user_id, 'current_deck')

    action = IncreaseCardRepetitions(user_id, deck_name, bot, card_id)
    action.perform()

    action = SetCardNextRepetition(user_id, deck_name, bot, card_id, period)
    action.perform()

    try:
        await bot.edit_message_reply_markup(user_id, callback.message.id, reply_markup=None)
    except ApiTelegramException:
        pass


