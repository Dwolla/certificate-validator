# -*- coding: utf-8 -*-
"""Custom Resource Provider module."""

from enum import Enum

import requests

from certificate_validator.data_mapper import (
    ClassValue, CleanListValue, DataMapper, DataMapperValue
)
from certificate_validator.exceptions import UnknownRequestType
from certificate_validator.logger import logger


class RequestType(str, Enum):
    """
    RequestType of a Custom Resource Request Object.

    The request type is sent in the `RequestType` field in the vendor request
    object sent by AWS CloudFormation when the template developer creates,
    updates, or deletes a stack that contains a custom resource.
    """
    CREATE = 'Create'
    UPDATE = 'Update'
    DELETE = 'Delete'


class Status(str, Enum):
    """
    Status of a Custom Resource Response Object.

    The status value sent by the custom resource provider in response to an AWS
    CloudFormation-generated request.
    """
    SUCCESS = 'SUCCESS'
    FAILED = 'FAILED'


class RequestResourceProperties(DataMapper):
    """
    Class holding Request Resource Properties.
    """
    MAP = {
        'ServiceToken': DataMapperValue('service_token'),
        'DomainName': DataMapperValue('domain_name'),
        'SubjectAlternativeNames': CleanListValue('sans'),
        'CertificateArn': DataMapperValue('certificate_arn'),
    }


class Request(DataMapper):
    """
    A request from a AWS Custom Resource.

    A Custom Resource Request Object has the following form:

    {
      'RequestType': 'Create | Update | Delete',
      'ServiceToken': 'string',
      'ResponseURL': 'string',
      'StackId': 'string',
      'RequestId': 'string',
      'ResourceType': 'string',
      'LogicalResourceId': 'string',
      'PhysicalResourceId': 'string',
      'ResourceProperties': {
        'ServiceToken': 'string',
        ...
      },
      'OldResourceProperties': {
        'ServiceToken': 'string',
        ...
      }
    }
    """
    DEFAULT_REGION = 'us-east-1'

    MAP = {
        'RequestType': DataMapperValue('request_type'),
        'ResponseURL': DataMapperValue('response_url'),
        'ServiceToken': DataMapperValue('service_token'),
        'StackId': DataMapperValue('stack_id'),
        'RequestId': DataMapperValue('request_id'),
        'ResourceType': DataMapperValue('resource_type'),
        'LogicalResourceId': DataMapperValue('logical_resource_id'),
        'PhysicalResourceId': DataMapperValue('physical_resource_id'),
        'ResourceProperties':
            ClassValue('resource_properties', clazz=RequestResourceProperties),
        'OldResourceProperties':
            ClassValue(
                'old_resource_properties', clazz=RequestResourceProperties
            )
    }

    def __init__(self, **kwargs):
        """
        Initialize Request.
        """
        super().__init__(**kwargs)
        self._region = None

    @property
    def region(self) -> str:
        """
        Get region of the certificate.

        If not explicitly set, auto-determine on first call from stack_id arn.
        """
        if not self._region:
            arn = self.stack_id.split(':', 5)
            if len(arn) > 3:
                region = arn[3]
                logger.info("Auto-determined region to be %s", region)
            else:
                region = self.DEFAULT_REGION
                logger.warning(
                    "Failed to parse stack ARN(%s) to get " +
                    "region - defaulting to %s", self.stack_id, region
                )
            self._region = region
        return self._region


