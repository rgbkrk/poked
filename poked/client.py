# The client bindings here use queries.py to build GraphQL queries, and
# cache.py to cache the results.  The client code is in client.py:

# We use the gql library to build GraphQL queries
from gql import gql

# We use the cache to cache the results of queries
import poked.cache as cache
import poked.queries as queries

from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport

import pandas as pd

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

    # If they have a client, use that
    if client:
        return await client.execute(query, variable_values=variables)

    # Otherwise, create a new client
    async with Client(transport=transport, fetch_schema_from_transport=True) as session:
        result = await session.execute(query)
        return result


async def list_pokemon():
    # Execute the query on a transport
    list_of_pokemon = await run_query(queries.pokemon_list_query)

    # Let's iterate over the rows to flatten the types and stats
    for pokemon in list_of_pokemon["pokemon_v2_pokemon"]:
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

        del pokemon["pokemon_v2_pokemontypes"]

        # Flatten the stats
        stats = pokemon["pokemon_v2_pokemonstats"]
        for s in stats:
            stat_name = s["pokemon_v2_stat"]["name"]
            pokemon[stat_name] = s["base_stat"]
            pokemon[stat_name + " effort"] = s["effort"]

        del pokemon["pokemon_v2_pokemonstats"]

        # To create the games this pokemon appears in, we need to iterate over the
        # pokemon_v2_pokemongameindices and extract the name of the version
        # from the pokemon_v2_version object
        game_indices = [
            game["pokemon_v2_version"]["name"]
            for game in pokemon["pokemon_v2_pokemongameindices"]
        ]

        pokemon["Game Appearances"] = game_indices

        del pokemon["pokemon_v2_pokemongameindices"]

        # Now we need to flatten the pokemon_v2_pokemonspecy object
        specy = pokemon["pokemon_v2_pokemonspecy"]

        pokemon["Base Happiness"] = specy["base_happiness"]
        pokemon["Capture Rate"] = specy["capture_rate"]
        pokemon["Is Baby"] = specy["is_baby"]
        pokemon["Is Mythical"] = specy["is_mythical"]
        pokemon["Is Legendary"] = specy["is_legendary"]

        # The evolution chain is a list of pokemon names. The evolution chain can be null
        # if the pokemon is not evolved. In that case, we should set the evolution chain to None
        pokemon["Evolution Chain"] = None
        if specy["pokemon_v2_evolutionchain"]:
            pokemon["Evolution Chain"] = [
                p["name"]
                for p in specy["pokemon_v2_evolutionchain"]["pokemon_v2_pokemonspecies"]
            ]

        pokemon["Color"] = specy["pokemon_v2_pokemoncolor"]["name"]

        pokemon["Shape"] = None
        if specy["pokemon_v2_pokemonshape"]:
            pokemon["Shape"] = specy["pokemon_v2_pokemonshape"]["name"]

        del pokemon["pokemon_v2_pokemonspecy"]

    df = pd.DataFrame(list_of_pokemon["pokemon_v2_pokemon"]).set_index("id")
    return df
