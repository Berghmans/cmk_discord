#!/usr/bin/env python3
import unittest
import sys
import os
from unittest.mock import patch

# Add parent directory to path to import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import cmk_discord


class TestMain(unittest.TestCase):
    """Tests for main function"""

    @patch('cmk_discord.post_webhook')
    @patch('cmk_discord.build_context')
    def test_main_success(self, mock_build_context, mock_post_webhook):
        mock_build_context.return_value = {
            "PARAMETER_1": "https://discord.com/api/webhooks/123",
            "PARAMETER_2": "https://monitoring.example.com",
            "OMD_SITE": "production",
            "WHAT": "SERVICE",
            "SHORTDATETIME": "2025-01-15T10:30:00",
            "LASTSERVICESTATE": "OK",
            "SERVICESTATE": "CRITICAL",
            "SERVICEOUTPUT": "Error",
            "NOTIFICATIONTYPE": "PROBLEM",
            "SERVICEDESC": "HTTP",
            "HOSTNAME": "host01",
            "SERVICECHECKCOMMAND": "check_http",
            "SERVICEURL": "/service",
        }

        cmk_discord.main()

        mock_post_webhook.assert_called_once()

    @patch('sys.stderr.write')
    @patch('cmk_discord.build_context')
    def test_main_empty_webhook_url(self, mock_build_context, mock_stderr):
        mock_build_context.return_value = {
            "PARAMETER_1": "",
            "PARAMETER_2": "https://monitoring.example.com",
        }

        with self.assertRaises(SystemExit) as cm:
            cmk_discord.main()

        self.assertEqual(cm.exception.code, 2)
        mock_stderr.assert_called_once()
        self.assertIn("Empty webhook url", mock_stderr.call_args[0][0])

    @patch('sys.stderr.write')
    @patch('cmk_discord.build_context')
    def test_main_missing_webhook_url(self, mock_build_context, mock_stderr):
        mock_build_context.return_value = {
            "PARAMETER_2": "https://monitoring.example.com",
        }

        with self.assertRaises(SystemExit) as cm:
            cmk_discord.main()

        self.assertEqual(cm.exception.code, 2)
        mock_stderr.assert_called_once()

    @patch('sys.stderr.write')
    @patch('cmk_discord.build_context')
    def test_main_invalid_webhook_url(self, mock_build_context, mock_stderr):
        mock_build_context.return_value = {
            "PARAMETER_1": "https://invalid.com/webhook",
            "PARAMETER_2": "https://monitoring.example.com",
        }

        with self.assertRaises(SystemExit) as cm:
            cmk_discord.main()

        self.assertEqual(cm.exception.code, 2)
        mock_stderr.assert_called_once()
        self.assertIn("Invalid Discord webhook url", mock_stderr.call_args[0][0])

    @patch('sys.stderr.write')
    @patch('cmk_discord.build_context')
    def test_main_invalid_site_url(self, mock_build_context, mock_stderr):
        mock_build_context.return_value = {
            "PARAMETER_1": "https://discord.com/api/webhooks/123",
            "PARAMETER_2": "not-a-url",
        }

        with self.assertRaises(SystemExit) as cm:
            cmk_discord.main()

        self.assertEqual(cm.exception.code, 2)
        mock_stderr.assert_called_once()
        self.assertIn("Invalid site url", mock_stderr.call_args[0][0])

    @patch('cmk_discord.post_webhook')
    @patch('cmk_discord.build_context')
    def test_main_without_site_url(self, mock_build_context, mock_post_webhook):
        mock_build_context.return_value = {
            "PARAMETER_1": "https://discord.com/api/webhooks/123",
            "OMD_SITE": "production",
            "WHAT": "SERVICE",
            "SHORTDATETIME": "2025-01-15T10:30:00",
            "LASTSERVICESTATE": "OK",
            "SERVICESTATE": "CRITICAL",
            "SERVICEOUTPUT": "Error",
            "NOTIFICATIONTYPE": "PROBLEM",
            "SERVICEDESC": "HTTP",
            "HOSTNAME": "host01",
            "SERVICECHECKCOMMAND": "check_http",
            "SERVICEURL": "/service",
        }

        cmk_discord.main()

        mock_post_webhook.assert_called_once()


if __name__ == '__main__':
    unittest.main()
