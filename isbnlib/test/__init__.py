# -*- coding: utf-8 -*-
""""Test battery for 'isbnlib'."""

# If a Google-Books-API-Key is given through a environment variable, add it to the config before starting the tests

import os
from ..config import add_apikey

gapikey = os.environ.get("GOOGLE_BOOKS_API_KEY")
if gapikey:
    add_apikey("goob", gapikey)