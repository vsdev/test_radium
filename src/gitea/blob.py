"""Functions for blob reading from gitea and writing to file."""

import base64
import logging
import os
import stat
from http import HTTPStatus

import aiofiles
import aiohttp


async def get_blob_data(url: str, sess: aiohttp.ClientSession) -> bytes | None:
    r"""Get blob from URL and get bytes decoded from base64 format.

    :param url: GET response from URL contains blob's data into
        \'contents\' field encoded in base64.
    :param sess: Active session object
    :returns: decoded contents of blob
    """
    try:
        response = await sess.get(url)
    except Exception as ex:
        msg = "Can't grab blob: {0}".format(url)
        logging.exception(msg)
        raise ex

    if response.status != HTTPStatus.OK:
        msg = "Response status: {0}".format(response.status)
        logging.error(msg)
        return None

    json = await response.json()

    blob_content = json.get('content')
    encoding = json.get('encoding')

    if encoding != 'base64':
        msg = 'get_blob_data. Unsupported encoding: {0}'.format(encoding)
        logging.error(msg)
        return None

    return base64.b64decode(blob_content)


async def write_blob_to_file(
    blob_data: bytes,
    relative_path: str,
    temp_dir: str,
    is_executable: bool,
) -> bool:
    """Write blob data (file) to newly created file.

    :param blob_data: Data from blob decoded from base64 format.
    :param relative_path: Relative path to file in the repository.
        Directory will be created if not exist before call of this func.
    :param temp_dir: Temp directory root. Absolute path.
    :param is_executable: chmod +x will be invoked if True
    :returns: True if no exceptions
    """
    subdir = os.path.dirname(relative_path)

    abs_dir = temp_dir
    if subdir:
        abs_dir = temp_dir + os.sep + subdir
        path = abs_dir + os.sep + os.path.basename(relative_path)
    else:
        path = temp_dir + os.sep + os.path.basename(relative_path)

    if not os.path.exists(abs_dir):
        os.makedirs(abs_dir, exist_ok=True)

    msg = 'Write blob to file: {0}'.format(path)
    logging.info(msg)
    async with aiofiles.open(path, mode='w+b') as fp:
        await fp.write(blob_data)

    if is_executable:
        os.chmod(path, os.stat(path).st_mode | stat.S_IEXEC)

    return True


def check_mode(ref: dict, page: int) -> bool:
    """Check blob mode and ignore symbolic link.

    :param ref: JSON dict contains information about blob.
    :param page: Page number (paginated reading of the git refs tree)
        for log output.
    :returns: True if blob mode is 100644 or 100664 (non-executable,
        group writable), 100755(executable).
        False for 120000 (symbolic link) and other types.
    """
    path = ref.get('path')
    sha = ref.get('sha')
    mode = ref.get('mode')

    if mode not in {'100644', '100664', '100755'}:
        s0 = 'Page {0}. Skipping blob. path: {1}'.format(page, path)
        s1 = ', mode: {0}, SHA: {1}'.format(mode, sha)
        s0 = '{0}{1}'.format(s0, s1)
        logging.info(s0)
        return False
    return True


def print_blob_info(ref: dict, page: int) -> None:
    """Print blob information to log.

    :param ref: JSON dict contains information about blob.
    :param page: Page number (paginated reading of the git refs tree)
        for log output.
    """
    str0 = 'Page {0}. Processing blob. path: {1}, mode: {2}, '.format(
        page,
        ref.get('path'),
        ref.get('mode'),
    )
    str1 = 'SHA: {0}, size: {1}, url: {2}'.format(
        ref.get('sha'),
        ref.get('size'),
        ref.get('url'),
    )
    msg = '{0}{1}'.format(str0, str1)
    logging.info(msg)
