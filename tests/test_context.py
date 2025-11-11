#!/usr/bin/env python3
import unittest
import sys
import os
from unittest.mock import patch

# Add parent directory to path to import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import cmk_discord


class TestBuildContext(unittest.TestCase):
    """Tests for build_context function"""

    @patch.dict(os.environ, {
        "NOTIFY_HOSTNAME": "webserver01",
        "NOTIFY_SERVICESTATE": "CRITICAL",
        "NOTIFY_PARAMETER_1": "https://discord.com/api/webhooks/123",
        "OTHER_VAR": "should_not_appear",
        "NOTIFY_OMD_SITE": "production",
        "NOTIFY_WHAT": "SERVICE",
        "NOTIFY_NOTIFICATIONTYPE": "PROBLEM",
        "NOTIFY_SHORTDATETIME": "2025-01-15T10:30:00"
    })
    def test_build_context(self):
        ctx = cmk_discord.build_context()

        self.assertIsInstance(ctx, cmk_discord.Context)
        self.assertEqual(ctx.hostname, "webserver01")
        self.assertEqual(ctx.service_state, "CRITICAL")
        self.assertEqual(ctx.webhook_url, "https://discord.com/api/webhooks/123")
        self.assertEqual(ctx.omd_site, "production")
        self.assertEqual(ctx.what, "SERVICE")
        self.assertEqual(ctx.notification_type, "PROBLEM")

    @patch.dict(os.environ, {}, clear=True)
    def test_build_context_empty(self):
        ctx = cmk_discord.build_context()

        self.assertIsInstance(ctx, cmk_discord.Context)
        self.assertEqual(ctx.what, "")
        self.assertEqual(ctx.hostname, "")


if __name__ == '__main__':
    unittest.main()
