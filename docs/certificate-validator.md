# Custom::CertificateValidator

The `Custom::CertificateValidator` resource creates, updates, and deletes a [`AWS::Route53::RecordSetGroup`](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-route53-recordsetgroup.html) resource.

The `Custom::CertificateValidator` resource retrieves the record set used by AWS Certificate Manager (ACM) to validate a certificate.

From the [Use DNS to Validate Domain Ownership](https://docs.aws.amazon.com/acm/latest/userguide/gs-acm-validate-dns.html) documentation:

>ACM uses CNAME (Canonical Name) records to validate that you own or control a domain. When you choose DNS validation, ACM provides you one or more CNAME records to insert into your DNS database. For example, if you request a certificate for the `example.com` domain with `www.example.com` as an additional name, ACM creates two CNAME records for you. Each record, created specifically for your domain and your account, contains a name and a value. The value is an alias that points to a domain that ACM owns and which ACM uses to automatically renew your certificate. You add the CNAME records to your DNS database only once. ACM automatically renews your certificate as long as the certificate is in use and your CNAME record remains in place. In addition, if you use Amazon Route 53 to create your domain, ACM can write the CNAME records for you.

## Syntax

To declare this resource in your AWS CloudFormation template, use the following syntax:

```yaml
Type: Custom::CertificateValidator
Properties:
  ServiceToken: String
  CertificateArn: String
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

### `CertificateArn`

The Amazon Resource Name (ARN) of the AWS Certificate Manager (ACM) certificate resource.

*Required*: Yes
*Type*: String
*Update requires*: Replacement

## Return Values

None

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

  CertificateValidator:
    Type: Custom::CertificateValidator
    Properties:
      ServiceToken: !Ref ServiceToken
      CertificateArn: !GetAtt Certificate.CertificateArn
```
