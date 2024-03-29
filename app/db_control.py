import mysql.connector
import json

cnx = mysql.connector.connect(user='user',
							host='localhost',
							port='3306',
							database='compsdb')
cursor = cnx.cursor()

async def get_popular_runes(champ, position):
	# This query gets a list of rune builds for a given champion and player position and orders it by its count.
	# The most commonly used rune build will be the first row of the result
	sql = f"""SELECT MatchRunes.rune_primary_style, MatchRunes.rune_primary_1, MatchRunes.rune_primary_2, MatchRunes.rune_primary_3, MatchRunes.rune_primary_4,
				MatchRunes.rune_secondary_style, MatchRunes.rune_secondary_1, MatchRunes.rune_secondary_2,
				MatchRunes.rune_stat_offense, MatchRunes.rune_stat_flex, MatchRunes.rune_stat_defense 
			FROM MatchRunes
			INNER JOIN MatchPicks
			ON MatchPicks.match_id=MatchRunes.match_id
				AND MatchPicks.account_puuid=MatchRunes.account_puuid
				AND MatchPicks.player_position="{position}"
				AND MatchPicks.champ_id={champ}
			GROUP BY MatchRunes.rune_primary_style, MatchRunes.rune_primary_1, MatchRunes.rune_primary_2, MatchRunes.rune_primary_3, MatchRunes.rune_primary_4,
				MatchRunes.rune_secondary_style, MatchRunes.rune_secondary_1, MatchRunes.rune_secondary_2,
				MatchRunes.rune_stat_offense, MatchRunes.rune_stat_flex, MatchRunes.rune_stat_defense
			ORDER BY COUNT(*) DESC
			"""
	cursor.execute(sql)
	result = cursor.fetchall()

	result_list = list(result[0]) # Sets result_list as the most popular rune build
	runes = result_list[1:5] # Sets "runes" to most popular primary rune build
	runes.extend(result_list[6:]) # Extends list to include secondary and stat runes
	styles = [result[0][0], result[0][5]] # Sets the style of above runes (required for rune page generation)

	return runes, styles

async def get_popular_items(champ, position): # FIXME Change to MatchItems
	# This query gets a set of items most frequently purchased for a specific champion and player position
	sql = f"""SELECT MatchItems.item_id
			FROM MatchItems
			INNER JOIN MatchPicks
			ON MatchItems.match_id=MatchPicks.match_id
				AND MatchItems.account_puuid=MatchPicks.account_puuid
				AND MatchPicks.player_position="{position}"
				AND MatchPicks.champ_id={champ}
				AND MatchItems.item_id!=0
			GROUP BY MatchItems.item_id, MatchPicks.player_position
			ORDER BY COUNT(*) DESC
			"""
	cursor.execute(sql)
	result = cursor.fetchall()
	result_list = [list(item)[0] for item in result] # Takes the results of the query and puts all items into a single list
	return result_list[:7] # Returns the first 6 items (most popular items) in the list

async def get_success_runes(champ, position):
	# This query gets a set of rune builds based on how many times the build recorded a win in a game
	# The first INNER JOIN gets a list of the most popular rune builds, similar to the get_popular_runes function above
	# The second INNER JOIN takes the first list and sorts it by how many wins the rune build has
	sql = f"""SELECT MatchRunes.rune_primary_style, MatchRunes.rune_primary_1, MatchRunes.rune_primary_2, MatchRunes.rune_primary_3, MatchRunes.rune_primary_4,
				MatchRunes.rune_secondary_style, MatchRunes.rune_secondary_1, MatchRunes.rune_secondary_2,
				MatchRunes.rune_stat_offense, MatchRunes.rune_stat_flex, MatchRunes.rune_stat_defense
			FROM ((MatchRunes
			INNER JOIN MatchPicks
			ON MatchPicks.match_id=MatchRunes.match_id
				AND MatchPicks.account_puuid=MatchRunes.account_puuid
				AND MatchPicks.player_position="{position}"
				AND MatchPicks.champ_id={champ})
			INNER JOIN MatchStats
			ON MatchStats.match_id=MatchRunes.match_id
				AND MatchStats.account_puuid=MatchRunes.account_puuid
				AND MatchStats.win=1
			)
			GROUP BY MatchRunes.rune_primary_style, MatchRunes.rune_primary_1, MatchRunes.rune_primary_2, MatchRunes.rune_primary_3, 
				MatchRunes.rune_primary_4, MatchRunes.rune_secondary_style, MatchRunes.rune_secondary_1, MatchRunes.rune_secondary_2,
				MatchRunes.rune_stat_offense, MatchRunes.rune_stat_flex, MatchRunes.rune_stat_defense, MatchStats.win
			ORDER BY COUNT(*) DESC
			"""
	cursor.execute(sql)
	result = cursor.fetchall()
	result_list = list(result[0]) # Sets result_list as the most popular rune build
	runes = result_list[1:5] # Sets "runes" to most popular primary rune build
	runes.extend(result_list[6:]) # Extends list to include secondary and stat runes
	styles = [result[0][0], result[0][5]] # Sets the style of above runes (required for rune page generation)
	return runes, styles

async def get_success_items(champ, position):
	return await get_popular_items(champ, position) #FIXME get most successful items
