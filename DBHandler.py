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

  def check_if_key_exists(self, key: str):
    result = True
    try:
      _ = db[str(key)]
    except KeyError:
      result = False
    return result

  def generate_json_dummy(self, userId: str, isAtoZ: bool):
    
    dummy = {
    "userId": str(userId),
    "isAtoZ": False,
    "currentChamp": 0,
    "champs": {}
    }
    if isAtoZ:
      dummy["isAtoZ"] = True
      dummy["currentChamp"] = 1
    else:
      dummy["isAtoZ"] = False
      dummy["currentChamp"] = len(self.champs)

    champs_dict = {}
    for champion in self.champs:
      temp_dict = {
        "tries": 0,
        "finished": False
      }
      champs_dict[self.champs.index(champion) + 1] = temp_dict

    dummy["champs"] = champs_dict

    return dummy
