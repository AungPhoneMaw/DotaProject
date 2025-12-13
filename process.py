import pandas as pd

df = pd.read_json("hero_data.json")
print(df[1])