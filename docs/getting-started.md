# Getting Started

It is extremely easy to get started with Certificate Validator.

1. Clone the [`certificate-validator`](https://github.com/Dwolla/certificate-validator) repository or download the latest [release](https://github.com/Dwolla/certificate-validator/releases).

2. Install Node.js and NPM:

```bash
brew install node
```

3. Install the Serverless Framework open-source CLI:

```bash
npm install -g serverless
```

4. Deploy Certificate Validator:

```bash
make deploy
```

**Note**: An optional `STAGE` variable can be used to specify the *stage*. Defaults to `dev`.

**Example**

```bash
make deploy STAGE=prod
```

To remove Certificate Validator, run `make remove`.

**Note**: An optional `STAGE` variable can be used to specify the *stage*. Defaults to `dev`.

**Example**

```bash
make remove STAGE=prod
```

5. Retrieve the Amazon Resource Name (ARN) of your newly created AWS Lambda function.

**Example**

```
arn:aws:lambda:<region>:<account-id>:function:<function-name>
```

The ARN of the AWS Lambda function serves as the service token ([`ServiceToken`](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cfn-customresource.html#cfn-customresource-servicetoken)) for your `Custom::Certificate` and `Custom::CertificateValidator` custom resources.

**Note**: The service token must be in the same region as the CloudFormation stack.

6. Add the `Custom::Certificate` and `Custom::CertificateValidator` custom resources to your CloudFormation template:

**Example**

```yaml
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

The `Custom::Certificate` custom resource can now be used anywhere a `AWS::CertificateManager::Certificate` resource would be used by calling `!GetAtt Certificate.CertificateArn`.

**Warning**: Since the ARN of a `AWS::CertificateManager::Certificate` resource is returned when you pass the logical ID of this resource to the intrinsic `Ref` function, an implicit dependency is created when it is referenced by other resources in your CloudFormation template. This ensures that the resource that references the `AWS::CertificateManager::Certificate` resource is created only after the certificate has been created. This is not the case for a `Custom::Certificate` custom resource, since the ARN is retrieved using the intrinsic `GetAtt` function, which does not create an implicit dependency. Therefore, you must explicitly create the dependency using the [`DependsOn`](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-attribute-dependson.html) attribute for the `Custom::CertificateValidator` custom resource.

**Example**

```yaml
CloudFrontDistribution:
  DependsOn: CertificateValidator
  Type: AWS::CloudFront::Distribution
  Properties:
    ...
```

The `Custom::CertificateValidator` uses a [waiter](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/acm.html?highlight=waiter#waiters), which polls for the status of the `AWS::CertificateManager::Certificate` resource created by the `Custom::Certificate` custom resource and only allows execution to proceed after the certificate has been issued.

For an example CloudFormation stack, see [`certificate-validator/example`](https://github.com/Dwolla/certificate-validator/tree/master/example).
