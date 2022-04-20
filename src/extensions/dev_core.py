from __future__ import annotations

from lightbulb.ext import tasks
from lightbulb.plugins import Plugin
from lightbulb import errors as lb_errors
from lightbulb.context.slash import SlashContext
from lightbulb.context.base import ResponseProxy
from lightbulb.events import SlashCommandErrorEvent

from hikari.embeds import Embed
from hikari.presences import Status, ActivityType, Activity

from ..core.bot import Gojo


class Developer(Plugin):
    def __init__(self) -> None:
        self.bot: Gojo
        self.pos = 0
        self.help_ignore = True
        super().__init__(name="Developer")


dev = Developer()


@tasks.task(m=10, auto_start=True)
async def updated_status() -> None:
    await dev.bot.update_presence(
        activity=Activity(
            type=ActivityType.LISTENING,
            name=f"/help in {len(dev.bot.cache.get_guilds_view())} servers.",
        ),
        status=Status.IDLE,
    )


@dev.listener(SlashCommandErrorEvent)
async def lightbulb_error(error: SlashCommandErrorEvent) -> None | ResponseProxy:
    context: SlashContext = error.context
    guild = context.get_guild()
    color = await dev.bot.color_for(guild)
    if isinstance(error.exception, lb_errors.CommandIsOnCooldown):
        await context.respond(
            embed=Embed(
                color=color,
                description=f"`{context.command.name}` command is on cooldown for `{error.exception.retry_after:.1f}` seconds.",
            )
        )
    elif isinstance(error.exception, lb_errors.NotOwner):
        await context.respond(
            embed=Embed(
                color=color,
                description=f"`{context.command.name}` is an owner only command.",
            )
        )
    elif isinstance(error.exception, lb_errors.MissingRequiredPermission):
        perms = "` , `".join(perm.name for perm in error.exception.missing_perms)
        await context.respond(
            embed=Embed(
                color=color,
                description=f"You need `{perms}` permission(s) to run this command.",
            )
        )

    elif isinstance(error.exception, lb_errors.BotMissingRequiredPermission):
        perms = "` , `".join(perm.name for perm in error.exception.missing_perms)
        await context.respond(
            embed=Embed(
                color=color,
                description=f"Bot need `{perms}` permission(s) to run this command.",
            )
        )
    elif isinstance(error.exception, lb_errors.OnlyInDM):
        await context.respond(
            embed=Embed(
                color=color,
                description=f"`{context.command.name}` command can only be used in DMs.",
            )
        )
    elif isinstance(error.exception, lb_errors.OnlyInGuild):
        await context.respond(
            embed=Embed(
                color=color,
                description=f"`{context.command.name}` command cannot be used in DMs.",
            )
        )
    else:
        raise error.exception


def load(bot: Gojo):
    bot.add_plugin(dev)
