import requests

class LoLDamageCalculator:

	def __init__(self):
		self.items_dict = requests.get("https://cdn.merakianalytics.com/riot/lol/resources/latest/en-US/items.json").json()
		self.champions_dict = requests.get("https://cdn.merakianalytics.com/riot/lol/resources/latest/en-US/champions.json").json()

	def calculate_damage_summary(self, current_participant, enemy_participants, timestamp=None):
		"""
		print summary of current_participant damage against each enemy_participant at the given timestamp

		ex.
		Damage at timestamp ____:
		vs Participant 1:
			attack: x
			q ability: x
			w...
			e...
			r...
		vs Participant 2:
			...
		"""
		if timestamp is None:
			match_timestamps = tuple(current_participant.timeline.keys())
			for match_timestamp in match_timestamps:
				self.calculate_damage_summary(current_participant, enemy_participants, match_timestamp)
		else:
			current_participant_state = current_participant.get_state(timestamp)
			enemy_participants_states = {enemy_participant.participant_id: enemy_participant.get_state(timestamp) for enemy_participant in enemy_participants}

			print(f"Match state at timestamp {timestamp}")
			print(f"Current Participant: ({current_participant.champion_name})\n{current_participant_state}")
			for enemy_state in enemy_participants_states:
				current_enemy_state = enemy_participants_states[enemy_state]
				print(f"Enemy {enemy_state}:\n{current_enemy_state}")
				self.calculate_vs_damage(current_participant_state, current_enemy_state)
			pass
	
	def calculate_vs_damage(self, current_participant_state, enemy_participant_state):
		#first get stats
		# offense: base AD*, bonus AD, AP, crit damage, armor pen, lethality, magic pen, 
		# defense: base health*, bonus health, armor*, bonus armor, magic resistance*, bonus magic resistance
		# utility: mana*
		print("vvvvvvvvvvvvvvvvvvvvv\ncalculate_vs_damage")

		current_par_stats = self.__get_current_stats(current_participant_state)
		print(f"Current Participant:\n{current_par_stats}")

		enemy_par_stats = self.__get_current_stats(enemy_participant_state)
		print(f"Enemy Participant:\n{enemy_par_stats}")
		print("^^^^^^^^^^^^^^^^^^^^^")


		#TODO calculations below


	def __get_current_stats(self, state):
		# for item in state["state"]["items"]:

		item_stats = {item: self.get_item_stats(item) for item in state["state"]["items"]}
		total_stats = self.__calc_total_stats(item_stats)

		offensive_stats = {
			"base_ad": self.__calc_increasing_stat(state, "attackDamage"),
			"bonus_ad": total_stats["attackDamage"] if "attackDamage" in total_stats else 0,
			"ap": total_stats["abilityPower"] if "abilityPower" in total_stats else 0,
			"crit_damage": 0, # 2.25 if 3031 in state["state"]["items"] else 1.75
			"armor_pen": total_stats["armorPenetration"] if "armorPenetration" in total_stats else 0,
			"lethality": total_stats["lethality"] if "lethality" in total_stats else 0,
			"magic_pen": total_stats["magicPenetration"] if "magicPenetration" in total_stats else 0
		}

		defensive_stats = {
			"base_health": self.__calc_increasing_stat(state, "health"),
			"bonus_health": total_stats["health"] if "health" in total_stats else 0,
			"armor": self.__calc_increasing_stat(state, "armor"),
			"bonus_armor": total_stats["armor"] if "armor" in total_stats else 0,
			"magic_resist": self.__calc_increasing_stat(state, "magicResistance"),
			"bonus_magic_resist": total_stats["magicResistance"] if "magicResistance" in total_stats else 0
		}

		utility_stats = {
			"mana": self.__calc_increasing_stat(state, "mana")
		}

		return {"offense": offensive_stats, "defense": defensive_stats, "utility": utility_stats}
	
	def get_item_stats(self, item):
		current_item = self.get_item(item)
		item_base_stats = current_item["stats"]

		item_base_stats_condensed = self.__condense_stats(item_base_stats)

		item_passives = current_item["passives"] if len(current_item["passives"]) > 0 else None
		item_passives_stats = [{"name": passive["name"], "effects": passive["effects"], "cooldown": passive["cooldown"], "stats": self.__condense_stats(passive["stats"])} for passive in item_passives] if item_passives is not None else None

		item_actives = current_item["active"] if len(current_item["active"]) > 0 else None
		item_actives_stats = [{"name": active["name"], "effects": active["effects"], "cooldown": active["cooldown"]} for active in item_actives] if item_actives is not None else None

		# if item_passives is not None:
		# 	item_passives_stats = [{"name": passive["name"], "effects": passive["effects"], "cooldown": passive["cooldown"], "stats": self.__condense_stats(passive["stats"])} for passive in item_passives]

		return_stats = {"base": item_base_stats_condensed, "passives": item_passives_stats, "actives": item_actives_stats}

		return return_stats
	
	def __condense_stats(self, full_stats):
		item_base_stats_condensed = {}
		for stat_category in full_stats:
			# print(stat_category)

			stat_measurement_dict = {}
			for stat_measurement in full_stats[stat_category]:
				# print(f"\t{stat_measurement}")
				# print("\t\t" + str(item_base_stats[stat_category][stat_measurement]))

				if (full_stats[stat_category][stat_measurement] != 0.0):
					stat_measurement_dict[stat_measurement] = full_stats[stat_category][stat_measurement]
			
			if (len(stat_measurement_dict) > 0):
				item_base_stats_condensed[stat_category] = stat_measurement_dict
		return item_base_stats_condensed if len(item_base_stats_condensed) > 0 else None
	
	def __calc_total_stats(self, item_stats): #item_stats: {item(int): dict of self.get_item_stats(item)}
		total_stats = {}
		for item in item_stats:
			# get base stats for each item
			base_stats = item_stats[item]["base"] # returns {stat_category: {stat_measurement: (float) , ...} ...}

			if base_stats is not None:
				for stat_category in base_stats:
					#get stat and add to total stat
					#if stat exists in total stat, add.
					#if not, create dict entry and add.
					if stat_category in total_stats:
						for stat_measurement in base_stats[stat_category]:
							
							if stat_measurement in total_stats[stat_category]:
								old_value = total_stats[stat_category][stat_measurement]
								total_stats[stat_category][stat_measurement] = old_value + base_stats[stat_category][stat_measurement]
							else:
								total_stats[stat_category][stat_measurement] = base_stats[stat_category][stat_measurement]
					else:
						total_stats[stat_category] = base_stats[stat_category]
		return total_stats
	
	def __calc_increasing_stat(self, state, stat):
		champion_name = state["champion_name"]
		champion_info = self.get_champion_byName(champion_name)

		stat_base = champion_info["stats"][stat]["flat"]
		stat_growth = champion_info["stats"][stat]["perLevel"]
		champ_level = state["state"]["champion_level"]

		return (stat_base + (stat_growth * (champ_level - 1) * (0.7025 + (0.0175 * (champ_level - 1) ) ) ) )
	
	#define attack/ability damage calculator

	def get_champion_byName(self, champion):
		return self.champions_dict[champion]

	def get_item(self, item):
		return self.items_dict[str(item)]
	


	#
	#
	#
	#
	#
	# temporary
	def find_passives(self):
		for item in self.items_dict:

			for passive in self.items_dict[item]["passives"]:
				passive_name = passive["name"]

				for passive_stat in passive["stats"]:

					for passive_stat_value in passive["stats"][passive_stat]:

						if (passive["stats"][passive_stat][passive_stat_value] != 0):
							print(item)
							print(f"\t{passive_name}")
							print(f"\t\t{passive_stat}")
							print(f"\t\t\t{passive_stat_value}: " + str(passive["stats"][passive_stat][passive_stat_value]))
	
