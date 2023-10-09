from sqlalchemy.orm import Session
from sqlalchemy import select

from postgres.init import engine
from postgres.models import User
from user_states import UserStates
from redis_init import redis_db
from exceptions import RedisError
from telebot.types import Message
from telebot.async_telebot import AsyncTeleBot
from keyboard_layouts import menu_markup


async def start(message: Message, bot: AsyncTeleBot):
    user = get_user_from_cache(str(message.from_user.id))
    if user is None:
        if is_user_exists(message.from_user.id):
            print('USER EXISTS')
        else:
            create_user(message.from_user.id)
            #await bot.set_state(message.from_user.id, UserStates.firstLogin)
    else:
        pass  # Show menu to user

    await bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name} {message.from_user.last_name}', reply_markup=menu_markup)


async def hello(message: Message, bot: AsyncTeleBot):
    from time import sleep
    sleep(3)
    await bot.send_message(message.chat.id, 'HELLO!')


def get_user_from_cache(user_id: str):
    try:
        print(user_id)
        user = redis_db.get('telebot_' + user_id)
    except Exception:
        raise RedisError('Problems with Redis')
    else:
        return user


def create_user(user_id):
    with Session(engine) as session:
        user = User(id=user_id, name='Max')
        session.add(user)
        session.commit()


def is_user_exists(user_id) -> bool:
    """
    Check existence of user in database
    :param user_id: user id got from user message object [telebot.types.Message]
    :return: True - if user exists, else - false
    """
    with Session(engine) as session:
        request = select(User).where(User.id == str(user_id))
        response = session.scalar(request)
    return response is not None
