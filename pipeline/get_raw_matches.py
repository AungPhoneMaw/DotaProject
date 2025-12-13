import opendota as opendota
import pandas as pd
import pprint 
import logging
"""
this script retrives the public matches with minimum rank immortal and append it to
 "matches.csv"
"""
#logger
logger = logging.getLogger(__name__)
#retrieving last match_id
with open("matches.csv", "r") as f:
    lines = f.readlines()
    last_line = lines[-1]
    last_match_id = last_line.split(",")[1]
    logger.info(f"last match id retrieved: {last_match_id}")
client = opendota.OpenDota()
matches = client.get("/publicMatches?min_rank=80&less_than_match_id="+str(last_match_id))
logger.info(f"retrieved {len(matches)} new matches from opendota")
matches_df = pd.DataFrame(matches)
matches_df = matches_df[["match_id","radiant_team","dire_team" ]]
matches_df.to_csv("matches.csv", mode="a",index=True, header=False)
logger.info(f"appended new matches to matches.csv")
print(matches_df)