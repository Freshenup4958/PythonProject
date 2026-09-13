import logging

logger = logging.getLogger('books')


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        logger.info(
            'Request: %s %s',
            request.method,
            request.path
        )

        response = self.get_response(request)

        logger.info(
            'Response: %s %s',
            response.status_code,
            request.path
        )

        return response