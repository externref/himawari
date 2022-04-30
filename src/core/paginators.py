from __future__ import annotations

import hikari
import lightbulb
import miru


class InfoEmbedPag(miru.View):
    def __init__(self, lb_context: lightbulb.Context):
        self.index = 0
        self.embeds: list[hikari.Embed] = []
        self.lb_context: lightbulb.Context = lb_context
        super().__init__(timeout=30)

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
