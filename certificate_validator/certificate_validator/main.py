# -*- coding: utf-8 -*-
"""Main AWS Lambda function module."""

import logging

from certificate_validator.logger import logger
from certificate_validator.provider import Request, Response
from certificate_validator.resources import Certificate, CertificateValidator


def handler(event: dict, context: object) -> dict:
    """
    Handle AWS Lambda function event.

    :param event: event data
    :type event: dict
    :param context: runtime information of the AWS Lambda function
    :type context: LambdaContext object
    """
    logger.debug('Request: {}'.format(event))

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
        logger.debug('Response: {}'.format(certificate.response.dict()))

    if request.resource_type == 'Custom::CertificateValidator':
        certificate_validator = CertificateValidator(request, response)
        certificate_validator.handler()
        logger.debug(
            'Response: {}'.format(certificate_validator.response.dict())
        )
