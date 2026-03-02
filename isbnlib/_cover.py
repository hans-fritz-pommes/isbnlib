# -*- coding: utf-8 -*-
"""Get image links of the book's cover."""

import logging

from .dev import cache
from .dev.webquery import query as wquery
from .dev._exceptions import ISBNLibHTTPError, WrongAPIKeyError

from .config import apikeys

LOGGER = logging.getLogger(__name__)

UA = 'isbnlib (gzip)'
SERVICE_URL = (
    'https://www.googleapis.com/books/v1/volumes?q={isbn}'
    '&fields=items/volumeInfo(imageLinks)&maxResults=1&key={api_key}')


@cache
def cover(isbn):
    """Get the urls for covers from Google Books."""
    api_key=""
    if apikeys.get("goob",False):
        api_key=apikeys["goob"]

    try:
        data = wquery(SERVICE_URL.format(isbn='isbn:' + isbn, api_key=api_key), user_agent=UA)
        if not data:
            # some times this works (see #119)
            data = wquery(SERVICE_URL.format(isbn=isbn, api_key=api_key), user_agent=UA)
        error_to_raise=None
    except ISBNLibHTTPError as error:
        if error.code==400 and api_key:
            error_to_raise=WrongAPIKeyError(error.msg)
        else:
            error_to_raise=error
    finally:
        if error_to_raise:
            raise error_to_raise

    urls = {}
    try:
        urls = data['items'][0]['volumeInfo']['imageLinks']
    except (KeyError, IndexError):  # pragma: no cover
        LOGGER.debug('No cover img data for %s', isbn)
    return urls
