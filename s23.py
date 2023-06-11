import streamlit as st
import pandas as pd
from datetime import datetime
import numpy as np
import time
import gspread

st.set_page_config(
    page_title="Life 2.1",
    page_icon="",
    menu_items={}
)

st.title("Life 2.1 TEST2")

finanzen, wochenstunden, investment = st.tabs(["Finanzen", "Wochenstunden", "Investment"])

with finanzen:
	##### TITEL #####
	st.title("Finanzen Interrail")

	#### DATA IMPORT ####
	sa = gspread.service_account("service_account.json")
	sh = sa.open("Finanzen_Interrail")
	aus = sh.worksheet("Ausgaben")
	aus = pd.DataFrame(aus.get_all_records())

	aus["Betrag"] = aus["Betrag"].div(100)

	aus["Datum"] = pd.to_datetime(aus["Datum"], format = "%d.%m.%Y", errors = "coerce")

	aus_months = aus.groupby(aus.Datum.dt.month)["Betrag"].sum()
	aus_cat = aus.groupby("Kategorie")["Betrag"].sum()

	#### ÜBERSICHT #####
	st.subheader("Übersicht")
	period = st.slider(label = "Zeitraum", min_value = 1, max_value = len(aus_months), value = [1,len(aus_months)])
	
	aus_tab, ein_tab = st.tabs(["Ausgaben", "Einnahmen"])
	with aus_tab:
		st.line_chart(aus_months[period[0]:period[1]])

	st.write("")
	st.markdown("---")
	st.write("")

	#### KATEGORIEN ####
	st.subheader("Kategorien")

	aus_tab, ein_tab = st.tabs(["Ausgaben", "Einnahmen"])

	with aus_tab:
		aus_categories = ["Einkauf", "Essen", "Uni", "Luna", "Verschiedenes", "Freizeit", "Menschen", "Transport", "Urlaub", "Sport", "Kleidung", "Wohnung"]
		aus_default_categories= ["Einkauf", "Essen", "Uni", "Luna", "Verschiedenes", "Freizeit", "Menschen", "Transport", "Sport", "Kleidung"]
		aus_cat_selection = st.multiselect("Ausgaben Kategorie", options = aus_categories, default = aus_default_categories)
		st.bar_chart(aus_cat[aus_cat_selection])

	with ein_tab:
		ein_categories = ["Gehalt", "Taschengeld", "Verschiedenes"]
		ein_cat_selection = st.multiselect("Einnahmen Kategorie", options = ein_categories)
		st.bar_chart(ein_cat[ein_cat_selection])

	st.write("")
	st.markdown("---")
	st.write("")


	#### GANZER DATENSATZ ####
	see_data = st.expander('Ganzer Datensatz')
	with see_data:
		aus_tab, ein_tab = st.tabs(["Ausgaben", "Einnahmen"])

		with aus_tab:
			st.markdown("##### Ausgaben")
			st.dataframe(data=aus.reset_index(drop=True))
		with ein_tab:
			st.markdown("##### Einnahmen")
			st.dataframe(data=ein.reset_index(drop=True))


with wochenstunden:
	##### TITEL #####
	st.title("Wochenstunden")

	##### DATA IMPORT #####
	sa = gspread.service_account("service_account.json")
	sh = sa.open("wochenstunden")
	df = sh.worksheet("Tabelle1")
	df = pd.DataFrame(df.get_all_records())

	df["Stunden"] = df["Stunden"].map(float)
	df["Stunden"] = df["Stunden"].div(100)

	##### AVERAGE #####
	avg_lst = []
	for i in range(len(df["Stunden"])):
		current_avg = (df["Stunden"][:i].sum()/i)
		avg_lst.append(current_avg)
	df["Average"] = avg_lst	
	average = avg_lst[-1]	

	##### FURTHER EDA #####
	sum_h = df["Stunden"].sum()
	average_money = round(((average * 14) - (average * 14 * 0.036)) * 4.33, 3)
	sum_money = round(((sum_h * 14) - (sum_h * 14 * 0.036)) * 4.33, 3)
	avg_soll = 7.42
	delta = round(average - avg_soll, 3)
	rente = round(sum_h * 14 * 0.036, 2)

	##### LINE GRAPH ####
	st.line_chart(df[["Stunden", "Average"]])

	##### METRICS #####
	col1, col2, col3 = st.columns(3)
	with col1:
		st.metric(label = "Ø € pro Monat", value = f"{round(average_money,2)}€")
		st.metric(label = "∑ h", value = f"{round(sum_h,2)}h")
	
	with col2:
		st.metric(label = "Δ zum Min-Ø", value = f"{round(delta,2)}h")
		st.metric(label = "∑ € seit Jan. 2022", value = f"{round(sum_money,2)}€")
	with col3:
		st.metric(label = "Ø h pro Woche", value = f"{round(average,2)}h")
		st.metric(label = "Eingezahlt in Rentenkasse", value =  f"{round(rente,2)}€")


with investment:
	st.title("Investments")
	st.write("Work in progress")
