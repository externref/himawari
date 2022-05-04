from __future__ import annotations

import hikari
import lightbulb

from ..core.bot import Gojo


class Starboard(lightbulb.Plugin):
    def __init__(self) -> None:
        self.bot: Gojo
        self.pos = 4
        self.message_cache_state: dict[str, int] = {}
        super().__init__(
            name="starboard",
            description="Setup a starboard for important messages to appear in a channel.",
        )
        self.add_checks(
            lightbulb.has_guild_permissions(hikari.Permissions.MANAGE_GUILD)
        )


starboard = Starboard()


@starboard.listener(hikari.GuildReactionAddEvent)
async def reaction_added(event: hikari.GuildReactionAddEvent) -> None:
    handler = starboard.bot.starboard_handler
    if not starboard.bot.is_alive:
        return
    if not getattr(handler, "connection", None):
        return
    if await handler.is_blacklisted(event.message_id):
        return
    guild = starboard.bot.cache.get_guild(event.guild_id)
    data = await handler.get_data(guild)
    if not data:
        return
    channel = await handler.get_channel(guild)
    if not channel:
        return
    emoji_raw = await handler.get_emoji(guild)
    if emoji_raw == "default":
        emoji = "⭐"
    elif emoji_raw.startswith("custom"):
        emoji = starboard.bot.cache.get_emoji(int(emoji_raw.replace("custom", "")))
    if not emoji:
        return

    def check(emoji, _event: str | hikari.CustomEmoji):
        if event.emoji_id:

            return emoji in (
                f"<:{event.emoji_name}:{event.emoji_id}>",
                f"<a:{event.emoji_name}:{event.emoji_id}>",
            )
        return emoji == event.emoji_name

    if check(str(emoji), event):
        cache = starboard.message_cache_state.get(str(event.message_id))
        if not cache:
            starboard.message_cache_state[str(event.message_id)] = 1
        else:
            starboard.message_cache_state[str(event.message_id)] = cache + 1
    min_count = await handler.get_emoji_count(guild)
    count = starboard.message_cache_state.get(str(event.message_id))
    if count and count >= min_count:
        message = starboard.bot.cache.get_message(event.message_id)
        if not message:
            try:
                message = await starboard.bot.rest.fetch_message(
                    event.channel_id, event.message_id
                )
            except hikari.NotFoundError:
                await handler.blacklist_message(event.message_id)
        jump_url = f"https://discord.com/channels/{event.guild_id}/{event.channel_id}/{event.message_id}"
        to_send = message.content
        image_url = None
        if not to_send and len(message.embeds):
            to_send = "Attached Embeds below."
        elif message.attachments:
            image_url = message.attachments[0].url
        if not any((to_send, image_url)):
            return

        embed = hikari.Embed(
            title=f"Message Sent in #{starboard.bot.cache.get_guild_channel(event.channel_id).name}",
            url=jump_url,
            color=await starboard.bot.color_for(guild),
        )
        embed.set_author(name=event.member.__str__(), icon=event.member.avatar_url)
        if image_url:
            embed.set_image(image_url)
        if to_send:
            embed.description = to_send
        try:
            embeds = [embed]
            if message.embeds:
                embeds.extend(message.embeds)
            await channel.send(embeds=embeds)
        except hikari.ForbiddenError:
            pass
        await handler.blacklist_message(event.message_id)


@starboard.listener(hikari.GuildReactionDeleteEvent)
async def reaction_removed(event: hikari.GuildReactionDeleteEvent) -> None:
    handler = starboard.bot.starboard_handler
    if not starboard.bot.is_alive:
        return
    if not getattr(handler, "connection", None):
        return
    if await handler.is_blacklisted(event.message_id):
        return
    guild = starboard.bot.cache.get_guild(event.guild_id)
    data = await handler.get_data(guild)
    if not data:
        return
    channel = await handler.get_channel(guild)
    if not channel:
        return
    emoji_raw = await handler.get_emoji(guild)
    if emoji_raw == "default":
        emoji = "⭐"
    elif emoji_raw.startswith("custom"):
        emoji = starboard.bot.cache.get_emoji(int(emoji_raw.replace("custom", "")))

    if str(emoji) == event.emoji_name:
        cache = starboard.message_cache_state.get(str(event.message_id))
        if not cache:
            return
        else:
            starboard.message_cache_state[str(event.message_id)] = cache - 1


