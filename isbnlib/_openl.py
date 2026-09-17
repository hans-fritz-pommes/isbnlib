# -*- coding: utf-8 -*-
"""Query the openlibrary.org service for metadata."""

import logging
import re

from .dev import stdmeta
from .dev._exceptions import DataNotFoundAtServiceError, RecordMappingError
from .dev.webquery import query as wquery

UA = 'isbnlib (gzip) (valarmmail@gmx.de)'
SERVICE_URL = ('http://openlibrary.org/search.json?q='
               '{isbn}&fields=title,subtitle,author_name,publisher,first_publish_year,language')
LOGGER = logging.getLogger(__name__)


# pylint: disable=broad-except
def _mapper(isbn, records):
    """Map canonical <- records."""
    # canonical:
    # -> ISBN-13, Title, Authors, Publisher, Year, Language
    try:
        # mapping: canonical <- records
        canonical = {}
        canonical['ISBN-13'] = isbn
        title = records.get('title', '').replace(' :', ':')
        subtitle = records.get('subtitle', '')
        title = title + ' - ' + subtitle if subtitle else title
        canonical['Title'] = title
        canonical['Authors'] = [
            a for a in records.get(
                'author_name',[]
            )
        ]
        canonical['Publisher'] = ''
        publs = records.get('publisher', [])
        if publs:
            canonical['Publisher'] = publs[0]
        canonical['Language'] = ''
        langs = records.get('language', [])
        if langs:
            canonical['Language'] = langs[0]
        canonical['Year'] = str(records.get('first_publish_year',''))
    except Exception:  # pragma: no cover
        LOGGER.debug('RecordMappingError for %s with data %s', isbn, records)
        raise RecordMappingError(isbn)
    # call stdmeta for extra cleaning and validation
    return stdmeta(canonical)


# pylint: disable=broad-except
def _records(isbn, data):
    """Classify (canonically) the parsed data."""
    try:
        # put the selected data in records
        records = data[0]
    except IndexError:  # pragma: no cover
        # don't raise exception!
        LOGGER.debug('No data from "openl" for isbn %s', isbn)
        return {}

    # map canonical <- records
    return _mapper(isbn, records)


def query(isbn):
    """Query the openlibrary.org service for metadata."""
    try:
        data = wquery(SERVICE_URL.format(isbn=isbn), user_agent=UA)
        data = data.get("docs", [])
    except DataNotFoundAtServiceError:
        LOGGER.debug('No data from "openl" for isbn %s', isbn)
        return {}
    return _records(isbn, data)
