import os

from dotenv import load_dotenv


load_dotenv('.env')

BOT_TOKEN = os.getenv('BOT_TOKEN')
OWNER = int(os.getenv('OWNER'))
DB_DSN = os.getenv('DATABASE_URL')
