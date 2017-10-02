# Meowth
A Discord helper bot for Pokemon Go communities.

Meowth is a Discord bot written in Python 3.5 using version 0.16.8 of the discord.py library.

## Meowth 2.0 is here! 

Meowth is now able to handle being on multiple servers of any size in any part of the world and can be invited to your server without having to install Python or run anything on a local machine yourself. The configuration process is now handled completely on Discord via DM with the server owner. First, a list of current features:

1. User-driven (not automated) wild spawn and raid reporting.
2. Role management for each Pokemon species (Discord limits a server to 250 roles, however) that allows each user to opt-in only for the Pokemon they want. These roles are mentioned when spawns or raids are reported.
3. Raid reporting: Report either !raidegg, !raid or !exraid on the server to have meowth create channels to organise in. Certain commands can be used within raid channels, such as updating your stauts with !interested, !coming and !here. Users can easily determine the status of involved members with the !list command. Meowth also queries Google Maps to get a guess of the raid location (no access to the game means no list of gyms), or you can paste a maps link in the channel after creation to update it to exact coordinates.
4. Optional team management and new member welcome functions.

## Directions for inviting a remotely hosted Meowth to your server:
Note: You must have manage_server permissions to invite.
1. Follow this link: https://discordapp.com/oauth2/authorize?client_id=346759953006198784&scope=bot&permissions=268822608
2. Select your server.
3. In your server, type !configure.
4. Meowth will DM you and ask you some questions about your time zone, what functions you want to enable, what channels you want to restrict certain functions to, and what locations to insert to Google Maps queries (these are channel-specific). 
5. That's it! Enjoy!

You can join the Meowth server here for updates, setup help, feature requests, or just to test out the bot before you add it. https://discord.gg/hhVjAN8 

If you want to tinker with Meowth yourself, you can still download this repo, make whatever changes you want (or keep everything if you want) and run Meowth locally. The configure process is the same except you'll have to use your own bot token.

## Directions for installing and running the bot on your server:

1. Install Python 3.5. 
https://www.python.org/downloads/release/python-350/

2. Install the packages needed to run meowth: discord.py, Pillow, pytesseract:

Linux:
```bash
python3 -m pip install -U discord.py pillow requests pytesseract
```

Windows: 
```bash
py -m pip install -U discord.py pillow requests pytesseract
```

3. Download the files in this repository. The source code is in meowth.py and bot config is in config.json.

4. Go to https://discordapp.com/developers/applications/me#top and create a new app. 

5. Name it and upload the avatar of your choice. 

6. Create a bot user for your app and reveal the bot token to copy it.

7. Open config.json in a text editor (a good one to use is Notepad++) and paste the bot token into the value for "bot_token", replacing the "yourtoken" string.

8. Replace the "master" value in config.json with your full discord username with the 4 digits after the hash. 

9. Run meowth.py from the command prompt or terminal window. If successful, it should show "Meowth! That's right!".

10. Go back to your Discord application page and copy the Client ID.

11. Go to the following link, replacing <CLIENT_ID> with the Client ID you copied.
https://discordapp.com/oauth2/authorize?client_id=<CLIENT_ID>&scope=bot&permissions=268822608

12. Select the server you want to add Meowth to and complete the prompts. If you get to an empty screen and didn't get to see the Google new reCaptcha tickbox, disable your adblocker.

9. The bot should now have sent you DM in Discord. Add the team roles: mystic, instinct and valor. Ensure they're below the bot role in the server role hierarchy. 

10. Simply type !configure in your server to start the configuration process.

## Directions for using Meowth:
Note: avoid punctuation of any kind inside commands. The <> in these instructions are there for decoration

1. !raid <teamname> - Adds you to a team role on the server. These roles should be created beforehand.

2. !want <pokemonname> - Adds a pokemon role to you so you'll be mentioned on reports. Meowth will create a role if none exists.

3. !wild <pokemonname> <location> - Meowth will @mention <pokemonname> and include a Google Maps link to <location>. If <location> is blank, Meowth will ask for more details.

4. !raid <pokemonname> <location> <time remaining> - Mentions the pokemon role, gives a google maps link o creates a new channel by the name of
#<pokemonname>-<location>. The message shows type effectiveness against the Pokemon. The raid channel will automatically delete after <time remaining> has expired. If <time remaining> is not given or is given in a format other than H:MM, Meowth will assume a two-hour time remaining and ask you to use !timerset.

5. !coming/!here - In a raid channel, this will tell Meowth that you are on your way to or at a raid. If you have multiple trainers with you, add a number, such as !coming <number>.

6. !cancel - In a raid channel, this will tell Meowth to remove you from the on the way or waiting lists. The !cancel command removes you from either list if you are on one.

7. !otw/!waiting/!lists - In a raid channel, these commands tell Meowth to list and mention the trainers who said they were on the way
or at a raid. It also includes the total number. !lists shows all member statuses.

8. !starting - in a raid channel, this command tells Meowth to delete the !waiting list for that raid. Meowth will mention the
users and ask them to respond with !here if they are still waiting.

9. !timerset H:MM - in a raid channel, this tells Meowth how long is remaining on the raid. Meowth will send a message notifying
the time at which the raid will end. Also overwrites any previously used !timerset command for that raid.

10. !timer - in a raid channel, tells Meowth to resend the message from the last !timerset command. Prevents unnecessary
scrolling.


## General notes on Meowth:

Meowth relies completely on user reports of raids, wild spawns, on the way to a raid, at a raid, and starting a raid. Meowth
was designed as an alternative to Discord bots that use scanners and other illegitimate sources of information about Pokemon Go.
As a result, Meowth works only as well as the users who use it. As there are 10+ ways of interacting with Meowth, there
can be a bit of a rough learning period, but it quickly becomes worth it.

## Known issues:

Compatibility with Python 3.6 on Mac OS X requires running "Install Certificates.command" in the Python 3.6 folder. Incompatible with discord.py 1.0



