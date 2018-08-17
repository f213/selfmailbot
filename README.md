# Selfmailbot — the bot that sends all messages to your inbox

![](https://user-images.githubusercontent.com/1592663/44275252-e059dd00-a24c-11e8-8ca9-44e3081c5ab6.png)

[![CircleCI](https://circleci.com/gh/f213/selfmailbot.svg?style=svg&circle-token=b689a894fe6b84c56e1052b95e3c2a7c0246bec6)](https://circleci.com/gh/f213/selfmailbot) [![uptime](https://img.shields.io/uptimerobot/ratio/7/m780844027-6fa56428dcb0970de6905410.svg?style=flat-square)](https://stats.uptimerobot.com/gn1MkTvPv) ![](https://img.shields.io/github/license/f213/selfmailbot.svg?style=flat-square)

Useful for GTD and email geeks.

## Installation

This bots works as free-for-all SaaS at [selfmailbot.co](https://t.me/selfmailbot), but you are free to build your own bot from this source code.

The bot app is dockerized, but if you want to run the bot on the local machine, you are going to need this:

* Python 3.6
* Redis
* Celery
* Mailgun account

## Configuration

Configure the bot through the environment variables (or the `.env` file):

```
BOT_TOKEN=100500:S3cr37T0k3n
MAILGUN_DOMAIN=mail.your.bot.addrress
MAILGUN_API_KEY=key-s3cr3t
MAILGUN_FROM=Note to self <yourbot@e.mail>
CELERY_BROKER_URL=redis://localhost:6379
```

## Hacking

PR's are welcome
