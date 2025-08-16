import reflex as rx

from code_jam_jazzy_jacarandas_2025.components.developer_box import developer_box
from code_jam_jazzy_jacarandas_2025.components.layout import base_layout
from code_jam_jazzy_jacarandas_2025.humans.developer_list import developers
from code_jam_jazzy_jacarandas_2025.settings import Settings

# Named "humans" because the other various files named "config" cause funny errors if folder is called "config"


@rx.page("/about")
def about() -> rx.Component:
    """Render the about page."""
    dev_boxes = [developer_box(**dev) for dev in developers]
    content = rx.center(
        rx.vstack(
            rx.text("About this app:", size="5", font_family=Settings.font_family),
            get_app_description(),
            rx.text("About the Jazzy Jacarandas:", size="5", font_family=Settings.font_family),
            *dev_boxes,
            spacing="2",
        ),
        height="100vh",
        width="100vw",
        overflow="auto",
    )
    return base_layout(content)


def get_app_description():
    return rx.html(
        "<br>"
        "This app displays weather data for selected locations using graphs that are completely "
        "inappropriate for weather visualization.<br>"
        "Created for the 2025 Python Code Jam with the theme 'wrong tool for the job' - "
        "because why use a sensible chart?"
        "<br><br>",
        font_size="var(--font-size-3)",
        font_family=Settings.font_family,
    )
