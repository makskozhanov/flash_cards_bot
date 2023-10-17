from user_states import UserStates
from telebot.types import Message
from telebot.async_telebot import AsyncTeleBot
from menu.keyboard_layouts import first_login_markup
from deck_actions import DeleteDeck, CreateDeck
from menu.menu import show_menu
from user_actions import get_user_from_db, get_user_from_cache, create_user
from bot_message import BotMessages
from redis_db.redis_init import redis_db
from redis_db.cache_actions import DelCurrentDeck


async def start(message: Message, bot: AsyncTeleBot):
    user_id = message.from_user.id
    user = get_user_from_cache(user_id)
    if user is None:  # There is no user in cache
        user = get_user_from_db(user_id)

        if user is None:  # There is no user in database
            create_user(message.from_user.id)
            bot_message = BotMessages.first_login % (message.from_user.first_name, message.from_user.last_name)
            await bot.send_message(message.chat.id, bot_message, reply_markup=first_login_markup)
        else:  # There is user in database, not in cache
            await bot.set_state(message.from_user.id, UserStates.menu)
            await show_menu(bot, message)

    else:  # There is user in cache
        await bot.set_state(message.from_user.id, UserStates.menu)
        await show_menu(bot, message)


async def create_deck(message: Message, bot: AsyncTeleBot):
    action = CreateDeck(message.from_user.id, message.text, bot)
    action.perform()
    await bot.set_state(message.from_user.id, UserStates.add_card)
    await bot.send_message(message.chat.id, message.text)


async def delete_deck(message: Message, bot: AsyncTeleBot):
    user_id = message.from_user.id
    deck_name = redis_db.hget(user_id, 'current_deck')

    if message.text.lower() == 'удалить':
        action = DeleteDeck(user_id, deck_name, bot)
        action.perform()
        DelCurrentDeck(user_id).update_cache()
        await bot.set_state(user_id, UserStates.menu)
        await show_menu(bot, message)


async def add_card(message: Message, bot: AsyncTeleBot):
    await bot.send_message(message.chat.id, 'ADD CARD')




