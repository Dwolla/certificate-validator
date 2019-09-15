# -*- coding: utf-8 -*-
"""Tests for the `resources` module."""

from unittest.mock import call, patch

from botocore import exceptions

from certificate_validator import resources
from certificate_validator.resources import (
    Action, Certificate, CertificateMixin, CertificateValidator
)

from .base import (
    BaseTestCase, CertificateBaseTestCase, CertificateValidatorBaseTestCase
)


class ActionTestCase(BaseTestCase):
    def setUp(self):
        super(ActionTestCase, self).setUp()

    def test_class(self):
        self.assertEqual('CREATE', Action.CREATE.value)
        self.assertEqual('UPSERT', Action.UPSERT.value)
        self.assertEqual('DELETE', Action.DELETE.value)


class CertificateMixinTestCase(BaseTestCase):
    def setUp(self):
        super(CertificateMixinTestCase, self).setUp()

    def test_is_valid_arn(self):
        valid_arn = 'arn:aws:acm:us-east-1:123:certificate/1337'
        self.assertTrue(CertificateMixin().is_valid_arn(valid_arn))
        invalid_arn = 'invalid'
        self.assertFalse(CertificateMixin().is_valid_arn(invalid_arn))


class CertificateTestCase(CertificateBaseTestCase):
    def setUp(self):
        super(CertificateTestCase, self).setUp()

    def test_init(self):
        c = Certificate(self.request, self.response)
        self.assertEqual(self.request, c.request)
        self.assertEqual(self.response, c.response)

    def test_create_success(self):
        c = Certificate(self.request, self.mock_response)
        c.create()
        self.mock_request_certificate.assert_called_with(
            domain_name='certificate-validator.com',
            subject_alternative_names=['www.certificate-validator.com'],
        )
        self.mock_response.set_status.assert_called_with(success=True)
        self.mock_response.set_physical_resource_id.assert_called_with(
            physical_resource_id='arn:aws:acm:us-east-1:123:certificate/1337'
        )
        self.mock_response.set_data.assert_called_with({
            'CertificateArn': 'arn:aws:acm:us-east-1:123:certificate/1337'
        })

    def test_create_failed(self):
        c = Certificate(self.request, self.mock_response)
        self.mock_request_certificate.side_effect = exceptions.ClientError(
            error_response={'Error': {
                'Code': '1337',
                'Message': 'Message'
            }},
            operation_name='Operation'
        )
        c.create()
        self.mock_request_certificate.assert_called_with(
            domain_name='certificate-validator.com',
            subject_alternative_names=['www.certificate-validator.com'],
        )
        self.mock_response.set_status.assert_called_with(success=False)
        reason = \
            'An error occurred (1337) when calling the Operation operation: ' \
            'Message'
        self.mock_response.set_reason.assert_called_with(reason=reason)

    def test_update(self):
        c = Certificate(self.request, self.response)
        mock_create = patch.object(c, 'create').start()
        c.update()
        mock_create.assert_called_once()

    def test_delete_success_certificate_does_not_exist(self):
        self.mock_request.physical_resource_id = ''
        c = Certificate(self.mock_request, self.mock_response)
        c.delete()
        self.mock_response.set_status.assert_called_with(success=True)
        self.mock_response.set_reason.assert_called_with(
            reason='Certificate does not exist.'
        )

    def test_delete_success(self):
        self.mock_request.physical_resource_id = \
            'arn:aws:acm:us-east-1:123:certificate/1337'
        c = Certificate(self.mock_request, self.mock_response)
        c.delete()
        self.mock_delete_certificate.assert_called_with(
            certificate_arn='arn:aws:acm:us-east-1:123:certificate/1337'
        )
        self.mock_response.set_status.assert_called_with(success=True)

    def test_delete_failed_certificate_arn_is_invalid(self):
        self.mock_request.physical_resource_id = 'invalid'
        c = Certificate(self.mock_request, self.mock_response)
        c.delete()
        self.mock_response.set_status.assert_called_with(success=False)
        self.mock_response.set_reason.assert_called_with(
            reason='Certificate ARN is invalid.'
        )

    def test_delete_failed(self):
        self.mock_request.physical_resource_id = \
            'arn:aws:acm:us-east-1:123:certificate/1337'
        c = Certificate(self.mock_request, self.mock_response)
        self.mock_delete_certificate.side_effect = exceptions.ClientError(
            error_response={'Error': {
                'Code': '1337',
                'Message': 'Message'
            }},
            operation_name='Operation'
        )
        c.delete()
        self.mock_delete_certificate.assert_called_with(
            certificate_arn='arn:aws:acm:us-east-1:123:certificate/1337'
        )
        self.mock_response.set_status.assert_called_with(success=False)
        reason = \
            'An error occurred (1337) when calling the Operation operation: ' \
            'Message'
        self.mock_response.set_reason.assert_called_with(reason=reason)


