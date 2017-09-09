# Meowth
A Discord helper bot for Pokemon Go communities.

Meowth is a Discord bot written in Python 3.5 using version 0.16.8 of the discord.py library.

## Meowth 2.0 is here! 

Meowth is now able to handle being on multiple servers of any size in any part of the world and can be invited to your server without having to install Python or run anything on a local machine yourself. The configuration process is now handled completely on Discord via DM with the server owner. First, a list of current features:

1. User-driven (not automated) wild spawn and raid reporting.
2. Role management for each Pokemon species (Discord limits a server to 250 roles, however) that allows each user to opt-in only for the Pokemon they want. These roles are mentioned when spawns or raids are reported.
3. Raid coordination: several methods of interacting with Meowth allow users to declare themselves as interested in, on the way to, or at a raid. These are compiled into lists that let users easily determine the size of the current raid party. Each reported raid gets its own channel that is deleted when the reported time on the raid expires. Meowth also queries Google Maps to get a guess of the raid location (no access to the game means no list of gyms).
4. Optional team management and new member welcome functions.

## Directions for inviting a remotely hosted Meowth to your server:
1. Be a user with the "Manage Server" permission on the server you're trying to invite Meowth to, or get such a person to follow these directions. The server owner will have to do the configure process anyway, so you might as well get that person.
2. Follow this link: https://discordapp.com/oauth2/authorize?client_id=346759953006198784&scope=bot&permissions=268471376 and select your server.
3. In your server, type !configure if you are the server owner. Meowth will DM you and ask you some questions about your time zone, what functions you want to enable, what channels you want to restrict certain functions to, and what locations to insert to Google Maps queries (these are channel-specific). Do NOT send anything to your server while in this process as a few times Meowth is just waiting to see any message from you. If you make a mistake just type !configure in your server to start over.
4. Meowth will send you a file with some custom emoji in it. You can just bulk upload those to your server. Meowth currently uses 23 custom emoji. 18 of these are type icons (for displaying type weaknesses of raid bosses), 3 of them are team icons, and 2 are for raid coordination. All functions are available without custom emoji, but the type icons in particular look slick in raid reports.
5. That's it! You can join the Meowth server here for updates, setup help, feature requests, or just to test out the bot before you add it. https://discord.gg/hhVjAN8 

If you want to tinker with Meowth yourself, you can still download this repo, make whatever changes you want (or keep everything if you want) and run Meowth locally. The configure process is the same except you'll have to use your own bot token.

## Directions for installing and running the bot on your server:

1. Install Python 3.5 for whatever OS you have on your home computer. https://www.python.org/downloads/release/python-350/

2. Install discord.py. To do this, run this command in your command prompt: python3 -m pip install -U discord.py
(On Windows: py -m pip install -U discord.py should work)

3. Download the files in this repository. The source code is in meowth.py, bot config is in config.json and language files are in locale.

4. Go here https://discordapp.com/developers/applications/me#top and create a new app. Name it Meowth if you like and upload the 
Meowth avatar included or one of your own. 

5. Create a bot user for your app and reveal the bot token, then copy it. Open config.json in a text editor.  Paste the bot token into line 13, replacing the "mytokenhere" string.

6. Run meowth.py from the command prompt or terminal window. If successful, it should print "Meowth! That's right!" or similar to the 
console.

7. Go to your Discord application page and copy the Client ID. Paste it into the following link, replacing <CLIENT_ID>.
   https://discordapp.com/oauth2/authorize?client_id=<CLIENT_ID>&scope=bot&permissions=268822608 

5. Select the server you want to add Meowth to and complete the prompts.

9. The bot should now be online and have sent you DM in Discord. Simply type !configure in your server to start the configuration process.



## Directions for using Meowth:
Note: avoid punctuation of any kind inside commands. The <> in these instructions are there for decoration

1. !team <teamname> - adds you to a team role on the server. These roles must be created beforehand.

2. !want <pokemonname> - adds you to an invisible role for a Pokemon. Meowth will create a role if none exists.

3. !wild <pokemonname> <location> - Meowth will send a message @mentioning <pokemonname> and including a Google Maps link
to <location>. If <location> is blank, Meowth will ask for more details.

4. !raid <pokemonname> <location> <time remaining> - Does the same thing as !wild, but also creates a new channel by the name of
#<pokemonname>-<location>. The message also includes the custom emoji for the types that do super effective damage against the 
Pokemon. The created raid channel will automatically delete after the <time remaining> has expired. If <time remaining> is not given or is given in a format other than H:MM, Meowth will assume a two-hour time remaining and ask you to use !timerset.

5. :omw:/:here:/!coming/!here - in a raid channel, the custom emoji for omw and here tell Meowth that you are on your way to or at a raid. !coming and !here do the same things as the custom emoji. If you have multiple trainers with you, type another emoji for each additional trainer. If you are using the commands, use them with !coming <number> to do the same thing. Typing :here: also removes you from the on the way list. The exact phrases are configurable on lines 53-56.

6. :unomw:/:unhere:/!cancel - in a raid channel, these custom emoji tell Meowth to remove you from the on the way or waiting lists. The !cancel command removes you from either list if you are on one. The exact phrases are configurable on lines 53-56.

7. !otw/!waiting - in a raid channel, these commands tell Meowth to list and mention the trainers who said they were on the way
or at a raid. It also includes the total number.

8. !starting - in a raid channel, this command tells Meowth to delete the !waiting list for that raid. Meowth will mention the
users and ask them to respond with :here: if they are still waiting.

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



