import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from app.config import BOT_TOKEN
from app.handlers import get_handlers_router
from service.scheduler import start_scheduler

logging.basicConfig(level=logging.INFO)

async def main():
    storage = MemoryStorage()
    bot = Bot(BOT_TOKEN)
    dp = Dispatcher(storage=storage)
    dp.include_router(get_handlers_router())
    scheduler = start_scheduler(bot)
    try:
        await dp.start_polling(bot)
    finally:
        scheduler.shutdown()
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
