"""
This file defines actions with decks and cards, related to database,
such as create, delete, rename or edit.
"""

from sqlalchemy.orm import Session
from sqlalchemy import select, ScalarResult
from postgres.init import ENGINE
from postgres.models import User, Deck, Card
from exceptions import PostgresError
from redis_db.init import redis_db
from datetime import date, timedelta
from enum import Enum
from typing import Protocol
from redis_db.cache_actions import RemoveDeck, DelCurrentDeck, AddDeck, ClearWordsToRepeat


class RepetitionPeriods(Enum):
    DAY = timedelta(days=1)
    WEEK = timedelta(days=7)
    MONTH = timedelta(days=30)


class Action(Protocol):
    """
    Interface for actions with postgres
    """

    def perform(self) -> None:
        raise NotImplementedError


class BaseAction:
    """
    Base class for actions with database
    """

    def perform(self) -> None:
        """
        Perform given action with object
        :return: None
        """
        with Session(ENGINE) as self._session:
            try:
                data = self._get_data()
            except Exception:
                raise PostgresError('Problems with Postgres')
            else:
                try:
                    self._commit_action(data)  # step 2
                except NotImplementedError:
                    pass
                else:
                    self._session.commit()  # step 3
                try:
                    self._update_cache()  # step 4
                except NotImplementedError:
                    pass

    def _update_cache(self) -> None:
        """
        Updates Redis cache after operations with Postgres
        :return: None
        """
        raise NotImplementedError

    def _commit_action(self, data):
        """
        Perform certain action with data. Redefined in subclasses
        :return: None
        """
        raise NotImplementedError

    def _get_data(self):
        raise NotImplementedError


# ======================================================================================================================
# Deck Actions

class DeckAction(BaseAction):
    """
    Base class for actions with decks
    It uses template method with 4 steps:
        1) Getting data from database
        2) Performing action with data
        3) Committing to database
        4) Updating cache
    """
    def __init__(self, user_id: any = None, deck_name: any = None, **kwargs) -> None:
        self._user_id = str(user_id)
        self._deck_name = str(deck_name)
        self._deck_id = redis_db.hget(self._user_id + ':decks', self._deck_name)
        self._kwargs = kwargs


class DeleteDeck(DeckAction):
    def __init__(self, user_id, deck_name):
        super().__init__(user_id, deck_name)
        self._request = select(Deck).join(Deck.user).where(User.id == self._user_id).where(Deck.name == self._deck_name)

    def _get_data(self):
        return self._session.scalar(self._request)

    def _commit_action(self, data: Deck) -> None:
        """
        Deletes deck form database
        :return: None
        """
        deck = data
        user = self._session.get(User, self._user_id)
        user.decks.remove(deck)

    def _update_cache(self) -> None:
        """
        Deletes deck from cache
        :return: None
        """
        RemoveDeck(self._user_id, self._deck_name).update_cache()
        DelCurrentDeck(self._user_id).update_cache()


class CreateDeck(DeckAction):
    def __init__(self, user_id, deck_name):
        super().__init__(user_id, deck_name)
        self._request = select(User).where(User.id == self._user_id)

    def _get_data(self):
        return self._session.scalar(self._request)

    def _commit_action(self, data: User) -> None:
        """
        Inserts new deck in database
        :return: None
        """
        user = data
        self._deck = Deck(name=self._deck_name)
        user.decks.append(self._deck)

    def _update_cache(self) -> None:
        """
        Inserts deck into cache
        :return: None
        """
        AddDeck(self._user_id, self._deck_name, self._deck.id).update_cache()


class GetDecks(DeckAction):
    def __init__(self, user_id):
        super().__init__(user_id)
        self._request = select(Deck).where(Deck.user_id == self._user_id)

    def _get_data(self):
        return self._session.scalars(self._request).all()

    def _commit_action(self, data: ScalarResult):
        self._decks = data

    def _update_cache(self) -> None:
        for deck in self._decks:
            AddDeck(self._user_id, deck.name, deck.id).update_cache()


class RenameDeck(DeckAction):
    def __init__(self, user_id, deck_name, new_name):
        super().__init__(user_id, deck_name, new_name=new_name)
        self._request = select(Deck).where(Deck.id == self._deck_id)

    def _get_data(self):
        return self._session.scalar(self._request)

    def _commit_action(self, data: Deck):
        deck = data
        self._new_name = self._kwargs.get('new_name')
        deck.name = self._new_name

    def _update_cache(self) -> None:
        redis_db.hdel(self._user_id + ':decks', self._deck_name)
        redis_db.hset(self._user_id + ':decks', self._new_name, self._deck_id)


# ======================================================================================================================
# Card Actions

class CardAction(BaseAction):
    """
       Base class for actions with cards
       It uses template method with 4 steps:
           1) Getting data from database
           2) Performing action with data
           3) Committing to database
           4) Updating cache
       """

    def __init__(self, user_id: any, deck_name: any, card_id: any = None) -> None:
        super().__init__()
        self._user_id = str(user_id)
        self._deck_name = str(deck_name)
        self._card_id = str(card_id)
        self._card_face = redis_db.hget(self._user_id, 'card_face')
        self._card_back = redis_db.hget(self._user_id, 'card_back')
        self._deck_id = redis_db.hget(self._user_id + ':decks', self._deck_name)


