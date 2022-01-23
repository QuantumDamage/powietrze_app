import streamlit as st
import pandas as pd
import numpy as np
from prophet import Prophet


st.title('PM 2.5 w gminie Otmuchów')

DATE_COLUMN = 'date/time'
DATA_URL = ('http://80.211.245.168/pm2_5')

@st.cache(ttl=15*60)
def load_data():
    data = pd.read_csv(DATA_URL, index_col=0)
    data.set_index(pd.to_datetime(data.index).tz_convert('Europe/Warsaw'), inplace=True)
    return data

# Create a text element and let the reader know the data is loading.
data_load_state = st.text('Loading data...')
# Load 10,000 rows of data into the dataframe.
data = load_data()
# Notify the reader that the data was successfully loaded.
data_load_state.text("Done! (using st.cache)")

if st.checkbox('Show raw data (tail)'):
    st.subheader('Raw data')
    st.write(data.tail())

options = st.multiselect(
     'Wyświetl wykres dla miejsc:',
     ['Meszno', 'Wójcice', 'Kałków', 'Maciejowice', 'Rynek', 'Krakowska'],
     ['Rynek'])

st.write('You selected:', options)

filtered_data = data[options]

st.line_chart(data=filtered_data.interpolate(method="time"), width=0, height=0, use_container_width=True)

st.subheader('Rynek')

for_prophet = pd.DataFrame()
for_prophet["ds"] = data.sort_index().index.tz_localize(None)
for_prophet["y"] = data.sort_index()["Rynek"].values
for_prophet['floor'] = 0

m = Prophet()
m.fit(for_prophet)

future = m.make_future_dataframe(periods=7*24, freq="H")
future["floor"] = 0
future.tail()

forecast = m.predict(future)
forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail()

for_chart = forecast[["ds", "yhat"]].set_index(["ds"], drop = True)

tmp_data = pd.DataFrame(data["Rynek"])
tmp_data.index = data.sort_index().index.tz_localize(None)
tmp_data = tmp_data.interpolate(method="time")
for_chart["data"] = tmp_data["Rynek"]

print(tmp_data)

st.line_chart(for_chart)