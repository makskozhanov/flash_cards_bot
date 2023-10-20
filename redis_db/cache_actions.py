from redis_db.redis_init import redis_db


class CacheAction:
    """
    Base class for actions with cache
    """
    def __init__(self, user_id: int, value=None, object_id=None):
        self._user_id = str(user_id)
        self._value = value
        self._id = object_id

    def update_cache(self):
        raise NotImplementedError


class SetCurrentDeck(CacheAction):
    def update_cache(self):
        redis_db.hset(self._user_id, mapping={'current_deck': self._value})


class DelCurrentDeck(CacheAction):
    def update_cache(self):
        redis_db.hdel(self._user_id, 'current_deck')


class SetCardFace(CacheAction):
    def update_cache(self):
        redis_db.hset(self._user_id, mapping={'card_face': self._value})
        if self._id is not None:
            redis_db.hset(self._user_id, mapping={'id': self._id})


class SetCardBack(CacheAction):
    def update_cache(self):
        redis_db.hset(self._user_id, mapping={'card_back': self._value})
