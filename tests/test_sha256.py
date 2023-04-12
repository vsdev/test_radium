"""Test sha256 functions."""
import hashlib
import os

import filesystem
import log
import sha256


def test_sha256():
    file_path = '{0}{1}{2}'.format(
        log.get_project_root_dir(),
        os.sep,
        'tests/test_sha256.py',
    )

    test_hash = hashlib.sha256()
    with open(file_path, 'rb') as fp:
        file_contents = fp.read()
        test_hash.update(file_contents)

    sha = sha256.calc_sha256(file_path)

    assert sha == test_hash.hexdigest()


def test_calc_sha_for_files_in_dir():
    test_dir = '{0}{1}{2}'.format(
        log.get_project_root_dir(),
        os.sep,
        'nitpick',
    )

    stats = sha256.calc_sha_for_files_in_dir(
        test_dir,
        save_stats=True,
    )
    test_files = list(filesystem.get_files_recursive(test_dir))

    for file_path in test_files:
        test_hash = hashlib.sha256()
        with open(file_path, 'rb') as fp:
            file_contents = fp.read()
            test_hash.update(file_contents)
        sha2 = test_hash.hexdigest()

        assert stats.get(file_path) == sha2
