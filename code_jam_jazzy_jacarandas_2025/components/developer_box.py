import reflex as rx


def developer_box(name: str, description: str, github_link: str, *, team_leader: bool = False) -> rx.Component:
    """Render box containing information about a developer.

    If team_leader is True, highlight the box in gold.
    """
    border_color = "gold" if team_leader else "white"

    username = github_link.rstrip("/").split("/")[-1]
    avatar_url = f"https://github.com/{username}.png"

    return rx.box(
        rx.hstack(
            rx.vstack(
                rx.text(name, size="6"),
                rx.text(description, size="4"),
                rx.link("Github link", href=github_link, size="3"),
                spacing="1",
                width="40vw",
            ),
            rx.image(src=avatar_url, alt=f"{name}'s profile picture", width="80px", border_radius="50%"),
            spacing="2",
            align_items="center",
        ),
        border=f"2px solid {border_color}",
        border_radius="25px",
        padding="15px",
        margin="10px",
    )
