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
        CountrySlider.new(width="80vw", margin_bottom="2"),
        rx.cond(
            FetcherState.loaded,
            rx.grid(
                rx.plotly(data=FetcherState.ohcl_temp_chart),
                rx.plotly(data=FetcherState.pie_temp_chart),
                rx.plotly(data=FetcherState.rain_radar_chart),
                rx.plotly(data=FetcherState.wind_speed_chart),
                columns="repeat(2, 1fr)",
                rows="repeat(2, auto)",
                gap=4,
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
