from typing import Union

import aiosqlite
from hikari import Guild

from lightbulb.context.base import Context

from hikari.guilds import Guild
from hikari.channels import TextableGuildChannel


class WelcomerHandler:
    connection: aiosqlite.Connection
    DEFAULT_WELCOME_MESSAGE = "$user, Welcome to $server"

    async def setup(self) -> aiosqlite.Connection:
        conn = await aiosqlite.connect("welcome.db")
        async with conn.cursor() as cursor:
            await cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS welcome
                (guild_id TEXT, channel_id TEXT, message TEXT, hex_code TEXT)
                """
            )
        await conn.commit()
        self.connection = conn

    async def insert_data(self, guild_id: int, channel_id: int) -> None:
        cursor = await self.connection.cursor()
        await cursor.execute(
            """
            INSERT INTO welcome
            ( guild_id, channel_id, message, hex_code )
            VALUES ( ?, ?, ?,? )
            """,
            (str(guild_id), str(channel_id), self.DEFAULT_WELCOME_MESSAGE, "ffffff"),
        )
        await self.connection.commit()

    async def update_data(
        self, guild_id: int, data: str, value: Union[str, int]
    ) -> None:
        cursor = await self.connection.cursor()
        await cursor.execute(
            """
            UPDATE welcome
            SET {} = ?
            WHERE guild_id = ?
            """.format(
                data
            ),
            (value, str(guild_id)),
        )
        await self.connection.commit()

    async def get_data(self, guild_id: int) -> dict:
        cursor = await self.connection.cursor()
        await cursor.execute(
            """
            SELECT * FROM welcome
            WHERE guild_id = ?
            """,
            (str(guild_id),),
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

    async def get_welcome_message(self, guild: Guild) -> str:
        return await self.get_message(guild.id)

    async def get_welcome_channel(self, guild: Guild) -> TextableGuildChannel:
        id_ = await self.get_channel_id(guild.id)
        return guild.get_channel(id_)

    async def get_welcome_hex_code(self, guild: Guild) -> int:
        return int(await self.get_hex_code(guild.id), 16)


class LeaveHandler(WelcomerHandler):
    def __init__(self) -> None:
        self.DEFAULT_LEAVE_MESSAGE = "$user left the server."
        self.get_leave_channel = self.get_welcome_channel
        self.get_leave_hex_code = self.get_welcome_hex_code
        self.get_leave_message = self.get_welcome_message
        super().__init__()
