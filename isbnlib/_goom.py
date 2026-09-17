# -*- coding: utf-8 -*-
"""Query the Google Books (JSON API v1) for metadata."""

import logging
from urllib.parse import quote

from .dev import cache, stdmeta
from .dev._exceptions import NoDataForSelectorError, RecordMappingError
from .dev.webquery import query as wquery

from .config import apikeys

UA = 'isbnlib (gzip)'
SERVICE_URL = (
    'https://www.googleapis.com/books/v1/volumes?q={words}'
    '&fields=items/volumeInfo(title,authors,publisher,publishedDate,'
    'language,industryIdentifiers)&maxResults=10&key={api_key}')
LOGGER = logging.getLogger(__name__)


# pylint: disable=broad-except
def _mapper(record):
    """Map canonical <- record."""
    # canonical:
    # -> ISBN-13, Title, Authors, Publisher, Year, Language
    try:
        # mapping: canonical <- records
        if 'industryIdentifiers' not in record:  # pragma: no cover
            return {}
        canonical = {}
        isbn = None
        for ident in record['industryIdentifiers']:
            if ident['type'] == 'ISBN_13':
                isbn = ident['identifier']
                break
        if not isbn:  # pragma: no cover
            return {}
        canonical['ISBN-13'] = isbn
        canonical['Title'] = record.get('title', '').replace(' :', ':')
        canonical['Authors'] = record.get('authors', [])
        canonical['Publisher'] = record.get('publisher', '')
        if 'publishedDate' in record and len(record['publishedDate']) >= 4:
            canonical['Year'] = record['publishedDate'][0:4]
        else:  # pragma: no cover
            canonical['Year'] = ''
        canonical['Language'] = record.get('language', '')
    except Exception:  # pragma: no cover
        raise RecordMappingError(isbn)
    # call stdmeta for extra cleaning and validation
    return stdmeta(canonical)


# pylint: disable=broad-except
def _records(words, data):
    """Classify (canonically) the parsed data."""
    # put the selected data in records
    try:
        recs = [d['volumeInfo'] for d in data['items']]
    except Exception:  # pragma: no cover
        LOGGER.debug('NoDataForSelectorError for (%s)', words)
        raise NoDataForSelectorError(words)
    # map canonical <- records
    return [_mapper(r) for r in recs if _mapper(r)]


@cache
def query(words):
    """Query the Google Books (JSON API v1) for metadata."""
    api_key=apikeys.get("goob","")
    words.replace(' ', '+')
    words = quote(words)
    data = wquery(SERVICE_URL.format(words=words,api_key=api_key), UA)
    return _records(words, data) if data else {}
