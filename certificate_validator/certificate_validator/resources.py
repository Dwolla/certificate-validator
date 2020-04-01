# -*- coding: utf-8 -*-
"""Custom Resource module."""

import re
import uuid
from enum import Enum

import polling
from botocore import exceptions

from certificate_validator.api import ACM, Route53
from certificate_validator.logger import logger
from certificate_validator.provider import Provider


class Action(str, Enum):
    """
    Action of a ChangeResourceRecordSets request.

    A ChangeResourceRecordSets request can have the following actions:
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
        self.acm = ACM(self.request.region)

    def create(self) -> None:
        """
        Create a AWS::CertificateManager::Certificate resource.

        :rtype: None
        :return: None
        """
        try:
            properties = self.request.resource_properties
            sans = properties.sans
            logger.info(
                "Creating certificate request for:  %s (%s)",
                properties.domain_name, ", ".join(properties.sans)
            )
            response = self.acm.request_certificate(
                domain_name=properties.domain_name,
                subject_alternative_names=sans
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
            if ex.response['Error']['Code'] == 'ResourceNotFoundException':
                self.response.set_status(success=True)
                self.response.set_reason(reason='Certificate not found.')
            else:
                self.response.set_status(success=False)
                self.response.set_reason(reason=str(ex))


class CertificateValidator(CertificateMixin, Provider):
    """
    A Custom::CertificateValidator Custom Resource.

    The Custom::CertificateValidator resource creates, updates, and deletes
    AWS::Route53::RecordSetGroup resources.

    The Custom::CertificateValidator resource retrieves the record sets used by
    AWS Certificate Manager (ACM) to validate a certificate.
    """
    def __init__(self, *args, **kwargs):
        """
        Create a new `CertificateValidator` object.

        :rtype: None
        :return: None
        """
        super(CertificateValidator, self).__init__(*args, **kwargs)
        self.acm = ACM(self.request.region)
        self.route53 = Route53()

    def change_resource_record_sets(
        self, certificate_arn: str, action: Action
    ) -> None:
        """
        Create, update, or delete AWS::Route53::RecordSetGroup resources.

        Given the ARN of a ACM certificate, create, update, or delete the
        AWS::Route53::RecordSetGroup resources used for initial validation.

        :type certificate_arn: str
        :param certificate_arn: ARN of the ACM certificate
        :type action: Action
        :param action: action of a ChangeResourceRecordSets request

        :rtype: None
        :return: None
        """
        if not self.is_valid_arn(certificate_arn):
            self.response.set_status(success=False)
            self.response.set_reason(reason='Certificate ARN is invalid.')
            return
        try:
            domain_validation_options = self.get_domain_validation_options(
                certificate_arn
            )
            for domain_validation_option in domain_validation_options:
                # remove subdomains from DomainName
                domain_name = '.'.join(
                    domain_validation_option['DomainName'].split('.')[-2:]
                )
                hosted_zone_id = self.get_hosted_zone_id(domain_name)
                resource_record = domain_validation_option['ResourceRecord']
                change_batch = self.get_change_batch(
                    action.value, resource_record
                )
                self.route53.change_resource_record_sets(
                    hosted_zone_id=hosted_zone_id, change_batch=change_batch
                )
            self.response.set_status(success=True)
        except exceptions.ClientError as ex:
            if ex.response['Error']['Code'] == 'ResourceNotFoundException':
                self.response.set_status(success=True)
                self.response.set_reason(reason='Certificate not found.')
            elif ex.response['Error']['Code'] == 'InvalidChangeBatch':
                if 'not found' in ex.response['Error']['Message']:
                    self.response.set_status(success=True)
                    self.response.set_reason(
                        reason='Resource Record Set not found.'
                    )
                else:
                    self.response.set_status(success=False)
                    self.response.set_reason(reason=str(ex))
            else:
                self.response.set_status(success=False)
                self.response.set_reason(reason=str(ex))

    def create(self) -> None:
        """
        Create AWS::Route53::RecordSetGroup resources.

        Wait until the AWS::CertificateManager::Certificate resource is issued
        before proceeding.

        :rtype: None
        :return: None
        """
        properties = self.request.resource_properties
        self.response.set_physical_resource_id(str(uuid.uuid4()))
        self.change_resource_record_sets(
            properties.certificate_arn, Action.UPSERT
        )
        self.acm.wait(properties.certificate_arn)

    def update(self) -> None:
        """
        Update AWS::Route53::RecordSetGroup resources.

        If either the DomainName or SubjectAlternativeNames for the
        Custom::Certificate are changed, delete the
        AWS::Route53::RecordSetGroup resources associated with the old
        Custom::Certificate and create the AWS::Route53::RecordSetGroup
        resources associated with the new Custom::Certificate.

        :rtype: None
        :return: None
        """
        properties = self.request.resource_properties
        old_properties = self.request.old_resource_properties
        self.change_resource_record_sets(
            old_properties.certificate_arn, Action.DELETE
        )
        self.change_resource_record_sets(
            properties.certificate_arn, Action.UPSERT
        )

    def delete(self) -> None:
        """
        Delete AWS::Route53::RecordSetGroup resources.

        :rtype: None
        :return: None
        """
        properties = self.request.resource_properties
        self.change_resource_record_sets(
            properties.certificate_arn, Action.DELETE
        )

    def get_domain_validation_options(self, certificate_arn: str) -> str:
        """
        Retrieve the domain validation options for a given Certificate.

        Polling of the DescribeCertificate API endpoint is used since there is
        a latency period between when the certificate is created and when the
        resource records used for domain validation are available.

        :type certificate_arn: str
        :param certificate_arn: ARN of the ACM certificate

        :rtype: list
        :return: domain validation options for a given Certificate
        """
        def resource_records_exist(response: dict) -> bool:
            domain_validation_options = response['Certificate'
                                                 ]['DomainValidationOptions']
            for domain_validation_option in domain_validation_options:
                if not domain_validation_option.get('ResourceRecord'):
                    return False
            else:
                return True

        response = polling.poll(
            lambda: self.acm.
            describe_certificate(certificate_arn=certificate_arn),
            check_success=resource_records_exist,
            step=5,
            timeout=60
        )

        return response['Certificate']['DomainValidationOptions']

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

    def get_change_batch(self, action: Action, resource_record: dict) -> dict:
        """
        Create a change batch given a resource record set.

        The `resource_record` parameter has the following form:

        {
          'Name': 'string',
          'Type': 'CNAME',
          'Value': 'string'
        }

        :type action: Action
        :param action: action of a ChangeResourceRecordSets request
        :type resource_record: dict
        :param resource_record: resource record set for domain validation

        :rtype: dict
        :return: a dict containing the resource record set for domain
          validation
        """
        changes = []
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
