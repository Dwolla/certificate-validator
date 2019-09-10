# -*- coding: utf-8 -*-
"""Exceptions module."""


class CertificateValidatorException(Exception):
    """
    Base exception class for Certificate Validator exceptions.
    """
    def __init__(self, *args, **kwargs) -> None:
        """
        Create a new `CertificateValidatorException` object.

        :rtype: None
        :return: None
        """
        if hasattr(self, 'msg'):
            self.msg = self.msg.format(**kwargs)
        else:
            self.msg = ''
        super(CertificateValidatorException, self).__init__(self.msg)


class UnknownRequestType(CertificateValidatorException):
    """
    Raised when the request type is not one of Create, Update, or Delete.

    The RequestType is set by the AWS CloudFormation stack operation
    (create-stack, update-stack, or delete-stack) that was initiated by the
    template developer for the stack that contains the custom resource.

    Must be one of: Create, Update, or Delete.
    """
    msg = 'Unknown RequestType: Must be one of: Create, Update, or Delete.'
