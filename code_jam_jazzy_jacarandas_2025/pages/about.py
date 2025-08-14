import reflex as rx

from code_jam_jazzy_jacarandas_2025.components.developer_box import developer_box
from code_jam_jazzy_jacarandas_2025.components.layout import base_layout


@rx.page("/about")
def about() -> rx.Component:
    """Render the about page."""
    content = rx.center(
        rx.vstack(
            rx.text("About This App", size="5"),
            rx.text("This app provides weather data visualizations.", size="3"),
            developer_box("Andre Binbow", "Test test 123", "https://github.com/AndreBinbow"),
            spacing="2",
        ),
        height="100vh",
        width="100vw",
    )
    return base_layout(content)
