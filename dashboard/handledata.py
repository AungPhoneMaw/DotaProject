import pandas
import os
import logging

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # folder of the script
STATE_DIR = os.path.join(BASE_DIR, "../state")

heroes = pandas.read_csv(os.path.join(STATE_DIR, "heroes.csv"))[["id", "localized_name", "primary_attr"]]
logger.info("Loaded heroes.csv for display")

print(heroes[heroes["localized_name"]=="Mars"]["id"])

