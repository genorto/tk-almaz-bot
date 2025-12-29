import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
PASSWORD = os.getenv("PASSWORD")
API_KEY = os.getenv("API_KEY")
API_URL = "https://parser-api.com/parser/transport_mos_api"
WHITELIST_PATH = "whitelist.json"
