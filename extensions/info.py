from __future__ import annotations

import datetime

import hikari
import lightbulb

from core.bot import Gojo
from core.paginators import InfoEmbedPag


class InfoPlugin(lightbulb.Plugin):
    def __init__(self) -> None:
        self.bot: Gojo
        self.pos = 1
        super().__init__(
            name="info",
            description="View details about server related entities.",
        )
        self.add_checks(lightbulb.guild_only)


def get_timestamp(date_time: datetime.datetime) -> str:
    return f"<t:{int(date_time.timestamp())}:R>"


async def get_base_embed_for_member(member: hikari.Member) -> hikari.Embed:
    embed = (
        hikari.Embed(
            timestamp=datetime.datetime.now().astimezone(),
            color=await member.app.color_for(member.get_guild()),
        )
        .set_author(name=str(member))
        .set_thumbnail(member.display_avatar_url)
    )
    return embed


async def get_base_embed_for_role(role: hikari.Role) -> hikari.Embed:
    embed = (
        hikari.Embed(
            timestamp=datetime.datetime.now().astimezone(),
            color=await role.app.color_for(role.app.cache.get_guild(role.guild_id)),
        )
        .set_author(name=str(role))
        .set_thumbnail(role.icon_url)
    )
    return embed


info = InfoPlugin()


@info.command
@lightbulb.option(
    name="member",
    description="Target member to get information about",
    type=hikari.Member,
    required=False,
)
@lightbulb.command(name="userinfo", description="Get information about a member.")
@lightbulb.implements(lightbulb.SlashCommand)
async def userinfo(context: lightbulb.SlashContext) -> None:
    member = context.options.member or context.member
    status_emojis = {
        "online": info.bot.cache.get_emoji(969613502576742450),
        "idle": info.bot.cache.get_emoji(969613426378821712),
        "dnd": info.bot.cache.get_emoji(969613864280920115),
        "offline": info.bot.cache.get_emoji(969670664950775919),
    }
    status_emoji = status_emojis.get(
        member.get_presence().visible_status.lower()
        if member.get_presence()
        else "offline"
    )
    basic_info_dict = {
        "🆔 user ID": member.id,
        "📥 joined server": get_timestamp(member.joined_at),
        f"{info.bot.custom_emojis.discord} joined discord": get_timestamp(
            member.created_at
        ),
        f"{info.bot.custom_emojis.online } status": status_emoji.__str__()
        + (
            member.get_presence().visible_status if member.get_presence() else "offline"
        ).title(),
        f"{info.bot.custom_emojis.role_icon } number of roles": len(member.get_roles()),
        "🛑 top role": member.get_top_role() if member.get_top_role() else "No roles",
        "📛 Nickname": member.nickname or "No nickname",
        f"{info.bot.custom_emojis.bot_icon} Bot account": "Yes"
        if member.is_bot
        else "No",
    }

    basic = await get_base_embed_for_member(member)
    basic.description = "\n".join(
        f"**{key.title()}** : {value}" for key, value in basic_info_dict.items()
    )
    basic.title = "BASIC INFO"

    role_embed = await get_base_embed_for_member(member)
    role_embed.description = " , ".join(
        f"{role.mention}" for role in member.get_roles()
    )
    role_embed.title = "ROLES INFO"

    perms_embed = await get_base_embed_for_member(member)
    perms_embed.description = (
        " , ".join(
            str(permission).title().replace("_", " ")
            for permission in lightbulb.utils.permissions_for(member)
        )
        or "No permissions."
    )
    perms_embed.title = "PERMISSION INFO"

    pag = InfoEmbedPag(context)
    pag.add_embeds(basic, role_embed, perms_embed)
    res = await context.respond(embed=basic, components=pag.build())
    msg = await res.message()
    pag.start(msg)


@info.command
@lightbulb.option(name="role", description="Role to get info about.", type=hikari.Role)
@lightbulb.command(name="roleinfo", description="Info about mentioned role.")
@lightbulb.implements(lightbulb.SlashCommand)
async def roleinfo(context: lightbulb.SlashContext) -> None:
    role: hikari.Role = context.options.role
    basic_info = {
        "📛 name": role.name,
        "🆔 ID": role.id,
        f"{info.bot.custom_emojis.member_icon} members with role": len(
            [
                mem
                for mem in context.get_guild().get_members().values()
                if role in mem.get_roles()
            ]
        ),
        "🟦 color": role.color,
        "✏️ created": get_timestamp(role.created_at),
        "🚩 hoist": role.is_hoisted,
        f"{info.bot.custom_emojis.mention_icon} mentionable?": role.is_mentionable,
        "`@` mention": f"`{role.mention}`",
        "🔢 position": role.position,
    }

    base_embed = await get_base_embed_for_role(role)
    base_embed.description = "\n".join(
        f"**{key.title()}** : {value}" for key, value in basic_info.items()
    )
    base_embed.title = "BASIC INFO"

    members_embed = await get_base_embed_for_role(role)
    members_embed.description = " , ".join(
        mem.mention
        for mem in context.get_guild().get_members().values()
        if role in mem.get_roles()
    )
    members_embed.title = (
        ("MEMBERS WITH ROLE" or "No users with this role")
        if role.id != context.guild_id
        else "Everyone"
    )

    perm_embed = await get_base_embed_for_role(role)
    perm_embed.description = (
        " , ".join(perm.name.title().replace("_", " ") for perm in role.permissions)
        or "No perms"
    )
    pag = InfoEmbedPag(context)
    pag.add_embeds(base_embed, members_embed, perm_embed)
    res = await context.respond(embed=base_embed, components=pag.build())
    msg = await res.message()
    pag.start(msg)


