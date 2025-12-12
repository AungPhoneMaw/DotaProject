import opendota as opendota
import pandas as pd
import pprint 
import json
import pickle
import time
import logging

"""
this script retrives match data from the match ids associted with each hero in 
'hero_match_dict.json'
"""
#constants
BATCH = 50
SLEEP = 60

#logger
logger = logging.getLogger(__name__)
handler = logging.FileHandler('logs/log.log')
formatter = logging.Formatter('%(asctime)s - %(levelname)s -%(name)s- %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

with open("hero_match_dict.json", "r") as f:
    hero_match_dict = json.load(f)
    logger.info("loaded hero_match_dict.json")
#retrieving hero id list
with open("hero_id_list.pkl", "rb") as f:
    HID = pickle.load(f)
    logger.info("loaded hero_id_list.pkl")

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
logger.info("Initialized hero_data_dict")
#retrieving match ids
matches = pd.read_csv("matches.csv")
match_ids = matches["match_id"].to_list()
logger.info(f"retrieved {len(match_ids)} match ids from matches.csv")
#opening opendota client
client = opendota.OpenDota()

#functions
def fetch_match(match_id):
    """this function validate the match data before returning it"""
    data = safe_get(match_id)
    if data is None:
        return None
    if "players" not in data or not data["players"]:
        logging.info(f"Skipping match {match_id}: no players")
        return None
    if "duration" not in data or data["duration"] == 0:
        logging.info(f"Skipping match {match_id}: invalid duration")
        return None
    return data

def safe_get(match_id, retries = 5, delay = 5):
    """ this function tries to retrieve match data with retries on failure"""
    url = f"/matches/{match_id}"
    for attempt in range(retries):
        try:
            logger.info(f"retrieving match id {match_id}, attempt {attempt + 1} of {retries}")
            return client.get(url)
        except Exception as e: 
            logger.error(f"Error retrieving match id {match_id} on attempt {attempt + 1}: {e}")
            time.sleep(delay)
    logger.error(f"Failed to retrieve match id {match_id} after {retries} attempts.", exc_info=True)
    return None

def save_progress(data, last_batch):
    """this function saves the progress of data collection"""
    with open("hero_data.json", "w") as f:
        json.dump(data, f)
    with open("progress.json", "w") as f:
        json.dump({"last_batch": last_batch}, f)
    logger.info(f"Progress saved. batch: {last_batch}")

def load_progress():
    """this function loads the progress of data collection"""
    try:
        with open("progress.json", "r") as f:
            progress = json.load(f)
            logger.info(f"Resuming from batch {progress.get('last_batch',-1)}")
            return progress.get("last_batch",-1)
    except FileNotFoundError:
        logger.info("No progress file found, starting from the beginning.")
        return -1
last_loaded_batch = load_progress()
for batch_index, batch_start in enumerate(range(0, len(match_ids), BATCH)):
    if batch_index <= last_loaded_batch:
        print(f"Skipping batch {batch_index}...")
        logger.info(f"Skipping batch {batch_index}...")
        continue
    for match_id in match_ids[batch_start:batch_start+BATCH]:
        match = fetch_match(match_id)
        if match is None:
            logger.error(f"Skipping match id {match_id} due to retrieval failure.")
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
            logger.debug(f"Updated {side} totals: {team_totals[side]}")

        # assign values
        for p in players:
            hid = p["hero_id"]
            if hid == 0:
                logging.debug(f"Skipping invalid hero_id 0 in match {match_id}")
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
            logger.debug(f"Appended data for hero_id {hid} in match {match_id}")
    save_progress(hero_data_dict, batch_index)

    print("waiting 60s to avoid rate limit...")
    logger.info("Batch completed, sleeping to avoid rate limit...")
    time.sleep(SLEEP)
pprint.pprint(hero_data_dict)
#saving hero data dict to json
with open("hero_data.json", "w") as f:
    json.dump(hero_data_dict, f)