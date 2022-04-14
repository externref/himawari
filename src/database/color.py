from __future__ import annotations

from typing import Union

import aiosqlite

from hikari.guilds import Guild
from hikari.messages import Message

from lightbulb.context import Context


class ColorHandler:
    database_connection: aiosqlite.Connection
    color_cache: dict[str, str]

    def __init__(self) -> None:
        self.color_cache = {}

    async def setup(self) -> None:
        """The internals call it for making a connection to the database"""
        conn = await aiosqlite.connect("colors.db")
        cursor = await conn.cursor()
        await cursor.execute(
            """
                CREATE TABLE IF NOT EXISTS  colors
                (guild_id TEXT , color TEXT)
                """
        )
        await conn.commit()
        self.database_connection = conn

    async def get_color(self, guild: Guild) -> str:
        """Method to use for the `color` arg in the lightbulb.BotApp object."""
        color_str = (
            self._from_cache(guild) or await self._from_database(guild) or "ffffff"
        )
        return color_str

    def _from_cache(self, guild: Guild) -> str:
        """Getting data from color_cache dictionary"""
        return self.color_cache.get(str(guild.id))

    async def _from_database(self, obj: Union[Message, Guild]) -> str:
        """Fetching the database from the sqlite3 database"""
        if isinstance(obj, Message):
            guild_id = obj.guild_id
        elif isinstance(obj, Guild):
            guild_id = obj.id
        async with self.database_connection.cursor() as cursor:
            await cursor.execute(
                """
                SELECT * FROM colors 
                WHERE guild_id = ?
                """,
                (str(guild_id),),
            )
            guild_data = await cursor.fetchone()
        if guild_data:
            self.color_cache[str(guild_id)] = guild_data[1]
            return guild_data[1]
        else:
            self.color_cache[str(guild_id)] = "ffffff"
            return

    async def set_color(self, ctx: Context, new_color: str) -> None:
        """Adding/Updating color for a server."""
        guild = ctx.get_guild()
        guild_data = await self._from_database(guild)
        async with self.database_connection.cursor() as cursor:
            if guild_data:
                await cursor.execute(
                    """
                    UPDATE colors
                    SET color = ?
                    WHERE guild_id = ?
                    """,
                    (new_color, str(guild.id)),
                )
            else:
                await cursor.execute(
                    """
                    INSERT INTO colors
                    (guild_id , color)
                    VALUES (? , ? )
                    """,
                    (str(guild.id), new_color),
                )
            await self.database_connection.commit()
            self.color_cache[str(guild.id)] = new_color
