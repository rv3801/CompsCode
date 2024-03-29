from riotwatcher import LolWatcher
import regex
from pathlib import Path
import urllib.parse
from requests import session
from LoLMatch import LoLMatch
from PlotSummary import plot_summaries
import json

def main():
	
	"""
	Code below is to be used with a Riot API Key.

	If you don't have one, skip to the next section.
	
	If you do have one, make sure it is pasted in a 
	text file located within the "evaluation" folder.
	"""

	# valid_name = False
	# while(not valid_name):
	# 	user_riot_id = input("Enter the player's Riot ID with tag (ex. \"name#tag\"): ")
	# 	valid_name = (regex.match(r"[\p{Letter}\s0-9]{3,16}#[\p{Letter}0-9]{3,5}", user_riot_id))

	# # Splits Riot ID for use by API
	# user_game_name = user_riot_id[:user_riot_id.find("#")]
	# user_tag = user_riot_id[user_riot_id.find("#") + 1:]

	# filepath = Path(__file__).parent / "RiotAPIKey.txt"
	# with open(filepath, "r") as f:
	# 	api_key = f.read()

	# # API call for endpoint unsupported by riotwatcher
	# encode_user_game_name = urllib.parse.quote(user_game_name)
	# encode_user_tag = urllib.parse.quote(user_tag)
	# this_session = session()
	# user_puuid = this_session.get(
	# 	f"https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{encode_user_game_name}/{encode_user_tag}",
	# 	headers={"X-Riot-Token": api_key}
	# ).json()["puuid"]

	# lol_watcher = LolWatcher(api_key)
	# user_region = "NA1"
	
	# user_matchlist = lol_watcher.match.matchlist_by_puuid(region=user_region, puuid=user_puuid, count=1) # Use https://static.developer.riotgames.com/docs/lol/queues.json to find queue number
	# # user_matchlist = [] # use this when you have a list of match ids you'd prefer to use 

	# for user_match in user_matchlist:
	# 	this_match = LoLMatch(user_match)
	# 	this_match.match_summary()
	# 	this_match.participants_summary()
	# 	this_match_damage_summary = this_match.calculate_participant_damage(user_puuid)
	


	"""
	Code below plots the provided damage summaries into the
	same graphs used in the paper.
	"""

	# Graves match 1 and 2
	filepath = Path(__file__).parent / "match_damage_summaries/NA1_4948110139.json"
	with open(filepath, "r") as f:
		match_1_1 = json.load(f)
	
	filepath = Path(__file__).parent / "match_damage_summaries/NA1_4948918567.json"
	with open(filepath, "r") as f:
		match_1_2 = json.load(f)
	
	plot_summaries(match_1_1, match_1_2) # Use 2000 for y axis when prompted
	


	#Xin Zhao match 1 and 2
	filepath = Path(__file__).parent / "match_damage_summaries/NA1_4948094107.json"
	with open(filepath, "r") as f:
		match_2_1 = json.load(f)
	
	filepath = Path(__file__).parent / "match_damage_summaries/NA1_4948906044.json"
	with open(filepath, "r") as f:
		match_2_2 = json.load(f)
	
	plot_summaries(match_2_1, match_2_2) # Use 1000 for y axis when prompted



	#Twisted Fate match 1 and 2
	filepath = Path(__file__).parent / "match_damage_summaries/NA1_4946973385.json"
	with open(filepath, "r") as f:
		match_3_1 = json.load(f)
	
	filepath = Path(__file__).parent / "match_damage_summaries/NA1_4950877410.json"
	with open(filepath, "r") as f:
		match_3_2 = json.load(f)
	
	plot_summaries(match_3_1, match_3_2) # Use 1500 for y axis when prompted
	
if __name__ == "__main__":
    main()
