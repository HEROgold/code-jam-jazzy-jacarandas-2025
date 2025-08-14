import reflex as rx


def developer_box(name: str, description: str, github_link: str, *, team_leader: bool = False) -> rx.Component:
    """Render box containing information about a developer.

    If team_leader is True, highlight the box in gold.
    """
    border_color = "gold" if team_leader else "white"

    return rx.box(
        rx.vstack(
            rx.text(name, size="8"),
            rx.text(description, size="5"),
            rx.link("Github!", href=github_link, target="_blank", size="4"),
            spacing="1",
            width="40vw",
        ),
        border=f"2px solid {border_color}",
        border_radius="25px",
        padding="15px",
        margin="10px",
    )
