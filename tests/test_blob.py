"""Test blob.py functions."""
import base64
import hashlib
import os
import tempfile
from http import HTTPStatus

import aiofiles
import aiohttp
import aioresponses
import pytest
from aiohttp.http_exceptions import HttpProcessingError

from gitea import blob

PATH_KEY = 'path'
SHA_KEY = 'sha'
MODE_KEY = 'mode'
SIZE_KEY = 'size'
ENCODING_KEY = 'encoding'
URL_KEY = 'url'

PATH_VALUE = 'path'
SHA_VALUE = 'sha'
BASE64_VALUE = 'base64'
DEBUG_DATA_VALUE = 'DEBUG DATA'


def test_check_mode():
    test_json = {PATH_KEY: PATH_VALUE, SHA_KEY: SHA_VALUE, MODE_KEY: '100'}
    assert not blob.check_mode(test_json, 0)

    test_json[MODE_KEY] = '100644'
    assert blob.check_mode(test_json, 0)

    test_json[MODE_KEY] = '100664'
    assert blob.check_mode(test_json, 0)

    test_json[MODE_KEY] = '100755'
    assert blob.check_mode(test_json, 0)


def test_print_blob_info():
    test_json = {PATH_KEY: PATH_VALUE, SHA_KEY: SHA_VALUE, MODE_KEY: '100'}
    # for coverage only
    assert blob.print_blob_info(test_json, 0) is None


def get_sha_from_bytes(bt: bytes) -> str:
    test_hash = hashlib.sha256()
    test_hash.update(bt)
    return test_hash.hexdigest()


@pytest.mark.asyncio()
async def test_write_blob_to_file(file_size: int = 8192):
    test_bytes: bytes = os.urandom(file_size)
    relative_path: str = '|sd443fs435ks23eds|324324fds|blob'
    relative_path = relative_path.replace('|', os.sep)
    absolute_path = '{0}{1}'.format(tempfile.tempdir, relative_path)

    if os.path.exists(absolute_path):
        os.remove(absolute_path)

    assert await blob.write_blob_to_file(
        test_bytes,
        relative_path,
        tempfile.tempdir,
        is_executable=True,
    )

    assert os.path.exists(absolute_path)
    assert os.path.isfile(absolute_path)
    assert os.access(absolute_path, os.X_OK)

    async with aiofiles.open(absolute_path, mode='rb') as fp:
        bytes1 = await fp.read()
        assert get_sha_from_bytes(bytes1) == get_sha_from_bytes(test_bytes)


TEST_BLOB_URL = (
    'https://gitea.radium.group/api/v1/repos/radium/' +
    'project-configuration/git/blobs' +
    '/36f689a9b02d7bb9ed1395dfb752c1c5826948da'
)


def get_blob_stub_data() -> dict:
    message = DEBUG_DATA_VALUE
    message_en = message.encode('ascii')
    message_en = base64.b64encode(message_en)
    message_en = message_en.decode('ascii')

    return {
        'content': message_en,
        ENCODING_KEY: 'base64',
        URL_KEY: (
            'https://gitea.radium.group/api/v1/repos/radium/' +
            'project-configuration/git/blobs/' +
            '36f689a9b02d7bb9ed1395dfb752c1c5826948da'
        ),
        SHA_KEY: '36f689a9b02d7bb9ed1395dfb752c1c5826948da',
        SIZE_KEY: 507,
        'debug': 1,
    }


def get_blob_stub_data_base16() -> dict:
    return {
        ENCODING_KEY: 'base16',
    }


@pytest.mark.asyncio()
async def test_get_blob_data():
    with aioresponses.aioresponses() as aresp:
        async with aiohttp.ClientSession() as sess:
            aresp.get(
                TEST_BLOB_URL,
                status=HTTPStatus.BAD_REQUEST,
                payload=get_blob_stub_data(),
            )

            blob_data = await blob.get_blob_data(TEST_BLOB_URL, sess)
            assert blob_data is None

            aresp.get(
                TEST_BLOB_URL,
                status=HTTPStatus.OK,
                payload=get_blob_stub_data(),
            )

            blob_data = await blob.get_blob_data(TEST_BLOB_URL, sess)
            assert blob_data is not None
            assert DEBUG_DATA_VALUE == blob_data.decode('ascii')

            aresp.get(
                TEST_BLOB_URL,
                status=HTTPStatus.OK,
                payload=get_blob_stub_data_base16(),
            )

            blob_data = await blob.get_blob_data(TEST_BLOB_URL, sess)
            assert blob_data is None

            aresp.get(
                TEST_BLOB_URL,
                status=HTTPStatus.BAD_REQUEST,
                exception=HttpProcessingError(message='test_get_blob_data'),
                payload=get_blob_stub_data(),
            )

            with pytest.raises(HttpProcessingError):
                await blob.get_blob_data(TEST_BLOB_URL, sess)
