from __future__ import annotations

import os

import hikari
import lightbulb

from lightbulb.ext import tasks


from hikari.presences import Status, ActivityType, Activity

from ..core.bot import Gojo


class Developer(lightbulb.Plugin):
    def __init__(self) -> None:
        self.bot: Gojo
        self.pos = 0
        self.help_ignore = True
        super().__init__(name="Developer")


dev = Developer()


@tasks.task(m=10)
async def update_status() -> None:
    await dev.bot.update_presence(
        activity=Activity(
            type=ActivityType.LISTENING,
            name=f"/help in {len(dev.bot.cache.get_guilds_view())} servers.",
        ),
        status=Status.IDLE,
    )


@tasks.task(m=10)
async def send_db_backup() -> None:
    await dev.bot.rest.create_message(
        os.getenv("BACKUP_CHANNEL"),
        attachments=[
            hikari.File(db_file)
            for db_file in (os.listdir())
            if db_file.endswith(".db")
        ],
    )


@dev.listener(hikari.GuildJoinEvent)
async def new_guild(event: hikari.GuildJoinEvent) -> None:
    embed = hikari.Embed(color=0x3FFF5C, title=f"+ {event.guild.name}")
    embed.set_thumbnail(event.guild.icon_url)
    embed.add_field(name="Guild ID", value=str(event.guild_id))
    embed.add_field(
        name="OWNER/ID",
        value=f"{await dev.bot.getch_user(event.guild.owner_id)} | {event.guild.owner_id}",
    )
    embed.add_field(name="Member Count", value=len(event.guild.get_members()))
    embed.add_field(
        name="Bot Count",
        value=len([m for m in event.guild.get_members().values() if m.is_bot]),
    )
    await dev.bot.rest.create_message(os.getenv("SERVER_LOG_CHANNEL"), embed=embed)


@dev.listener(hikari.GuildLeaveEvent)
async def new_guild(event: hikari.GuildLeaveEvent) -> None:
    embed = hikari.Embed(color=0xFF0000, title=f"- {event.guild.name}")
    embed.set_thumbnail(event.old_guild.icon_url)
    embed.add_field(name="Guild ID", value=str(event.guild_id))
    embed.add_field(
        name="OWNER/ID",
        value=f"{await dev.bot.getch_user(event.old_guild.owner_id)} | {event.old_guild.owner_id}",
    )
    embed.add_field(name="Member Count", value=len(event.old_guild.get_members()))
    embed.add_field(
        name="Bot Count",
        value=len([m for m in event.old_guild.get_members().values() if m.is_bot]),
    )
    await dev.bot.rest.create_message(os.getenv("SERVER_LOG_CHANNEL"), embed=embed)


@dev.listener(hikari.StartedEvent)
async def start_tasks(_: hikari.StartedEvent) -> None:
    update_status.start()
    send_db_backup.start()


@dev.listener(lightbulb.SlashCommandErrorEvent)
async def lightbulb_error(
    error: lightbulb.SlashCommandErrorEvent,
) -> None | lightbulb.ResponseProxy:
    context: lightbulb.SlashContext = error.context
    guild = context.get_guild()
    color = await dev.bot.color_for(guild)
    if isinstance(error.exception, lightbulb.CommandIsOnCooldown):
        await context.respond(
            embed=hikari.Embed(
                color=color,
                description=f"`{context.command.name}` command is on cooldown for `{error.exception.retry_after:.1f}` seconds.",
            )
        )
    elif isinstance(error.exception, lightbulb.NotOwner):
        await context.respond(
            embed=hikari.Embed(
                color=color,
                description=f"`{context.command.name}` is an owner only command.",
            )
        )
    elif isinstance(error.exception, lightbulb.MissingRequiredPermission):
        perms = "` , `".join(perm.name for perm in error.exception.missing_perms)
        await context.respond(
            embed=hikari.Embed(
                color=color,
                description=f"You need `{perms}` permission(s) to run this command.",
            )
        )

    elif isinstance(error.exception, lightbulb.BotMissingRequiredPermission):
        perms = "` , `".join(perm.name for perm in error.exception.missing_perms)
        await context.respond(
            embed=hikari.Embed(
                color=color,
                description=f"Bot need `{perms}` permission(s) to run this command.",
            )
        )
    elif isinstance(error.exception, lightbulb.OnlyInDM):
        await context.respond(
            embed=hikari.Embed(
                color=color,
                description=f"`{context.command.name}` command can only be used in DMs.",
            )
        )
    elif isinstance(error.exception, lightbulb.OnlyInGuild):
        await context.respond(
            embed=hikari.Embed(
                color=color,
                description=f"`{context.command.name}` command cannot be used in DMs.",
            )
        )
    else:
        raise error.exception


def load(bot: Gojo):
    bot.add_plugin(dev)


def unload(bot: Gojo):
    bot.remove_plugin(dev)
