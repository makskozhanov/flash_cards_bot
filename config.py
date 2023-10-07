import os
from dotenv import load_dotenv
from enum import Enum

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')


class PostgresConf(Enum):
    HOST = os.getenv('POSTGRES_HOST')
    USER = os.getenv('POSTGRES_USER')
    PASSWORD = os.getenv('POSTGRES_PASSWORD')
    ADDRESS = ''.join(('postgresql+asyncpg://', USER, ':', PASSWORD, '@', HOST, '/'))


class RedisConf(Enum):
    HOST = os.getenv('REDIS_HOST')
    PORT = os.getenv('REDIS_PORT')
    DB = os.getenv('REDIS_DB')


