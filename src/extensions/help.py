from __future__ import annotations

from datetime import datetime

from lightbulb.app import BotApp
from lightbulb.plugins import Plugin
from lightbulb.commands.base import Command
from lightbulb.context.slash import SlashContext
from lightbulb.help_command import BaseHelpCommand
from lightbulb.commands.slash import SlashCommandGroup

from hikari.embeds import Embed
from hikari.messages import ButtonStyle
from hikari.impl.special_endpoints import ActionRowBuilder

from ..core.bot import Gojo


class MyHelp(BaseHelpCommand):
    def __init__(self, bot: BotApp) -> None:
        self._bot: Gojo = bot
        super().__init__(bot)

    async def send_help(self, context: SlashContext, obj: str | None) -> None:
        if obj is None:
            await self.send_bot_help(context)
            return
        s_cmd = self.app.get_slash_command(obj.lower())
        if s_cmd is not None and not s_cmd.hidden:
            if isinstance(s_cmd, SlashCommandGroup):
                await self.send_group_help(context, s_cmd)
                return
            await self.send_command_help(context, s_cmd)
            return
        plugin = self.app.get_plugin(obj.lower())
        if plugin is not None:
            await self.send_plugin_help(context, plugin)
            return
        await self.object_not_found(context, obj)

    async def send_bot_help(self, context: SlashContext) -> None:

        embed = (
            Embed(
                color=await self._bot.color_for(context.get_guild()),
                timestamp=datetime.now().astimezone(),
            )
            .set_author(name=f"{self._bot.get_me().username.upper()} HELP")
            .set_footer(
                text=f"Requested by {context.author}", icon=context.author.avatar_url
            )
            .set_thumbnail(self._bot.get_me().avatar_url)
        )
        embed.description = "\n".join(
            (
                "```yaml\n",
                "Prefix for the server: /",
                f"In the server since: {context.get_guild().get_my_member().joined_at.strftime('%d %b %y')}",
                "\n```",
                "Use `/config <module>` to check my configs for the server.",
            )
        )
        for _plugin in self._bot.plugins:
            plugin: Plugin = self._bot.get_plugin(_plugin)
            if getattr(plugin, "help_ignore", None):
                continue
            embed.add_field(
                name=f"{getattr(plugin, 'emoji', None) or ''} {plugin.name.upper()} COMMANDS (`/help {plugin.name}`)",
                value=plugin.description,
            )

        comps = ActionRowBuilder()
        comps.add_button(ButtonStyle.LINK, self._bot.invite_url).set_label(
            "Invite Me"
        ).add_to_container()
        comps.add_button(
            ButtonStyle.LINK, "https://github.com/sarthak-py/gojo"
        ).set_label("Source Code").add_to_container()
        await context.respond(embed=embed, component=comps)

    async def send_plugin_help(self, context: SlashContext, plugin: Plugin) -> None:

        embed = (
            Embed(
                color=await self._bot.color_for(context.get_guild()),
                timestamp=datetime.now().astimezone(),
            )
            .set_author(name=f"{plugin.name.upper()} COMMANDS HELP")
            .set_footer(
                text=f"Requested by {context.author}", icon=context.author.avatar_url
            )
            .set_thumbnail(self._bot.get_me().avatar_url)
        )
        description = ""
        for command in plugin.all_commands:
            description += f"`/{command.name}` : {command.description}\n"
            if isinstance(command, SlashCommandGroup):
                description += (
                    "\n".join(
                        f"> `/{command.name} {command.subcommands.get(sub_c).name}` : {command.subcommands.get(sub_c).description}"
                        for sub_c in command.subcommands
                    )
                    + "\n"
                )
        embed.description = description
        await context.respond(embed=embed)

    async def send_command_help(self, context: SlashContext, command: Command) -> None:
        embed = (
            Embed(
                color=await self._bot.color_for(
                    context.get_guild(),
                ),
                description=command.description,
                timestamp=datetime.now().astimezone(),
            )
            .set_author(name=f"{command.name.upper()} COMMAND HELP")
            .set_footer(
                text=f"Requested by {context.author}", icon=context.author.avatar_url
            )
            .set_thumbnail(self._bot.get_me().avatar_url)
        )
        embed.add_field(name="USAGE", value=f"```fix\n/{command.signature}\n```")
        await context.respond(embed=embed)

    async def send_group_help(
        self, context: SlashContext, group: SlashCommandGroup
    ) -> None:
        embed = (
            Embed(color=await self._bot.color_for(context.get_guild()))
            .set_author(name=f"{group.name.upper()} COMMAND HELP")
            .set_footer(
                text=f"Requested by {context.author}", icon=context.author.avatar_url
            )
            .set_thumbnail(self._bot.get_me().avatar_url)
        )
        description = f"`/{group.name}` : {group.description}\n"
        description += (
            "\n".join(
                f"> `/{group.name} {group.subcommands.get(sub_c).name}` : {group.subcommands.get(sub_c).description}"
                for sub_c in group.subcommands
            )
            + "\n"
        )
        embed.description = description
        await context.respond(embed=embed)


def load(bot: Gojo):
    bot.help_command = MyHelp(bot)


def unload(bot: Gojo):
    bot.help_command = None
