from __future__ import annotations

import datetime

import hikari
import lightbulb

from ..core.bot import Gojo
from ..core.paginators import InfoEmbedPag


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
        "user ID": member.id,
        "joined server": get_timestamp(member.joined_at),
        "joined discord": get_timestamp(member.created_at),
        "status": status_emoji.__str__()
        + (
            member.get_presence().visible_status if member.get_presence() else "offline"
        ).title(),
        "number of roles": len(member.get_roles()),
        "top role": member.get_top_role() if member.get_top_role() else "No roles",
        "Nickname": member.nickname or "No nickname",
        "Bot account": "Yes" if member.is_bot else "No",
    }

    basic = await get_base_embed_for_member(member)
    basic.description = "\n".join(
        f"**{key.title()}** : {value}" for key, value in basic_info_dict.items()
    )
    basic.title = "BASIC INFO"

    role_embed = await get_base_embed_for_member(member)
    role_embed.description = "\n".join(
        f"{role.mention} : {role.id}" for role in member.get_roles()
    )
    role_embed.title = "ROLES INFO"

    perms_embed = await get_base_embed_for_member(member)
    perms_embed.description = " , ".join(
        str(permission).title().replace("_", " ")
        for permission in lightbulb.utils.permissions_for(member)
    )
    perms_embed.title = "PERMISSION INFO"

    pag = InfoEmbedPag(context)
    pag.add_embeds(basic, role_embed, perms_embed)
    res = await context.respond(embed=basic, components=pag.build())
    msg = await res.message()
    pag.start(msg)


"""
@info.command
@lightbulb.option(name="role", description="Role to get info about.", type=hikari.Role)
@lightbulb.command(name="roleinfo", description="Info about mentioned role.")
async def roleinfo(context: lightbulb.SlashContext) -> None:
    role: hikari.Role = context.options.role
    basic_info= {
        "name" : role.name,
        "ID" : role.id,

    }
"""


def load(bot: Gojo) -> None:
    bot.add_plugin(info)