class Response():
    """
    A response to a AWS Custom Resource.

    A Custom Resource Response Object has the following form:

    {
       'Status': 'SUCCESS | FAILED',
       'Reason': 'string',
       'StackId': 'string',
       'RequestId': 'string',
       'LogicalResourceId': 'string',
       'PhysicalResourceId': 'string',
       'NoEcho': bool,
       'Data': {
         ...
       }
    }
    """
    def __init__(
        self,
        request_id: str = '',
        stack_id: str = '',
        logical_resource_id: str = '',
        physical_resource_id: str = '',
        *args: list,
        **kwargs: dict
    ) -> None:
        """
        Create a new `Response` object.

        :type request_id: str
        :param request_id: unique ID for the request
        :type stack_id: str
        :param stack_id: ARN of the AWS CloudFormation stack that contains the
            custom resource
        :type logical_resource_id: str
        :param logical_resource_id: template developer-chosen name of the
            custom resource
        :type physical_resource_id: str
        :param physical_resource_id: unique ID for the custom resource

        :rtype: None
        :return: None
        """
        if kwargs:
            self.__dict__.update(**kwargs)
        else:
            self.RequestId = request_id
            self.StackId = stack_id
            self.LogicalResourceId = logical_resource_id

            if physical_resource_id:
                self.PhysicalResourceId = physical_resource_id
            else:
                self.set_physical_resource_id('')

    @property
    def status(self) -> str:
        """
        Return the Status of the Custom Resource Response Object.

        The Status value sent by the custom resource provider in response to an
        AWS CloudFormation-generated request.

        Must be either SUCCESS or FAILED.
        """
        return self.Status

    @property
    def reason(self) -> str:
        """
        Return the Reason of the Custom Resource Response Object.

        Describes the reason for a failure response.

        Required if Status is FAILED. It's optional otherwise.
        """
        return self.Reason

    @property
    def stack_id(self) -> str:
        """
        Return the StackId of the Custom Resource Response Object.

        The Amazon Resource Name (ARN) that identifies the stack that contains
        the custom resource. This response value should be copied verbatim from
        the request.
        """
        return self.StackId

    @property
    def request_id(self) -> str:
        """
        Return the RequestId of the Custom Resource Response Object.

        A unique ID for the request. This response value should be copied
        verbatim from the request.
        """
        return self.RequestId

    @property
    def logical_resource_id(self) -> str:
        """
        Return the LogicalResourceId of the Custom Resource Response Object.

        The template developer-chosen name (logical ID) of the custom resource
        in the AWS CloudFormation template. This response value should be
        copied verbatim from the request.
        """
        return self.LogicalResourceId

    @property
    def physical_resource_id(self) -> str:
        """
        Return the PhysicalResourceId of the Custom Resource Request Object.

        This value should be an identifier unique to the custom resource
        vendor, and can be up to 1 Kb in size. The value must be a non-empty
        string and must be identical for all responses for the same resource.
        """
        return self.PhysicalResourceId

    @property
    def no_echo(self) -> bool:
        """
        Return the NoEcho of the Custom Resource Response Object.

        Indicates whether to mask the output of the custom resource when
        retrieved by using the Fn::GetAtt function. If set to true, all
        returned values are masked with asterisks (*****). The default value is
        false.
        """
        return self.NoEcho

    @property
    def data(self) -> dict:
        """
        Return the Data of the Custom Resource Response Object.

        The custom resource provider-defined name-value pairs to send with the
        response. You can access the values provided here by name in the
        template with Fn::GetAtt.

        If the name-value pairs contain sensitive information, you should use
        the NoEcho field to mask the output of the custom resource. Otherwise,
        the values are visible through APIs that surface property values (such
        as DescribeStackEvents).
        """
        return self.Data

    def set_status(self, success: bool) -> None:
        """
        Set the Status of the Custom Resource Response Object.
        """
        if success:
            self.Status = Status.SUCCESS.value
        else:
            self.Status = Status.FAILED.value

    def set_reason(self, reason: str) -> None:
        """
        Set the Reason of the Custom Resource Response Object.
        """
        self.Reason = reason

    def set_physical_resource_id(self, physical_resource_id: str) -> None:
        """
        Set the PhysicalResourceId of the Custom Resource Response Object.

        The PhysicalResourceId is a custom resource provider-defined physical
        ID that is unique for that provider.

        This value should be an identifier unique to the custom resource
        vendor, and can be up to 1 Kb in size. The value must be a non-empty
        string and must be identical for all responses for the same resource.
        """
        self.PhysicalResourceId = physical_resource_id

    def set_data(self, data: dict) -> None:
        """
        Set the Data of the Custom Resource Response Object.

        The custom resource provider-defined name-value pairs to send with the
        response. You can access the values provided here by name in the
        template with Fn::GetAtt.

        If the name-value pairs contain sensitive information, you should use
        the NoEcho field to mask the output of the custom resource. Otherwise,
        the values are visible through APIs that surface property values (such
        as DescribeStackEvents).
        """
        if hasattr(self, 'Data'):
            self.Data.update(data)
        else:
            self.Data = data

    def dict(self) -> dict:
        """
        Return dict representation of this object.
        """
        return self.__dict__


