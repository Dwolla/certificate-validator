# -*- coding: utf-8 -*-
"""Base test module."""

import unittest
from unittest.mock import Mock, patch

from certificate_validator import api, logger, main, provider, resources
from certificate_validator.api import AWS
from certificate_validator.provider import Provider, Request, Response


class BaseTestCase(unittest.TestCase):
    def setUp(self):
        super(BaseTestCase, self).setUp()
        self.addCleanup(patch.stopall)


class AWSBaseTestCase(BaseTestCase):
    def setUp(self):
        super(AWSBaseTestCase, self).setUp()
        self.region = 'region'
        self.session = Mock()
        self.mock_session = patch.object(api.boto3, 'Session').start()
        self.mock_session.return_value = self.session
        self.aws = AWS(region=self.region)


class MainBaseTestCase(BaseTestCase):
    def setUp(self):
        super(MainBaseTestCase, self).setUp()
        self.mock_logging = patch.object(logger.logging, 'getLogger').start()
        self.mock_logging.return_value = Mock()
        self.mock_logger = patch.object(main, 'logger').start()
        self.event = {
            'RequestType': '',
            'ServiceToken': '',
            'ResponseURL': '',
            'StackId': '',
            'RequestId': '',
            'ResourceType': '',
            'LogicalResourceId': '',
            'PhysicalResourceId': '',
            'ResourceProperties': {
                'ServiceToken': ''
            },
            'OldResourceProperties': {
                'ServiceToken': ''
            }
        }
        self.request = Mock()
        self.mock_request = patch.object(main, 'Request').start()
        self.mock_request.return_value = self.request
        self.response = Mock()
        self.mock_response = patch.object(main, 'Response').start()
        self.mock_response.return_value = self.response
        self.certificate = Mock()
        self.mock_certificate = patch.object(main, 'Certificate').start()
        self.mock_certificate.return_value = self.certificate
        self.certificate_validator = Mock()
        self.mock_certificate_validator = patch.object(
            main, 'CertificateValidator'
        ).start()
        self.mock_certificate_validator.return_value = \
            self.certificate_validator


class RequestBaseTestCase(BaseTestCase):
    def setUp(self):
        super(RequestBaseTestCase, self).setUp()
        self.kwargs = {
            'RequestType': 'request_type',
            'ServiceToken': 'service_token',
            'ResponseURL': 'response_url',
            'StackId': 'stack_id',
            'RequestId': 'request_id',
            'ResourceType': 'resource_type',
            'LogicalResourceId': 'logical_resource_id',
            'PhysicalResourceId': 'physical_resource_id',
            'ResourceProperties': {
                'ServiceToken': 'service_token'
            },
            'OldResourceProperties': {
                'ServiceToken': 'service_token'
            }
        }
        self.mock_logger = patch.object(provider, 'logger').start()
        self.request = Request(**self.kwargs)


class ResponseBaseTestCase(BaseTestCase):
    def setUp(self):
        super(ResponseBaseTestCase, self).setUp()
        self.kwargs = {
            'Status': 'status',
            'Reason': 'reason',
            'StackId': 'stack_id',
            'RequestId': 'request_id',
            'LogicalResourceId': 'logical_resource_id',
            'PhysicalResourceId': 'physical_resource_id',
            'NoEcho': True,
            'Data': {
                'a': 1,
                'b': 2,
                'c': 3
            }
        }
        self.response = Response(**self.kwargs)


class ProviderBaseTestCase(BaseTestCase):
    def setUp(self):
        super(ProviderBaseTestCase, self).setUp()
        self.request_kwargs = {
            'RequestType': 'request_type',
            'ServiceToken': 'service_token',
            'ResponseURL': 'response_url',
            'StackId': 'stack_id',
            'RequestId': 'request_id',
            'ResourceType': 'resource_type',
            'LogicalResourceId': 'logical_resource_id',
            'PhysicalResourceId': 'physical_resource_id',
            'ResourceProperties': {
                'ServiceToken': 'service_token'
            },
            'OldResourceProperties': {
                'ServiceToken': 'service_token'
            }
        }
        self.request = Request(**self.request_kwargs)
        self.response_kwargs = {
            'Status': 'status',
            'Reason': 'reason',
            'StackId': 'stack_id',
            'RequestId': 'request_id',
            'LogicalResourceId': 'logical_resource_id',
            'PhysicalResourceId': 'physical_resource_id',
            'NoEcho': True,
            'Data': {
                'a': 1,
                'b': 2,
                'c': 3
            }
        }
        self.response = Response(**self.response_kwargs)
        self.provider = Provider(self.request, self.response)
        self.mock_requests = patch.object(provider, 'requests').start()


