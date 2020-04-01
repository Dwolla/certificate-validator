# -*- coding: utf-8 -*-
"""Tests for the `main` module."""

from unittest import mock

from certificate_validator import main
from certificate_validator.main import handler

from .base import MainBaseTestCase


class MainTestCase(MainBaseTestCase):
    def setUp(self):
        super(MainTestCase, self).setUp()

    def test_handler_nop(self):
        handler(self.event, None)
        self.mock_logger.debug.assert_called_with('Request: %s', self.event)
        self.mock_request.assert_called_with(**self.event)
        self.mock_response.assert_called_with(
            request_id=self.request.request_id,
            stack_id=self.request.stack_id,
            logical_resource_id=self.request.logical_resource_id,
            physical_resource_id=self.request.physical_resource_id
        )

    def test_handler_no_log_level(self):
        handler(self.event, None)
        self.mock_logger.setLevel.assert_called_with(main.DEFAULT_LOG_LEVEL)

    def test_handler_log_level_DEBUG(self):
        self.event.setdefault('ResourceProperties', {})['LogLevel'] = 'DEBUG'
        handler(self.event, None)
        self.mock_logger.setLevel.assert_called_with('DEBUG')

    def test_handler_log_level_INFO(self):
        self.event.setdefault('ResourceProperties', {})['LogLevel'] = 'INFO'
        handler(self.event, None)
        self.mock_logger.setLevel.assert_called_with('INFO')

    def test_handler_certificate(self):
        self.event['ResourceType'] = 'Custom::Certificate'
        self.request.resource_type = 'Custom::Certificate'
        handler(self.event, None)
        self.mock_logger.debug.assert_has_calls([
            mock.call('Request: %s', self.event),
            mock.call('Response: %s', self.certificate.response.dict())
        ])
        self.mock_request.assert_called_with(**self.event)
        self.mock_response.assert_called_with(
            request_id=self.request.request_id,
            stack_id=self.request.stack_id,
            logical_resource_id=self.request.logical_resource_id,
            physical_resource_id=self.request.physical_resource_id
        )
        self.mock_certificate.assert_called_with(self.request, self.response)
        self.certificate.handler.assert_called_once()

    def test_handler_certificate_validator(self):
        self.event['ResourceType'] = 'Custom::CertificateValidator'
        self.request.resource_type = 'Custom::CertificateValidator'
        handler(self.event, None)
        self.mock_logger.debug.assert_has_calls([
            mock.call('Request: %s', self.event),
            mock.call(
                'Response: %s', self.certificate_validator.response.dict()
            )
        ])
        self.mock_request.assert_called_with(**self.event)
        self.mock_response.assert_called_with(
            request_id=self.request.request_id,
            stack_id=self.request.stack_id,
            logical_resource_id=self.request.logical_resource_id,
            physical_resource_id=self.request.physical_resource_id
        )
        self.mock_certificate_validator.assert_called_with(
            self.request, self.response
        )
        self.certificate_validator.handler.assert_called_once()
