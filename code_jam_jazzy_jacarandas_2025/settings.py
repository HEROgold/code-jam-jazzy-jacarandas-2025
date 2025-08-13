import reflex as rx
from confkit import Enum
from rxconfig import config

from code_jam_jazzy_jacarandas_2025.config import Config


class Settings:
    """Application settings."""

    app_name = Config(config.app_name)
    log_level = Config(Enum(rx.constants.LogLevel.DEFAULT))
