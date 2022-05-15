from __future__ import annotations
import hikari
import lightbulb


class EmojiStore:
    def __init__(self, bot: lightbulb.BotApp) -> None:
        self.bot = bot

    def emoji_by_id(self, id: int) -> hikari.Emoji | None:
        return self.bot.cache.get_emoji(id)

    @property
    def member_icon(self) -> hikari.Emoji | None:
        return self.emoji_by_id(973914850965204993)

    @property
    def text_channel_icon(self) -> hikari.Emoji | None:
        return self.emoji_by_id(973914950739316757)

    @property
    def voice_channel_icon(self) -> hikari.Emoji | None:
        return self.emoji_by_id(973914727317119036)

    @property
    def mention_icon(self) -> hikari.Emoji | None:
        return self.emoji_by_id(973915479481659412)

    @property
    def online(self) -> hikari.Emoji | None:
        return self.emoji_by_id(969613502576742450)

    @property
    def offline(self) -> hikari.Emoji | None:
        return self.emoji_by_id(969670664950775919)

    @property
    def dnd(self) -> hikari.Emoji | None:
        return self.emoji_by_id(969613864280920115)

    @property
    def idle(self) -> hikari.Emoji | None:
        return self.emoji_by_id(969613426378821712)

    @property
    def discord(self) -> hikari.Emoji | None:
        return self.emoji_by_id(973920155522441216)

    @property
    def role_icon(self) -> hikari.Emoji | None:
        return self.emoji_by_id(973921118740156466)

    @property
    def bot_icon(self) -> hikari.Emoji | None:
        return self.emoji_by_id(973921643304988682)

    @property
    def owner_icon(self) -> hikari.Emoji | None:
        return self.emoji_by_id(973922134718029896)
