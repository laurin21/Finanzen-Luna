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
df = pd.DataFrame(rows, columns =['Datum', 'Beschreibung', 'Kategorie', 'Betrag'])
# Print results.

df["Datum"] = pd.to_datetime(df["Datum"], format = "%d.%m.%Y", errors = "coerce")

st.dataframe(df)


cats = df["Kategorie"].unique
cat_selection = st.multiselect("Ausgaben Kategorie", options = cats)
st.bar_chart(cats[cat_selection])

st.write("Itsch libbe ditsch 🧡")