@starboard.command
@lightbulb.command(name="starboard", description="Starboard commands.")
@lightbulb.implements(lightbulb.SlashCommandGroup)
async def starboard_base(context: lightbulb.SlashContext) -> None:
    ...


@starboard_base.child
@lightbulb.option(
    name="channel",
    description="The starboard channel",
    type=hikari.TextableGuildChannel,
    required=True,
)
@lightbulb.command(
    name="channel",
    description="Set/Change The starboard Channel.",
)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def set_channel(context: lightbulb.SlashContext) -> None:
    handler = starboard.bot.starboard_handler
    data = await handler.get_data(context.get_guild())
    channel = context.get_guild().get_channel(context.options.channel.id)

    if data:
        await handler.update_channel(channel)
    else:
        await handler.insert_data(channel)
    await context.respond(
        embed=hikari.Embed(
            description=f"`{context.options.channel}` is the new starboard channel.",
            color=await starboard.bot.color_for(context.get_guild()),
        )
    )


@starboard_base.child
@lightbulb.option(
    name="emoji",
    description="The emoji by which starboard is triggered",
    type=hikari.Emoji,
    required=True,
)
@lightbulb.command(name="emoji", description="Set the starboard emoji, `⭐` by default.")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def set_emoji(context: lightbulb.SlashContext) -> None | lightbulb.ResponseProxy:
    handler = starboard.bot.starboard_handler
    color = await starboard.bot.color_for(context.get_guild())
    data = await handler.get_data(context.get_guild())
    if not data:
        return await context.respond(
            embed=hikari.Embed(
                description="You don't have a starboard channel setup yet.", color=color
            )
        )

    emoji = await lightbulb.EmojiConverter(context).convert(context.options.emoji)
    if isinstance(emoji, hikari.CustomEmoji):
        if emoji.id not in (
            emoji_.id for emoji_ in context.get_guild().get_emojis().values()
        ):

            return await context.respond(
                embed=hikari.Embed(
                    description="The custom emoji must be a default emoji or an emoji from this server.",
                    color=color,
                )
            )
        to_enter = f"custom{emoji.id}"
    elif emoji.name == "⭐":
        to_enter = "default"
    else:
        return await context.respond(
            embed=hikari.Embed(
                color=color, description="`emoji` must be a custom emoji or `⭐`"
            )
        )
    await handler.update_emoji(context.get_guild(), to_enter)
    await context.respond(
        embed=hikari.Embed(
            color=color, description=f"{emoji} is the new starboard emoji."
        )
    )


@starboard_base.child
@lightbulb.option(
    name="number", description="Number of reactions", type=int, required=True
)
@lightbulb.command(
    name="min_count",
    description="The minumum number of reactions required to add the message to starboard.",
)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def set_minimum_count(
    context: lightbulb.SlashContext,
) -> None | lightbulb.ResponseProxy:
    handler = starboard.bot.starboard_handler
    color = await starboard.bot.color_for(context.get_guild())
    data = await handler.get_data(context.get_guild())
    if not data:
        return await context.respond(
            embed=hikari.Embed(
                description="You don't have a starboard channel setup yet.", color=color
            )
        )

    await handler.update_min_count(context.get_guild(), context.options.number)
    await context.respond(
        embed=hikari.Embed(
            color=color,
            description=f"Now messages need atleast {context.options.number} reactions to get added to starboard.",
        )
    )


@starboard_base.child
@lightbulb.command(name="remove", description="Remove all starboard related settings.")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def remove_starboard(
    context: lightbulb.SlashContext,
) -> None | lightbulb.ResponseProxy:
    color = await starboard.bot.color_for(context.get_guild())
    handler = starboard.bot.starboard_handler
    data = await handler.get_data(context.get_guild())
    if not data:
        return await context.respond(
            embed=hikari.Embed(
                description="You don't have a starboard channel setup yet.", color=color
            )
        )

    cursor = await handler.connection.cursor()
    await cursor.execute(
        """
        DELETE FROM starboard
        WHERE guild_id = ?
        """,
        (str(context.guild_id),),
    )
    await handler.connection.commit()
    await context.respond(
        embed=hikari.Embed(color=color, description="Removed all starboard configs.")
    )


def load(bot: Gojo) -> None:
    bot.add_plugin(starboard)


def unload(bot: Gojo) -> None:
    bot.remove_plugin(starboard)
