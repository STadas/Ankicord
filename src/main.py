"""Main script for Ankicord"""
# pylint: disable=broad-except

import time
import os
from typing import Union
from threading import Thread, Semaphore

from anki.hooks import addHook
from aqt import mw

from .pypresence import presence as pp


class Ankicord():
    """Ankicord class"""

    def __init__(self):
        config = self.__get_resolved_config()
        self.main_conf = config['main']
        self.status_conf = config['statuses']

        self.rpc_next_details = "   "
        self.rpc_next_state = "   "
        self.deck_name = ""
        self.skip_edit = False

        self.connected = False
        self.rpc = pp.Presence('745326655395856514')
        self.start_time = round(time.time())

        if self.__get_config_val(self.main_conf, 'activity', bool):
            self.rpc_next_details = self.__get_config_val(self.status_conf,
                                                          'menu_status',
                                                          str)
        else:
            self.rpc_next_details = "   "

        self.sem = Semaphore()

    def __get_resolved_config(self,
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
                cfg[k] = self.__get_resolved_config(cfg[k])
            elif isinstance(cfg[k], str) and cfg[k] in table:
                cfg[k] = table[cfg[k]]
        return cfg

    def connect_rpc(self) -> None:
        """Connect to the Discord Rich Presence"""
        try:
            self.rpc.connect()
            self.connected = True
        except Exception as ex:
            print(ex)

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
            print(ex)
            return None

    def __get_config_val(self, cfg: Union[list, dict], cfg_key: str, cfg_type):
        """Check if key in config exists. If it does, get value, if not - None"""
        cfg_val = cfg.get(cfg_key, None)
        if isinstance(cfg_val, cfg_type):
            return cfg_val
        return None

    def __rpc_update(self) -> None:
        """Updates the Discord Rich Presence with provided details_message"""
        self.sem.acquire()
        try:
            if not self.connected:
                self.connect_rpc()

            # update Rich Presence
            #! Spotify (LINUX ONLY)
            if self.__get_config_val(self.main_conf, 'spotify', bool):
                spotify_info = self.__get_spotify_info()
                if spotify_info is not None:
                    self.rpc.update(details=self.rpc_next_details,
                                    state=self.rpc_next_state,
                                    large_image="anki",
                                    small_image="spotify",
                                    small_text=spotify_info,
                                    start=self.start_time)
                else:
                    self.rpc.update(details=self.rpc_next_details,
                                    state=self.rpc_next_state,
                                    large_image="anki",
                                    start=self.start_time)
            else:
                self.rpc.update(details=self.rpc_next_details,
                                state=self.rpc_next_state,
                                large_image="anki",
                                start=self.start_time)
        except Exception as ex:
            self.connected = False
            print(ex)
        self.sem.release()

    def __update_rpc_next_state(self) -> None:
        """Calculate reviews due"""
        due_count = 0

        for i in mw.col.sched.deckDueTree():  # TODO: deprecated
            _name, _did, due, lrn, new, _children = i
            due_count += due + lrn + new

        # Correct for single or no cards
        if due_count == 0:
            self.rpc_next_state = self.__get_config_val(self.status_conf,
                                                        'no_cards_left_txt',
                                                        str)
        elif due_count == 1:
            self.rpc_next_state = "(" + str(due_count) + " card left)"
        else:
            self.rpc_next_state = "(" + str(due_count) + " cards left)"

    def on_state(self, state, _old_state):
        """Take current state and old_state from hook; If browsing, skip
        'edit' hook; Call update"""
        self.sem.acquire()
        if self.__get_config_val(self.main_conf, 'card_count', bool):
            self.__update_rpc_next_state()

        if not self.__get_config_val(self.main_conf, 'activity', bool):
            self.rpc_next_details = "   "
            return

        if state == "deckBrowser":
            self.rpc_next_details = self.__get_config_val(self.status_conf,
                                                          'menu_status',
                                                          str)

        elif state == "review":
            reviews_msg = self.__get_config_val(self.status_conf,
                                                'reviewing_status',
                                                str)
            show_deck = self.__get_config_val(self.main_conf,
                                              'deck_name',
                                              bool)
            if show_deck and self.deck_name != "":
                reviews_msg += " [" + self.deck_name + "]"
            self.rpc_next_details = reviews_msg

        elif state == "browse":
            self.skip_edit = True
            self.rpc_next_details = self.__get_config_val(self.status_conf,
                                                          'browsing_status',
                                                          str)

        elif state == "edit":
            self.rpc_next_details = self.__get_config_val(self.status_conf,
                                                          'editing_status',
                                                          str)
        self.sem.release()

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
        self.deck_name = str(mw.col.decks.get(mw.reviewer.card.did)['name'])
        self.on_state("review", "dummy")

    def job(self):
        """Loop: call rpc update and wait 15 seconds."""
        while True:
            self.__rpc_update()
            time.sleep(15)


ac = Ankicord()
ac.connect_rpc()
t = Thread(target=ac.job, daemon=True)
t.start()

addHook("afterStateChange", ac.on_state)
addHook("browser.setupMenus", ac.on_browse)
addHook("setupEditorShortcuts", ac.on_editor)
addHook("showAnswer", ac.on_answer)
