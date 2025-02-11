# Deprecated. I overcomplicated it gathering data via webscraping with selenium,
# A second version has been created that consumes data on demand via API
# ps.: this will later be updated for practice reasons

import matplotlib.pyplot as plt
import navigation as nav
import streamlit as st
import seaborn as sns
import pandas as pd
import numpy as np
import requests
import base64
import time

from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from io import StringIO
from PIL import Image


image_path = 'icons/finance_graph.jpg'
image = Image.open(image_path)
st.image(image=image, use_container_width=True)
st.title('APP DO ECONOMISTA JG 👍')

st.markdown("""
## Esse programa traz a correção monetária de acordo com a Taxa Selic

**Fonte:** [BACEN]('https://www.bcb.gov.br/controleinflacao/historicotaxasjuros')
""")

# helper objects and functions
relevant_info1 = [
    'list_of_values',
    'start_date',
    'end_date'
]

relevant_info2 = [
    'dt_init',
    'dt_fim',
    'valor'
]

def dt_treatment(row):
    try:
        return pd.to_datetime(row, dayfirst=True)
    except ValueError as e:
        print(f'Error on {row}: {e}')
        return row

def split_time_interval(row):
    dates = row.split('-')
    data_init = (dates[0].strip())
    data_fim = (dates[1].strip()) if dates[1] else str(datetime.today().date())#.strftime('%d/%m/%Y')
    return pd.Series([data_init, data_fim])

def udata_treatment(dataframe):
    udata = dataframe.iloc[:,:3]
    udata.columns = relevant_info2
    for date in relevant_info2[:2]:
        udata[date] = udata[date].map(dt_treatment)
    udata[relevant_info2[-1]] = udata[relevant_info2[-1]].apply(lambda x: x.replace(',', '.'))
    udata[relevant_info2[-1]] = pd.to_numeric(udata[relevant_info2[-1]], errors='coerce').astype(float)
    return udata

# Static info -> Gather the data from BACEN and store it in cache
@st.cache_data
def get_data():     # All was tested on 'selic_webscraping.ipynb'
    # open the driver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    url = nav.all_datasets['webscraping']['selic_historico']
    driver.get(url)
    time.sleep(10)      # wait so the dynamic JavaScript will load, 10 secods was arbritrary
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()
    table = soup.find('table', {'id': "historicotaxasjuros"})
    html_string = str(table)
    html_string = html_string.replace(',', '.')

    # Declare a dataframe, start data cleansing
    df = pd.read_html(StringIO(html_string), header=1)[0]
    col_rename = [
        'numero',
        'data',
        'vies',
        'periodo_vigencia',
        'meta_selic',
        'TBAN',
        'taxa_mensal',
        'taxa_acumulado_ano'
    ]
    df.columns = col_rename

    # Transforming obj -> Int64
    df['numero'] = df['numero'].str.replace('Pres. (9)','')
    df['numero'] = df['numero'].str.replace(' (7)','')
    df['numero'] = df['numero'].str.replace(' ex. (8)','')
    df['numero'] = df['numero'].str.replace('ª','')
    df['numero'] = pd.to_numeric(df['numero'], errors='coerce').fillna(-1).astype('Int64')

    # Treating Datetime
    ll_dates = ['data_init', 'data_fim']
    df['data'] = df['data'].map(dt_treatment)
    df[ll_dates] = df['periodo_vigencia'].apply(split_time_interval)
    for date in ll_dates:
        df[date] = df[date].map(dt_treatment)

    # excluding irrelevant columns
    keep = [
        'numero',
        'data',
        'data_init',
        'data_fim',
        'taxa_mensal',
        'taxa_acumulado_ano',
        'meta_selic'
    ]
    data = df[keep]
    return data

for info in relevant_info1:
    if info not in st.session_state:
        st.session_state[info] = []


# # SIDEBAR AREA
st.sidebar.header('Campos e Filtros')#
option = st.sidebar.radio("Escolha uma opção:", ("Preenchimento Manual", "Arquivo CSV"))

if option == "Preenchimento Manual":
    data_init, date_end = st.sidebar.columns(2)
    start_date = data_init.date_input("Data Inicial", datetime.now())
    end_date = date_end.date_input("Data Final", datetime.now())
    if start_date > end_date:
        st.sidebar.error("A Data Final **não** pode ser antes da Data Inicial!")
    else:
        initial_amount = st.sidebar.number_input("Valor Inicial", value=0.00, format="%.2f", min_value=0.00)
        if st.sidebar.button("Adicionar Dados"):
            st.session_state.list_of_values.append(initial_amount)
            st.session_state.start_date.append(start_date)
            st.session_state.end_date.append(end_date)
            st.sidebar.success(f"Valores Adicionados!")
        user_data = pd.DataFrame({
            str(relevant_info2[0]): st.session_state.start_date,
            str(relevant_info2[1]): st.session_state.end_date,
            'valor': st.session_state.list_of_values
        })
elif option == "Arquivo CSV":
    uploaded_file = st.sidebar.file_uploader("Arraste o arquivo pra cá:", type=['csv'])
    if uploaded_file:
        try:
            user_data = udata_treatment(pd.read_csv(uploaded_file,sep=';', dtype='object'))
            st.sidebar.success("Importado com Sucesso!")
            # st.write(user_data)  # Display the DataFrame in the main page
        except Exception as e:
            st.sidebar.error(f"Ocorreu um erro: {e}")
    else:
        user_data = pd.DataFrame()


# # MAIN PAGE AREA
data = get_data()
st.header('Tabela com juros calculados')

if not user_data.empty:
    for date in relevant_info2[:2]:
        user_data[date] = (pd.to_datetime(user_data[date])).dt.to_period('d')
    st.write(
        user_data[relevant_info2[0]].dtype, 
        user_data[relevant_info2[1]].dtype,
        user_data[relevant_info2[2]].dtype
    )


st.write(
    data['data'].dtype,
    data['data_init'].dtype, 
    data['data_fim'].dtype
)



# começar os calculos: o que tem que fazer? 
# Primeiro: duas tabelas, somente data e valor/ data e taxa,
# converter a selic de intervalo para diário
# converter o user_data de intervalo para diário
# iterar sobre as duas para encontrar todo o periodo vigente
# filtrar usando dia como índice, 'merge' trazendo a taxa relativa ao dia
# mostrar userdata somente com o valor final corrigido e diferença
# permitir download the acumulação diária de cada valor, pra ver evolução .json

if st.button('Resetar Valores'):
    for info in relevant_info1:
        st.session_state[info] = []
    user_data = pd.DataFrame()


# st.dataframe(pd.DataFrame({'valor': [f"{x:.2f}" for x in st.session_state.list_of_values]}))
st.dataframe(user_data)
st.subheader('Selic Histórica (referência)')
if st.button('Ver Tabela'):
    st.dataframe(data)
##
