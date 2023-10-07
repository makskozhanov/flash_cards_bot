import redis
from exceptions import RedisError

redis_base = redis.StrictRedis(host='localhost', port=6379, db=0, charset='utf-8', decode_responses='True')


class User:
    def __int__(self, user_id):
        self.id = user_id


def check_user_in_cache(user_id: str):
    try:
        user = redis_base.get(user_id)
    except Exception:
        raise RedisError('Database error has occurred')
    else:
        return user
