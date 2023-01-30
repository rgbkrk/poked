import unittest
from unittest.mock import mock_open, patch

from poked import cache


@patch("builtins.open", new_callable=mock_open, read_data="test")
@patch("os.remove", return_value=None)
@patch("os.makedirs", return_value=None)
@patch("os.path.exists", return_value=False)
@patch("appdirs.user_cache_dir", return_value="/tmp/poked")
class TestClient(unittest.TestCase):
    def test_get_cache_filename(
        self, mock_user_cache_dir, mock_exists, mock_makedirs, mock_remove, mock_open
    ):
        filename = cache.get_cache_filename("test")
        self.assertEqual(
            filename,
            "/tmp/poked/9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08",
        )

    def test_get_cached_query(
        self, mock_user_cache_dir, mock_exists, mock_makedirs, mock_remove, mock_open
    ):
        result = cache.get_cached_query("test")
        self.assertEqual(result, None)

    def test_get_cached_query_with_file(
        self, mock_user_cache_dir, mock_exists, mock_makedirs, mock_remove, mock_open
    ):
        mock_exists.return_value = True
        mock_open.return_value.__enter__.return_value.read.return_value = (
            '{"pokemon": "good"}'
        )

        result = cache.get_cached_query("real fake query")
        self.assertEqual(result, {"pokemon": "good"})

        mock_open.assert_called_once_with(
            cache.get_cache_filename("real fake query"),
            "r",
        )

        opened_file = mock_open.return_value.__enter__.return_value
        opened_file.read.assert_called_once_with()

    def test_cache_query(
        self, mock_user_cache_dir, mock_exists, mock_makedirs, mock_remove, mock_open
    ):
        result = cache.cache_query("test", "test")
        self.assertEqual(result, None)

        mock_makedirs.assert_called_once_with("/tmp/poked", exist_ok=True)
        mock_open.assert_called_once_with(
            "/tmp/poked/9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08",
            "w",
        )

        opened_file = mock_open.return_value.__enter__.return_value
        opened_file.write.assert_called_once_with('"test"')

    def test_clear_cache(
        self, mock_user_cache_dir, mock_exists, mock_makedirs, mock_remove, mock_open
    ):
        result = cache.clear_cache()
        self.assertEqual(result, None)

        mock_user_cache_dir.assert_called_once_with("poked")
        mock_remove.assert_called_once_with("/tmp/poked")
        mock_exists.assert_not_called()

    def test_clear_cache_with_query(
        self, mock_user_cache_dir, mock_exists, mock_makedirs, mock_remove, mock_open
    ):
        mock_exists.return_value = True

        result = cache.clear_cache("test")
        self.assertEqual(result, None)

        mock_exists.assert_called_once_with(
            "/tmp/poked/9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08"
        )
        mock_remove.assert_called_once_with(
            "/tmp/poked/9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08"
        )
