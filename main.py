import urllib3
import json

api_key = ""
tagLine = None
gameName = ""
puuid = None

if __name__ == "__main__":
	http = urllib3.PoolManager()
	# get puuid
	response = http.request('GET', F'https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{gameName}/{tagLine}?api_key={api_key}')

	
	puuid = json.loads(response.data.decode())["puuid"]
	print(puuid)

	print(response.data) # Raw data.
	print(response.data.decode('utf-8')) # Text.
	print(response.status) # Status code.
	print(response.headers['Content-Type']) # Content type.
