"""Welcome to Reflex! This file outlines the steps to create a basic app."""

import openmeteo_requests
import pandas as pd
import plotly.graph_objects as go
import reflex as rx
import requests_cache
from retry_requests import retry


class FetcherState(rx.State):
    """Store plotly charts once fetched."""

    fig: go.Figure = go.Figure()
    fig_pie_all: go.Figure = go.Figure()
    loaded: bool = False

    def fetch_weather_data(
        self,
    ) -> None:  # Majority of data fetching logic is copied from https://open-meteo.com/en/docs
        """Fetch data about temperatures from the Open-meteo free API."""
        self.loaded = False

        # Setup the Open-Meteo API client with cache and retry on error
        cache_session = requests_cache.CachedSession(".cache", expire_after=3600)
        retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
        openmeteo = openmeteo_requests.Client(session=retry_session)

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

        # Process hourly data. The order of variables needs to be the same as requested.
        hourly = response.Hourly()
        hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()

        hourly_data = {
            "date": pd.date_range(
                start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
                end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
                freq=pd.Timedelta(seconds=hourly.Interval()),
                inclusive="left",
            ),
        }

        hourly_data["temperature_2m"] = hourly_temperature_2m

        hourly_dataframe = pd.DataFrame(data=hourly_data)

        hourly_dataframe["date"] = pd.to_datetime(hourly_dataframe["date"])

        df_ohlc = (
            hourly_dataframe.set_index("date")["temperature_2m"]
            .resample("D")
            .agg(["first", "max", "min", "last"])
            .dropna()
        )

        df_ohlc = (
            df_ohlc.rename(columns={"first": "Open", "max": "High", "min": "Low", "last": "Close"})  # OHLC conversion
        )
        df_ohlc = df_ohlc.reset_index()

        # Truncate all numeric columns to 2 decimal places
        df_ohlc = df_ohlc.round(2)

        fig = go.Figure(
            data=[
                go.Candlestick(
                    x=df_ohlc["date"],
                    open=df_ohlc["Open"],
                    high=df_ohlc["High"],
                    low=df_ohlc["Low"],
                    close=df_ohlc["Close"],
                ),
            ],
        )

        fig.update_layout(
            title={
                "text": "Daily Temperature OHLC (°C) in London",
                "x": 0.5,
            },
            xaxis_rangeslider_visible=False,
            yaxis_title="Temperature (°C)",
            font={
                "family": "Comic Sans MS, Comic Sans, cursive",
                "size": 14,
            },
        )

        labels = df_ohlc["date"].dt.strftime("%b %d")
        values = df_ohlc["High"]

        fig_pie_all = go.Figure(
            data=[
                go.Pie(
                    labels=labels,
                    values=values,
                    hovertemplate="%{label}<br>%{value:.2f}°C<extra></extra>",  # Tags needed to remove text box
                )
            ],
        )

        fig_pie_all.update_layout(
            title={
                "text": "Daily Highest Temperatures in London",
                "x": 0.5,
                "xanchor": "center",
                "font": {
                    "family": "Comic Sans MS, Comic Sans, cursive",
                    "size": 24,
                },
            },
            font={
                "family": "Comic Sans MS, Comic Sans, cursive",
                "size": 12,
            },
        )

        self.fig = fig
        self.fig_pie_all = fig_pie_all
        self.loaded = True


@rx.page(on_load=FetcherState.fetch_weather_data)
def index() -> rx.Component:
    """Render the main page component.

    Displays temperature data visualizations once loaded.
    Shows a loading spinner and message while data is being fetched.
    """
    content = rx.vstack(
        rx.cond(
            FetcherState.loaded,
            rx.vstack(
                rx.plotly(
                    data=FetcherState.fig,
                    height="40vh",
                    width="40vw",
                ),
                rx.center(
                    rx.plotly(
                        data=FetcherState.fig_pie_all,
                        height="55vh",
                        width="20vw",
                    ),
                ),
                align_items="center",
            ),
            rx.vstack(
                rx.text("Loading data...", font_size="5"),
                rx.spinner(),
                align_items="center",
            ),
        ),
        spacing="3",
        align_items="center",
    )
    return rx.center(content, height="100vh", width="100vw")


app = rx.App()
