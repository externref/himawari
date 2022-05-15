from __future__ import annotations


import aiosqlite

from hikari.guilds import Guild
from hikari.channels import GuildTextChannel


class StarboardHandler:
    connection: aiosqlite.Connection

    async def setup(self) -> aiosqlite.Connection:
        conn = await aiosqlite.connect("starboard.db")
        cursor = await conn.cursor()
        await cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS starboard
            (guild_id BIGINT, channel_id BIGINT, emoji TEXT, minimum_reaction REAL)
            """
        )
        await cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS sent_messages
            (message_id BIGINT )
            """
        )
        await conn.commit()
        self.connection = conn
        return conn

    async def insert_data(self, channel: GuildTextChannel) -> None:
        cursor = await self.connection.cursor()
        await cursor.execute(
            """
            INSERT INTO starboard
            VALUES (? , ?, ? , ?)
            """,
            (channel.get_guild().id, channel.id, "default", 3),
        )
        await self.connection.commit()

    async def update(self, guild: Guild, data: str, value: str | int) -> None:
        cursor = await self.connection.cursor()
        await cursor.execute(
            """
            UPDATE starboard
            SET {} = ?
            WHERE guild_id = ?
            """.format(
                data
            ),
            (value, guild.id),
        )
        await self.connection.commit()

    async def update_channel(self, channel: GuildTextChannel) -> None:
        await self.update(channel.get_guild(), "channel_id", str(channel.id))

    async def update_emoji(self, guild: Guild, emoji: str) -> None:
        await self.update(guild, "emoji", emoji)

    async def update_min_count(self, guild: Guild, count: int) -> None:
        await self.update(guild, "minimum_reaction", count)

    async def get_data(self, guild: Guild) -> dict | None:
        cursor = await self.connection.cursor()
        await cursor.execute(
            """
            SELECT * FROM starboard
            WHERE guild_id =?
            """,
            (guild.id,),
        )
        data = await cursor.fetchone()
        if not data:
            return
        return {"channel_id": data[1], "emoji": data[2], "count": data[3]}

    async def get_channel(self, guild: Guild) -> GuildTextChannel | None:
        data = await self.get_data(guild)
        if not data:
            return
        return guild.get_channel(int(data.get("channel_id")))

    async def get_emoji(self, guild: Guild) -> str:
        data = await self.get_data(guild)
        if not data:
            return
        return data.get("emoji")

    async def get_emoji_count(self, guild: Guild) -> int:
        data = await self.get_data(guild)
        if not data:
            return
        return data.get("count")

    async def blacklist_message(self, id: int) -> None:
        cursor = await self.connection.cursor()
        await cursor.execute(
            """
            INSERT INTO sent_messages
            VALUES ( ? )
            """,
            (id,),
        )
        await self.connection.commit()

    async def is_blacklisted(self, id: int) -> bool:
        cursor = await self.connection.cursor()
        await cursor.execute(
            """
            SELECT * from sent_messages 
            WHERE message_id = ?
            """,
            (id,),
        )
        if await cursor.fetchone():
            return True
        else:
            return
