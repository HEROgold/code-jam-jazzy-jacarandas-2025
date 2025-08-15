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

    fig: go.Figure = go.Figure()
    fig_pie_all: go.Figure = go.Figure()
    rain: go.Figure = go.Figure()
    wind_speed: go.Figure = go.Figure()

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
                "family": Settings.font_family,
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
                    "family": Settings.font_family,
                    "size": 24,
                },
            },
            font={
                "family": Settings.font_family,
                "size": 12,
            },
        )

        return fig_pie_all

    def _create_rain_radar_chart(self, hourly_dataframe: pd.DataFrame) -> go.Figure:
        """Create a creative radar chart for precipitation data."""
        if "precipitation" in hourly_dataframe.columns and hourly_dataframe["precipitation"].sum() > 0:
            # Use real precipitation data if available
            hourly_dataframe["hour"] = hourly_dataframe["date"].dt.hour
            rain_by_hour = hourly_dataframe.groupby("hour")["precipitation"].mean().reset_index()
        else:
            # Create creative fake precipitation data based on temperature variations
            # This is intentionally "improper" as requested - using temperature to fake rain patterns
            rain_by_hour = self._generate_fake_rain_data(hourly_dataframe)

        # Create 24-hour labels
        hours = list(range(24))
        rain_values: list[float] = []

        for hour in hours:
            value = rain_by_hour[rain_by_hour["hour"] == hour]["precipitation"]
            rain_values.append(float(value.iloc[0]) if len(value) > 0 else 0.0)

        # Add first value at the end to close the radar chart
        rain_values.append(rain_values[0])
        hour_labels = [f"{h:02d}:00" for h in hours] + [f"{hours[0]:02d}:00"]

        fig_rain = go.Figure()

        # Add radar trace
        fig_rain.add_trace(
            go.Scatterpolar(
                r=rain_values,
                theta=hour_labels,
                fill="toself",
                fillcolor="rgba(54, 162, 235, 0.3)",
                line={"color": "rgba(54, 162, 235, 1)", "width": 3},
                marker={"size": 8, "color": "rgba(54, 162, 235, 1)"},
                name="Precipitation",
                hovertemplate="%{theta}<br>%{r:.2f} mm<extra></extra>",
            )
        )

        max_rain = max(rain_values) if rain_values else 1
        fig_rain.update_layout(
            polar={
                "radialaxis": {
                    "visible": True,
                    "range": [0, max_rain * 1.1] if max_rain > 0 else [0, 1],
                    "tickfont": {"size": 10},
                },
                "angularaxis": {"tickfont": {"size": 12}, "rotation": 90, "direction": "clockwise"},
            },
            title={
                "text": f"24-Hour Precipitation Radar in {FetcherSettings.country_name}",
                "x": 0.5,
                "xanchor": "center",
                "font": {
                    "family": Settings.font_family,
                    "size": 20,
                },
            },
            font={
                "family": Settings.font_family,
                "size": 12,
            },
            showlegend=False,
        )

        return fig_rain

    def _generate_fake_rain_data(self, hourly_dataframe: pd.DataFrame) -> pd.DataFrame:
        hourly_dataframe["hour"] = hourly_dataframe["date"].dt.hour
        temp_by_hour = hourly_dataframe.groupby("hour")["temperature_2m"].mean().reset_index()

        # Convert temperature variations to fake "rain intensity"
        # Lower temperatures = higher chance of rain (very simplified model)
        min_temp = temp_by_hour["temperature_2m"].min()
        max_temp = temp_by_hour["temperature_2m"].max()
        temp_range = max_temp - min_temp if max_temp != min_temp else 1

        # Invert temperature (lower temp = more rain) and add some randomness
        rng = np.random.default_rng(42)  # Fixed seed for consistency
        fake_rain = []
        for temp in temp_by_hour["temperature_2m"]:
            # Normalize and invert: colder temps get higher values
            normalized = 1 - ((temp - min_temp) / temp_range)
            # Scale to reasonable precipitation values (0-5mm)
            rain_value = normalized * 5 + rng.uniform(0, 1)
            fake_rain.append(max(0, rain_value))

        return pd.DataFrame({"hour": temp_by_hour["hour"], "precipitation": fake_rain})

    def _create_wind_spiral_chart(self, hourly_dataframe: pd.DataFrame) -> go.Figure:
        """Create a creative wind speed chart organized by date coordinates."""
        # Check if we have real wind speed data or need to create fake data
        if "wind_speed_10m" in hourly_dataframe.columns and hourly_dataframe["wind_speed_10m"].sum() > 0:
            # Use real wind speed data if available
            hourly_dataframe["day"] = hourly_dataframe["date"].dt.date
            daily_wind = hourly_dataframe.groupby("day")["wind_speed_10m"].mean().reset_index()
        else:
            # Create creative fake wind speed data based on temperature variations
            # This is intentionally "improper" - using temperature swings to fake wind patterns
            daily_wind = self._generate_fake_wind_data(hourly_dataframe)

        if len(daily_wind) == 0:
            return go.Figure()

        # Setup the seed for random, ensuring reproducibility
        seed = int(abs(FetcherSettings.latitude + FetcherSettings.longitude))
        random.seed(seed)
        rng = np.random.default_rng(seed)

        # Create organized coordinates based on dates
        # X-axis represents day of forecast (0 to n)
        # Y-axis represents wind speed scaled
        # This creates a more organized visualization than the spiral
        daily_wind = daily_wind.sort_values("day").reset_index(drop=True)
        wind_speeds = daily_wind["wind_speed_10m"].tolist()
        x_coords = list(range(len(daily_wind)))  # Day index (0, 1, 2, ...)
        y_coords = list(random.choices(wind_speeds, k=len(daily_wind)))  # noqa: S311

        # Add random deviation of 25% to x and y coordinates for more natural data visualization
        x_deviation = rng.uniform(-0.25, 0.25, len(x_coords))  # 25% deviation
        y_deviation = rng.uniform(-0.25, 0.25, len(y_coords))  # 25% deviation

        # Apply deviation - multiply by original values to maintain scale
        x_coords = [x * (1 + dev) for x, dev in zip(x_coords, x_deviation, strict=False)]
        y_coords = [y * (1 + dev) for y, dev in zip(y_coords, y_deviation, strict=False)]

        # Create color scale based on wind speed
        colors = daily_wind["wind_speed_10m"].tolist()
        dates = [str(d) for d in daily_wind["day"]]

        # Create size based on wind speed for visual emphasis
        sizes = [max(8, min(20, speed * 1.5)) for speed in wind_speeds]

        fig_wind = go.Figure()

        # Add organized scatter plot
        fig_wind.add_trace(
            go.Scatter(
                x=x_coords,
                y=y_coords,
                mode="markers+lines",
                marker={
                    "size": sizes,
                    "color": colors,
                    "colorscale": "Viridis",
                    "showscale": True,
                    "colorbar": {
                        "title": "Wind Speed (km/h)",
                    },
                    "line": {"width": 1, "color": "DarkSlateGrey"},
                },
                line={"width": 2, "color": "rgba(100, 100, 100, 0.5)"},
                text=dates,
                customdata=wind_speeds,
                hovertemplate="Date: %{text}<br>Wind Speed: %{customdata:.1f} km/h<br>Day: %{x}<extra></extra>",
                name="Wind Speed Journey",
            )
        )

        fig_wind.update_layout(
            title={
                "text": (
                    f"Wind Speed Timeline in {FetcherSettings.country_name}<br>"
                    "<sub>X-axis: Days from start, Y-axis: Wind Speed (km/h)</sub>"
                ),
                "x": 0.5,
                "xanchor": "center",
                "font": {
                    "family": Settings.font_family,
                    "size": 18,
                },
            },
            xaxis={"showgrid": True, "zeroline": False, "title": "Days from Start"},
            yaxis={"showgrid": True, "zeroline": False, "title": "Wind Speed (km/h)"},
            font={
                "family": Settings.font_family,
                "size": 12,
            },
            showlegend=False,
            plot_bgcolor="rgba(245,245,245,0.8)",
        )

        return fig_wind

    def _generate_fake_wind_data(self, hourly_dataframe: pd.DataFrame) -> pd.DataFrame:
        hourly_dataframe["day"] = hourly_dataframe["date"].dt.date
        daily_temp = hourly_dataframe.groupby("day")["temperature_2m"].agg(["mean", "std"]).reset_index()
        daily_temp.columns = ["day", "temp_mean", "temp_std"]

        # Convert temperature variation to fake wind speed
        # Higher temperature variation = more wind (oversimplified model)
        rng = np.random.default_rng(42)  # Fixed seed for consistency
        fake_wind = []
        for _, row in daily_temp.iterrows():
            # Use temperature standard deviation as base for wind speed
            wind_base = row["temp_std"] * 3 if not pd.isna(row["temp_std"]) else 5
            # Add some randomness and ensure reasonable wind speeds (0-25 km/h)
            wind_speed = max(0, min(25, wind_base + rng.uniform(-3, 8)))
            fake_wind.append(wind_speed)

        return pd.DataFrame({"day": daily_temp["day"], "wind_speed_10m": fake_wind})

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
        self.rain = self._create_rain_radar_chart(hourly_dataframe)
        self.wind_speed = self._create_wind_spiral_chart(hourly_dataframe)

        self.loaded = True
