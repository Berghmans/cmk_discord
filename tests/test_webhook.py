#!/usr/bin/env python3
import unittest
import sys
import os
from unittest.mock import patch, MagicMock
from http import HTTPStatus

# Add parent directory to path to import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import cmk_discord


class TestPostWebhook(unittest.TestCase):
    """Tests for post_webhook function"""

    @patch('cmk_discord.requests.post')
    def test_post_webhook_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = HTTPStatus.NO_CONTENT.value
        mock_post.return_value = mock_response

        url = "https://discord.com/api/webhooks/123"
        json_data = {"test": "data"}

        # Should not raise an exception
        cmk_discord.post_webhook(url, json_data)

        mock_post.assert_called_once_with(url=url, json=json_data)

    @patch('cmk_discord.requests.post')
    @patch('sys.stderr.write')
    def test_post_webhook_failure(self, mock_stderr, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_post.return_value = mock_response

        url = "https://discord.com/api/webhooks/123"
        json_data = {"test": "data"}

        with self.assertRaises(SystemExit) as cm:
            cmk_discord.post_webhook(url, json_data)

        self.assertEqual(cm.exception.code, 1)
        mock_stderr.assert_called_once()
        self.assertIn("Unexpected response", mock_stderr.call_args[0][0])
        self.assertIn("400", mock_stderr.call_args[0][0])


if __name__ == '__main__':
    unittest.main()
