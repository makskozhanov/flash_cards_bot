from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Boolean, ForeignKey
from postgres.init import engine
from typing import List, Dict


class BaseModel(DeclarativeBase):
    pass


class User(BaseModel):
    __tablename__ = 'users'
    id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    is_premium: Mapped[bool] = mapped_column(Boolean)
    decks: Mapped[List['Deck']] = relationship(back_populates='user', cascade='all, delete-orphan')


class Deck(BaseModel):
    __tablename__ = 'decks'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey('users.id'))
    name: Mapped[str] = mapped_column(String(300))
    deck_type: Mapped[str] = mapped_column(String(50))
    user: Mapped['User'] = relationship(back_populates='decks')


BaseModel.metadata.create_all(engine)
