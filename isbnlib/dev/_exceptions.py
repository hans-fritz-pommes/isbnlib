# -*- coding: utf-8 -*-
"""Exceptions for 'isbnlib.dev'.

The classes in isbnlib.dev should use the exceptions below.
"""

# TODO(MV) merge these exceptions with the top exceptions on version 4.

from .._exceptions import ISBNLibException


# pylint: disable=super-init-not-called
class ISBNLibDevException(ISBNLibException):
    """Base class for isbnlib.dev exceptions.

    This exception should not be raised directly,
    only subclasses of this exception should be used!
    """

    def __init__(self, msg=None):
        self.msg=msg
        if msg:
            self.message = f'{self.message} ({msg})'

    def __str__(self):
        return getattr(self, 'message', '')  # pragma: no cover


class ISBNLibHTTPError(ISBNLibDevException):
    """Exception raised for HTTP related errors."""

    message = 'an HTTP error has occurred'

    def __init__(self, msg=None, code=None):
        self.code=code
        if self.code:
            msg=f'{self.code}: {msg}'
        ISBNLibDevException.__init__(self,msg)


class ISBNLibURLError(ISBNLibDevException):
    """Exception raised for URL related errors."""

    message = 'an URL error has occurred'


class DataNotFoundAtServiceError(ISBNLibDevException):
    """Exception raised when there is no target data from the service."""

    message = 'the target data was not found at this service'


class ServiceIsDownError(ISBNLibDevException):
    """Exception raised when the service is not available."""

    message = 'the service is down (try later)'


class DataWrongShapeError(ISBNLibDevException):
    """Exception raised when the data hasn't the expected format."""

    message = "the data hasn't the expected format"


class NoDataForSelectorError(ISBNLibDevException):
    """Exception raised when there is no data for the selector."""

    message = 'no data for this selector'


class NotValidMetadataError(ISBNLibDevException):
    """Exception raised when the metadata hasn't the expected format."""

    message = "the metadata hasn't the expected format"


class ISBNNotConsistentError(ISBNLibDevException):
    """Exception raised when the isbn request != isbn response."""

    message = 'isbn request != isbn response'


class RecordMappingError(ISBNLibDevException):
    """Exception raised when the mapping records -> canonical doesn't work."""

    message = "the mapping `canonical <- records` doesn't work"


class NoAPIKeyError(ISBNLibDevException):
    """Exception raised when the API Key for a service is not found."""

    message = 'this service needs an API key'

class WrongAPIKeyError(ISBNLibDevException):
    """Exception raised when the API Key for a service was wrong."""

    message = 'this API key was wrong'


# pylint: disable=redefined-builtin
class FileNotFoundError(ISBNLibDevException):
    """Exception raised when a given file doesn't exist."""

    message = "the file wasn't found"
