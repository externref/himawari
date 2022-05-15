from __future__ import annotations

from typing import Union

import aiosqlite

from lightbulb.context.base import Context

from hikari.guilds import Guild
from hikari.channels import TextableGuildChannel


class GoodbyeHandler:
    connection: aiosqlite.Connection
    DEFAULT_GOODBYE_MESSAGE = "$user, left the server"

    async def setup(self) -> aiosqlite.Connection:
        conn = await aiosqlite.connect("goodbye.db")
        async with conn.cursor() as cursor:
            await cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS goodbye
                (guild_id BIGINT, channel_id BIGINT, message TEXT, hex_code TEXT)
                """
            )
        await conn.commit()
        self.connection = conn
        return conn

    async def insert_data(self, guild_id: int, channel_id: int) -> None:
        cursor = await self.connection.cursor()
        await cursor.execute(
            """
            INSERT INTO goodbye
            VALUES ( ?, ?, ?, ? )
            """,
            (guild_id, channel_id, self.DEFAULT_GOODBYE_MESSAGE, "ffffff"),
        )
        await self.connection.commit()

    async def update_data(self, guild_id: int, data: str, value: str | int) -> None:
        cursor = await self.connection.cursor()
        await cursor.execute(
            """
            UPDATE goodbye
            SET {} = ?
            WHERE guild_id = ?
            """.format(
                data
            ),
            (value, guild_id),
        )
        await self.connection.commit()

    async def get_data(self, guild_id: int) -> dict:
        cursor = await self.connection.cursor()
        await cursor.execute(
            """
            SELECT * FROM goodbye
            WHERE guild_id = ?
            """,
            (guild_id,),
        )
        data = await cursor.fetchone()
        if data is None:
            return
        return {
            "channel_id": int(data[1]),
            "message": data[2],
            "hex_code": data[3],
        }

    async def get_channel_id(self, guild_id: int) -> int:
        data = await self.get_data(guild_id)
        if data is None:
            return
        return int(data["channel_id"])

    async def get_message(self, guild_id: int) -> str:
        data = await self.get_data(guild_id)
        if data is None:
            return
        return data["message"]

    async def get_hex_code(self, guild_id: int) -> str:
        data = await self.get_data(guild_id)
        if data is None:
            return
        return data["hex_code"]

    async def update_color(self, context: Context, hex_code: str) -> None:
        await self.update_data(context.get_guild().id, "hex_code", hex_code)

    async def update_message(self, context: Context, message: str) -> None:
        await self.update_data(context.get_guild().id, "message", message)

    async def update_channel(
        self, context: Context, channel: TextableGuildChannel
    ) -> None:
        await self.update_data(context.get_guild().id, "channel_id", channel.id)

    async def get_goodbye_message(self, guild: Guild) -> str:
        return await self.get_message(guild.id)

    async def get_goodbye_channel(self, guild: Guild) -> TextableGuildChannel | None:
        id_ = await self.get_channel_id(guild.id)
        return guild.get_channel(id_)

    async def get_goodbye_hex_code(self, guild: Guild) -> int:
        return int(await self.get_hex_code(guild.id), 16)
