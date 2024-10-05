
import logging
from django.conf import settings
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)

def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    if response is None:
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return Response({
            "error": "An unexpected error occurred.",
            "detail": str(exc) if settings.DEBUG else "Please contact support."
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Add extra details to the response
    if isinstance(response.data, dict):
        response.data['status_code'] = response.status_code
        
    logger.error(f"Handled exception: {exc}", exc_info=True)
    return response