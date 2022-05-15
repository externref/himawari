from __future__ import annotations

import hikari
import lightbulb
import miru


class InfoEmbedSelect(miru.Select):
    def __init__(
        self, lb_context: lightbulb.Context, *, embeds: list[hikari.Embed]
    ) -> None:
        self.embeds = embeds
        options: list[miru.SelectOption] = []
        for index, embed in enumerate(embeds, start=1):
            options.append(
                miru.SelectOption(label=f"{index}. {embed.title or embed.author}")
            )
        super().__init__(options=options, placeholder="Select Group.", row=2)

    async def callback(self, context: miru.Context) -> None:
        embed = self.embeds[int(context.interaction.values[0][0]) - 1]
        await context.edit_response(
            content=f"Page `{context.interaction.values[0][0]}` of `{len(self.embeds)}`",
            embed=embed,
        )


class InfoEmbedPag(miru.View):
    def __init__(
        self, lb_context: lightbulb.Context, *, with_select: bool = False
    ) -> None:
        self.select_menu = with_select
        self.index = 0
        self.embeds: list[hikari.Embed] = []
        self.lb_context: lightbulb.Context = lb_context
        super().__init__(timeout=30)

    def build(self) -> list[hikari.impl.ActionRowBuilder]:
        if self.select_menu:
            self.add_item(InfoEmbedSelect(self.lb_context, embeds=self.embeds))
        return super().build()

    async def view_check(self, context: miru.Context) -> bool:
        if not self.lb_context.author == context.user:
            return await context.respond(
                f"This command was invoked by {self.lb_context}.",
                flags=hikari.MessageFlag.EPHEMERAL,
            )
        return True

    def add_embed(self, embed: hikari.Embed) -> None:
        self.embeds.append(embed)

    def add_embeds(self, *embeds) -> None:
        self.embeds.extend(embeds)

    async def on_timeout(self) -> None:
        await self.message.edit(components=[])

    @miru.button(emoji="◀️", style=hikari.ButtonStyle.PRIMARY)
    async def previous(
        self, button: miru.Button, context: miru.Context
    ) -> None | lightbulb.ResponseProxy:
        if self.index == 0:
            return await context.respond(
                "This is the first page of the menu.",
                flags=hikari.MessageFlag.EPHEMERAL,
            )
        self.index -= 1
        await context.edit_response(
            content=f"Page `{self.index+1}` of `{len(self.embeds)}`",
            embed=self.embeds[self.index],
        )

    @miru.button(emoji="▶️", style=hikari.ButtonStyle.PRIMARY)
    async def next(
        self, button: miru.Button, context: miru.Context
    ) -> None | lightbulb.ResponseProxy:
        if self.index == (len(self.embeds) - 1):
            return await context.respond(
                "This is the last page of the menu.",
                flags=hikari.MessageFlag.EPHEMERAL,
            )
        self.index += 1
        await context.edit_response(
            content=f"Page `{self.index+1}` of `{len(self.embeds)}`",
            embed=self.embeds[self.index],
        )

    @miru.button(emoji="⏹️", style=hikari.ButtonStyle.DANGER)
    async def stop(
        self, button: miru.Button, context: miru.Context
    ) -> None | lightbulb.ResponseProxy:
        await self.on_timeout()
