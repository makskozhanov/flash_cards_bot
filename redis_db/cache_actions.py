from redis_db.redis_init import redis_db


class CacheAction:
    """
    Base class for actions with cache
    """
    def __init__(self, user_id: any, value: any = None, object_id: any = None):
        self._user_id = str(user_id)
        self._value = str(value)
        self._object_id = str(object_id)

    def update_cache(self):
        raise NotImplementedError


class DeleteDeck(CacheAction):
    def update_cache(self):
        redis_db.hdel(self._user_id + ':decks', self._value)


class AddDeck(CacheAction):
    def update_cache(self):
        redis_db.hset(self._user_id + ':decks', mapping={self._value: self._object_id})


class SetCurrentDeck(CacheAction):
    def update_cache(self):
        redis_db.hset(self._user_id, mapping={'current_deck': self._value})


class DelCurrentDeck(CacheAction):
    def update_cache(self):
        redis_db.hdel(self._user_id, 'current_deck')


class ClearWordsToRepeat(CacheAction):
    def update_cache(self):
        redis_db.delete(f'{self._user_id}:{self._value}:cards')  # Clear list of words to repeat


class SetCardFace(CacheAction):
    def update_cache(self):
        redis_db.hset(self._user_id, mapping={'card_face': self._value})


class SetCardBack(CacheAction):
    def update_cache(self):
        redis_db.hset(self._user_id, mapping={'card_back': self._value})


class SetCardId(CacheAction):
    def update_cache(self):
        redis_db.hset(self._user_id, mapping={'id': self._object_id})


