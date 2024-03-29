import mysql.connector
from riotwatcher import LolWatcher
import json
from pathlib import Path

cnx = mysql.connector.connect(user='user',
							host='localhost',
							port='3306',
							database='compsdb')
cursor = cnx.cursor()

filepath = Path(__file__).parent / "RiotAPIKey.txt"
with open(filepath, "r") as f:
	api_key = f.read()

api_key = open("RiotAPIKey.txt", "r").read()
lol_watcher = LolWatcher(api_key)

sql = "SELECT * FROM Accounts"

cursor.execute(sql)
result = cursor.fetchall()

for account in result:
	print(account[0])
	match_list = lol_watcher.match.matchlist_by_puuid(region=account[1], puuid=account[0], count=10, queue=420) # Add queue=420 for SoloQ games 

	for match in match_list:
		match_info = lol_watcher.match.by_id(region=account[1], match_id=match)
		match_timeline = json.dumps(lol_watcher.match.timeline_by_match(region=match[:match.find("_")], match_id=match))

		try:
			sql = "INSERT INTO Matches VALUES (%s, %s, %s)"
			val = (match, match_info["info"]["gameVersion"], match_timeline)

			cursor.execute(sql, val)
			cnx.commit()
		except mysql.connector.errors.IntegrityError as err:
			print("Matches exception: %s", err)

		for participant in match_info["info"]["participants"]:
			try:
				sql = "INSERT INTO MatchPicks VALUES (%s, %s, %s, %s)"
				val = (match, participant["puuid"], participant["championId"], participant["teamPosition"])

				cursor.execute(sql, val)
				cnx.commit()
			except mysql.connector.errors.IntegrityError as err:
				print("MatchPick exception: %s", err)
			
			# Runes values
			if participant["puuid"] == account[0]:
				try:
					sql = "INSERT INTO MatchRunes VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

					# Runes values
					rune_primary_style = participant["perks"]["styles"][0]["style"]
					rune_primary_1 = participant["perks"]["styles"][0]["selections"][0]["perk"]
					rune_primary_2 = participant["perks"]["styles"][0]["selections"][1]["perk"]
					rune_primary_3 = participant["perks"]["styles"][0]["selections"][2]["perk"]
					rune_primary_4 = participant["perks"]["styles"][0]["selections"][3]["perk"]
					rune_secondary_style = participant["perks"]["styles"][1]["style"]
					rune_secondary_1 = participant["perks"]["styles"][1]["selections"][0]["perk"]
					rune_secondary_2 = participant["perks"]["styles"][1]["selections"][1]["perk"]
					rune_stat_offense = participant["perks"]["statPerks"]["offense"]
					rune_stat_flex = participant["perks"]["statPerks"]["flex"]
					rune_stat_defense = participant["perks"]["statPerks"]["defense"]

					# Summoner Spells values
					summoner_1 = participant["summoner1Id"]
					summoner_2 = participant["summoner2Id"]

					val = (match, participant["puuid"], rune_primary_style, rune_primary_1, rune_primary_2, rune_primary_3, rune_primary_4,
						rune_secondary_style, rune_secondary_1, rune_secondary_2, rune_stat_offense, rune_stat_flex, rune_stat_defense,
						summoner_1, summoner_2)
					
					cursor.execute(sql, val)
					cnx.commit()
				except mysql.connector.errors.IntegrityError as err:
					print("MatchBuild exception: %s", err)
				
				#Item Values
				items_list = [participant[f"item{x}"] for x in range(6)]
				item_no = 0
				for item in items_list:
					try:
						sql = "INSERT INTO MatchItems VALUES (%s, %s, %s, %s)"
						val = (match, participant["puuid"], item_no, item)

						cursor.execute(sql, val)
						cnx.commit()
					except mysql.connector.errors.IntegrityError as err:
						print("MatchBuild exception: %s", err)
					item_no = item_no + 1
				
				# Match Stats values
				try:
					total_champ_damage = participant["totalDamageDealtToChampions"]
					total_champ_shield = participant["totalDamageShieldedOnTeammates"]
					total_champ_heal = participant["totalHeal"]
					total_cs = participant["totalMinionsKilled"]
					total_kills = participant["kills"]
					total_deaths = participant["deaths"]
					total_assists = participant["assists"]
					if participant["win"] == False:
						win = 0
					else:
						win = 1
					
					sql = "INSERT INTO MatchStats VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

					val = (match, participant["puuid"], total_champ_damage, total_champ_shield, total_champ_heal, total_cs, total_kills, 
							total_deaths, total_assists, win)
					cursor.execute(sql, val)
					cnx.commit()
				except mysql.connector.errors.IntegrityError as err:
					print("MatchBuild exception: %s", err)


