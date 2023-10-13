from sqlalchemy.orm import Session
from sqlalchemy import select
from postgres.init import engine
from postgres.models import User
from redis_init import redis_db
from exceptions import RedisError


def get_user_from_cache(user_id: int):
    user_id = str(user_id)
    try:
        print(user_id)
        user = redis_db.get('telebot_' + user_id)
    except Exception:
        raise RedisError('Problems with Redis')
    else:
        return user


def get_user_from_db(user_id: int):
    """
    Retrive user from datdbase
    :param user_id: user id got from user message object [telebot.types.Message]
    :return: user - if user exists, else - None
    """
    user_id = str(user_id)
    with Session(engine) as session:
        request = select(User).where(User.id == user_id)
        user = session.scalar(request)
    return user


def create_user(user_id):
    with Session(engine) as session:
        user = User(id=user_id, name='Max', is_premium=False)
        session.add(user)
        session.commit()
