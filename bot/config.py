import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    GIGACHAT_API_KEY = os.getenv("GIGACHAT_API_KEY")
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///bot.db")

config = Config()