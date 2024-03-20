import requests

class LoLDamageCalculator:

	def __init__(self):
		self.items_dict = requests.get("https://cdn.merakianalytics.com/riot/lol/resources/latest/en-US/items.json").json()
		self.champions_dict = requests.get("https://cdn.merakianalytics.com/riot/lol/resources/latest/en-US/champions.json").json()
	
	def get_item(self, item):
		return self.items_dict[str(item)]
	
	def get_stats(self, item):
		item_base_stats = self.get_item(item)["stats"]

		print(item_base_stats)

		item_return_stats = {}
		for stat_name in item_base_stats:
			print(stat_name)

			stat_values = {}
			for stat_value in item_base_stats[stat_name]:
				print(f"\t{stat_value}")
				print("\t\t" + str(item_base_stats[stat_name][stat_value]))

				if (item_base_stats[stat_name][stat_value] != 0.0):
					stat_values[stat_value] = item_base_stats[stat_name][stat_value]
			
			if (len(stat_values) > 0):
				item_return_stats[stat_name] = stat_values
		return item_return_stats
	
	def get_passive(self):
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
	
