from __future__ import annotations

from lightbulb.plugins import Plugin
from lightbulb.context.slash import SlashContext
from lightbulb.checks import has_guild_permissions
from lightbulb.decorators import command, option, implements
from lightbulb.commands.slash import SlashCommand, SlashCommandGroup, SlashSubCommand

from hikari.embeds import Embed
from hikari.permissions import Permissions


from ..core.bot import Gojo


class Admin(Plugin):
    def __init__(self) -> None:
        self.bot: Gojo
        super().__init__(
            name="admin",
            description="Admin commands for configuring bot's behaviour in server.",
        )
        self.add_checks(has_guild_permissions(Permissions.MANAGE_GUILD))


admin = Admin()


@admin.command
@option(
    name="hexcode",
    description="Hexcode of the color to set for the server embed messages.",
    required=True,
)
@command(
    name="color",
    description="Change the embed colors for messages sent by the bot in the server.",
)
@implements(SlashCommand)
async def set_color(context: SlashContext) -> None:
    try:
        int(context.options.hexcode, 16)
    except:
        return await context.respond(
            embed=Embed(
                color=await admin.bot.color_for(context.get_guild()),
                description="`hexcode` must be a valid Hexcode.",
            ),
            reply=True,
        )
    await admin.bot.color_handler.set_color(context, context.options.hexcode)
    await context.respond(
        embed=Embed(
            description=f"Changed server embed color to `{context.options.hexcode}`",
            color=await admin.bot.color_for(context.get_guild()),
        ),
        reply=True,
    )


@admin.command
@command(name="configs", description="Check configurations for the server.")
@implements(SlashCommandGroup)
async def _config(_: SlashContext) -> None:
    ...


@_config.child
@command(name="welcome", description="Show welcome configurations for the server.")
@implements(SlashSubCommand)
async def welcome_config(context: SlashContext) -> None:
    if not await admin.bot.welcome_handler.get_data(context.guild_id):
        await context.respond(
            embed=Embed(
                color=await admin.bot.color_for(context.get_guild()),
                description="This server has no welcome channel setup yet.",
            )
        )
        return
    channel = await admin.bot.welcome_handler.get_welcome_channel(context.get_guild())
    welcome_message = await admin.bot.welcome_handler.get_welcome_message(
        context.get_guild()
    )
    hex = await admin.bot.welcome_handler.get_hex_code(context.guild_id)

    await context.respond(
        embed=Embed(
            color=await admin.bot.color_for(context.get_guild()),
            description=f"```yaml\nWelcome Channel: {channel}\nWelcome Hex: {hex}\nWelcome Message: {welcome_message}```",
        ).set_author(name="WELCOME CONFIGURATIONS", icon=context.get_guild().icon_url)
    )


@_config.child
@command(name="goodbye", description="Show goodbye configurations for the server.")
@implements(SlashSubCommand)
async def goodbye_config(context: SlashContext) -> None:
    if not await admin.bot.goodbye_handler.get_data(context.guild_id):
        await context.respond(
            embed=Embed(
                color=await admin.bot.color_for(context.get_guild()),
                description="This server has no goodbye channel setup yet.",
            )
        )
        return
    channel = await admin.bot.goodbye_handler.get_goodbye_channel(context.get_guild())
    goodbye_message = await admin.bot.goodbye_handler.get_goodbye_message(
        context.get_guild()
    )
    hex = await admin.bot.goodbye_handler.get_hex_code(context.guild_id)

    await context.respond(
        embed=Embed(
            color=await admin.bot.color_for(context.get_guild()),
            description=f"```yaml\nGoodbye Channel: {channel}\nGoodbye Hex: {hex}\nGoodbye Message: {goodbye_message}\n```",
        ).set_author(name="GOODBYE CONFIGURATIONS", icon=context.get_guild().icon_url)
    )


@_config.child
@command(name="starboard", description="Show starboard configs.")
@implements(SlashSubCommand)
async def starboard_config(context: SlashContext) -> None:
    handler = admin.bot.starboard_handler
    if not await handler.get_channel(context.get_guild()):
        await context.respond(
            embed=Embed(
                color=await admin.bot.color_for(context.get_guild()),
                description="This server has no starbord channel setup yet.",
            )
        )
    channel = await handler.get_channel(context.get_guild())
    minimum = await handler.get_emoji_count(context.get_guild())
    emoji = (await handler.get_emoji(context.get_guild())).replace("custom", "")
    await context.respond(
        embed=Embed(
            color=await admin.bot.color_for(context.get_guild()),
            description=f"```yaml\nStarboard Channel: {channel}\nMimimum Reactions: {minimum}\nEmoji: {emoji}```",
        )
        .set_author(name="STARBOARD CONFIGURATIONS", icon=context.get_guild().icon_url)
        .set_thumbnail(
            f"https://cdn.discordapp.com/emojis/{emoji}.webp?size=40&quality=lossless"
        )
    )


def load(bot: Gojo):
    bot.add_plugin(admin)


def unload(bot: Gojo):
    bot.remove_plugin(admin)
