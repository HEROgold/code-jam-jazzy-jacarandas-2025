import reflex as rx
from code_jam_jazzy_jacarandas_2025.components.header import header

@rx.page("/about")
def about() -> rx.Component:
    """Render the about page."""
    return rx.center(
        rx.vstack(
            header(),
            rx.text("About This App", font_size="5"),
            rx.text("This app provides weather data visualizations.", font_size="3"),
            spacing="2",
        ),
        height="100vh",
        width="100vw",
    )
