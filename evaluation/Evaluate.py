from riotwatcher import LolWatcher
import regex
from pathlib import Path
from requests import session
from AnalyzeMatch import analyze_match

def main():

	def validate_name(riot_id):
		"""
		Validates Riot ID.

		A Riot ID consists of a 3-16 character "game name" followed
		by a "#" symbol and a 3-5 character "tag". The game name and
		the tag can be any Unicode letter.

		Validating the ID before using it elsewhere prevents any unwanted
		or unintended issues.

		Parameters
		----------
		riot_id : str
			Riot ID that will be validated
		
		Returns
		-------
		bool
			Returns True or False based on Riot Id validity
		"""
		if (regex.match("^\p{Letter}{3,16}#\p{Letter}{3,5}$", riot_id)):
			return True
		print("Invalid name, try again.")
		return False



	valid_name = False
	while(not valid_name):
		user_name = input("Enter the player's Riot ID with tag (ex. \"name#tag\"): ")
		valid_name = validate_name(user_name)

	# Splits Riot ID for use by API
	user_game_name = user_name[:user_name.find("#")]
	user_tag = user_name[user_name.find("#") + 1:]

	filepath = Path(__file__).parent / "RiotAPIKey.txt"
	with open(filepath, "r") as f:
		api_key = f.read()

	# API call for endpoint unsupported by riotwatcher
	this_session = session()
	user_puuid = this_session.get(
		f"https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{user_game_name}/{user_tag}",
		headers={"X-Riot-Token": api_key}
	).json()["puuid"]

	lol_watcher = LolWatcher(api_key)
	user_region = "NA1"
	
	user_matchlist = lol_watcher.match.matchlist_by_puuid(region=user_region, puuid=user_puuid, count=5) # Use https://static.developer.riotgames.com/docs/lol/queues.json to find queue number

	for user_match in user_matchlist:
		analyze_match(user_match, user_puuid)
	
if __name__ == "__main__":
    main()
