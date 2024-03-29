import db_control

# Takes the current state of champ select and returns the user's selected champion and assigned position
async def get_info(state):
	cell_id = state["localPlayerCellId"]
	for player in state["myTeam"]:
		if player["cellId"] == cell_id:
			champ = player["championId"]
			position = player["assignedPosition"]
			break
	return champ, position

# Returns a champ based on ban/pick state
async def champ_suggest(state):
	bans = state["bans"]["myTeamBans"]
	ally_picks = []
	enemy_picks = []

	for ally in state["myTeam"]:
		ally_picks.append(ally["championId"])
	
	for enemy in state["theirTeam"]:
		enemy_picks.append(enemy["championId"])
	
	return 0
	#return state["timer"]["phase"]

# Returns most popular runes and items based on finalized pick
async def popular_suggest(state):
	champ, position = await get_info(state)
	return await db_control.get_popular_runes(champ, position), await db_control.get_popular_items(champ, position)

# Returns most successful runes and items based on finalized pick
async def success_suggest(state):
	champ, position = await get_info(state)
	return await db_control.get_success_runes(champ, position), await db_control.get_success_items(champ, position)

