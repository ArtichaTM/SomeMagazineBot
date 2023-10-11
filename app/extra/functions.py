import asyncio

from aiogram.types import Message


async def _delete_msg(delay: float, message: Message) -> None:
    await asyncio.sleep(delay)
    await message.delete()


async def delete_msg(message: Message, delay: float = 0) -> None:
    asyncio.ensure_future(_delete_msg(delay, message), loop=asyncio.get_running_loop())
