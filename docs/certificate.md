# Custom::Certificate

The `Custom::Certificate` resource creates, updates, and deletes a [`AWS::CertificateManager::Certificate`](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-certificatemanager-certificate.html) resource.

The `Custom::Certificate` resource requests an AWS Certificate Manager (ACM) certificate that you can use to enable secure connections. However, unlike a `AWS::CertificateManager::Certificate` resource, the `Custom::Certificate` resource returns a successful status upon creation, *not* upon validation of the certificate request.

From the [`AWS::CertificateManager::Certificate`](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-certificatemanager-certificate.html) documentation:

>**Important**
>
>When you use the `AWS::CertificateManager::Certificate` resource in an AWS CloudFormation stack, the stack will remain in the `CREATE_IN_PROGRESS` state. Further stack operations will be delayed until you validate the certificate request, either by acting upon the instructions in the validation email, or by adding a CNAME record to your DNS configuration.

## Syntax

To declare this resource in your AWS CloudFormation template, use the following syntax:

```yaml
Type: Custom::Certificate
Properties:
  ServiceToken: String
  DomainName: String
  SubjectAlternativeNames:
    - String
```

## Properties

### `LogLevel`

Log Level for Lambda Function output

One of: DEBUG, INFO, WARNING, ERROR, CRITICAL

*Default*: INFO
*Required*: No
*Type*: String

### `ServiceToken`

>**Note**
>Only one property is defined by AWS for a custom resource: `ServiceToken`. All other properties are defined by the service provider.

The service token that was given to the template developer by the service provider to access the service, such as an Amazon SNS topic ARN or Lambda function ARN. The service token must be from the same region in which you are creating the stack.

Updates are not supported.

*Required*: Yes
*Type*: String
*Update requires*: Replacement

### `DomainName`

The fully qualified domain name (FQDN), such as `www.example.com`, with which you want to secure an ACM certificate. Use an asterisk (*) to create a wildcard certificate that protects several sites in the same domain. For example, `*.example.com` protects `www.example.com`, `site.example.com`, and `images.example.com`.

*Required*: Yes
*Type*: String
*Minimum*: 1
*Maximum*: 253
*Pattern*: `^(\*\.)?(((?!-)[A-Za-z0-9-]{0,62}[A-Za-z0-9])\.)+((?!-)[A-Za-z0-9-]{1,62}[A-Za-z0-9])$`
*Update requires*: Replacement

### `SubjectAlternativeNames`

Additional FQDNs to be included in the Subject Alternative Name extension of the ACM certificate. For example, you can add `www.example.net` to a certificate for which the `DomainName` field is `www.example.com` if users can reach your site by using either name.

*Required*: No
*Type*: List of String
*Maximum*: 100
*Update requires*: Replacement

## Return Values

The [`Fn::GetAtt`](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-getatt.html) intrinsic function returns values that are defined by the custom resource provider. The following values are retrieved by calling `Fn::GetAtt` on the provider-defined attributes.

### `CertificateArn`

Returns the Amazon Resource Name (ARN) of the AWS Certificate Manager (ACM) certificate resource.

Example: `arn:aws:acm:<region>:<account-id>:certificate/<certificate-id>`

## Examples

**Example**

```yaml
AWSTemplateFormatVersion: '2010-09-09'

Description: Certificate Validator example

Parameters:
  DomainName:
    Description: Domain name for the certificate
    Type: String
  ServiceToken:
    Description: AWS Lambda function ARN
    Type: String

Resources:

  Certificate:
    Type: Custom::Certificate
    Properties:
      ServiceToken: !Ref ServiceToken
      DomainName: !Ref DomainName
      SubjectAlternativeNames:
        - !Sub 'www.${DomainName}'
```
