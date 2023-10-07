from sqlalchemy.ext.asyncio import create_async_engine
from config import DATABASE_ADDRESS

engine = create_async_engine(
    url=DATABASE_ADDRESS+'users',
    echo=True,
    pool_size=5,
    max_overflow=10
)

