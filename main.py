import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from app.config import BOT_TOKEN
from app.handlers import get_handlers_router

async def main():
	bot = Bot(BOT_TOKEN)
	dp = Dispatcher(storage=MemoryStorage())
	dp.include_router(get_handlers_router())
	try:
		await dp.start_polling(bot)
	finally:
		await bot.session.close()

if __name__ == "__main__":
	asyncio.run(main())
