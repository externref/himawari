from lightbulb.plugins import Plugin
from lightbulb.context.slash import SlashContext
from lightbulb.commands.slash import SlashCommand
from lightbulb.decorators import command, option, implements

from hikari.embeds import Embed
from hikari.events.lifetime_events import StartingEvent

from ..core.bot import Gojo


class Admin(Plugin):
    def __init__(self) -> None:
        self.bot: Gojo
        super().__init__(
            name="Admin Commands",
            description="Admin commands for configuring bot's behaviour in server.",
        )


admin = Admin()


@admin.listener(StartingEvent)
async def _on_starting(_: StartingEvent) -> None:
    await admin.bot.color_handler.create_connection()


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


def load(bot: Gojo):
    bot.add_plugin(admin)
