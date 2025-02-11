import navigation as nav
import matplotlib.pyplot as plt
import streamlit as st
import yfinance as yf
from PIL import Image
import pandas as pd
import seaborn as sns
import numpy as np
import base64


image_path = 'icons\\stock-exchange-3972311_1280.jpg'
image = Image.open(image_path)
st.image(image=image, use_container_width=True)
st.title('S&P 500 App')

st.markdown("""
## This app retrieves the list of the **S&P 500**

**Data source:** [Wikipedia](https://en.wikipedia.org/wiki/List_of_S%26P_500_companies)
""")

st.sidebar.header('User Input Features')

# Static info
url = nav.all_datasets['webscraping']['S&P500']
collected = pd.read_html(url, header=0)

stocks = pd.DataFrame(collected[0])
tickers=list(stocks.Symbol)

# Gather data from yfinance (customize at will)
dates = [date.date() for date in pd.date_range(start='1980-1-1', end='2024-12-1', freq='MS')]
low_year = st.sidebar.select_slider('Begginig', dates)
up_year = st.sidebar.select_slider('Ending', reversed(dates))

# webscraping -> S&P 500 data
@st.cache_data
def get_data(y1, y2):
    data = yf.download(
        tickers=tickers,
        start=y1,
        end=y2,
        interval='1d',
        group_by='ticker',
        auto_adjust=True,
        prepost=True,
        threads=True,
        proxy=None
    )
    return data
data = get_data(low_year, up_year)

def price_plot(symbol):
    df = pd.DataFrame(data[symbol].Close)
    df['Date'] = df.index.date
    # df['Date'] = df['Date'].date()

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.fill_between(df.Date, df.Close, color='skyblue', alpha=0.3)
    ax.plot(df.Date, df.Close, color='skyblue', alpha=0.8)
    ax.set_xticklabels(df.Date, rotation=90)
    ax.set_xlabel("Date", fontweight='bold')
    ax.set_ylabel("Closing Price", fontweight='bold')

    return fig

def volume_plot(symbol):
    df = pd.DataFrame(data[symbol].Volume)
    df['Date'] = df.index.date

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.fill_between(df.Date, df.Volume, color='skyblue', alpha=0.3)
    ax.plot(df.Date, df.Volume, color='skyblue', alpha=0.8)
    ax.set_xticklabels(df.Date, rotation=90)
    ax.set_xlabel("Date", fontweight='bold')
    ax.set_ylabel("Volume", fontweight='bold')

    return fig

# sidebar filters
unique_sectors = st.sidebar.selectbox('Sector', sorted(list(stocks['GICS Sector'].unique().tolist())))
sorted_unique_symbols = st.sidebar.selectbox('Symbol', sorted(tickers))

# filtering dataframe
df_selected_stocks = data[sorted_unique_symbols]
st.header('Display Stock Infoarmation')
st.write(f'Data Dimensions: {str(df_selected_stocks.shape[0])} rows and {str(df_selected_stocks.shape[1])} columns')
st.dataframe(df_selected_stocks)

# Closing Price and Volume maps
if st.button('Graphic'):
    st.header('Stock Analysis')
    col1, col2 = st.columns(2)
    with col1:
        st.subheader('Closing Prices')
        st.pyplot(price_plot(sorted_unique_symbols))

    with col2:
        st.subheader('Trade Volume')
        st.pyplot(volume_plot(sorted_unique_symbols))

# # NEXT STEPS:
# Add net Volume of trade and avererage of closing prices of each stock grouped by sector
# Add an interactive graph with candles and moving averages
# Variation of each sector in the given period (example: up by 59.45%)