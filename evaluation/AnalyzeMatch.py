from riotwatcher import LolWatcher
from pathlib import Path

# Class "Participant" is used by the get_champ_states method to keep
# an object of each participant containing their items and champion stats
class Participant:

	def __init__(self, participant_id, items):
		self.participant_id = participant_id
		self.items = items
		self.champion_stats = {}

# Finds the participant ID of the user and opponents.
def get_participants(participants, user_puuid):
	for par in participants:
		if par["puuid"] == user_puuid:
			user_par_id = par["participantId"]
			break
	
	if (user_par_id >= 6):
		new_participants = (user_par_id, 1, 2, 3, 4, 5)
	else:
		new_participants = (user_par_id, 6, 7, 8, 9, 10)
	return new_participants

def undo_items(events, undo_item_id, undo_participant):
	print("Undo Items called")
	destroyed_items = []
	purchased_items = []
	undo_item_timestamp = 0
	print("--Full event loop:")
	for event in events:
		# print(event["type"])
		# print(event["timestamp"])
		match event["type"]:
			case "ITEM_DESTROYED":
				print("\tItem destroyed")
				destroyed_items.insert(0, event)
				print(len(destroyed_items))
			case "ITEM_PURCHASED":
				print("\tItem purchased")
				purchased_items.insert(0, event)
				print(len(purchased_items))
			case "ITEM_UNDO":
				if ((event["beforeId"] == undo_item_id) and (event["participantId"] == undo_participant)):
					break
				else:
					pass
			case _:
				pass
	print(f"Full event loop over.")
	
	undo_timestamp = 0 # Timestamp for the undo item when it was purchased
	for event in purchased_items:
		if (event["itemId"] == undo_item_id):
			undo_timestamp = event["timestamp"]
			break

	print(f"Undo timestamp: {undo_timestamp}")
	print(f"Undo item: {undo_item_id}")
	
	return_items = []
	for event in destroyed_items:
		print("--Destroyed item element:")
		print(event["timestamp"])
		if (event["timestamp"] == undo_timestamp):
			return_items.insert(0, event["itemId"])
			print("Item inserted for return")
		elif (event["timestamp"] < undo_timestamp):
			print(f"--End (after {undo_timestamp})")
			print(event["timestamp"])
			break
		else:
			pass
	
	return return_items
	
def get_participant_items(match_participants, events, start_items, past_events):
	participants = []
	par_index = {}
	for participant in match_participants:
		new_participant = Participant(participant, start_items[participant])
		participants.append(new_participant)
		index = participants.index(new_participant)
		par_index[participant] = index
	tuple_participants = tuple(participants)

	for event in events:
		past_events.insert(len(past_events), event)
		if ("ITEM" in event["type"]):
			if (event["participantId"] in match_participants):
				event_time = event["timestamp"]
				print(f"Timestamp: {event_time}")
				# item_id = event["itemId"]
				par_id = event["participantId"]
				print(f"\tParticipant \"{par_id}\"")
				match event["type"]:
					case "ITEM_PURCHASED":
						next_index = len(tuple_participants[par_index[event["participantId"]]].items)
						tuple_participants[par_index[event["participantId"]]].items.insert(next_index, event["itemId"])
						print("\t\tItem added")
					case "ITEM_UNDO":
						if (event["beforeId"] > 0):
							reset_items = undo_items(past_events, event["beforeId"], event["participantId"])
							print("Returned Undo Items:")
							for item in reset_items:
								next_index = len(tuple_participants[par_index[event["participantId"]]].items)
								tuple_participants[par_index[event["participantId"]]].items.insert(next_index, item)
								print(f"\t\t--Item {item} reset.")
							tuple_participants[par_index[event["participantId"]]].items.remove(event["beforeId"])
							print("\t\tItem purchase undone.")
						else:
							tuple_participants[par_index[event["participantId"]]].items.insert(next_index, event["afterId"])
					case _:
						item_elixirs = [2138, 2139, 2140, 2150, 2151, 2152]
						if ((event["type"] == "ITEM_DESTROYED") and (event["itemId"] in item_elixirs) and (event["itemId"] not in tuple_participants[par_index[event["participantId"]]].items)):
							pass
						else:
							non_added_items = [2010, 2422, 3513, 3340, 2421, 2052] # Items that are not directly purchased and thus not previously added
							if event["itemId"] not in non_added_items:
								tuple_participants[par_index[event["participantId"]]].items.remove(event["itemId"])
								print("\t\tItem removed")
							else:
								print("Item already not added")

	return tuple_participants, past_events

def get_champ_states(match_timeline, match_participants):
	match_frames = {}
	past_events = []
	for frame in match_timeline["info"]["frames"]:
		frame_time = int(frame["timestamp"] / 60000)

		start_items = {}
		for participant in match_participants:
			start_items[participant] = []
		if (frame_time > 0):
			for participant in match_frames[frame_time - 1]:
				start_items[participant.participant_id] = participant.items


		print(f"Frame: {frame_time}")
		tuple_participants, past_events = get_participant_items(match_participants, frame["events"], start_items, past_events)

		par_index = 0
		for participant in tuple_participants:
			par_id = participant.participant_id
			print(f"Final Frame items for Participant {par_id}: ")
			print(participant.items)
			start_items[par_index] = participant.items
			par_index += 1
			participant.champion_stats = frame["participantFrames"][str(participant.participant_id)]["championStats"]
			
		match_frames[frame_time] = tuple_participants

		

# Main method for analyzing a match.
def analyze_match(match_id, user_puuid):
	filepath = Path(__file__).parent / "RiotAPIKey.txt"
	with open(filepath, "r") as f:
		api_key = f.read()
	lol_watcher = LolWatcher(api_key)

	match_timeline = lol_watcher.match.timeline_by_match(region=match_id[:match_id.find("_")], match_id=match_id)

	# Returns list of participant IDs, [0] is user, rest (next 5) are opponents
	match_pars = get_participants(match_timeline["info"]["participants"], user_puuid)

	champ_states = get_champ_states(match_timeline, match_pars)

	print(champ_states)
