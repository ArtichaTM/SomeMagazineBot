from io import StringIO

from aiogram import Bot
from aiogram.types import Message

from settings import Settings


class LongMessage(StringIO):
    __slots__ = ('message', 'len')
    LIMIT = 4096

    def __init__(self, message: Message):
        super().__init__()
        self.message = message
        self.len = 0

    async def write(self, __s: str) -> None:
        self.len += len(__s)
        if self.len > self.LIMIT:
            bot: Bot = Settings['bot']
            await bot.send_message(self.message.chat.id, self.getvalue())
            self.seek(0)
            self.truncate(0)
            self.len = len(__s)
        super().write(__s)

    @classmethod
    async def autofill(cls, __s: str, limit: int = None) -> str:
        """
        :param __s: String to fill in
        :type __s: str
        :return: created string
        :rtype: str
        :param limit: Maximum amount of characters in string
        :type limit: int
        """
        if limit is None:
            limit = cls.LIMIT
        __s = __s[:limit]
        last_new_line = __s.rfind('\n')
        if last_new_line != -1:
            __s = __s[:last_new_line]
        return __s
