### Changes in 2.14


##### Global Changes

1. Proper changelog added! Changes going forward will be added per patch.
2. config.json now requires USER ID NUMBER instead of name. To get this, right click your name and click Copy ID (developer mode must be enabled in discord)
3. Per-Server Prefixes
Prefixes are now able to be set per-server. Default is still `!`.
The prefix commands are limited to members with the *Manage Server* permission.

`!get prefix` - This lets you see your server's current prefix.

`!set prefix` - This sets the prefix for your server. Examples:
    `!set prefix %` : This sets the server prefix to `%`
    `!set prefix` or `!set prefix clear` : This resets the server prefix to the default.

4. Added About Command

The ``!about`` command will give people info on Meowth, the owner and stats such as the number of servers and members it's servicing and uptime. Optionally, one can use `!uptime` to see that stat alone.

5. New Command Check Handling

Commands won't show outside of usable channel's `!help` output, and won't fail silently when used in the wrong place, instead giving the user a reponse to guide them to the proper place to use it.

6. Configure Bug Fix

The issue where `!configure` couldn't be cancelled at the Pokemon Notification stage should now be fixed.

7. Raid Report Timer Fix

The issue where `!raid`, `!raidegg` timers on initial reports would accept any duration timer, even beyond 60 minutes, no matter the format, should now be fixed.

8. Immortal Expired Channel Bug Fix

Raid channels that recently expired may not have been picked up properly when Meowth was restarted. This should now be resolved.

9. Backend has had a restructure and tidy.

10. `!announce` command has been added. Use this to announce to your server. [2.14.5]

11. Spruced up the `!configure` process. More to come. [2.14.6]

### Changes in 2.13


##### Global Changes

1. Channel cleanup and maintenance has been fixed and Meowth should be able to delete expired channels and maintain active channels easier now.
1. Commands are no longer case sensitive. `!raid`, `!Raid`, `!RAID`, etc. will all work.
1. Shortcut / Command aliases have been added. `!i` for `!interested/!maybe`, `!c` for `!coming`, `!h` for `!here`. `!lists` is back and is an alias for `!list`
1. Minor text fixes

### Changes in 2.12


##### Global Changes

1. Backend has been rewritten to be more stable with the cleanup of channels and other admin/helper functions. Makes life easier for the server owner.
1. `!duplicate` has been rewritten to be more stable and will now ask last reporter for confirmation
1. GymHuntrBot and HuntrBot integration has been rewritten to better handle duplicates and logic on how to deal with raid eggs has been added.
1. Time remaining in `!raid, !raidegg, !timerset` can be input as \<minutes remaining\> (15) OR \<time remaining\> (0:15)
1. Minor text fixes

##### New Commands

1. `!raidegg` - Usage: `!raidegg \<level\> \<location\> \<time until hatch\>` Example: !raidegg 2 downtown 15
  * Creates a temporary channel to coordinate for new egg spawns
  * Use `!raid \<pokemon\>` within raid channel once egg hatches to update to an active raid channel
  * Use `!raid assume \<pokemon\>` within raid channel to have the channel auto-update to a raid channel, currently only supported for Level 5 raid eggs
  * Only `!maybe` will work in raid eggs, unless it is an assumed egg, to avoid people leaving if it isn’t the wanted boss
2. `!exraid` - Usage: `!exraid \<pokemon\> \<location\>` Example: !exraid Mewtwo downtown
  * Creates a temporary channel to coordinate for an EX Raid that lasts for three days
3. `!invite` [Experimental]
A totally automated way for your users to gain access to a previously reported exraid channel. Here's how it works...
  * A user receives an EX Raid invitation.
  * User uploads a screenshot of the invite to the Discord server, with the message `!invite` (the message and attached image must be sent together)
  * Using dark magic developed by Google, Meowth reads the text in the image, searching for the phrase 'EX Raid Battle'
  * If Meowth finds the keyphrase in the image, it responds to the user with a list of previously reported EX Raids and prompts the user to select the matching channel.
  * User selects the channel and Meowth grants read and send messages permissions to that channel. If the user's raid has not been reported, they can simply type 'N' to report their own (they will have to go through the `!invite` process again.
  * If Meowth doesn't find the keyphrase, it’ll say so. If the user sends an erroneous reply, it'll say that too. If no EX raids have been reported, it'll say that too.
4. `!lists` has been renamed to `!list`. `!list` alone will function the same as the old `!lists` in city channels (active raid list) and in raid channels (status lists), but there is now `!list interested, !list coming, !list here` to see those specific lists. `!interest, !otw, !waiting` have been removed.
5. `!location` - Will send raid location if sent within raid channels
  * `!location new \<address\>` will change the raid location. Sending a Google Maps link will also correct the location as before

##### Other Commands - Just for reference

`!want` - A command for declaring a Pokemon species the user wants. Usage: `!want \<pokemon\>`

`!unwant` - A command for removing the !want for a Pokemon. Usage: `!unwant \<pokemon\>`

`!wild` - Report a wild Pokemon spawn location. Usage: `!wild \<pokemon\> \<location\>`

`!raid` - Report an ongoing raid. Usage: `!raid \<pokemon\> \<location\> \<time remaining\>`

`!raidegg` - Report a raid egg. Usage: `!raidegg \<level\> \<location\> \<time until hatch\>`

`!exraid` - Report an upcoming EX raid. Usage: `!exraid \<pokemon\> \<location\>`

`!maybe`- Indicate you are interested in the raid. Usage: `!maybe \<number of accounts *optional*\>`

`!coming` - Indicate you are on the way to a raid. Usage: `!coming \<number of accounts *optional*\>`

`!here` - Indicate you have arrived at the raid. Usage: `!here \<number of accounts *optional*\>`

`!cancel` - Indicate you are no longer interested in a raid and clears whatever your status is. Usage: `!cancel`

`!timerset` - Set the remaining duration on a raid. Usage: `!timerset \<time remaining\>`

`!timer` - Have Meowth resend the expire time message for a raid. Usage: `!timer`

`!starting` - Signal that a raid is starting. Usage: `!starting`

`!location` - Get raid location. Usage: `!location`. Use `!location new \<address\>` to change location

`!duplicate` - A command to report a raid channel as a duplicate. Usage: `!duplicate` (requires three users to remove)

`!invite` - Grants access to EX Raid channels. Usage: `!invite` WITH attached invite screenshot
