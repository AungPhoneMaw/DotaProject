import opendota as opendota
import pandas as pd
import pprint 
import json
import pickle
import time, os, tempfile
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

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # folder of the script
STATE_DIR = os.path.join(BASE_DIR, "../state")
os.makedirs(STATE_DIR, exist_ok=True)

with open(os.path.join(STATE_DIR,"hero_match_dict.json"), "r") as f:
    hero_match_dict = json.load(f)
    logger.info("loaded hero_match_dict.json")
#retrieving hero id list
with open(os.path.join(STATE_DIR,"hero_id_list.pkl"), "rb") as f:
    HID = pickle.load(f)
    logger.info("loaded hero_id_list.pkl")

#data format to be collected for each hero
def load_hero_data_dict(HID):
    """ load hero data dict from existing hero_data.json if exists """

    header = ["hero_damage","tower_damage","healing",
              "team_hero_damage","team_tower_damage","team_healing", "total_gold", "total_xp",
              "hdpm","tdpm","hpm","thdpm","ttdpm","thpm","gpm","xpm"]
    if not os.path.exists(os.path.join(STATE_DIR,"hero_data.json")):
        return {
            hid: {k:[] for k in header} for hid in HID
        }
    #load existing data
    with open(os.path.join(STATE_DIR,"hero_data.json"), "r") as f:
        try:
            existing_data = json.load(f)
            logger.info("Loaded existing hero_data.json")
            return existing_data
        except json.JSONDecodeError:
            logger.error("Error decoding existing hero_data.json, initializing new data structure.")
            return {
                hid: {k:[] for k in header} for hid in HID
            }
    
hero_data_dict = load_hero_data_dict(HID)
logger.info("Initialized hero_data_dict")
#retrieving match ids
matches = pd.read_csv(os.path.join(STATE_DIR,"matches.csv"))
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

def atomic_json_dump(path, data):
    with tempfile.NamedTemporaryFile("w", delete=False) as tf:
        json.dump(data, tf, indent=2)
        temp_path = tf.name
    os.replace(temp_path, path)

def save_progress(data, last_batch):
    """this function saves the progress of data collection"""
    atomic_json_dump(os.path.join(STATE_DIR,"hero_data.json"), data)
    atomic_json_dump(os.path.join(STATE_DIR,"progress.json"), {"last_batch": last_batch})
    logger.info(f"Progress saved. batch: {last_batch}")

def load_progress():
    """this function loads the progress of data collection"""
    try:
        with open(os.path.join(STATE_DIR,"progress.json"), "r") as f:
            progress = json.load(f)
            logger.info(f"Resuming from batch {progress.get('last_batch',-1)}")
            return progress.get("last_batch",-1)
    except FileNotFoundError:
        logger.info("No progress file found, starting from the beginning.")
        return -1

def hero_data():
    """pipeline to collect hero data from matches and stoere it in hero_data.json"""
    last_loaded_batch = load_progress()
    total_batches = (len(match_ids) + BATCH - 1) // BATCH
    if last_loaded_batch >= total_batches - 1:
        logger.info("All batches have already been processed. Exiting.")
        exit(0)
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