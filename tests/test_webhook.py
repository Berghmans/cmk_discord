#!/usr/bin/env python3
import unittest
import sys
import os
from unittest.mock import patch, MagicMock
from http import HTTPStatus

# Add parent directory to path to import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'notifications')))

import cmk_discord
from tests.test_data_loader import load_latest_test_data


class TestDiscordWebhookSend(unittest.TestCase):
    """Tests for DiscordWebhook.send() method"""

    @patch('requests.post')
    def test_send_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = HTTPStatus.NO_CONTENT.value
        mock_post.return_value = mock_response

        ctx = load_latest_test_data("service", "problem_critical.json")
        webhook_url = "https://discord.com/api/webhooks/123/abc"

        embed = cmk_discord.Embed.from_context(ctx)
        webhook = cmk_discord.DiscordWebhook(webhook_url, embed, ctx.omd_site)

        # Should not raise an exception
        webhook.send()

        mock_post.assert_called_once()
        call_kwargs = mock_post.call_args[1]
        self.assertEqual(call_kwargs['url'], webhook_url)
        self.assertIn('json', call_kwargs)

    @patch('requests.post')
    @patch('sys.stderr.write')
    def test_send_failure(self, mock_stderr, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_post.return_value = mock_response

        ctx = load_latest_test_data("service", "problem_critical.json")
        webhook_url = "https://discord.com/api/webhooks/123/abc"

        embed = cmk_discord.Embed.from_context(ctx)
        webhook = cmk_discord.DiscordWebhook(webhook_url, embed, ctx.omd_site)

        with self.assertRaises(SystemExit) as cm:
            webhook.send()

        self.assertEqual(cm.exception.code, 1)
        mock_stderr.assert_called_once()
        self.assertIn("Unexpected response", mock_stderr.call_args[0][0])
        self.assertIn("400", mock_stderr.call_args[0][0])


if __name__ == '__main__':
    unittest.main()
