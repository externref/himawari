import os
from datetime import datetime, timedelta

from lightbulb.app import BotApp

from hikari.guilds import Guild
from hikari.intents import Intents

from ..database.color import ColorHandler
from ..database.welcome import WelcomerHandler


def get_token():
    import dotenv

    dotenv.load_dotenv()
    return os.getenv("TOKEN")


class Gojo(BotApp):
    def __init__(self):
        self.color_handler = ColorHandler("FFFFFF")
        self.welcome_handler = WelcomerHandler()
        super().__init__(
            token=get_token(),
            help_slash_command=True,
            default_enabled_guilds=(946977305891340338,),
            intents=(
                Intents.ALL_UNPRIVILEGED
                | Intents.GUILD_MEMBERS
                | Intents.GUILD_PRESENCES
            ),
            banner="hikari",
        )
        self._boot_time = datetime.now()
        self.load_extensions("lightbulb.ext.filament.exts.superuser")
        self.load_extensions_from("src/extensions")
        self.invite_url = (
            "https://discord.com/api/oauth2/authorize?client_id=961613807564775447"
            + "&permissions=378025593921&scope=bot%20applications.commands"
        )

    @property
    def uptime(self) -> timedelta:
        return datetime.now() - self._boot_time

    async def color_for(self, guild: Guild) -> int:
        color = await self.color_handler.get_color(guild)
        return int(color, 16)
