from typing import TypedDict


class Developer(TypedDict):
    """Create developer object in order to unpack when rendering."""

    name: str
    description: str
    github_link: str
    team_leader: bool


developers: list[Developer] = [
    {
        "name": "Hero",
        "description": "Team leader. Built fetcher system, sliders, and configuration.",
        "github_link": "https://github.com/HEROgold",
        "team_leader": True,
    },
    {
        "name": "KKiyomi",
        "description": "Team member contributing with planning, brainstorming and behind the scenes code improvement.",
        "github_link": "https://github.com/kkiyomi",
        "team_leader": False,
    },
    {
        "name": "Doodleheimer",
        "description": "App setup specialist. Created foundation Reflex app and slider components.",
        "github_link": "https://github.com/artahadhahd",
        "team_leader": False,
    },
    {
        "name": "Bananadado",
        "description": "Team member contributing to project development, UI improvements and testing.",
        "github_link": "https://github.com/bananadado",
        "team_leader": False,
    },
    {
        "name": "Andre Binbow",
        "description": "UI/UX developer. Created developer boxes, charts, logo integration, and styling.",
        "github_link": "https://github.com/AndreBinbow",
        "team_leader": False,
    },
]
