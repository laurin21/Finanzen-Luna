import yfinance as yf
import streamlit as st

ticker = yf.Ticker('GOOGL').info
market_price = ticker['regularMarketPrice']
previous_close_price = ticker['regularMarketPreviousClose']
st.write('Ticker: GOOGL')
st.write('Market Price:', market_price)
st.write('Previous Close Price:', previous_close_price)

