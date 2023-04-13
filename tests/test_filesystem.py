"""Test filesystem functions."""
import os
import shutil
import tempfile

from pytest_mock import MockerFixture

from filesystem import get_directories, get_files, get_files_recursive

os_listdir = 'os.listdir'
some_dir = 'some_dir'
filesystem_exists = 'filesystem.exists'
filesystem_isfile = 'filesystem.isfile'


def mock_isfile(filename: str) -> bool:
    """Test function."""
    return filename.find('.') != -1


def test_get_files(mocker: MockerFixture):
    mocker.patch(
        os_listdir,
        return_value=[
            '/1/etc/cups/interfaces',
            '/1/etc/cups/ppd',
            '/1/etc/cups/cups-browsed.conf',
            '/1/etc/cups/cupsd.conf',
        ],
    )

    mocker.patch(filesystem_exists, return_value=True)
    mocker.patch(filesystem_isfile, mock_isfile)

    ls = list(get_files(some_dir))

    assert len(ls) == 2


def test_get_files_empty_dir(mocker: MockerFixture):
    mocker.patch(
        os_listdir,
        return_value=[],
    )

    num_files = sum(get_directories(some_dir))

    assert num_files == 0


def test_get_directories(mocker: MockerFixture):
    mocker.patch(
        os_listdir,
        return_value=[
            '/1/etc/cups/interfaces',
            '/1/etc/cups/ppd',
            '/1/etc/cups/cups-browsed.conf',
            '/1/etc/cups/cupsd.conf',
        ],
    )

    mocker.patch(filesystem_exists, return_value=True)
    mocker.patch(filesystem_isfile, mock_isfile)

    ls = list(get_directories(some_dir))

    assert len(ls) == 2


def test_get_directories_empty_dir(mocker: MockerFixture):
    mocker.patch(
        os_listdir,
        return_value=[],
    )

    ls = list(get_directories(some_dir))

    assert not ls


def make_files_in_dir(directory: str, count: int) -> int:
    return len([tempfile.mkstemp(dir=directory) for _ in range(count)])


def test_get_files_recursively():
    root_dir = tempfile.mkdtemp()
    count = make_files_in_dir(root_dir, 3)

    subdir = '{0}{1}1'.format(root_dir, os.sep)
    os.makedirs(name=subdir)
    count += make_files_in_dir(subdir, 5)

    subdir = '{0}{1}2'.format(root_dir, os.sep)
    os.makedirs(name=subdir)
    count += make_files_in_dir(subdir, 1)

    subdir = ('{0}{1}2{2}2.1'.format(root_dir, os.sep, os.sep))
    os.makedirs(name=subdir)
    count += make_files_in_dir(subdir, 2)

    ls = list(get_files_recursive(root_dir))

    shutil.rmtree(root_dir)

    assert len(ls) == count
