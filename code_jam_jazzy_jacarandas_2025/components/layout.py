import reflex as rx

from code_jam_jazzy_jacarandas_2025.components.navbar import navbar


def base_layout(children: rx.Component) -> rx.Component:
    """Wrap page content with navbar."""
    return rx.vstack(
        navbar(),  # Always on top
        children,  # Page-specific content below
        spacing="4",
        align_items="center",
        width="100%",
    )
