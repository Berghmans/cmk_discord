#!/usr/bin/env python3
import unittest
import sys
import os

# Add parent directory to path to import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import cmk_discord


class TestEmojiForNotificationType(unittest.TestCase):
    """Tests for emoji_for_notification_type function"""

    def test_problem_notification(self):
        self.assertEqual(cmk_discord.emoji_for_notification_type("PROBLEM"), ":rotating_light: ")
        self.assertEqual(cmk_discord.emoji_for_notification_type("PROBLEMHOST"), ":rotating_light: ")

    def test_recovery_notification(self):
        self.assertEqual(cmk_discord.emoji_for_notification_type("RECOVERY"), ":white_check_mark: ")
        self.assertEqual(cmk_discord.emoji_for_notification_type("RECOVERYHOST"), ":white_check_mark: ")

    def test_acknowledgement_notification(self):
        self.assertEqual(cmk_discord.emoji_for_notification_type("ACKNOWLEDGEMENT"), ":ballot_box_with_check: ")

    def test_flapping_start_notification(self):
        self.assertEqual(cmk_discord.emoji_for_notification_type("FLAPPINGSTART"), ":interrobang: ")

    def test_flapping_stop_notification(self):
        self.assertEqual(cmk_discord.emoji_for_notification_type("FLAPPINGSTOP"), ":white_check_mark: ")

    def test_downtime_start_notification(self):
        self.assertEqual(cmk_discord.emoji_for_notification_type("DOWNTIMESTART"), ":alarm_clock: ")

    def test_downtime_end_notification(self):
        self.assertEqual(cmk_discord.emoji_for_notification_type("DOWNTIMEEND"), ":white_check_mark: ")

    def test_downtime_cancelled_notification(self):
        self.assertEqual(cmk_discord.emoji_for_notification_type("DOWNTIMECANCELLED"), ":ballot_box_with_check: ")

    def test_unknown_notification_type(self):
        self.assertEqual(cmk_discord.emoji_for_notification_type("UNKNOWN_TYPE"), "")
        self.assertEqual(cmk_discord.emoji_for_notification_type(""), "")


if __name__ == '__main__':
    unittest.main()
