import reflex as rx


def navbar_button_format(name: str, redirect: rx.event.EventSpec) -> rx.Component:
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

def logo() -> rx.Component:
    """Render logo"""
    return rx.image(src="/jazzy_jacarandas_logo.png", width="100px", height="auto")


def navbar() -> rx.Component:
    """Render navigation bar with all buttons."""
    # to add a new button just put it in the hstack
    return rx.box(
        rx.box(
            # Logo pinned to the top-left
            logo(),
            position="absolute", # Ensures that logo is in line with other navbar buttons
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
        style={"fontFamily": "Comic Sans MS, Comic Sans, cursive"},
    )
