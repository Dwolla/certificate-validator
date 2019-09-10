# -*- coding: utf-8 -*-
"""Custom Resource module."""

import re
import uuid
from enum import Enum

import polling
from botocore import exceptions

from certificate_validator.api import ACM, Route53
from certificate_validator.provider import Provider


class Action(str, Enum):
    """
    Action of a Change Resource Record Sets request.

    A Change Resource Record Sets request can have the following actions:
      * CREATE: Creates a resource record set that has the specified values.
      * DELETE: Deletes an existing resource record set that has the specified
        values.
      * UPSERT: If a resource record set does not already exist, AWS creates
        it. If a resource set does exist, Route 53 updates it with the values
        in the request.
    """
    CREATE = 'CREATE'
    UPSERT = 'UPSERT'
    DELETE = 'DELETE'


class CertificateMixin():
    """
    Mixin class containing helpful methods for handling ACM certificates.
    """
    def is_valid_arn(self, certificate_arn: str) -> bool:
        """
        Determine if the ARN of an ACM certificate is valid.

        :type certificate_arn: str
        :param certificate_arn: ARN of the ACM certificate

        :rtype: bool
        :return: whether the ARN of the ACM certificate is valid
        """
        pattern = re.compile(
            r'arn:aws:acm:[\w+=/,.@-]*:[0-9]+:[\w+=,.@-]+(/[\w+=,.@-]+)*'
        )
        return bool(re.match(pattern, certificate_arn))


class Certificate(CertificateMixin, Provider):
    """
    A Custom::Certificate Custom Resource.

    The Custom::Certificate resource creates, updates, and deletes a
    AWS::CertificateManager::Certificate resource.

    The Custom::Certificate resource requests an AWS Certificate Manager (ACM)
    certificate that you can use to enable secure connections. However, unlike
    a AWS::CertificateManager::Certificate resource, the Custom::Certificate
    resource returns a successful status upon creation, not upon validation of
    the certificate request.
    """
    def __init__(self, *args, **kwargs):
        """
        Create a new `Certificate` object.

        :rtype: None
        :return: None
        """
        super(Certificate, self).__init__(*args, **kwargs)
        self.acm = ACM()

    def create(self) -> None:
        """
        Create a AWS::CertificateManager::Certificate resource.

        :rtype: None
        :return: None
        """
        try:
            response = self.acm.request_certificate(
                domain_name=self.request.resource_properties['DomainName'],
                subject_alternative_names=self.request.
                resource_properties['SubjectAlternativeNames']
            )
            self.response.set_status(success=True)
            # canonically, the ARN (Amazon Resource Name) of the Certificate
            # resource is used for the PhysicalResourceId
            self.response.set_physical_resource_id(
                physical_resource_id=response['CertificateArn']
            )
            self.response.set_data(response)
        except exceptions.ClientError as ex:
            self.response.set_status(success=False)
            self.response.set_reason(reason=str(ex))

    def update(self) -> None:
        """
        Update the AWS::CertificateManager::Certificate resource.

        :rtype: None
        :return: None
        """
        self.delete()
        self.create()

    def delete(self) -> None:
        """
        Delete the AWS::CertificateManager::Certificate resource.

        :rtype: None
        :return: None
        """
        if self.request.physical_resource_id == '':
            self.response.set_status(success=True)
            self.response.set_reason(reason='Certificate does not exist.')
            return
        if not self.is_valid_arn(self.request.physical_resource_id):
            self.response.set_status(success=False)
            self.response.set_reason(reason='Certificate ARN is invalid.')
            return
        try:
            self.acm.delete_certificate(
                certificate_arn=self.request.physical_resource_id
            )
            self.response.set_status(success=True)
        except exceptions.ClientError as ex:
            self.response.set_status(success=False)
            self.response.set_reason(reason=str(ex))


