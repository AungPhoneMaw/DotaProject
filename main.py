import opendota as opendota
import pandas as pd
from pipeline.fetch_hero_data import hero_data
import subprocess
import sys
def run_streamlit():
    subprocess.run([sys.executable,"-m","streamlit", "run", "dashboard/app.py"])
if __name__ == "__main__":
    run_streamlit()