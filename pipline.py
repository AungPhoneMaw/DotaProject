import opendota as opendota
import pandas as pd
import pprint 
import json
import pickle
import time

"""
this script retrives match data from the match ids associted with each hero in 
'hero_match_dict.json'
"""
#constants
BATCH = 50
SLEEP = 60


with open("hero_match_dict.json", "r") as f:
    hero_match_dict = json.load(f)
print(hero_match_dict)
#retrieving hero id list
with open("hero_id_list.pkl", "rb") as f:
    HID = pickle.load(f)

#data format to be collected for each hero
hero_data_dict = {hid: {"hero_damage":[],
                        "tower_damage":[],
                        "healing":[],
                        "team_hero_damage":[],
                        "team_tower_damage":[],
                        "team_healing":[],
                        "total_gold":[],
                        "total_xp":[],
                        "hdpm":[],
                        "tdpm":[],
                        "hpm":[],
                        "thdpm":[],
                        "ttdpm":[],
                        "thpm":[],
                        "gpm":[],
                        "xpm":[]} for hid in HID}
#retrieving match ids
matches = pd.read_csv("matches.csv")
match_ids = matches["match_id"].to_list()

#opening opendota client
client = opendota.OpenDota()

def safe_get(match_id, retries = 5, delay = 5):
    url = f"/matches/{match_id}"
    for attempt in range(retries):
        try:
            return client.get(url)
        except Exception as e: 
            print(f"Error retrieving match id {match_id}, attempt {attempt + 1} of {retries}")
            time.sleep(delay)
    print(f"Failed to retrieve match id {match_id} after {retries} attempts.")
    return None


for batch in range(0, len(match_ids), BATCH):
    for match_id in match_ids[batch:batch+BATCH]:
        match = safe_get(match_id)
        if match is None:
            continue
        duration = match["duration"]
        print("Match Duration: ", duration)
        players = match["players"]
        # Radiant/dire totals
        team_totals = {
            "radiant": {"hero": 0, "tower": 0, "heal": 0},
            "dire": {"hero": 0, "tower": 0, "heal": 0}
        }

        for p in players:
            side = "radiant" if p["isRadiant"] else "dire"
            team_totals[side]["hero"] += p["hero_damage"]
            team_totals[side]["tower"] += p["tower_damage"]
            team_totals[side]["heal"] += p["hero_healing"]

        # assign values
        for p in players:
            hid = p["hero_id"]
            if hid == 0:
                continue

            side = "radiant" if p["isRadiant"] else "dire"
            t = team_totals[side]

            dmin = duration / 60

            hero_data_dict[hid]["hero_damage"].append(p["hero_damage"])
            hero_data_dict[hid]["tower_damage"].append(p["tower_damage"])
            hero_data_dict[hid]["healing"].append(p["hero_healing"])
            hero_data_dict[hid]["team_hero_damage"].append(t["hero"])
            hero_data_dict[hid]["team_tower_damage"].append(t["tower"])
            hero_data_dict[hid]["team_healing"].append(t["heal"])
            hero_data_dict[hid]["total_gold"].append(p["total_gold"])
            hero_data_dict[hid]["total_xp"].append(p["total_xp"])

            hero_data_dict[hid]["hdpm"].append(p["hero_damage"] / dmin)
            hero_data_dict[hid]["tdpm"].append(p["tower_damage"] / dmin)
            hero_data_dict[hid]["hpm"].append(p["hero_healing"] / dmin)
            hero_data_dict[hid]["thdpm"].append(t["hero"] / dmin)
            hero_data_dict[hid]["ttdpm"].append(t["tower"] / dmin)
            hero_data_dict[hid]["thpm"].append(t["heal"] / dmin)
            hero_data_dict[hid]["gpm"].append(p["total_gold"] / dmin)
            hero_data_dict[hid]["xpm"].append(p["total_xp"] / dmin)
    print("waiting 60s to avoid rate limit...")
    time.sleep(SLEEP)
pprint.pprint(hero_data_dict)
#saving hero data dict to json
with open("hero_data.json", "w") as f:
    json.dump(hero_data_dict, f)