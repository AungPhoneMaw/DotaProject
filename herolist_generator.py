import pandas as pd
import pickle
heroes_df = pd.read_csv("heroes.csv")
HID = heroes_df["id"].to_list()
print(HID)
with open("hero_id_list.pkl", "wb") as f:
    pickle.dump(HID, f)