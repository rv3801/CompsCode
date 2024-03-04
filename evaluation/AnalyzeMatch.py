from riotwatcher import LolWatcher
from pathlib import Path

# Class "Participant" is used to organize the state of a
# champion in each frame.
class Participant:
	"""
	Class for a Participant in a match.

	Attributes
	----------
	participant_id : int
		Participant ID of the participant
	items : list of int
		A list of items. Length could range from 0 to 7
	skill_levels : list of int
		List of skill levels. Length of 4, values range from 0 to 6
	champion_stats : dict of {str : int}
		Key is the name of the stat, int is the value.
	champion_level : int
		Level of the champion.
	"""

	def __init__(self, participant_id, items, skill_levels, champion_stats, champion_level):
		self.participant_id = participant_id
		self.items = items
		self.skill_levels = skill_levels 
		self.champion_stats = champion_stats
		self.champion_level = champion_level
	
	def __str__(self):
		participant_string = f"Participant ID:\n\t{self.participant_id}\n"
		item_string = f"Participant Items:\n\t{self.items}\n"
		skills_string = f"Participant Skills:\n\t{self.skill_levels}\n"
		stats_string = f"Participant Champ Stats:\n\t{self.champion_stats}\n"
		level_string = f"Participant Champ Level:\n\t{self.champion_level}\n"
		return participant_string + item_string + skills_string + stats_string + level_string
		
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
	match_timeline : dict
		Timeline of events in a match
	user_puuid : str
		Unique identifier for user to be analyzed in a match
	
	Returns
	-------
	dict of {int : tuple of (Participant, Participant, Participant, Participant, Participant)}
	"""


	def loop_frames(frame_participants):
		"""
		Loop through 'match_timeline' events to generate a list of timestamps,
		and dictionaries of events, champion stats, and champion levels for
		every given timestamp.

		"""
		frame_timestamps = [] # [timestamp, ...]
		participant_events = {x:[] for x in frame_participants} # {participant_id: [event, ...], ... }
		participant_stats = {} # {timestamp: {participant_id: {champion_stats}, ... } }
		participant_levels = {} # {timestamp: {participant_id: champion_level, ... } }

		for frame in match_timeline["info"]["frames"]:
			frame_timestamps.append(frame["timestamp"])

			for event in frame["events"]:
				valid_event = ("ITEM_PURCHASED", "ITEM_DESTROYED", "ITEM_UNDO", "SKILL_LEVEL_UP")
				if (event["type"] in valid_event) and (event["participantId"] in frame_participants):
					participant_events[event["participantId"]].append(event)

			frame_participant_stats = {participant_id: frame["participantFrames"][str(participant_id)]["championStats"] for participant_id in frame_participants}
			participant_stats[frame["timestamp"]] = frame_participant_stats

			frame_participant_levels = {participant_id: frame["participantFrames"][str(participant_id)]["level"] for participant_id in frame_participants}
			participant_levels[frame["timestamp"]] = frame_participant_levels
		
		return frame_timestamps, participant_events, participant_stats, participant_levels
	
	def organize_match(frame_participants, frame_timestamps, participant_events, participant_stats, participant_levels):
		"""
		Generate a dictionary (key = timestamp) with a value of a tuple
		containing 5 Participant objects for each frame participant.
		"""

		def loop_events():
			"""
			Loop through each participant's event list and organize items
			and skill levels based on the timestamp. Returns two dictionaries
			containing the items and skill_levels respectively for each participant
			in the given frame timestamp.
			"""

			participant_items = {timestamp: {} for timestamp in frame_timestamps}
			participant_skill_levels = {timestamp: {} for timestamp in frame_timestamps}

			for participant in frame_participants:
				current_items = []
				current_skills = [0, 0, 0, 0]

				current_timestamp_index = 0

				current_event_index = 0 # To be used with ITEM_UNDO case
				for event in participant_events[participant]:

					if event["timestamp"] > frame_timestamps[current_timestamp_index]:
						insert_items = []
						for item in current_items:
							insert_items.insert(len(insert_items), item)
						participant_items[frame_timestamps[current_timestamp_index]][participant] = insert_items

						insert_skills = [current_skills[0], current_skills[1], current_skills[2], current_skills[3]]
						participant_skill_levels[frame_timestamps[current_timestamp_index]][participant] = insert_skills

						current_timestamp_index += 1

					item_events = ("ITEM_PURCHASED", "ITEM_DESTROYED", "ITEM_UNDO")
					if event["type"] in item_events:

						match event["type"]:

							case "ITEM_PURCHASED":
								current_items.insert(len(current_items), event["itemId"])

							case "ITEM_DESTROYED":
								non_purchase_items = (0, 2010, 2051,  2052, 2138, 2139, 2140, 2150, 2151, 2152, 2422, 3340, 3513)

								if event["itemId"] in non_purchase_items:
									pass
								else:
									current_items.remove(event["itemId"])

							case "ITEM_UNDO":
								if event["beforeId"] == 0: # Undo a sell
									current_items.insert(len(current_items), event["afterId"])
								else: # Undo a purchase
									undo_item_id = event["beforeId"]
									event_search_index = current_event_index - 1
									

									item_match = False
									while(not item_match):
										current_search_event = participant_events[participant][event_search_index]
										if (current_search_event["type"] == "ITEM_PURCHASED") and (current_search_event["itemId"] == undo_item_id):
											item_match = True
											item_purchase_timestamp = current_search_event["timestamp"]
										event_search_index -= 1
									
									destroyed_items = []
									final_destroyed_item = False
									if event_search_index >= 0:
										while((not final_destroyed_item) and (event_search_index >= 0)):
											current_destroyed_event = participant_events[participant][event_search_index]
											if (current_destroyed_event["type"] == "ITEM_DESTROYED") and (current_destroyed_event["timestamp"] == item_purchase_timestamp):
												destroyed_items.insert(len(destroyed_items), current_destroyed_event["itemId"])
											elif current_destroyed_event["timestamp"] < item_purchase_timestamp:
												final_destroyed_item = True
											event_search_index -= 1
									
									current_items.remove(undo_item_id)

									for item in destroyed_items:
										current_items.insert(len(current_items), item)

					elif event["type"] == "SKILL_LEVEL_UP":
						current_skills[event["skillSlot"] - 1] += 1
					
					if current_event_index == len(participant_events[participant]) - 1:
						for timestamp in frame_timestamps[current_timestamp_index:]:
							participant_skill_levels[timestamp][participant] = insert_skills
							participant_items[timestamp][participant] = insert_items
					
					current_event_index += 1

			return participant_items, participant_skill_levels
		

		participant_items, participant_skill_levels = loop_events()

		# return participant_items, participant_skill_levels
	
		frames_dict = {}
		for timestamp in frame_timestamps:
			# Loop to create Participant objects in a tuple and insert into dict by timestamp
			frames_dict[timestamp] = tuple([
				Participant(
					participant,
					participant_items[timestamp][participant],
					participant_skill_levels[timestamp][participant],
					participant_stats[timestamp][participant],
					participant_levels[timestamp][participant]
					) for participant in frame_participants
				])
	
		return frames_dict # Is supposed to return a dict {int: tuple of Participant objects}

	for participant in match_timeline["info"]["participants"]:
		if participant["puuid"] == user_puuid:
			user_participant_id = participant["participantId"]
			break
	
	if user_participant_id <=5:
		frame_participants = (user_participant_id, 6, 7, 8, 9, 10)
	else:
		frame_participants = (user_participant_id, 1, 2, 3, 4, 5)
	
		
	frame_timestamps, participant_events, participant_stats, participant_levels = loop_frames(frame_participants)

	# Testing Section
	#================
	# participant_items, participant_skill_levels = organize_match(frame_participants, frame_timestamps, participant_events, participant_stats, participant_levels)
	
	# return frame_timestamps, participant_events, participant_stats, participant_levels, participant_items, participant_skill_levels
	
	
	# Section for looping frames and organizing data
	#===============================================

	match_frames = organize_match(frame_participants, frame_timestamps, participant_events, participant_stats, participant_levels)

	return match_frames
	

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
	"""
	Calculate user strength in given match at one-minute intervals.

	Match timelines given by the Riot API only gives a vague
	summary of events and stats in a game without the specifics on
	what a player's strength was like at a given frame. This method
	aims to fix this by looping through every frame and creating a
	snapshot of the main user (player to be analyzed) and their
	five opponents.

	Parameters
	----------
	match_id : str
		globally unique match identifier
	user_puuid : str
		globally unique player identifier
	"""
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

	match_frames_keys = tuple(match_frames.keys())
	for key in match_frames_keys:
		print(f"Timestamp: {key}")
		for participant in match_frames[key]:
			print(participant)
	# print(match_frames)

	"""
	After all frames in the match are collected, an analysis
	is done. This means going through each frame and calculating
	the damage the user could do to an opponent. Every situation
	would be calculated, including when an item is on cooldown.

	Frame analysis would print the final results and finish the
	script.
	"""
	analyze_frames(match_frames)

