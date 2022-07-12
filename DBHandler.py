from replit import db
import mwclient

class DBHandler():
		def __init__(self):
				self.keys = db.keys()
				self.champs = self.grab_all_champions()

		def grab_all_champions(self) -> []:
				site = mwclient.Site('lol.fandom.com', path='/')
				query_response = site.api('cargoquery', limit="max", tables="Champions=Ch", fields="Ch.Name")
				champs = [champ_dict['title']['Name'] for champ_dict in query_response['cargoquery']]

				return champs

		def check_if_champ_is_finished(self, userId: int, champId: int) -> bool:
				value = self.get_key_value(userId)
				if value['champs'][str(champId)]['finished']:
						return True
				else:
						return False

		def add_key_value_pair(self, key: str, value: str):
				db[key] = value

		def remove_key_value_pair(self, key: str):
				if self.check_if_key_exists(key):
						del db[str(key)]
						return True
				else:
						return False

		def get_key_value(self, key: str):
				if self.check_if_key_exists(key):
						return db[str(key)]
				else: 
						return False

		def generate_json_dummy(self, userId: str, isAtoZ: bool):
				dummy = {"userId": str(userId), "isAtoZ": False, "currentChamp": 0, "champs": {} }
				if isAtoZ:
						dummy["isAtoZ"] = True
						dummy["currentChamp"] = 1
				else:
						dummy["isAtoZ"] = False
						dummy["currentChamp"] = len(self.champs)

				champs_dict = {}
				for champion in self.champs:
						temp_dict = {"tries": 0, "finished": False}
						champs_dict[self.champs.index(champion) + 1] = temp_dict
				dummy["champs"] = champs_dict

				return dummy

		def check_if_key_exists(self, key: str):
				try:
						_ = db[str(key)]
				except KeyError:
						return False
				return True
		
		def is_user_finished(self, userId):
				userEntry = db[str(userId)]['champs']
				for value in userEntry:
						champDict = userEntry[value]
						print(champDict)
						if champDict['finished'] == False:
								return False
				return True

		def grab_player_stats(self, user):
				userId = user.id
				base_str_1 = ""
				base_str_2 = ""
				base_str_3 = ""
				done_str = ""
				started_str = ""
				done_champs = []
				started_champs = []
				userEntry = db[str(userId)]['champs']
				for value in userEntry:
						champDict = userEntry[value]
						if champDict['finished'] == True:
								done_champs.append((self.champs[int(value) - 1], champDict['tries']))
						elif champDict['tries'] > 0:
								started_champs.append((self.champs[int(value) - 1], champDict['tries']))
				base_str_1 += f"Stats for {user.name} \n"
				base_str_2 += f"{user.name} has won on the following champions: \n"

				for championName, tries in done_champs:
						done_str += f"{championName} in {tries} attemps. \n"

				base_str_3 += f"{user.name} has played the following champs unsuccessfully: \n"

				for championName, tries in started_champs:
						started_str += f"{championName} with currently {tries} attemps \n"

				return base_str_1, base_str_2, done_str, base_str_3, started_str

		def get_winrate_for_id(self, user):
				userId = user.id
				userEntry = db[str(userId)]['champs']
				totalTries = 0
				totalWins = 0
				totalLosses = 0
				champsPlayed = 0
				for value in userEntry:
						champDict = userEntry[value]
						if champDict['finished'] == True:
								champTries = champDict['tries']
								totalTries += champTries
								totalWins += 1
								totalLosses = champTries - 1
								champsPlayed += 1
						elif champDict['tries'] > 0:
								champTries = champDict['tries']
								totalTries += champTries
								totalLosses += champTries
								champsPlayed += 1
				if totalTries == 0:
						return
				winrate = totalWins / totalTries * 100
				str_1 = f"You have had a total of {totalTries} Attempts at a total of {champsPlayed} Champions"
				str_2 = f"Your winrate accros all those games is {winrate}%"
				return str_1, str_2
							
