from rest_framework.views import exception_handler
from rest_framework import exceptions

from config.settings.base import logger


def custom_exception_handler(exc, context):
    print('ER|%s| %s' % (exc, context))
    logger.error(f'{exc}, {context}')

    response = exception_handler(exc, context)

    if response is not None:
        if isinstance(exc, exceptions.ParseError):
            msg = exc.detail
        elif isinstance(exc, exceptions.AuthenticationFailed):
            msg = exc.detail
        elif isinstance(exc, exceptions.NotAuthenticated):
            msg = 'No Auth'
        elif isinstance(exc, exceptions.PermissionDenied):
            msg = exc.detail
        elif isinstance(exc, exceptions.NotFound):
            msg = exc.detail
        elif isinstance(exc, exceptions.MethodNotAllowed):
            msg = exc.detail
        elif isinstance(exc, exceptions.NotAcceptable):
            msg = exc.detail
        elif isinstance(exc, exceptions.UnsupportedMediaType):
            msg = exc.detail
        elif isinstance(exc, exceptions.Throttled):
            msg = exc.detail
        elif isinstance(exc, exceptions.ValidationError):
            msg = exc.detail
        elif isinstance(exc, exceptions.APIException):
            msg = exc.detail

        response.data['message'] = msg

        try:
            del response.data['detail']
        except Exception:
            pass

        return response
    else:
        return response
