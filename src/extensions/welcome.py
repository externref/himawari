from typing import Optional

from lightbulb.plugins import Plugin
from lightbulb.context.slash import SlashContext
from lightbulb.decorators import command, option, implements
from lightbulb.context.base import ResponseProxy
from lightbulb.commands.slash import SlashCommandGroup, SlashSubCommand


from hikari.embeds import Embed
from hikari.channels import TextableGuildChannel
from hikari.events.lifetime_events import StartedEvent

from ..core.bot import Gojo


class Welcome(Plugin):
    def __init__(self) -> None:
        self.bot: Gojo
        super().__init__(
            name="Welcome Commands", description="Welcome module to greet new users."
        )


welcome = Welcome()


@welcome.listener(StartedEvent)
async def connect(_) -> None:
    await welcome.bot.welcome_handler.setup()


@welcome.command
@command(
    name="welcome",
    description="Welcome commands to greet new members joining your server.",
)
@implements(SlashCommandGroup)
async def _welcome(_: SlashContext) -> None:
    ...


@_welcome.child
@option(
    name="channel",
    description="Channel to send welcome messages in.",
    type=TextableGuildChannel,
)
@command(name="channel", description="Change/set welcome channel.")
@implements(SlashSubCommand)
async def channel_setter(context: SlashContext) -> Optional[ResponseProxy]:
    if not isinstance(context.options.channel, TextableGuildChannel):
        await context.respond(
            embed=Embed(
                description=f"`{context.options.channel}` is not a valid text channel."
            )
        )
    data = await welcome.bot.welcome_handler.get_data(context.guild_id)
    if not data:
        await welcome.bot.welcome_handler.insert_data(
            context.guild_id, context.options.channel.id
        )
    else:
        await welcome.bot.welcome_handler.update_channel(
            context, context.options.channel
        )
    await context.respond(
        embed=Embed(
            description=f"Changed welcome channel to `{context.options.channel.name}`",
            color=await welcome.bot.color_for(context.get_guild()),
        )
    )


@_welcome.child
@option(name="message", description="New welcome message.")
@command(name="message", description="Setup your own welcome message.")
@implements(SlashSubCommand)
async def message_setter(context: SlashContext) -> Optional[ResponseProxy]:
    data = await welcome.bot.welcome_handler.get_data(context.guild_id)
    if not data:
        return await context.respond(
            embed=Embed(
                description="You need to setup a welcome channel first.",
                color=await welcome.bot.color_for(context.get_guild()),
            )
        )
    await welcome.bot.welcome_handler.update_message(
        context, context.options.message.replace("\\n", "\n")
    )
    await context.respond(
        embed=Embed(
            description=context.options.message.replace("\\n", "\n"),
            color=await welcome.bot.color_for(context.get_guild()),
        ).set_author(name="Changed Welcome Message to :")
    )


@_welcome.child
@option(name="hex", description="New hex color.")
@command(name="color", description="Change the color of welcome embeds.")
@implements(SlashSubCommand)
async def hex_setter(context: SlashContext) -> Optional[ResponseProxy]:
    data = await welcome.bot.welcome_handler.get_data(context.guild_id)
    if not data:
        return await context.respond(
            embed=Embed(
                description="You need to setup a welcome channel first.",
                color=await welcome.bot.color_for(context.get_guild()),
            )
        )
    try:
        int(context.options.hex, 16)
    except:
        return await context.respond(
            embed=Embed(
                color=await welcome.bot.color_for(context.get_guild()),
                description="`hex` must be a valid Hexcode.",
            ),
            reply=True,
        )
    await welcome.bot.welcome_handler.update_color(context, context.options.hex)
    await context.respond(
        embed=Embed(
            description=f"Changed welcome Embed hex to `{context.options.hex}`",
            color=await welcome.bot.welcome_handler.get_welcome_hex_code(
                context.get_guild()
            ),
        )
    )


@_welcome.child
@command(name="remove", description="Remove all welcome related data for the server.")
@implements(SlashSubCommand)
async def welcome_remover(context: SlashContext) -> Optional[ResponseProxy]:
    data = await welcome.bot.welcome_handler.get_data(context.guild_id)
    if not data:
        return await context.respond(
            embed=Embed(
                description="This server does not have a welcome configuration yet.",
                color=await welcome.bot.color_for(context.get_guild()),
            )
        )
    c = await welcome.bot.welcome_handler.connection.cursor()
    await c.execute(
        """
        DELETE FROM welcome
        WHERE guild_id = ?
        """,
        (str(context.guild_id)),
    )
    await welcome.bot.welcome_handler.connection.commit()


def load(bot: Gojo):
    bot.add_plugin(welcome)
