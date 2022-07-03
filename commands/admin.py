import hikari
import lightbulb

from core.bot import Bot


class Plugin(lightbulb.Plugin):
    bot: Bot


plugin = Plugin("Admin")
plugin.add_checks(lightbulb.has_guild_permissions(hikari.Permissions.ADMINISTRATOR))


@plugin.command
@lightbulb.option(
    "channel",
    "The channel to send confessions in.",
    type=hikari.TextableGuildChannel,
    channel_types=[hikari.ChannelType.GUILD_TEXT],
)
@lightbulb.command(
    "set_channel",
    description="Set confession channel for the server.",
    pass_options=True,
)
@lightbulb.implements(lightbulb.SlashCommand)
async def set_channel(
    context: lightbulb.SlashContext, channel: hikari.GuildTextChannel
) -> None:
    if (guild_id := context.guild_id) is None:
        return
    member = plugin.bot.cache.get_member(
        guild_id, plugin.bot.me.id
    ) or await plugin.bot.rest.fetch_member(guild_id, plugin.bot.me.id)
    ch: hikari.GuildTextChannel = plugin.bot.cache.get_guild_channel(channel.id)  # type: ignore
    if not (
        lightbulb.utils.permissions_in(ch, member, include_guild_permissions=False)
        & (hikari.Permissions.SEND_MESSAGES | hikari.Permissions.EMBED_LINKS)
    ):
        await context.respond(
            embed=hikari.Embed(
                color=plugin.bot.color,
                description="I am missing `SEND_MESSAGES` and `EMBED_LINKS` permissions in the channel you mentioned.\nNote: These permissions need to be explicitly turned on for the bot.",
            )
        )
        return
    await plugin.bot.db.set_confession_channel(guild_id, channel.id)
    await context.respond(
        embed=hikari.Embed(
            color=plugin.bot.color,
            description=f"Set confession channel to {ch.name} ( {ch.mention} )",
        )
    )


def load(bot: Bot) -> None:
    bot.add_plugin(plugin)
