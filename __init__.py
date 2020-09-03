"""
	Full disclosure: https://ankiweb.net/shared/info/1133851639 was used as a base.
	I tried using it first but noticed several problems including the deprecated RPC library.
	The main problem was that the addon/repository had not been updated to fix these issues for more than half a year.
	So I decided to (hopefully) fix all the issues and improve the add-on overall as well as keep updating it if anything pops up
"""

from anki.hooks import addHook
from aqt import mw
import time, os
from . import pypresence

# Globals
dueMessage = "   " # initial state value for Rich Presence as it doesn't allow an empty value like ""
skipEdit = 0
connected = False
start_time = round(time.time()) # timer start for Rich Presence
curr_time = start_time - 15 # timer for limiting Rich Presence requests
client_id = '745326655395856514' # the Discord developer application in use. You can change this if you want to use your own with your own assets (like icons, etc.)
rpc = pypresence.presence.Presence(client_id) # init client class

##### PRINTEXCEPTION: Prints exception with separators
def printException(e):
	print("--- EXCEPTION START ---")
	print(e)
	print("--- EXCEPTION END ---")

# attempt first connect
try:
	rpc.connect()
	connected = True
except Exception as e:
	printException(e)

##### GETSPOTIFY: Gets currently active Spotify track info #! LINUX ONLY as far as I know
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
			#! [Spotify (LINUX ONLY)] 1. Uncomment the next 5 lines
			# spotify_info = getSpotify()
			# if spotify_info != "":
			# 	rpc.update(details=detailsMessage, state=dueMessage, large_image="anki", small_image="spotify", small_text=spotify_info, start=start_time)
			# else:
			# 	rpc.update(details=detailsMessage, state=dueMessage, large_image="anki", start=start_time)
			rpc.update(details=detailsMessage, state=dueMessage, large_image="anki", start=start_time) #! [Spotify (LINUX ONLY)] 2. Comment this line if uncommenting the upper 5 lines
			curr_time = round(time.time()) # update timer to wait another 15 seconds before sending another update
	except Exception as e:
		connected = False
		printException(e)

update("Slacking off")

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
		dueMessage = "No cards left"
	elif dueCount == 1:
		dueMessage = "(" + str(dueCount) + " card left)"
	else:
		dueMessage = "(" + str(dueCount) + " cards left)"

##### ONSTATE: Updates with state of anki
# Takes current state and oldState from hook
# If opening browse, skips 'edit' hook
def onState(state, oldState):
	global skipEdit
	dueToday()

	# Check states:
	if state == "deckBrowser":
		update("Slacking off")
	if state == "review":
		update("Daily reviews")
	if state == "browse":
		skipEdit = 1
		update("Browsing decks")
	if state == "edit":
		update("Adding cards")

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
	onState("review", "review")

##### Hooks
addHook("afterStateChange", onState)
addHook("browser.setupMenus", onBrowse)
addHook("setupEditorShortcuts", onEditor)
addHook("showAnswer", onAnswer)