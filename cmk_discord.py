#!/usr/bin/env python3
# Discord Notification

# https://github.com/fschlag/cmk_discord
# Version: DEVELOPMENT-SNAPSHOT
# Release date: DEVELOPMENT-SNAPSHOT

import os
import sys
import datetime
import requests
from enum import IntEnum
from http import HTTPStatus


class DiscordColor(IntEnum):
    GREEN = 5763719
    ORANGE = 15105570
    RED = 15548997
    DARK_GREY = 9936031
    YELLOW = 16776960

ALERT_COLORS = {
    "CRITICAL": DiscordColor.RED,
    "DOWN": DiscordColor.RED,
    "WARNING": DiscordColor.YELLOW,
    "OK": DiscordColor.GREEN,
    "UP": DiscordColor.GREEN,
    "UNKNOWN": DiscordColor.ORANGE,
    "UNREACHABLE": DiscordColor.DARK_GREY,
}


def emoji_for_notification_type(notification_type: str):
    if notification_type.startswith("PROBLEM"):
        return ":rotating_light: "
    if notification_type.startswith("RECOVERY"):
        return ":white_check_mark: "
    if notification_type.startswith("ACKNOWLEDGEMENT"):
        return ":ballot_box_with_check: "
    if notification_type.startswith("FLAPPINGSTART"):
        return ":interrobang: "
    if notification_type.startswith("FLAPPINGSTOP"):
        return ":white_check_mark: "
    if notification_type.startswith("DOWNTIMESTART"):
        return ":alarm_clock: "
    if notification_type.startswith("DOWNTIMEEND"):
        return ":white_check_mark: "
    if notification_type.startswith("DOWNTIMECANCELLED"):
        return ":ballot_box_with_check: "
    return ""


class Embed:
    """Base class for Discord embeds"""

    def __init__(self, ctx: dict, site_url: str, timestamp: str):
        self.ctx = ctx
        self.site_url = site_url
        self.timestamp = timestamp

    @classmethod
    def from_context(cls, ctx: dict, site_url: str = None) -> "Embed":
        """Factory method to create the appropriate embed type based on context"""
        timestamp = str(datetime.datetime.fromisoformat(ctx["SHORTDATETIME"]).astimezone())
        embed_class = ServiceEmbed if ctx.get("WHAT") == "SERVICE" else HostEmbed
        return embed_class(ctx, site_url, timestamp)

    def _build_description(self, last_state_key: str, fallback_key: str, current_state_key: str, output_key: str) -> str:
        """Build the embed description with state transition and output"""
        description = "**%s -> %s**\n\n%s" % (
            self.ctx.get(last_state_key, self.ctx.get(fallback_key)),
            self.ctx.get(current_state_key),
            self.ctx.get(output_key),
        )
        if len(self.ctx.get("NOTIFICATIONCOMMENT", "")) > 0:
            description = "\n\n".join([description, self.ctx.get("NOTIFICATIONCOMMENT")])
        return description

    def _build_title(self, subject: str) -> str:
        """Build the embed title with emoji and notification type"""
        return "%s%s: %s" % (
            emoji_for_notification_type(self.ctx.get("NOTIFICATIONTYPE")),
            self.ctx.get("NOTIFICATIONTYPE"),
            subject,
        )

    def to_dict(self) -> dict:
        """Convert embed to dictionary format for Discord API"""
        raise NotImplementedError("Subclasses must implement to_dict()")


class ServiceEmbed(Embed):
    """Discord embed for service notifications"""

    def to_dict(self) -> dict:
        description = self._build_description(
            "LASTSERVICESTATE",
            "PREVIOUSSERVICEHARDSTATE",
            "SERVICESTATE",
            "SERVICEOUTPUT"
        )

        embed = {
            "title": self._build_title(self.ctx.get("SERVICEDESC")),
            "description": description,
            "color": ALERT_COLORS[self.ctx.get("SERVICESTATE")],
            "fields": [
                {"name": "Host", "value": self.ctx.get("HOSTNAME"), "inline": True},
                {"name": "Service", "value": self.ctx.get("SERVICEDESC"), "inline": True},
            ],
            "footer": {
                "text": self.ctx.get("SERVICECHECKCOMMAND"),
            },
            "timestamp": self.timestamp,
        }

        if self.site_url:
            embed["url"] = "".join([self.site_url, self.ctx.get("SERVICEURL")])
        return embed


class HostEmbed(Embed):
    """Discord embed for host notifications"""

    def to_dict(self) -> dict:
        description = self._build_description(
            "LASTHOSTSTATE",
            "PREVIOUSHOSTHARDSTATE",
            "HOSTSTATE",
            "HOSTOUTPUT"
        )

        embed = {
            "title": self._build_title("Host: %s" % self.ctx.get("HOSTNAME")),
            "description": description,
            "color": ALERT_COLORS[self.ctx.get("HOSTSTATE")],
            "footer": {"text": self.ctx.get("HOSTCHECKCOMMAND")},
            "timestamp": self.timestamp,
        }

        if self.site_url:
            embed["url"] = "".join([self.site_url, self.ctx.get("HOSTURL")])
        return embed


class DiscordWebhook:
    """Discord webhook for sending CheckMK notifications"""

    AVATAR_URL = "https://checkmk.com/android-chrome-192x192.png"

    def __init__(self, url: str, embed: Embed, site_name: str):
        self.url = url
        self.embed = embed
        self.site_name = site_name

    def _build_payload(self) -> dict:
        """Build the complete webhook payload"""
        return {
            "username": "Checkmk - " + self.site_name,
            "avatar_url": self.AVATAR_URL,
            "embeds": [self.embed.to_dict()],
        }

    def send(self) -> None:
        """Send the webhook to Discord"""
        response = requests.post(url=self.url, json=self._build_payload())
        if response.status_code != HTTPStatus.NO_CONTENT.value:
            sys.stderr.write(
                "Unexpected response when calling webhook url %s: %i. Response body: %s"
                % (self.url, response.status_code, response.text)
            )
            sys.exit(1)


def build_context():
    return {
        var[7:]: value
        for (var, value) in os.environ.items()
        if var.startswith("NOTIFY_")
    }


def main():
    ctx = build_context()
    webhook_url = ctx.get("PARAMETER_1")
    site_url = ctx.get("PARAMETER_2")

    if not webhook_url:
        sys.stderr.write("Empty webhook url given as parameter 1")
        sys.exit(2)
    if not webhook_url.startswith("https://discord.com"):
        sys.stderr.write(
            "Invalid Discord webhook url given as first parameter (not starting with https://discord.com )"
        )
        sys.exit(2)
    if site_url and not site_url.startswith("http"):
        sys.stderr.write(
            "Invalid site url given as second parameter (not starting with http): %s"
            % site_url
        )
        sys.exit(2)

    embed = Embed.from_context(ctx, site_url)
    webhook = DiscordWebhook(webhook_url, embed, ctx.get("OMD_SITE"))
    webhook.send()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        sys.stderr.write("Unhandled exception: %s\n" % e)
        sys.exit(2)
