import os
from dotenv import load_dotenv
import streamlit as st
import requests as r
import json
import pandas as pd

load_dotenv()
api_key = os.getenv("API_KEY", 'Missing_Key')

st.set_page_config(layout="wide", page_icon='🌤️')
st.title('Welcome to the Adventure Planning Dashboard!')

st.sidebar.header('Enter a Location')
lat = st.sidebar.text_input(value='', label='Latitude')
lon = st.sidebar.text_input(value='', label='Longitude')
fetch_button = st.sidebar.button('Fetch Weather')

if fetch_button:
    try:
        lat_float = float(lat)
        lon_float = float(lon)
        st.write(f'Valid Coordinates: {lat_float}, {lon_float}')
    except ValueError:
        st.error('Please enter a valid latitude and longitude.')


cache_path = 'data/cache.json'

if os.path.exists(cache_path):
    with open(cache_path, 'r') as f:
        cache = json.load(f)
        st.info('Loaded from Cache File')
        with open(cache_path, 'w') as f:
            json.dump(cache, f)
else:
    st.error('Cache File Not Found')


