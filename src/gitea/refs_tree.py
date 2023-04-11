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
    """Get refs tree (paginated) from gitea and parse each ref."""
    pages_count = await get_tree_refs_pages_count(sha, sess, urlp)
    if pages_count == 0:
        raise ValueError('pages count == 0')

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
    """Get and parse each ref from the selected page."""
    logging.info('Processing page: {0}'.format(page))

    fl = filter(
        lambda rf: rf.get('type') == 'blob',
        await get_tree_data(sha, sess, urlp, page),
    )

    while True:
        try:
            ref = next(fl)
        except StopIteration:
            break
        except Exception as ex:
            logging.exception(ex)
            return

        if not check_mode(ref, page):
            continue

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
    """Get tree JSON dict from response or empty dict."""
    json = await get_tree_refs_page(sha, page, sess, urlp)
    if json is None:
        return {}

    tree_data = json.get('tree')
    if tree_data is None:
        logging.error("Page {0}. \'tree\' not found".format(page))
        return {}
    return tree_data


async def get_tree_refs_page(
    sha: str,
    page: int,
    sess: aiohttp.ClientSession,
    urlp: GiteaUrlParams,
) -> dict | None:
    """Get paginated refs' data from selected page."""
    recursive_str = 'true' if urlp.recursive else 'false'

    str0 = '{0}/repos/{1}/{2}/git/trees/{3}'.format(
        urlp.base_api_url,
        urlp.owner,
        urlp.project,
        sha,
    )
    str1 = '?recursive={0}&page={1}&per_page={2}'.format(
        recursive_str,
        page,
        urlp.refs_per_page,
    )
    url = '{0}{1}'.format(str0, str1)
    logging.info('GET tree from {0}'.format(url))

    try:
        response = await sess.get(url)
    except Exception as ex:
        logging.error("Can\'t grab page: {0}".format(page))
        logging.exception(ex)
        return None

    return await response.json()


async def get_tree_refs_pages_count(
    sha: str,
    sess: aiohttp.ClientSession,
    urlp: GiteaUrlParams,
) -> int:
    """Get number of pages for tree."""
    json = await get_tree_refs_page(sha, 1, sess, urlp)
    if json is None:
        return 0

    total_count = json.get('total_count')
    if total_count is None:
        logging.error('total_count not found')
        return 0

    if total_count < urlp.refs_per_page:
        pages_count = 1
    else:
        pages_count = int(total_count / urlp.refs_per_page)
        if total_count % urlp.refs_per_page != 0:
            pages_count += 1

    logging.info('Pages count: {0}'.format(pages_count))
    return pages_count
