
from configparser import ConfigParser
from pathlib import Path

import reflex as rx
from confkit import Config, Enum
from rxconfig import config

file = Path("config.ini")
parser = ConfigParser()
Config.set_file(file)
Config.set_parser(parser)


class Settings:
    """Application settings."""

    app_name = Config(config.app_name)
    log_level = Config(Enum(rx.constants.LogLevel.DEFAULT))


settings = Settings()
