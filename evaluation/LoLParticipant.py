import json

class LoLParticipant:

	def __init__(self, puuid, riot_id, participant_id, champion_id, champion_name, team_id, timeline=None):
		self.puuid = puuid
		self.riot_id = riot_id
		self.participant_id = participant_id
		self.champion_id = champion_id
		self.champion_name = champion_name
		self.team_id = team_id
		if timeline is None:
			self.timeline = {}
		else:
			self.timeline = timeline

	def __str__(self):
		return f"Participant {self.participant_id} (Team {self.team_id}): {self.champion_name} ({self.riot_id})"
	
	def get_timeline(self):
		organize_timeline = json.dumps(self.timeline, indent=4)
		return f"Participant {self.participant_id} ({self.champion_name}): {organize_timeline}"
	
	def get_state(self, timestamp):
		return {"champion_id": self.champion_id, "champion_name": self.champion_name, "state": self.timeline[timestamp]}
