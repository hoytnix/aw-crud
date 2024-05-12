import re
try:
    from urlparse import urljoin
except ImportError:
    from urllib.parse import urljoin

from flask import url_for, request
from unidecode import unidecode

from hoyt.extensions import Freezer
from hoyt.app import create_app
from hoyt.settings import settings

_punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.:]+')


def all_urls():
    app = create_app()
    freezer = Freezer(app, with_static_files=False)
    return [url for url in freezer.all_urls()]


def canonical_url_for(endpoint, **values):
    canonical_url = settings()['CANONICAL_URL']
    return urljoin(canonical_url, url_for(endpoint, **values))


def canonical_request_url():
    canonical_url = settings()['CANONICAL_URL']
    return urljoin(canonical_url, request.path)


def slugify(text, delim=u'-'):
    """Return an ASCII-only slug.

    Lovingly taken from FlaskBB. <@shanks>
    License: BSD 3-Clause

    Args:
        text (str): text to "slugify".
        delim (str): Default '-'. Delimiter for whitespace.

    Returns:
        str: normalized, delimited string for urls.
    """

    text = text.replace('.', '')
    text = unidecode(text)
    result = []
    for word in _punct_re.split(text.lower()):
        result.append(word)
    return delim.join(result)
