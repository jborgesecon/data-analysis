import navigation as nav
import streamlit as st
import pandas as pd
import base64
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from PIL import Image


# Defining header image and title
image = Image.open('icons\\basketball-8030918_1280.png')
st.image(image=image, use_container_width=True)
st.title('NBA Player Stats Explorer')

st.markdown("""
This app peforms simple webscraping of NBA player stats data!            

""")

# side menu
st.sidebar.header('User Input Features')
selected_year = st.sidebar.selectbox('Year', list(reversed(range(1980, 2023))))


# WEBSCRAPING -> collecting data of NBA players stats
@st.cache_data
def load_data(year):
    string = nav.all_datasets['webscraping']['basketball']
    url = string.format(year)
    html = pd.read_html(url, header=0)
    main_df = pd.DataFrame()

    # try this separately before creating the def
    for i in range(len(html)):
        immediate = pd.DataFrame(html[i])
        main_df = pd.concat([main_df, immediate], ignore_index=True)
    
    main_df = main_df[main_df.Age.notna()]
    main_df = main_df.drop_duplicates()
    main_df = main_df.fillna(0)
    playerstats = main_df.drop(labels=['Rk'], axis=1)
    return playerstats
playerstats = load_data(selected_year)

# Sidebar - Team selection
sorted_unique_teams = sorted(playerstats['Team'].unique())
selected_team = st.sidebar.multiselect('Team', sorted_unique_teams)

# Sidebar - Position selection
unique_pos = ['C', 'PF', 'SF', 'PG', 'SG']
selected_pos = st.sidebar.multiselect('Position', unique_pos)

# Filtering data
df_selected_teams = playerstats[(playerstats['Team'].isin(selected_team)) & playerstats['Pos'].isin(selected_pos)]

st.header('Display Player Stats of Selected Team(s)')
st.write(f'Data Dimensions: {str(df_selected_teams.shape[0])} rows and {str(df_selected_teams.shape[1])} columns')
st.dataframe(df_selected_teams)

# Download NBA player stats data
# https://docs.streamlit.io/knowledge-base/using-streamlit/how-download-file-streamlit
# https://discuss.streamlit.io/t/how-to-download-file-in-streamlit/1806
def file_download(df):
    # Convert DataFrame to CSV
    csv = df.to_csv(index=False)
    # Encode the CSV file to base64
    b64 = base64.b64encode(csv.encode()).decode()
    # Create the download link
    href = f'<a href="data:file/csv;base64,{b64}" download="playerstats.csv">Download CSV File</a>'
    return href

st.markdown(file_download(df_selected_teams), unsafe_allow_html=True)

# Heatmap
if st.button('Intercorrelation Heatmap'):
    st.header('Intercorrelation Matrix Heatmap')

    # Exclude non-numeric columns
    numeric_df = df_selected_teams.select_dtypes(include=[np.number])

    # Calculate the correlation matrix
    corr = numeric_df.corr()

    # Create a mask for the upper triangle
    mask = np.zeros_like(corr)
    mask[np.triu_indices_from(mask)] = True

    # Plot the heatmap
    with sns.axes_style("white"):
        f, ax = plt.subplots(figsize=(7, 5))
        ax = sns.heatmap(corr, mask=mask, vmax=1, square=True, annot=False, cmap="coolwarm")
        st.pyplot(f)