import reflex as rx

from code_jam_jazzy_jacarandas_2025.components.developer_box import developer_box
from code_jam_jazzy_jacarandas_2025.components.layout import base_layout
from code_jam_jazzy_jacarandas_2025.humans.developer_list import developers


@rx.page("/about")
def about() -> rx.Component:
    """Render the about page."""
    dev_boxes = [developer_box(**dev) for dev in developers]
    content = rx.center(
        rx.vstack(
            rx.text("About this app:", size="5"),
            rx.text("This app provides weather data visualizations.", size="3"),
            rx.text("About the Jazzy Jacarandas:", size="5"),
            *dev_boxes,
            spacing="2",
        ),
        height="100vh",
        width="100vw",
        overflow="auto",
    )
    return base_layout(content)
