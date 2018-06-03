[![PyPI](https://img.shields.io/badge/discord.py-1.0.0a-green.svg)](https://github.com/Rapptz/discord.py/tree/rewrite/)
[![PyPI](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/downloads/release/python-364/)
[![PyPI](https://img.shields.io/badge/support-discord-lightgrey.svg)](https://discord.gg/hhVjAN8)

# Meowth
A Discord helper bot for Pokemon Go communities.

Meowth is a Discord bot written in Python 3.6.1+ built with [discord.py v1.0.0a (rewrite branch)](https://github.com/Rapptz/discord.py/tree/rewrite)

## Meowth v2 Features

Meowth assists with organising Pokemon Go communities with support for:

 - Team assignments
 - Server greetings
 - Wild Pokemon reporting
 - Raid reporting and RSVP
 - Research reporting
 - Pokebattler integration for raid counters
 - Silph card integration
 - Gym matching extension for self-hosters

#### *`Note: All reports are provided by your active server members. Meowth does not support any TOS breaking features such as spoofing, Pokemon Go bot accounts and automated raid reporting.`*

# Invite Public Meowth (no hosting required)


1. Use [THIS LINK](https://discordapp.com/oauth2/authorize?client_id=346759953006198784&scope=bot&permissions=268822608) to invite Meowth  
1. Select your server and click Authorize
1. Verify you aren't a robot (if the captcha doesn't appear, disable your adblocker)
1. In your server, type `!configure`
1. Go through the DM configuration session with Meowth to setup your server  
   *Be sure to read the prompts carefully and join the [support server](https://discord.gg/hhVjAN8) if you get stuck*
1. That's it! Enjoy!

#### *``Note: You must have the manage_server permission to invite a bot.``*

You can join the Meowth Discord Support Server for updates, setup help, feature requests, or just to test out the bot before you add it:  
https://discord.gg/hhVjAN8

# Install your own Meowth

## Dependancies

## **`Python 3.6.1+`**

[Go here](https://github.com/FoglyOgly/Meowth#installing-python) for details on how to install Python 3.6.

**For all future CLI commands, replace the command name `python3` with the relevant interpreter command name for your system (such as the common `py` command name on Windows). See details [here](https://github.com/FoglyOgly/Meowth#installing-python).**

## **`Discord.py v1.0.0a (Rewrite Branch)`**

The [rewrite branch of discord.py](https://github.com/Rapptz/discord.py/tree/rewrite) is an in-development branch that does not yet have an official stable release, however the default/master branch is feature-frozen, and lacks support for some of the newer features in discord such as categories.

If you intend to fork Meowth and alter any code, ensure you keep up to date with any breaking changes that might occur in this branch of discord.py.

```bash
python3 -m pip install -U git+https://github.com/Rapptz/discord.py@rewrite
```

#### *``Note: You will receive the following warning on your first run, which can be disregarded:``*
`PyNaCl is not installed, voice will NOT be supported`

## **`Git`**

To clone the files from our repository or your own forked repository on GitHub, you will need to have `git` installed.

### Windows

Download the [Git for Windows](https://git-scm.com/download/win) software.

On install, ensure the following:
 - `Windows Explorer integration` component (and all sub-components) is selected.
 - `Use Git from the Windows Command Prompt` is selected in the PATH adjustment step.
 - `Checkout as-is, commit Unix-style line endings` is selected in the line ending config step.
 
 ### Linux

First check if it's already installed with:
```bash
git --version
```

If it's not already installed, use your relevant package manager to install it.

For Debian and Ubuntu, it would usually be:
```bash
sudo apt-get install git
```

## **`Required Python Packages`**

Linux:
```bash
python3 -m pip install "requests>=2.18.4" "hastebin.py>=0.2" "python-dateutil>=2.6.1" "fuzzywuzzy>=0.15.1" "dateparser>=0.6.0"
```

## **`Optional Python Packages`**

`python-Levenshtein` is an optional package that increases the speed of fuzzy matching strings, which we use for matching up pokemon names, gym names and possibly other things in future. It also removes the `Using slow pure-python SequenceMatcher` warning emitted from the `fuzzywuzzy` python package, which can otherwise be ignored.

```bash
python3 -m pip install python-Levenshtein
```

The above may not be supported on all systems. You can sometimes find a suitable wheel [here](https://www.lfd.uci.edu/~gohlke/pythonlibs/#python-levenshtein) to install with, or you may have to look around for details suitable for your specific system.

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

### Admin or Manager Commands:

| Commands | Requirements  | Description |
| -------- |:-------------:| ------------|
| **!save**  | *Owner Only* | Saves the save data to file. |
| **!exit**  | *Owner Only* | Saves the save data to file and shutdown Meowth. |
| **!restart**  | *Owner Only* | Saves the save data to file and restarts Meowth. |
| **!announce** \[msg\] | *Owner Only* | Sends announcement message to server owners. |
| **!welcome** \[@member\] | *Owner Only* | Sends the welcome message to either user or mentioned member. |
| **!outputlog**  | *Server Manager Only* | Uploads the log file to hastebin and replies with the link. |
| **!set prefix** \[prefix\] | *Server Manager Only* | Sets Meowth's prefix. |
| **!set regional** \<pkmn\> | *Server Manager Only* | Sets server's regional raid boss. Accepts number or name. |
| **!set timezone** \<UTC offset\> | *Server Manager Only* | Sets server's timezone. Accepts numbers from -12 to 14. |
| **!get prefix** | *Server Manager Only* | Displays Meowth's prefix. |
| **!get perms** \[channelid\] | *Server Manager Only* | Displays Meowth's permissions in guild and channel. |
| **!welcome** \[user\] | *Owner Only* | Test welcome message on mentioned member |
| **!configure** | *Server Manager Only* | Configure Meowth |
| **!reload_json** | *Owner Only* | reloads JSON files for the server |
| **!raid_json** \[level\] \[bosslist\] | *Owner Only* | Edits or displays raid_info.json |
| **!changeraid** \[level or boss\] | *Channel Manager Only* | Changes raid boss or egg level |
| **!clearstatus**  | *Channel Manager<br/>Raid Channel* | Cancel everyone's status. |
| **!setstatus** \<user\> \<status\> \[count\] | *Channel Manager<br/>Raid Channel* | Changes raid channel status lists. |
| **!cleanroles** | *Channel Manager* | Removes all 0 member pokemon roles. |
| **!reset_board** \[user\] \[type\] | *Server Manager* | Resets \[user\]'s or server's leaderboard by type or total. |

### Miscellaneous Commands
| Commands | Requirements  | Description |
| -------- |:-------------:| ------------|
| **!help** \[command\] | - | Shows bot/command help, with descriptions. |
| **!about** | - | Shows info about Meowth. |
| **!uptime** | - | Shows Meowth's uptime. |
| **!team** \<team\> | - | Let's users set their team role. |
| **!set silph** \<Silph name\> | - | Links user\'s Silph Road account to Meowth. |
| **!silphcard** \[Silph name\] | - | Displays [Silph name]\'s or user\'s trainer card. |
| **!profile** \[username\] | - | Displays [username]\'s or user\'s profile. |
| **!leaderboard** \[type\] | - | Displays reporting leaderboard. Accepts total, raids, eggs, exraids, wilds, research. Defaults to total. |

### Pokemon Notification Commands:

| Commands | Requirements  | Description |
| -------- |:-------------:| ------------|
| **!want** \<pkmn\> | *Want Channel* | Adds a Pokemon to your notification roles. |
| **!unwant** \<pkmn\> | *Want Channel* | Removes a Pokemon from your notification roles. |
| **!unwant all**  | *Want Channel* | Removes all Pokemon from your notification roles. |

### Reporting Commands:

| Commands | Requirements  | Description |
| -------- |:-------------:| ------------|
| **!wild** \<pkmn\> \<location\> | *Region Channel* | Reports a wild pokemon, notifying people who want it. `Aliases: !w` |
| **!raid** \<pkmn\> \<place\> \[timer\] | *Region Channel* | Creates an open raid channel. `Aliases: !r`|
| **!raidegg** \<level\> \<place\> \[timer\] | *Region Channel* | Creates a raid egg channel. `Aliases: !re, !regg, !egg` |
| **!raid** \<pkmn\> | *Raid Egg Channel* | Converts raid egg to an open raid. |
| **!raid assume** \<pkmn\> | *Raid Egg Channel* | Assumes a pokemon on hatch. |
| **!exraid** \<pkmn\> \<place\> | *Region Channel* | Creates an exraid channel. `Aliases: !ex`|
| **!invite**  | *Region Channel* | Gain entry to exraids. |
| **!research** \[pokestop name \[optional URL\], quest, reward\] | *Region Channel* | Reports field research. Guided version available with just **!research** `Aliases: !res` |

### Raid Channel Management:

| Commands | Requirements  | Description |
| -------- |:-------------:| ------------|
| **!timer** | *Raid Channel* | Shows the expiry time for the raid. |
| **!timerset** \<timer\> | *Raid Channel* | Set the expiry time for the raid. |
| **!starttime** \[HH:MM AM/PM\] | *Raid Channel* | Set a time for a group to start a raid. |
| **!location** | *Raid Channel* | Shows the raid location. |
| **!location new** \<place/map\> | *Raid Channel* | Sets the raid location. |
| **!recover** | *Raid Channel* | Recovers an unresponsive raid channel. |
| **!duplicate** | *Raid Channel* | Reports the raid as a duplicate channel. |
| **!weather** | *Raid Channel* | Sets the weather for the raid. |
| **!counters** | *Raid Channel* | Simulate a Raid battle with Pokebattler. |
| **!archive** | *Raid Channel* | Mark a channel for archiving. |

### Status Management:

| Commands | Requirements  | Description |
| -------- |:-------------:| ------------|
| **!interested** \[number\] \[teamcounts\] \[boss list or all\] | *Raid Channel* | Sets your status for the raid to 'interested'. Teamcounts format is `m# v# i# u#`. You can also supply a list of bosses or 'all' that you are interested in. `Aliases: !i, !maybe` |
| **!coming** \[number\] \[teamcounts\] \[boss list or all\] | *Raid Channel* | Sets your status for the raid to 'coming'.  Teamcounts format is `m# v# i# u#`. You can also supply a list of bosses or 'all' that you are interested in. `Aliases: !c` |
| **!here** \[number\] \[teamcounts\] \[boss list or all\] | *Raid Channel* | Sets your status for the raid to 'here'.  Teamcounts format is `m# v# i# u#`. You can also supply a list of bosses or 'all' that you are interested in. `Aliases: !h` |
| **!lobby** \[number\] | *Raid Channel* | Indicate you are entering the raid lobby. `Aliases: !l` |
| **!starting** \[team\] | *Raid Channel* | Clears all members 'here', announce raid start. |
| **!backout** | *Raid Channel* | Request players in lobby to backout. |
| **!cancel**  | *Raid Channel* | Cancel your status. `Aliases: !x` |

### List Commands:

| Commands | Requirements  | Description |
| -------- |:-------------:| ------------|
| **!list** | *Region Channel* | Lists all raids from that region channel. `Aliases: !lists`|
| **!list**  | *Raid Channel* | Lists all member status' for the raid. `Aliases: !lists`|
| **!list tags** | *Raid Channel* | Same behavior as !list, but with @mentions. |
| **!list interested** | *Raid Channel* | Lists 'interested' members for the raid. |
| **!list coming**  | *Raid Channel* | Lists 'coming' members for the raid. |
| **!list here** | *Raid Channel* | Lists 'here' members for the raid. |
| **!list lobby** | *Raid Channel* | List the number and users who are in the raid lobby. |
| **!list teams** | *Raid Channel* | Lists teams of the members that have RSVPd. |
| **!list mystic** | *Raid Channel* | Lists teams of mystic members that have RSVPd. |
| **!list valor** | *Raid Channel* | Lists teams of valor members that have RSVPd. |
| **!list instinct** | *Raid Channel* | Lists teams of instinct members that have RSVPd. |
| **!list unknown** | *Raid Channel* | Lists members with unknown team that have RSVPd. |
| **!list bosses** | *Raid Channel* | Lists boss interest of members that have RSVPd. |
| **!list wants** | *Want Channel* | List the wants for the user. |
| **!list wilds** | *Region Channel* | List the wilds for the channel. |
| **!list research** | *Region Channel* | List the research for the channel. |

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

If the version is not `3.6.1` or above, or `python3` is not found, you will need to install it on your system. You do not need to remove any existing versions from your system and it is usually not recommended to uninstal the default package as other system packages may rely on it.

**There are a large variety of flavours of linux, so be sure to reference online guides on how to install the required Python version with your specific system and package manager.**

If you're on a version of Debian or Ubuntu and there is not a suitable ready-made package to install, the following is how to build and install Python 3.6.5 tailored for your specific system:
```bash
sudo apt-get update &&
sudo apt-get install ca-certificates libexpat1 libffi6 libgdbm3 libreadline7 libsqlite3-0 libssl1.1 dpkg-dev gcc libbz2-dev libc6-dev libexpat1-dev libffi-dev libgdbm-dev liblzma-dev libncursesw5-dev libreadline-dev libsqlite3-dev libssl-dev make tcl-dev tk-dev wget xz-utils zlib1g-dev gnupg dirmngr
wget https://www.python.org/ftp/python/3.6.5/Python-3.6.5.tar.xz
wget https://www.python.org/ftp/python/3.6.5/Python-3.6.5.tar.xz.asc
gpg --keyserver ha.pool.sks-keyservers.net --recv-keys 0D96DF4D4110E5C43FBFB17F2D347EA6AA65421D
gpg --batch --verify Python-3.6.5.tar.xz.asc Python-3.6.5.tar.xz
tar -xf Python-3.6.5.tar.xz
cd Python-3.6.5
./configure --enable-optimizations --enable-loadable-sqlite-extensions --enable-shared --with-system-expat --with-system-ffi
sudo make -j "$(nproc)"
sudo make altinstall
```
#### *``Credits to Devon from the discord.py support server for testing and providing the above script.``*
