# Certificate Validator Example

## Prerequisites

* Set the Amazon Resource Name (ARN) of the custom resource in `parameters.json` or `parameters.properties`.

**Example**

```json
[
  {
    "ParameterKey": "ServiceToken",
    "ParameterValue": "arn:aws:lambda:<region>:<account-id>:function:<function-name>"
  }
]
```

```properties
ServiceToken=arn:aws:lambda:<region>:<account-id>:function:<function-name>
```

**Note**: The service token must be in the same region as the CloudFormation stack.

* Set the domain name purchased through AWS in `parameters.json` or `parameters.properties`.

* Set a CloudFormation stack name:

```bash
STACK_NAME=<stack-name>
```

## Validation

```bash
aws cloudformation validate-template \
--template-body file://template.yaml
```

## Deployment

```bash
aws cloudformation create-stack \
--stack-name $STACK_NAME \
--template-body file://template.yaml \
--parameters file://parameters.json
```

Alternatively, using `deploy`:

```bash
aws cloudformation deploy \
--stack-name $STACK_NAME \
--template-file template.yaml \
--parameter-overrides $(cat parameters.properties)
```
