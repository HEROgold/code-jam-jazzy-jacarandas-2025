import reflex as rx

from code_jam_jazzy_jacarandas_2025.components.about import about_button


def header() -> rx.Component:
    """Render the header component."""
    content = rx.vstack(about_button())
    return rx.center(content)
