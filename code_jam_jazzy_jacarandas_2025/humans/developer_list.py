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
        "description": "Team leader",
        "github_link": "https://github.com/HEROgold",
        "team_leader": True,
    },
    {
        "name": "KKiyomi",
        "description": "Test test 123",
        "github_link": "https://github.com/kkiyomi",
        "team_leader": False,
    },
    {
        "name": "Doodleheimer",
        "description": "Test test 123",
        "github_link": "https://github.com/artahadhahd",
        "team_leader": False,
    },
    {
        "name": "Bananadado",
        "description": "Test test 123",
        "github_link": "https://github.com/bananadado",
        "team_leader": False,
    },
    {
        "name": "Andre Binbow",
        "description": "Test test 123",
        "github_link": "https://github.com/AndreBinbow",
        "team_leader": False,
    },
]
