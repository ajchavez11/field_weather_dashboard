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
        url = 'https://api.openweathermap.org/data/2.5/forecast'
        params = {
            'lat': lat_float,
            'lon': lon_float,
            'appid': api_key,
            'units': 'metric',
        }

        cache_path = 'data/cache.json'
        if os.path.exists(cache_path):
            with open(cache_path, 'r') as f:
                data = json.load(f)
                st.info(f'Cache file {cache_path} loaded')
                st.write(f'Cache data for {data['city']['name']}')
                st.success(f'Got weather data! Ready to process!')
        else:
            response = r.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                cache_path = 'data/cache.json'
                with open(cache_path, 'w') as f:
                    json.dump(data, f)
            else:
                st.error(f'API Error: {response.json().get('message', 'Unknown Error')}')
    except ValueError:
        st.error('Please enter a valid latitude and longitude.')


