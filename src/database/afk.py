from __future__ import annotations

import datetime

import aiosqlite
import hikari

class AFKHandler:
    connection: aiosqlite.Connection
    afk_users: dict[str, datetime.datetime] = {}

    async def setup(self) -> None:
        conn = await aiosqlite.connect("afk.db")
        cursor = await conn.cursor()
        await cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS afk
            ( user_id BIGINT, guild_id BIGINT, timestamp INT )
            """
        )
        await conn.commit()
        self.connection = conn

    async def add_afk_to_member(self, member: hikari.Member) -> None:
        cursor = await self.connection.cursor()
        await cursor.execute(
            """
            INSERT INTO afk 
            ()
            """
        )