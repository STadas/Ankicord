*"on"* or *true* to enable feature, anything else to disable it.
### main
>**activity**: Display what you're doing in Anki as the first field.<br>
>Default values for statuses:<br>
>*Slacking off / Daily reviews / Browsing decks / Adding cards*

>**card_count**: Display cards left for today as the second field.<br>
>*(<card amount\> cards left)*

>**count_deck**: Display cards left only for the last active deck instead of all of them. No effect if card_count is off.

>**counts**: Set which counts to sum up for the 'cards left' status. (["new", "learn", "review"], which are the blue, red, green numbers respectively)

>**timer**: Display time elapsed after Anki has been launched<br>
>*<time in hh:mm:ss or days, etc.\> elapsed*

>**deck_name**: Display deck name next to "Daily reviews" when reviewing<br>
>*Daily reviews \[<deck name\>\]*

>**spotify**: \[LINUX ONLY. Commands used: gdbus, dbus-send\] Display Spotify icon and track name when hovered over it when something is playing.<br>
>*[Example](https://i.imgur.com/IJba0Tj.png)*

>**discord_client**: Use your own Discord Application with custom icons. Currently used icon names are: "anki", "spotify". (745326655395856514)

### statuses
>**menu_status**: Text to display when in menu (Slacking off)

>**reviewing_status**: Text to display when reviewing (Daily reviews)

>**browsing_status**: Text to display when browsing decks/cards (Browsing decks)

>**editing_status**: Text to display when editing/adding cards (Adding cards)

>**no_cards_left_txt**: (Only works if card_count is on) Text to display when cards left to study/review is 0 (No cards left)