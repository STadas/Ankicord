"""Main script for Ankicord"""
# pylint: disable=broad-except

import time
import os
import asyncio
from typing import Union
from threading import Thread

from anki.hooks import addHook
from aqt import mw

from .pypresence import presence as pp
from .pypresence import utils as pp_utils


class Ankicord():
    """Ankicord class"""

    def __init__(self):
        cfg = self.__get_resolved_cfg()
        self.main_cfg = cfg['main']
        self.status_cfg = cfg['statuses']

        self.rpc_next_details = "   "
        self.rpc_next_state = "   "
        self.last_deck = None
        self.skip_edit = False

        self.connected = False
        self.start_time = round(time.time())
        self.cfg_disc_id = self.__cfg_val(self.main_cfg, 'discord_client', str)
        self.default_disc_id = "745326655395856514"

        if self.__cfg_val(self.main_cfg, 'activity', bool):
            self.rpc_next_details = self.__cfg_val(self.status_cfg,
                                                   'menu_status',
                                                   str)

    def __get_resolved_cfg(self,
                           cfg: Union[dict, list] = None) -> Union[dict, list]:
        """Translate config (e.g. 'on' -> True)"""
        if cfg is None:
            cfg = mw.addonManager.getConfig(__name__)['defaults']
        table = {
            "on": True,
            "off": False
        }

        config_keys = None
        if isinstance(cfg, dict):
            cfg = dict(cfg)
            config_keys = cfg.keys()
        elif isinstance(cfg, list):
            cfg = list(cfg)
            config_keys = range(len(cfg))

        for k in config_keys:
            if isinstance(cfg[k], (dict, list)):
                cfg[k] = self.__get_resolved_cfg(cfg[k])
            elif isinstance(cfg[k], str) and cfg[k] in table:
                cfg[k] = table[cfg[k]]
        return cfg

    def connect_rpc(self) -> None:
        """Connect to the Discord Rich Presence"""
        try:
            asyncio.set_event_loop(pp.get_event_loop(True))
            self.rpc = pp.Presence(self.cfg_disc_id if self.cfg_disc_id else self.default_disc_id)
            self.rpc.connect()
            self.connected = True
        except Exception as ex:
            print("Couldn't connect to Discord Rich Presence:", ex)

    @staticmethod
    def __get_spotify_info() -> str:
        """Get currently active Spotify track info. LINUX ONLY"""
        try:
            player_status_cmd = "gdbus call --session --dest org.mpris.MediaPlayer2.spotify \
                --object-path /org/mpris/MediaPlayer2 --method org.freedesktop.DBus.Properties.Get \
                org.mpris.MediaPlayer2.Player PlaybackStatus | cut -d \"'\" -f 2"
            track_cmd = "dbus-send --print-reply --dest=org.mpris.MediaPlayer2.spotify \
                /org/mpris/MediaPlayer2 org.freedesktop.DBus.Properties.Get \
                string:org.mpris.MediaPlayer2.Player string:Metadata | sed -n '/title/{n;p}' | \
                cut -d '\"' -f 2"
            artist_cmd = "dbus-send --print-reply --dest=org.mpris.MediaPlayer2.spotify \
                /org/mpris/MediaPlayer2 org.freedesktop.DBus.Properties.Get \
                string:org.mpris.MediaPlayer2.Player string:Metadata | sed -n '/artist/{n;n;p}' | \
                cut -d '\"' -f 2"

            stream = os.popen(player_status_cmd)
            player_status = stream.read().strip()

            if player_status == "Playing":
                stream = os.popen(artist_cmd)
                artist = stream.read().strip()

                stream = os.popen(track_cmd)
                track = stream.read().strip()

                return artist + " ー " + track

            return None
        except Exception as ex:
            print("Couldn't get Spotify info:", ex)
            return None

    def __cfg_val(self, cfg: Union[list, dict], cfg_key: str, cfg_type):
        """Check if key in config exists. If it does, get value,
        if not - None"""
        cfg_val = cfg.get(cfg_key, None)
        if isinstance(cfg_val, cfg_type):
            return cfg_val
        return False if cfg_type == bool else None

    def __rpc_update(self) -> None:
        """Updates the Discord Rich Presence with provided details_message"""
        try:
            if not self.connected:
                self.connect_rpc()

            if len(self.rpc_next_details) < 3 or len(self.rpc_next_state) < 3:
                self.rpc.clear()
                self.start_time = round(time.time())
                return
            
            show_timer = self.__cfg_val(self.main_cfg, 'timer', bool)
            start_time = self.start_time if show_timer else None

            # update Rich Presence
            #! Spotify (LINUX ONLY)
            if self.__cfg_val(self.main_cfg, 'spotify', bool):
                spotify_info = self.__get_spotify_info()
                if spotify_info is not None:
                    self.rpc.update(details=self.rpc_next_details,
                                    state=self.rpc_next_state,
                                    large_image="anki",
                                    small_image="spotify",
                                    small_text=spotify_info,
                                    start=start_time)
                else:
                    self.rpc.update(details=self.rpc_next_details,
                                    state=self.rpc_next_state,
                                    large_image="anki",
                                    start=start_time)
            else:
                self.rpc.update(details=self.rpc_next_details,
                                state=self.rpc_next_state,
                                large_image="anki",
                                start=start_time)
        except Exception as ex:
            self.connected = False
            print("Couldn't update Discord Rich Presence:", ex)

    def __update_rpc_next_state(self) -> None:
        """Calculate cards due"""
        collection = mw.col
        if collection is None:
            return

        due_count = 0
        count_deck = self.__cfg_val(self.main_cfg, 'count_deck', bool)

        if count_deck and self.last_deck is not None:
            node = collection.sched.deck_due_tree(self.last_deck['id'])
        else:
            node = collection.sched.deck_due_tree()

        try:
            if node and node.children:
                counts = {
                    "new":  sum(ch.new_count for ch in node.children),
                    "learn": sum(ch.learn_count for ch in node.children),
                    "review": sum(ch.review_count for ch in node.children),
                }
            elif node:
                counts = {
                    "new":  node.new_count,
                    "learn": node.learn_count,
                    "review": node.review_count,
                }
            else:
                counts = {}

            counts_keys = self.__cfg_val(self.main_cfg, 'counts', list)
            if isinstance(counts_keys, list):
                for key in counts_keys:
                    due_count += counts.get(key, 0)
        except AttributeError as ex:
            print("Deck doesn't have the expected attributes:", ex)

        card_count_parens = self.__cfg_val(self.main_cfg, 'card_count_parens', bool)

        paren_left = ""
        paren_right = ""
        if card_count_parens:
            paren_left = "("
            paren_right = ")"

        if due_count == 0:
            self.rpc_next_state = self.__cfg_val(self.status_cfg,
                                                 'no_cards_left_txt',
                                                 str)
        elif due_count == 1:
            self.rpc_next_state = paren_left + str(due_count) + " card left" + paren_right
        else:
            self.rpc_next_state = paren_left + str(due_count) + " cards left" + paren_right

    def on_state(self, state, _old_state):
        """Take current state and old_state from hook; If browsing, skip
        'edit' hook; Call update"""

        if not self.__cfg_val(self.main_cfg, 'activity', bool):
            self.rpc_next_details = "   "
            return

        if state == "deckBrowser":
            self.last_deck = None
            if self.rpc_next_state != self.__cfg_val(self.status_cfg,
                                                 'no_cards_left_txt',
                                                 str):
                self.rpc_next_details = self.__cfg_val(self.status_cfg,
                                                   'menu_status',
                                                   str)
            else:
                self.rpc_next_details = self.__cfg_val(self.status_cfg,
                                                   'menu_status_no_cards',
                                                   str)

        elif state == "review":
            last_card = mw.reviewer.card
            if last_card is None:
                return

            self.last_deck = mw.col.decks.get(last_card.did)
            reviews_msg = self.__cfg_val(self.status_cfg,
                                         'reviewing_status',
                                         str)
            show_deck = self.__cfg_val(self.main_cfg, 'deck_name', bool)

            if show_deck:
                reviews_msg += " [" + self.last_deck['name'] + "]"
            self.rpc_next_details = reviews_msg

        elif state == "browse":
            self.last_deck = None
            self.skip_edit = True
            self.rpc_next_details = self.__cfg_val(self.status_cfg,
                                                   'browsing_status',
                                                   str)

        elif state == "edit":
            self.last_deck = None
            self.rpc_next_details = self.__cfg_val(self.status_cfg,
                                                   'editing_status',
                                                   str)

        if self.__cfg_val(self.main_cfg, 'card_count', bool):
            self.__update_rpc_next_state()

    def on_browse(self, _x):
        """Handle browse state"""
        self.on_state("browse", "dummy")

    def on_editor(self, _x, _y):
        """Handle editor state if not in browser"""
        if not self.skip_edit:
            self.on_state("edit", "dummy")

        self.skip_edit = False

    def on_answer(self):
        """Handle review state"""
        self.on_state("review", "dummy")

    def job(self):
        """Loop: call rpc update and wait 15 seconds."""
        while True:
            self.__rpc_update()
            time.sleep(15)


ac = Ankicord()
t = Thread(target=ac.job, daemon=True)
t.start()

addHook("afterStateChange", ac.on_state)
addHook("browser.setupMenus", ac.on_browse)
addHook("setupEditorShortcuts", ac.on_editor)
addHook("showAnswer", ac.on_answer)
