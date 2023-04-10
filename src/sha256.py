import hashlib
import logging
import os
from os.path import join, isfile, exists
from typing import Generator, Any


def get_files(path) -> Generator[str, Any, None]:
    for file in os.listdir(path):
        full_path = join(path, file)
        if isfile(full_path):
            if exists(full_path):
                yield full_path


def get_directories(path):
    for directory in os.listdir(path):
        full_path = join(path, directory)
        if not isfile(full_path):
            if exists(full_path):
                yield full_path


def get_files_recursive(directory):
    yield from get_files(directory)
    for subdirectory in get_directories(directory):
        yield from get_files_recursive(subdirectory)


def calc_sha256(file_path: str) -> str:
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()


def calc_sha_for_files_in_dir(directory: str) -> None:
    logging.info(f"Calculation of hashes for directory: {directory}")

    for file_path in get_files_recursive(directory):
        sha = calc_sha256(file_path)
        logging.info(f"File: {file_path}. SHA256: {sha}")
