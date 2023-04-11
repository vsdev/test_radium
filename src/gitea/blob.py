"""Functions for blob reading from gitea and writing to file."""

import base64
import logging
import os
import stat

import aiofiles
import aiohttp


async def get_blob_data(url: str, sess: aiohttp.ClientSession) -> bytes | None:
    """Get blob from URL and get bytes decoded from base64 format."""
    try:
        response = await sess.get(url)
    except Exception as ex:
        logging.error("Can't grab blob: {0}".format(url))
        logging.exception(ex)
        return None

    json = await response.json()

    blob_content = json.get('content')
    encoding = json.get('encoding')

    if encoding != 'base64':
        logging.warning(
            'get_blob_data. Unsupported encoding: {0}'.
            format(encoding),
        )
        return None

    return base64.b64decode(blob_content)


async def write_blob_to_file(
    blob_data: bytes,
    relative_path: str,
    temp_dir: str,
    is_executable: bool,
) -> bool:
    """Write blob data (file) to newly created file."""
    subdir = os.path.dirname(relative_path)
    filename = os.path.basename(relative_path)

    abs_dir = temp_dir
    if subdir:
        abs_dir = temp_dir + os.sep + subdir
        path = abs_dir + os.sep + filename
    else:
        path = temp_dir + os.sep + filename

    if not os.path.exists(abs_dir):
        try:
            os.makedirs(abs_dir, exist_ok=True)
        except Exception as ex:
            logging.exception(ex)
            return False

    logging.info('Write blob to file: {0}'.format(path))
    async with aiofiles.open(path, mode='w+b') as fp:
        await fp.write(blob_data)

    if is_executable:
        os.chmod(path, os.stat(path).st_mode | stat.S_IEXEC)

    return True


def check_mode(ref: dict, page: int) -> bool:
    """Check blob mode and ignore symbolic link."""
    path = ref.get('path')
    sha = ref.get('sha')
    mode = ref.get('mode')

    if mode not in {'100644', '100755'}:
        logging.info(
            'Page {0}. Skipping blob. path: {1}, mode: {2}, SHA: {3}'.
            format(page, path, mode, sha),
        )
        return False
    return True


def print_blob_info(ref: dict, page: int) -> None:
    """Print blob information to log."""
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
    logging.info('{0}{1}'.format(str0, str1))