class AddCard(CardAction):
    def __init__(self, user_id, deck_name):
        super().__init__(user_id, deck_name)
        self._request = select(Deck).where(Deck.id == self._deck_id)

    def _get_data(self):
        return self._session.scalar(self._request)

    def _commit_action(self, data: Deck):
        self._card = Card(face=self._card_face, back=self._card_back)
        deck = data
        deck.empty = False
        deck.cards.append(self._card)


class DeleteCard(CardAction):
    def __init__(self, user_id, deck_name, card_id):
        super().__init__(user_id, deck_name, card_id)
        self._request = select(Deck).where(Deck.id == self._deck_id)

    def _get_data(self):
        return self._session.scalar(self._request)

    def _commit_action(self, data: Deck):
        card = self._session.get(Card, str(self._card_id))
        try:
            deck = data
            deck.cards.remove(card)
            if len(deck.cards) == 0:
                deck.empty = True
        except ValueError:
            pass  # Карточка уже удалена

    def _update_cache(self):
        if redis_db.exists(f'{self._user_id}:{self._deck_name}:{self._card_id}'):
            redis_db.delete(f'{self._user_id}:{self._deck_name}:{self._card_id}')


class EditCard(CardAction):
    def __init__(self, user_id, deck_name, card_id):
        super().__init__(user_id, deck_name, card_id)
        self._request = select(Card).where(Card.id == self._card_id).where(Card.deck_id == self._deck_id)

    def _get_data(self):
        return self._session.scalar(self._request)


class EditCardFace(EditCard):
    def _commit_action(self, data: Card):
        self._card = data
        self._card.face = self._card_face

    def _update_cache(self) -> None:
        redis_db.hset(f'{self._user_id}:{self._deck_name}:{self._card_id}', 'face', self._card_face)


class EditCardBack(EditCard):
    def _commit_action(self, data: Card):
        self._card = data
        self._card.back = self._card_back

    def _update_cache(self) -> None:
        redis_db.hset(f'{self._user_id}:{self._deck_name}:{self._card_id}', 'back', self._card_back)


class GetCards(DeckAction):
    def __init__(self, user_id, deck_name):
        super().__init__(user_id, deck_name)
        self._request = select(Card).where(Card.deck_id == self._deck_id)

    def _get_data(self):
        return self._session.scalars(self._request).all()

    def _commit_action(self, data: ScalarResult):
        self._cards = data

    def _update_cache(self):
        ClearWordsToRepeat(self._user_id, self._deck_name).update_cache()
        for card in self._cards:
            self._add_card_to_repetition_list(card)

    def _push_card_to_cache(self, card):
        redis_db.hset(f'{self._user_id}:{self._deck_name}:{card.id}',
                      items=['face', card.face, 'back', card.back, 'repetitions', card.repetitions, 'next_repetition',
                             str(card.next_repetition)])
        redis_db.expire(f'{self._user_id}:{self._deck_name}:{card.id}', 1200)

    def _add_card_to_repetition_list(self, card):
        redis_db.lpush(f'{self._user_id}:{self._deck_name}:cards', card.id)  # Create new list of words to repeat


class GetNewCards(GetCards):
    def __init__(self, user_id, deck_name):
        super().__init__(user_id, deck_name)
        self._request = select(Card).where(Card.repetitions < 5).where(Card.deck_id == self._deck_id)


class GetTodayCards(GetCards):
    def __init__(self, user_id, deck_name):
        super().__init__(user_id, deck_name)
        self._request = select(Card).where(Card.next_repetition == date.today())


class AddCardsToCache(GetCards):
    def __init__(self, user_id, deck_name, card_id):
        super().__init__(user_id, deck_name)
        self._card_id = card_id
        self.card_list = redis_db.lrange(f'{self._user_id}:{self._deck_name}:cards', 0, 3)
        self.card_list.append(self._card_id)
        self._request = select(Card).where(Card.id.in_(self.card_list))

    def _get_data(self):
        return self._session.scalars(self._request).all()

    def _commit_action(self, data: ScalarResult):
        self._cards = data

    def _update_cache(self):
        for card in self._cards:
            self._push_card_to_cache(card)


class IncreaseCardRepetitions(CardAction):
    def __init__(self, user_id, deck_name, card_id):
        super().__init__(user_id, deck_name, card_id)
        self._request = select(Card).where(Card.id == card_id).where(Card.deck_id == self._deck_id)

    def _get_data(self):
        return self._session.scalar(self._request)

    def _commit_action(self, data: Card):
        self._card = data
        self._card.repetitions += 1

    def _update_cache(self):
        redis_db.hset(f'{self._user_id}:{self._deck_name}:{self._card.id}', 'repetitions', self._card.repetitions)


class SetCardNextRepetition(CardAction):
    def __init__(self, user_id, deck_name, card_id, period):
        super().__init__(user_id, deck_name, card_id)
        self._period = period.value
        self._request = select(Card).where(Card.id == card_id).where(Card.deck_id == self._deck_id)

    def _get_data(self):
        return self._session.scalar(self._request)

    def _commit_action(self, data: Card):
        self._card = data
        if self._card.next_repetition is not None:
            self._card.next_repetition += self._period
        else:
            self._card.next_repetition = date.today()

    def _update_cache(self):
        redis_db.hset(f'{self._user_id}:{self._deck_name}:{self._card.id}', 'next_repetition',
                      str(self._card.next_repetition))


def get_deck_by_id(deck_id: str):
    with Session(ENGINE) as session:
        request = select(Deck).where(Deck.id == deck_id)
        try:
            deck = session.scalar(request)
        except Exception:
            raise PostgresError('Problems with Postgres')
        else:
            session.rollback()
            return deck.name, deck.empty
