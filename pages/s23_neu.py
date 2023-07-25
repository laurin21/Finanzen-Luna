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

df_feed = pd.DataFrame(rows, columns =['Datum', 'Beschreibung', 'Kategorie', 'Betrag', 'Stadt'])
df_feed['Stadt'] = df_feed['Stadt'].fillna("Split")
df_feed["Stadt"] = df_feed["Stadt"].astype("category")
df_feed["Datum"] = pd.to_datetime(df_feed["Datum"], format = "%d.%m.%Y", errors = "coerce").dt.date 
df_feed["Betrag"] = df_feed["Betrag"].str.replace(",",".")
df_feed["Betrag"] = df_feed["Betrag"].astype('float')

days_list = ["18.07.2023", "19.07.2023", "20.07.2023", "21.07.2023", "22.07.2023", "23.07.2023", "24.07.2023", "25.07.2023", "26.07.2023", "27.07.2023", "28.07.2023", "29.07.2023", "30.07.2023", "31.07.2023", "01.08.2023", "02.08.2023", "03.08.2023", "04.08.2023", "05.08.2023", "06.08.2023", "07.08.2023", "08.08.2023", "09.08.2023", "10.08.2023", "11.08.2023", "12.08.2023", "13.08.2023", "14.08.2023", "15.08.2023", "16.08.2023", "17.08.2023"]

df_split = df_feed[df_feed["Stadt"] == "Split"]
splitted = round(float(df_split["Betrag"].sum()) / days, 2)
splitted_per_day = [splitted]*days
df_split.reset_index(drop=True, inplace=True)
df_split.drop(columns=['Stadt'], inplace=True)

df_no_split = df_feed[df_feed["Stadt"] != "Split"]
df_no_split['Datum'] = df_no_split['Datum'].apply(lambda dt: dt.strftime('%d.%m.%Y'))
sum_dates = pd.DataFrame(df_no_split.groupby("Datum")["Betrag"].sum())

df_days = pd.DataFrame([days_list, splitted_per_day])
df_days = df_days.T
new_column_names = {0: 'Datum',
                    1: 'Betrag'}
df_days.rename(columns=new_column_names, inplace=True)
df_days = df_days.merge(sum_dates, on='Datum', how='left', suffixes=('_df1', '_df2'))
df_days['Betrag_df2'].fillna(0, inplace=True)
df_days['Betrag'] = df_days['Betrag_df1'] + df_days['Betrag_df2']
df_days.drop(columns=['Betrag_df1', 'Betrag_df2'], inplace=True)

df = df_feed.copy()
for index in range(len(df_split)):
    amount_per_day = df_split.loc[index]["Betrag"] / days
    daily_expenses = pd.DataFrame({'Datum': days_list, 'Beschreibung': df_split.loc[index]["Beschreibung"] + " (splitted)", 'Kategorie': df_split.loc[index]["Kategorie"], 'Betrag': round(amount_per_day, 2)})
    df = pd.concat([df, daily_expenses], ignore_index=True)

df_budget = df_days.copy()
df_budget["Budget"] = daily_budget
df_budget["Budget Differenz"] = df_budget["Budget"] - df_budget["Betrag"]
df_budget["Betrag Gesamt"] = df_budget['Betrag'].cumsum()
df_budget["Budget Gesamt"] = df_budget['Budget'].cumsum()
df_budget["Gesamt Diff"] = df_budget["Budget Gesamt"] - df_budget["Betrag Gesamt"]

df_city = pd.DataFrame(df_feed.groupby("Stadt")["Betrag"].sum())
df_city = df_city.sort_values(by='Betrag', ascending = False, inplace=True)

df_categories = pd.DataFrame(df_feed.groupby("Kategorie")["Betrag"].sum())
df_categories = df_categories.sort_values(by='Betrag', ascending = False, inplace=True)

##########################

st.title("Finanzen Interrail")
st.markdown("### Ausgaben pro Tag")
st.bar_chart(df_days["Betrag"])

st.markdown("---")

st.write(df_categories)

st.markdown("### Ausgaben pro Kategorie")
#st.bar_chart(df_categories["Betrag"])

st.markdown("---")

st.markdown("### Ausgaben pro Stadt")
st.bar_chart(df_city["Betrag"])

##########################

st.markdown("---")
st.write("df_feed:")
st.write(df_feed)
st.write("df_split:")
st.write(df_split)
st.write("df:")
st.write(df)
st.write("df_days:")
st.write(df_days)
st.write("df_budget:")
st.write(df_budget)
st.write("df_city:")
st.write(df_city)
st.write("df_categories")
st.write(df_categories)

##########################

st.write("Itsch libbe ditsch 🧡")