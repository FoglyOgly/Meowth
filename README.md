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

## Docker

### Installing Docker

[Go here](https://docs.docker.com/engine/install/) for details on how to install Docker.

### Usage
A Docker image for this app is available on [Docker Hub](https://hub.docker.com/r/jackyaz/meowth)

#### docker cli
```bash
docker run -d \
  --name=meowth \
  -v /path/to/data:/app/config \
  --restart unless-stopped \
  jackyaz.io/jackyaz/meowth
```

#### Parameters
The Docker image supports some parameters. These parameters are separated by a colon and indicate `<external>:<internal>` respectively. For example, `-v /apps/meowth:/app/config` would map ```/apps/meowth``` on the Docker host to ```/app/config``` inside the container, allowing you to edit the configuration file from outside the container.

| Parameter | Function |
| :----: | --- |
| `-v /app/config` | Local path for Meowth configuration directory |

## Running Meowth

1. Create a Bot user in the [Discord Developers panel](https://discordapp.com/developers/applications/me):
   - Click `New Application`
   - Add an App Name and click Create
   - Make a note of your Application ID
   - Click `Bot`
   - Enable the Privileged Gateway Intents and click Save Changes
   - Click Reset Token and then make a note of the generated Token
   - *Optional:* Tick the Public Bot tickbox if you want to allow others to invite your bot to their own server.

1. Copy the bot config template `config_template.py`, rename to `config.py` and edit it:
   - `bot_token` is the Token you copied down earlier from the Discord Developers page and requires quotes as it's a string.
   - `default_prefix` is the prefix the bot will use by default until a guild specifies otherwise with the `set prefix` command
   - `bot_master` is your personal discord account ID. This should be a long set of numbers like `174764205927432192` and should not have quotes around it, as it's an `int` not a string.
     * You can get your ID by enabling Developer Mode on the Discord Client, in `User Settings` > `Appearance` > `Advanced`, which then enables you to right-click your username in chat and select the option `Copy ID`
     * Another method is to mention yourself in chat and add `\` directly behind the mention for it to escape the mention string that's created, revealing your ID.
   - `xyz_emoji` specifies which emojis to use for your bot.
      - By default, it assumes you have the emojis in your own discord guild, and doesn't use the specific external emoji format.  If you intend to allow the bot on multiple guilds, you will want to setup the external emoji strings.

1. Invite your Bot's User to your guild:
   - Get the Application ID you copied earlier from the Discord Developers page and replace the text `<APPLICATION_ID>` with it in the following URL:
   `https://discordapp.com/oauth2/authorize?client_id=<CLIENT_ID>&scope=bot&permissions=18135768366161`
   - Go to the URL, select your server and click `Authorize`
   - Verify you aren't a robot (if the captcha doesn't appear, disable your adblocker)

1. Start the Docker container. You can check everything is up and running by checking the container logs (e.g. ```sudo docker logs -f meowth```) and looking for output similar to the below:
   ```
   Launching... Connected.
   Shard 0 is ready.
   We're on!
   
   Bot Version: 3
   
   Python Version: 3.10.13
   Discord.py Version: 2.0.0a3786+g3d74da8d
   Platform: Linux-5.15.90.1-microsoft-standard-WSL2-x86_64-with-glibc2.36
   
   Servers: 1
   Members: 1
   
   Invite URL: https://discord.com/oauth2/authorize?client_id=1234567890&scope=bot&permissions=18135768366161
   ```

1. Simply type `!configure` in your server to start the configuration process as normal.

## Directions for using Meowth:
Note: Avoid punctuation inside commands.

Arguments within \< \> are required.<br/>
Arguments within \[ \] are optional.<br/>
pkmn = Pokemon

## General notes on Meowth:

Meowth relies completely on users for reports. Meowth was designed as an alternative to Discord bots that use scanners and other illegitimate sources of information about Pokemon Go. As a result, Meowth works only as well as the users who use it. As there are a lot of ways to interact with Meowth, there can be a bit of a rough learning period, but it quickly becomes worth it. Some commands are not necessary for normal usage and are only there for advanced users.

If you are having trouble getting Meowth running in your server, we have found that the majority of problems are either from permissions or your configuration. Check permissions with `!get perms` and check your configuration with `!configure` before asking for help in the support server.

# Database Setup

Meowth uses a Postgres database for data management.

## Using the Docker container's built-in Postgres database

The Docker container includes Postgres with a pre-configured database ready for use, no extra steps are required.

## Using a separate Postgres database

### Loading the required data

The schema and required data are provided in the database directory. Using either the pgAdmin app or the psql command-line tool, load the files in the database directory starting with the schema. The schema contains the information on all the required tables as well as the triggers and functions that enable some real-time updates to trigger Meowth messages. Once the schema is loaded, each remaining file in the directory contains required data for another table. These are critical data regarding Pokemon, their moves, and so on. However, the data in them is badly out of date in some respects. You will likely have to do a lot of manual work here to get things up to date - for instance, many Pokemon which were not available in the wild at the time of the last update to the data are now available in the wild. You will either need to make a blanket update to allow all Pokemon to be reported in the wild or you will need to figure out which ones are missing. Instructions on how to update the data in the database likely requires some basic knowledge of SQL and is beyond the scope of this readme.

### Configuring Meowth

Modify the relevant settings in config.py in the db_details section.

## Keeping the database up to date

Several Meowth features, notably the raid feature, require Meowth to have an up-to-date list of the available raid bosses in the raid_bosses table. In the past, this data was available via a Silph Road API. At the time of this writing there is no known alternative API, so updates must be done to the database manually. Additionally, as new Pokemon, forms, variants, moves, etc. become available in the game, various tables need to be kept up-to-date manually as well.
