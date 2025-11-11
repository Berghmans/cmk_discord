# cmk_discord - Checkmk Discord Notifications

[![GitHub Release](https://img.shields.io/github/v/release/fschlag/cmk_discord)](https://github.com/fschlag/cmk_discord/releases)
![Static Badge](https://img.shields.io/badge/Tested%20with%20Checkmk-2.2.0p21-neon)
[![Static Badge](https://img.shields.io/badge/Link%20to-Checkmk%20Exchange-green)](https://exchange.checkmk.com/p/discord)

Discord notification plugin for Checkmk monitoring platform.

:warning: _Disclaimer: This is not an official plugin of Checkmk!_

## Acknowledgements

:clap: This project was originally created by [@fschlag](https://github.com/fschlag). Thank you for the excellent foundation and initial work on this plugin!

:clap: Inspired by the Discord notification plugin of [n00rm](https://github.com/n00rm) that was created as a GitHub
gist a while ago: https://gist.github.com/n00rm/32f1334b1dd2efc40122fee36551ef17
_(unfortunately only as a gist so I couldn't extend it via PR)_

## Features

* Colorized mesage to highlight alert state (incl. emoji :sparkles:)
* Supports all current notification types
    * :rotating_light: `PROBLEM`
    * :white_check_mark: `RECOVERY`
    * :ballot_box_with_check: `ACKNOWLEDGEMENT`
    * :interrobang: `FLAPPINGSTART`
    * :white_check_mark: `FLAPPINGSTOP`
    * :alarm_clock: `DOWNTIMESTART`
    * :white_check_mark: `DOWNTIMEEND`
    * :ballot_box_with_check: `DOWNTIMECANCELLED`
* Service: Includes service description details
* Supports comments (e.g. for acknowledgements or downtimes)
* Link to failed service/host

## Examples

![Example: Host down](images/example-1.png)
![Example: Filesystem Recovery](images/example-2.png)

## Installation

### Method 1: MKP installation (preferred)

Download the mkp either from [Checkmk Exchange](https://exchange.checkmk.com/p/discord) or from
the [latest releases](https://github.com/fschlag/cmk_discord/releases).

For installation instructions, please follow the official
documentation: https://docs.checkmk.com/latest/en/mkps.html#_adding_an_mkp

### Method 2: Manually

* Download `cmk_discord.py` from the [latest releases](https://github.com/fschlag/cmk_discord/releases)
* On your Checkmk server, login to the instance you want to install the plugin (`sudo su - <instance name>`)
* Copy `cmk_discord.py` to `~/local/share/check_mk/notifications`
* Make sure `cmk_discord.py` is executable: `chmod +x ~/local/share/check_mk/notifications/cmk_discord.py`

## Configuration

In your Checkmk ui, go to Setup --> Notifications --> Add rule

* As "Notification Method" select "Discord Notification"
* **First parameter** should be the Discord Webhook URL (mandatory)
* **Second parameter** (optional) URL to your checkmk instance. This is needed for links to the alerting
  service/host. (check known limitations below)

![cmk-discord setup ui](images/cmk-discord-setup-ui.png)

### Known limitations

**Site URL needs to be a FQDN**

If you see an error like

```text
Unexpected response when calling webhook url https://discord.com/xyz 400. Response body: {"embeds": ["0"]}
```

This probably means that your site URL (the second parameters you've setup) isn't a FQDN (full-qualified-domain-name).
Something like `http://checkmkhost/my_monitoring` won't work since "checkmkhost" is not a FQDN.

Instead using a FQDN `https://checkmkhost.mycompany.com/my_monitoring` (where "my_monitoring" is your site name)
