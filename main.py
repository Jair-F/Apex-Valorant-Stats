import time
import urllib3
import json
import os
import sys
import pygamesense

locale:str = None # europe ap br esports eu
api_key:str = None
tagLine:int = None
gameName:str = None
puuid:str = None
SSE3Addr = None # Steelseries 3 Engine Address - (ip:port)

http = urllib3.PoolManager()

"""
	@return Get matchlist for games played by puuid
	https://developer.riotgames.com/apis#val-match-v1/GET_getMatchlist
"""
def getMatchList(puuid:str, locale:str="eu") -> list:
	response = http.request('GET', F'https://{locale}.api.riotgames.com/val/match/v1/matchlists/by-puuid/{puuid}&api_key={api_key}')
	
	print(response.status)
	print(response.headers)
	print(response.data)
	if response.status == 200:
		return response.data.decode()
		#return json.loads(response.data.decode())["history"]

def getRunningMatchId(puuid, locale:str="eu") -> str:
	matchList = getMatchList(puuid, locale)
	for match in matchList:
		matchId = match["matchId"]
		if getMatchRunning(matchId, locale):
			return matchId



"""
	gets the information about a match by id like KDA...
	https://developer.riotgames.com/apis#val-match-v1/GET_getMatch
"""
def getMatchById(matchId:str, puuid:str, locale:str="eu") -> list:
	response = http.request('GET', F'https://{locale}.api.riotgames.com/val/match/v1/matches/{matchId}&api_key={api_key}')
	
	print(response.status)
	print(response.headers)
	print(response.data)

	playerStats = None # stats to return

	if response.status == 200:
		players = json.loads(response.data.decode())["players"]
		for player in players:
			if player["puuid"] == puuid:
				playerStats = player["stats"]

		#return playerStats
		return json.loads(response.data.decode())["matchInfo"]
		# return response.data.decode()

def getMatchRunning(matchId:str, locale:str="eu") -> bool:
	response = http.request('GET', F'https://{locale}.api.riotgames.com/val/match/v1/matches/{matchId}&api_key={api_key}')
	if response.status == 200:
		return json.loads(response.data.decode())["matchInfo"]["isCompleted"]

"""
	@param locale: europe, asia, america, esports
"""
def getAccountPuuid(gameName:str, tagLine:str, locale:str="europe") -> str:
	response  = http.request('GET', F'https://{locale}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{gameName}/{tagLine}?api_key={api_key}')
	if response.status == 200: # Ok
		jsonStr = response.data.decode()
		return json.loads(jsonStr)["puuid"]
	else:
		raise ValueError(F"invalid parameter passed or other unknown error {response.status}, {response.headers}, {response.data}")

def sendPost(addr:tuple, payloadObj:str, application:str):
	app_reg_data = {
		"game": "Apex-Valorant-Stats",
		"game_display_name": 'Apex Valorant Stats',
		"developer": 'developer'
	}

	http.request('POST', url=SSE3Addr + '/game_metadata', json=app_reg_data)

	sendData = {
		"device-type": "screened",
		"game": "MYGAME",
		"event": "MYEVENT",
		"handlers": [{
			"data": {
				"device-type": "screened",
                "mode": "screen",
				"value": 56,
				"frame": {
					"textvalue": "this is some text",
					"numericalvalue": 88
					}
				}
		}]
	}
	http.request('POST', url=SSE3Addr + '/bind_game_event', json=sendData)

if __name__ == "__main__":
	client = pygamesense.SSE3Client("asdf", "asdf", "developer")
	client.registerGame()
	client.bindEvent("try", '')

	for _ in range(10):
		print("sending")
		client.gameEvent("try")
		time.sleep(1)

	sys.exit(0)
	
	while not os.path.exists(F'{os.getenv('PROGRAMDATA')}/SteelSeries/SteelSeries Engine 3/coreProps.json'):
		print("Steelseries Engine not running...", file=sys.stderr)
		time.sleep(1)
	else:
		with open(F'{os.getenv('PROGRAMDATA')}/SteelSeries/SteelSeries Engine 3/coreProps.json') as file:
			SSE3Addr = json.loads(file.read())['address']
			print(SSE3Addr)

	tmp = SSE3Addr + '/bind_game_event'
	print(tmp)
	sendPost(tmp, '', '')
	tmp = SSE3Addr + '/game_event'
	print(tmp)

	for _ in range(10):
		print("sending")
		sendPost(tmp, '', '')
		time.sleep(1)
	
	tmp = SSE3Addr + '/remove_game'
	sendPost(tmp, '', '')
	print(tmp)

	sys.exit(0)

	userCreds = None
	with open("./config.json", 'r') as file:
		UserCreds = json.loads(file.read())
	print(UserCreds)
	puuid = getAccountPuuid(UserCreds["gameName"], UserCreds["tagLine"])
	print(puuid)
	print(getRunningMatchId(puuid))
	# get puuid
	
	
	#resp, content = httplib2.Http().request('https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/BeautyBomb6/6767?api_key=RGAPI-31b4daf6-fdba-4099-81fb-7c6de58e5e62')
	#print(resp)