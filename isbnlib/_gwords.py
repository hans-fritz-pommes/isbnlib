# -*- coding: utf-8 -*-
"""Use Google to get an ISBN from words from title and author's name."""

import logging
from urllib.parse import quote

from ._core import get_canonical_isbn, get_isbnlike
from .dev import cache, webservice

LOGGER = logging.getLogger(__name__)


@cache
def goos(words):
    """Use DuckDuckGo - HTML to get an ISBN from words from title and author's name.""" # Google is making too complex responses
    service_url = 'https://html.duckduckgo.com/html?q=ISBN+'
    search_url = service_url + quote(words.replace(' ', '+'))

    user_agent = 'Mozilla/5.0' # w3m too old

    content = webservice.query(
        search_url,
        user_agent=user_agent,
        appheaders={
            'Content-Type': 'text/plain; charset="UTF-8"',
            'Content-Transfer-Encoding': 'Quoted-Printable',
        },
    )
    isbns = get_isbnlike(content)
    isbn = ''
    try:
        for item in isbns:
            isbn = get_canonical_isbn(item, output='isbn13')
            if isbn:  # pragma: no cover
                break
    except IndexError:  # pragma: no cover
        pass
    if not isbns or not isbn:  # pragma: no cover
        LOGGER.debug('No ISBN found for %s', words)
    return isbn
