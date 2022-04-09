from typing import Optional

from lightbulb.plugins import Plugin
from lightbulb.context.base import ResponseProxy
from lightbulb.context.slash import SlashContext
from lightbulb.commands.slash import SlashCommand
from lightbulb.decorators import command, option, implements
from lightbulb.commands.slash import SlashCommandGroup, SlashSubCommand

from hikari.embeds import Embed
from hikari.guilds import Guild
from hikari.users import User
from hikari.errors import ForbiddenError
from hikari.channels import TextableGuildChannel
from hikari.events.lifetime_events import StartedEvent
from hikari.events.member_events import MemberCreateEvent, MemberDeleteEvent

from ..core.bot import Gojo


class Greeting(Plugin):
    def __init__(self) -> None:
        self.bot: Gojo
        super().__init__(
            name="greeting",
            description="Welcome/Leave module to greet new users and goodbyes.",
        )


greeting = Greeting()


@greeting.listener(StartedEvent)
async def connect(_) -> None:
    await greeting.bot.welcome_handler.setup()
    await greeting.bot.goodbye_handler.setup()


def process_raw_message(message: str, member: User, guild: Guild) -> str:
    message_to_return = (
        message.replace("$usermention", str(member.mention))
        .replace("$userid", str(member.id))
        .replace("$username", str(member.username))
        .replace("$userdiscriminator", str(member.discriminator))
        .replace("$userdiscrim", str(member.discriminator))
        .replace("$user", str(member))
        .replace("$servername", str(guild.name))
        .replace("$server", str(guild.name))
        .replace("$membercount", str(len(guild.get_members())))
    )
    return message_to_return


@greeting.listener(MemberCreateEvent)
async def new_member(event: MemberCreateEvent) -> None:
    data = await greeting.bot.welcome_handler.get_data(event.guild_id)
    if not data:
        return
    channel = await greeting.bot.welcome_handler.get_welcome_channel(event.get_guild())
    if not channel:
        return
    raw_message = await greeting.bot.welcome_handler.get_welcome_message(
        event.get_guild()
    )
    embed = Embed(
        description=process_raw_message(raw_message, event.member, event.get_guild()),
        color=await greeting.bot.welcome_handler.get_welcome_hex_code(
            event.get_guild()
        ),
    )
    embed.set_author(name=str(event.member)).set_thumbnail(event.member.avatar_url)
    try:
        await channel.send(embed=embed)
    except ForbiddenError:
        ...


@greeting.listener(MemberDeleteEvent)
async def remove_member(event: MemberDeleteEvent) -> None:
    data = await greeting.bot.goodbye_handler.get_data(event.guild_id)
    if not data:
        return
    channel = await greeting.bot.goodbye_handler.get_goodbye_channel(event.get_guild())
    if not channel:
        return
    raw_message = await greeting.bot.goodbye_handler.get_goodbye_message(
        event.get_guild()
    )
    embed = Embed(
        description=process_raw_message(raw_message, event.user, event.get_guild()),
        color=await greeting.bot.goodbye_handler.get_goodbye_hex_code(
            event.get_guild()
        ),
    )
    embed.set_author(name=str(event.user)).set_thumbnail(event.user.avatar_url)
    try:
        await channel.send(embed=embed)
    except ForbiddenError:
        ...


@greeting.command
@command(
    name="greetingvariables",
    description="Variables allowed in welcome/goodbye messages",
)
@implements(SlashCommand)
async def variables(context: SlashContext) -> None:
    await context.respond(
        embed=Embed(
            color=await greeting.bot.color_for(context.get_guild()),
            description="""
```bash
$user : Name and tag of the User [ Sarthak_#0460 ]
$usermention : Mention of the new Member [ <@!580034015759826944> ]
$userid : Id of the Member [ 580034015759826944 ]
$username : Username of the Member [ Sarthak_ ]
$userdiscrim / $userdiscriminator : Discriminator of the User [ 0460 ]
$server / $servername : Name of the Server [ VELOC1TY ]
$membercount : Membercount of the Server [ 69 ] 
```
""",
        ).set_author(name="GREETING VARIABLES")
    )


@greeting.command
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
    description="Channel to send greeting messages in.",
    type=TextableGuildChannel,
)
@command(name="channel", description="Change/set welcome channel.")
@implements(SlashSubCommand)
async def channel_setter(context: SlashContext) -> Optional[ResponseProxy]:
    data = await greeting.bot.welcome_handler.get_data(context.guild_id)
    if not data:
        await greeting.bot.welcome_handler.insert_data(
            context.guild_id, context.options.channel.id
        )
    else:
        await greeting.bot.welcome_handler.update_channel(
            context, context.options.channel
        )
    await context.respond(
        embed=Embed(
            description=f"Changed greeting channel to `{context.options.channel.name}`",
            color=await greeting.bot.color_for(context.get_guild()),
        )
    )


@_welcome.child
@option(name="message", description="New welcome message.")
@command(name="message", description="Setup your own welcome message.")
@implements(SlashSubCommand)
async def message_setter(context: SlashContext) -> Optional[ResponseProxy]:
    data = await greeting.bot.welcome_handler.get_data(context.guild_id)
    if not data:
        return await context.respond(
            embed=Embed(
                description="You need to setup a welcome channel first.",
                color=await greeting.bot.color_for(context.get_guild()),
            )
        )
    await greeting.bot.welcome_handler.update_message(
        context, context.options.message.replace("\\n", "\n")
    )
    await context.respond(
        embed=Embed(
            description=context.options.message.replace("\\n", "\n"),
            color=await greeting.bot.color_for(context.get_guild()),
        ).set_author(name="Changed Welcome Message to :")
    )


