from __future__ import annotations

from datetime import datetime

import hikari
import lightbulb

from ..core.bot import Gojo


class MyHelp(lightbulb.BaseHelpCommand):
    def __init__(self, bot: lightbulb.BotApp) -> None:
        self._bot: Gojo = bot
        super().__init__(bot)

    async def send_help(self, context: lightbulb.SlashContext, obj: str | None) -> None:
        if obj is None:
            await self.send_bot_help(context)
            return
        s_cmd = self.app.get_slash_command(obj.lower())
        if s_cmd is not None and not s_cmd.hidden:
            if isinstance(s_cmd, lightbulb.SlashCommandGroup):
                await self.send_group_help(context, s_cmd)
                return
            await self.send_command_help(context, s_cmd)
            return
        plugin = self.app.get_plugin(obj.lower())
        if plugin is not None:
            await self.send_plugin_help(context, plugin)
            return
        await self.object_not_found(context, obj)

    async def send_bot_help(self, context: lightbulb.SlashContext) -> None:

        embed = (
            hikari.Embed(
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
                (
                    f"[Invite]({self._bot.invite_url}) | [Documentation](http://gojo.rtfd.io/) |"
                    + "[Source](https://github.com/sarthhh/gojo) | [Support](https://discord.gg/xpRd6tB5TF) \n"
                ),
                "Use `/config <module>` to check my configs for the server.",
            )
        )
        plugins = [self._bot.get_plugin(_plugin) for _plugin in self._bot.plugins]
        plugins.sort(key=lambda f: f.pos)
        for plugin in plugins:
            if getattr(plugin, "help_ignore", None):
                continue
            embed.add_field(
                name=f"{getattr(plugin, 'emoji', None) or ''} {plugin.name.upper()} COMMANDS (`/help {plugin.name}`)",
                value=plugin.description,
            )

        comps = hikari.impl.ActionRowBuilder()
        comps.add_button(hikari.ButtonStyle.LINK, self._bot.invite_url).set_label(
            "Invite Me"
        ).add_to_container()
        comps.add_button(
            hikari.ButtonStyle.LINK, "https://github.com/sarthhh/gojo"
        ).set_label("Source Code").add_to_container()
        comps.add_button(hikari.ButtonStyle.LINK, "http://gojo.rtfd.io/").set_label(
            "Docs"
        ).add_to_container()
        await context.respond(embed=embed, component=comps)

    async def send_plugin_help(
        self, context: lightbulb.SlashContext, plugin: lightbulb.Plugin
    ) -> None:

        embed = (
            hikari.Embed(
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
            if isinstance(command, lightbulb.SlashCommandGroup):
                description += (
                    "\n".join(
                        f"> `/{command.name} {command.subcommands.get(sub_c).name}` : {command.subcommands.get(sub_c).description}"
                        for sub_c in command.subcommands
                    )
                    + "\n"
                )
        embed.description = description
        await context.respond(embed=embed)

    async def send_command_help(
        self, context: lightbulb.SlashContext, command: lightbulb.Command
    ) -> None:
        embed = (
            hikari.Embed(
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
        self, context: lightbulb.SlashContext, group: lightbulb.SlashCommandGroup
    ) -> None:
        embed = (
            hikari.Embed(color=await self._bot.color_for(context.get_guild()))
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
