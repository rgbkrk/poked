# We have to import display.display in this way for mocks to work
import IPython.display
from IPython.display import Image

from poked.client import get_pokemon


def get_sprite(ID: int) -> Image:
    """Get the sprite for the given Pokemon ID"""
    url = f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{ID}.png"
    return Image(url=url, width=200, embed=False)


# Does not return, uses display() as a side effect
async def show(name: str) -> None:
    """Show the sprite for the given Pokemon name, asynchronously"""
    pokemon = await get_pokemon(name)
    # The ID is the index, which on a series is the property called name. Make sure to convert it to an int
    ID: int = pokemon.name  # type: ignore

    if ID is None:
        raise ValueError(f"Could not find Pokemon with name {name}")

    # type: ignore
    show_by_id(ID)


def show_by_id(ID: int):
    """Show the sprite for the given Pokemon ID"""
    IPython.display.display(get_sprite(ID))
