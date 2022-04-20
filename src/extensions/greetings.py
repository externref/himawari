from __future__ import annotations

import hikari
import lightbulb

from ..core.bot import Gojo


class Greeting(lightbulb.Plugin):
    def __init__(self) -> None:
        self.bot: Gojo
        self.pos = 3
        super().__init__(
            name="greeting",
            description="Welcome/Leave module to greet new users and goodbyes.",
        )
        self.add_checks(
            lightbulb.has_guild_permissions(hikari.Permissions.MANAGE_GUILD)
        )


greeting = Greeting()


def process_raw_message(message: str, user: hikari.User, guild: hikari.Guild) -> str:
    message_to_return = (
        message.replace("$usermention", str(user.mention))
        .replace("$userid", str(user.id))
        .replace("$username", str(user.username))
        .replace("$userdiscriminator", str(user.discriminator))
        .replace("$userdiscrim", str(user.discriminator))
        .replace("$user", str(user))
        .replace("$servername", str(guild.name))
        .replace("$server", str(guild.name))
        .replace("$membercount", str(len(guild.get_members())))
    )
    return message_to_return


@greeting.listener(hikari.MemberCreateEvent)
async def new_member(event: hikari.MemberCreateEvent) -> None:
    data = await greeting.bot.welcome_handler.get_data(event.guild_id)
    if not data:
        return
    channel = await greeting.bot.welcome_handler.get_welcome_channel(event.get_guild())
    if not channel:
        return
    raw_message = await greeting.bot.welcome_handler.get_welcome_message(
        event.get_guild()
    )
    embed = hikari.Embed(
        description=process_raw_message(raw_message, event.member, event.get_guild()),
        color=await greeting.bot.welcome_handler.get_welcome_hex_code(
            event.get_guild()
        ),
    )
    embed.set_author(name=str(event.member)).set_thumbnail(event.member.avatar_url)
    try:
        await channel.send(embed=embed)
    except hikari.ForbiddenError:
        ...


@greeting.listener(hikari.MemberDeleteEvent)
async def remove_member(event: hikari.MemberDeleteEvent) -> None:
    data = await greeting.bot.goodbye_handler.get_data(event.guild_id)
    if not data:
        return
    channel = await greeting.bot.goodbye_handler.get_goodbye_channel(event.get_guild())
    if not channel:
        return
    raw_message = await greeting.bot.goodbye_handler.get_goodbye_message(
        event.get_guild()
    )
    embed = hikari.Embed(
        description=process_raw_message(raw_message, event.user, event.get_guild()),
        color=await greeting.bot.goodbye_handler.get_goodbye_hex_code(
            event.get_guild()
        ),
    )
    embed.set_author(name=str(event.user)).set_thumbnail(event.user.avatar_url)
    try:
        await channel.send(embed=embed)
    except hikari.ForbiddenError:
        ...


