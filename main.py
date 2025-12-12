import opendota as opendota
import pandas as pd
import ast
import pprint 
import json

heroes_df = pd.read_csv("heroes.csv")

HID = heroes_df["id"].to_list()
print(HID)
matches_df = pd.read_csv("matches.csv")
matches_df["radiant_team"] = matches_df["radiant_team"].apply(ast.literal_eval)
matches_df["dire_team"] = matches_df["dire_team"].apply(ast.literal_eval)
print(matches_df)
"""
the goal is to get a dict where keys are hero id and values are match id where 
the hero is picked
"""
hero_match_dict = {hid: [] for hid in HID}
for _,row in matches_df.iterrows():
    match_id = row["match_id"]
    for hid in row["radiant_team"] + row["dire_team"]:
        if hid != 0:
            hero_match_dict[hid].append(match_id)

with open("hero_match_dict.json", "w") as f:
    json.dump(hero_match_dict, f)

hero_match_count = {}
for key in hero_match_dict.keys():
    hero_match_count[key] = len(hero_match_dict[key])

pprint.pprint(hero_match_count)