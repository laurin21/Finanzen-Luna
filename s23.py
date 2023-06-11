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


df = pd.DataFrame(rows, columns =['Datum', 'Beschreibung', 'Kategorie', 'Betrag', 'Split'])

df["Split"].fillna(0, inplace=True)
df["Split"] = df["Split"].astype('int')

df["Datum"] = pd.to_datetime(df["Datum"], format = "%d.%m.%Y", errors = "coerce")
df["Betrag"] = df["Betrag"].str.replace(",",".")
df["Betrag"] = df["Betrag"].astype('float')

df_split = df[df["Split"] == 1]
df = df[df["Split"] != 1]

splitted = round(float(df_split["Betrag"].sum()) / days, 2)



cats = df["Kategorie"].unique()

sum_cats = pd.DataFrame(df.groupby("Kategorie")["Betrag"].sum())
sum_dates = pd.DataFrame(df.groupby("Datum")["Betrag"].sum())

days_list = ["18.07.2023", "19.07.2023", "20.07.2023", "21.07.2023", "22.07.2023", "23.07.2023", "24.07.2023", "25.07.2023", "26.07.2023", "27.07.2023", "28.07.2023", "29.07.2023", "30.07.2023", "31.07.2023", "01.08.2023", "02.08.2023", "03.08.2023", "04.08.2023", "05.08.2023", "06.08.2023", "07.08.2023", "08.08.2023", "09.08.2023", "10.08.2023", "11.08.2023", "12.08.2023", "13.08.2023", "14.08.2023", "15.08.2023", "16.08.2023", "17.08.2023"]
sum_list = [splitted] * days 

df_budget = pd.DataFrame(columns =['Datum', 'Betrag', 'Tagesbudget', 'Diff', "Gesamtbetrag",  "Moving Budget", "Moving Diff"])
df_budget["Datum"] = days_list
df_budget["Betrag"] = sum_list
df_budget["Tagesbudget"] = [daily_budget] * days
df_budget["Diff"] = [0] * days 
df_budget["Gesamtbetrag"] = [0] * days 
df_budget["Moving Budget"] = [0] * days 
df_budget["Datum"] = pd.to_datetime(df_budget["Datum"], format = "%d.%m.%Y", errors = "coerce")


st.dataframe(sum_dates)

for date in range(len(days_list)):
    for i in range(len(sum_dates)):
        if days_list[date] == sum_dates["Datum"][i]:
            sum_list[date] += sum_dates[i]

df_budget["Diff"] = df_budget["Tagesbudget"] - df_budget["Betrag"]

df_budget["Gesamtbetrag"] = df_budget['Betrag'].cumsum()
df_budget["Moving Budget"] = df_budget['Tagesbudget'].cumsum()

df_budget["Moving Diff"] = df_budget["Moving Budget"] - df_budget["Gesamtbetrag"]


st.dataframe(df_budget)






#####

st.title("Finanzen Interrail")

st.dataframe(sum_dates)
st.bar_chart(sum_dates)
st.dataframe(sum_cats)
st.bar_chart(sum_cats)

see_data = st.expander('Ganzer Datensatz')
with see_data:
    st.dataframe(df)

st.markdown("---")

st.write("Itsch libbe ditsch 🧡")