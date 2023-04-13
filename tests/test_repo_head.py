"""Test repo_head.py functions."""
from http import HTTPStatus

import aiohttp
import aioresponses
import pytest
from aiohttp.http_exceptions import HttpProcessingError

from gitea.repo_head import get_ref_sha
from gitea.url_params import GiteaUrlParams

TEST_REF_SHA = 'eb4dc314435649737ad343ef82240b96256d5eb8'


def get_ref_stub_data() -> list:
    return [
        {
            'ref': 'refs/heads/master',
            'url': (
                'https://gitea.radium.group/api/v1/repos/radium/' +
                'project-configuration/git/refs/heads/master'
            ),
            'object': {
                'type': 'commit',
                'sha': TEST_REF_SHA,
            },
        },
    ]


def get_ref_stub_data_empty() -> list:
    return []


TEST_REF_URL = (
    'https://gitea.radium.group/api/v1/' +
    'repos/radium/project-configuration/git/refs'
)


@pytest.mark.asyncio()
async def test_get_ref_sha():
    with aioresponses.aioresponses() as aresp:
        async with aiohttp.ClientSession() as sess:
            aresp.get(
                TEST_REF_URL,
                status=HTTPStatus.OK,
                payload=get_ref_stub_data(),
            )

            sha = await get_ref_sha(sess, GiteaUrlParams())
            assert sha == TEST_REF_SHA

            aresp.get(
                TEST_REF_URL,
                status=HTTPStatus.BAD_REQUEST,
                payload=get_ref_stub_data(),
            )
            sha = await get_ref_sha(sess, GiteaUrlParams())
            assert sha is None

            aresp.get(
                TEST_REF_URL,
                status=HTTPStatus.OK,
                payload=get_ref_stub_data_empty(),
            )
            await get_ref_sha(sess, GiteaUrlParams())
            assert not sha

            aresp.get(
                TEST_REF_URL,
                status=HTTPStatus.BAD_REQUEST,
                payload=get_ref_stub_data_empty(),
                exception=HttpProcessingError(message='test_get_ref_sha'),
            )

            with pytest.raises(HttpProcessingError):
                await get_ref_sha(sess, GiteaUrlParams())
