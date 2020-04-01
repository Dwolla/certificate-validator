# -*- coding: utf-8 -*-
"""Tests for the `provider` module."""

from unittest.mock import patch

from certificate_validator.provider import (
    Provider, Request, RequestResourceProperties, RequestType, Response,
    Status
)

from .base import (
    BaseTestCase, ProviderBaseTestCase, RequestBaseTestCase,
    ResponseBaseTestCase
)


class RequestTypeTestCase(BaseTestCase):
    def setUp(self):
        super(RequestTypeTestCase, self).setUp()

    def test_class(self):
        self.assertEqual('Create', RequestType.CREATE.value)
        self.assertEqual('Update', RequestType.UPDATE.value)
        self.assertEqual('Delete', RequestType.DELETE.value)


class StatusTestCase(BaseTestCase):
    def setUp(self):
        super(StatusTestCase, self).setUp()

    def test_class(self):
        self.assertEqual('SUCCESS', Status.SUCCESS.value)
        self.assertEqual('FAILED', Status.FAILED.value)


class RequestTestCase(RequestBaseTestCase):
    def setUp(self):
        super(RequestTestCase, self).setUp()

    def test_init(self):
        kwargs = {'a': 1, 'b': 2, 'c': 3}
        r = Request(**kwargs)
        self.assertEqual(1, r.a)
        self.assertEqual(2, r.b)
        self.assertEqual(3, r.c)
        self.assertEqual(Request.DEFAULT_REGION, r.region)

    def test_request_type(self):
        self.assertEqual('request_type', self.request.request_type)

    def test_service_token(self):
        self.assertEqual('service_token', self.request.service_token)

    def test_response_url(self):
        self.assertEqual('response_url', self.request.response_url)

    def test_stack_id(self):
        self.assertEqual('stack_id', self.request.stack_id)

    def test_request_id(self):
        self.assertEqual('request_id', self.request.request_id)

    def test_resource_type(self):
        self.assertEqual('resource_type', self.request.resource_type)

    def test_logical_resource_id(self):
        self.assertEqual(
            'logical_resource_id', self.request.logical_resource_id
        )

    def test_physical_resource_id(self):
        self.assertEqual(
            'physical_resource_id', self.request.physical_resource_id
        )
        kwargs = {}
        r = Request(**kwargs)
        self.assertEqual('', r.physical_resource_id)

    def test_resource_properties(self):
        self.assertEqual(
            'service_token', self.request.resource_properties.service_token
        )

    def test_resource_properties_none(self):
        r = Request(ResourceProperties=None)
        properties = r.resource_properties
        self.assertIsInstance(properties, RequestResourceProperties)
        # TODO

    def test_old_resource_properties(self):
        self.assertEqual(
            'service_token', self.request.old_resource_properties.service_token
        )

    def test_old_resource_properties_none(self):
        r = Request(OldResourceProperties=None)
        properties = r.old_resource_properties
        self.assertIsInstance(properties, RequestResourceProperties)
        # TODO

    def test_sans(self):
        kwargs = {
            'ResourceProperties': {
                'SubjectAlternativeNames': ['www.certificate-validator.com']
            }
        }
        r = Request(**kwargs)
        self.assertEqual(['www.certificate-validator.com'],
                         r.resource_properties.sans)

    def test_old_sans(self):
        kwargs = {
            'OldResourceProperties': {
                'SubjectAlternativeNames': ['www.certificate-validator.com']
            }
        }
        r = Request(**kwargs)
        properties = r.resource_properties
        old_properties = r.old_resource_properties
        self.assertEqual([], properties.sans)
        self.assertEqual(['www.certificate-validator.com'],
                         old_properties.sans)

    def test_sans_with_empty_only(self):
        self.assertEqual([], self.request.resource_properties.sans)
        for case in [None, [''], [None], ['', None], [None, '']]:
            kwargs = {'ResourceProperties': {'SubjectAlternativeNames': case}}
            r = Request(**kwargs)
            properties = r.resource_properties
            self.assertEqual([], properties.sans,
                             "Failed test. input %s, expected %s, got %s" %
                             (case, [], properties.sans))

    def test_sans_with_mixed(self):
        for case in [['', 'www.certificate-validator.com'],
                     [None, 'www.certificate-validator.com'],
                     ['www.certificate-validator.com', None],
                     ['', 'www.certificate-validator.com', None],
                     [None, '', 'www.certificate-validator.com']]:
            kwargs = {'ResourceProperties': {'SubjectAlternativeNames': case}}
            r = Request(**kwargs)
            properties = r.resource_properties
            sans = properties.sans
            self.assertEqual(['www.certificate-validator.com'], sans,
                             "Failed test. input %s, expected %s, got %s" %
                             (case, ['www.certificate-validator.com'], sans))

    def test_region_default(self):
        self.assertEqual(Request.DEFAULT_REGION, self.request.region)

    def test_region_caching(self):
        region = self.request.region
        self.mock_logger.warning.assert_called_with(
            "Failed to parse stack ARN(%s) to get region - defaulting to %s",
            'stack_id', Request.DEFAULT_REGION
        )
        self.mock_logger.reset_mock()
        region2 = self.request.region
        self.mock_logger.warning.assert_not_called()
        self.assertIs(region, region2)
        self.assertEqual(Request.DEFAULT_REGION, self.request.region)

    def test_region_from_arn(self):
        for region in ['us-west-1', 'us-east-1', 'us-west-2', 'ap-south-1']:
            kwargs = {
                "StackId":
                    "arn:aws:cloudformation:{}:{}:stack/stackname/guid".format(
                        region, '123456789012'
                    )
            }
            r = Request(**kwargs)
            actual = r.region
            self.assertEqual(
                region, actual, "Expected %s, got %s" % (region, actual)
            )


