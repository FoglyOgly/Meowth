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
1. Use [THIS LINK](https://discordapp.com/oauth2/authorize?client_id=346759953006198784&scope=bot&permissions=268822608) to invite Meowth.   
2. Select your server.
3. In your server, type !configure.
4. Meowth will DM you to setup your server. Be sure to read the prompts properly.
5. That's it! Enjoy!


You can join the Meowth server here for updates, setup help, feature requests, or just to test out the bot before you add it. https://discord.gg/hhVjAN8

If you want to tinker with Meowth yourself, you can still download this repo, make whatever changes you want (or keep everything if you want) and run Meowth locally. The configure process is the same except you'll have to use your own bot token.

## Directions for installing and running the bot on your server:


1. Install Python 3.5.
https://www.python.org/downloads/release/python-350/

2. Install the packages needed to run meowth:

Linux:
```bash
python3 -m pip install -U discord.py pillow requests pytesseract hastebin.py
sudo apt-get install tesseract-ocr tesseract-ocr-eng
```

Windows:
```bash
py -m pip install -U discord.py pillow requests pytesseract hastebin.py
```
Tesseract-OCR has to be installed with a standard binary installer on Windows.
Get the installer [HERE](https://github.com/tesseract-ocr/tesseract/wiki/Downloads)

3. Download the files in this repository. The source code is in meowth.py and bot config is in config.json.

4. Go to https://discordapp.com/developers/applications/me#top and create a new app.

5. Name it and upload the avatar of your choice.

6. Create a bot user for your app and reveal the bot token to copy it.

7. Open config.json in a text editor (a good one to use is Notepad++) and paste the bot token into the value for "bot_token", replacing the "yourtoken" string.

8. Replace the "master" value in config.json with your full discord username with the 4 digits after the hash.

9. Run meowth.py from the command prompt or terminal window. If successful, it should show "Meowth! That's right!".

10. Go back to your Discord application page and copy the Client ID.

11. Go to the following link, replacing <CLIENT_ID> with the Client ID you copied.
`https://discordapp.com/oauth2/authorize?client_id=<CLIENT_ID>&scope=bot&permissions=268822608`

12. Select the server you want to add Meowth to and complete the prompts. If you get to an empty screen and didn't get to see the Google new reCaptcha tickbox, disable your adblocker.

9. The bot should now have sent you DM in Discord. Add the team roles: mystic, instinct and valor. Ensure they're below the bot role in the server role hierarchy.

10. Simply type !configure in your server to start the configuration process.

## Directions for using Meowth:
Note: Avoid punctuation inside commands. The <> in these instructions are there for decoration.

### General Commands:

| Commands | Requirements  | Description |
| -------- |:-------------:| ------------|
| **!help**  | - | Shows commands you can use in that channel, with descriptions. |
| **!team**  | - | Let's users set their team role. |
| **!save**  | *Owner Only* | Saves the save data to file. |
| **!exit**  | *Owner Only* | Saves the save data to file and quits the script. |
| **!outputlog**  | *Server Manager Only* | Uploads the log file to hastebin and replies with the link. |

### Pokemon Notification Commands:

| Commands | Requirements  | Description |
| -------- |:-------------:| ------------|
| **!want**  | - | Adds a Pokemon to your notification roles. |
| **!unwant**  | - | Removes a Pokemon from your notification roles. |
| **!unwant all**  | - | Removes all Pokemon from your notification roles. |
| **!wild**  | *Region Channel* | Reports a wild pokemon, notifying people who want it. |


### Raid Commands:

| Commands | Requirements  | Description |
| -------- |:-------------:| ------------|
| **!raid**  | *Region Channel* | Creates an open raid channel. |
| **!exraid**  | *Region Channel* | Creates an exraid channel. |
| **!invite**  | *Region Channel* | Check attached pass for entry to exraids. |
| **!raidegg**  | *Region Channel* | Creates a raid egg channel. |
| **!raid**  | *Raid Egg Channel* | Converts raid egg to an open raid. |
| **!timer**  | *Raid Channel* | Shows the expiry time for the raid. |
| **!timerset**  | *Raid Channel* | Set the expiry time for the raid. |
| **!location**  | *Raid Channel* | Shows the raid location. |
| **!location new**  | *Raid Channel* | Sets the raid location. |
| **!interested**  | *Raid Channel* | Sets your status for the raid to 'interested'. |
| **!coming**  | *Raid Channel* | Sets your status for the raid to 'coming'. |
| **!here** | *Raid Channel* | Sets your status for the raid to 'here'. |
| **!starting**  | *Raid Channel* | Clears all members with 'here' status, announce raid battle start. |
| **!cancel**  | *Raid Channel* | Cancel your status. |
| **!clearstatus**  | *Server Manager/Raid Channel* | Cancel everyone's status. |
| **!list**  | *Region Channel* | Lists all raids from that region channel. |
| **!list**  | *Raid Channel* | Lists all member status' for the raid. |
| **!list interested** | *Raid Channel* | Lists 'interested' members for the raid. |
| **!list coming**  | *Raid Channel* | Lists 'coming' members for the raid. |
| **!list here** | *Raid Channel* | Lists 'here' members for the raid. |
| **!duplicate** | *Raid Channel* | Reports the raid as a duplicate channel. |

## General notes on Meowth:

Meowth relies completely on users for reports. Meowth was designed as an alternative to Discord bots that use scanners and other illegitimate sources of information about Pokemon Go. As a result, Meowth works only as well as the users who use it. As there are 10+ ways of interacting with Meowth, there can be a bit of a rough learning period, but it quickly becomes worth it.

## Known issues:

Compatibility with Python 3.6 on Mac OS X requires running "Install Certificates.command" in the Python 3.6 folder. Incompatible with discord.py 1.0
