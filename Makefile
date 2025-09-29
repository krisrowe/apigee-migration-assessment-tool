# Makefile for Apigee Migration Assessment Tool
#
# This Makefile provides a simple interface for setting up, testing, and running
# the assessment tool.

# Use bash for all shell commands
SHELL := /bin/bash
IMAGE_NAME := apigee-migration-assessment-tool:latest
PYTHON_EXEC := venv/bin/python

# Define variables that can be overridden from the command line.
APIGEE_USERNAME ?=
APIGEE_PASSWORD ?=
MFA_CODE ?=
SOURCE_ORG ?=
TESTS ?=

# Load .env file if it exists
ifneq (,$(wildcard .env))
    include .env
    export
endif

# Default command, runs if you just type "make"
.DEFAULT_GOAL := help

# Phony targets don't represent files
.PHONY: setup install test build token command run clean help

# Creates the necessary configuration files.
setup:
	@python3 scripts/setup.py -o "$(SOURCE_ORG)"

# Installs dependencies into a venv for local testing/development, mirroring the CI workflow.
install:
	@echo "--- Installing local dependencies for testing ---"
	@if ! command -v python3.12 &> /dev/null; then \
		echo "Error: python3.12 not found in PATH. Please install it to continue."; \
		exit 1; \
	fi
	@if [ ! -d "venv" ]; then \
		echo "Creating Python 3.12 virtual environment..."; \
		python3.12 -m venv venv; \
	fi
	@echo "Installing dependencies from requirements.txt and test-requirements.txt..."
	@$(PYTHON_EXEC) -m pip install --upgrade pip
	@$(PYTHON_EXEC) -m pip install -r requirements.txt -r test-requirements.txt
	@echo "Installation complete."

# Runs unit tests, mirroring the CI workflow.
test: install
	@echo "--- Running unit tests ---"
	@$(PYTHON_EXEC) -m unittest -v $(TESTS)

# Builds the Docker image.
build:
	@echo "--- Building Docker image: $(IMAGE_NAME) ---"
	@docker build -t $(IMAGE_NAME) .

# Generates a new auth token and prints it to stdout.
token:
	@APIGEE_USERNAME=$(APIGEE_USERNAME) APIGEE_PASSWORD=$(APIGEE_PASSWORD) MFA_CODE=$(MFA_CODE) bash scripts/get_token.sh 

# Displays the docker run command.
command:
	@if [ -z "$$SOURCE_AUTH_TOKEN" ]; then \
		echo "Error: SOURCE_AUTH_TOKEN is not set. Please run 'export SOURCE_AUTH_TOKEN=$(make token)' first."; \
		exit 1; \
	fi
	@echo ""
	@echo "--- Docker command for execution ---"
	@echo ""
	@echo "Copy and paste the following command to run the assessment:"
	@echo "----------------------------------------------------------------------"
	@echo 'docker run --rm -v "$$(pwd)/output:/app/target" -v "$$(pwd)/input.properties:/app/input.properties" -e SOURCE_AUTH_TOKEN="$$SOURCE_AUTH_TOKEN" "$(IMAGE_NAME)" --resources all --skip-target-validation'
	@echo "----------------------------------------------------------------------"
	@echo ""

# Builds the image and runs the tool. Requires SOURCE_AUTH_TOKEN to be set.
run: build
	@if [ -z "$$SOURCE_AUTH_TOKEN" ]; then \
		echo "Error: SOURCE_AUTH_TOKEN is not set. Please run 'export SOURCE_AUTH_TOKEN=$(make token)' first."; \
		exit 1; \
	fi
	@echo "--- Running assessment tool ---"
	@docker run --rm \
		-v "$(pwd)/output:/app/target" \
		-v "$(pwd)/input.properties:/app/input.properties" \
		-e SOURCE_AUTH_TOKEN="$$SOURCE_AUTH_TOKEN" \
		"$(IMAGE_NAME)" --resources all --skip-target-validation

# Resets the workspace to a fresh-clone state.
clean:
	@echo "--- Cleaning workspace ---"
	@git clean -dfx

help:
	@echo ""
	@echo "Apigee Migration Assessment Tool - Helper Scripts"
	@echo "-------------------------------------------------"
	@echo ""
	@echo "Interactive Workflow:"
	@echo "  1. make setup"
	@echo "  2. make build"
	@echo "  3. export SOURCE_AUTH_TOKEN=\$$(make token)" 
	@echo "  4. make command"
	@echo "  5. Copy, paste, and execute the command from the previous step."
	@echo ""
	@echo "Non-Interactive Workflow:"
	@echo "  1. make setup SOURCE_ORG=\"<org>\""
	@echo "  2. make build"
	@echo "  3. export SOURCE_AUTH_TOKEN=\$$(make token APIGEE_USERNAME=\"<user>\" APIGEE_PASSWORD=\"<pass>\" MFA_CODE=\"<mfa>\")"
	@echo "  4. make run"
	@echo ""
	@echo "Unit Testing:"
	@echo "  make install       - Creates a Python 3.12 venv and installs dependencies for local testing."
	@echo "  make test          - Runs all unit tests."
	@echo "  make test TESTS=tests/test_scripts.py - Runs tests only for a specific module."
	@echo ""
	@echo "Other Commands:"
	@echo "  make clean      - Resets the workspace to a fresh-clone state."
	@echo ""
	@echo "Prerequisites:"
	@echo "  - Docker installed and user added to docker group"
	@echo "  - If 'make build' fails with permission denied, run:"
	@echo "    sudo usermod -aG docker \$$USER && newgrp docker"
	@echo ""