import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///bot.db")
    MODEL_NAME = "sberbank-ai/rugpt3small_based_on_gpt2"

config = Config()