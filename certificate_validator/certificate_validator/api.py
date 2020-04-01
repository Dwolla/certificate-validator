# -*- coding: utf-8 -*-
"""AWS API module."""

from enum import Enum

import boto3
import botocore


class ValidationMethod(str, Enum):
    """
    ValidationMethod of a RequestCertificate request.

    The ValidationMethod is the method you want to use to validate that you own
    or control the domain associated with a public certificate. You can
    validate with DNS or validate with email.
    """
    DNS = 'DNS'
    EMAIL = 'EMAIL'


class AWS:
    """
    Wrapper for the AWS SDK for Python.

    The AWS class provides a default configuration for a `boto3.Session` from
    which a low-level service client can be created.
    """
    SERVICE_NAME = None
    REGION = 'us-east-1'

    def __init__(self, region: str = None) -> None:
        """
        Create a new `AWS` object.

        :type region: str
        :param region: region associated with the client
            A client may only be associated with a single region.

        :rtype: None
        :return: None
        """
        self.region = region or self.REGION
        self.session = self._get_session()
        self.client = self._get_client()

    def _get_session(self) -> boto3.Session:
        """
        Create a session.

        :rtype: boto3.Session
        :return: a boto3 session instance
        """
        session_config = {'region_name': self.region}
        return boto3.Session(**session_config)

    def _get_client(self) -> botocore.client.BaseClient:
        """
        Create a low-level service client by name.

        :rtype: botocore.client.BaseClient
        :return: a botocore client instance
        """
        client_config = {
            'use_ssl': True,
        }
        return self.session.client(self.SERVICE_NAME, **client_config)


class ACM(AWS):
    """
    Wrapper for a low-level client representing AWS Certificate Manager (ACM).
    """
    SERVICE_NAME = 'acm'

    def __init__(self, *args, **kwargs) -> None:
        """
        Create a new `ACM` object.

        :rtype: None
        :return: None
        """
        super(ACM, self).__init__(*args, **kwargs)
        self.waiter = self.client.get_waiter('certificate_validated')

    def request_certificate(
        self, domain_name: str, subject_alternative_names: list
    ) -> dict:
        """
        Request an ACM certificate for use with other AWS services.

        Returns:
        {
          'CertificateArn': 'string'
        }

        :type domain_name: str
        :param domain_name: a fully qualified domain name (FQDN)
        :type subject_alternative_names: list
        :param subject_alternative_names: additional FQDNs to be included

        :rtype: dict
        :return: ARN of the issued certificate
        """
        kwargs = dict(
            DomainName=domain_name,
            ValidationMethod=ValidationMethod.DNS.value
        )
        if subject_alternative_names:
            kwargs['SubjectAlternativeNames'] = subject_alternative_names
        return self.client.request_certificate(**kwargs)

    def delete_certificate(self, certificate_arn: str) -> None:
        """
        Delete a certificate and its associated private key.

        :type certificate_arn: str
        :param certificate_arn: ARN of the ACM certificate to be deleted

        :rtype: None
        :return: None
        """
        return self.client.delete_certificate(CertificateArn=certificate_arn, )

    def describe_certificate(self, certificate_arn: str) -> dict:
        """
        Retrieve detailed metadata about the specified ACM certificate.

        :type certificate_arn: str
        :param certificate_arn: ARN of the ACM certificate

        :rtype: dict
        :return: detailed metadata about the specified ACM certificate
        """
        return self.client.describe_certificate(
            CertificateArn=certificate_arn,
        )

    def wait(self, certificate_arn: str) -> None:
        """
        Wait for the specified ACM certificate to be issued.

        Poll the DescribeCertificate API endpoint every 5 seconds until a
        successful state is reached. An error is returned after 60 failed
        checks (5 minutes).

        :type certificate_arn: str
        :param certificate_arn: ARN of the ACM certificate

        :rtype: None
        :return: None
        """
        return self.waiter.wait(
            CertificateArn=certificate_arn,
            WaiterConfig={
                'Delay': 5,
                'MaxAttempts': 60
            }
        )


class Route53(AWS):
    """
    Wrapper for a low-level client representing Amazon Route 53.
    """
    SERVICE_NAME = 'route53'

    def __init__(self, *args, **kwargs):
        """
        Create a new `Route53` object.

        :rtype: None
        :return: None
        """
        super(Route53, self).__init__(*args, **kwargs)

    def change_resource_record_sets(
        self, hosted_zone_id: str, change_batch: dict
    ) -> dict:
        """
        Create, change, or delete a resource record set.

        A resource record set contains authoritative DNS information for a
        specified domain name or subdomain name.

        Example change batch:
        {
          'Changes': [
            {
              'Action': 'CREATE'|'DELETE'|'UPSERT',
              'ResourceRecordSet': {
                ...
              }
            },
          ]
        }

        Returns:
        {
          'ChangeInfo': {
            'Id': 'string',
            'Status': 'PENDING'|'INSYNC',
            'SubmittedAt': datetime(2015, 1, 1),
            'Comment': 'string'
            }
        }

        :type hosted_zone_id: str
        :param hosted_zone_id: ID of the hosted zone
        :type change_batch: dict
        :param change_batch: a dict containing the `Changes` object

        :rtype: dict
        :return: a dict containing the response for the request
        """
        return self.client.change_resource_record_sets(
            HostedZoneId=hosted_zone_id, ChangeBatch=change_batch
        )

    def list_hosted_zones_by_name(
        self, dns_name: str = '', max_items: str = '1'
    ) -> dict:
        """
        Retrieve a list of hosted zones in lexicographic order.

        Returns:
        {
          'HostedZones': [
            {
              'Id': 'string',
              'Name': 'string',
              ...
            }
          ],
          ...
        }

        :type dns_name: str
        :param dns_name: DNS name of the hosted zone
        :type max_items: str
        :param max_items: maximum number of hosted zones to be included in the
          response body for this request. Defaults to 1.

        :rtype: dict
        :return: a dict containing the response for the request
        """
        return self.client.list_hosted_zones_by_name(
            DNSName=dns_name, MaxItems=max_items
        )
