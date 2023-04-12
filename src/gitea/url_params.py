"""Helper class using in functions of the gitea package."""

from dataclasses import dataclass

from gitea.config import BASE_API_URL, PROJECT, PROJECT_OWNER, REFS_PER_PAGE


@dataclass
class GiteaUrlParams(object):
    """Shared readonly parameters for gitea repository URL.

    :cvar base_api_url: URL of repository API.
        Example: https://gitea.radium.group/api/v1
    :cvar owner: Owner of repository.
        Example: radium
    :cvar project: Name of the project.
        Example: project-configuration
    :cvar recursive: Query parameter for ref tree output.
        True by default. Parses full tree with all subtrees.
    :cvar refs_per_page: Number of elements in paginated tree output.
    """

    base_api_url: str = BASE_API_URL
    owner: str = PROJECT_OWNER
    project: str = PROJECT
    recursive: bool = True
    refs_per_page: int = REFS_PER_PAGE
