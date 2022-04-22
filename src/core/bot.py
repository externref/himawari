from __future__ import annotations

import os
from datetime import datetime, timedelta

import aiohttp
import hikari
import lightbulb
from lightbulb.ext import tasks

from ..database.color import ColorHandler
from ..database.leave import GoodbyeHandler
from ..database.starboard import StarboardHandler
from ..database.welcome import WelcomerHandler


def get_token():
    import dotenv

    # getting the `TOKEN` enviornment variable from .env file

    dotenv.load_dotenv()
    return os.getenv("TOKEN")


class Gojo(lightbulb.BotApp):
    """Initialising the bot class with all additional methods and attributes."""

    def __init__(self):
        self.color_handler = (
            ColorHandler()
        )  # color handler to deal with bot's custom embed colors.
        self.goodbye_handler = (
            GoodbyeHandler()
        )  # goodbye database connection for MemberDeleteEvent events.
        self.welcome_handler = (
            WelcomerHandler()
        )  # welcomer database connection for greeting new users.
        self.starboard_handler = (
            StarboardHandler()
        )  # starboard manager with required methods.
        super().__init__(
            token=get_token(),
            help_slash_command=True,
            # default_enabled_guilds=(os.getenv("GUILD_ID"),),
            intents=(
                hikari.Intents.ALL_UNPRIVILEGED  # adding all not privilaged intents to the bot
                | hikari.Intents.GUILD_MEMBERS  # GUILD_MEMBERS intents for welcome & leave module
                | hikari.Intents.GUILD_PRESENCES  # GUILD_PRESENCES intents for other utils.
            ),
            banner="hikari",
        )
        tasks.load(self)
        self._boot_time = datetime.now()
        self.load_extensions_from(
            "src/extensions"
        )  # loading all plugins and help command from the extensions folder.
        self.invite_url = (
            "https://discord.com/api/oauth2/authorize?client_id=961613807564775447"
            + "&permissions=378025593921&scope=bot%20applications.commands"
        )
        self.event_manager.subscribe(hikari.StartingEvent, self.start_handlers)

    async def start_handlers(self, _: hikari.StartingEvent) -> None:
        """Additional setups which need to be called under async functions."""
        self.custom_session = aiohttp.ClientSession()
        await self.color_handler.setup()
        await self.goodbye_handler.setup()
        await self.welcome_handler.setup()
        await self.starboard_handler.setup()

    @property
    def uptime(self) -> timedelta:
        # returning a timedelta which is diff between boot time and current datetime
        return datetime.now() - self._boot_time

    async def color_for(self, guild: hikari.Guild) -> int:
        if not guild:
            return 0xFFFFFF  # returning a default value if its a dm command.
        color = await self.color_handler.get_color(guild)
        return int(color, 16)  # converting the string to a hexadecimal int

    async def getch_user(self, id: int) -> hikari.User | None:
        """Getting a user from the cache or the API"""
        cached = self.cache.get_user(id)
        if cached:
            return cached
        try:
            fetch = await self.rest.fetch_user(id)
            return fetch
        except hikari.NotFoundError:
            return
