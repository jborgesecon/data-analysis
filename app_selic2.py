# updated version, consuming from API

import navigation as nav
import streamlit as st
import pandas as pd
import numpy as np
import requests
import base64
import time
import os

from dotenv import load_dotenv
from datetime import datetime
from io import StringIO
from PIL import Image


load_dotenv()
# # FUNCTIONS/ DB_CONN
# definitions and initialization
relevant_info2 = [
    'dt_init',
    'dt_fim',
    'valor'
]

for info in relevant_info2:
    if info not in st.session_state:
        st.session_state[info] = []

# update selic, send to economics.db at bcb.selic
def update_interest():
    params = {
    'formato': 'json',
    'dataInicial': '01/01/2001',
    'dataFinal': datetime.today().strftime('%d/%m/%Y')
    }
    url = nav.all_datasets['BR_apis']['bcb_selic']
    main2 = requests.get(url=url, params=params)
    df = pd.DataFrame(main2.json())
    df['data'] = pd.to_datetime(df['data'], dayfirst=True)
    df['valor'] = pd.to_numeric(df['valor'].astype('float'))
    df.to_sql("bcb.selic", nav.sqlite_conn, if_exists='replace')
    return

def dt_treatment(row):
    try:
        return pd.to_datetime(row, dayfirst=True)
    except ValueError as e:
        print(f'Error on {row}: {e}')
        return row

def udata_treatment(dataframe):
    udata = dataframe.iloc[:,:3]
    udata.columns = relevant_info2
    for date in relevant_info2[:2]:
        udata[date] = udata[date].map(dt_treatment)
    udata[relevant_info2[-1]] = udata[relevant_info2[-1]].apply(lambda x: x.replace(',', '.'))
    udata[relevant_info2[-1]] = pd.to_numeric(udata[relevant_info2[-1]], errors='coerce').astype(float)
    return udata



# # SIDEBAR
st.sidebar.header('Campos e Filtros')
option = st.sidebar.radio("Escolha uma opção:", ("Preenchimento Manual", "Arquivo CSV"))

if option == "Preenchimento Manual":
    d1, d2 = st.sidebar.columns(2)
    dt_init = d1.date_input("Data Inicial", datetime.now())
    dt_fim = d2.date_input("Data Final", datetime.now())
    if dt_init > dt_fim:
        st.sidebar.error("A Data Final **não** pode ser antes da Data Inicial!")
    else:
        initial_amount = st.sidebar.number_input("Valor Inicial", value=0.00, format="%.2f", min_value=0.00)
        if st.sidebar.button("Adicionar Dados"):
            st.session_state.valor.append(initial_amount)
            st.session_state.dt_init.append(dt_init)
            st.session_state.dt_fim.append(dt_fim)
            st.sidebar.success(f"Valores Adicionados!")
        user_data = pd.DataFrame({
            str(relevant_info2[0]): st.session_state.dt_init,
            str(relevant_info2[1]): st.session_state.dt_fim,
            'valor': st.session_state.valor
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

# # MAIN PAGE

image = Image.open(os.getenv('icon_selic'))
st.image(image=image, use_container_width=True)
st.title('APP DO ECONOMISTA JG 👍')

st.markdown("""
## Esse programa traz a correção monetária de acordo com a Taxa Selic

**Fonte:** [BACEN]('https://www.bcb.gov.br/controleinflacao/historicotaxasjuros')
""")

data = pd.read_sql(nav.read_sql_file('selic'), nav.sqlite_conn)


if st.button('Atualizar Selic'):
    update_interest()