class Provider():
    """
    Custom Resource Provider for an AWS Custom Resource.

    A custom sesouce provider owns the custom resource and determines how to
    handle and respond to requests from AWS CloudFormation. The custom resource
    provider must provide a service token that the template developer uses.
    """
    def __init__(
        self,
        request: Request = None,
        response: Response = None,
    ) -> None:
        """
        Create a new `Provider` object.

        :type request: Request
        :param request: Custom Resource Request Object
        :type response: Response
        :param response: Custom Resource Response Object

        :rtype: None
        :return: None
        """
        self.request = request
        self.response = response

    def _set_response(self, response: Response) -> None:
        """
        Set the Custom Resource Response Object.
        """
        self.response = response

    def create(self) -> None:
        """
        Handle a "Create" request type.

        This method must be implemented by the child class or an
        NotImplementedError exception is raised.

        Custom resource provider requests with RequestType set to "Create" are
        sent when the template developer creates a stack that contains a custom
        resource.
        """
        raise NotImplementedError

    def update(self) -> None:
        """
        Handle an "Update" request type.

        This method must be implemented by the child class or an
        NotImplementedError exception is raised.

        Custom resource provider requests with RequestType set to "Update" are
        sent when there's any change to the properties of the custom resource
        within the template. Therefore, custom resource code doesn't have to
        detect changes because it knows that its properties have changed when
        Update is being called.

        *Replacing a Custom Resource During an Update*

        You can update custom resources that require a replacement of the
        underlying physical resource. When you update a custom resource in an
        AWS CloudFormation template, AWS CloudFormation sends an update request
        to that custom resource. If a custom resource requires a replacement,
        the new custom resource must send a response with the new physical ID.
        When AWS CloudFormation receives the response, it compares the
        PhysicalResourceId between the old and new custom resources. If they
        are different, AWS CloudFormation recognizes the update as a
        replacement and sends a delete request to the old resource.
        """
        raise NotImplementedError

    def delete(self) -> None:
        """
        Handle a "Delete" request type.

        This method must be implemented by the child class or an
        NotImplementedError exception is raised.

        Custom resource provider requests with RequestType set to "Delete" are
        sent when the template developer deletes a stack that contains a custom
        resource. To successfully delete a stack with a custom resource, the
        custom resource provider must respond successfully to a delete request.
        """
        raise NotImplementedError

    def handler(self) -> None:
        """
        Handle a "Create", "Update", or "Delete" request type.

        If the request type is not one of "Create", "Update", or "Delete", an
        UnknownRequestType exception is raised and a response is returned with
        a status of "FAILED".
        """
        try:
            if self.request.request_type == RequestType.CREATE.value:
                self.create()
            elif self.request.request_type == RequestType.UPDATE.value:
                self.update()
            elif self.request.request_type == RequestType.DELETE.value:
                self.delete()
            else:
                raise UnknownRequestType
        except Exception as ex:
            self.response.set_status(success=False)
            self.response.set_reason(reason=str(ex))
        finally:
            self.send_response()

    def send_response(self):
        """
        Send response to the pre-signed S3 URL.

        The custom resource provider processes the AWS CloudFormation request
        and returns a response of SUCCESS or FAILED to the pre-signed URL. The
        custom resource provider provides the response in a JSON-formatted file
        and uploads it to the pre-signed S3 URL.
        """
        url = self.request.response_url
        r = requests.put(
            url, json=self.response.dict(), headers={'Content-Type': ''}
        )
        r.raise_for_status()
