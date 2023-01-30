# Time to test client.py
# Path: poked/test_client.py

import unittest
from unittest.mock import AsyncMock, patch

import pandas as pd
from gql import gql

import poked.client as client


class TestClient(unittest.IsolatedAsyncioTestCase):
    def test_client(self):
        # Just bootstrapping here
        self.assertEqual(client.endpoint, "https://beta.pokeapi.co/graphql/v1beta")

    @patch("poked.cache.get_cached_query", return_value=None)
    @patch("poked.cache.cache_query", return_value=None)
    async def test_autocache(self, mock_cache, mock_get):
        # Set up our async query function
        async def func(query):
            return f"Queried: {query}"

        # Wrap it with autocache
        cached_query = client.autocache(func)

        result = await cached_query("test")
        self.assertEqual(result, "Queried: test")

        self.assertTrue(mock_cache.called)
        self.assertTrue(mock_get.called)

        # Assert that it was called with the correct arguments
        mock_cache.assert_called_with("test", "Queried: test")

    @patch("poked.cache.get_cached_query", return_value=None)
    @patch("poked.cache.cache_query", return_value=None)
    async def test_autocache_cached(self, mock_cache, mock_get):
        # Set up our async query function
        async def func(query):
            return f"Queried: {query}"

        # Wrap it with autocache
        cached_query = client.autocache(func)

        # Mock the cache to return a value
        mock_get.return_value = "Cached"

        result = await cached_query("test")
        self.assertEqual(result, "Cached")

        # Assert that it was called with the correct arguments
        mock_cache.assert_not_called()
        mock_get.assert_called_with("test")

    @patch("poked.cache.get_cached_query", return_value=None)
    @patch("poked.cache.cache_query", return_value=None)
    async def test_run_query(self, mock_cache, mock_get):
        graphql_client = AsyncMock()
        query = gql(
            """
        {
            junk {
                test
            }
        }
        """
        )
        result = await client.run_query(query, client=graphql_client)

        graphql_client.execute.assert_called_with(query, variable_values=None)

    async def test_convert_list_query_data(self):
        query = gql(
            """
            query GetPokemon {
              pokemon_v2_pokemon(limit: 1, offset: 567) {
                id
                name
                base_experience
                height
                weight
                pokemon_v2_pokemonstats {
                  base_stat
                  effort
                  pokemon_v2_stat {
                    name
                  }
                }
                pokemon_v2_pokemontypes {
                  slot
                  pokemon_v2_type {
                    name
                  }
                }
                pokemon_v2_pokemongameindices {
                  pokemon_v2_version {
                    name
                  }
                }
                pokemon_v2_pokemonspecy {
                  base_happiness
                  capture_rate
                  is_baby
                  is_mythical
                  is_legendary
                  gender_rate
                  has_gender_differences
                  pokemon_v2_pokemoncolor {
                    name
                  }
                  pokemon_v2_evolutionchain {
                    pokemon_v2_pokemonspecies {
                      name
                    }
                  }
                  pokemon_v2_pokemonshape {
                    name
                  }
                }
              }
            }
        """
        )

        data = {
            "pokemon_v2_pokemon": [
                {
                    "id": 568,
                    "name": "trubbish",
                    "base_experience": 66,
                    "height": 6,
                    "weight": 310,
                    "pokemon_v2_pokemonstats": [
                        {
                            "base_stat": 50,
                            "effort": 0,
                            "pokemon_v2_stat": {"name": "hp"},
                        },
                        {
                            "base_stat": 50,
                            "effort": 0,
                            "pokemon_v2_stat": {"name": "attack"},
                        },
                        {
                            "base_stat": 62,
                            "effort": 0,
                            "pokemon_v2_stat": {"name": "defense"},
                        },
                        {
                            "base_stat": 40,
                            "effort": 0,
                            "pokemon_v2_stat": {"name": "special-attack"},
                        },
                        {
                            "base_stat": 62,
                            "effort": 0,
                            "pokemon_v2_stat": {"name": "special-defense"},
                        },
                        {
                            "base_stat": 65,
                            "effort": 1,
                            "pokemon_v2_stat": {"name": "speed"},
                        },
                    ],
                    "pokemon_v2_pokemontypes": [
                        {"slot": 1, "pokemon_v2_type": {"name": "poison"}}
                    ],
                    "pokemon_v2_pokemongameindices": [
                        {"pokemon_v2_version": {"name": "black"}},
                        {"pokemon_v2_version": {"name": "white"}},
                        {"pokemon_v2_version": {"name": "black-2"}},
                        {"pokemon_v2_version": {"name": "white-2"}},
                    ],
                    "pokemon_v2_pokemonspecy": {
                        "base_happiness": 50,
                        "capture_rate": 190,
                        "is_baby": False,
                        "is_mythical": False,
                        "is_legendary": False,
                        "gender_rate": 4,
                        "has_gender_differences": False,
                        "pokemon_v2_pokemoncolor": {"name": "green"},
                        "pokemon_v2_evolutionchain": {
                            "pokemon_v2_pokemonspecies": [
                                {"name": "trubbish"},
                                {"name": "garbodor"},
                            ]
                        },
                        "pokemon_v2_pokemonshape": {"name": "humanoid"},
                    },
                }
            ]
        }
        result = client.convert_list_query_data(data["pokemon_v2_pokemon"])

        # First we'll compare columns that should be shared between our computed DataFrame
        # and the one we expect
        hokey_df = pd.DataFrame(data["pokemon_v2_pokemon"]).set_index("id")

        common_columns = ["name", "base_experience", "height", "weight"]

        pd.testing.assert_frame_equal(result[common_columns], hokey_df[common_columns])

        self.assertEqual(result["Number of Appearances"][568], 4)
        self.assertEqual(result["Type (Primary)"][568], "poison")
        self.assertEqual(result["Type (Secondary)"][568], None)

        trubbish = result.loc[568]
        self.assertEqual(trubbish["Type (Primary)"], "poison")
        self.assertEqual(trubbish["Type (Secondary)"], None)
        self.assertEqual(trubbish["HP"], 50)
        self.assertEqual(trubbish["Attack"], 50)
        self.assertEqual(trubbish["Defense"], 62)
        self.assertEqual(trubbish["Special Attack"], 40)
        self.assertEqual(trubbish["Special Defense"], 62)
        self.assertEqual(trubbish["Speed"], 65)
        self.assertEqual(trubbish["Base Happiness"], 50)
        self.assertEqual(trubbish["Capture Rate"], 190)
        self.assertEqual(trubbish["Is Baby"], False)
        self.assertEqual(trubbish["Is Mythical"], False)
        self.assertEqual(trubbish["Is Legendary"], False)

        self.assertEqual(trubbish["Evolution Chain"], ["trubbish", "garbodor"])
        self.assertEqual(trubbish["Color"], "green")
        self.assertEqual(trubbish["Shape"], "humanoid")  # lolwut


if __name__ == "__main__":
    unittest.main()
