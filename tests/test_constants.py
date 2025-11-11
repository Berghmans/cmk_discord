#!/usr/bin/env python3
import unittest
import sys
import os

# Add parent directory to path to import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import cmk_discord


class TestAlertColors(unittest.TestCase):
    """Tests for ALERT_COLORS constants"""

    def test_alert_colors_exist(self):
        expected_states = ["CRITICAL", "DOWN", "WARNING", "OK", "UP", "UNKNOWN", "UNREACHABLE"]

        for state in expected_states:
            self.assertIn(state, cmk_discord.ALERT_COLORS)
            self.assertIsInstance(cmk_discord.ALERT_COLORS[state], int)


class TestDiscordColors(unittest.TestCase):
    """Tests for DISCORD_COLORS constants"""

    def test_discord_colors_exist(self):
        expected_colors = ["Green", "Orange", "Red", "DarkGrey", "Yellow"]

        for color in expected_colors:
            self.assertIn(color, cmk_discord.DISCORD_COLORS)
            self.assertIsInstance(cmk_discord.DISCORD_COLORS[color], int)

    def test_discord_colors_are_valid_integers(self):
        # Discord colors should be positive integers (decimal representation of hex colors)
        for color_value in cmk_discord.DISCORD_COLORS.values():
            self.assertGreater(color_value, 0)
            self.assertLess(color_value, 16777216)  # Max value for 24-bit RGB color


if __name__ == '__main__':
    unittest.main()
