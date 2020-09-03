# Ankicord

Full disclosure: https://ankiweb.net/shared/info/1133851639 was used as a base.
I tried using it myself at first but noticed several problems including the deprecated RPC library.
The main problem was that the addon/repository had not been updated to fix these issues for more than half a year.
So I decided to (hopefully) fix all the issues and improve the add-on overall as well as keep updating it if anything pops up

[![pypresence](https://img.shields.io/badge/using-pypresence-00bb88.svg?style=for-the-badge&logo=discord&logoWidth=20)](https://github.com/qwertyquerty/pypresence)

If anyone has any problems with this being up, please contact me on Discord (`tadz#1030`) and we can discuss them.

Moving on, at the moment there is a sort-of-hidden feature of showing the current playing Spotify track as well in the Rich Presence. However as far as I know it should only work on Linux distros as it utilizes the `gdbus call` and `dbus-send` commands. I've also only tested it on my own system (arch btw). I will probably add an easier way of enabling/disabling this feature soon™️ but for now, if you want to, you can uncomment/comment certain lines to enable it (I've included some instructions in the comments).

Thanks for visiting, reading. Again, any feedback, `tadz#1030` for now.

`This will be added to the official Anki 2.1 add-on section as well as the release section here soon™️`