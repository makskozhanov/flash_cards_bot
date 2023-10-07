import os
from dotenv import load_dotenv
load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
DATABASE_ADDRESS = ''.join(
    (
        'postgresql+asyncpg://',
        os.getenv('DB_USER'),
        ':',
        os.getenv('DB_PASSWORD'),
        '@',
        os.getenv('DB'),
        '/'
    )
)
