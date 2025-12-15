import opendota as opendota
import pandas as pd
import pprint 
import logging
import os
"""
this script retrives the public matches with minimum rank immortal and append it to
 "matches.csv"
"""

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # folder of the script
STATE_DIR = os.path.join(BASE_DIR, "../state")

#logger
logger = logging.getLogger(__name__)
#retrieving last match_id

def get_raw_matches():
    """ retrieve raw matches from opendota and append to matches.csv """
    with open(os.path.join(STATE_DIR,"matches.csv"), "r") as f:
        lines = f.readlines()
        last_line = lines[-1]
        last_match_id = last_line.split(",")[1]
        logger.info(f"last match id retrieved: {last_match_id}")
    client = opendota.OpenDota()
    matches = client.get("/publicMatches?min_rank=80&less_than_match_id="+str(last_match_id))
    logger.info(f"retrieved {len(matches)} new matches from opendota")
    matches_df = pd.DataFrame(matches)
    matches_df = matches_df[["match_id","radiant_team","dire_team" , "radiant_win"]]
    matches_df["radiant_win"] = matches_df["radiant_win"].astype(int)
    matches_df.to_csv(os.path.join(STATE_DIR,"matches.csv"), mode="a",index=True, header=False)
    logger.info(f"appended new matches to matches.csv")
    print(matches_df)

def fix_index():
    """ fix index of matches.csv after appending new matches """
    matches_df = pd.read_csv(os.path.join(STATE_DIR,"matches.csv"))
    matches_df.reset_index(drop=True, inplace=True)
    matches_df.index += 1  # start index from 1
    matches_df.drop(columns="i", inplace=True)
    matches_df.to_csv(os.path.join(STATE_DIR,"matches.csv"), index=True)

fix_index()