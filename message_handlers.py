from user_states import UserStates
from redis_init import redis_db
from exceptions import RedisError
from telebot.types import Message
from telebot.async_telebot import AsyncTeleBot


async def start(message: Message, bot: AsyncTeleBot):
    state = check_user_state(str(message.from_user.id))
    print(state)
    if state is None:
        pass  # Create new user in Postrgres
        await bot.set_state(message.from_user.id, UserStates.firstLogin)
    else:
        pass  # Show menu to user

    await bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name} {message.from_user.last_name}')


async def hello(message: Message, bot: AsyncTeleBot):
    await bot.send_message(message.chat.id, 'HELLO!')


def check_user_state(user_id: str):
    try:
        print(user_id)
        state = redis_db.get('telebot_' + user_id)
    except Exception:
        raise RedisError('Problems with Redis')
    else:
        return state
