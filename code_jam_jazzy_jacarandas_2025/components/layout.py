import reflex as rx

from code_jam_jazzy_jacarandas_2025.components.navbar import navbar


def base_layout(children: rx.Component) -> rx.Component:
    """Wrap page content with navbar."""
    return rx.vstack(
        navbar(),  # Always on top
        rx.box(
            children,
            padding_top="4rem",
            width="100%",
        ),
        spacing="4",
        align_items="center",
        width="100%",
    )
