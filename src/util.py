import logging.config
import os
from os import path


def get_project_root_dir() -> str:
    path_to = path.abspath(__file__)
    dirname = path.dirname(path_to)
    dirname = dirname.replace(os.sep + "src", "")
    return dirname


def init_logger():
    log_file_path = get_project_root_dir() + os.sep + 'logconfig.ini'
    print('Load logging config from {0}'.format(path))
    logging.config.fileConfig(log_file_path)