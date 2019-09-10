.PHONY: help clean deploy package test
.DEFAULT_GOAL := help

PACKAGE_DIR := package
STAGE := dev

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

help: ## display help information
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

clean: ## remove deployment and Python artifacts
	rm -f certificate-validator.zip
	rm -rf ${PACKAGE_DIR}
	@$(MAKE) -C certificate_validator clean

deploy: package ## deploy AWS Lambda function via Serverless
	serverless deploy -v --stage ${STAGE}

package: clean ## create AWS Lambda function deployment package
	mkdir -p ${PACKAGE_DIR}
	pip3 install -r certificate_validator/requirements.txt -t ${PACKAGE_DIR}
	cp -R certificate_validator/certificate_validator ${PACKAGE_DIR}
	cd ${PACKAGE_DIR}; \
	zip -9 --exclude '*dist-info*' '*__pycache__*' -r ../certificate-validator.zip *;

test: ## run certificate_validator tests
	@$(MAKE) -C certificate_validator test

format: ## format certificate_validator code and imports
	@$(MAKE) -C certificate_validator format