class CertificateValidator(CertificateMixin, Provider):
    """
    A Custom::CertificateValidator Custom Resource.

    The Custom::CertificateValidator resource creates, updates, and deletes a
    AWS::Route53::RecordSetGroup resource.

    The Custom::CertificateValidator resource retrieves the record set used by
    AWS Certificate Manager (ACM) to validate a certificate.
    """
    def __init__(self, *args, **kwargs):
        """
        Create a new `CertificateValidator` object.

        :rtype: None
        :return: None
        """
        super(CertificateValidator, self).__init__(*args, **kwargs)
        self.acm = ACM()
        self.route53 = Route53()

    def create(self) -> None:
        """
        Create a AWS::Route53::RecordSetGroup resource.

        :rtype: None
        :return: None
        """
        if not self.is_valid_arn(
            self.request.resource_properties['CertificateArn']
        ):
            self.response.set_status(success=False)
            self.response.set_reason(reason='Certificate ARN is invalid.')
            return
        self.response.set_physical_resource_id(str(uuid.uuid4()))
        try:
            response = self.acm.describe_certificate(
                certificate_arn=self.request.
                resource_properties['CertificateArn']
            )
            domain_name = response['Certificate']['DomainName']
            hosted_zone_id = self.get_hosted_zone_id(domain_name)
            resource_records = self.get_resource_records(
                self.request.resource_properties['CertificateArn']
            )
            change_batch = self.get_change_batch(
                Action.CREATE.value, resource_records
            )
            self.route53.change_resource_record_sets(
                hosted_zone_id=hosted_zone_id, change_batch=change_batch
            )
            self.response.set_status(success=True)
        except exceptions.ClientError as ex:
            self.response.set_status(success=False)
            self.response.set_reason(reason=str(ex))

    def update(self) -> None:
        """
        Update the AWS::Route53::RecordSetGroup resource.

        :rtype: None
        :return: None
        """
        self.delete()
        self.create()

    def delete(self) -> None:
        """
        Delete the AWS::Route53::RecordSetGroup resource.

        :rtype: None
        :return: None
        """
        if not self.is_valid_arn(
            self.request.resource_properties['CertificateArn']
        ):
            self.response.set_status(success=False)
            self.response.set_reason(reason='Certificate ARN is invalid.')
            return
        try:
            response = self.acm.describe_certificate(
                certificate_arn=self.request.
                resource_properties['CertificateArn']
            )
            domain_name = response['Certificate']['DomainName']
            hosted_zone_id = self.get_hosted_zone_id(domain_name)
            resource_records = self.get_resource_records(
                self.request.resource_properties['CertificateArn']
            )
            change_batch = self.get_change_batch(
                Action.DELETE.value, resource_records
            )
            self.route53.change_resource_record_sets(
                hosted_zone_id=hosted_zone_id, change_batch=change_batch
            )
            self.response.set_status(success=True)
        except exceptions.ClientError as ex:
            self.response.set_status(success=False)
            self.response.set_reason(reason=str(ex))

    def get_resource_records(self, certificate_arn: str) -> list:
        """
        Retrieve the resouce records for a given Certificate.

        :type certificate_arn: str
        :param certificate_arn: ARN of the ACM certificate

        :rtype: list
        :return: list of resource records
        """
        def resource_records_exist(response: dict) -> bool:
            if response['Certificate']['DomainValidationOptions'][0].get(
                'ResourceRecord'
            ):
                return True
            else:
                return False

        response = polling.poll(
            lambda: self.acm.describe_certificate(
                certificate_arn=self.request.resource_properties[
                    'CertificateArn']
            ),
            check_success=resource_records_exist,
            step=5,
            timeout=60
        )

        resource_records = [
            x['ResourceRecord']
            for x in response['Certificate']['DomainValidationOptions']
        ]
        return resource_records

    def get_hosted_zone_id(self, domain_name: str) -> str:
        """
        Retrieve the hosted zone ID given a domain name.

        :type domain_name: str
        :param domain_name: domain name of the hosted zone

        :rtype: str
        :return: ID of the hosted zone
        """
        response = self.route53.list_hosted_zones_by_name(dns_name=domain_name)
        hosted_zone = response['HostedZones'][0]
        return hosted_zone['Id'].split('/hostedzone/')[1]

    def get_change_batch(self, action: Action, resource_records: list) -> dict:
        """
        Create a change batch given a resource record set.

        The `resource_records` parameter has the following form:

        [
          'Name': 'string',
          'Type': 'CNAME',
          'Value': 'string'
        ]

        :type action: Action
        :param action: action of a Change Resource Record Sets request
        :type resource_records: list
        :param resource_records: resource record sets to add for domain
          validation

        :rtype: dict
        :return: a dict containing the resource record sets to add for domain
          validation
        """
        changes = []
        for resource_record in resource_records:
            changes.append({
                'Action': action,
                'ResourceRecordSet': {
                    'Name': resource_record['Name'],
                    'Type': resource_record['Type'],
                    'TTL': 300,
                    'ResourceRecords': [{
                        'Value': resource_record['Value']
                    }]
                }
            })
        change_batch = {'Changes': changes}
        return change_batch
