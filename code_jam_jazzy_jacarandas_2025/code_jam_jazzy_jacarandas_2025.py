"""Welcome to Reflex! This file outlines the steps to create a basic app."""

import reflex as rx

from rxconfig import config
import plotly.graph_objects as go


import openmeteo_requests # Line 9-51 copied from https://open-meteo.com

import pandas as pd
import requests_cache
from retry_requests import retry

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

# Make sure all required weather variables are listed here
# The order of variables in hourly or daily is important to assign them correctly below
url = "https://api.open-meteo.com/v1/forecast"
params = {
	"latitude": 51.5085,
	"longitude": -0.1257,
	"hourly": "temperature_2m",
	"timezone": "auto",
    "forecast_days": 16,
}
responses = openmeteo.weather_api(url, params=params)

# Process first location. Add a for-loop for multiple locations or weather models
response = responses[0]
print(f"Coordinates: {response.Latitude()}°N {response.Longitude()}°E")
print(f"Elevation: {response.Elevation()} m asl")
print(f"Timezone: {response.Timezone()}{response.TimezoneAbbreviation()}")
print(f"Timezone difference to GMT+0: {response.UtcOffsetSeconds()}s")

# Process hourly data. The order of variables needs to be the same as requested.
hourly = response.Hourly()
hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()

hourly_data = {"date": pd.date_range(
	start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
	end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
	freq = pd.Timedelta(seconds = hourly.Interval()),
	inclusive = "left"
)}

hourly_data["temperature_2m"] = hourly_temperature_2m

hourly_dataframe = pd.DataFrame(data = hourly_data)

hourly_dataframe["date"] = pd.to_datetime(hourly_dataframe["date"])

df_ohlc = hourly_dataframe.set_index("date")["temperature_2m"].resample("D").agg(["first", "max", "min", "last"]).dropna()
df_ohlc = df_ohlc.rename(columns={"first": "Open", "max": "High", "min": "Low", "last": "Close"})
df_ohlc.reset_index(inplace=True)

fig = go.Figure(
    data=[
        go.Candlestick(
            x=df_ohlc["date"],
            open=df_ohlc["Open"],
            high=df_ohlc["High"],
            low=df_ohlc["Low"],
            close=df_ohlc["Close"],
        )
    ]
)

fig.update_layout(
    title="Daily Temperature OHLC (°C) in London",
    xaxis_rangeslider_visible=False,
    yaxis_title="Temperature (°C)"
)


#df = df.tail(100) # Input has many rows, only need a few

#fig = go.Figure(data=[go.Candlestick(x=df['Date'],
                #open=df['AAPL.Open'],
                #high=df['AAPL.High'],
                #low=df['AAPL.Low'],
                #close=df['AAPL.Close'])])


class State(rx.State):
    """The app state."""


def index() -> rx.Component:
    # Welcome Page (Index)
    return rx.center(
        rx.plotly(
            data=fig,
            height = "100%",
            width = "20vw"
            )

    )


app = rx.App()
app.add_page(index)
