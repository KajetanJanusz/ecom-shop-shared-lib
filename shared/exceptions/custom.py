from http import HTTPStatus

from base import BaseHttpException


class NotFoundError(BaseHttpException):
    code = HTTPStatus.NOT_FOUND
    error_code = HTTPStatus.NOT_FOUND
    message = HTTPStatus.NOT_FOUND.description


class MultipleResultsError(BaseHttpException):
    code = HTTPStatus.CONFLICT
    error_code = HTTPStatus.CONFLICT
    message = HTTPStatus.CONFLICT.description
