import pandas as pd
import os
import logging
import json
import matplotlib.pyplot as plt
import numpy as np
#logger
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # folder of the script
STATE_DIR = os.path.join(BASE_DIR, "../state")

with open(os.path.join(STATE_DIR, "hero_data.json"), "r") as f:
    hero_data = json.load(f)
    logger.info("Loaded hero_data.json for display")

heroes = pd.read_csv(os.path.join(STATE_DIR, "heroes.csv"))[["id", "localized_name", "primary_attr"]]
heroes["id"] = heroes["id"].astype(int)
logger.info("Loaded heroes.csv into a df")
df = pd.DataFrame(hero_data)
mean_stat_hero_data = df.map(np.mean).transpose().reset_index().rename(columns={"index":"id"}, inplace=False)
mean_stat_hero_data["id"] = mean_stat_hero_data["id"].astype(int)
logger.info("Calculated mean stats for each hero")
mean_stat_hero_data = pd.merge(heroes, mean_stat_hero_data, on="id", how="left")
logger.info("Merged mean stats with hero info")
