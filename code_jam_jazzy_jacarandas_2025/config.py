"""Passthrough config module to setup confkit when it's used."""

from configparser import ConfigParser
from pathlib import Path

from confkit import Config

file = Path("config.ini")
parser = ConfigParser()
Config.set_file(file)
Config.set_parser(parser)
