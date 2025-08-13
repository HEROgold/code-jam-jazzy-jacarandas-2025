"""Welcome to Reflex! This file outlines the steps to create a basic app."""

import reflex as rx

# Import all pages so they're registered and functional.
from .pages import *  # noqa: F403

app = rx.App()
