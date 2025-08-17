import reflex as rx
from confkit import Enum
from rxconfig import config

from code_jam_jazzy_jacarandas_2025.config import Config


class Settings:
    """Application settings."""

    app_name = Config(config.app_name)
    log_level = Config(Enum(rx.constants.LogLevel.DEFAULT))
    font_family = Config("Comic Sans MS, Comic Sans, cursive")


class FetcherSettings:
    """Configuration for fetching weather data."""

    latitude = Config(51.5085)
    longitude = Config(-0.1257)
    hourly = Config("temperature_2m,precipitation,rain,showers,wind_speed_10m,wind_direction_10m,wind_gusts_10m")
    timezone = Config("auto")
    forecast_days = Config(16)
    lookback_days = Config(365)
    api_url = Config("https://api.open-meteo.com/v1/forecast")
    archive_api_url = Config("https://archive-api.open-meteo.com/v1/archive")
    country_name = Config("London")
    country_code = Config("GB")
