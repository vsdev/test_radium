"""Integration tests."""
import shutil
import tempfile

import aiohttp
import pytest

import filesystem
import main
from gitea.refs_tree import process_tree_refs_page, process_tree_refs_pages
from gitea.url_params import GiteaUrlParams

TEST_REF_URL = (
    'https://gitea.radium.group/api/v1/repos/radium/' +
    'project-configuration/git/trees/' +
    'eb4dc314435649737ad343ef82240b96256d5eb8' +
    '?recursive=true&page=1&per_page=5'
)

REFS_SHA = 'eb4dc314435649737ad343ef82240b96256d5eb8'
TEST_PAGE = 1


@pytest.mark.asyncio()
async def test_process_tree_refs_page():
    temp_dir = tempfile.mkdtemp()

    async with aiohttp.ClientSession() as sess:
        await process_tree_refs_page(
            REFS_SHA,
            sess,
            temp_dir,
            GiteaUrlParams(),
            TEST_PAGE,
        )

        count = len(list(filesystem.get_files_recursive(temp_dir)))
        shutil.rmtree(temp_dir)

        assert count == 4


@pytest.mark.asyncio()
async def test_process_tree_refs_pages():
    async with aiohttp.ClientSession() as sess:
        temp_dir = tempfile.mkdtemp()
        await process_tree_refs_pages(
            REFS_SHA,
            sess,
            GiteaUrlParams(),
            temp_dir,
        )

        count = len(list(filesystem.get_files_recursive(temp_dir)))
        shutil.rmtree(temp_dir)

        assert count == 10


@pytest.mark.asyncio()
async def test_main():
    temp_dir = await main.main()
    count = len(list(filesystem.get_files_recursive(temp_dir)))
    shutil.rmtree(temp_dir)
    assert count == 10
