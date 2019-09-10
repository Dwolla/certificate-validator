# -*- coding: utf-8 -*-
"""Tests for the `exceptions` module."""

from certificate_validator.exceptions import (
    CertificateValidatorException, UnknownRequestType
)

from .base import BaseTestCase


class CertificateValidatorExceptionTestCase(BaseTestCase):
    def setUp(self):
        super(CertificateValidatorExceptionTestCase, self).setUp()

    def test_init(self):
        e = CertificateValidatorException()
        self.assertEqual('', e.msg)


class UnknownRequestTypeTestCase(BaseTestCase):
    def setUp(self):
        super(UnknownRequestTypeTestCase, self).setUp()

    def test_init(self):
        e = UnknownRequestType()
        self.assertEqual(
            'Unknown RequestType: Must be one of: Create, Update, or Delete.',
            e.msg
        )
