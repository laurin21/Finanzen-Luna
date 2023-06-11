# streamlit_app.py

import streamlit as st
from google.oauth2 import service_account
from gsheetsdb import connect
import pandas as pd

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


days = 31
total_budget = 3000
daily_budget = round(total_budget / days, 2)

days_list = ["18.07.2023", "19.07.2023", "20.07.2023", "21.07.2023", "22.07.2023", "23.07.2023", "24.07.2023", "25.07.2023", "26.07.2023", "27.07.2023", "28.07.2023", "29.07.2023", "30.07.2023", "31.07.2023", "01.08.2023", "02.08.2023", "03.08.2023", "04.08.2023", "05.08.2023", "06.08.2023", "07.08.2023", "08.08.2023", "09.08.2023", "10.08.2023", "11.08.2023", "12.08.2023", "13.08.2023", "14.08.2023", "15.08.2023", "16.08.2023", "17.08.2023"]
sum_list = [0] * days 
budget_list = [daily_budget] * days
diff_list = [0] * days 
floating_budget_list = [0] * days 

df = pd.DataFrame(rows, columns =['Datum', 'Beschreibung', 'Kategorie', 'Betrag', 'Split'])

df["Split"].fillna(0, inplace=True)
df["Split"] = df["Split"].astype('int')
df_split = df[df["Split"] == 1]
df = df[df["Split"] != 1]

splitted = round(float(df_split["Betrag"].sum()) / days, 2)

df["Datum"] = pd.to_datetime(df["Datum"], format = "%d.%m.%Y", errors = "coerce")
df["Betrag"] = df["Betrag"].str.replace(",",".")
df["Betrag"] = df["Betrag"].astype('float')

df_budget = pd.DataFrame([columns =['Datum', 'Betrag', 'Tagesbudget', 'Diff', "Floating Budget"])
df_budget["Datum"] = days_list
df_budget["Betrag"] = sum_list
df_budget["Tagesbudget"] = budget_list
df_budget["Diff"] = diff_list
df_budget["Floating Budget"] = floating_budget_list
df_budget["Datum"] = pd.to_datetime(df_budget["Datum"], format = "%d.%m.%Y", errors = "coerce")

st.dataframe(df_budget)

#####

st.title("Finanzen Interrail")

cats = df["Kategorie"].unique()

sum_cats = df.groupby("Kategorie")["Betrag"].sum()
sum_dates = df.groupby("Datum")["Betrag"].sum()

st.dataframe(sum_dates)
st.bar_chart(sum_dates)
st.dataframe(sum_cats)
st.bar_chart(sum_cats)

see_data = st.expander('Ganzer Datensatz')
with see_data:
    st.dataframe(df)

st.markdown("---")

st.write("Itsch libbe ditsch 🧡")