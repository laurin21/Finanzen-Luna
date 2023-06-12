# streamlit_app.py

import streamlit as st
from google.oauth2 import service_account
from gsheetsdb import connect
import pandas as pd
import datetime as dt

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


df = pd.DataFrame(rows, columns =['Datum', 'Beschreibung', 'Kategorie', 'Ausgaben', 'Split'])

df["Split"].fillna(0, inplace=True)
df["Split"] = df["Split"].astype('int')

df["Datum"] = pd.to_datetime(df["Datum"], format = "%d.%m.%Y", errors = "coerce").dt.date 
df["Ausgaben"] = df["Ausgaben"].str.replace(",",".")
df["Ausgaben"] = df["Ausgaben"].astype('float')

df_split = df[df["Split"] == 1]
df = df[df["Split"] != 1]

splitted = round(float(df_split["Ausgaben"].sum()) / days, 2)



cats = df["Kategorie"].unique()

sum_cats = pd.DataFrame(df.groupby("Kategorie")["Ausgaben"].sum())
sum_dates = pd.DataFrame(df.groupby("Datum")["Ausgaben"].sum())
sum_dates["Datum"] = sum_dates.index

days_list = ["18.07.2023", "19.07.2023", "20.07.2023", "21.07.2023", "22.07.2023", "23.07.2023", "24.07.2023", "25.07.2023", "26.07.2023", "27.07.2023", "28.07.2023", "29.07.2023", "30.07.2023", "31.07.2023", "01.08.2023", "02.08.2023", "03.08.2023", "04.08.2023", "05.08.2023", "06.08.2023", "07.08.2023", "08.08.2023", "09.08.2023", "10.08.2023", "11.08.2023", "12.08.2023", "13.08.2023", "14.08.2023", "15.08.2023", "16.08.2023", "17.08.2023"]
sum_list = [splitted] * days 

df_budget = pd.DataFrame(columns =['Datum', 'Ausgaben', 'Tagesbudget', 'Diff', "Ausgaben Gesamt",  "Moving Budget", "Moving Diff"])
df_budget["Datum"] = days_list
df_budget["Ausgaben"] = sum_list
df_budget["Tagesbudget"] = [daily_budget] * days
df_budget["Diff"] = [0] * days 
df_budget["Ausgaben Gesamt"] = [0] * days 
df_budget["Moving Budget"] = [0] * days 
df_budget["Datum"] = pd.to_datetime(df_budget["Datum"], format = "%d.%m.%Y", errors = "coerce").dt.date 


for date in range(len(days_list)):
    for i in range(len(sum_dates)):
        if dt.datetime.strptime(days_list[date], '%d.%m.%Y') == sum_dates["Datum"][i]:
            sum_list[date] += sum_dates["Ausgaben"][i]

df_budget["Ausgaben"] = sum_list

df_budget["Diff"] = df_budget["Tagesbudget"] - df_budget["Ausgaben"]

df_budget["Ausgaben Gesamt"] = df_budget['Ausgaben'].cumsum()

df_budget["Moving Diff"] = df_budget.iloc[:,2]+df_budget.iloc[:,3]

df_budget["Moving Budget"] = df_budget['Tagesbudget'].cumsum() 


#####

st.title("Finanzen Interrail")

st.markdown("### Ausgaben pro Tag")
st.dataframe(sum_dates)
st.bar_chart(sum_dates["Ausgaben"])

st.markdown("---")

st.markdown("### Ausgaben pro Kategorie")
st.dataframe(sum_cats)
st.bar_chart(sum_cats)

st.markdown("---")

st.markdown("### Ausgaben Gesamt vs. Moving Budgetdifferenz")
st.line_chart(df_budget[["Ausgaben Gesamt", "Moving Diff"]])

st.markdown("### Ausgaben vs. Budget (pro Tag)")
st.line_chart(df_budget[["Ausgaben", "Tagesbudget"]])

st.markdown("---")

st.write(f"Gesamtausgaben {df['Ausgaben'].sum()}")

st.markdown("---")

see_data = st.expander('Weitere Infos')
with see_data:
    
    st.markdown("### Budgetübersicht")
    st.dataframe(df_budget)
    st.markdown("---")

    st.markdown("### Rohdaten")    
    st.dataframe(df)
    st.markdown("---")

st.markdown("---")

st.write("Itsch libbe ditsch 🧡")