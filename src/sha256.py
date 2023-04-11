"""Calculations of SHA256 for files in nested directories."""

import hashlib
import logging
import os
from os.path import exists, isfile, join
from typing import Any, Generator


def get_files(path: str) -> Generator[str, Any, None]:
    """Enumerate all files inside path directory."""
    for filename in os.listdir(path):
        full_path = join(path, filename)
        if isfile(full_path):
            if exists(full_path):
                yield full_path


def get_directories(path: str) -> Generator[str, Any, None]:
    """Enumerate all directories inside path directory."""
    for directory in os.listdir(path):
        full_path = join(path, directory)
        if not isfile(full_path):
            if exists(full_path):
                yield full_path


def get_files_recursive(path: str) -> Generator[str, Any, None]:
    """Enumerate all files inside path directory recursively."""
    yield from get_files(path)
    for subdirectory in get_directories(path):
        yield from get_files_recursive(subdirectory)


def calc_sha256(file_path: str, block_size: int = 4096) -> str:
    """Calculate SHA256 checksum for file file_path."""
    sha256_hash = hashlib.sha256()
    with open(file_path, 'rb') as fp:
        while True:
            block = fp.read(block_size)
            if not block:
                break
            sha256_hash.update(block)
    return sha256_hash.hexdigest()


def calc_sha_for_files_in_dir(directory: str) -> None:
    """Calculate SHA256 checksum for each file in directory recursively."""
    msg = 'Calculation of hashes for directory: {0}'.format(directory)
    logging.info(msg)

    for file_path in get_files_recursive(directory):
        sha = calc_sha256(file_path)
        msg = 'File: {0}. SHA256: {1}'.format(file_path, sha)
        logging.info(msg)
