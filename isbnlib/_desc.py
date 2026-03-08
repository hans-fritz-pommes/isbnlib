# -*- coding: utf-8 -*-
"""Return a small description of the book."""

import logging
from json import loads

from .dev import cache
from .dev._exceptions import ISBNLibHTTPError, WrongAPIKeyError
from .dev.webservice import query as wquery

from .config import apikeys

LOGGER = logging.getLogger(__name__)

UA = 'isbnlib (gzip)'
SERVICE_URL = (
    'https://www.googleapis.com/books/v1/volumes?q={isbn}'
    '&fields=items/volumeInfo(description)&maxResults=1&key={api_key}')


# pylint: disable=broad-except
@cache
def goo_desc(isbn):
    """Get description from Google Books API."""
    api_key = ""
    if apikeys.get("goob", False):
        api_key = apikeys["goob"]

    try:
        data = wquery(SERVICE_URL.format(isbn='isbn:' + isbn, api_key=api_key), user_agent=UA)
        if not data:
            # some times this works (see #119)
            data = wquery(SERVICE_URL.format(isbn=isbn, api_key=api_key), user_agent=UA)
        error_to_raise = None
    except ISBNLibHTTPError as error:
        if error.code == 400 and api_key:
            error_to_raise = WrongAPIKeyError(error.msg)
        else:
            error_to_raise = error
    finally:
        if error_to_raise:
            raise error_to_raise

    try:
        content = loads(data)
        content = content['items'][0]['volumeInfo']['description']
        return content if content else ''
    except Exception:  # pragma: no cover
        LOGGER.debug('No description for %s', isbn)
        return ''
