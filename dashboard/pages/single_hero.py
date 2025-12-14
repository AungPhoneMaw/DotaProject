import streamlit as st
import os
import callback as cb

placeholder = st.empty()
for name, button in st.session_state.heroes.items():
    if button:
        placeholder.empty()
        cb.show_df(name)
        