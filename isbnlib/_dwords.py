# -*- coding: utf-8 -*-
"""Use DuckDuckGo to get an ISBN from words from title and author's name."""

import logging
from urllib.parse import quote

from ._core import get_canonical_isbn, get_isbnlike
from .dev import cache, webservice

LOGGER = logging.getLogger(__name__)


@cache
def doos(words):
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
    possible_isbns_to_return={}
    for item in isbns:
        isbn = get_canonical_isbn(item, output='isbn13')
        if isbn:
            if isbn in possible_isbns_to_return:
                possible_isbns_to_return[isbn]+=1
            else:
                possible_isbns_to_return[isbn]=1
    if len(possible_isbns_to_return)>0:
        max_count=0
        for e in possible_isbns_to_return:
            if possible_isbns_to_return[e]>=max_count: # >= because the isbns are rather at the end of the search
                isbn=e
                max_count=possible_isbns_to_return[e]
    else:
        LOGGER.debug('No ISBN found for %s', words)
        isbn=''
    return isbn
