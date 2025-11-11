#!/usr/bin/env python3
import unittest
import sys
import os

# Add parent directory to path to import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import cmk_discord
from tests.test_data_loader import load_test_data


class TestBuildServiceEmbeds(unittest.TestCase):
    """Tests for build_service_embeds function"""

    def setUp(self):
        self.ctx = load_test_data("service/problem_critical.json")
        self.site_url = self.ctx.get("PARAMETER_2")
        self.timestamp = "2025-01-15T10:30:00+00:00"

    def test_build_service_embeds_basic(self):
        embeds = cmk_discord.build_service_embeds(self.ctx, self.site_url, self.timestamp)

        self.assertEqual(len(embeds), 1)
        embed = embeds[0]

        self.assertEqual(embed["title"], ":rotating_light: PROBLEM: HTTP")
        self.assertIn("OK -> CRITICAL", embed["description"])
        self.assertIn("Connection timeout", embed["description"])
        self.assertEqual(embed["color"], cmk_discord.ALERT_COLORS["CRITICAL"])
        self.assertEqual(embed["timestamp"], self.timestamp)
        self.assertEqual(embed["url"], "https://checkmkhost.mycompany.com/my_monitoring/check_mk/view.py?host=webserver01&service=HTTP")

    def test_build_service_embeds_with_comment(self):
        ctx = load_test_data("service/acknowledgement.json")
        site_url = ctx.get("PARAMETER_2")
        embeds = cmk_discord.build_service_embeds(ctx, site_url, self.timestamp)

        embed = embeds[0]
        self.assertIn("Acknowledged by admin", embed["description"])

    def test_build_service_embeds_without_site_url(self):
        embeds = cmk_discord.build_service_embeds(self.ctx, None, self.timestamp)

        embed = embeds[0]
        self.assertNotIn("url", embed)

    def test_build_service_embeds_warning_state(self):
        ctx = load_test_data("service/problem_warning.json")
        site_url = ctx.get("PARAMETER_2")
        embeds = cmk_discord.build_service_embeds(ctx, site_url, self.timestamp)

        embed = embeds[0]
        self.assertEqual(embed["color"], cmk_discord.ALERT_COLORS["WARNING"])

    def test_build_service_embeds_fields(self):
        embeds = cmk_discord.build_service_embeds(self.ctx, self.site_url, self.timestamp)

        embed = embeds[0]
        fields = embed["fields"]
        self.assertEqual(len(fields), 2)
        self.assertEqual(fields[0]["name"], "Host")
        self.assertEqual(fields[0]["value"], "webserver01")
        self.assertEqual(fields[1]["name"], "Service")
        self.assertEqual(fields[1]["value"], "HTTP")

    def test_build_service_embeds_recovery(self):
        ctx = load_test_data("service/recovery_ok.json")
        site_url = ctx.get("PARAMETER_2")
        embeds = cmk_discord.build_service_embeds(ctx, site_url, self.timestamp)

        embed = embeds[0]
        self.assertEqual(embed["title"], ":white_check_mark: RECOVERY: HTTP")
        self.assertIn("CRITICAL -> OK", embed["description"])
        self.assertEqual(embed["color"], cmk_discord.ALERT_COLORS["OK"])


class TestBuildHostEmbeds(unittest.TestCase):
    """Tests for build_host_embeds function"""

    def setUp(self):
        self.ctx = load_test_data("host/problem_down.json")
        self.site_url = self.ctx.get("PARAMETER_2")
        self.timestamp = "2025-01-15T10:30:00+00:00"

    def test_build_host_embeds_basic(self):
        embeds = cmk_discord.build_host_embeds(self.ctx, self.site_url, self.timestamp)

        self.assertEqual(len(embeds), 1)
        embed = embeds[0]

        self.assertEqual(embed["title"], ":rotating_light: PROBLEM: Host: webserver01")
        self.assertIn("UP -> DOWN", embed["description"])
        self.assertIn("Host Unreachable", embed["description"])
        self.assertEqual(embed["color"], cmk_discord.ALERT_COLORS["DOWN"])
        self.assertEqual(embed["timestamp"], self.timestamp)
        self.assertEqual(embed["url"], "https://checkmkhost.mycompany.com/my_monitoring/check_mk/view.py?host=webserver01")

    def test_build_host_embeds_with_comment(self):
        ctx = load_test_data("host/downtime_start.json")
        site_url = ctx.get("PARAMETER_2")
        embeds = cmk_discord.build_host_embeds(ctx, site_url, self.timestamp)

        embed = embeds[0]
        self.assertIn("Scheduled maintenance", embed["description"])

    def test_build_host_embeds_without_site_url(self):
        embeds = cmk_discord.build_host_embeds(self.ctx, None, self.timestamp)

        embed = embeds[0]
        self.assertNotIn("url", embed)

    def test_build_host_embeds_unreachable_state(self):
        ctx = load_test_data("host/unreachable.json")
        site_url = ctx.get("PARAMETER_2")
        embeds = cmk_discord.build_host_embeds(ctx, site_url, self.timestamp)

        embed = embeds[0]
        self.assertEqual(embed["color"], cmk_discord.ALERT_COLORS["UNREACHABLE"])

    def test_build_host_embeds_footer(self):
        embeds = cmk_discord.build_host_embeds(self.ctx, self.site_url, self.timestamp)

        embed = embeds[0]
        self.assertEqual(embed["footer"]["text"], "check-host-alive")

    def test_build_host_embeds_recovery(self):
        ctx = load_test_data("host/recovery_up.json")
        site_url = ctx.get("PARAMETER_2")
        embeds = cmk_discord.build_host_embeds(ctx, site_url, self.timestamp)

        embed = embeds[0]
        self.assertEqual(embed["title"], ":white_check_mark: RECOVERY: Host: webserver01")
        self.assertIn("DOWN -> UP", embed["description"])
        self.assertEqual(embed["color"], cmk_discord.ALERT_COLORS["UP"])


class TestBuildEmbeds(unittest.TestCase):
    """Tests for build_embeds function"""

    def test_build_embeds_for_service(self):
        ctx = load_test_data("service/problem_critical.json")
        site_url = ctx.get("PARAMETER_2")

        embeds = cmk_discord.build_embeds(ctx, site_url)

        self.assertEqual(len(embeds), 1)
        self.assertIn("HTTP", embeds[0]["title"])

    def test_build_embeds_for_host(self):
        ctx = load_test_data("host/problem_down.json")
        site_url = ctx.get("PARAMETER_2")

        embeds = cmk_discord.build_embeds(ctx, site_url)

        self.assertEqual(len(embeds), 1)
        self.assertIn("Host: webserver01", embeds[0]["title"])


class TestBuildWebhookContent(unittest.TestCase):
    """Tests for build_webhook_content function"""

    def test_build_webhook_content(self):
        ctx = load_test_data("service/problem_critical.json")
        site_url = ctx.get("PARAMETER_2")

        content = cmk_discord.build_webhook_content(ctx, site_url)

        self.assertEqual(content["username"], "Checkmk - production")
        self.assertEqual(content["avatar_url"], "https://checkmk.com/android-chrome-192x192.png")
        self.assertIn("embeds", content)
        self.assertEqual(len(content["embeds"]), 1)


if __name__ == '__main__':
    unittest.main()
