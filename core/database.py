import typing as t

import aiosqlite
import hikari


class Database:
    async def setup(self) -> "Database":
        conn = await aiosqlite.connect("database.db")
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS channels
            ( guild_id BIGINT, channel_id BIGINT )
            """
        )
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS bans
            ( guild_id BIGINT, user_id BIGINT )
            """
        )
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS confessions
            ( guild_id BIGINT, user_id BIGINT, channel_id BIGINT, message_id BIGINT )
            """
        )
        await conn.commit()
        self.connection = conn
        return self

    async def get_confession_channel(self, guild_id: int) -> None | aiosqlite.Row:
        async with self.connection.cursor() as cursor:
            await cursor.execute(
                """
                SELECT * FROM channels
                WHERE guild_id = ?
                """,
                (guild_id,),
            )
            return await cursor.fetchone()

    async def set_confession_channel(
        self, guild_id: int, channel_id: int | None
    ) -> None:
        async with self.connection.cursor() as cursor:
            if await self.get_confession_channel(guild_id):
                await cursor.execute(
                    """
                    UPDATE channels
                    SET channel_id = ?
                    WHERE guild_id = ?
                    """,
                    (channel_id, guild_id),
                )
                return
            await cursor.execute(
                "INSERT INTO channels VALUES ( ?, ? )", (guild_id, channel_id)
            )

    async def add_confession(
        self, member: hikari.Member, message: hikari.Message
    ) -> None:
        async with self.connection.cursor() as cursor:
            await cursor.execute(
                "INSERT INTO confessions VALUES ( ?, ?, ?, ? )",
                (member.guild_id, member.id, message.channel_id, message.id),
            )
            await self.connection.commit()

    async def ban_user(self, guild_id: int, user_id: int) -> None:
        async with self.connection.cursor() as cursor:
            await cursor.execute("INSERT INTO bans VALUES ( ?, ?)", (guild_id, user_id))
        await self.connection.commit()

    async def check_ban(self, guild_id: int, user_id: int) -> None | aiosqlite.Row:
        async with self.connection.cursor() as cursor:
            await cursor.execute(
                """
                SELECT * FROM bans 
                WHERE guild_id = ? AND user_id = ?
                """,
                (guild_id, user_id),
            )
            return await cursor.fetchone()

    async def remove_ban(self, guild_id: int, user_id: int) -> None:
        async with self.connection.cursor() as cursor:
            await cursor.execute(
                """
                DELETE FROM bans
                WHERE guild_id = ? AND user_id =? 
                """,
                (guild_id, user_id),
            )


async def create_database() -> Database:
    return await Database().setup()
