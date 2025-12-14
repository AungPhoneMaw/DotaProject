import streamlit as st
import os
import callback as cb

st.title("Dota 2 Hero Analysis")
row = st.columns(5)
row[0].button("Mean", on_click=cb.show_stats, args=("mean",))
row[1].button("Std", on_click= cb.show_stats, args= ("std",)) 
row[2].button("Min", on_click= cb.show_stats, args=("min",))
row[3].button("Median", on_click= cb.show_stats, args=("median",))
row[4].button("Max", on_click= cb.show_stats, args=("max",)) 