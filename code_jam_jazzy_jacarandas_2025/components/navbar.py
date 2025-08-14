import reflex as rx

def redirect_to_about() -> rx.event.EventSpec:
    """Redirect to the about page."""
    return rx.redirect("/about")


def about_button() -> rx.Component:
    """Render the about button."""
    return rx.button("About", on_click=redirect_to_about)


def redirect_to_index() -> rx.event.EventSpec:
    """Redirect to the home page."""
    return rx.redirect("/")


def home_button() -> rx.Component:
    """Render the home button."""
    return rx.button("Home", on_click=redirect_to_index)


# eventually if we have more pages should create a BaseLayout() function to wrap pages in a navbar
def navbar() -> rx.Component:
    return rx.box(
        rx.hstack(
            home_button(),
            about_button(),
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
