import asyncio
import os

import aiohttp

import util
from gitea import GiteaUrlParams, process_tree_refs_pages, get_head_sha
from sha256 import calc_sha_for_files_in_dir

HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:27.0) Gecko/20100101 Firefox/27.0'}


async def main() -> None:
    util.init_logger()
    url_params = GiteaUrlParams()

    async with aiohttp.ClientSession(headers=HEADERS) as sess:
        head_sha = await get_head_sha(sess, url_params)
        if len(head_sha) == 0:
            return

        temp_dir = await process_tree_refs_pages(head_sha, sess, url_params)
        calc_sha_for_files_in_dir(temp_dir)


if __name__ == '__main__':
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
