import reflex as rx

from code_jam_jazzy_jacarandas_2025.components.navbar import navbar


def header() -> rx.Component:
    """Render the header component."""
    return rx.center(rx.vstack(navbar()))
