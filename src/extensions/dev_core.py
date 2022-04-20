from __future__ import annotations

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


@tasks.task(m=10, auto_start=True)
async def updated_status() -> None:
    await dev.bot.update_presence(
        activity=Activity(
            type=ActivityType.LISTENING,
            name=f"/help in {len(dev.bot.cache.get_guilds_view())} servers.",
        ),
        status=Status.IDLE,
    )


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
