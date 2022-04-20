from __future__ import annotations

from random import choice

from lightbulb.plugins import Plugin
from lightbulb.context.base import ResponseProxy
from lightbulb.context.slash import SlashContext
from lightbulb.decorators import command, option, implements
from lightbulb.commands.slash import SlashCommand

from hikari.embeds import Embed
from hikari.messages import ComponentType
from hikari.events.interaction_events import InteractionCreateEvent
from hikari.interactions.component_interactions import ComponentInteraction

from ..core.bot import Gojo


class Fun(Plugin):
    def __init__(self):
        self.bot: Gojo
        self.pos = 5
        super().__init__(
            name="fun",
            description="Fun and image commands.",
        )


async def fetch_meme():
    res = await fun.bot.custom_session.get(
        f"https://meme-api.herokuapp.com/gimme/{choice(['memes','dankmemes','me_irl','wholesomememes'])}"
    )
    data = await res.json()
    return data


fun = Fun()


@fun.command
@command(name="meme", description="Get a random meme from reddit.")
@implements(SlashCommand)
async def meme(context: SlashContext) -> None:
    nsfw = True
    while nsfw == True:
        """Avoiding Nsfw"""
        data = await fetch_meme()
        if not data["nsfw"]:
            nsfw = False

    embed = Embed(
        title=f"r/{data['subreddit']}",
        description=data["title"],
        color=await fun.bot.color_for(context.get_guild()),
        url=f"https://reddit.com/r/{data['subreddit']}",
    ).set_author()
    embed.set_image(data["url"])
    embed.set_footer(
        text=f'👍 {data["ups"]} ups | Requested by {context.author}',
        icon=context.author.avatar_url or context.author.default_avatar_url,
    )
    await context.respond(embed=embed, reply=True)


animals_dict = {
    "dog": ["🐶", "https://some-random-api.ml/animal/dog"],
    "cat": ["🐱", "https://some-random-api.ml/animal/cat"],
    "panda": ["🐼", "https://some-random-api.ml/animal/panda"],
    "fox": ["🦊", "https://some-random-api.ml/animal/fox"],
    "red_panda": ["🐼", "https://some-random-api.ml/animal/red_panda"],
    "koala": ["🐨", "https://some-random-api.ml/animal/koala"],
    "bird": ["🐦", "https://some-random-api.ml/animal/birb"],
    "racoon": ["🦝", "https://some-random-api.ml/animal/racoon"],
    "kangaroo": ["🦘", "https://some-random-api.ml/animal/kangaroo"],
    # "whale": ["🐋", "https://some-random-api.ml/animal/whale"],
}


@fun.command
@command(
    name="animal", description="Get a random animal image and fact from gives choices."
)
@implements(SlashCommand)
async def animal_command(context: SlashContext) -> None | ResponseProxy:
    act_row = (
        fun.bot.rest.build_action_row()
        .add_select_menu(str(context.author.id))
        .set_placeholder("Select an animal.")
    )

    for animal, data in animals_dict.items():
        act_row.add_option(animal.title().replace("_", " "), animal).set_emoji(
            data[0]
        ).add_to_menu()

    embed = Embed(
        color=await fun.bot.color_for(context.get_guild()),
        description="Select an animal.",
    )
    res = await context.respond(embed=embed, component=act_row.add_to_container())
    msg = await res.message()
    try:
        event: InteractionCreateEvent = await fun.bot.wait_for(
            InteractionCreateEvent,
            timeout=30,
            predicate=lambda inter: isinstance(inter.interaction, ComponentInteraction)
            and inter.interaction.user.id
            and context.author.id
            and inter.interaction.message.id == msg.id
            and inter.interaction.component_type == ComponentType.SELECT_MENU,
        )
    except __import__("asyncio").TimeoutError:
        embed.description = "You didn't chose an option on time"
        embed.color = 0xFF0000
        return await context.edit_last_response(embed=embed, components=[])

    response = await fun.bot.custom_session.get(
        (animals_dict.get(event.interaction.values[0]))[1]
    )
    if not response.status == 200:
        print(await response.json())
        embed.description = "Something went wrong while getting the image."
        embed.color = 0xFF0000
        return await context.edit_last_response(embed=embed, components=[])

    data = await response.json()
    embed.description = data.get("fact")
    embed.set_image(data.get("image")).set_footer(
        text=f"Requested by {context.author}",
        icon=context.author.avatar_url or context.author.default_avatar_url,
    ).set_author(name=event.interaction.values[0].upper())
    await context.edit_last_response(embed=embed, components=[])


def load(bot: Gojo) -> None:
    bot.add_plugin(fun)
