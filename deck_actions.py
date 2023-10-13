from sqlalchemy.orm import Session
from sqlalchemy import select

from postgres.init import engine
from postgres.models import User, Deck
from exceptions import PostgresError


class DeckAction:
    """
    Base class for actions with decks
    It uses template method with 3 steps:
        1) Getting data from database
        2) Performing action with data
        3) Committing to database
    """
    def __init__(self, user_id, deck_name, bot):
        self._user_id = user_id
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


class CreateDeck(DeckAction):
    def __init__(self, user_id, deck_name, bot):
        super().__init__(user_id, deck_name, bot)
        self._request = select(User).where(User.id == str(self._user_id))

    def _commit_action(self, data, session):
        user = data
        user.decks.append(Deck(name=self._deck_name, deck_type='straight'))


def get_user_decks(user_id: int):
    with Session(engine) as session:
        request = select(User).where(User.id == str(user_id))
        try:
            user = session.scalar(request)  # step 1
        except Exception:
            raise PostgresError('Problems with Postgres')
        else:
            session.rollback()
            return user.decks
