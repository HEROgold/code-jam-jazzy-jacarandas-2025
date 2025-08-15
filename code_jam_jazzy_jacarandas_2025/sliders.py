from typing import Any, ClassVar

import reflex as rx
from reflex.components.radix.themes.components.slider import Slider
from reflex.components.radix.themes.layout.stack import VStack

from code_jam_jazzy_jacarandas_2025.settings import FetcherSettings
from code_jam_jazzy_jacarandas_2025.states import FetcherState


class CountrySlider(rx.State):
    """A slider for selecting a country."""

    # We trust AI on this information!
    countries: ClassVar[list[tuple[str, str, float, float]]] = [
        ("Afghanistan", "AF", 33.9391, 67.7100),
        ("Albania", "AL", 41.1533, 20.1683),
        ("Algeria", "DZ", 28.0339, 1.6596),
        ("Argentina", "AR", -38.4161, -63.6167),
        ("Australia", "AU", -25.2744, 133.7751),
        ("Austria", "AT", 47.5162, 14.5501),
        ("Bangladesh", "BD", 23.6850, 90.3563),
        ("Belgium", "BE", 50.5039, 4.4699),
        ("Brazil", "BR", -14.2350, -51.9253),
        ("Canada", "CA", 56.1304, -106.3468),
        ("Chile", "CL", -35.6751, -71.5430),
        ("China", "CN", 35.8617, 104.1954),
        ("Colombia", "CO", 4.5709, -74.2973),
        ("Denmark", "DK", 56.2639, 9.5018),
        ("Egypt", "EG", 26.8206, 30.8025),
        ("Finland", "FI", 61.9241, 25.7482),
        ("France", "FR", 46.2276, 2.2137),
        ("Germany", "DE", 51.1657, 10.4515),
        ("Ghana", "GH", 7.9465, -1.0232),
        ("Greece", "GR", 39.0742, 21.8243),
        ("India", "IN", 20.5937, 78.9629),
        ("Indonesia", "ID", -0.7893, 113.9213),
        ("Iran", "IR", 32.4279, 53.6880),
        ("Iraq", "IQ", 33.2232, 43.6793),
        ("Ireland", "IE", 53.4129, -8.2439),
        ("Israel", "IL", 31.0461, 34.8516),
        ("Italy", "IT", 41.8719, 12.5674),
        ("Japan", "JP", 36.2048, 138.2529),
        ("Jordan", "JO", 30.5852, 36.2384),
        ("Kenya", "KE", -0.0236, 37.9062),
        ("Malaysia", "MY", 4.2105, 101.9758),
        ("Mexico", "MX", 23.6345, -102.5528),
        ("Netherlands", "NL", 52.1326, 5.2913),
        ("Nigeria", "NG", 9.0820, 8.6753),
        ("Norway", "NO", 60.4720, 8.4689),
        ("Pakistan", "PK", 30.3753, 69.3451),
        ("Philippines", "PH", 12.8797, 121.7740),
        ("Poland", "PL", 51.9194, 19.1451),
        ("Portugal", "PT", 39.3999, -8.2245),
        ("Russia", "RU", 61.5240, 105.3188),
        ("Saudi Arabia", "SA", 23.8859, 45.0792),
        ("Singapore", "SG", 1.3521, 103.8198),
        ("South Africa", "ZA", -30.5595, 22.9375),
        ("South Korea", "KR", 35.9078, 127.7669),
        ("Spain", "ES", 40.4637, -3.7492),
        ("Sweden", "SE", 60.1282, 18.6435),
        ("Switzerland", "CH", 46.8182, 8.2275),
        ("Thailand", "TH", 15.8700, 100.9925),
        ("Turkey", "TR", 38.9637, 35.2433),
        ("Ukraine", "UA", 48.3794, 31.1656),
        ("United Kingdom", "GB", 55.3781, -3.4360),
        ("United States", "US", 39.8283, -98.5795),
        ("Venezuela", "VE", 6.4238, -66.5897),
        ("Vietnam", "VN", 14.0583, 108.2772),
    ]

    country_index: int = 0

    @rx.event
    def set_country(self, value: list[int | float]) -> None:
        """Set the selected country based on slider value."""
        self.country_index = int(value[0])
        FetcherSettings.country_name = self.countries[self.country_index][0]
        FetcherSettings.country_code = self.countries[self.country_index][1]
        FetcherSettings.latitude = self.countries[self.country_index][2]
        FetcherSettings.longitude = self.countries[self.country_index][3]

    @rx.var
    def selected_country_display(self) -> str:
        """Return a formatted string of the selected country."""
        name, code, _, _ = self.countries[self.country_index]
        return f" ({code}) {name}"

    @staticmethod
    def new(**kw: Any) -> VStack:  # noqa: ANN401
        """Create a new CountrySlider component."""
        return rx.vstack(
            rx.text("Country:"),
            rx.text(f"Selected: {CountrySlider.selected_country_display}"),
            CountrySlider._make_slider(),
            rx.button("Update charts", on_click=FetcherState.fetch_weather_data),
            spacing="2",
            **kw,
        )

    @staticmethod
    def _make_slider() -> Slider:
        return rx.slider(
            min=0,
            max=len(CountrySlider.countries) - 1,
            step=1,
            value=[CountrySlider.country_index],
            on_change=CountrySlider.set_country,
        )
