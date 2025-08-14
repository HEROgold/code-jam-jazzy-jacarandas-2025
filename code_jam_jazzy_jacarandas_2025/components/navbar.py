import reflex as rx

def navbar() -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.button(
                "Home",
                on_click=lambda: rx.redirect("/"),
                padding="2",
                border_radius="md",
            ),
            rx.button(
                "About",
                on_click=lambda: rx.redirect("/about"),
                padding="2",
                border_radius="md",
            ),
            spacing="4",
            align_items="center",
        ),
        width="100%",
        padding="0.75rem 1rem",
        background_color="gray.50",
        box_shadow="sm",
        style={
            "fontFamily": "Comic Sans MS, Comic Sans, cursive",
        },
    )
