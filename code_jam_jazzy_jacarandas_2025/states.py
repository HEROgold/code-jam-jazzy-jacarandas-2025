from __future__ import annotations

import random
import struct
from typing import TYPE_CHECKING, TypedDict

import numpy as np
import openmeteo_requests
import pandas as pd
import plotly.graph_objects as go
import reflex as rx
import requests_cache
from openmeteo_sdk.VariableWithValues import VariableWithValues
from retry_requests import retry

from code_jam_jazzy_jacarandas_2025.logger import app_log
from code_jam_jazzy_jacarandas_2025.settings import FetcherSettings, Settings

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
    precipitation: ndarray
    wind_speed_10m: ndarray


class FetcherState(rx.State):
    """Store plotly charts once fetched."""

    ohcl_temp_chart: go.Figure = go.Figure()
    pie_temp_chart: go.Figure = go.Figure()
    rain_radar_chart: go.Figure = go.Figure()
    wind_speed_chart: go.Figure = go.Figure()

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

    def get_hourly_data(
        self, response: WeatherApiResponse
    ) -> None | tuple[VariablesWithTime, list[VariableWithValues]]:
        """Process hourly data. The order of variables needs to be the same as requested."""
        hourly = response.Hourly()
        if hourly is None:
            return None

        variables = self._extract_hourly_variables(hourly)

        return (hourly, variables) if variables else None

    def _extract_hourly_variables(self, hourly: VariablesWithTime) -> list[VariableWithValues]:
        variables: list[VariableWithValues] = []
        i = 0
        while True:
            try:
                hourly_var = hourly.Variables(i)
                if hourly_var is None:
                    break
                variables.append(hourly_var)
                i += 1
            except struct.error:
                # API buffer issues - stop collecting variables
                break
        return variables

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
            hourly, hourly_variables = data
        else:
            return None

        date_range = pd.date_range(
            start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
            end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=hourly.Interval()),
            inclusive="left",
        )

        if len(hourly_variables) < 1:
            return None

        hourly_data: dict[str, pd.DatetimeIndex | np.ndarray] = {
            "date": date_range,
            "temperature_2m": hourly_variables[0].ValuesAsNumpy(),
        }

        self._add_precipitation(hourly_variables, date_range, hourly_data)
        self._add_wind_speed(hourly_variables, date_range, hourly_data)

        hourly_dataframe = pd.DataFrame(data=hourly_data)
        hourly_dataframe["date"] = pd.to_datetime(hourly_dataframe["date"])

        return hourly_dataframe

    def _add_wind_speed(
        self,
        hourly_variables: list[VariableWithValues],
        date_range: pd.DatetimeIndex,
        hourly_data: dict[str, pd.DatetimeIndex | np.ndarray],
    ) -> None:
        if len(hourly_variables) > 2:  # noqa: PLR2004
            try:
                hourly_data["wind_speed_10m"] = hourly_variables[2].ValuesAsNumpy()
            except struct.error:
                hourly_data["wind_speed_10m"] = np.zeros(len(date_range))
        else:
            hourly_data["wind_speed_10m"] = np.zeros(len(date_range))

    def _add_precipitation(
        self,
        hourly_variables: list[VariableWithValues],
        date_range: pd.DatetimeIndex,
        hourly_data: dict[str, pd.DatetimeIndex | np.ndarray],
    ) -> None:
        if len(hourly_variables) > 1:
            try:
                hourly_data["precipitation"] = hourly_variables[1].ValuesAsNumpy()
            except struct.error:
                hourly_data["precipitation"] = np.zeros(len(date_range))
        else:
            hourly_data["precipitation"] = np.zeros(len(date_range))

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
        self.ohcl_temp_chart = create_candlestick_chart(df_ohlc)
        self.pie_temp_chart = create_pie_chart(df_ohlc)
        self.rain_radar_chart = create_rain_radar_chart(hourly_dataframe)
        self.wind_speed_chart = create_wind_spiral_chart(hourly_dataframe)

        self.loaded = True