@info.command
@lightbulb.command(name="serverinfo", description="View information about the server.")
@lightbulb.implements(lightbulb.SlashCommand)
async def serverinfo(context: lightbulb.SlashContext) -> None:
    guild = context.get_guild()
    color = await info.bot.color_for(guild)
    emoji_class = info.bot.custom_emojis
    base_embed = (
        hikari.Embed(title="SERVER INFO", color=color)
        .set_author(name=f"INFORMATION ABOUT {guild.name}")
        .set_thumbnail(guild.icon_url)
    )
    base_data = {
        "📛 name": guild.name,
        "🆔 id": context.guild_id,
        f"{emoji_class.owner_icon} owner": f"<@{guild.owner_id}> | `{info.bot.cache.get_user(guild.owner_id)}`",
        "✏️ created on": f"{guild.created_at.strftime('%d %b %Y')} | {get_timestamp(guild.created_at)}",
        f"{emoji_class.member_icon} total members": len(guild.get_members()),
        f"{emoji_class.text_channel_icon} total channels": len(
            [
                channel
                for channel in guild.get_channels().values()
                if isinstance(channel, hikari.TextableGuildChannel)
                or isinstance(channel, hikari.GuildVoiceChannel)
            ]
        ),
        f"{emoji_class.voice_channel_icon} afk channel": f"<#{guild.afk_channel_id}>"
        if guild.afk_channel_id
        else "None",
        "😄 emojis": len(guild.get_emojis()),
        f"{emoji_class.role_icon } total roles": len(guild.get_roles()),
        f"{emoji_class.emoji_by_id(974393185335922718)} Boost Tier/Boosts": f"Level {guild.premium_tier} | {guild.premium_subscription_count} Boosters",
    }
    base_embed.description = "\n".join(
        f"**{key.title()}** : {value}" for key, value in base_data.items()
    )
    base_embed.set_image(guild.banner_url)

    channel_embed = hikari.Embed(title="CHANNELS", color=color)
    channels = [
        channel
        for channel in guild.get_channels().values()
        if isinstance(channel, hikari.TextableGuildChannel)
        or isinstance(channel, hikari.GuildVoiceChannel)
    ]
    category_channels = [
        channel
        for channel in guild.get_channels().values()
        if isinstance(channel, hikari.GuildCategory)
    ]
    text_channels = [
        channel
        for channel in guild.get_channels().values()
        if isinstance(channel, hikari.TextableGuildChannel)
    ]
    voice_channels = [
        channel
        for channel in guild.get_channels().values()
        if isinstance(channel, hikari.GuildVoiceChannel)
    ]

    news_channels = [
        channel
        for channel in guild.get_channels().values()
        if isinstance(channel, hikari.GuildNewsChannel)
    ]

    channel_data = {
        f"{emoji_class.emoji_by_id(974750756966121522)} total channels": len(channels),
        f"{emoji_class.emoji_by_id(974750403608596610)} total categories": len(
            category_channels
        ),
        f"{emoji_class.text_channel_icon} text channels": len(text_channels),
        f"{emoji_class.voice_channel_icon} voice channels": len(voice_channels),
        f"{emoji_class.news_channel} news channels": len(news_channels),
        f"⚙️ system channel": (
            f"`{guild.get_channel(guild.system_channel_id).name}` | {guild.get_channel(guild.system_channel_id).mention}"
            if guild.system_channel_id
            else "No System channel set."
        ),
        f"{emoji_class.rules_channel} rules channel": (
            f"`{guild.get_channel(guild.rules_channel_id).name}` | {guild.get_channel(guild.rules_channel_id).mention}"
            if guild.rules_channel_id
            else "No Rule channel set."
        ),
        f"💤 afk channel": (
            f"`{guild.get_channel(guild.afk_channel_id).name}` | {guild.get_channel(guild.afk_channel_id).mention}"
            if guild.afk_channel_id
            else "No AFK channel set."
        ),
    }

    channel_embed.description = "\n".join(
        f"**{key.title()}** : {value}" for key, value in channel_data.items()
    )
    server_roles = [r for r in guild.get_roles().values()]
    server_roles.sort(key=lambda role: role.position, reverse=True)
    role_embed = hikari.Embed(color=color, title="ROLES")
    role_data = {
        f"{emoji_class.role_icon} total roles": len(guild.get_roles()),
        "⬆️ top role": f"`{server_roles[0].name}` | {server_roles[0].mention}",
        f"{emoji_class.emoji_by_id(975521766812299334)} roles with administrator": len(
            [
                role
                for role in guild.get_roles().values()
                if hikari.Permissions.ADMINISTRATOR in role.permissions
            ]
        ),
    }
    role_embed.description = "\n".join(
        f"**{key.title()}** : {value}" for key, value in role_data.items()
    )
    role_embed.add_field(
        name="@everyone roles perms.",
        value=", ".join(perm.name.title() for perm in server_roles[-1].permissions),
    )

    pag = InfoEmbedPag(context, with_select=True)
    pag.add_embeds(base_embed, channel_embed, role_embed)
    res = await context.respond(embed=base_embed, components=pag.build())
    msg = await res.message()
    pag.start(msg)


def load(bot: Gojo) -> None:
    bot.add_plugin(info)
