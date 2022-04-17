*"on"* or *true* to enable feature, anything else to disable it.
### main
>**activity**: Display what you're doing in Anki as the first field.<br>
>Default values for statuses:<br>
>*Slacking off / Daily reviews / Browsing decks / Adding cards*

>**card_count**: Display cards left for today as the second field.<br>
>*(<card amount\> cards left)*

>**card_count_parens**: (Does nothing if card_count is off) Display parentheses around card count.

>**count_deck**: Display cards left only for the last active deck instead of all of them. No effect if card_count is off.

>**counts**: Set which counts to sum up for the 'cards left' (2nd) field. (["new", "learn", "review"], which are the blue, red, green numbers respectively) Simply remove any that you don't want to be tracked from the list.

>**timer**: Display how long the rich presence has been active.<br>
>*<time in hh:mm:ss or days, etc.\> elapsed*

>**deck_name**: Display deck name next to "Daily reviews" (1st) field when reviewing.<br>
>*Daily reviews \[<deck name\>\]*

>**spotify**: \[LINUX ONLY. Commands used: gdbus, dbus-send\] Display Spotify icon and track name when hovered over it when something is playing.<br>
>*[Example](https://i.imgur.com/IJba0Tj.png)*

>**discord_client**: Use your own Discord Application with custom icons. Currently used icon names are: "anki", "spotify". (745326655395856514)

### statuses
If you do not want your rich presence to be displayed when in a certain state, set it to "", for example: "menu_status": "".<br>
If you want the 1st field to be empty for a certain state, set it to "&nbsp;&nbsp;&nbsp;" (3 spaces), for example "menu_status": "&nbsp;&nbsp;&nbsp;".
>**menu_status**: Text to display when in menu (Slacking off)

>**reviewing_status**: Text to display when reviewing (Daily reviews)

>**browsing_status**: Text to display when browsing decks/cards (Browsing decks)

>**editing_status**: Text to display when editing/adding cards (Adding cards)

>**no_cards_left_txt**: (Only works if card_count is on) Text to display when cards left to study/review is 0 (No cards left)

>**menu_status_no_cards**: (Only works if card_count is on) Text to display when in menu and cards left to study/review is 0 (Feeling good)