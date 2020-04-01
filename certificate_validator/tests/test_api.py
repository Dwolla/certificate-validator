# -*- coding: utf-8 -*-
"""Tests for the `api` module."""

from datetime import datetime
from unittest.mock import Mock

from certificate_validator.api import ACM, Route53, ValidationMethod

from .base import AWSBaseTestCase, BaseTestCase


class ValidationMethodTestCase(BaseTestCase):
    def setUp(self):
        super(ValidationMethodTestCase, self).setUp()

    def test_class(self):
        self.assertEqual('DNS', ValidationMethod.DNS.value)
        self.assertEqual('EMAIL', ValidationMethod.EMAIL.value)


class AWSTestCase(AWSBaseTestCase):
    def setUp(self):
        super(AWSTestCase, self).setUp()

    def test_get_session(self):
        self.aws._get_session()
        self.mock_session.assert_called_with(region_name='region')

    def test_get_client(self):
        self.aws._get_client()
        self.session.client.assert_called_with(None, use_ssl=True)


class ACMTestCase(AWSBaseTestCase):
    def setUp(self):
        super(ACMTestCase, self).setUp()
        self.acm = ACM()
        self.acm.client = Mock()
        self.acm.waiter = Mock()

    def test_request_certificate(self):
        expected = {'CertificateArn': 'string'}
        self.acm.client.request_certificate.return_value = {
            'CertificateArn': 'string'
        }
        actual = self.acm.request_certificate(
            'example.com', ['www.example.com']
        )
        self.acm.client.request_certificate.assert_called_with(
            DomainName='example.com',
            SubjectAlternativeNames=['www.example.com'],
            ValidationMethod='DNS'
        )
        self.assertEqual(expected, actual)

    def test_request_certificate_no_san(self):
        expected = {'CertificateArn': 'string'}
        self.acm.client.request_certificate.return_value = {
            'CertificateArn': 'string'
        }
        actual = self.acm.request_certificate('example.com', [])
        self.acm.client.request_certificate.assert_called_with(
            DomainName='example.com', ValidationMethod='DNS'
        )
        self.assertEqual(expected, actual)

    def test_delete_certificate(self):
        certificate_arn = \
            'arn:aws:acm:region:account-id:certificate/certificate-id'
        expected = None
        self.acm.client.delete_certificate.return_value = None
        actual = self.acm.delete_certificate(certificate_arn)
        self.acm.client.delete_certificate.assert_called_with(
            CertificateArn=certificate_arn
        )
        self.assertEqual(expected, actual)

    def test_describe_certificate(self):
        certificate_arn = \
            'arn:aws:acm:region:account-id:certificate/certificate-id'
        expected = {
            'Certificate': {
                'CertificateArn': certificate_arn,
                'DomainName': 'example.com',
                'SubjectAlternativeNames': ['www.example.com', ]
            }
        }
        self.acm.client.describe_certificate.return_value = {
            'Certificate': {
                'CertificateArn': certificate_arn,
                'DomainName': 'example.com',
                'SubjectAlternativeNames': ['www.example.com', ]
            }
        }
        actual = self.acm.describe_certificate(certificate_arn)
        self.acm.client.describe_certificate.assert_called_with(
            CertificateArn=certificate_arn
        )
        self.assertEqual(expected, actual)

    def test_wait(self):
        certificate_arn = \
            'arn:aws:acm:region:account-id:certificate/certificate-id'
        self.acm.wait(certificate_arn)
        self.acm.waiter.wait.assert_called_with(
            CertificateArn=certificate_arn,
            WaiterConfig={
                'Delay': 5,
                'MaxAttempts': 60
            }
        )


class Route53TestCase(AWSBaseTestCase):
    def setUp(self):
        super(Route53TestCase, self).setUp()
        self.route53 = Route53()
        self.route53.client = Mock()

    def test_change_resource_record_sets(self):
        change_batch = {
            'Changes': {
                'Action': 'CREATE',
                'ResourceRecordSet': {
                    'Name': 'string',
                    'Type': 'CNAME',
                    'TTL': 300,
                    'ResourceRecords': [{
                        'Value': 'string'
                    }]
                }
            }
        }
        expected = {
            'ChangeInfo': {
                'Id': 'string',
                'Status': 'INSYNC',
                'SubmittedAt': datetime(1970, 1, 1),
                'Comment': 'string'
            }
        }
        self.route53.client.change_resource_record_sets.return_value = {
            'ChangeInfo': {
                'Id': 'string',
                'Status': 'INSYNC',
                'SubmittedAt': datetime(1970, 1, 1),
                'Comment': 'string'
            }
        }
        actual = self.route53.change_resource_record_sets(
            'Z23ABC4XYZL05B', change_batch
        )
        self.route53.client.change_resource_record_sets.assert_called_with(
            HostedZoneId='Z23ABC4XYZL05B', ChangeBatch=change_batch
        )
        self.assertEqual(expected, actual)

    def test_list_hosted_zones_by_name(self):
        expected = {
            'HostedZones': [{
                'Id': 'string',
                'Name': 'string',
            }]
        }
        self.route53.client.list_hosted_zones_by_name.return_value = {
            'HostedZones': [{
                'Id': 'string',
                'Name': 'string',
            }]
        }
        actual = self.route53.list_hosted_zones_by_name('example.com')
        self.route53.client.list_hosted_zones_by_name.assert_called_with(
            DNSName='example.com', MaxItems='1'
        )
        self.assertEqual(expected, actual)
