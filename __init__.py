"""
	Full disclosure: https://ankiweb.net/shared/info/1133851639 was used as a base.
	I tried using it myself at first but noticed several problems including the deprecated RPC library.
	The main problem was that the add-on/repository had not been updated to fix these issues for more than half a year.
	So I decided to (hopefully) fix all the issues and improve the add-on overall as well as keep updating it if anything pops up
"""

from anki.hooks import addHook
from aqt import mw
from aqt.utils import showInfo
import time, os, json
from . import pypresence

# Globals
dueMessage = "   " # initial state value for Rich Presence as it doesn't allow an empty value like ""
deck_name = ""
skipEdit = 0
connected = False
start_time = round(time.time()) # timer start for Rich Presence
curr_time = round(time.time()) - 15 # timer for limiting Rich Presence requests
client_id = '745326655395856514' # the Discord developer application in use. You can change this if you want to use your own with your own assets (like icons, etc.)
rpc = pypresence.presence.Presence(client_id) # init client class

# set default config
default_config = {
	"main": {
		"activity": "on",
		"card_count": "on",
		"deck_name": "on",
		"timer": "on",
		"spotify": "off"
	},
	"statuses": {
		"menu_status": "Slacking off",
		"reviewing_status": "Daily reviews",
		"browsing_status": "Browsing decks",
		"editing_status": "Adding cards",
		"no_cards_left_txt": "No cards left"
	}
}

# get meta config
config = mw.addonManager.getConfig(__name__)['defaults']

def applyConfig(conf_json):
	global activity_on
	global card_count_on
	global show_deck_on
	global spotify_on
	global timer_on

	global menu_status
	global reviewing_status
	global browsing_status
	global editing_status
	global no_cards_left_txt

	main_conf = conf_json ['main']
	activity_on = main_conf['activity'] == "on"
	card_count_on = main_conf['card_count'] == "on"
	show_deck_on = main_conf['deck_name'] == "on"
	spotify_on = main_conf['spotify'] == "on"
	timer_on = main_conf['timer'] == "on"

	status_conf = conf_json['statuses']
	menu_status = str(status_conf['menu_status'])
	reviewing_status = str(status_conf['reviewing_status'])
	browsing_status = str(status_conf['browsing_status'])
	editing_status = str(status_conf['editing_status'])
	no_cards_left_txt = str(status_conf['no_cards_left_txt'])

try:
	# try to use meta config
	applyConfig(config)
except:
	# use defaults if failed
	applyConfig(default_config)
	showInfo(text="The default config.json for Ankicord has been updated or there is an error in your custom config!\n\nIt is recommended to go to Tools>Add-ons>Ankicord>Config and restore defaults or find any mistakes in your custom config if you have made/plan to make edits (and if you don't want this infobox popping up).\n\nFor now, the default config will be used.")

if not timer_on: #! config setting
	start_time = None

# attempt first connect
try:
	rpc.connect()
	connected = True
except Exception as e:
	print(e)

##### GETSPOTIFY: Gets currently active Spotify track info #! LINUX ONLY
def getSpotify():
	try:
		player_status_command = "gdbus call --session --dest org.mpris.MediaPlayer2.spotify --object-path /org/mpris/MediaPlayer2 --method org.freedesktop.DBus.Properties.Get org.mpris.MediaPlayer2.Player PlaybackStatus | cut -d \"'\" -f 2"
		track_command = "dbus-send --print-reply --dest=org.mpris.MediaPlayer2.spotify /org/mpris/MediaPlayer2 org.freedesktop.DBus.Properties.Get string:org.mpris.MediaPlayer2.Player string:Metadata | sed -n '/title/{n;p}' | cut -d '\"' -f 2"
		artist_command = "dbus-send --print-reply --dest=org.mpris.MediaPlayer2.spotify /org/mpris/MediaPlayer2 org.freedesktop.DBus.Properties.Get string:org.mpris.MediaPlayer2.Player string:Metadata | sed -n '/artist/{n;n;p}' | cut -d '\"' -f 2"
		
		stream = os.popen(player_status_command)
		player_status = stream.read().strip()

		if player_status == "Playing":
			stream = os.popen(artist_command)
			spotify_artist = stream.read().strip()

			stream = os.popen(track_command)
			spotify_track = stream.read().strip()

			return spotify_artist + " ー " + spotify_track
		else:
			return ""
	except Exception as e:
		print(e)
		return ""

##### UPDATE: Updates the Discord Rich Presence
# Takes details message to display in status
def update(detailsMessage):
	global connected
	global curr_time

	try:
		if not connected:
			rpc.connect()
			connected = True

		# update Rich Presence
		if round(time.time()) - 15 > curr_time:
			#! Spotify (LINUX ONLY)
			if spotify_on: #! config setting
				spotify_info = getSpotify()
				if spotify_info != "":
					rpc.update(details=detailsMessage, state=dueMessage, large_image="anki", small_image="spotify", small_text=spotify_info, start=start_time)
				else:
					rpc.update(details=detailsMessage, state=dueMessage, large_image="anki", start=start_time)
			else:
				rpc.update(details=detailsMessage, state=dueMessage, large_image="anki", start=start_time)
			curr_time = round(time.time()) # update timer to wait another 15 seconds before sending another update
	except Exception as e:
		connected = False
		print(e)

if activity_on: #! config setting
	update(menu_status) #! config status
else:
	update("   ")

##### DUETODAY: Calculates reviews due
# Stored in global variable 'dueMessage'
# Don't call before Anki has loaded
def dueToday():
	# Globals and reset variables
	global dueMessage
	dueCount = 0

	# Loop through deckDueTree to find cards due
	for i in mw.col.sched.deckDueTree(): # go through each deck
		name, did, due, lrn, new, children = i
		dueCount += due + lrn + new # sum up today's cards

	# Correct for single or no cards
	if dueCount == 0:
		dueMessage = no_cards_left_txt #! config status
	elif dueCount == 1:
		dueMessage = "(" + str(dueCount) + " card left)"
	else:
		dueMessage = "(" + str(dueCount) + " cards left)"

##### ONSTATE: Updates with state of anki
# Takes current state and oldState from hook
# If opening browse, skips 'edit' hook
def onState(state, oldState):
	global skipEdit

	if card_count_on: #! config setting
		dueToday()

	if not activity_on: #! config setting
		update("   ")
		return

	# Check states:
	if state == "deckBrowser":
		update(menu_status) #! config status
	elif state == "review":
		reviews_msg = reviewing_status #! config status
		if show_deck_on and deck_name != "": #! config setting
			reviews_msg += " [" + deck_name + "]"
		update(reviews_msg)
	elif state == "browse":
		skipEdit = 1
		update(browsing_status) #! config status
	elif state == "edit":
		update(editing_status) #! config status

##### Simulated states
## onBrowse --> when loading browser menu
def onBrowse(x):
	onState("browse", "dummy")

## onEdit --> when loading editor
def onEditor(x, y):
	global skipEdit

	# if skipEdit 1, opening browse
	if skipEdit == 0:
		onState("edit", "dummy")
	# reset
	skipEdit = 0

## onAnswer --> when answering card (update cards left)
def onAnswer():
	global deck_name
	deck_name = str(mw.col.decks.get(mw.reviewer.card.did)['name'])
	onState("review", "dummy")

##### Hooks
addHook("afterStateChange", onState)
addHook("browser.setupMenus", onBrowse)
addHook("setupEditorShortcuts", onEditor)
addHook("showAnswer", onAnswer)