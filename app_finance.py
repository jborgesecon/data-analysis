import yfinance as yf
import streamlit as st
import pandas as pd


st.write("""
# Simple Stock Price App
         
Show are the stock closing price and volume of Google!         

""")

tickerSymbol = 'GOOGL'
tickerData = yf.Ticker(tickerSymbol)
tickerDf = tickerData.history(period='1d', start='2019-6-1', end='2022-6-1')

st.line_chart(tickerDf.Close)
st.line_chart(tickerDf.Volume)