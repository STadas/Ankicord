# Ankicord

An Anki add-on that utilizes the pypresence library and updates your Discord status (Rich Presence) to display your Anki activity.

[![pypresence](https://img.shields.io/badge/using-pypresence-00bb88.svg?style=for-the-badge&logo=discord&logoWidth=20)](https://github.com/qwertyquerty/pypresence)

Full disclosure: https://ankiweb.net/shared/info/1133851639 was used as a base.
I tried using it myself at first but noticed several problems including the deprecated RPC library.
The main problem was that the addon/repository had not been updated to fix these issues for more than half a year.
So I decided to (hopefully) fix all the issues and improve the add-on overall as well as keep updating it if anything pops up

At the moment there is a sort-of-hidden feature of showing the current playing Spotify track as well in the Rich Presence.
It should only work on Linux distros as it utilizes the `gdbus call` and `dbus-send` commands. I've only tested it on my own system (arch btw).
I will probably add an easier way of enabling/disabling this feature soon™️.
**For now, if you want to, you can uncomment/comment certain lines to enable it (I've included some instructions in the comments).**

If anyone has any problems with this being up or just general feedback - `tadz#1030` on Discord.

Example appearance of add-on
![Example appearance of add-on](https://i.imgur.com/RWI7XD4.png)
