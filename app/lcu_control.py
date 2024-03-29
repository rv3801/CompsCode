from lcu_driver import Connector
import json
import champ_select_control

connector = Connector()

# Established WebSocket connection when client is launched
@connector.ready
async def connect(connection):
	print('LCU API is ready to be used.')
	this_summoner = await connection.request('get', '/lol-summoner/v1/current-summoner')
	response = json.loads(await this_summoner.read())
	global summoner_id
	summoner_id = response['summonerId'] # Assigns current user's summonerId to summoner_id, which is needed for runes page and item set generation

# Listens for anu updates in the champ select endpoint
@connector.ws.register('/lol-champ-select/v1/session', event_types=('UPDATE',))
async def updated(connection, event):
	response = await connection.request('get', '/lol-champ-select/v1/session')
	champ_select = json.loads(await response.read())
	phase = champ_select["timer"]["phase"]

	# When a champ select update is sent, check which phase of champ select the game is currently in
	match phase:
		case "BAN_PICK":
			print("BAN_PICK")
			# FIXME Get pick suggestion
		case "FINALIZATION":
			# Is run when all picks have been made
			print("FINALIZATION")
			get_pages = await connection.request('get', '/lol-perks/v1/pages')
			pages = json.loads(await get_pages.read())
			set_ids = [x["id"] for x in pages]

			# Gets the most popular runes page and items
			popular_runes, popular_items = await champ_select_control.popular_suggest(champ_select) # Runes object contains both runes and rune styles
			# Creates the first runes page for the most popular runes build
			new_popular_page = await connection.request('put', f'/lol-perks/v1/pages/{set_ids[0]}',
									  data={"name": "Most Popular",
									  "primaryStyleId": popular_runes[1][0], "selectedPerkIds": popular_runes[0], # Runes[1] contains styles
									  "subStyleId": popular_runes[1][1]})
			
			# Gets the most successful runes page and items
			success_runes, success_items = await champ_select_control.success_suggest(champ_select)
			# Creates the second runes page for the most successful runes build
			new_popular_page = await connection.request('put', f'/lol-perks/v1/pages/{set_ids[1]}',
									  data={"name": "Most Successful",
									  "primaryStyleId": success_runes[1][0], "selectedPerkIds": success_runes[0], # Runes[1] contains styles
									  "subStyleId": success_runes[1][1]})

			# Creates lists for both sets of items in the correct form for item set generation
			popular_item_list = [{"count": 1, "id": str(item)} for item in popular_items]
			success_item_list = [{"count": 1, "id": str(item)} for item in success_items]
			# Creates the new item set with the given item lists
			new_set = await connection.request('put', f'/lol-item-sets/v1/item-sets/{summoner_id}/sets', 
                                data={"itemSets": [{"associatedChampions": [], "associatedMaps": [12, 11], 
								"blocks": [{"items": popular_item_list, "type": "Most Popular Items"}, 
				   					{"items": success_item_list, "type": "Most Successful Items"}],
								"title": "Suggestion Sets"}]})
			
			


connector.start()