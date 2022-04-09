from datetime import datetime

from lightbulb.plugins import Plugin
from lightbulb.app import BotApp
from lightbulb.commands.base import Command
from lightbulb.context.slash import SlashContext
from lightbulb.help_command import BaseHelpCommand

from hikari.embeds import Embed

from ..core.bot import Gojo


class MyHelp(BaseHelpCommand):
    def __init__(self, bot: BotApp) -> None:
        self._bot: Gojo = bot
        super().__init__(bot)

    async def send_bot_help(self, context: SlashContext) -> None:
        embed = (
            Embed(
                color=await self._bot.color_for(context.get_guild()), timestamp=datetime.now().astimezone()
            )
            .set_author(name=f"{self._bot.get_me().username.upper()} HELP")
            .set_footer(
                text=f"Requested by {context.author}", icon=context.author.avatar_url
            )
            .set_thumbnail(self._bot.get_me().avatar_url)
        )
        for _plugin in self._bot.plugins:
            plugin: Plugin = self._bot.get_plugin(_plugin)
            if getattr(plugin, "help_ignore", None):
                continue
            embed.add_field(
                name=f"{getattr(plugin, 'emoji', None) or ''} {plugin.name}",
                value=plugin.description,
            )

        await context.respond(embed=embed)

    async def send_plugin_help(self, context: SlashContext, plugin: Plugin) -> None:
        all_slash_cmds = (
            self._bot.get_slash_command(command) for command in self._bot.slash_commands
        )
        plugin_slash_cmds = (
            command for command in all_slash_cmds if command.plugin == plugin
        )
        embed = (
            Embed(color=await self._bot.color_for(context.get_guild()))
            .set_author(name=f"{plugin.name.upper()} HELP")
            .set_footer(
                text=f"Requested by {context.author}", icon=context.author.avatar_url
            )
            .set_thumbnail(self._bot.get_me().avatar_url)
        )
        embed.description = "\n".join(
            f"`\\{command.name}` : {command.description}"
            for command in plugin_slash_cmds
        )
        await context.respond(embed=embed)

    async def send_command_help(self, context: SlashContext, command: Command) -> None:
        return await super().send_command_help(context, command)
    async def send_group_help(self, context: SlashContext, group) -> None:
        return await super().send_group_help(context, group)

def load(bot:Gojo):
    bot.help_command = MyHelp(bot)