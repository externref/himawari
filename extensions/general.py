from __future__ import annotations

from datetime import datetime

import hikari
import lightbulb
import miru

from core.bot import Gojo


class General(lightbulb.Plugin):
    def __init__(self):
        self.bot: Gojo
        self.pos = 6
        super().__init__(
            name="general",
            description="General bot commands.",
        )


general = General()


@general.command
@lightbulb.command(name="ping", description="Bot's latency in ms.")
@lightbulb.implements(lightbulb.SlashCommand)
async def _ping(context: lightbulb.SlashContext) -> None:
    embed = hikari.Embed(
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
@lightbulb.command(name="vote", description="Vote for me on bot lists!")
@lightbulb.implements(lightbulb.SlashCommand)
async def _vote(context: lightbulb.SlashContext) -> None:
    top_gg = f"https://top.gg/bot/{context.bot.get_me().id}/vote"
    embed = (
        hikari.Embed(
            color=await general.bot.color_for(context.get_guild()),
            description=f"{general.bot.cache.get_emoji(975653528825655317)} Vote on [`top.gg`]({top_gg})",
        )
        .set_author(name=f"VOTE FOR {general.bot.get_me().username.upper()}")
        .set_thumbnail(general.bot.get_me().avatar_url)
        .set_footer(
            text=f"Requested by {context.author}",
            icon=context.author.display_avatar_url,
        )
    )
    view = miru.View()
    view.add_item(
        miru.Button(
            style=hikari.ButtonStyle.LINK,
            emoji=general.bot.cache.get_emoji(975653528825655317),
            label="top.gg",
            url=top_gg,
        )
    )
    await context.respond(embed=embed, components=view.build())


@general.command
@lightbulb.option(
    name="user",
    description="User to check avatar of.",
    required=False,
    type=hikari.User,
)
@lightbulb.command(name="avatar", description="Check avatar of a user.")
@lightbulb.implements(lightbulb.SlashCommand)
async def av_command(context: lightbulb.SlashContext) -> None:
    target = context.options.user or context.author
    await context.respond(
        embed=hikari.Embed(
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
