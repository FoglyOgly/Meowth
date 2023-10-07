[![PyPI](https://img.shields.io/badge/discord.py-1.0.0a-green.svg)](https://github.com/Rapptz/discord.py/)
[![PyPI](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/downloads/release/python-364/)
[![PyPI](https://img.shields.io/badge/support-discord-lightgrey.svg)](https://discord.gg/hhVjAN8)

# Meowth
A Discord helper bot for Pokemon Go communities.

Meowth is a Discord bot written in Python 3.8+ built with [discord.py](https://github.com/Rapptz/discord.py/)

## Meowth v3 Features

Meowth assists with organising Pokemon Go communities with support for:

 - Team assignments
 - Server greetings
 - Wild Pokemon reporting
 - Raid reporting and RSVP
 - Research reporting
 - Pokebattler integration for raid counters
 - Gym matching extension for self-hosters

#### *`Note: All reports are provided by your active server members. Meowth does not support any TOS breaking features such as spoofing, Pokemon Go bot accounts and automated raid reporting.`*


You can join the Meowth Discord Support Server for setup help:  
https://discord.gg/hhVjAN8

# Install your own Meowth

## Dependencies

## **`Python 3.8+`**

[Go here](https://github.com/jackyaz/Meowth#installing-python) for details on how to install Python 3.6.

**For all future CLI commands, replace the command name `python3` with the relevant interpreter command name for your system (such as the common `py` command name on Windows). See details [here](https://github.com/jackyaz/Meowth#installing-python).**

## **`Other dependencies`**

Note: It is recommended to setup a venv for this as newer versions of some dependencies may have breaking changes.

```bash
python3 -m pip install -r requirements.txt
```

## **`S2Geometry`**

The Meowth mapping extension, which is responsible for storing location information on gyms, pokestops, etc., as well as for defining the geographical areas covered by reporting channels, the weather forecasting features, etc, is all based on the S2Geometry framework. This is a C++ package that has a Python wrapper that can be very very difficult to get working. Since the last time it was set up things seem to have changed quite a bit, so you will need to visit the [S2Geometry](https://s2geometry.io/) website to try to get it working with your Python installation. 

You can run the included ```build_s2.sh``` script to help with this.

## **`Meowth`**

1. Create a Bot user in the [Discord Developers panel](https://discordapp.com/developers/applications/me):
   - Click `New App`
   - Add an App Name, Description and App Icon (which will be intial bot avatar image)
   - Click `Create App`
   - Click `Create a Bot User`
   - Copy down your Client ID in the App Details box at the very top
   - In the App Bot User box, click to reveal Token and copy it down
   - *Optional:* Tick the Public Bot tickbox if you want to allow others to invite your bot to their own server.

1. Download the files in this repository, or your own fork if you intend to modify source  
   #### *``Note: If you alter the code significantly, adapt to support platforms we don't or integrate any TOS-breaking features, we ask you don't name your instance Meowth to avoid confusion to users between our instance and yours.``*

1. Install the bot by running:
   ```python3 setup.py install```

1. Copy the bot config template `config_blank.json`, rename to `config.json` and edit it:
   - `bot_token` is the Token you copied down earlier from the Discord Developers page and requires quotes as it's a string.
   - `default_prefix` is the prefix the bot will use by default until a guild specifies otherwise with the `set prefix` command
   - `master` is your personal discord account ID. This should be a long set of numbers like `174764205927432192` and should not have quotes around it, as it's an `int` not a string.
     * You can get your ID by enabling Developer Mode on the Discord Client, in `User Settings` > `Appearance` > `Advanced`, which then enables you to right-click your username in chat and select the option `Copy ID`
     * Another method is to mention yourself in chat and add `\` directly behind the mention for it to escape the mention string that's created, revealing your ID.
   - `type_id_dict` specifies what Pokemon Type emojis to use for your bot.  
      - By default, it assumes you have the emojis in your own discord guild, and doesn't use the specific external emoji format.  If you intend to allow the bot on multiple guilds, you will want to setup the external emoji strings.

1. Invite your Bot's User to your guild:
   - Get the Client ID you copied earlier from the Discord Developers page and replace the text `<CLIENT_ID>` with it in the following URL:  
   `https://discordapp.com/oauth2/authorize?client_id=<CLIENT_ID>&scope=bot&permissions=268822608`
   - Go to the URL, select your server and click `Authorize`
   - Verify you aren't a robot (if the captcha doesn't appear, disable your adblocker)
  


1. Run the launcher from the command prompt or terminal window:  
   `python3 launcher.py`

   If successful, it should send "Meowth! That's right!" as well as basic info on startup.

1. Simply type `!configure` in your server to start the configuration process as normal.

## Launcher Reference:
### Arguments
```
  --help, -h           Show the help message
  --auto-restart, -r   Auto-Restarts Meowth in case of a crash.
  --debug, -d          Prevents output being sent to Discord DM, as restarting
                       could occur often.
```

### Launch Meowth normally
```bash
python3 launcher.py
```

### Launch Meowth in debug mode if working on code changes
```bash
python3 launcher.py -d
```

### Launch Meowth with Auto-Restart
```bash
python3 launcher.py -r
```

## How to Translate Meowth:

We currently only support English with our public bot, with self-hosting being the only way to support other languages.

However, we have quite a few people [on our support server](https://discord.gg/hhVjAN8) who have been working on their own translations in a variety of languages.

If you are wanting to translate Meowth to your language, check there in our `#non-english-support` channel to see if someone might be able to share what they've worked on in the language you need.

To translate Meowth yourself, you can use pygettext.py and edit the generated translation files using [Poedit](https://poedit.net/). 

To generate a .pot file in Windows for example:

1. Nativate to `[pythonpath]\Python36\Tools\i18n\`

1. Open Command Prompt or PowerShell in this directory and run:

   `py pygettext.py -d <RESULTING FILENAME> <PATH TO SPECIFIC *.PY FILE>`

1. This will generate a meowth.pot that you can then translate using Poedit

1. Place the po/mo files from poedit into the `/locale/<language abbreviation>/LC_MESSAGES` directory (use other languages for reference)

1. Change Meowth's config.json `bot-language` and `pokemon-language` to `<language abbreviation>`

#### *``Note: Since moving to Python 3.6 we have utlised f-strings in our source code in order to take advantage of the cleanliness and additional performance it brings. Unfortunately, we have later found out it is incompatible with pygettext's string extraction and replacement methods. As such, any strings that require translating that use f-strings will need to be edited in source to use str.format() instead.``*

## Directions for using Meowth:
Note: Avoid punctuation inside commands.

Arguments within \< \> are required.<br/>
Arguments within \[ \] are optional.<br/>
pkmn = Pokemon

## General notes on Meowth:

Meowth relies completely on users for reports. Meowth was designed as an alternative to Discord bots that use scanners and other illegitimate sources of information about Pokemon Go. As a result, Meowth works only as well as the users who use it. As there are a lot of ways to interact with Meowth, there can be a bit of a rough learning period, but it quickly becomes worth it. Some commands are not necessary for normal usage and are only there for advanced users.

If you are having trouble getting Meowth running in your server, we have found that the majority of problems are either from permissions or your configuration. Check permissions with `!get perms` and check your configuration with `!configure` before asking for help in the support server.

## Known issues:

Compatibility with Python 3.6 on Mac OS X requires running "Install Certificates.command" in the Python 3.6 folder.

# Installing Python

## Windows

Install the latest Python 3.6 package from the official site if you have not already got it. At the time of writing, Python 3.6.5 was the latest maintenance release.  
https://www.python.org/downloads/release/python-365/

Python must be added the the environment's PATH, which is typically done automatically on install.

Your newly installed Python interpreter can be run in CLI in either Command Prompt or PowerShell typically with one of the following commands:

> `python`  
> `py`  
> `py -3`  
> `py -3.6`

To check your referenced interpreter version, use:
```bash
python --version
```

Be sure to replace all instructions that specify a certain interpreter command with the one relevant to your system, as this differs between each individual OS, configuration and environment.

#### Linux

If you're using Linux, you will likely have a version of Python 3 already installed on your system. Check your current version with:
```bash
python3 --version
```

If the version is not `3.8` or above, or `python3` is not found, you will need to install it on your system. You do not need to remove any existing versions from your system and it is usually not recommended to uninstal the default package as other system packages may rely on it.

# Database Setup

## Installing PostgreSQL

Meowth uses a Postgres database for data management. The schema and required data are provided in the database directory. You should make sure that postgres is installed on the machine you intend to run Meowth on as Meowth uses a purely local connection to the database. Visit the [Postgres website](https://www.postgresql.org/) to download Postgres if necessary. When installed, create a database called meowth on the server.

## Loading the required data

Using either the pgAdmin app or the psql command-line tool, load the files in the database directory starting with the schema. The schema contains the information on all the required tables as well as the triggers and functions that enable some real-time updates to trigger Meowth messages. Once the schema is loaded, each remaining file in the directory contains required data for another table. These are critical data regarding Pokemon, their moves, and so on. However, the data in them is badly out of date in some respects. You will likely have to do a lot of manual work here to get things up to date - for instance, many Pokemon which were not available in the wild at the time of the last update to the data are now available in the wild. You will either need to make a blanket update to allow all Pokemon to be reported in the wild or you will need to figure out which ones are missing. Instructions on how to update the data in the database likely requires some basic knowledge of SQL and is beyond the scope of this readme.

## Keeping the database up to date

Several Meowth features, notably the raid feature, require Meowth to have an up-to-date list of the available raid bosses in the raid_bosses table. In the past, this data was available via a Silph Road API. At the time of this writing there is no known alternative API, so updates must be done to the database manually. Additionally, as new Pokemon, forms, variants, moves, etc. become available in the game, various tables need to be kept up-to-date manually as well.

# Running Meowth locally

When Meowth began, it was a purely local effort run for one Discord server out of its creator's parent's house on a seldom-used iMac. In this configuration the only requirement to run Meowth for a single server or a small number of servers is to run it on a machine that can stay on and connected to the Internet most of the time. If that isn't doable, there are various cloud hosting services such as AWS, Azure, and GCP, along with others. Many of these offer free trials or some limited services for free indefinitely, but it definitely adds complexity to the deployment setup as well as any restarts that need to happen.