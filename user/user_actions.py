"""
This file defines actions on users such as: create new user, get user from cache or database.
"""

from sqlalchemy.orm import Session
from sqlalchemy import select
from postgres.init import ENGINE
from postgres.models import User
from redis_db.init import redis_db
from exceptions import RedisError


def get_user_from_cache(user_id: int):
    user_id = str(user_id)
    try:
        user = redis_db.get('telebot_' + user_id)
    except Exception:
        raise RedisError('Problems with Redis')
    else:
        return user


def get_user_from_db(user_id: int):
    """
    Retrieve user from database
    :param user_id: user id got from user message object [telebot.types.Message]
    :return: user - if user exists, else - None
    """
    user_id = str(user_id)
    with Session(ENGINE) as session:
        request = select(User).where(User.id == user_id)
        user = session.scalar(request)
    return user


def create_user(user_id):
    with Session(ENGINE) as session:
        user = User(id=user_id, name='Max', is_premium=False)
        session.add(user)
        session.commit()
