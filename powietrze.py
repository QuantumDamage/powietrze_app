import streamlit as st
import pandas as pd
import numpy as np
from prophet import Prophet
from datetime import datetime, timedelta

st.set_page_config(layout="wide")

st.title('PM 2.5 w gminie Otmuchów')

DATE_COLUMN = 'date/time'
DATA_URL = ('http://80.211.245.168/pm2_5')

@st.cache(ttl=15*60)
def load_data():
    data = pd.read_csv(DATA_URL, index_col=0)
    data.set_index(pd.to_datetime(data.index).tz_convert('Europe/Warsaw'), inplace=True)
    return data

data = load_data()

st.subheader('Ostatnie dane:')
st.write(data.tail(n=6))

# options = st.multiselect(
#      'Wyświetl wykres dla miejsc:',
#      ['Meszno', 'Wójcice', 'Kałków', 'Maciejowice', 'Rynek', 'Krakowska'],
#      ['Rynek'])
# st.write('You selected:', options)
# filtered_data = data[options]
# st.line_chart(data=filtered_data.interpolate(method="time"), width=0, height=0, use_container_width=True)

st.subheader('Predykcja')

@st.cache()
def calculate_predictions(data, place):
    for_prophet = pd.DataFrame()
    for_prophet["ds"] = data.sort_index().index.tz_localize(None)
    for_prophet["y"] = data.sort_index()[place].values
    for_prophet['floor'] = 0

    m = Prophet()
    m.fit(for_prophet)

    future = m.make_future_dataframe(periods=7*24, freq="H")
    future["floor"] = 0
    future.tail()

    forecast = m.predict(future)
    forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail()

    for_chart = forecast[["ds", "yhat"]].set_index(["ds"], drop = True)

    tmp_data = pd.DataFrame(data[place])
    tmp_data.index = data.sort_index().index.tz_localize(None)
    tmp_data = tmp_data.interpolate(method="time")
    for_chart["data"] = tmp_data[place]
    for_chart["yhat"].clip(lower=0, inplace=True)
    for_chart["Bardzo dobry"] = 13
    for_chart["Dobry"] = 35
    for_chart["Umiarkowany"] = 55
    for_chart["Dostateczny"] = 75
    for_chart["Zły"] = 110
    return for_chart

place = st.selectbox(
     'Wybierz miejsce żeby zobaczyć historię i predykcję:',
     ('Meszno', 'Wójcice', 'Kałków', 'Maciejowice', 'Rynek', 'Krakowska'), 4)

for_chart = calculate_predictions(data=data, place=place)
# st.write(for_chart.head(n=6))
# st.write(for_chart[datetime.now()+timedelta(-7):].head(n=6))
for_chart = for_chart[datetime.now()+timedelta(-7):]
st.line_chart(for_chart)