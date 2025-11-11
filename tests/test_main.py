#!/usr/bin/env python3
import unittest
import sys
import os
from unittest.mock import patch

# Add parent directory to path to import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'notifications')))

import cmk_discord
from tests.test_data_loader import load_latest_test_data


class TestMain(unittest.TestCase):
    """Tests for main function"""

    @patch('requests.post')
    @patch('cmk_discord.Context.from_env')
    def test_main_success(self, mock_from_env, mock_requests_post):
        # Load test data from the latest version
        ctx = load_latest_test_data("service", "problem_critical.json")
        mock_from_env.return_value = ctx

        # Mock successful webhook response
        mock_response = unittest.mock.MagicMock()
        mock_response.status_code = 204
        mock_requests_post.return_value = mock_response

        cmk_discord.main()

        mock_requests_post.assert_called_once()

    @patch('sys.stderr.write')
    @patch('cmk_discord.Context.from_env')
    def test_main_empty_webhook_url(self, mock_from_env, mock_stderr):
        ctx = cmk_discord.Context(
            what="SERVICE",
            notification_type="PROBLEM",
            short_datetime="2025-01-15T10:30:00",
            omd_site="production",
            hostname="webserver01",
            webhook_url="",
            site_url="https://monitoring.example.com"
        )
        mock_from_env.return_value = ctx

        with self.assertRaises(SystemExit) as cm:
            cmk_discord.main()

        self.assertEqual(cm.exception.code, 2)
        mock_stderr.assert_called_once()
        self.assertIn("Empty webhook url", mock_stderr.call_args[0][0])

    @patch('sys.stderr.write')
    @patch('cmk_discord.Context.from_env')
    def test_main_missing_webhook_url(self, mock_from_env, mock_stderr):
        ctx = cmk_discord.Context(
            what="SERVICE",
            notification_type="PROBLEM",
            short_datetime="2025-01-15T10:30:00",
            omd_site="production",
            hostname="webserver01",
            webhook_url=None,
            site_url="https://monitoring.example.com"
        )
        mock_from_env.return_value = ctx

        with self.assertRaises(SystemExit) as cm:
            cmk_discord.main()

        self.assertEqual(cm.exception.code, 2)
        mock_stderr.assert_called_once()

    @patch('sys.stderr.write')
    @patch('cmk_discord.Context.from_env')
    def test_main_invalid_webhook_url(self, mock_from_env, mock_stderr):
        ctx = cmk_discord.Context(
            what="SERVICE",
            notification_type="PROBLEM",
            short_datetime="2025-01-15T10:30:00",
            omd_site="production",
            hostname="webserver01",
            webhook_url="https://invalid.com/webhook",
            site_url="https://monitoring.example.com"
        )
        mock_from_env.return_value = ctx

        with self.assertRaises(SystemExit) as cm:
            cmk_discord.main()

        self.assertEqual(cm.exception.code, 2)
        mock_stderr.assert_called_once()
        self.assertIn("Invalid Discord webhook url", mock_stderr.call_args[0][0])

    @patch('sys.stderr.write')
    @patch('cmk_discord.Context.from_env')
    def test_main_invalid_site_url(self, mock_from_env, mock_stderr):
        ctx = cmk_discord.Context(
            what="SERVICE",
            notification_type="PROBLEM",
            short_datetime="2025-01-15T10:30:00",
            omd_site="production",
            hostname="webserver01",
            webhook_url="https://discord.com/api/webhooks/123",
            site_url="not-a-url"
        )
        mock_from_env.return_value = ctx

        with self.assertRaises(SystemExit) as cm:
            cmk_discord.main()

        self.assertEqual(cm.exception.code, 2)
        mock_stderr.assert_called_once()
        self.assertIn("Invalid site url", mock_stderr.call_args[0][0])

    @patch('requests.post')
    @patch('cmk_discord.Context.from_env')
    def test_main_without_site_url(self, mock_from_env, mock_requests_post):
        # Load test data from the latest version and remove site URL
        ctx = load_latest_test_data("service", "problem_critical.json")
        ctx.site_url = None  # Remove site URL to test without it
        mock_from_env.return_value = ctx

        # Mock successful webhook response
        mock_response = unittest.mock.MagicMock()
        mock_response.status_code = 204
        mock_requests_post.return_value = mock_response

        cmk_discord.main()

        mock_requests_post.assert_called_once()


if __name__ == '__main__':
    unittest.main()
