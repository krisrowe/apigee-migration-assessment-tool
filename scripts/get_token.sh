#!/bin/bash
# This script generates and prints an Apigee OAuth2 token.
# It prompts for credentials if they are not provided as environment variables.

# --- Use existing credentials or prompt if missing ---
if [ -z "$APIGEE_USERNAME" ]; then
    read -p "Enter your Apigee Username (email): " APIGEE_USERNAME
fi
if [ -z "$APIGEE_PASSWORD" ]; then
    read -s -p "Enter your Apigee Password: " APIGEE_PASSWORD
    echo "" >&2
fi

# --- Get MFA code from user or environment variable ---
if [ -z "$MFA_CODE" ]; then
    read -p "Please enter your 6-digit MFA code: " -s MFA_CODE >&2
    echo "" >&2 # Add a newline after the prompt
fi

# --- Generate the token using curl and parse it ---
TOKEN_RESPONSE=$(curl -s -H "Content-Type:application/x-www-form-urlencoded;charset=utf-8" \
  -H "Accept: application/json;charset=utf-8" \
  -H "Authorization: Basic ZWRnZWNsaTplZGdlY2xpc2VjcmV0" \
  -X POST https://login.apigee.com/oauth/token \
  -d "username=$APIGEE_USERNAME&password=$APIGEE_PASSWORD&mfa_token=$MFA_CODE&grant_type=password")

ACCESS_TOKEN=$(echo $TOKEN_RESPONSE | grep -o '"access_token":"[^"]*' | sed 's/"access_token":"//')

if [ -z "$ACCESS_TOKEN" ]; then
    echo "Error: Failed to get access token. Please check your credentials and MFA code." >&2
    echo "API Response: $TOKEN_RESPONSE" >&2
    exit 1
fi

# --- Print ONLY the token to stdout ---
echo $ACCESS_TOKEN
