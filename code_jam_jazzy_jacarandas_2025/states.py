from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict

import openmeteo_requests
import pandas as pd
import plotly.graph_objects as go
import reflex as rx
import requests_cache
from retry_requests import retry

from code_jam_jazzy_jacarandas_2025.config import Config
from code_jam_jazzy_jacarandas_2025.logger import app_log

if TYPE_CHECKING:
    from logging import Logger

    from numpy import ndarray
    from openmeteo_sdk.VariablesWithTime import VariablesWithTime
    from openmeteo_sdk.VariableWithValues import VariableWithValues
    from openmeteo_sdk.WeatherApiResponse import WeatherApiResponse


class HourlyData(TypedDict):
    """TypedDict for hourly weather data dictionary."""

    date: pd.DatetimeIndex
    temperature_2m: ndarray


class FetcherSettings:
    """Configuration for fetching weather data."""

    latitude = Config(51.5085)
    longitude = Config(-0.1257)
    hourly = Config("temperature_2m")
    timezone = Config("auto")
    forecast_days = Config(16)


class FetcherState(rx.State):
    """Store plotly charts once fetched."""

    fig: go.Figure = go.Figure()
    fig_pie_all: go.Figure = go.Figure()
    loaded: bool = False

    # This avoids the unserializable state issue.
    @property
    def log(self) -> Logger:
        """Get logger for FetcherState."""
        return app_log.getChild("FetcherState")

    def _get_session(self) -> openmeteo_requests.Client:
        cache_session = requests_cache.CachedSession(".cache", expire_after=3600)
        retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
        # retry() returns our cache_session
        return openmeteo_requests.Client(session=retry_session)  # type: ignore[reportArgumentType]

    def get_hourly_data(self, response: WeatherApiResponse) -> None | tuple[VariablesWithTime, VariableWithValues]:
        """Process hourly data. The order of variables needs to be the same as requested."""
        hourly = response.Hourly()
        if hourly is None:
            self.log.warning("No hourly data found")
            return None

        hourly_var = hourly.Variables(0)
        if hourly_var is None:
            self.log.warning("No hourly variables found")
            return None

        return hourly, hourly_var

    def fetch_weather_data(
        self,
    ) -> None:  # Majority of data fetching logic is copied from https://open-meteo.com/en/docs
        """Fetch data about temperatures from the Open-meteo free API."""
        self.loaded = False

        openmeteo = self._get_session()

        # Make sure all required weather variables are listed here
        # The order of variables in hourly or daily is important to assign them correctly below
        url = "https://api.open-meteo.com/v1/forecast"
        params: dict[str, str | float | int] = {
            "latitude": FetcherSettings.latitude,
            "longitude": FetcherSettings.longitude,
            "hourly": FetcherSettings.hourly,
            "timezone": FetcherSettings.timezone,
            "forecast_days": FetcherSettings.forecast_days,
        }
        responses = openmeteo.weather_api(url, params=params)

        # Process first location. Add a for-loop for multiple locations or weather models
        response = responses[0]

        if data := self.get_hourly_data(response):
            hourly, hourly_temperature_2m = data
        else:
            return  # return > warnings are logged in get_hourly_data

        date_range = pd.date_range(
            start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
            end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=hourly.Interval()),
            inclusive="left",
        )

        hourly_data: HourlyData = {
            "date": date_range,
            "temperature_2m": hourly_temperature_2m.ValuesAsNumpy(),
        }

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
