from __future__ import annotations

from datetime import datetime

import hikari
import lightbulb
import miru

from core.bot import Gojo


class MyHelp(lightbulb.BaseHelpCommand):
    def __init__(self, bot: lightbulb.BotApp) -> None:
        miru.load(bot)  # loading the bot to miru
        self._bot: Gojo = bot  # setting a custom attr for typehints.
        super().__init__(bot)

    async def send_help(self, context: lightbulb.SlashContext, obj: str | None) -> None:
        if obj is None:
            #  invoking normal help if no obj supplied
            await self.send_bot_help(context)
            return
        s_cmd = self.app.get_slash_command(obj.lower())  # checking for slash commands
        if s_cmd is not None and not s_cmd.hidden:
            # is `s_cmd` a slash command group?
            if isinstance(s_cmd, lightbulb.SlashCommandGroup):
                await self.send_group_help(context, s_cmd)
                return
            # else, sending normal command help.
            await self.send_command_help(context, s_cmd)
            return
        # checking for plugins
        plugin = self.app.get_plugin(obj.lower())
        if plugin is not None:
            await self.send_plugin_help(context, plugin)
            return
        await self.object_not_found(
            context, obj
        )  # sending error message if no obj found.

    async def send_bot_help(self, context: lightbulb.SlashContext) -> None:

        embed = (
            hikari.Embed(
                color=await self._bot.color_for(context.get_guild()),
                timestamp=datetime.now().astimezone(),
            )
            .set_author(
                name=f"{self._bot.get_me().username.upper()} HELP",
                icon=self._bot.get_me().avatar_url,
            )
            .set_footer(
                text=f"Requested by {context.author}", icon=context.author.avatar_url
            )
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
        plugins.sort(
            key=lambda f: f.pos
        )  # sorting the plugins on the basis of their `pos` attribute.
        for plugin in plugins:
            if getattr(
                plugin, "help_ignore", None
            ):  # is the plugin meant to be ignored by the loop?
                continue
            embed.add_field(
                name=f"{getattr(plugin, 'emoji', None) or ''} {plugin.name.upper()} COMMANDS (`/help {plugin.name}`)",
                value=plugin.description,
            )

        view = HelpButtons(self._bot, context)  # initialising the View class
        res = await context.respond(embed=embed, components=view.build())
        msg = await res.message()
        view.start(msg)

    async def send_plugin_help(
        self, context: lightbulb.SlashContext, plugin: lightbulb.Plugin
    ) -> None:

        embed = (
            hikari.Embed(
                color=await self._bot.color_for(context.get_guild()),
                timestamp=datetime.now().astimezone(),
            )
            .set_author(
                name=f"{plugin.name.upper()} COMMANDS HELP",
                icon=self._bot.get_me().avatar_url,
            )
            .set_footer(
                text=f"Requested by {context.author}", icon=context.author.avatar_url
            )
        )
        description = ""
        for command in plugin.all_commands:
            description += f"`/{command.name}` : {command.description}\n"
            if isinstance(
                command, lightbulb.SlashCommandGroup
            ):  # different syntax ( grouped commands ) for Slash command groups.
                description += (
                    "\n".join(
                        f"> `/{command.name} {command.subcommands.get(sub_c).name}` : {command.subcommands.get(sub_c).description}"
                        for sub_c in command.subcommands  # embedding the sub commands under the parent command
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
            .set_author(
                name=f"{command.name.upper()} COMMAND HELP",
                icon=self._bot.get_me().avatar_url,
            )
            .set_footer(
                text=f"Requested by {context.author}", icon=context.author.avatar_url
            )
        )
        embed.add_field(name="USAGE", value=f"```fix\n/{command.signature}\n```")
        await context.respond(embed=embed)

    async def send_group_help(
        self, context: lightbulb.SlashContext, group: lightbulb.SlashCommandGroup
    ) -> None:
        embed = (
            hikari.Embed(color=await self._bot.color_for(context.get_guild()))
            .set_author(
                name=f"{group.name.upper()} COMMAND HELP",
                icon=self._bot.get_me().avatar_url,
            )
            .set_footer(
                text=f"Requested by {context.author}", icon=context.author.avatar_url
            )
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


class HelpButtons(miru.View):
    msg: hikari.Message

    def __init__(self, bot: Gojo, context: lightbulb.Context) -> None:
        self.lb_context = context  # lightbulb's context for command author info, etc.
        self.plugin_index = -1  # setting the default index status for paginator.
        self._bot = bot

        plugins = [self._bot.get_plugin(_plugin) for _plugin in self._bot.plugins]
        plugins.sort(key=lambda f: f.pos)

        self.plugins = plugins[1:]  # ignoring dev_core.py

        super().__init__(timeout=30)

    async def on_timeout(self) -> None:
        # clearing all the button from the message on timeout
        await self.message.edit(components=None)

    async def view_check(self, context: miru.Context) -> bool:
        # checking if the button was clicked by the command author only.
        if context.user.id != self.lb_context.author.id:
            return await context.respond(
                f"This help menu belongs to {self.lb_context.author}. Only they can use it.",
                flags=hikari.MessageFlag.EPHEMERAL,
            )
        return True

    async def send_plugin_help(
        self,
        context: miru.Context,
    ) -> None:
        plugin: lightbulb.Plugin = self.plugins[self.plugin_index]
        embed = (
            hikari.Embed(
                color=await self._bot.color_for(context.get_guild()),
                timestamp=datetime.now().astimezone(),
            )
            .set_author(
                name=f"{plugin.name.upper()} COMMANDS HELP",
                icon=self._bot.get_me().avatar_url,
            )
            .set_footer(
                text=f"Requested by {self.lb_context.author}",
                icon=self.lb_context.author.avatar_url,
            )
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
        await context.edit_response(embed=embed, components=self.build())

    @miru.button(emoji="◀️", style=hikari.ButtonStyle.PRIMARY)
    async def previous(self, button: miru.Button, context: miru.Context) -> None:
        if self.plugin_index < 1:
            return await context.respond(
                "This action cannot be trigged.\nYou are viewing the Help Home or the 1st plugin.",
                flags=hikari.MessageFlag.EPHEMERAL,
            )
        self.plugin_index -= 1
        await self.send_plugin_help(context)

    @miru.button(label="Home", style=hikari.ButtonStyle.PRIMARY)
    async def home(self, button: miru.Button, context: miru.Context) -> None:
        self.plugin_index = -1
        embed = (
            hikari.Embed(
                color=await self._bot.color_for(self.lb_context.get_guild()),
                timestamp=datetime.now().astimezone(),
            )
            .set_author(
                name=f"{self._bot.get_me().username.upper()} HELP",
                icon=self._bot.get_me().avatar_url,
            )
            .set_footer(
                text=f"Requested by {self.lb_context.author}",
                icon=self.lb_context.author.avatar_url,
            )
        )
        embed.description = "\n".join(
            (
                "```yaml\n",
                "Prefix for the server: /",
                f"In the server since: {self.lb_context.get_guild().get_my_member().joined_at.strftime('%d %b %y')}",
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

        await context.edit_response(embed=embed)

    @miru.button(emoji="▶️", style=hikari.ButtonStyle.PRIMARY)
    async def next(self, button: miru.Button, context: miru.Context) -> None:
        if self.plugin_index == (len(self.plugins) - 1):
            return await context.respond(
                "This is the last plugin!", flags=hikari.MessageFlag.EPHEMERAL
            )

        self.plugin_index += 1
        await self.send_plugin_help(context)

    @miru.button(emoji="⏹️", style=hikari.ButtonStyle.DANGER)
    async def stop_view(self, button: miru.Button, context: miru.Context) -> None:
        await self.on_timeout()
