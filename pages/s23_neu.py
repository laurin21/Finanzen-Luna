# streamlit_app.py

import streamlit as st
from google.oauth2 import service_account
from gsheetsdb import connect
import pandas as pd
import datetime as dt

#############

# Create a connection object.
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=[
        "https://www.googleapis.com/auth/spreadsheets",
    ],
)
conn = connect(credentials=credentials)

# Perform SQL query on the Google Sheet.
# Uses st.cache_data to only rerun when the query changes or after 10 min.
@st.cache_resource(ttl=600)
def run_query(query):
    rows = conn.execute(query, headers=1)
    rows = rows.fetchall()
    return rows

sheet_url = st.secrets["private_gsheets_url"]
rows = run_query(f'SELECT * FROM "{sheet_url}"')

##########################
days = 31
total_budget = 3000
daily_budget = round(total_budget / days, 2)

df_feed = pd.DataFrame(rows, columns =['Datum', 'Beschreibung', 'Kategorie', 'Betrag', 'Stadt', 'Split'])
df_feed["Split"].fillna(0, inplace=True)
df_feed["Split"] = df_feed["Split"].astype('int')
df_feed["Stadt"] = df_feed["Stadt"].astype("category")
df_feed["Datum"] = pd.to_datetime(df_feed["Datum"], format = "%d.%m.%Y", errors = "coerce").dt.date 
df_feed["Betrag"] = df_feed["Betrag"].str.replace(",",".")
df_feed["Betrag"] = df_feed["Betrag"].astype('float')

days_list = ["18.07.2023", "19.07.2023", "20.07.2023", "21.07.2023", "22.07.2023", "23.07.2023", "24.07.2023", "25.07.2023", "26.07.2023", "27.07.2023", "28.07.2023", "29.07.2023", "30.07.2023", "31.07.2023", "01.08.2023", "02.08.2023", "03.08.2023", "04.08.2023", "05.08.2023", "06.08.2023", "07.08.2023", "08.08.2023", "09.08.2023", "10.08.2023", "11.08.2023", "12.08.2023", "13.08.2023", "14.08.2023", "15.08.2023", "16.08.2023", "17.08.2023"]

df_split = df_feed[df_feed["Split"] == 1]
splitted = round(float(df_split["Betrag"].sum()) / days, 2)
splitted_per_day = [splitted]*days

df_days = pd.DataFrame([days_list, splitted_per_day])

df = pd.DataFrame()

df_budget = pd.DataFrame()

df_city = pd.DataFrame()

##########################

st.write("Feed:")
st.write(df_feed)
st.write("Split:")
st.write(df_split)
st.write("Main:")
st.write(df)
st.write("Days:")
st.write(df_days)
st.write("Budget:")
st.write(df_budget)
st.write("Stadt:")
st.write(df_city)





##########################

st.write("Itsch libbe ditsch 🧡")