@greeting.command
@lightbulb.command(
    name="greetingvariables",
    description="Variables allowed in welcome/goodbye messages",
)
@lightbulb.implements(lightbulb.SlashCommand)
async def variables(context: lightbulb.SlashContext) -> None:
    await context.respond(
        embed=hikari.Embed(
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
@lightbulb.command(
    name="welcome",
    description="Welcome commands to greet new members joining your server.",
)
@lightbulb.implements(lightbulb.SlashCommandGroup)
async def _welcome(_: lightbulb.SlashContext) -> None:
    ...


@_welcome.child
@lightbulb.option(
    name="channel",
    description="Channel to send greeting messages in.",
    type=hikari.TextableGuildChannel,
    required=True,
)
@lightbulb.command(name="channel", description="Change/set welcome channel.")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def channel_setter(
    context: lightbulb.SlashContext,
) -> None | lightbulb.ResponseProxy:
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
        embed=hikari.Embed(
            description=f"Changed greeting channel to `{context.options.channel.name}`",
            color=await greeting.bot.color_for(context.get_guild()),
        )
    )


@_welcome.child
@lightbulb.option(
    name="message",
    description="New welcome message.",
    required=True,
)
@lightbulb.command(name="message", description="Setup your own welcome message.")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def message_setter(
    context: lightbulb.SlashContext,
) -> None | lightbulb.ResponseProxy:
    data = await greeting.bot.welcome_handler.get_data(context.guild_id)
    if not data:
        return await context.respond(
            embed=hikari.Embed(
                description="You need to setup a welcome channel first.",
                color=await greeting.bot.color_for(context.get_guild()),
            )
        )
    await greeting.bot.welcome_handler.update_message(
        context, context.options.message.replace("\\n", "\n")
    )
    await context.respond(
        embed=hikari.Embed(
            description=context.options.message.replace("\\n", "\n"),
            color=await greeting.bot.color_for(context.get_guild()),
        ).set_author(name="Changed Welcome Message to :")
    )


@_welcome.child
@lightbulb.option(
    name="hex",
    description="New hex color.",
    required=True,
)
@lightbulb.command(name="color", description="Change the color of welcome embeds.")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def hex_setter(context: lightbulb.SlashContext) -> None | lightbulb.ResponseProxy:
    data = await greeting.bot.welcome_handler.get_data(context.guild_id)
    if not data:
        return await context.respond(
            embed=hikari.Embed(
                description="You need to setup a welcome channel first.",
                color=await greeting.bot.color_for(context.get_guild()),
            )
        )
    try:
        int(context.options.hex, 16)
    except:
        return await context.respond(
            embed=hikari.Embed(
                color=await greeting.bot.color_for(context.get_guild()),
                description="`hex` must be a valid Hexcode.",
            ),
            reply=True,
        )
    await greeting.bot.welcome_handler.update_color(context, context.options.hex)
    await context.respond(
        embed=hikari.Embed(
            description=f"Changed welcome Embed hex to `{context.options.hex}`",
            color=await greeting.bot.welcome_handler.get_welcome_hex_code(
                context.get_guild()
            ),
        )
    )


@_welcome.child
@lightbulb.command(
    name="remove", description="Remove all welcome related data for the server."
)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def welcome_remover(
    context: lightbulb.SlashContext,
) -> None | lightbulb.ResponseProxy:
    data = await greeting.bot.welcome_handler.get_data(context.guild_id)
    if not data:
        return await context.respond(
            embed=hikari.Embed(
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
@lightbulb.command(
    name="goodbye",
    description="Goodbye commands.",
)
@lightbulb.implements(lightbulb.SlashCommandGroup)
async def _goodbye(_: lightbulb.SlashContext) -> None:
    ...


@_goodbye.child
@lightbulb.option(
    name="channel",
    description="Channel to send greeting messages in.",
    type=hikari.TextableGuildChannel,
    required=True,
)
@lightbulb.command(name="channel", description="Change/set goodbye channel.")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def channel_setter(
    context: lightbulb.SlashContext,
) -> None | lightbulb.ResponseProxy:
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
        embed=hikari.Embed(
            description=f"Changed goodbye channel to `{context.options.channel.name}`",
            color=await greeting.bot.color_for(context.get_guild()),
        )
    )


@_goodbye.child
@lightbulb.option(
    name="message",
    description="New goodbye message.",
    required=True,
)
@lightbulb.command(name="message", description="Setup your own goodbye message.")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def message_setter(
    context: lightbulb.SlashContext,
) -> None | lightbulb.ResponseProxy:
    data = await greeting.bot.goodbye_handler.get_data(context.guild_id)
    if not data:
        return await context.respond(
            embed=hikari.Embed(
                description="You need to setup a goodbye channel first.",
                color=await greeting.bot.color_for(context.get_guild()),
            )
        )
    await greeting.bot.goodbye_handler.update_message(
        context, context.options.message.replace("\\n", "\n")
    )
    await context.respond(
        embed=hikari.Embed(
            description=context.options.message.replace("\\n", "\n"),
            color=await greeting.bot.color_for(context.get_guild()),
        ).set_author(name="Changed goodbye Message to :")
    )


@_goodbye.child
@lightbulb.option(
    name="hex",
    description="New hex color.",
    required=True,
)
@lightbulb.command(name="color", description="Change the color of goodbye embeds.")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def hex_setter(context: lightbulb.SlashContext) -> None | lightbulb.ResponseProxy:
    data = await greeting.bot.goodbye_handler.get_data(context.guild_id)
    if not data:
        return await context.respond(
            embed=hikari.Embed(
                description="You need to setup a goodbye channel first.",
                color=await greeting.bot.color_for(context.get_guild()),
            )
        )
    try:
        int(context.options.hex, 16)
    except:
        return await context.respond(
            embed=hikari.Embed(
                color=await greeting.bot.color_for(context.get_guild()),
                description="`hex` must be a valid Hexcode.",
            ),
            reply=True,
        )
    await greeting.bot.goodbye_handler.update_color(context, context.options.hex)
    await context.respond(
        embed=hikari.Embed(
            description=f"Changed goodbye Embed hex to `{context.options.hex}`",
            color=await greeting.bot.goodbye_handler.get_goodbye_hex_code(
                context.get_guild()
            ),
        )
    )


@_goodbye.child
@lightbulb.command(
    name="remove", description="Remove all goodbye related data for the server."
)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def goodbye_remover(
    context: lightbulb.SlashContext,
) -> None | lightbulb.ResponseProxy:
    data = await greeting.bot.goodbye_handler.get_data(context.guild_id)
    if not data:
        return await context.respond(
            embed=hikari.Embed(
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


def unload(bot: Gojo):
    bot.remove_plugin(greeting)
