import os
import typing as t

import dotenv
import hikari
import lightbulb
import miru

from core.database import Database, create_database


class Bot(lightbulb.BotApp):

    __slots__: t.Sequence[str]
    color: int = 13616926

    def __init__(self) -> None:
        dotenv.load_dotenv()
        if not (token := os.getenv("TOKEN")):
            raise BaseException("No token added in `.env` file.")
        super().__init__(token)
        miru.load(self)
        self.load_extensions("commands.confess", "commands.admin")
        self.event_manager.subscribe(hikari.StartedEvent, self.on_started)

    async def on_started(self, _: hikari.StartedEvent) -> None:
        self.db: Database = await create_database()

    @property
    def me(self) -> hikari.OwnUser:
        return self.get_me()  # type: ignore
