import os
from dotenv import load_dotenv
import streamlit as st
import requests as r
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

THRESHOLDS = {
    'high_temp': 30,
    'low_temp': -5,
    'high_wind': 10,
    'high_precip': 5
}

load_dotenv()
api_key = os.getenv("API_KEY", 'Missing_Key')

st.set_page_config(layout="wide", page_icon='🌤️')
st.title('Welcome to the Adventure Planning Dashboard!')

st.sidebar.header('Enter a Latitude and Longitude')
lat = st.sidebar.text_input(value='', label='Latitude')
lon = st.sidebar.text_input(value='', label='Longitude')

st.sidebar.header('Alert Settings')
high_temp_slider = st.sidebar.slider(label='High Temp Threshold (C)', min_value=20, max_value=40, value=30)
low_temp_slider = st.sidebar.slider(label='Low Temp Threshold (C)', min_value=-20, max_value=0, value=-5)
high_wind_slider = st.sidebar.slider(label='High Wind Speed (m/s)', min_value=20, max_value=100, value=50)
high_precip_slider = st.sidebar.slider(label='High Precipitation (mm)', min_value=0, max_value=10, value=3)
THRESHOLDS['high_temp'] = high_temp_slider
THRESHOLDS['low_temp'] = low_temp_slider
THRESHOLDS['high_wind'] = high_wind_slider
THRESHOLDS['high_precip'] = high_precip_slider

fetch_button = st.sidebar.button('Fetch Weather', icon='🌤️', width='content')

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
        response = r.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            try:
                with open(cache_path, 'w') as f:
                    json.dump(data, f)
                st.info(f'New data fetched and saved to {cache_path}')
            except Exception as e:
                st.error(f"New data fetched (cache not saved: {str(e)}")
        else:
            st.error(f'API Error: {response.json().get('message', 'Unknown Error')}')
        st.success(f'Got weather data! Ready to process!')

        forecast_list = data['list']
        df = pd.DataFrame(forecast_list)
        df['temp'] = df['main'].apply(lambda x: x['temp'] )
        df['wind_speed'] = df['wind'].apply(lambda x: x['speed'])

        def get_precipitation(weather_data):
            precip = 0
            if isinstance(weather_data.get('rain'), dict):
                precip += weather_data.get('3h', 0)
            if isinstance(weather_data.get('snow'), dict):
                precip += weather_data.get('3h', 0)
            return precip
        df['precip'] = df.apply(lambda x: get_precipitation(x), axis=1)

        df['date'] = pd.to_datetime(df['dt'], unit='s')
        df = df.drop(columns=['main', 'wind', 'rain', 'weather', 'clouds'], errors='ignore')
        start_date = df['date'].min()
        end_date = start_date + pd.Timedelta(days=3)
        df = df[df['date'] <= end_date]
        df['wind_chill'] = df['temp'] - (df['wind_speed'] * 0.7)
        df['precip'].fillna(0, inplace=True)
        avg_temp = np.mean(df['temp'])
        st.dataframe(df[['date', 'temp', 'wind_speed', 'precip', 'wind_chill']])
        st.write(f'Average Temperature: {avg_temp: .2f} C')

        # Weather Alerts
        alerts = []
        if (df['temp'] > THRESHOLDS['high_temp']).any():
            alerts.append(f'High Temperature: {df['temp'].max():.2f}')
        if (df['temp'] < THRESHOLDS['low_temp']).any():
            alerts.append(f'Low Temperature: {df['temp'].min():.2f}')
        if (df['precip'] > THRESHOLDS['high_precip']).any():
            alerts.append(f'High Precipitation: {df['precip'].max():.2f} mm')
        if (df['wind_speed'] > THRESHOLDS['high_wind']).any():
            alerts.append(f'High Wind Speed: {df["wind_speed"].max():.2f} m/s')
        if alerts:
            for alert in alerts:
                if 'High Temperature' in alert or 'High Precipitation' in alert:
                    st.error(alert)
                else:
                    st.warning(alert)
        else:
            st.success("No extreme weather conditions.")
        try:
            with open('data/alerts.txt', 'w') as f:
                if alerts:
                    f.write('\n'.join(alerts))
                else:
                    f.write('No alerts found.')
        except Exception as e:
            st.warning(f"Alerts not saved to file: {str(e)}")

        # descriptive graphs displaying various data (usually Time and Date vs *variable*)
        plt.figure(figsize=(10,6))
        sns.lineplot(x='date', y='temp', data=df, label='Temperature (C)')
        sns.lineplot(x='date', y='wind_chill', data=df, label='Wind Chill (C)')
        plt.xlabel('Date')
        plt.ylabel('Temperature (C)')
        plt.title('3-Day Temperature vs. Wind Chill')
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(plt.gcf())
        plt.savefig('data/temp_plot.png')
        plt.clf()

        plt.figure(figsize=(10,6))
        sns.barplot(x='date', y='precip', data=df)
        plt.xlabel('Date')
        plt.ylabel('Precipitation (mm)')
        plt.title('3-Day Precipitation')
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(plt.gcf())
        plt.savefig('data/precip_plot.png')
        plt.clf()


    except ValueError:
        st.error('Please enter a valid latitude and longitude.')
    except Exception as e:
        st.error(f'Unexpected error: {str(e)}')


