import reflex as rx

from code_jam_jazzy_jacarandas_2025.components.layout import base_layout
from code_jam_jazzy_jacarandas_2025.sliders import CountrySlider
from code_jam_jazzy_jacarandas_2025.states import FetcherState


@rx.page("/", on_load=FetcherState.fetch_weather_data)
def index() -> rx.Component:
    """Render the main page component.

    Displays temperature data visualizations once loaded.
    Shows a loading spinner and message while data is being fetched.
    """
    content = rx.vstack(
        CountrySlider.new(width="40vw", margin_bottom="2"),
        rx.cond(
            FetcherState.loaded,
            rx.vstack(
                rx.plotly(
                    data=FetcherState.fig,
                    height="40vh",
                    width="40vw",
                ),
                rx.center(
                    rx.plotly(
                        data=FetcherState.fig_pie_all,
                        height="55vh",
                        width="40vw",
                    ),
                ),
                align_items="center",
            ),
            rx.vstack(
                rx.text("Loading data...", font_size="5"),
                rx.spinner(),
                align_items="center",
            ),
        ),
        spacing="1",
        align_items="center",
    )
    center = rx.center(content, height="100vh", width="100vw")
    return base_layout(center)
