**Meowth! That's right! I've been updated!**  

__**Changes:**__  
  
**Configure Update**  
Configure has been put into embed messages to help with readability and presentation.

**Prefix Update**  
Prefixes should allow multiple characters now. This is still in testing, so be sure to give feedback if you're using it.

**Region Output on Wrong Channel Fix**  
Servers with a large list of region channels wern't into the 'command not in region channel' error.
Now if you have more than 10 region channels, it'll give a standard message, no super long lists.

**Added Announcement Command**   
Server Admins can now use the command **!announce**  
It'll output provided content into an announcement similar to this one.  
This can be handy for posting updates in a nice format. It's also a way to have in-line hyperlinks.  

To use it, you can either add the message in-line like:  
```
!announce This is the message output. It'll respect formatting like **bold** and
new lines.
You can make links like [this one that goes to our github](https://github.com/FoglyOgly/Meowth/)
```
or use `!announce` on it's own, and it'll wait for to send the content in the next message.  

Give it a go and let us know what you think.  

**General Backend Cleanup**  
The usual business here.

__**Coming Major Update**__  
We have an update coming up that is on the more major side of things.

Because it's adjusting the way raid data is saved, there's the possibility of existing raids becoming unresponsive after the update, as the bot may not be able to reference them anymore and backend checks will likely show the old raid channels as invalid.

We haven't got a set time for the update to be rolled out, but we will provide another announcement at least 24 hrs in advanced to provide the date and time.

Be sure to pop into our server to give feedback on the updates we've been rolling out, and to suggest any of your own ideas.

**Reconfigure shouldn't be necessary for this update.**
