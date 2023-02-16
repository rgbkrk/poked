from typing import Optional
import pandas as pd

# We use the gql library to build GraphQL queries
from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport

# We use the cache to cache the results of queries
import poked.cache as cache
import poked.queries as queries

# The endpoint for the GraphQL API
endpoint = "https://beta.pokeapi.co/graphql/v1beta"

transport = AIOHTTPTransport(url=endpoint)


def autocache(func):
    """A decorator to automatically cache results"""

    async def wrapped(*args, **kwargs):
        # Get the query from the function's arguments
        query = args[0]

        # Check if it's cached
        cached = cache.get_cached_query(query)
        if cached:
            return cached

        # Otherwise, run the function
        result = await func(*args, **kwargs)

        # Cache the result
        cache.cache_query(query, result)

        return result

    return wrapped


@autocache
async def run_query(
    query,
    # Variables
    variables=None,
    client=None,
):
    """Run the given query on the GraphQL endpoint"""
    # The query can either be a string or the result of gql()

    # If it's a string, convert it to a gql object
    if isinstance(query, str):
        query = gql(query)

    try:
        # If they have a client, use that
        if client:
            return await client.execute(query, variable_values=variables)

        # Otherwise, create a new client
        async with Client(
            transport=transport, fetch_schema_from_transport=True
        ) as session:
            result = await session.execute(query, variable_values=variables)
            return result
    except Exception as e:
        print("Error running query against PokeAPI")
        print(e)

        print("Falling back on old data")

        import urllib.request

        with urllib.request.urlopen(
            "https://poke-sprites.vercel.app/data.json"
        ) as response:
            return response.read()


def convert_list_query_data(list_of_pokemon):
    # Let's iterate over the rows to flatten the types and stats
    for pokemon in list_of_pokemon:
        for key in ["name", "base_experience", "height", "weight"]:
            pokemon[key.replace("_", " ").title()] = pokemon[key]
            del pokemon[key]

        # Flatten the types
        types = pokemon["pokemon_v2_pokemontypes"]
        for t in types:
            slot = t["slot"]
            if slot == 1:
                pokemon["Type (Primary)"] = t["pokemon_v2_type"]["name"]
            elif slot == 2:
                pokemon["Type (Secondary)"] = t["pokemon_v2_type"]["name"]
            else:
                pokemon[f"Type ({slot})"] = t["pokemon_v2_type"]["name"]

        if "Type (Secondary)" not in pokemon:
            pokemon["Type (Secondary)"] = None

        del pokemon["pokemon_v2_pokemontypes"]

        # Pull out the stats and efforts individually, applying the
        # effort after the stat for aesthetics
        stats = pokemon["pokemon_v2_pokemonstats"]
        effort = {}

        for s in stats:
            # These should be capitalized like HP, Attack, Special Defense, etc.
            # special-defense becomes Special Defense
            stat_name = s["pokemon_v2_stat"]["name"]
            if stat_name == "hp":
                stat_name = "HP"
            else:
                stat_name = stat_name.title()

            stat_name = stat_name.replace("-", " ")

            pokemon[stat_name] = s["base_stat"]

            effort[stat_name + " Effort"] = s["effort"]

        pokemon.update(effort)

        del pokemon["pokemon_v2_pokemonstats"]

        # To create the games this pokemon appears in, we need to iterate over the
        # pokemon_v2_pokemongameindices and extract the name of the version
        # from the pokemon_v2_version object
        game_indices = [
            game["pokemon_v2_version"]["name"]
            for game in pokemon["pokemon_v2_pokemongameindices"]
        ]

        pokemon["Game Appearances"] = game_indices
        pokemon["Number of Appearances"] = len(game_indices) if game_indices else None

        del pokemon["pokemon_v2_pokemongameindices"]

        # Now we need to flatten the pokemon_v2_pokemonspecy object
        specy = pokemon["pokemon_v2_pokemonspecy"]

        pokemon["Base Happiness"] = specy["base_happiness"]
        pokemon["Capture Rate"] = specy["capture_rate"]

        # The API will just leave is_baby not set if it's false, so we need to set it to False otherwise
        pokemon["Baby"] = False
        if "is_baby" in specy:
            pokemon["Baby"] = specy["is_baby"]

        # Same for mythical and legendary

        pokemon["Mythical"] = False
        if "is_mythical" in specy:
            pokemon["Mythical"] = specy["is_mythical"]

        pokemon["Legendary"] = False
        if "is_legendary" in specy:
            pokemon["Legendary"] = specy["is_legendary"]

        pokemon["Ultra Beast"] = False
        # The API does not have a field for ultra beasts, so we need to check the name
        if pokemon["Name"] in [
            "nihilego",
            "buzzwole",
            "pheromosa",
            "xurkitree",
            "celesteela",
            "kartana",
            "guzzlord",
            "poipole",
            "naganadel",
            "stakataka",
            "blacephalon",
        ]:
            pokemon["Ultra Beast"] = True

        pokemon["Mega"] = False
        # The API does not have a field for mega evolutions, so we need to check the name
        if "-mega" in pokemon["Name"]:
            pokemon["Mega"] = True

        # The evolution chain is a list of pokemon names. The evolution chain can be null
        # if the pokemon is not evolved. In that case, we should set the evolution chain to None
        pokemon["Evolution Chain"] = None
        if specy["pokemon_v2_evolutionchain"]:
            pokemon["Evolution Chain"] = [
                p["name"]
                for p in specy["pokemon_v2_evolutionchain"]["pokemon_v2_pokemonspecies"]
            ]

        pokemon["Evolution Chain Length"] = (
            len(pokemon["Evolution Chain"]) if pokemon["Evolution Chain"] else None
        )

        pokemon["Color"] = specy["pokemon_v2_pokemoncolor"]["name"]

        pokemon["Shape"] = None
        if specy["pokemon_v2_pokemonshape"]:
            pokemon["Shape"] = specy["pokemon_v2_pokemonshape"]["name"]

        del pokemon["pokemon_v2_pokemonspecy"]

    df = pd.DataFrame(list_of_pokemon).set_index("id")

    # Include an easy way to filter out Legendaries, Mythicals, Ultra Beasts, and Megas
    df["Legendary or Mythical or Ultra Beast or Mega"] = (
        df["Legendary"] | df["Mythical"] | df["Ultra Beast"] | df["Mega"]
    )

    return df


class PokemonClient:
    # Cache the DataFrame to make lookup quick
    _all_pokemon_df: Optional[pd.DataFrame] = None

    @classmethod
    async def get_pokemon(cls, name: str) -> pd.Series:
        """
        Get a pokemon by name
        """
        # Assume we can use the cached DataFrame and not have to go through
        # copying the dataframe
        all_pokemon: Optional[pd.DataFrame] = cls._all_pokemon_df

        # Otherwise, build the cache
        if all_pokemon is None:
            all_pokemon = await cls.list_pokemon()

        filtered = all_pokemon[all_pokemon["Name"] == name]
        if len(filtered) == 0:
            raise ValueError(f"Pokemon {name} not found")
        return filtered.iloc[0]

    @classmethod
    async def list_pokemon(cls) -> pd.DataFrame:
        if cls._all_pokemon_df is not None:
            return cls._all_pokemon_df.copy()

        # Execute the query on a transport
        result = await run_query(queries.pokemon_list_query)
        cls._all_pokemon_df = convert_list_query_data(result["pokemon_v2_pokemon"])
        return cls._all_pokemon_df.copy()


get_pokemon = PokemonClient.get_pokemon
list_pokemon = PokemonClient.list_pokemon
