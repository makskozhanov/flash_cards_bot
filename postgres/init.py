from sqlalchemy import create_engine
from config import PostgresConf


engine = create_engine(
    url=str(PostgresConf.ADDRESS.value) + 'users',
    echo=True,
    pool_size=5,
    max_overflow=10
)






