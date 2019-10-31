# Miscellaneous

## AWS Lambda Timeout

The [`Timeout`](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-lambda-function.html#cfn-lambda-function-timeout) for an AWS Lambda function is the amount of time that Lambda allows a function to run before stopping it. The default is 3 seconds. The maximum allowed value is 900 seconds.

The timeout for the Certificate Validator Lambda function is set in the `serverless.yml` file:

```yaml
provider:
  ...
  timeout: 900
```

Here, the default is set to 900 seconds (15 minutes), which is the maximum amount of time a function may run.

The reason for using the maximum timeout is due to the latency between when the ACM certificate is requested and when it is issued. It may take less than a minute or several minutes for the certificate to be issued. Therefore, an execution time of 15 minutes allows ample time for AWS to issue the certificate.

## AWS Lambda Pricing

With AWS Lambda you are charged based on the number of requests for your functions and the duration of execution of your code.

**Requests**
You are charged $0.0000002 per request for the total number of requests across all your functions. However, the first 1M requests per month are free.

**Duration**
Duration is calculated from the time your code begins executing until it returns or otherwise terminates, rounded up to the nearest 100ms. The price depends on the amount of memory you allocate to your function. The first 400,000 GB-seconds per month are free.

The [`MemorySize`](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-lambda-function.html#cfn-lambda-function-memorysize) for an AWS Lambda function is the amount of memory that your function has access to. Increasing the function's memory also increases its CPU allocation. The default value is 128 MB.

The memory size for the Certificate Validator Lambda function is not set in the `serverless.yml` file and therefore uses the default set by Serverless which is 1024 MB.

With a memory size of 1024 MB, you are granted 400,000 free tier seconds per month or approximately 6666.67 minutes. Since, certificate creation is an infrequent occurrence and median execution time is very low, you should be well within the Lambda free tier limits when utilizing Certificate Validator in your infrastructure.
