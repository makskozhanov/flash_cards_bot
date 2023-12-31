"""
This file establishes SQLAlchemy models, which serve as representations of both PostgreSQL tables and Python objects.
"""

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Boolean, ForeignKey, Date
from postgres.init import ENGINE
from typing import List, Optional


class BaseModel(DeclarativeBase):
    pass


class User(BaseModel):
    """
    Represents user entity.
    """
    __tablename__ = 'users'
    id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    is_premium: Mapped[bool] = mapped_column(Boolean, default=False)
    decks: Mapped[List['Deck']] = relationship(back_populates='user', cascade='all, delete-orphan')


class Deck(BaseModel):
    """
    Represents deck entity.
    """
    __tablename__ = 'decks'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey('users.id'))
    name: Mapped[str] = mapped_column(String(300))
    empty: Mapped[bool] = mapped_column(Boolean, default=True)
    user: Mapped['User'] = relationship(back_populates='decks')
    cards: Mapped[List['Card']] = relationship(back_populates='deck', cascade='all, delete-orphan')


class Card(BaseModel):
    """
    Represents card entity.
    """
    __tablename__ = 'cards'
    id: Mapped[int] = mapped_column(primary_key=True)
    deck_id: Mapped[str] = mapped_column(ForeignKey('decks.id'))
    face: Mapped[str] = mapped_column(String(3000))
    back: Mapped[str] = mapped_column(String(3000))
    next_repetition: Mapped[Optional[str]] = mapped_column(Date, default=None)
    repetitions: Mapped[int] = mapped_column(Integer, default=0)
    deck: Mapped['Deck'] = relationship(back_populates='cards')


BaseModel.metadata.create_all(ENGINE)
