"""Helper class using in functions of the gitea package."""

from dataclasses import dataclass

from gitea.config import BASE_API_URL, PROJECT, PROJECT_OWNER, REFS_PER_PAGE


@dataclass
class GiteaUrlParams(object):
    """Shared readonly parameters for gitea repository URL."""

    base_api_url: str = BASE_API_URL
    owner: str = PROJECT_OWNER
    project: str = PROJECT
    recursive: bool = True
    refs_per_page: int = REFS_PER_PAGE
