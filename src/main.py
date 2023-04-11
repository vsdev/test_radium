"""Main module of the project."""

import asyncio
import os
import tempfile

import aiohttp

import log
from gitea.refs_tree import process_tree_refs_pages
from gitea.repo_head import get_head_sha
from gitea.url_params import GiteaUrlParams
from sha256 import calc_sha_for_files_in_dir


async def main() -> None:
    """Entry point."""
    log.init_logger()
    url_params = GiteaUrlParams()

    headers = {
        'User-Agent':
        'Mozilla/5.0 (X11; Linux x86_64; rv:27.0) Gecko/20100101 Firefox/27.0',
    }

    async with aiohttp.ClientSession(headers=headers) as sess:
        head_sha = await get_head_sha(sess, url_params)
        if not len(head_sha):
            return

        temp_dir = tempfile.mkdtemp()
        await process_tree_refs_pages(head_sha, sess, url_params, temp_dir)
        calc_sha_for_files_in_dir(temp_dir)


if __name__ == '__main__':
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
