# streamlit_app.py

import pandas as pd
import streamlit as st

st.title("Finanzen Interrail")

# Read in data from the Google Sheet.
# Uses st.cache_data to only rerun when the query changes or after 10 min.
@st.cache_data(ttl=600)
def load_data(sheets_url):
    csv_url = sheets_url.replace("/edit#gid=", "/export?format=csv&gid=")
    return pd.read_csv(csv_url, sep='delimiter')

df = load_data(st.secrets["public_gsheets_url"])

st.dataframe(df)