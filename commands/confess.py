import hikari
import lightbulb
import miru

from core.bot import Bot


class QuestionModal(miru.Modal):
    channel_id: int
    message: hikari.Message

    def __init__(self) -> None:
        super().__init__("Make a confession")
        self.add_item(
            miru.TextInput(
                label="Your Confession Here.",
                style=hikari.TextInputStyle.PARAGRAPH,
                required=True,
            )
        )

    async def callback(self, context: miru.ModalContext) -> None:
        text = list(context.values.values())[0]
        embed = hikari.Embed(
            title="Anonymous Confession", description=text, color=0xFFFFFF
        )
        await context.bot.rest.create_message(self.channel_id, embed=embed)
        embed = self.message.embeds[0]
        embed.description = f"Your confession has been sent to <#{self.channel_id}>!"
        await context.edit_response(embed=embed, components=[])


class ConfessButtonView(miru.View):
    channel_id: int
    message: hikari.Message

    @miru.button(label="Confess", style=hikari.ButtonStyle.PRIMARY)
    async def confess(self, _: miru.Button, ctx: miru.ViewContext) -> None:
        modal = QuestionModal()
        modal.channel_id = self.channel_id
        modal.message = self.message
        await ctx.respond_with_modal(modal)


class Plugin(lightbulb.Plugin):
    bot: Bot


plugin = Plugin("confess")


@plugin.command
@lightbulb.command("confess", "Send a confession in this server's confession channel.")
@lightbulb.implements(lightbulb.SlashCommand)
async def confess(context: lightbulb.SlashContext) -> None:
    if not (guild_id := context.guild_id):
        return
    if (data := await plugin.bot.db.get_confession_channel(guild_id)) is None:
        await context.respond(
            embed=hikari.Embed(
                description="No confession channel has been set for this server yet.",
                color=plugin.bot.color,
            )
        )
        return
    view = ConfessButtonView()
    embed = hikari.Embed(
        title="Make a confession.",
        description=(
            f"Hey there **{context.author}**, thanks for using"
            f"{plugin.bot.me.username} !\n"
            "All the confessions you make with this bot are private and secured.\n"
            "For security purpose confession message IDs are saved along with your ID."
        ),
        color=plugin.bot.color,
    )
    res = await context.respond(
        embed=embed, components=view.build(), flags=hikari.MessageFlag.EPHEMERAL
    )
    view.start(await res.message())
    view.channel_id = data[1]


def load(bot: Bot) -> None:

    bot.add_plugin(plugin)
