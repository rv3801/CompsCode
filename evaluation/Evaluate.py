from riotwatcher import LolWatcher
import regex
from pathlib import Path
import urllib.parse
from requests import session
from AnalyzeMatch import analyze_match

def main():
	valid_name = False
	while(not valid_name):
		user_riot_id = input("Enter the player's Riot ID with tag (ex. \"name#tag\"): ")
		valid_name = (regex.match(r"[\p{Letter}\s0-9]{3,16}#[\p{Letter}0-9]{3,5}", user_riot_id))

	# Splits Riot ID for use by API
	user_game_name = user_riot_id[:user_riot_id.find("#")]
	user_tag = user_riot_id[user_riot_id.find("#") + 1:]

	filepath = Path(__file__).parent / "RiotAPIKey.txt"
	with open(filepath, "r") as f:
		api_key = f.read()

	# API call for endpoint unsupported by riotwatcher
	encode_user_game_name = urllib.parse.quote(user_game_name)
	encode_user_tag = urllib.parse.quote(user_tag)
	this_session = session()
	user_puuid = this_session.get(
		f"https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{encode_user_game_name}/{encode_user_tag}",
		headers={"X-Riot-Token": api_key}
	).json()["puuid"]

	lol_watcher = LolWatcher(api_key)
	user_region = "NA1"
	
	user_matchlist = lol_watcher.match.matchlist_by_puuid(region=user_region, puuid=user_puuid, count=10) # Use https://static.developer.riotgames.com/docs/lol/queues.json to find queue number

	for user_match in user_matchlist:
		analyze_match(user_match, user_puuid)
	
if __name__ == "__main__":
    main()
