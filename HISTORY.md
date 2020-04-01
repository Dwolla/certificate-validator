# History

## v???

* Deploy certificate to same region as CloudFormation stack
* Allow Setting Log Level from CloudFormation Stack
* Do not fail if SubjectAlternativeNames is an empty list. Support empty items
  in SubjectAlternativeNames list.

## v0.4.1 (2019-09-19)
---

* The timeout for the Certificate Validator Lambda function is now 900 seconds
(15 minutes).

## v0.4.0 (2019-09-19)
---

* A delete request will no longer fail if the specified resources do not exist.

## v0.3.0 (2019-09-18)
---

* The CertificateValidator custom resource will now wait until the ACM
Certificate is issued before returning a SUCCESS response.

## v0.2.0 (2019-09-16)
---

* The CertificateValidator custom resource can now handle subject alternative
names in multiple hosted zones.

* The CertificateValidator custom resource will now remove the CNAME records
for subject alternative names that are removed from the Certificate custom
resource.

## v0.1.0 (2019-09-10)
---

* First release.
