from collections.abc import Callable

import reflex as rx

from code_jam_jazzy_jacarandas_2025.settings import Settings


def navbar_button_format(name: str, redirect: Callable[[], rx.event.EventSpec]) -> rx.Component:
    """Style navigation button."""
    return rx.button(
        name,
        on_click=redirect,
        padding="0.6rem 1.2rem",
        border_radius="xl",
        background="linear-gradient(to right, #4b4b4b, #2c2c2c)",  # dark gray gradient
        color="white",
        font_weight="semibold",
        box_shadow="sm",
        _hover={
            "background": "linear-gradient(to right, #606060, #3a3a3a)",
            "transform": "scale(1.05)",
            "transition": "0.2s",
        },
    )


def redirect_to_about() -> rx.event.EventSpec:
    """Redirect to the about page."""
    return rx.redirect("/about")


def about_button() -> rx.Component:
    """Render the about button."""
    return navbar_button_format("About", redirect_to_about)


def redirect_to_index() -> rx.event.EventSpec:
    """Redirect to the home page."""
    return rx.redirect("/")


def home_button() -> rx.Component:
    """Render the home button."""
    return navbar_button_format("Home", redirect_to_index)


def jazzy_jacarandas_logo_component() -> rx.Component:
    """Render 'Jazzy Jacarandas' logo."""
    return rx.image(src="/jazzy_jacarandas_logo.png", width="100px", height="auto")


def the_forecast_strikes_back_component() -> rx.Component:
    """Render 'The Forecast Strikes Back' logo."""
    return rx.image(src="/the_forecast_strikes_back_logo.png", width="100px", height="auto")


def navbar() -> rx.Component:
    """Render navigation bar with all buttons."""
    # to add a new button just put it in the hstack
    return rx.box(
        rx.box(
            the_forecast_strikes_back_component(),
            position="absolute",  # Ensures that logo is in line with other navbar buttons
        ),
        rx.box(
            jazzy_jacarandas_logo_component(),
            position="absolute",  # Ensures that logo is in line with other navbar buttons
            right="1rem",
        ),
        rx.hstack(
            home_button(),
            about_button(),
            spacing="4",
            align_items="center",
            justify_content="center",  # center buttons horizontally
            width="100%",
        ),
        width="100%",
        padding="0.75rem 1rem",
        background="linear-gradient(to bottom, #222222, #121212)",
        box_shadow="md",
        position="sticky",
        top="0",
        z_index="1000",
        style={"fontFamily": Settings.font_family},
    )
