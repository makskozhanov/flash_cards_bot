from sqlalchemy.orm import Session
from sqlalchemy import select
from postgres.init import engine
from postgres.models import User, Deck, Card
from exceptions import PostgresError
from redis_db.redis_init import redis_db


class DeckAction:
    """
    Base class for actions with decks
    It uses template method with 3 steps:
        1) Getting data from database
        2) Performing action with data
        3) Committing to database
    """
    def __init__(self, user_id, deck_name, bot):
        self._user_id = str(user_id)
        self._deck_name = deck_name
        self._bot = bot
        self._request = None

    def perform(self) -> None:
        """
        Perform certain action with object
        :return: None
        """
        with Session(engine) as session:
            try:
                data = session.scalar(self._request)  # step 1
            except Exception:
                raise PostgresError('Problems with Postgres')
            else:
                self._commit_action(data, session)  # step 2
                session.commit()  # step 3
                self._update_cache()

    def _update_cache(self):
        raise NotImplementedError

    def _commit_action(self, data, session):
        """
        Perform certain action with data. Redefined in subclasses
        :param data: object to be modified
        :param session: session object created via context manager
        :return: None
        """
        raise NotImplementedError


class DeleteDeck(DeckAction):
    def __init__(self, user_id, deck_name, bot):
        super().__init__(user_id, deck_name, bot)
        self._request = select(Deck).join(Deck.user).where(User.id == str(self._user_id)).where(Deck.name == str(self._deck_name))

    def _commit_action(self, data, session):
        user = session.get(User, str(self._user_id))
        user.decks.remove(data)

    def _update_cache(self):
        redis_db.hdel(self._user_id + ':decks', self._deck_name)


class CreateDeck(DeckAction):
    def __init__(self, user_id, deck_name, bot):
        super().__init__(user_id, deck_name, bot)
        self._request = select(User).where(User.id == str(self._user_id))

    def _commit_action(self, data, session):
        self._user = data
        self._deck = Deck(name=self._deck_name, deck_type='straight')
        self._user.decks.append(self._deck)

    def _update_cache(self):
        print(self._deck.id)
        redis_db.hset(self._user_id + ':decks', mapping={self._deck_name: self._deck.id})


class AddCard(DeckAction):
    def __init__(self, user_id, deck_name, bot):
        super().__init__(user_id, deck_name, bot)
        self._card_face = redis_db.hget(user_id, 'card_face')
        self._card_back = redis_db.hget(user_id, 'card_back')
        self._deck_id = redis_db.hget(self._user_id + ':decks', self._deck_name)
        self._request = select(Deck).where(Deck.id == self._deck_id)

    def _commit_action(self, data, session):
        self._deck = data
        self._card = Card(face=self._card_face, back=self._card_back)
        self._deck.cards.append(self._card)

    def _update_cache(self):
        pass


class GetCards(DeckAction):
    def __init__(self, user_id, deck_name, bot):
        super().__init__(user_id, deck_name, bot)
        self._deck_id = redis_db.hget(self._user_id + ':decks', self._deck_name)
        self._request = select(Deck).where(Deck.id == self._deck_id)

    def _commit_action(self, data, session):
        self._deck = data
        print(self._deck.cards)

    def _update_cache(self):
        for card in self._deck.cards:
            redis_db.hset(f'{self._user_id}:{self._deck_name}:{card.id}',
                          items=['face', card.face, 'back', card.back])
            redis_db.lpush(f'{self._user_id}:{self._deck_name}:cards', card.id)


def get_user_decks(user_id: any):
    with Session(engine) as session:
        request = select(User).where(User.id == str(user_id))
        try:
            user = session.scalar(request)  # step 1
        except Exception:
            raise PostgresError('Problems with Postgres')
        else:
            session.rollback()
            user_decks = {}
            for deck in user.decks:
                user_decks[deck.name] = deck.id
            return user_decks


def get_deck_name_by_id(deck_id: str):
    with Session(engine) as session:
        request = select(Deck).where(Deck.id == deck_id)
        try:
            deck = session.scalar(request)
        except Exception:
            raise PostgresError('Problems with Postgres')
        else:
            session.rollback()
            return deck.name
