from __future__ import annotations

from lightbulb.plugins import Plugin
from lightbulb.context.slash import SlashContext
from lightbulb.context.base import ResponseProxy
from lightbulb.checks import has_guild_permissions
from lightbulb.converters.special import EmojiConverter
from lightbulb.decorators import command, option, implements
from lightbulb.commands.slash import SlashCommand, SlashCommandGroup, SlashSubCommand

from hikari.embeds import Embed
from hikari.permissions import Permissions
from hikari.emojis import CustomEmoji, Emoji
from hikari.channels import TextableGuildChannel
from hikari.events.lifetime_events import StartingEvent

from ..core.bot import Gojo


class Starboard(Plugin):
    def __init__(self) -> None:
        self.bot: Gojo
        super().__init__(
            name="starboard",
            description="Setup a starboard for important messages to appear in a channel.",
        )
        self.add_checks(has_guild_permissions(Permissions.MANAGE_GUILD))


starboard = Starboard()


@starboard.listener(StartingEvent)
async def connect(_: StartingEvent) -> None:
    await starboard.bot.starboard_handler.setup()


@starboard.command
@command(name="starboard", description="Starboard commands.")
@implements(SlashCommandGroup)
async def starboard_base(context: SlashContext) -> None:
    ...


@starboard_base.child
@option(
    name="channel",
    description="The starboard channel",
    type=TextableGuildChannel,
    required=True,
)
@command(
    name="channel",
    description="Set/Change The starboard Channel.",
)
@implements(SlashSubCommand)
async def set_channel(context: SlashContext) -> None:
    handler = starboard.bot.starboard_handler
    data = await handler.get_data(context.get_guild())
    channel = context.get_guild().get_channel(context.options.channel.id)

    if data:
        await handler.update_channel(channel)
    else:
        await handler.insert_data(channel)
    await context.respond(
        embed=Embed(
            description=f"`{context.options.channel}` is the new starboard channel.",
            color=await starboard.bot.color_for(context.get_guild()),
        )
    )


@starboard_base.child
@option(
    name="emoji",
    description="The emoji by which starboard is triggered",
    type=Emoji,
    required=True,
)
@command(name="emoji", description="Set the starboard emoji, `⭐` by default.")
@implements(SlashSubCommand)
async def set_emoji(context: SlashContext) -> None | ResponseProxy:
    handler = starboard.bot.starboard_handler
    color = await starboard.bot.color_for(context.get_guild())
    data = await handler.get_data(context.get_guild())
    if not data:
        return await context.respond(
            embed=Embed(
                description="You don't have a starboard channel setup yet.", color=color
            )
        )

    emoji = await EmojiConverter(context).convert(context.options.emoji)
    if isinstance(emoji, CustomEmoji):
        if emoji.id not in (
            emoji_.id for emoji_ in context.get_guild().get_emojis().values()
        ):

            return await context.respond(
                embed=Embed(
                    description="The custom emoji must be a default emoji or an emoji from this server.",
                    color=color,
                )
            )
        to_enter = f"custom{emoji.id}"
    elif emoji.name == "⭐":
        to_enter = "default"
    else:
        return await context.respond(
            embed=Embed(
                color=color, description="`emoji` must be a custom emoji or `⭐`"
            )
        )
    await handler.update_emoji(context.get_guild(), to_enter)
    await context.respond(
        embed=Embed(color=color, description=f"{emoji} is the new starboard emoji.")
    )


@starboard_base.child
@option(name="number", description="Number of reactions", type=int, required=True)
@command(
    name="min_count",
    description="The minumum number of reactions required to add the message to starboard.",
)
@implements(SlashSubCommand)
async def set_minimum_count(context: SlashContext) -> None | ResponseProxy:
    handler = starboard.bot.starboard_handler
    color = await starboard.bot.color_for(context.get_guild())
    data = await handler.get_data(context.get_guild())
    if not data:
        return await context.respond(
            embed=Embed(
                description="You don't have a starboard channel setup yet.", color=color
            )
        )

    await handler.update_min_count(context.get_guild(), context.options.number)
    await context.respond(
        embed=Embed(
            color=color,
            description=f"Now messages need atleast {context.options.number} reactions to get added to starboard.",
        )
    )


def load(bot: Gojo) -> None:
    bot.add_plugin(starboard)


def unload(bot: Gojo) -> None:
    bot.remove_plugin(starboard)
