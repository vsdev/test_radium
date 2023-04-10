import asyncio
import logging
import os
import tempfile
from dataclasses import dataclass

import aiohttp as aiohttp

import util

HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:27.0) Gecko/20100101 Firefox/27.0'}

BASE_API_URL = "https://gitea.radium.group/api/v1"
PROJECT_OWNER = "radium"
PROJECT = "project-configuration"
REF_HEAD = "refs/heads/master"
REFS_PER_PAGE = 5
PARALLEL_DOWNLOADS = 3


@dataclass
class GiteaUrlParams:
    base_api_url: str = BASE_API_URL
    owner: str = PROJECT_OWNER
    project: str = PROJECT
    recursive: bool = True
    refs_per_page: int = REFS_PER_PAGE


def parse_sha(json: dict, ref_to_find: str) -> str:
    sha = ""
    try:
        ref = next(filter(lambda x: x.get('ref') == ref_to_find, json))
        obj = ref.get("object")
        sha = obj.get("sha")
        logging.info(f"HEAD SHA {sha}")

    except StopIteration:
        logging.error(f"parse_sha: {ref_to_find} not found")
    except Exception as e:
        logging.exception(e)
    return sha


async def get_head_sha(sess: aiohttp.ClientSession,
                       urlp: GiteaUrlParams,
                       ref=REF_HEAD
                       ) -> str:
    url = f"{urlp.base_api_url}/repos/{urlp.owner}/{urlp.project}/git/refs"
    logging.info(f"GET refs from {url}")

    try:
        response = await sess.get(url)
    except Exception as e:
        logging.exception(e)
        return ""

    data = await response.json()
    return parse_sha(data, ref)


def parse_tree(json: dict) -> list[str]:
    tree_data = json.get('tree')
    if tree_data is None:
        raise ValueError("tree not found")


async def get_tree_refs_page(sha: str,
                             page: int,
                             sess: aiohttp.ClientSession,
                             urlp: GiteaUrlParams) -> dict | None:
    recursive_str = 'true' if urlp.recursive else 'false'
    url = f"{urlp.base_api_url}/repos/{urlp.owner}/{urlp.project}/git/trees/{sha}?recursive={recursive_str}&page={page}&per_page={urlp.refs_per_page}"
    logging.info(f"GET tree from {url}")

    try:
        response = await sess.get(url)
    except Exception as e:
        logging.error(f"Can't grab page: {page}")
        logging.exception(e)
        return None

    data = await response.json()
    return data


async def get_tree_refs_pages_count(sha: str,
                                    sess: aiohttp.ClientSession,
                                    urlp: GiteaUrlParams) -> int:
    data = await get_tree_refs_page(sha, 1, sess, urlp)
    if data is None:
        return 0

    total_count = data.get('total_count')
    if total_count is None:
        logging.error("total_count not found")
        return 0

    if total_count < urlp.refs_per_page:
        pages_count = 1
    else:
        pages_count: int = total_count / urlp.refs_per_page
        if total_count % urlp.refs_per_page != 0:
            pages_count += 1

    logging.info(f"Pages count: {pages_count}")
    return pages_count


async def process_tree_refs_page(sha: str,
                                 sess: aiohttp.ClientSession,
                                 temp_dir: str,
                                 urlp: GiteaUrlParams,
                                 page: int
                                 ) -> None:
    data = await get_tree_refs_page(sha, page, sess, urlp)
    if data is None:
        return

    tree_data = data.get('tree')
    if tree_data is None:
        logging.error(f"tree not found, page {page}")

    i = 0
    while i < urlp.refs_per_page:
        try:
            ref = next(filter(lambda x: x.get('type') == 'blob', tree_data))
            path = ref.get('path')
            sha = ref.get('sha')
            size = ref.get('size')
            url = ref.get('url')
            filename = os.path.basename(path)

            logging.info(f"Processing {path}")
        except StopIteration:
            break
        except Exception as e:
            logging.exception(e)

        i += 1


async def process_tree_refs_pages(sha: str,
                                  sess: aiohttp.ClientSession,
                                  urlp: GiteaUrlParams,
                                  num_parallel: int = PARALLEL_DOWNLOADS) -> bool:
    pages_count = await get_tree_refs_pages_count(sha, sess, urlp)
    if pages_count == 0:
        raise ValueError("process_tree_refs_pages pages count == 0")

    temp_dir = tempfile.mkdtemp()
    i = 1
    while i <= pages_count:
        j = i

        tasks = []
        while j < i + num_parallel and j < pages_count:
            tasks.append(asyncio.create_task(process_tree_refs_page(sha, sess, temp_dir, urlp, page=j)))
            j += 1

        await asyncio.gather(*tasks)
        i += num_parallel


async def main() -> None:
    util.init_logger()
    url_params = GiteaUrlParams()

    async with aiohttp.ClientSession(headers=HEADERS) as sess:
        head_sha = await get_head_sha(sess, url_params)
        if len(head_sha) == 0:
            return

        await process_tree_refs_pages(head_sha, sess, url_params)


if __name__ == '__main__':
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
