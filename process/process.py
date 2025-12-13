import pandas as pd
import os
import logging

#logger
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # folder of the script
STATE_DIR = os.path.join(BASE_DIR, "../state")

df = pd.read_json(os.path.join(STATE_DIR, "hero_data.json")).transpose()
print(df)