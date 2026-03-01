# -*- coding: utf-8 -*-
"""Query the Google Books (JSON API v1) service for metadata."""

import logging

from .dev import stdmeta
from .dev._exceptions import ISBNNotConsistentError, RecordMappingError, ISBNLibHTTPError, WrongAPIKeyError
from .dev.webquery import query as wquery

from .config import apikeys

UA = 'isbnlib (gzip)'
SERVICE_URL = (
    'https://www.googleapis.com/books/v1/volumes?q={isbn}'
    '&fields=items/volumeInfo(title,subtitle,authors,publisher,publishedDate,'
    'language,industryIdentifiers,description,imageLinks)&maxResults=1&key={api_key}')
LOGGER = logging.getLogger(__name__)


# pylint: disable=broad-except
def _mapper(isbn, records):
    """Map: canonical <- records."""
    # canonical: ISBN-13, Title, Authors, Publisher, Year, Language
    try:
        canonical = {}
        canonical['ISBN-13'] = isbn
        title = records.get('title', '').replace(' :', ':')
        subtitle = records.get('subtitle', '')
        title = title + ' - ' + subtitle if subtitle else title
        canonical['Title'] = title
        canonical['Authors'] = records.get('authors', [''])
        # see issue #64
        canonical['Publisher'] = records.get('publisher', '').strip('"')
        if 'publishedDate' in records and len(records['publishedDate']) >= 4:
            canonical['Year'] = records['publishedDate'][0:4]
        else:  # pragma: no cover
            canonical['Year'] = ''
        canonical['Language'] = records.get('language', '')
    except Exception:  # pragma: no cover
        LOGGER.debug('RecordMappingError for %s with data %s', isbn, records)
        raise RecordMappingError(isbn)
    # call stdmeta for extra cleaning and validation
    return stdmeta(canonical)


def _records(isbn, data):
    """Classify (canonically) the parsed data."""
    # put the selected data in records
    try:
        recs = data['items'][0]['volumeInfo']
    except Exception:  # pragma: no cover
        # don't raise exception!
        LOGGER.debug('No data from "goob" for isbn %s', isbn)
        return {}
    # consistency check (isbn request = isbn response)
    if recs:
        ids = recs.get('industryIdentifiers', '')
        if 'ISBN_13' in repr(ids) and isbn not in repr(ids):  # pragma: no cover
            LOGGER.debug('ISBNNotConsistentError for %s (%s)', isbn, repr(ids))
            msg = f'{isbn} not in {ids!r}'
            raise ISBNNotConsistentError(msg)
    else:
        return {}  # pragma: no cover
    # map canonical <- records
    return _mapper(isbn, recs)


# pylint: disable=broad-except
def query(isbn):
    """Query the Google Books (JSON API v1) service for metadata."""
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

    if not data:
        LOGGER.debug('No data from "goob" for isbn %s', isbn)
        return {}
    return _records(isbn, data)
