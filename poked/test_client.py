# Time to test client.py
# Path: poked/test_client.py

import unittest
import poked.client as client

from unittest.mock import patch, AsyncMock

from gql import gql


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


if __name__ == "__main__":
    unittest.main()