@_welcome.child
@option(name="hex", description="New hex color.")
@command(name="color", description="Change the color of welcome embeds.")
@implements(SlashSubCommand)
async def hex_setter(context: SlashContext) -> Optional[ResponseProxy]:
    data = await greeting.bot.welcome_handler.get_data(context.guild_id)
    if not data:
        return await context.respond(
            embed=Embed(
                description="You need to setup a welcome channel first.",
                color=await greeting.bot.color_for(context.get_guild()),
            )
        )
    try:
        int(context.options.hex, 16)
    except:
        return await context.respond(
            embed=Embed(
                color=await greeting.bot.color_for(context.get_guild()),
                description="`hex` must be a valid Hexcode.",
            ),
            reply=True,
        )
    await greeting.bot.welcome_handler.update_color(context, context.options.hex)
    await context.respond(
        embed=Embed(
            description=f"Changed welcome Embed hex to `{context.options.hex}`",
            color=await greeting.bot.welcome_handler.get_welcome_hex_code(
                context.get_guild()
            ),
        )
    )


@_welcome.child
@command(name="remove", description="Remove all welcome related data for the server.")
@implements(SlashSubCommand)
async def welcome_remover(context: SlashContext) -> Optional[ResponseProxy]:
    data = await greeting.bot.welcome_handler.get_data(context.guild_id)
    if not data:
        return await context.respond(
            embed=Embed(
                description="This server does not have a welcome configuration yet.",
                color=await greeting.bot.color_for(context.get_guild()),
            )
        )
    c = await greeting.bot.welcome_handler.connection.cursor()
    await c.execute(
        """
        DELETE FROM welcome
        WHERE guild_id = ?
        """,
        (str(context.guild_id)),
    )
    await greeting.bot.welcome_handler.connection.commit()


@greeting.command
@command(
    name="goodbye",
    description="Goodbye commands.",
)
@implements(SlashCommandGroup)
async def _goodbye(_: SlashContext) -> None:
    ...


@_goodbye.child
@option(
    name="channel",
    description="Channel to send greeting messages in.",
    type=TextableGuildChannel,
)
@command(name="channel", description="Change/set goodbye channel.")
@implements(SlashSubCommand)
async def channel_setter(context: SlashContext) -> Optional[ResponseProxy]:
    data = await greeting.bot.goodbye_handler.get_data(context.guild_id)
    if not data:
        await greeting.bot.goodbye_handler.insert_data(
            context.guild_id, context.options.channel.id
        )
    else:
        await greeting.bot.goodbye_handler.update_channel(
            context, context.options.channel
        )
    await context.respond(
        embed=Embed(
            description=f"Changed greeting channel to `{context.options.channel.name}`",
            color=await greeting.bot.color_for(context.get_guild()),
        )
    )


@_goodbye.child
@option(name="message", description="New goodbye message.")
@command(name="message", description="Setup your own goodbye message.")
@implements(SlashSubCommand)
async def message_setter(context: SlashContext) -> Optional[ResponseProxy]:
    data = await greeting.bot.goodbye_handler.get_data(context.guild_id)
    if not data:
        return await context.respond(
            embed=Embed(
                description="You need to setup a goodbye channel first.",
                color=await greeting.bot.color_for(context.get_guild()),
            )
        )
    await greeting.bot.goodbye_handler.update_message(
        context, context.options.message.replace("\\n", "\n")
    )
    await context.respond(
        embed=Embed(
            description=context.options.message.replace("\\n", "\n"),
            color=await greeting.bot.color_for(context.get_guild()),
        ).set_author(name="Changed goodbye Message to :")
    )


@_goodbye.child
@option(name="hex", description="New hex color.")
@command(name="color", description="Change the color of goodbye embeds.")
@implements(SlashSubCommand)
async def hex_setter(context: SlashContext) -> Optional[ResponseProxy]:
    data = await greeting.bot.goodbye_handler.get_data(context.guild_id)
    if not data:
        return await context.respond(
            embed=Embed(
                description="You need to setup a goodbye channel first.",
                color=await greeting.bot.color_for(context.get_guild()),
            )
        )
    try:
        int(context.options.hex, 16)
    except:
        return await context.respond(
            embed=Embed(
                color=await greeting.bot.color_for(context.get_guild()),
                description="`hex` must be a valid Hexcode.",
            ),
            reply=True,
        )
    await greeting.bot.goodbye_handler.update_color(context, context.options.hex)
    await context.respond(
        embed=Embed(
            description=f"Changed goodbye Embed hex to `{context.options.hex}`",
            color=await greeting.bot.goodbye_handler.get_goodbye_hex_code(
                context.get_guild()
            ),
        )
    )


@_goodbye.child
@command(name="remove", description="Remove all goodbye related data for the server.")
@implements(SlashSubCommand)
async def goodbye_remover(context: SlashContext) -> Optional[ResponseProxy]:
    data = await greeting.bot.goodbye_handler.get_data(context.guild_id)
    if not data:
        return await context.respond(
            embed=Embed(
                description="This server does not have a goodbye configuration yet.",
                color=await greeting.bot.color_for(context.get_guild()),
            )
        )
    c = await greeting.bot.goodbye_handler.connection.cursor()
    await c.execute(
        """
        DELETE FROM goodbye
        WHERE guild_id = ?
        """,
        (str(context.guild_id)),
    )
    await greeting.bot.goodbye_handler.connection.commit()


def load(bot: Gojo):
    bot.add_plugin(greeting)
