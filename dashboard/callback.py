import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import handledata as hd
import json
import os
import logging

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # folder of the script
STATE_DIR = os.path.join(BASE_DIR, "../state")

def show_df(hero):
    id = hd.heroes[hd.heroes["localized_name"]==hero]["id"].values[0]
    logger.debug(f"hero name: {hero}\n id: {id}")
    with open(os.path.join(STATE_DIR,"hero_data.json"),"r") as f:
        hero_data = json.load(f)
        logger.info("loaded json file") 
    df = pd.DataFrame(hero_data[str(id)])
    logger.info("loaded df")
    st.dataframe(df)
    st.dataframe(df.agg(["mean", "std", "min", "median", "max"]).transpose())
    for col in df.columns:
        fig, ax = plt.subplots()
        ax.set_title(f"Histogram of {col} for {hero}")
        df[col].hist(bins=50, ax=ax)
        st.pyplot(fig)

def show_stats(statistic): #"mean", "std", "min", "median", "max"
    agg = {
        "mean": np.mean,
        "std": np.std,
        "min": np.min,
        "median": np.median,
        "max": np.max
    }
    with open(os.path.join(STATE_DIR, "hero_data.json"), "r") as f:
        hero_data = json.load(f)
        logger.info("Loaded hero_data.json for display")

    heroes = pd.read_csv(os.path.join(STATE_DIR, "heroes.csv"))[["id", "localized_name", "primary_attr"]]
    heroes["id"] = heroes["id"].astype(int)
    logger.info("Loaded heroes.csv into a df")
    df = pd.DataFrame(hero_data)
    _stat_hero_data = df.applymap(agg[statistic]).transpose().reset_index().rename(columns={"index":"id"}, inplace=False)
    _stat_hero_data["id"] = _stat_hero_data["id"].astype(int)
    logger.info("Calculated mean stats for each hero")
    stat_hero_data = pd.merge(heroes, _stat_hero_data, on="id", how="left")
    logger.info("Merged stats with hero info")
    placeholder = st.empty()
    placeholder.empty()
    placeholder.dataframe(stat_hero_data)
    


    
