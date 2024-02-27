from riotwatcher import LolWatcher
import regex

def validate_player(player):
	# A Riot ID can contain between 3-16 characters before the # and
	# between 3-5 characters after. These characters can be any
	# Unicode letter. This regular expression checks if the given 
	# name matches this pattern and returns False if not correct.
	if (regex.match("^\p{Letter}{3,16}#\p{Letter}{3,5}$", player)):
		return True
	print("Invalid name, try again.")
	return False

def evaluate_start():
	# A makeshift do/while loop, asks for a Riot ID first to validate,
	# then loops until a valid ID is passed through.
	valid_name = False
	while(not valid_name):
		player_name = input("Enter the player's Riot ID with tag (ex. \"name#tag\"): ")
		valid_name = validate_player(player_name)
	
	print(player_name)

evaluate_start()
