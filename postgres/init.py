"""
This document generates a SQLAlchemy engine using the provided parameters.
"""

from sqlalchemy import create_engine
from config import PostgresConf


ENGINE = create_engine(
    url=str(PostgresConf.ADDRESS.value) + 'users',
    echo=True,
    pool_size=5,
    max_overflow=10
)
