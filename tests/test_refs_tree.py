"""Test refs_tree.py functions."""
from http import HTTPStatus

import aiohttp
import aioresponses
import pytest
from aiohttp.http_exceptions import HttpProcessingError

from gitea.refs_tree import (
    get_tree_data,
    get_tree_refs_page,
    get_tree_refs_pages_count,
)
from gitea.url_params import GiteaUrlParams

TEST_REF_URL = (
    'https://gitea.radium.group/api/v1/repos/radium/' +
    'project-configuration/git/trees/' +
    'eb4dc314435649737ad343ef82240b96256d5eb8' +
    '?recursive=true&page=1&per_page=5'
)

REFS_SHA = 'eb4dc314435649737ad343ef82240b96256d5eb8'
REFS_PAGE = 1
DEBUG_KEY = 'debug'
REFS_PER_PAGE = 5
TREE_KEY = 'tree'


@pytest.mark.asyncio()
async def test_get_tree_refs_page():
    with aioresponses.aioresponses() as aresp:
        async with aiohttp.ClientSession() as sess:
            aresp.get(
                TEST_REF_URL,
                status=HTTPStatus.OK,
                payload={'debug': 1},
            )

            json = await get_tree_refs_page(
                REFS_SHA,
                REFS_PAGE,
                sess,
                GiteaUrlParams(),
            )
            assert json
            assert json.get(DEBUG_KEY) == 1

            aresp.get(
                TEST_REF_URL,
                status=HTTPStatus.BAD_REQUEST,
                payload={DEBUG_KEY: 1},
                exception=HttpProcessingError(
                    message='test_get_tree_refs_page',
                ),
            )

            json = await get_tree_refs_page(
                REFS_SHA,
                REFS_PAGE,
                sess,
                GiteaUrlParams(),
            )
            assert not json


@pytest.mark.asyncio()
@pytest.mark.parametrize(('total_count', 'pages_count_exp'), [
    (19, 4),
    (11, 3),
    (1, 1),
    (0, 0),
],
)
async def test_get_tree_refs_pages_count(
    total_count: int,
    pages_count_exp: int,
):
    with aioresponses.aioresponses() as aresp:
        async with aiohttp.ClientSession() as sess:
            aresp.get(
                TEST_REF_URL,
                status=HTTPStatus.OK,
                payload={'total_count': total_count},
            )

            pages_count = await get_tree_refs_pages_count(
                REFS_SHA,
                sess,
                GiteaUrlParams(),
            )
            assert pages_count == pages_count_exp


@pytest.mark.asyncio()
async def test_get_tree_refs_pages_count_empty():
    with aioresponses.aioresponses() as aresp:
        async with aiohttp.ClientSession() as sess:
            aresp.get(
                TEST_REF_URL,
                status=HTTPStatus.OK,
                exception=HttpProcessingError(
                    message='test',
                ),
            )

            pages_count = await get_tree_refs_pages_count(
                REFS_SHA,
                sess,
                GiteaUrlParams(),
            )
            assert pages_count == 0


@pytest.mark.asyncio()
async def test_get_tree_data():
    with aioresponses.aioresponses() as aresp:
        async with aiohttp.ClientSession() as sess:
            aresp.get(
                TEST_REF_URL,
                status=HTTPStatus.OK,
                payload={TREE_KEY: 1},
            )

            json = await get_tree_data(
                REFS_SHA,
                sess,
                GiteaUrlParams(),
                REFS_PAGE,
            )
            assert json == 1

            aresp.get(
                TEST_REF_URL,
                status=HTTPStatus.BAD_REQUEST,
                payload={TREE_KEY: 1},
                exception=HttpProcessingError(
                    message='test_get_tree_data',
                ),
            )

            json = await get_tree_data(
                REFS_SHA,
                sess,
                GiteaUrlParams(),
                REFS_PAGE,
            )
            assert not json
