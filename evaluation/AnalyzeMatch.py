from riotwatcher import LolWatcher
from pathlib import Path

# Class "Participant" is used to organize the state of a
# champion in each frame.
class Participant:

	def __init__(self, participant_id, items):
		self.is_user = False
		self.participant_id = participant_id
		self.items = items
		self.champion_stats = {}
		
def get_match_frames(match_timeline, user_puuid):
	"""
	Generate a frame snapshot for a match.

	The match timeline for a match does not accurately represent the state of
	each player in the match at the given frame. Only basic champion and player
	stats/information is listed out at the end of each frame, ability levels, items,
	and more are simply listed in the form of events. Generating a snapshot for
	each frame makes it easier for analysis of a champ at a given point in the match.

	Parameters
	----------
	match_timeline : FIXME
		Timeline of events in a match
	user_puuid : str
		Unique identifier for user to be analyzed in a match
	
	Returns
	-------
	dict of {int : tuple of (Participant, Participant, Participant, Participant, Participant)}
	"""
	pass

def analyze_frames(match_frames):
	"""
	Run analysis of match frames

	After the frame snapshots of a match are generated, analysis can proceed
	by iterating through each frame and calculating the main user's strength
	against their opponents. This analysis is done by using the stats and items
	stored within each ''Participant'' in each frame.

	Parameters
	----------
	match_frames
		Dictionary containing each frame snapshot
	"""
	pass

# Main method for analyzing a match.
def analyze_match(match_id, user_puuid):
	filepath = Path(__file__).parent / "RiotAPIKey.txt"
	with open(filepath, "r") as f:
		api_key = f.read()
	lol_watcher = LolWatcher(api_key)

	"""
	When a match is passed through, the first step is to
	go through each frame and create a snapshot of the
	user and their opponents. This includes a list of items,
	their ability levels, their champion level, and base
	champion stats.
	""" 
	match_timeline = lol_watcher.match.timeline_by_match(region=match_id[:match_id.find("_")], match_id=match_id)

	match_frames = get_match_frames(match_timeline, user_puuid)

	"""
	After all frames in the match are collected, an analysis
	is done. This means going through each frame and calculating
	the damage the user could do to an opponent. Every situation
	would be calculated, including when an item is on cooldown.

	Frame analysis would print the final results and finish the
	script.
	"""
	analyze_frames(match_frames)

