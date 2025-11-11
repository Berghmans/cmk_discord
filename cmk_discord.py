#!/usr/bin/env python3
# Discord Notification

# https://github.com/fschlag/cmk_discord
# Version: DEVELOPMENT-SNAPSHOT
# Release date: DEVELOPMENT-SNAPSHOT

import os
import sys
import datetime
import requests
from dataclasses import dataclass
from enum import IntEnum
from http import HTTPStatus
from typing import Optional


@dataclass
class Context:
    """CheckMK notification context"""
    # Common fields
    what: str  # SERVICE or HOST
    notification_type: str
    short_datetime: str
    omd_site: str
    hostname: str

    # Optional parameters
    webhook_url: Optional[str] = None  # PARAMETER_1
    site_url: Optional[str] = None     # PARAMETER_2

    # Service-specific fields
    service_desc: Optional[str] = None
    service_state: Optional[str] = None
    previous_service_state: Optional[str] = None
    service_output: Optional[str] = None
    service_check_command: Optional[str] = None
    service_url: Optional[str] = None

    # Host-specific fields
    host_state: Optional[str] = None
    previous_host_state: Optional[str] = None
    host_output: Optional[str] = None
    host_check_command: Optional[str] = None
    host_url: Optional[str] = None

    # Optional comment
    notification_comment: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "Context":
        """Create Context from environment variable dictionary"""
        return cls(
            what=data.get("WHAT", ""),
            notification_type=data.get("NOTIFICATIONTYPE", ""),
            short_datetime=data.get("SHORTDATETIME", ""),
            omd_site=data.get("OMD_SITE", ""),
            hostname=data.get("HOSTNAME", ""),
            webhook_url=data.get("PARAMETER_1"),
            site_url=data.get("PARAMETER_2"),
            service_desc=data.get("SERVICEDESC"),
            service_state=data.get("SERVICESTATE"),
            previous_service_state=data.get("LASTSERVICESTATE") or data.get("PREVIOUSSERVICEHARDSTATE"),
            service_output=data.get("SERVICEOUTPUT"),
            service_check_command=data.get("SERVICECHECKCOMMAND"),
            service_url=data.get("SERVICEURL"),
            host_state=data.get("HOSTSTATE"),
            previous_host_state=data.get("LASTHOSTSTATE") or data.get("PREVIOUSHOSTHARDSTATE"),
            host_output=data.get("HOSTOUTPUT"),
            host_check_command=data.get("HOSTCHECKCOMMAND"),
            host_url=data.get("HOSTURL"),
            notification_comment=data.get("NOTIFICATIONCOMMENT"),
        )


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


@dataclass
class Embed:
    """Base class for Discord embeds"""

    ctx: Context
    timestamp: str
    previous_state: Optional[str]
    current_state: Optional[str]
    output: Optional[str]
    title_subject: str
    color: int
    footer_text: Optional[str]
    url_path: str
    fields: Optional[list] = None

    @classmethod
    def from_context(cls, ctx: Context) -> "Embed":
        """Factory method to create the appropriate embed type based on context"""
        timestamp = str(datetime.datetime.fromisoformat(ctx.short_datetime).astimezone())
        embed_class = ServiceEmbed if ctx.what == "SERVICE" else HostEmbed
        return embed_class(ctx, timestamp)

    def _build_description(self) -> str:
        """Build the embed description with state transition and output"""
        description = "**%s -> %s**\n\n%s" % (
            self.previous_state,
            self.current_state,
            self.output,
        )
        if self.ctx.notification_comment:
            description = "\n\n".join([description, self.ctx.notification_comment])
        return description

    def _build_title(self) -> str:
        """Build the embed title with emoji and notification type"""
        return "%s%s: %s" % (
            emoji_for_notification_type(self.ctx.notification_type),
            self.ctx.notification_type,
            self.title_subject,
        )

    def to_dict(self) -> dict:
        """Convert embed to dictionary format for Discord API"""
        embed = {
            "title": self._build_title(),
            "description": self._build_description(),
            "color": self.color,
            "timestamp": self.timestamp,
        }

        # Add footer if available
        if self.footer_text:
            embed["footer"] = {"text": self.footer_text}

        # Add fields if available
        if self.fields:
            embed["fields"] = self.fields

        # Add URL if site_url is configured
        if self.ctx.site_url:
            embed["url"] = "".join([self.ctx.site_url, self.url_path])

        return embed


class ServiceEmbed(Embed):
    """Discord embed for service notifications"""

    def __init__(self, ctx: Context, timestamp: str):
        super().__init__(
            ctx=ctx,
            timestamp=timestamp,
            previous_state=ctx.previous_service_state,
            current_state=ctx.service_state,
            output=ctx.service_output,
            title_subject=ctx.service_desc,
            color=ALERT_COLORS[ctx.service_state],
            footer_text=ctx.service_check_command,
            url_path=ctx.service_url,
            fields=[
                {"name": "Host", "value": ctx.hostname, "inline": True},
                {"name": "Service", "value": ctx.service_desc, "inline": True},
            ],
        )


class HostEmbed(Embed):
    """Discord embed for host notifications"""

    def __init__(self, ctx: Context, timestamp: str):
        super().__init__(
            ctx=ctx,
            timestamp=timestamp,
            previous_state=ctx.previous_host_state,
            current_state=ctx.host_state,
            output=ctx.host_output,
            title_subject="Host: %s" % ctx.hostname,
            color=ALERT_COLORS[ctx.host_state],
            footer_text=ctx.host_check_command,
            url_path=ctx.host_url,
        )


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


def build_context() -> Context:
    """Build Context from environment variables"""
    env_dict = {
        var[7:]: value
        for (var, value) in os.environ.items()
        if var.startswith("NOTIFY_")
    }
    return Context.from_dict(env_dict)


def main():
    ctx = build_context()

    if not ctx.webhook_url:
        sys.stderr.write("Empty webhook url given as parameter 1")
        sys.exit(2)
    if not ctx.webhook_url.startswith("https://discord.com"):
        sys.stderr.write(
            "Invalid Discord webhook url given as first parameter (not starting with https://discord.com )"
        )
        sys.exit(2)
    if ctx.site_url and not ctx.site_url.startswith("http"):
        sys.stderr.write(
            "Invalid site url given as second parameter (not starting with http): %s"
            % ctx.site_url
        )
        sys.exit(2)

    embed = Embed.from_context(ctx)
    webhook = DiscordWebhook(ctx.webhook_url, embed, ctx.omd_site)
    webhook.send()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        sys.stderr.write("Unhandled exception: %s\n" % e)
        sys.exit(2)
