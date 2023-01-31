import unittest

from unittest.mock import patch

import poked.sprites as sprites


class TestClient(unittest.IsolatedAsyncioTestCase):
    def test_get_sprite(self):
        bulbasaur = sprites.get_sprite(1)
        self.assertEqual(
            bulbasaur.url,
            "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/1.png",
        )

    @patch("IPython.display.display", return_value=None)
    async def test_show(self, display):
        await sprites.show("bulbasaur")

        display.assert_called()
        # The image object will not be the same, but the URL will be
        self.assertEqual(
            display.call_args[0][0].url,
            "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/1.png",
        )

    @patch("IPython.display.display", return_value=None)
    def test_show_by_id(self, display):
        sprites.show_by_id(1)

        display.assert_called()
        # The image object will not be the same, but the URL will be
        self.assertEqual(
            display.call_args[0][0].url,
            "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/1.png",
        )
