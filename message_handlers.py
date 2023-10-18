from user_states import UserStates
from telebot.types import Message
from telebot.async_telebot import AsyncTeleBot
from menu.keyboard_layouts import no_decks_markup, card_add_markup
from deck_actions import DeleteDeck, CreateDeck
from menu.menu import show_menu
from user_actions import get_user_from_db, get_user_from_cache, create_user
from bot_message import BotMessages
from redis_db.redis_init import redis_db
from redis_db.cache_actions import DelCurrentDeck, SetCardFace


from sqlalchemy.orm import Session
from sqlalchemy import select
from postgres.init import engine
from postgres.models import User, Deck, Card
from exceptions import PostgresError


async def start(message: Message, bot: AsyncTeleBot):
    user_id = message.from_user.id
    user = get_user_from_cache(user_id)
    if user is None:  # There is no user in cache
        user = get_user_from_db(user_id)

        if user is None:  # There is no user in database
            create_user(message.from_user.id)
            bot_message = BotMessages.first_login % (message.from_user.first_name, message.from_user.last_name)
            await bot.send_message(message.chat.id, bot_message, reply_markup=no_decks_markup)
        else:  # There is user in database, not in cache
            await bot.set_state(message.from_user.id, UserStates.menu)
            await show_menu(bot, message)

    else:  # There is user in cache
        await bot.set_state(message.from_user.id, UserStates.menu)
        await show_menu(bot, message)


async def create_deck(message: Message, bot: AsyncTeleBot):
    action = CreateDeck(message.from_user.id, message.text, bot)
    action.perform()
    await bot.set_state(message.from_user.id, UserStates.add_card_face)
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


async def add_card_face(message: Message, bot: AsyncTeleBot):
    user_id = message.from_user.id
    SetCardFace(user_id, message.text).update_cache()
    await bot.set_state(user_id, UserStates.add_card_back)
    await bot.send_message(message.chat.id, 'Теперь введи оборотную сторону:')


async def add_card_back(message: Message, bot: AsyncTeleBot):
    user_id = message.from_user.id
    card_face = redis_db.hget(user_id, 'card_face')
    card_back = message.text
    current_deck = redis_db.hget(str(user_id), 'current_deck')
    current_deck_id = redis_db.hget(str(user_id) + ':decks', current_deck)

    print(current_deck_id)
    with Session(engine) as session:
        request = select(Deck).where(Deck.id == current_deck_id)
        try:
            deck = session.scalar(request)
        except Exception:
            raise PostgresError('Problems with Postgres')
        else:
            card = Card(face=card_face, back=card_back)
            deck.cards.append(card)
            session.commit()

    await bot.set_state(user_id, UserStates.add_card_more)
    await bot.send_message(message.chat.id, 'Карточка добавлена', reply_markup=card_add_markup)




