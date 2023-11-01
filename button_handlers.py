from user_states import UserStates
from redis_db.cache_actions import SetCurrentDeck
from menu.menu import show_menu
from bot_message import BotMessages
from card_actions import *


# ======================================================================================================================
# Deck Handlers

async def create_deck_handler(callback: CallbackQuery, bot: AsyncTeleBot):
    user_id = callback.from_user.id
    await bot.set_state(user_id, UserStates.create_deck)
    await bot.answer_callback_query(callback.id, text='Введи название колоды:', show_alert=True)


async def delete_deck_confirmation_handler(callback: CallbackQuery, bot: AsyncTeleBot):
    user_id = callback.from_user.id
    await bot.set_state(user_id, UserStates.delete_deck)
    await bot.answer_callback_query(callback.id)

    await hide_previous_message_keyboard(user_id, callback.message.chat.id, bot)
    current_message = await bot.send_message(callback.message.chat.id, 'Подтверди удаление', reply_markup=delete_deck_markup)
    cache.SetBotMessageId(user_id, current_message.id).update_cache()


async def delete_deck_handler(callback: CallbackQuery, bot: AsyncTeleBot):
    user_id = callback.from_user.id
    deck_name = redis_db.hget(user_id, 'current_deck')
    action = DeleteDeck(user_id, deck_name)
    action.perform()

    await bot.set_state(user_id, UserStates.menu)
    await bot.answer_callback_query(callback.id)
    await show_menu(bot, callback.message)


async def rename_deck_handler(callback: CallbackQuery, bot: AsyncTeleBot):
    user_id = callback.from_user.id
    await bot.set_state(user_id, UserStates.rename_deck)
    await bot.answer_callback_query(callback.id, text='Введи новое имя колоды:', show_alert=True)


# ======================================================================================================================
# Menu Handlers

async def deck_menu_handler(callback: CallbackQuery, bot: AsyncTeleBot):
    user_id = callback.from_user.id
    deck_name, deck_empty = get_deck_by_id(callback.data)
    if deck_empty:
        reply_markup = empty_deck_markup
        reply = 'Выбрана колода: %s \n[ПУСТАЯ]' % deck_name
    else:
        reply_markup = deck_menu_markup
        reply = 'Выбрана колода: %s' % deck_name
    SetCurrentDeck(user_id, deck_name).update_cache()

    await hide_previous_message_keyboard(user_id, callback.message.chat.id, bot)
    current_message = await bot.send_message(callback.message.chat.id, reply, reply_markup=reply_markup)
    cache.SetBotMessageId(user_id, current_message.id).update_cache()

    await bot.answer_callback_query(callback.id)


async def main_menu_handler(callback: CallbackQuery, bot: AsyncTeleBot):
    await bot.answer_callback_query(callback.id)
    await show_menu(bot, callback.message)


# ======================================================================================================================
# Learning mode Handlers

async def learn_cards_handler(callback: CallbackQuery, bot: AsyncTeleBot):
    await bot.answer_callback_query(callback.id)
    user_id = callback.from_user.id

    await hide_previous_message_keyboard(user_id, callback.message.chat.id, bot)
    current_message = await bot.send_message(callback.message.chat.id, 'Выбери режим повторения', reply_markup=learn_mode_markup)
    cache.SetBotMessageId(user_id, current_message.id).update_cache()


async def learn_mode_handler(callback: CallbackQuery, bot: AsyncTeleBot):
    user_id = callback.message.chat.id
    deck_name = redis_db.hget(user_id, 'current_deck')
    learn_mode = callback.data.split(':')[1]
    if learn_mode == 'all':
        action = GetCards(user_id, deck_name)
    elif learn_mode == 'new':
        action = GetNewCards(user_id, deck_name)
    else:
        action = GetTodayCards(user_id, deck_name)

    action.perform()
    await bot.answer_callback_query(callback.id)

    await hide_previous_message_keyboard(user_id, callback.message.chat.id, bot)
    current_message = await bot.send_message(callback.message.chat.id, 'Выбери режим колоды', reply_markup=deck_mode_markup)
    cache.SetBotMessageId(user_id, current_message.id).update_cache()


async def deck_mode_handler(callback: CallbackQuery, bot: AsyncTeleBot):
    user_id = callback.message.chat.id
    deck_mode = callback.data.split(':')[1]
    redis_db.hset(user_id, 'deck_mode', deck_mode)
    await bot.answer_callback_query(callback.id)
    await show_card(callback, bot)


# ======================================================================================================================
# Card Handlers

async def add_card_face_handler(callback: CallbackQuery, bot: AsyncTeleBot):
    user_id = callback.from_user.id
    await bot.set_state(user_id, UserStates.add_card_face)

    await hide_previous_message_keyboard(user_id, callback.message.chat.id, bot)
    current_message = await bot.send_message(callback.message.chat.id, 'Введи текст лицевой стороны карточки:')
    cache.SetBotMessageId(user_id, current_message.id).update_cache()

    await bot.answer_callback_query(callback.id)


async def delete_card_handler(callback: CallbackQuery, bot: AsyncTeleBot):
    user_id = callback.message.chat.id
    deck_name = redis_db.hget(user_id, 'current_deck')
    card_id = redis_db.hget(user_id, 'id')
    action = DeleteCard(user_id, deck_name, card_id=card_id)
    action.perform()
    await bot.answer_callback_query(callback.id, text='Карточка удалена')
    await show_card(callback, bot)


async def edit_card_handler(callback: CallbackQuery, bot: AsyncTeleBot):
    await bot.answer_callback_query(callback.id)
    await bot.edit_message_reply_markup(callback.message.chat.id, callback.message.id, reply_markup=edit_card_markup)


async def edit_card_content_handler(callback: CallbackQuery, bot: AsyncTeleBot):
    user_id = callback.from_user.id
    card_part = callback.data.split(':')[1]
    redis_db.hset(user_id, 'edit', card_part)
    redis_db.hset(user_id, 'message_id', callback.message.message_id)
    await bot.set_state(user_id, UserStates.edit_card)
    await bot.answer_callback_query(callback.id, 'Введи текст', show_alert=True)


async def repeat_card_handler(callback: CallbackQuery, bot: AsyncTeleBot):
    user_id = str(callback.message.chat.id)
    card_id = redis_db.hget(user_id, 'id')
    deck_name = redis_db.hget(user_id, 'current_deck')

    repeat_mode = callback.data.split(':')[1]

    if repeat_mode == 'tomorrow':
        period = RepetitionPeriods.DAY
        reply = BotMessages.card_repeat_tomorrow
    elif repeat_mode == 'week':
        period = RepetitionPeriods.WEEK
        reply = BotMessages.card_repeat_week
    else:
        period = RepetitionPeriods.MONTH
        reply = BotMessages.card_repeat_month

    action = IncreaseCardRepetitions(user_id, deck_name, card_id)
    action.perform()

    action = SetCardNextRepetition(user_id, deck_name, card_id, period)
    action.perform()

    await bot.answer_callback_query(callback.id, reply)
    await show_card(callback, bot)