class CertificateBaseTestCase(AWSBaseTestCase, ProviderBaseTestCase):
    def setUp(self):
        super(CertificateBaseTestCase, self).setUp()
        self.request_kwargs = {
            'RequestType': 'request_type',
            'ServiceToken': 'service_token',
            'ResponseURL': 'response_url',
            'StackId': 'stack_id',
            'RequestId': 'request_id',
            'ResourceType': 'Custom::Certificate',
            'LogicalResourceId': 'logical_resource_id',
            'PhysicalResourceId': 'physical_resource_id',
            'ResourceProperties': {
                'ServiceToken': 'service_token',
                'DomainName': 'certificate-validator.com',
                'SubjectAlternativeNames': ['www.certificate-validator.com']
            },
            'OldResourceProperties': {
                'ServiceToken': 'service_token'
            }
        }
        self.request = Request(**self.request_kwargs)
        self.mock_request = patch.object(provider, 'Request').start()
        self.mock_request.return_value = Mock()
        self.mock_response = patch.object(provider, 'Response').start()
        self.mock_response.return_value = Mock()
        self.mock_request_certificate = patch.object(
            resources.ACM, 'request_certificate'
        ).start()
        self.mock_request_certificate.return_value = {
            'CertificateArn': 'arn:aws:acm:us-east-1:123:certificate/1337',
        }
        self.mock_delete_certificate = patch.object(
            resources.ACM, 'delete_certificate'
        ).start()
        self.mock_delete_certificate.return_value = None


class CertificateValidatorBaseTestCase(AWSBaseTestCase, ProviderBaseTestCase):
    def setUp(self):
        super(CertificateValidatorBaseTestCase, self).setUp()
        self.request_kwargs = {
            'RequestType': 'request_type',
            'ServiceToken': 'service_token',
            'ResponseURL': 'response_url',
            'StackId': 'stack_id',
            'RequestId': 'request_id',
            'ResourceType': 'Custom::CertificateValidator',
            'LogicalResourceId': 'logical_resource_id',
            'PhysicalResourceId': 'physical_resource_id',
            'ResourceProperties': {
                'ServiceToken': 'service_token',
                'CertificateArn': 'arn:aws:acm:us-east-1:123:certificate/1',
            },
            'OldResourceProperties': {
                'ServiceToken': 'service_token',
                'CertificateArn': 'arn:aws:acm:us-east-1:123:certificate/0',
            }
        }
        self.request = Request(**self.request_kwargs)
        self.certificate_arn = 'arn:aws:acm:us-east-1:123:certificate/1337'
        self.mock_request = patch.object(provider, 'Request').start()
        self.mock_request.return_value = Mock()
        self.mock_response = patch.object(provider, 'Response').start()
        self.mock_response.return_value = Mock()
        self.mock_uuid4 = patch.object(resources.uuid, 'uuid4').start()
        self.mock_uuid4.return_value = '1337'
        self.mock_describe_certificate = patch.object(
            resources.ACM, 'describe_certificate'
        ).start()
        self.mock_describe_certificate.return_value = {
            'Certificate': {
                'DomainName': 'certificate-validator.com',
                'DomainValidationOptions': [{
                    'ResourceRecord': {
                        'Name': '_x1.certificate-validator.com.',
                        'Type': 'CNAME',
                        'Value': '_x2.acm-validations.aws.'
                    }
                }]
            }
        }
        self.mock_change_resource_record_sets = patch.object(
            resources.Route53, 'change_resource_record_sets'
        ).start()
        self.mock_get_domain_validation_options = patch.object(
            resources.CertificateValidator, 'get_domain_validation_options'
        ).start()
        self.mock_get_domain_validation_options.return_value = [{
            'DomainName': 'certificate-validator.com',
            'ResourceRecord': {
                'Name': '_x1.certificate-validator.com.',
                'Type': 'CNAME',
                'Value': '_x2.acm-validations.aws.'
            }
        }]
        self.mock_get_hosted_zone_id = patch.object(
            resources.CertificateValidator, 'get_hosted_zone_id'
        ).start()
        self.mock_get_hosted_zone_id.return_value = 'Z23ABC4XYZL05B'
        self.mock_get_change_batch = patch.object(
            resources.CertificateValidator, 'get_change_batch'
        ).start()
        self.mock_get_change_batch.return_value = {
            'Changes': {
                'ResourceRecordSet': {
                    'Name': '_x1.certificate-validator.com.',
                    'Type': 'CNAME',
                    'TTL': 300,
                    'ResourceRecords': [{
                        'Value': '_x2.acm-validations.aws.'
                    }]
                }
            }
        }
