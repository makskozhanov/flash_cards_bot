"""
This file defines actions with Redis cache.
"""

from redis_db.redis_init import redis_db
from exceptions import EmptyDeckError


class CacheAction:
    """
    Base class for actions with cache.
    Subclasses redefines update_cache() method.
    """
    def __init__(self, user_id: any, value: any = None, object_id: any = None):
        self._user_id = str(user_id)
        self._value = str(value)
        self._object_id = str(object_id)

    def update_cache(self):
        raise NotImplementedError


class DeleteDeck(CacheAction):
    """
    Deletes deck from cache.
    """
    def update_cache(self):
        redis_db.hdel(self._user_id + ':decks', self._value)


class AddDeck(CacheAction):
    """
    Adds deck to cache.
    """
    def update_cache(self):
        redis_db.hset(self._user_id + ':decks', mapping={self._value: self._object_id})


class SetCurrentDeck(CacheAction):
    """
    Sets current deck, which user have chose.
    """
    def update_cache(self):
        redis_db.hset(self._user_id, mapping={'current_deck': self._value})


class DelCurrentDeck(CacheAction):
    """
    Deletes current deck.
    """
    def update_cache(self):
        redis_db.hdel(self._user_id, 'current_deck')


class ClearWordsToRepeat(CacheAction):
    """
    Clear list of words that was selected to be repeated.
    """
    def update_cache(self):
        redis_db.delete(f'{self._user_id}:{self._value}:cards')  # Clear list of words to repeat


class SetCardFace(CacheAction):
    """
    Sets card face in cache when user creates or edit card.
    """
    def update_cache(self):
        redis_db.hset(self._user_id, mapping={'card_face': self._value})


class SetCardBack(CacheAction):
    """
    Sets card back in cache when user creates or edit card.
    """
    def update_cache(self):
        redis_db.hset(self._user_id, mapping={'card_back': self._value})


class SetCardId(CacheAction):
    """
    Sets card id in cache.
    """
    def update_cache(self):
        redis_db.hset(self._user_id, mapping={'id': self._object_id})


class SetBotMessageId(CacheAction):
    """
    Sets last bot message id in order to edit its keyboard in the future.
    """
    def update_cache(self):
        redis_db.hset(self._user_id, mapping={'bot_message_id': self._value})


class SetCurrentCard(CacheAction):
    def update_cache(self):
        print(self._user_id, self._value, self._object_id)
        if self._object_id == 'None':
            raise EmptyDeckError

        card = redis_db.hgetall(f'{self._user_id}:{self._value}:{self._object_id}')
        SetCardFace(self._user_id, card['face']).update_cache()
        SetCardBack(self._user_id, card['back']).update_cache()
        SetCardId(self._user_id, object_id=self._object_id).update_cache()