class ResponseTestCase(ResponseBaseTestCase):
    def setUp(self):
        super(ResponseTestCase, self).setUp()

    def test_init(self):
        kwargs = {'a': 1, 'b': 2, 'c': 3}
        r = Response(**kwargs)
        self.assertEqual(1, r.a)
        self.assertEqual(2, r.b)
        self.assertEqual(3, r.c)
        r = Response(
            request_id='request_id',
            stack_id='stack_id',
            logical_resource_id='logical_resource_id'
        )
        self.assertEqual('request_id', r.request_id)
        self.assertEqual('stack_id', r.stack_id)
        self.assertEqual('logical_resource_id', r.logical_resource_id)
        self.assertEqual('', r.physical_resource_id)
        r = Response(
            request_id='request_id',
            stack_id='stack_id',
            logical_resource_id='logical_resource_id',
            physical_resource_id='physical_resource_id'
        )
        self.assertEqual('request_id', r.request_id)
        self.assertEqual('stack_id', r.stack_id)
        self.assertEqual('logical_resource_id', r.logical_resource_id)
        self.assertEqual('physical_resource_id', r.physical_resource_id)

    def test_status(self):
        self.assertEqual('status', self.response.status)

    def test_reason(self):
        self.assertEqual('reason', self.response.reason)

    def test_stack_id(self):
        self.assertEqual('stack_id', self.response.stack_id)

    def test_request_id(self):
        self.assertEqual('request_id', self.response.request_id)

    def test_logical_resource_id(self):
        self.assertEqual(
            'logical_resource_id', self.response.logical_resource_id
        )

    def test_physical_resource_id(self):
        self.assertEqual(
            'physical_resource_id', self.response.physical_resource_id
        )

    def test_no_echo(self):
        self.assertEqual(True, self.response.no_echo)

    def test_data(self):
        self.assertEqual({'a': 1, 'b': 2, 'c': 3}, self.response.data)

    def test_set_status(self):
        self.response.set_status(True)
        self.assertEqual('SUCCESS', self.response.status)
        self.response.set_status(False)
        self.assertEqual('FAILED', self.response.status)

    def test_set_reason(self):
        self.response.set_reason('')
        self.assertEqual('', self.response.reason)

    def test_set_physical_resource_id(self):
        self.response.set_physical_resource_id('1337')
        self.assertEqual('1337', self.response.physical_resource_id)

    def test_set_data(self):
        self.response.set_data({'a': 1, 'b': 2, 'c': 3})
        self.assertEqual({'a': 1, 'b': 2, 'c': 3}, self.response.data)
        kwargs = {}
        r = Response(**kwargs)
        r.set_data({'a': 1, 'b': 2, 'c': 3})
        self.assertEqual({'a': 1, 'b': 2, 'c': 3}, r.data)

    def test_dict(self):
        self.kwargs = self.response.dict()


class ProviderTestCase(ProviderBaseTestCase):
    def setUp(self):
        super(ProviderTestCase, self).setUp()

    def test_init(self):
        self.assertEqual(self.provider.request, self.request)
        self.assertEqual(self.provider.response, self.response)

    def test_set_response(self):
        r = Response()
        self.provider._set_response(r)
        self.assertEqual(r, self.provider.response)

    def test_create(self):
        with self.assertRaises(NotImplementedError):
            self.provider.create()

    def test_update(self):
        with self.assertRaises(NotImplementedError):
            self.provider.update()

    def test_delete(self):
        with self.assertRaises(NotImplementedError):
            self.provider.delete()

    def test_handler_create(self):
        self.mock_create = patch.object(Provider, 'create').start()
        self.mock_send_response = patch.object(Provider,
                                               'send_response').start()
        self.request_kwargs['RequestType'] = 'Create'
        request = Request(**self.request_kwargs)
        provider = Provider(request, self.response)
        provider.handler()
        self.mock_create.assert_called_once()
        self.mock_send_response.assert_called_once()

    def test_handler_update(self):
        self.mock_update = patch.object(Provider, 'update').start()
        self.mock_send_response = patch.object(Provider,
                                               'send_response').start()
        self.request_kwargs['RequestType'] = 'Update'
        request = Request(**self.request_kwargs)
        provider = Provider(request, self.response)
        provider.handler()
        self.mock_update.assert_called_once()
        self.mock_send_response.assert_called_once()

    def test_handler_delete(self):
        self.mock_delete = patch.object(Provider, 'delete').start()
        self.mock_send_response = patch.object(Provider,
                                               'send_response').start()
        self.request_kwargs['RequestType'] = 'Delete'
        request = Request(**self.request_kwargs)
        provider = Provider(request, self.response)
        provider.handler()
        self.mock_delete.assert_called_once()
        self.mock_send_response.assert_called_once()

    def test_handler_unknown(self):
        self.mock_send_response = patch.object(Provider,
                                               'send_response').start()
        self.request_kwargs['RequestType'] = 'Unknown'
        request = Request(**self.request_kwargs)
        provider = Provider(request, self.response)
        provider.handler()
        self.assertEqual('FAILED', self.provider.response.status)
        self.assertEqual(
            'Unknown RequestType: Must be one of: Create, Update, or Delete.',
            self.provider.response.reason
        )
        self.mock_send_response.assert_called_once()

    def test_send_response(self):
        self.provider.send_response()
        self.mock_requests.put.assert_called_with(
            'response_url',
            json=self.provider.response.dict(),
            headers={'Content-Type': ''}
        )
