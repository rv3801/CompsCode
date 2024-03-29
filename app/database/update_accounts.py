import mysql.connector
import json

cnx = mysql.connector.connect(user='user',
							host='localhost',
							port='3306',
							database='compsdb')
cursor = cnx.cursor()

f = open("C:/Users/rober/Documents/School/2023/2023_Fall/lol_comp_app/database/db_players.json", encoding='utf8')
data = json.load(f)

for team in data["teams"]:
	try:
		sql = "INSERT INTO Teams (team_name, team_shortname, team_region) VALUES (%s, %s, %s)"
		val = (team["team_name"], team["team_shortname"], team["team_region"])

		cursor.execute(sql, val)
		cnx.commit()
	except mysql.connector.errors.IntegrityError as err:
			print("Matches exception: %s", err)
	

	team_id = cursor.lastrowid
	for player in team["players"]:
		try:
			sql = "INSERT INTO Players (player_ign, player_role, team_id) VALUES (%s, %s, %s);"
			val = (player["player_ign"], player["player_role"], team_id)

			cursor.execute(sql, val)
			cnx.commit()
		except mysql.connector.errors.IntegrityError as err:
			print("Matches exception: %s", err)
		

		player_id = cursor.lastrowid
		for account in player["accounts"]:
			try:
				sql = "INSERT INTO Accounts VALUES (%s, %s, %s)"
				val = (account["account_puuid"], account["account_region"], player_id)
				
				cursor.execute(sql, val)
				cnx.commit()
			except mysql.connector.errors.IntegrityError as err:
				print("Matches exception: %s", err)
			
