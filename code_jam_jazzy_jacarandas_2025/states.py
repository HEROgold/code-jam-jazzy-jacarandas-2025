from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict

import openmeteo_requests
import pandas as pd
import plotly.graph_objects as go
import reflex as rx
import requests_cache
from retry_requests import retry

from code_jam_jazzy_jacarandas_2025.logger import app_log
from code_jam_jazzy_jacarandas_2025.settings import FetcherSettings

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

    def _get_api_params(self) -> dict[str, str | float | int]:
        """Get API parameters for weather data request."""
        return {
            "latitude": FetcherSettings.latitude,
            "longitude": FetcherSettings.longitude,
            "hourly": FetcherSettings.hourly,
            "timezone": FetcherSettings.timezone,
            "forecast_days": FetcherSettings.forecast_days,
        }

    def _fetch_api_data(self) -> WeatherApiResponse | None:
        """Fetch raw weather data from Open-meteo API."""
        openmeteo = self._get_session()
        params = self._get_api_params()

        return openmeteo.weather_api(FetcherSettings.api_url, params=params)[0]

    def _process_hourly_data(self, response: WeatherApiResponse) -> pd.DataFrame | None:
        """Process hourly weather data into a DataFrame."""
        if data := self.get_hourly_data(response):
            hourly, hourly_temperature_2m = data
        else:
            return None  # warnings are logged in get_hourly_data

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

        return hourly_dataframe

    def _create_ohlc_dataframe(self, hourly_dataframe: pd.DataFrame) -> pd.DataFrame:
        """Convert hourly data to OHLC (Open, High, Low, Close) format."""
        df_ohlc = (
            hourly_dataframe.set_index("date")["temperature_2m"]
            .resample("D")
            .agg(["first", "max", "min", "last"])
            .dropna()
        )

        return (
            df_ohlc.rename(columns={"first": "Open", "max": "High", "min": "Low", "last": "Close"})  # type: ignore[reportCallIssue]
            .reset_index()
            .round(2)
        )

    def _create_candlestick_chart(self, df_ohlc: pd.DataFrame) -> go.Figure:
        """Create candlestick chart from OHLC data."""
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
                "text": f"Daily Temperature OHLC (°C) in {FetcherSettings.country_name}",
                "x": 0.5,
            },
            xaxis_rangeslider_visible=False,
            yaxis_title="Temperature (°C)",
            font={
                "family": "Comic Sans MS, Comic Sans, cursive",
                "size": 14,
            },
        )

        return fig

    def _create_pie_chart(self, df_ohlc: pd.DataFrame) -> go.Figure:
        """Create pie chart showing daily highest temperatures."""
        labels = df_ohlc["date"].dt.strftime("%b %d")
        values = df_ohlc["High"]

        fig_pie_all = go.Figure(
            data=[
                go.Pie(
                    labels=labels,
                    values=values,
                    hovertemplate="%{label}<br>%{value:.2f}°C<extra></extra>",
                )
            ],
        )

        fig_pie_all.update_layout(
            title={
                "text": f"Daily Highest Temperatures in {FetcherSettings.country_name}",
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

        return fig_pie_all

    @rx.event
    def fetch_weather_data(self) -> None:
        """Fetch data about temperatures from the Open-meteo free API."""
        self.loaded = False

        # Fetch raw data from API
        response = self._fetch_api_data()
        if not response:
            return

        # Process hourly data
        hourly_dataframe = self._process_hourly_data(response)
        if hourly_dataframe is None:
            return

        # Create OHLC dataframe
        df_ohlc = self._create_ohlc_dataframe(hourly_dataframe)

        # Create charts
        self.fig = self._create_candlestick_chart(df_ohlc)
        self.fig_pie_all = self._create_pie_chart(df_ohlc)

        self.loaded = True
