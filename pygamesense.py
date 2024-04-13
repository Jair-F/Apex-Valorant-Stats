import os
import sys
import time
import json
import urllib3

class SSE3Client:
	def __init__(self, _game:str, _gameDisplayName:str, _developer:str):
		self.addr:str = None # Steelseries 3 Engine Address - (ip:port)
		self.game:str = _game
		self.gameDisplayName:str = _gameDisplayName
		self.developer:str = _developer
		self.websocket = urllib3.PoolManager()

		while not os.path.exists(F'{os.getenv('PROGRAMDATA')}/SteelSeries/SteelSeries Engine 3/coreProps.json'):
			print("Steelseries Engine not running. - retrying...", file=sys.stderr)
			time.sleep(1)
		else:
			with open(F'{os.getenv('PROGRAMDATA')}/SteelSeries/SteelSeries Engine 3/coreProps.json') as file:
				self.addr = json.loads(file.read())['address']
	
	def registerGame(self):
		metaDataPayload = {
			"game": self.game,
			"game_display_name": self.gameDisplayName,
			"developer": self.developer
		}
		self.websocket.request("POST", url=self.addr + '/game_metadata', json=metaDataPayload)

	"""
	https://github.com/EranVazana/Arctis-OLED-Battery-Indicator/blob/master/GameSenseManager.js

	event = {
		game: this.app_name,
		event: this.percent_event_name,
		value_optional: true,
		handlers: [{
			'device-type': 'screened',
			'mode': 'screen',
			'datas': [
				{
					'lines': [{
						'has-text': true,
						'context-frame-key': 'headline',
						'prefix': headset_name + ' - ',
						'bold': true,
					},
						{
							'has-text': true,
							'context-frame-key': 'subline'
						},
						{
							'has-progress-bar': true,
							'context-frame-key': 'progress'
						}
					]
				}
			]
		}]
	};
	"""
	def bindEvent(self, eventName:str, eventPayload:str):
		event = {
			"game": self.game,
			"event": eventName,
			"value_optional": True,
			"handlers": [{
			"device-type": "screened",
			"mode": "screen",
			"datas": [{
					"lines": [{
						"has-text": True,
						"context-frame-key": "headline",
						"prefix": "headset_name" + " - ",
						"bold": True,
					},
						{
							"has-text": True,
							"context-frame-key": "subline"
						},
						{
							"has-progress-bar": True,
							"context-frame-key": "progress"
						}
					]
				}]
			}]
		}
		self.websocket.request("POST", url=self.addr + '/bind_game_event', json=event)

	def gameEvent(self, eventName:str):
		gameEvent = { 
			"game": self.game,
            "event": eventName,
            "data": {
				"frame": {
					"headline":" headset_status(percent)",
					"subline": "text_to_display",
					"progress": 10
					}
				}
			}
		self.websocket.request("POST", url=self.addr + '/game_event', json=gameEvent)

	# heart beat timeout is by default 15 sec.
	def sendHeartBeat(self):
		heartBeatPayload = {
			"game": self.game
		}
		self.websocket.request("POST", url=self.addr + '/game_heartbeat', json=heartBeatPayload)

	def exitGame(self):
		exit_event = {
			"game": self.game
		}
		self.websocket.request("POST", url=self.addr + '/stop_game', json=exit_event)

	# unregister game
	def endGame(self):
		remove_event = {
			"game": self.game
		}
		self.websocket.request("POST", url=self.addr + '/remove_game', json=remove_event)