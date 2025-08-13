import reflex as rx

def redirect_to_about() -> rx.event.EventSpec:
    """Redirect to the about page."""
    return rx.redirect("/about")

def about_button() -> rx.Component:
    """Render the about button."""
    return rx.button("About", on_click=redirect_to_about)
