import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv('.env')

BASE_DIR = Path(__file__).resolve().parent

BOT_TOKEN = os.getenv('BOT_TOKEN')
OWNER = int(os.getenv('OWNER'))
DB_DSN = os.getenv('DATABASE_URL')
TEST_DB_DSN = os.getenv('TEST_DATABASE_URL')
