"""Calculations of SHA-256 hash for files."""

import hashlib
import logging

from filesystem import get_files_recursive


def calc_sha256(file_path: str, block_size: int = 4096) -> str:
    """Calculate SHA-256 for file.

    :param file_path: Path to file.
    :param block_size: Size of block to read in bytes.
    :returns: SHA-256 hash for file.
    """
    sha256_hash = hashlib.sha256()
    with open(file_path, 'rb') as fp:
        while True:
            block = fp.read(block_size)
            if not block:
                break
            sha256_hash.update(block)
    return sha256_hash.hexdigest()


def calc_sha_for_files_in_dir(
    directory: str,
    save_stats: bool = False,
) -> dict:
    """Calculate SHA256 checksum for each file in directory recursively.

    :param directory: Directory to parse.
    :param save_stats: Save filename and SHA to dict if True
    :returns: Dict with stats or empty dict depends on save_stats.
    """
    msg = 'Calculation of hashes for directory: {0}'.format(directory)
    logging.info(msg)

    stats = {}

    for file_path in get_files_recursive(directory):
        sha = calc_sha256(file_path)

        if save_stats:
            stats[file_path] = sha

        msg = 'File: {0}. SHA256: {1}'.format(file_path, sha)
        logging.info(msg)
    return stats
