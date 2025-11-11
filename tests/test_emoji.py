#!/usr/bin/env python3
import unittest
import sys
import os

# Add parent directory to path to import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import cmk_discord


class TestEmojiForNotificationType(unittest.TestCase):
    """Tests for Embed.get_emoji() static method"""

    def test_problem_notification(self):
        self.assertEqual(cmk_discord.Embed.get_emoji("PROBLEM"), ":rotating_light:")
        self.assertEqual(cmk_discord.Embed.get_emoji("PROBLEMHOST"), ":rotating_light:")

    def test_recovery_notification(self):
        self.assertEqual(cmk_discord.Embed.get_emoji("RECOVERY"), ":white_check_mark:")
        self.assertEqual(cmk_discord.Embed.get_emoji("RECOVERYHOST"), ":white_check_mark:")

    def test_acknowledgement_notification(self):
        self.assertEqual(cmk_discord.Embed.get_emoji("ACKNOWLEDGEMENT"), ":ballot_box_with_check:")

    def test_flapping_start_notification(self):
        self.assertEqual(cmk_discord.Embed.get_emoji("FLAPPINGSTART"), ":interrobang:")

    def test_flapping_stop_notification(self):
        self.assertEqual(cmk_discord.Embed.get_emoji("FLAPPINGSTOP"), ":white_check_mark:")

    def test_downtime_start_notification(self):
        self.assertEqual(cmk_discord.Embed.get_emoji("DOWNTIMESTART"), ":alarm_clock:")

    def test_downtime_end_notification(self):
        self.assertEqual(cmk_discord.Embed.get_emoji("DOWNTIMEEND"), ":white_check_mark:")

    def test_downtime_cancelled_notification(self):
        self.assertEqual(cmk_discord.Embed.get_emoji("DOWNTIMECANCELLED"), ":ballot_box_with_check:")

    def test_unknown_notification_type(self):
        self.assertEqual(cmk_discord.Embed.get_emoji("UNKNOWN_TYPE"), "")
        self.assertEqual(cmk_discord.Embed.get_emoji(""), "")


if __name__ == '__main__':
    unittest.main()
