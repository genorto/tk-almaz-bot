import os

from dotenv import load_dotenv

from db.database import Database


class ConfigException(Exception):
    def __init__(self, msg: str) -> None:
        super().__init__(msg)

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if BOT_TOKEN is None:
    raise ConfigException("No bot token in .env")

API_KEY = os.getenv("API_KEY")
if API_KEY is None:
    raise ConfigException("No api key in .env")

API_URL = "https://parser-api.com/parser/transport_mos_api"
PLATES_PER_PAGE = 3

db = Database("bot.sqlite")
