"""Functions for parsing the HEAD or another ref through gitea REST API."""
import logging
from http import HTTPStatus

import aiohttp

from gitea.config import REF_HEAD
from gitea.url_params import GiteaUrlParams


async def get_ref_sha(
    sess: aiohttp.ClientSession,
    urlp: GiteaUrlParams,
    ref: str = REF_HEAD,
) -> str:
    """Get SHA for selected ref (HEAD) of the gitea repository.

    :param sess: Active session.
    :param urlp: Base URL parameters for repository (pagination etc.).
    :param ref: Name of ref. For example refs/heads/master.
    :returns: SHA of the ref or an empty string if ref not found
    """
    url = '{0}/repos/{1}/{2}/git/refs'.format(
        urlp.base_api_url,
        urlp.owner,
        urlp.project,
    )
    msg = 'GET refs from {0}'.format(url)
    logging.info(msg)

    try:
        response = await sess.get(url)
    except Exception as ex:
        logging.exception('Exception occurred')
        raise ex

    if response.status != HTTPStatus.OK:
        msg = "Response status: {0}".format(response.status)
        logging.error(msg)
        return None

    json = await response.json()
    return parse_ref(json, ref)


def parse_ref(json: dict, ref_to_find: str) -> str:
    """Parse JSON array of refs for specific ref name.

    :param json: JSON dict with all refs of repo.
    :param ref_to_find: Name of the ref
    :returns: SHA of the ref or an empty string if ref not found
    """
    sha = ''
    fl = filter(lambda el: el.get('ref') == ref_to_find, json)
    try:
        ref = next(fl)
    except StopIteration:
        msg = 'parse_sha: {0} not found'.format(ref_to_find)
        logging.error(msg)
        return sha

    ob = ref.get('object')
    sha = ob.get('sha')
    msg = 'HEAD SHA {0}'.format(sha)
    logging.info(msg)

    return sha
