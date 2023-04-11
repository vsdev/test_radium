"""Functions for parsing the HEAD or another ref through gitea REST API."""
import logging

import aiohttp

from gitea.config import REF_HEAD
from gitea.url_params import GiteaUrlParams


async def get_head_sha(
    sess: aiohttp.ClientSession,
    urlp: GiteaUrlParams,
    ref=REF_HEAD,
) -> str:
    """Get SHA for selected ref (HEAD) of the gitea repository."""
    url = '{0}/repos/{1}/{2}/git/refs'.format(
        urlp.base_api_url,
        urlp.owner,
        urlp.project,
    )
    logging.info('GET refs from {0}'.format(url))

    try:
        response = await sess.get(url)
    except Exception as ex:
        logging.exception(ex)
        return ''

    json = await response.json()
    return parse_sha(json, ref)


def parse_sha(json: dict, ref_to_find: str) -> str:
    """Parse JSON array of refs for specific ref name."""
    sha = ''
    fl = filter(lambda el: el.get('ref') == ref_to_find, json)
    try:
        ref = next(fl)
    except StopIteration:
        logging.error('parse_sha: {0} not found'.format(ref_to_find))
        return sha

    except Exception as ex:
        logging.exception(ex)
        return sha

    ob = ref.get('object')
    sha = ob.get('sha')
    logging.info('HEAD SHA {0}'.format(sha))

    return sha
