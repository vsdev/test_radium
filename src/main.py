"""Main module of the project."""

import asyncio
import os
import tempfile

import aiohttp

import log
from gitea.refs_tree import process_tree_refs_pages
from gitea.repo_head import get_ref_sha
from gitea.url_params import GiteaUrlParams
from sha256 import calc_sha_for_files_in_dir


async def main() -> str:
    """Entry point."""
    log.init_logger()
    url_params = GiteaUrlParams()

    async with aiohttp.ClientSession() as sess:
        head_sha = await get_ref_sha(sess, url_params)
        temp_dir = tempfile.mkdtemp()
        await process_tree_refs_pages(head_sha, sess, url_params, temp_dir)
        calc_sha_for_files_in_dir(temp_dir)
        return temp_dir


if __name__ == '__main__':
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
