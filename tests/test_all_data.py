#!/usr/bin/env python3
"""
Data-driven tests that automatically run for all test data files.
Adding new JSON files to tests/data will automatically create new tests.
"""
import unittest
import sys
import os

# Add parent directory to path to import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import cmk_discord
from tests.test_data_loader import (
    load_test_data,
    generate_test_params_for_all_versions,
    get_available_versions
)


class TestAllServiceData(unittest.TestCase):
    """Test all service notification data files across all versions"""

    @classmethod
    def setUpClass(cls):
        """Generate test cases for all service data files"""
        cls.test_params = [
            (version, filepath, filename)
            for version, category, filepath, filename in generate_test_params_for_all_versions()
            if category == "service"
        ]

    def test_service_data_files_exist(self):
        """Verify that service test data files exist"""
        self.assertGreater(len(self.test_params), 0, "No service test data files found")

    def test_all_service_embeds_generate(self):
        """Test that all service data files generate valid embeds"""
        for version, filepath, filename in self.test_params:
            test_label = f"[{version}] {filepath}"
            with self.subTest(test=test_label):
                ctx = load_test_data(filepath, version=version)
                site_url = ctx.get("PARAMETER_2")
                timestamp = str(ctx.get("SHORTDATETIME", "2025-01-15T10:30:00")) + "+00:00"

                # Should generate embeds without errors
                try:
                    embeds = [cmk_discord.ServiceEmbed(ctx, site_url, timestamp).to_dict()]
                except Exception as e:
                    self.fail(f"Failed to generate embeds for {test_label}: {type(e).__name__}: {e}")

                # Basic validations
                self.assertEqual(len(embeds), 1, f"Expected 1 embed for {filename}")
                embed = embeds[0]

                # All embeds should have these required fields
                self.assertIn("title", embed)
                self.assertIn("description", embed)
                self.assertIn("color", embed)
                self.assertIn("timestamp", embed)
                self.assertIn("fields", embed)
                self.assertIn("footer", embed)

                # Validate state transition in description
                self.assertIn("->", embed["description"])

                # Validate color is valid
                self.assertIsInstance(embed["color"], int)
                self.assertIn(embed["color"], cmk_discord.ALERT_COLORS.values())

                # Validate fields structure
                self.assertEqual(len(embed["fields"]), 2)
                self.assertEqual(embed["fields"][0]["name"], "Host")
                self.assertEqual(embed["fields"][1]["name"], "Service")

                # If site_url provided, URL should be present
                if site_url:
                    self.assertIn("url", embed)
                    self.assertTrue(embed["url"].startswith(site_url))


class TestAllHostData(unittest.TestCase):
    """Test all host notification data files across all versions"""

    @classmethod
    def setUpClass(cls):
        """Generate test cases for all host data files"""
        cls.test_params = [
            (version, filepath, filename)
            for version, category, filepath, filename in generate_test_params_for_all_versions()
            if category == "host"
        ]

    def test_host_data_files_exist(self):
        """Verify that host test data files exist"""
        self.assertGreater(len(self.test_params), 0, "No host test data files found")

    def test_all_host_embeds_generate(self):
        """Test that all host data files generate valid embeds"""
        for version, filepath, filename in self.test_params:
            test_label = f"[{version}] {filepath}"
            with self.subTest(test=test_label):
                ctx = load_test_data(filepath, version=version)
                site_url = ctx.get("PARAMETER_2")
                timestamp = str(ctx.get("SHORTDATETIME", "2025-01-15T10:30:00")) + "+00:00"

                # Should generate embeds without errors
                try:
                    embeds = [cmk_discord.HostEmbed(ctx, site_url, timestamp).to_dict()]
                except Exception as e:
                    self.fail(f"Failed to generate embeds for {test_label}: {type(e).__name__}: {e}")

                # Basic validations
                self.assertEqual(len(embeds), 1, f"Expected 1 embed for {filename}")
                embed = embeds[0]

                # All embeds should have these required fields
                self.assertIn("title", embed)
                self.assertIn("description", embed)
                self.assertIn("color", embed)
                self.assertIn("timestamp", embed)
                self.assertIn("footer", embed)

                # Validate state transition in description
                self.assertIn("->", embed["description"])

                # Validate color is valid
                self.assertIsInstance(embed["color"], int)
                self.assertIn(embed["color"], cmk_discord.ALERT_COLORS.values())

                # Validate title contains hostname
                self.assertIn(ctx["HOSTNAME"], embed["title"])

                # If site_url provided, URL should be present
                if site_url:
                    self.assertIn("url", embed)
                    self.assertTrue(embed["url"].startswith(site_url))


class TestAllWebhookContent(unittest.TestCase):
    """Test webhook content generation for all data files"""

    @classmethod
    def setUpClass(cls):
        """Generate test cases for all data files"""
        cls.test_params = generate_test_params_for_all_versions()

    def test_all_webhook_content_generates(self):
        """Test that all data files generate valid webhook content"""
        for version, category, filepath, filename in self.test_params:
            test_label = f"[{version}] {filepath}"
            with self.subTest(test=test_label):
                ctx = load_test_data(filepath, version=version)
                site_url = ctx.get("PARAMETER_2")

                # Should generate webhook content without errors
                try:
                    webhook_url = "https://discord.com/api/webhooks/123/abc"
                    embed = cmk_discord.Embed.from_context(ctx, site_url)
                    webhook = cmk_discord.DiscordWebhook(webhook_url, embed, ctx.get("OMD_SITE"))
                    content = webhook._build_payload()
                except Exception as e:
                    self.fail(f"Failed to generate webhook content for {test_label}: {type(e).__name__}: {e}")

                # Validate structure
                self.assertIn("username", content)
                self.assertIn("avatar_url", content)
                self.assertIn("embeds", content)

                # Validate username contains site name
                self.assertIn(ctx["OMD_SITE"], content["username"])

                # Validate avatar URL
                self.assertTrue(content["avatar_url"].startswith("https://"))

                # Validate embeds
                self.assertEqual(len(content["embeds"]), 1)


class TestAllVersionsCoverage(unittest.TestCase):
    """Test version coverage and data consistency"""

    def test_all_versions_have_data(self):
        """Verify all versions have at least some test data"""
        versions = get_available_versions()
        self.assertGreater(len(versions), 0, "No test data versions found")

        for version in versions:
            with self.subTest(version=version):
                params = [
                    p for p in generate_test_params_for_all_versions()
                    if p[0] == version
                ]
                self.assertGreater(
                    len(params), 0,
                    f"Version {version} has no test data files"
                )

    def test_list_all_test_data(self):
        """List all available test data for documentation"""
        params = generate_test_params_for_all_versions()

        # Group by version
        by_version = {}
        for version, category, filepath, filename in params:
            if version not in by_version:
                by_version[version] = {"service": [], "host": []}
            by_version[version][category].append(filename)

        # Print summary (visible when running with -v)
        for version, categories in by_version.items():
            print(f"\nVersion {version}:")
            print(f"  Service files: {len(categories['service'])}")
            for f in categories['service']:
                print(f"    - {f}")
            print(f"  Host files: {len(categories['host'])}")
            for f in categories['host']:
                print(f"    - {f}")


if __name__ == '__main__':
    unittest.main()
