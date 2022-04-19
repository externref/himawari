from __future__ import annotations

from datetime import datetime

from lightbulb.plugins import Plugin
from lightbulb.context.slash import SlashContext
from lightbulb.commands.slash import SlashCommand
from lightbulb.decorators import command, option, implements

from hikari.users import User
from hikari.embeds import Embed

from ..core.bot import Gojo


class General(Plugin):
    def __init__(self):
        self.bot: Gojo
        super().__init__(
            name="general",
            description="General bot commands.",
            default_enabled_guilds=(964157647752400916),
        )


general = General()


@general.command
@command(name="ping", description="Bot's latency in ms.")
@implements(SlashCommand)
async def _ping(context: SlashContext) -> None:
    embed = Embed(
        color=await general.bot.color_for(context.get_guild()),
        description="Getting Bot Ping.",
    )
    await context.respond(embed=embed, reply=True)
    start = datetime.now()
    await general.bot.color_for(context.get_guild())
    prefix_fetch = (datetime.now() - start).microseconds
    embed.description = f"Bot Latency: `{round(general.bot.heartbeat_latency*1000,2)} ms`\nDatabase Latency: `{prefix_fetch} ms`"
    await context.edit_last_response(embed=embed)


@general.command
@option(name="user", description="User to check avatar of.", required=False, type=User)
@command(name="avatar", description="Check avatar of a user.")
@implements(SlashCommand)
async def av_command(context: SlashContext) -> None:
    target = context.options.user or context.author
    await context.respond(
        embed=Embed(
            color=await general.bot.color_for(context.get_guild()),
            description=f"[Download Avatar]({target.avatar_url or target.default_avatar_url})",
        )
        .set_author(name=f"{target.username.replace('_','_/')}'s avatar")
        .set_footer(text=f"Requested by {context.author}")
        .set_image(target.display_avatar_url)
    )


def load(bot: Gojo):
    bot.add_plugin(general)


def unload(bot: Gojo):
    bot.remove_plugin(general)
