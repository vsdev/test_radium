"""Log helper functions of the project."""
import os
from logging import config, info


def get_project_root_dir() -> str:
    """Return root dir of the project.

    :returns: Project's working directory.
    """
    path_to = os.path.abspath(__file__)
    dirname = os.path.dirname(path_to)
    return dirname.replace('{0}src'.format(os.sep), '')


def init_logger() -> None:
    """Initialize logging logger from config file logconfig.ini."""
    root_dir = get_project_root_dir()
    log_file_path = '{0}{1}logconfig.ini'.format(root_dir, os.sep)
    config.fileConfig(log_file_path)
    msg = 'Load logging config from: {0}'.format(log_file_path)
    info(msg)
