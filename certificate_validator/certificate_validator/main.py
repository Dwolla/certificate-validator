# -*- coding: utf-8 -*-
"""Main AWS Lambda function module."""

from certificate_validator.logger import logger
from certificate_validator.provider import Request, Response
from certificate_validator.resources import Certificate, CertificateValidator
from certificate_validator.version import version

DEFAULT_LOG_LEVEL = 'INFO'


def handler(event: dict, context: object) -> dict:
    """
    Handle AWS Lambda function event.

    :param event: event data
    :type event: dict
    :param context: runtime information of the AWS Lambda function
    :type context: LambdaContext object
    """
    # Set log level manually before anything else
    props = event.get('ResourceProperties', {})
    logger.setLevel(props.get('LogLevel', DEFAULT_LOG_LEVEL))

    logger.info('Starting certificate-validator v%s', version)
    logger.debug('Request: %s', event)

    request = Request(**event)

    response = Response(
        request_id=request.request_id,
        stack_id=request.stack_id,
        logical_resource_id=request.logical_resource_id,
        physical_resource_id=request.physical_resource_id
    )

    if request.resource_type == 'Custom::Certificate':
        certificate = Certificate(request, response)
        certificate.handler()
        logger.debug('Response: %s', certificate.response.dict())

    if request.resource_type == 'Custom::CertificateValidator':
        certificate_validator = CertificateValidator(request, response)
        certificate_validator.handler()
        logger.debug('Response: %s', certificate_validator.response.dict())
