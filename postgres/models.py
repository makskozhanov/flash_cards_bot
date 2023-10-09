from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
from sqlalchemy import String, Integer, Boolean
from postgres.init import engine


class BaseModel(DeclarativeBase):
    pass


class User(BaseModel):
    __tablename__ = 'users'
    id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    is_premium: Mapped[bool] = mapped_column(Boolean)



BaseModel.metadata.create_all(engine)
