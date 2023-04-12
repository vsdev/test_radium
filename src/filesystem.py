"""Extract filenames from path recursively."""

import os
from os.path import exists, isfile, join
from typing import Any, Generator


def get_files(path: str) -> Generator[str, Any, None]:
    """List all files inside path directory.

    :param path: Absolute path for existing directory.
    :returns: Next filename in the directory or raises StopIteration exception.
    """
    for filename in os.listdir(path):
        full_path = join(path, filename)
        if isfile(full_path):
            if exists(full_path):
                yield full_path


def get_directories(path: str) -> Generator[str, Any, None]:
    """List all directories inside path directory.

    :param path: Absolute path for existing directory.
    :returns: Next directory name or raises StopIteration exception.
    """
    for directory in os.listdir(path):
        full_path = join(path, directory)
        if not isfile(full_path):
            if exists(full_path):
                yield full_path


def get_files_recursive(path: str) -> Generator[str, Any, None]:
    """List all files inside directory recursively.

    :param path: Absolute path for existing directory.
    :returns: Next filename in the directory or raises StopIteration exception.
    """
    yield from get_files(path)
    for subdirectory in get_directories(path):
        yield from get_files_recursive(subdirectory)
