#!/usr/bin/env python3
import unittest
import sys
import os

# Add parent directory to path to import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'notifications')))

import cmk_discord
from tests.test_data_loader import load_test_data


class TestBuildServiceEmbeds(unittest.TestCase):
    """Tests for ServiceEmbed class"""

    def setUp(self):
        self.ctx = load_test_data("service/problem_critical.json")
        self.timestamp = "2025-01-15T10:30:00+00:00"

    def test_build_service_embeds_basic(self):
        embeds = [cmk_discord.ServiceEmbed(self.ctx, self.timestamp).to_dict()]

        self.assertEqual(len(embeds), 1)
        embed = embeds[0]

        self.assertEqual(embed["title"], ":rotating_light: PROBLEM: HTTP")
        self.assertIn("OK -> CRITICAL", embed["description"])
        self.assertIn("Connection timeout", embed["description"])
        self.assertEqual(embed["color"], cmk_discord.Embed.get_alert_color("CRITICAL"))
        self.assertEqual(embed["timestamp"], self.timestamp)
        self.assertEqual(embed["url"], "https://checkmkhost.mycompany.com/my_monitoring/check_mk/view.py?host=webserver01&service=HTTP")

    def test_build_service_embeds_with_comment(self):
        ctx = load_test_data("service/acknowledgement.json")
        embeds = [cmk_discord.ServiceEmbed(ctx, self.timestamp).to_dict()]

        embed = embeds[0]
        self.assertIn("Acknowledged by admin", embed["description"])

    def test_build_service_embeds_without_site_url(self):
        ctx_no_url = load_test_data("service/problem_critical.json")
        ctx_no_url.site_url = None
        embeds = [cmk_discord.ServiceEmbed(ctx_no_url, self.timestamp).to_dict()]

        embed = embeds[0]
        self.assertNotIn("url", embed)

    def test_build_service_embeds_warning_state(self):
        ctx = load_test_data("service/problem_warning.json")
        embeds = [cmk_discord.ServiceEmbed(ctx, self.timestamp).to_dict()]

        embed = embeds[0]
        self.assertEqual(embed["color"], cmk_discord.Embed.get_alert_color("WARNING"))

    def test_build_service_embeds_fields(self):
        embeds = [cmk_discord.ServiceEmbed(self.ctx, self.timestamp).to_dict()]

        embed = embeds[0]
        fields = embed["fields"]
        self.assertEqual(len(fields), 2)
        self.assertEqual(fields[0]["name"], "Host")
        self.assertEqual(fields[0]["value"], "webserver01")
        self.assertEqual(fields[1]["name"], "Service")
        self.assertEqual(fields[1]["value"], "HTTP")

    def test_build_service_embeds_recovery(self):
        ctx = load_test_data("service/recovery_ok.json")
        embeds = [cmk_discord.ServiceEmbed(ctx, self.timestamp).to_dict()]

        embed = embeds[0]
        self.assertEqual(embed["title"], ":white_check_mark: RECOVERY: HTTP")
        self.assertIn("CRITICAL -> OK", embed["description"])
        self.assertEqual(embed["color"], cmk_discord.Embed.get_alert_color("OK"))


class TestBuildHostEmbeds(unittest.TestCase):
    """Tests for HostEmbed class"""

    def setUp(self):
        self.ctx = load_test_data("host/problem_down.json")
        self.timestamp = "2025-01-15T10:30:00+00:00"

    def test_build_host_embeds_basic(self):
        embeds = [cmk_discord.HostEmbed(self.ctx, self.timestamp).to_dict()]

        self.assertEqual(len(embeds), 1)
        embed = embeds[0]

        self.assertEqual(embed["title"], ":rotating_light: PROBLEM: Host: webserver01")
        self.assertIn("UP -> DOWN", embed["description"])
        self.assertIn("Host Unreachable", embed["description"])
        self.assertEqual(embed["color"], cmk_discord.Embed.get_alert_color("DOWN"))
        self.assertEqual(embed["timestamp"], self.timestamp)
        self.assertEqual(embed["url"], "https://checkmkhost.mycompany.com/my_monitoring/check_mk/view.py?host=webserver01")

    def test_build_host_embeds_with_comment(self):
        ctx = load_test_data("host/downtime_start.json")
        embeds = [cmk_discord.HostEmbed(ctx, self.timestamp).to_dict()]

        embed = embeds[0]
        self.assertIn("Scheduled maintenance", embed["description"])

    def test_build_host_embeds_without_site_url(self):
        ctx_no_url = load_test_data("host/problem_down.json")
        ctx_no_url.site_url = None
        embeds = [cmk_discord.HostEmbed(ctx_no_url, self.timestamp).to_dict()]

        embed = embeds[0]
        self.assertNotIn("url", embed)

    def test_build_host_embeds_unreachable_state(self):
        ctx = load_test_data("host/unreachable.json")
        embeds = [cmk_discord.HostEmbed(ctx, self.timestamp).to_dict()]

        embed = embeds[0]
        self.assertEqual(embed["color"], cmk_discord.Embed.get_alert_color("UNREACHABLE"))

    def test_build_host_embeds_footer(self):
        embeds = [cmk_discord.HostEmbed(self.ctx, self.timestamp).to_dict()]

        embed = embeds[0]
        self.assertEqual(embed["footer"]["text"], "check-host-alive")

    def test_build_host_embeds_recovery(self):
        ctx = load_test_data("host/recovery_up.json")
        embeds = [cmk_discord.HostEmbed(ctx, self.timestamp).to_dict()]

        embed = embeds[0]
        self.assertEqual(embed["title"], ":white_check_mark: RECOVERY: Host: webserver01")
        self.assertIn("DOWN -> UP", embed["description"])
        self.assertEqual(embed["color"], cmk_discord.Embed.get_alert_color("UP"))


class TestBuildEmbeds(unittest.TestCase):
    """Tests for Embed.from_context factory method"""

    def test_build_embeds_for_service(self):
        ctx = load_test_data("service/problem_critical.json")

        embed = cmk_discord.Embed.from_context(ctx)
        embed_dict = embed.to_dict()

        self.assertIn("HTTP", embed_dict["title"])
        self.assertIsInstance(embed, cmk_discord.ServiceEmbed)

    def test_build_embeds_for_host(self):
        ctx = load_test_data("host/problem_down.json")

        embed = cmk_discord.Embed.from_context(ctx)
        embed_dict = embed.to_dict()

        self.assertIn("Host: webserver01", embed_dict["title"])
        self.assertIsInstance(embed, cmk_discord.HostEmbed)


class TestDiscordWebhook(unittest.TestCase):
    """Tests for DiscordWebhook class"""

    def test_webhook_payload(self):
        ctx = load_test_data("service/problem_critical.json")
        webhook_url = "https://discord.com/api/webhooks/123/abc"

        embed = cmk_discord.Embed.from_context(ctx)
        webhook = cmk_discord.DiscordWebhook(webhook_url, embed, ctx.omd_site)
        content = webhook._build_payload()

        self.assertEqual(content["username"], "Checkmk - production")
        self.assertEqual(content["avatar_url"], "https://checkmk.com/android-chrome-192x192.png")
        self.assertIn("embeds", content)
        self.assertEqual(len(content["embeds"]), 1)


if __name__ == '__main__':
    unittest.main()
