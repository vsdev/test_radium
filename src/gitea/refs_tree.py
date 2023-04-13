"""Functions for parsing of list of git refs through REST API."""

import asyncio
import logging

import aiohttp

from gitea.blob import (
    check_mode,
    get_blob_data,
    print_blob_info,
    write_blob_to_file,
)
from gitea.config import PARALLEL_DOWNLOADS
from gitea.url_params import GiteaUrlParams


async def process_tree_refs_pages(
    sha: str,
    sess: aiohttp.ClientSession,
    urlp: GiteaUrlParams,
    temp_dir: str,
    num_parallel: int = PARALLEL_DOWNLOADS,
) -> None:
    """GET information (paginated) for HEAD or selected ref.

    GET ref tree info from gitea repository and parse each ref file entry.
    Decode blobs for files and restore directory structure.
    Load each file to corresponding subdirectory in the temp
    directory.

    :param sha: SHA of the HEAD or another ref to parse.
    :param sess: Active session.
    :param urlp: Base URL parameters for repository (pagination etc.).
    :param temp_dir: Temporary directory for files loading.
    :param num_parallel: Number of async aiohttp requests and tasks.
    """
    pages_count = await get_tree_refs_pages_count(sha, sess, urlp)

    i0 = 1
    while i0 <= pages_count:
        j0 = i0

        tasks = []
        while j0 < i0 + num_parallel and j0 <= pages_count:
            task = asyncio.create_task(
                process_tree_refs_page(sha, sess, temp_dir, urlp, page=j0),
            )
            tasks.append(task)
            j0 += 1

        await asyncio.gather(*tasks)
        i0 += num_parallel


async def process_tree_refs_page(
    sha: str,
    sess: aiohttp.ClientSession,
    temp_dir: str,
    urlp: GiteaUrlParams,
    page: int,
) -> None:
    r"""Parse each ref with type \'blob\' from the selected page.

    Each blob data grabbed from remote and saved to disk with relative
    path from remote.
    :param sha: SHA of the HEAD or another ref to parse.
    :param sess: Active session.
    :param temp_dir: Temporary directory for files loading.
    :param urlp: Base URL parameters for repository (pagination etc.).
    :param page: Page number for paginated request
    """
    msg = 'Processing page: {0}'.format(page)
    logging.info(msg)

    fl = filter(
        lambda rf: rf.get('type') == 'blob',
        await get_tree_data(sha, sess, urlp, page),
    )

    while True:
        try:
            ref = next(fl)
        except StopIteration:
            break
        if check_mode(ref, page):
            print_blob_info(ref, page)

            await write_blob_to_file(
                await get_blob_data(ref.get('url'), sess),
                ref.get('path'),
                temp_dir,
                is_executable=ref.get('mode') == '100755',
            )


async def get_tree_data(
    sha: str,
    sess: aiohttp.ClientSession,
    urlp: GiteaUrlParams,
    page: int,
) -> dict:
    """GET JSON dict for blobs and trees (paginated) from top-level tree.

    :param sha: SHA of the HEAD or another ref to parse.
    :param sess: Active session.
    :param urlp: Base URL parameters for repository (pagination etc.).
    :param page: Page number for paginated request
    :returns: JSON dict for blobs and trees for page.
    """
    json = await get_tree_refs_page(sha, page, sess, urlp)
    if json is None:
        return {}

    return json.get('tree')


async def get_tree_refs_page(
    sha: str,
    page: int,
    sess: aiohttp.ClientSession,
    urlp: GiteaUrlParams,
) -> dict | None:
    """GET top-level tree object page data.

    :param sha: SHA of the HEAD or another ref to parse.
    :param page: Page number for paginated request
    :param sess: Active session.
    :param urlp: Base URL parameters for repository (pagination etc.).
    :returns: JSON dict for blobs and trees (paginated).
    """
    str0 = '{0}/repos/{1}/{2}/git/trees/{3}'.format(
        urlp.base_api_url,
        urlp.owner,
        urlp.project,
        sha,
    )
    str1 = '?recursive={0}&page={1}&per_page={2}'.format(
        'true' if urlp.recursive else 'false',
        page,
        urlp.refs_per_page,
    )
    url = '{0}{1}'.format(str0, str1)
    msg = 'GET tree from {0}'.format(url)
    logging.info(msg)

    try:
        response = await sess.get(url)
    except Exception as ex:
        msg = "Can\'t grab page: {0}".format(page)
        logging.exception(msg)
        return None

    return await response.json()


async def get_tree_refs_pages_count(
    sha: str,
    sess: aiohttp.ClientSession,
    urlp: GiteaUrlParams,
) -> int:
    """Get number of pages for ref.

    :param sha: SHA of the HEAD or another ref to parse.
    :param sess: Active session.
    :param urlp: Base URL parameters for repository (pagination etc.).
    :returns: Number of pages to parse.
    """
    json = await get_tree_refs_page(sha, 1, sess, urlp)
    if json is None:
        return 0

    total_count = json.get('total_count')
    if total_count is None or total_count == 0:
        logging.error('total_count not found')
        return 0

    if total_count < urlp.refs_per_page:
        pages_count = 1
    else:
        pages_count = int(total_count / urlp.refs_per_page)
        if total_count % urlp.refs_per_page != 0:
            pages_count += 1

    logging.info('Pages count: {pc}', extra={'pc': pages_count})
    return pages_count
