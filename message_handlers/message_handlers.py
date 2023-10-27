import menu.menu
from user_states import UserStates
from telebot.types import Message
from telebot.async_telebot import AsyncTeleBot
from menu.keyboard_layouts import card_add_markup, empty_deck_markup
from deck_actions import DeleteDeck, CreateDeck, AddCard
from menu.menu import show_menu
from redis_db.redis_init import redis_db
from redis_db.cache_actions import DelCurrentDeck, SetCardFace, SetCardBack


async def create_deck(message: Message, bot: AsyncTeleBot):
    action = CreateDeck(message.from_user.id, message.text)
    action.perform()
    #await bot.set_state(message.from_user.id, UserStates.add_card_face)
    await bot.set_state(message.from_user.id, UserStates.menu)
    await bot.send_message(message.chat.id, f'Колода {message.text} создана', reply_markup=empty_deck_markup)
    await menu.menu.show_menu(bot, message)


async def delete_deck(message: Message, bot: AsyncTeleBot):
    user_id = message.from_user.id
    deck_name = redis_db.hget(user_id, 'current_deck')

    if message.text.lower() == 'удалить':
        action = DeleteDeck(user_id, deck_name)
        action.perform()
        DelCurrentDeck(user_id).update_cache()
        await bot.set_state(user_id, UserStates.menu)
        await show_menu(bot, message)


async def add_card_face(message: Message, bot: AsyncTeleBot):
    user_id = message.from_user.id
    SetCardFace(user_id, message.text).update_cache()
    await bot.set_state(user_id, UserStates.add_card_back)
    await bot.send_message(message.chat.id, 'Теперь введи оборотную сторону:')


async def add_card_back(message: Message, bot: AsyncTeleBot):
    user_id = message.from_user.id
    deck_name = redis_db.hget(user_id, 'current_deck')

    SetCardBack(user_id, message.text).update_cache()
    action = AddCard(user_id, deck_name)
    action.perform()

    await bot.set_state(user_id, UserStates.add_card_more)
    await bot.send_message(message.chat.id, 'Карточка добавлена', reply_markup=card_add_markup)




