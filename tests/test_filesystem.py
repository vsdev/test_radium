"""Test filesystem functions."""

from pytest_mock import MockerFixture

from filesystem import get_directories, get_files

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


def test_get_files_recursively(mocker: MockerFixture):
    mocker.patch(
        os_listdir,
        return_value=[
            '/1/etc/cups',
            '/1/etc/cups/file.txt',
            '/1/etc/cups/ppd',
            '/1/etc/cups/ppd/cups-browsed.conf',
        ],
    )

    mocker.patch(filesystem_exists, return_value=True)
    mocker.patch(filesystem_isfile, mock_isfile)

    ls = list(get_files(some_dir))

    assert len(ls) == 2
