"""
This file defines a Redis client instance.
"""

import redis
from config import RedisConf

redis_db = redis.StrictRedis(
    host=RedisConf.HOST.value,
    port=RedisConf.PORT.value,
    db=RedisConf.DB.value,
    charset='utf-8',
    decode_responses=True
)
