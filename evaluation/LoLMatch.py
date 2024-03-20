from riotwatcher import LolWatcher
from pathlib import Path
from LoLParticipant import LoLParticipant

filepath = Path(__file__).parent / "RiotAPIKey.txt"
with open(filepath, "r") as f:
	api_key = f.read()

class LoLMatch:

	def __init__(self, match_id):
		self.match_id = match_id

		lol_watcher = LolWatcher(api_key)
		user_region = "NA1"
		match_info = lol_watcher.match.by_id(user_region, match_id)

		self.match_patch = match_info["info"]["gameVersion"]

		# Participants
		self.match_timestamps, match_frames = self.__get_match_frames()
		self.match_participants = tuple(LoLParticipant(participant["puuid"], (participant["riotIdGameName"] + "#" + str(participant["riotIdTagline"])), participant["participantId"], participant["championId"], participant["championName"], participant["teamId"], timeline=match_frames[participant["participantId"]]) for participant in match_info["info"]["participants"])
	
	def __get_match_frames(self): # return timestamps tuple(int), participant timelines dict{participant: {timestamp: {"items": [int], "skills": [int], "stats": {}, "level": int} } }
		lol_watcher = LolWatcher(api_key)
		match_timeline = lol_watcher.match.timeline_by_match(region=self.match_id[:self.match_id.find("_")], match_id=self.match_id)

		match_frame_timestamps = []
		match_frames = {participant_id: {} for participant_id in range(1, 11)}
		match_events = []
		for match_frame in match_timeline["info"]["frames"]:
			current_timestamp = match_frame["timestamp"]
			match_frame_timestamps.append(current_timestamp)

			for frame_event in match_frame["events"]:
				valid_event = ("ITEM_PURCHASED", "ITEM_DESTROYED", "ITEM_UNDO", "SKILL_LEVEL_UP")
				if (frame_event["type"] in valid_event):
					match_events.append(frame_event)

			for participant in match_frame["participantFrames"]:
				current_participant_frame = match_frame["participantFrames"][participant]
				match_frames[int(participant)][current_timestamp] = {"champion_stats": current_participant_frame["championStats"], "champion_level": current_participant_frame["level"]}
	

		participant_items_skills = self.__get_items_skills(match_events, match_frame_timestamps)
		for participant in participant_items_skills:
			for timestamp in participant_items_skills[participant]:
				match_frames[participant][timestamp].update(participant_items_skills[participant][timestamp])

		return tuple(match_frame_timestamps), match_frames
	
	def __get_items_skills(self, events, timestamps): # take list of events, return participant items/skills {participant: {timestamp: {"items": [int], "skills": [int] } } }
		return_items_skills = {participant_id: {} for participant_id in range(1, 11)}
		current_items_skills = {participant_id: {"items": [], "skills": [0, 0, 0, 0]} for participant_id in range(1, 11)}

		current_timestamp_index = 0
		current_event_index = 0 # To be used with ITEM_UNDO case
		for event in events:
			
			#check if add to return object
			if (event["timestamp"] > timestamps[current_timestamp_index]):
				for participant_id in current_items_skills:
					insert_items = []
					for item in current_items_skills[participant_id]["items"]:
						insert_items.insert(len(insert_items), item)
					insert_skills = [current_items_skills[participant_id]["skills"][0], current_items_skills[participant_id]["skills"][1], current_items_skills[participant_id]["skills"][2], current_items_skills[participant_id]["skills"][3]]

					return_items_skills[participant_id].update({timestamps[current_timestamp_index]: {"items": insert_items, "skills": insert_skills}})
					
				current_timestamp_index += 1
			
			match event["type"]:
				case "ITEM_PURCHASED":
					current_items_skills[event["participantId"]]["items"].insert(len(current_items_skills[event["participantId"]]["items"]), event["itemId"])
				case "ITEM_DESTROYED":
					non_purchase_items = (0, 2010, 2051,  2052, 2138, 2139, 2140, 2150, 2151, 2152, 2403, 2421, 2422, 3340, 3400, 3513, 3599, 3866, 3867)

					if event["itemId"] in non_purchase_items:
						pass
					else:
						if (event["itemId"] == 2055) and (event["itemId"] not in current_items_skills[event["participantId"]]["items"]): # CASE: player purchases 2 control wards, but destroys 3. Match: KR_6964987876 Timestamp: 1738274
							pass
						elif (event["itemId"] == 4638) and (event["itemId"] not in current_items_skills[event["participantId"]]["items"]):# CASE: player destroys 2 watchful wardstones, can only own 1. Match: KR_6964987876 Timestamp: 1839921
							pass
						else:
							current_items_skills[event["participantId"]]["items"].remove(event["itemId"])
				case "ITEM_UNDO":
					if event["beforeId"] == 0: # Undo a sell
						current_items_skills[event["participantId"]]["items"].insert(len(current_items_skills[event["participantId"]]["items"]), event["afterId"])
					else: # Undo a purchase
						undo_item_id = event["beforeId"]
						event_search_index = current_event_index - 1
						
						event_participant = event["participantId"]
						item_match = False
						while(not item_match):
							current_search_event = events[event_search_index]
							if ((current_search_event["type"] == "ITEM_PURCHASED") and (current_search_event["itemId"] == undo_item_id) and (current_search_event["participantId"] == event_participant)):
								item_match = True
								item_purchase_timestamp = current_search_event["timestamp"]
							event_search_index -= 1
						
						destroyed_items = []
						final_destroyed_item = False
						if event_search_index >= 0:
							while((not final_destroyed_item) and (event_search_index >= 0)):
								current_destroyed_event = events[event_search_index]
								if ((current_destroyed_event["type"] == "ITEM_DESTROYED") and (current_destroyed_event["timestamp"] == item_purchase_timestamp) and (current_search_event["participantId"] == event_participant)):
									destroyed_items.insert(len(destroyed_items), current_destroyed_event["itemId"])
								elif current_destroyed_event["timestamp"] < item_purchase_timestamp:
									final_destroyed_item = True
								event_search_index -= 1
						
						current_items_skills[event["participantId"]]["items"].remove(undo_item_id)

						for item in destroyed_items:
							current_items_skills[event["participantId"]]["items"].insert(len(current_items_skills[event["participantId"]]["items"]), item)
				case "SKILL_LEVEL_UP":
					current_items_skills[event["participantId"]]["skills"][event["skillSlot"] - 1] += 1
			
			if current_event_index == len(events) - 1:
				for participant_id in current_items_skills:
					insert_items = []
					for item in current_items_skills[participant_id]["items"]:
						insert_items.insert(len(insert_items), item)
					insert_skills = [current_items_skills[participant_id]["skills"][0], current_items_skills[participant_id]["skills"][1], current_items_skills[participant_id]["skills"][2], current_items_skills[participant_id]["skills"][3]]

					return_items_skills[participant_id].update({timestamps[current_timestamp_index]: {"items": insert_items, "skills": insert_skills}})
				

			current_event_index += 1

		return return_items_skills
	
	def match_summary(self):
		return f"Match ID: {self.match_id}\nMatch Patch: {self.match_patch}"
	
	def participants_summary(self):
		return_string = ""
		for participant in self.match_participants:
			return_string = return_string + str(participant) + "\n"
		return return_string
	
	def get_participant_timeline(self):
		return self.match_participants[0].get_timeline()
	
	def get_match_state(self):
		pass
	

