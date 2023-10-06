# Python imports
import asyncio
import logging
import sys
from os import getenv

# Libraries imports
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

# App Imports
from db import db_init
from states import router
from settings import Settings

TOKEN = getenv("BOT_TOKEN")

# All handlers should be attached to the Router (or Dispatcher)
dp = Dispatcher()
dp.include_router(router)


async def main() -> None:
    db_init()
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    Settings['bot'] = bot
    Settings['products_limit'] = 9
    Settings['orders_limit'] = 9
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
    asyncio.run(main())
