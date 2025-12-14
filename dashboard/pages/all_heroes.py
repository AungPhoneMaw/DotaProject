import streamlit as st
import os
import handledata as hd
import callback as cb

st.title("Dota 2 Hero Analysis")
strength, agility, intelligence, universal = st.columns(4)
strength.header("Strength")
agility.header("Agility")
intelligence.header("Intelligence")
universal.header("Universal")
st.session_state.heroes = {}
st.session_state.cols = {"str": strength, "agi": agility,
                         "int": intelligence, "all": universal}
for attr in ["str", "agi", "int", "all"]:
    for name in hd.heroes[hd.heroes["primary_attr"]==attr]["localized_name"]:
        st.session_state.heroes[name]=st.session_state.cols[attr].button(name)

for name, button in st.session_state.heroes.items():
    if button:
        cb.show_df(name)