class CertificateValidatorTestCase(CertificateValidatorBaseTestCase):
    def setUp(self):
        super(CertificateValidatorTestCase, self).setUp()

    def test_init(self):
        cv = CertificateValidator(self.request, self.response)
        self.assertEqual(self.request, cv.request)
        self.assertEqual(self.response, cv.response)

    def test_change_resource_record_sets_failed_certificate_arn_is_invalid(
        self
    ):
        cv = CertificateValidator(self.mock_request, self.mock_response)
        cv.change_resource_record_sets('invalid', Action.CREATE)
        self.mock_response.set_status.assert_called_with(success=False)
        self.mock_response.set_reason.assert_called_with(
            reason='Certificate ARN is invalid.'
        )

    def test_change_resource_record_sets_create_success(self):
        self.mock_request.resource_properties = {
            'CertificateArn': self.certificate_arn
        }
        cv = CertificateValidator(self.mock_request, self.mock_response)
        cv.change_resource_record_sets(self.certificate_arn, Action.CREATE)
        self.mock_get_hosted_zone_id.assert_called_with(
            'certificate-validator.com'
        )
        self.mock_get_domain_validation_options.assert_called_with(
            'arn:aws:acm:us-east-1:123:certificate/1337'
        )
        self.mock_get_change_batch.assert_called_with(
            'CREATE', {
                'Name': '_x1.certificate-validator.com.',
                'Type': 'CNAME',
                'Value': '_x2.acm-validations.aws.'
            }
        )
        self.mock_change_resource_record_sets.assert_called_with(
            hosted_zone_id='Z23ABC4XYZL05B',
            change_batch={
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
        )
        self.mock_response.set_status.assert_called_with(success=True)

    def test_change_resource_record_sets_create_failed(self):
        self.mock_request.resource_properties = {
            'CertificateArn': self.certificate_arn
        }
        self.mock_get_domain_validation_options.side_effect = \
            exceptions.ClientError(
                error_response={'Error': {
                    'Code': '1337',
                    'Message': 'Message'
                }},
                operation_name='Operation'
            )
        cv = CertificateValidator(self.mock_request, self.mock_response)
        cv.change_resource_record_sets(self.certificate_arn, Action.CREATE)
        self.mock_response.set_status.assert_called_with(success=False)
        reason = \
            'An error occurred (1337) when calling the Operation operation: ' \
            'Message'
        self.mock_response.set_reason.assert_called_with(reason=reason)

    def test_change_resource_record_sets_upsert(self):
        self.mock_request.resource_properties = {
            'CertificateArn': self.certificate_arn
        }
        cv = CertificateValidator(self.mock_request, self.mock_response)
        cv.change_resource_record_sets(self.certificate_arn, Action.UPSERT)
        self.mock_get_hosted_zone_id.assert_called_with(
            'certificate-validator.com'
        )
        self.mock_get_domain_validation_options.assert_called_with(
            'arn:aws:acm:us-east-1:123:certificate/1337'
        )
        self.mock_get_change_batch.assert_called_with(
            'UPSERT', {
                'Name': '_x1.certificate-validator.com.',
                'Type': 'CNAME',
                'Value': '_x2.acm-validations.aws.'
            }
        )
        self.mock_change_resource_record_sets.assert_called_with(
            hosted_zone_id='Z23ABC4XYZL05B',
            change_batch={
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
        )
        self.mock_response.set_status.assert_called_with(success=True)

    def test_change_resource_record_sets_delete_success(self):
        self.mock_request.resource_properties = {
            'CertificateArn': self.certificate_arn
        }
        cv = CertificateValidator(self.mock_request, self.mock_response)
        cv.change_resource_record_sets(self.certificate_arn, Action.DELETE)
        self.mock_get_hosted_zone_id.assert_called_with(
            'certificate-validator.com'
        )
        self.mock_get_domain_validation_options.assert_called_with(
            'arn:aws:acm:us-east-1:123:certificate/1337'
        )
        self.mock_get_change_batch.assert_called_with(
            'DELETE', {
                'Name': '_x1.certificate-validator.com.',
                'Type': 'CNAME',
                'Value': '_x2.acm-validations.aws.'
            }
        )
        self.mock_change_resource_record_sets.assert_called_with(
            hosted_zone_id='Z23ABC4XYZL05B',
            change_batch={
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
        )
        self.mock_response.set_status.assert_called_with(success=True)

    def test_change_resource_record_sets_delete_failed(self):
        self.mock_request.resource_properties = {
            'CertificateArn': self.certificate_arn
        }
        self.mock_get_domain_validation_options.side_effect = \
            exceptions.ClientError(
                error_response={'Error': {
                    'Code': '1337',
                    'Message': 'Message'
                }},
                operation_name='Operation'
            )
        cv = CertificateValidator(self.mock_request, self.mock_response)
        cv.change_resource_record_sets(self.certificate_arn, Action.DELETE)
        self.mock_response.set_status.assert_called_with(success=False)
        reason = \
            'An error occurred (1337) when calling the Operation operation: ' \
            'Message'
        self.mock_response.set_reason.assert_called_with(reason=reason)

    def test_create(self):
        mock_change_resource_record_sets = \
            patch.object(resources.CertificateValidator,
                         'change_resource_record_sets').start()
        cv = CertificateValidator(self.request, self.mock_response)
        cv.create()
        self.mock_response.set_physical_resource_id.assert_called_with('1337')
        mock_change_resource_record_sets.assert_called_with(
            'arn:aws:acm:us-east-1:123:certificate/1', Action.UPSERT
        )

    def test_update(self):
        mock_change_resource_record_sets = \
            patch.object(resources.CertificateValidator,
                         'change_resource_record_sets').start()
        cv = CertificateValidator(self.request, self.mock_response)
        cv.update()
        mock_change_resource_record_sets.assert_has_calls([
            call('arn:aws:acm:us-east-1:123:certificate/0', Action.DELETE),
            call('arn:aws:acm:us-east-1:123:certificate/1', Action.UPSERT)
        ])

    def test_delete(self):
        mock_change_resource_record_sets = \
            patch.object(resources.CertificateValidator,
                         'change_resource_record_sets').start()
        cv = CertificateValidator(self.request, self.mock_response)
        cv.delete()
        mock_change_resource_record_sets.assert_called_with(
            'arn:aws:acm:us-east-1:123:certificate/1', Action.DELETE
        )

    def test_get_domain_validation_options(self):
        patch.stopall()
        mock_describe_certificate = patch.object(
            resources.ACM, 'describe_certificate'
        ).start()
        mock_describe_certificate.return_value = {
            'Certificate': {
                'DomainName': 'certificate-validator.com',
                'DomainValidationOptions': [{
                    'DomainName': 'certificate-validator.com',
                    'ResourceRecord': {
                        'Name': '_x1.certificate-validator.com.',
                        'Type': 'CNAME',
                        'Value': '_x2.acm-validations.aws.'
                    }
                }]
            }
        }
        cv = CertificateValidator(self.request, self.response)
        actual = cv.get_domain_validation_options(
            certificate_arn='arn:aws:acm:us-east-1:123:certificate/1337'
        )
        expected = [{
            'DomainName': 'certificate-validator.com',
            'ResourceRecord': {
                'Name': '_x1.certificate-validator.com.',
                'Type': 'CNAME',
                'Value': '_x2.acm-validations.aws.'
            }
        }]
        self.assertEqual(expected, actual)

    def test_get_domain_validation_options_poll(self):
        patch.stopall()
        patch('time.sleep', return_value=None).start()
        mock_describe_certificate = patch.object(
            resources.ACM, 'describe_certificate'
        ).start()
        mock_describe_certificate.side_effect = [{
            'Certificate': {
                'DomainName': 'certificate-validator.com',
                'DomainValidationOptions': [{
                    'DomainName': 'certificate-validator.com'
                }],
            }
        }, {
            'Certificate': {
                'DomainName': 'certificate-validator.com',
                'DomainValidationOptions': [{
                    'DomainName': 'certificate-validator.com',
                    'ResourceRecord': {
                        'Name': '_x1.certificate-validator.com.',
                        'Type': 'CNAME',
                        'Value': '_x2.acm-validations.aws.'
                    }
                }]
            }
        }]
        cv = CertificateValidator(self.request, self.response)
        actual = cv.get_domain_validation_options(
            certificate_arn='arn:aws:acm:us-east-1:123:certificate/1337'
        )
        expected = [{
            'DomainName': 'certificate-validator.com',
            'ResourceRecord': {
                'Name': '_x1.certificate-validator.com.',
                'Type': 'CNAME',
                'Value': '_x2.acm-validations.aws.'
            }
        }]
        self.assertEqual(expected, actual)

    def test_get_hosted_zone_id(self):
        patch.stopall()
        mock_list_hosted_zones_by_name = patch.object(
            resources.Route53, 'list_hosted_zones_by_name'
        ).start()
        mock_list_hosted_zones_by_name.return_value = {
            'HostedZones': [{
                'Id': '/hostedzone/Z23ABC4XYZL05B',
                'Name': 'certificate-validator.com.',
            }]
        }
        cv = CertificateValidator(self.request, self.response)
        actual = cv.get_hosted_zone_id(domain_name='certificate-validator.com')
        expected = 'Z23ABC4XYZL05B'
        self.assertEqual(expected, actual)

    def test_get_change_batch(self):
        patch.stopall()
        cv = CertificateValidator(self.request, self.response)
        resource_record = {
            'Name': '_x1.certificate-validator.com.',
            'Type': 'CNAME',
            'Value': '_x2.acm-validations.aws.'
        }
        actual = cv.get_change_batch(
            action='CREATE', resource_record=resource_record
        )
        expected = {
            'Changes': [{
                'Action': 'CREATE',
                'ResourceRecordSet': {
                    'Name': '_x1.certificate-validator.com.',
                    'Type': 'CNAME',
                    'TTL': 300,
                    'ResourceRecords': [{
                        'Value': '_x2.acm-validations.aws.'
                    }]
                }
            }]
        }
        self.assertEqual(expected, actual)
