import streamlit as st
import pandas as pd
import numpy as np

st.title('PM 2.5 w gminie Otmuchów')

DATE_COLUMN = 'date/time'
DATA_URL = ('http://80.211.245.168/pm2_5')

@st.cache
def load_data():
    data = pd.read_csv(DATA_URL, index_col=0)
    return data

# Create a text element and let the reader know the data is loading.
data_load_state = st.text('Loading data...')
# Load 10,000 rows of data into the dataframe.
data = load_data()
# Notify the reader that the data was successfully loaded.
data_load_state.text("Done! (using st.cache)")

if st.checkbox('Show raw data'):
    st.subheader('Raw data')
    st.write(data)
