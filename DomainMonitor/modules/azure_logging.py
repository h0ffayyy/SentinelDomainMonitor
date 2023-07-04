import os
import requests
import datetime
import hashlib
import hmac
import base64
import logging

from config.config import DOMAIN_LOGS, AZURE_CONFIG

logger = logging.getLogger(DOMAIN_LOGS['logger'])

# The log type is the name of the event that is being submitted
log_type = 'DomainMonitor'
WORKSPACE_ID = AZURE_CONFIG('WorkspaceId')
WORKSPACE_KEY = AZURE_CONFIG('SharedKey')

# Build the API signature
def build_signature(customer_id, shared_key, date, content_length, method, content_type, resource):
    x_headers = 'x-ms-date:' + date
    string_to_hash = method + "\n" + str(content_length) + "\n" + content_type + "\n" + x_headers + "\n" + resource
    bytes_to_hash = bytes(string_to_hash, encoding="utf-8")  
    decoded_key = base64.b64decode(shared_key)
    encoded_hash = base64.b64encode(hmac.new(decoded_key, bytes_to_hash, digestmod=hashlib.sha256).digest()).decode()
    authorization = f"SharedKey {customer_id}:{encoded_hash}"
    return authorization

# Build and send a request to the POST API
def post_data(body):
    customer_id = WORKSPACE_ID
    shared_key = WORKSPACE_KEY
    method = 'POST'
    content_type = 'application/json'
    resource = '/api/logs'
    rfc1123date = datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
    content_length = len(body)
    signature = build_signature(customer_id, shared_key, rfc1123date, content_length, method, content_type, resource)
    uri = f'https://{customer_id}.ods.opinsights.azure.com{resource}?api-version=2016-04-01'

    headers = {
        'content-type': content_type,
        'Authorization': signature,
        'Log-Type': log_type,
        'x-ms-date': rfc1123date
    }

    response = requests.post(uri,data=body, headers=headers)
    if (response.status_code >= 200 and response.status_code <= 299):
        logger.info('Accepted')
    else:
        logger.error(f"Error sending logs to Azure. Response code: {response.status_code}")
