from sqlalchemy.ext.asyncio import create_async_engine
from config import PostgresConf

engine = create_async_engine(
    url=str(PostgresConf.ADDRESS.value) + 'users',
    echo=True,
    pool_size=5,
    max_overflow=10
)


