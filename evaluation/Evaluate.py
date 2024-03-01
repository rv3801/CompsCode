from riotwatcher import LolWatcher
import regex
from pathlib import Path
from requests import session
import json
from AnalyzeMatch import analyze_match

def validate_name(name):
	# A Riot ID can contain between 3-16 characters before the # and
	# between 3-5 characters after. These characters can be any
	# Unicode letter. This regular expression checks if the given 
	# name matches this pattern and returns False if not correct.
	if (regex.match("^\p{Letter}{3,16}#\p{Letter}{3,5}$", name)):
		return True
	print("Invalid name, try again.")
	return False

def evaluate_start():
	# A makeshift do/while loop, asks for a Riot ID first to validate,
	# then loops until a valid ID is passed through.
	valid_name = False
	while(not valid_name):
		user_name = input("Enter the player's Riot ID with tag (ex. \"name#tag\"): ")
		valid_name = validate_name(user_name)

	# After the name is verified, start the evaluation process by getting
	# a list of the player's TODO most recent games.
	user_game_name = user_name[:user_name.find("#")]
	user_tag = user_name[user_name.find("#") + 1:]

	# Uses Path() to avoid working directory issues with finding the .txt file
	filepath = Path(__file__).parent / "RiotAPIKey.txt"
	with open(filepath, "r") as f:
		api_key = f.read()

	# API call for unsupported endpoint
	this_session = session()
	user_puuid = this_session.get(
		f"https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{user_game_name}/{user_tag}",
		headers={"X-Riot-Token": api_key}
	).json()["puuid"]

	lol_watcher = LolWatcher(api_key)
	user_region = "NA1"
	# Use https://static.developer.riotgames.com/docs/lol/queues.json to find queue number
	user_matchlist = lol_watcher.match.matchlist_by_puuid(region=user_region, puuid=user_puuid, count=5)

	for user_match in user_matchlist:
		analyze_match(user_match, user_puuid)
	
evaluate_start()
