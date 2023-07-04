import os

BASE = os.path.join(os.getcwd())

DOMAIN_LIST = {
    'filename': os.path.join(BASE, 'domains.txt')
}

DOMAIN_LOGS = {
    'logger': 'domains.log',
    'log_file': os.path.join(BASE, 'logs', 'domain_monitor.log')
}

AZURE_CONFIG = {
    'WorkspaceId': os.environ.get('WORKSPACE_ID'),
    'SharedKey': os.environ.get('SHARED_KEY'),
    'AZURE_STORAGE_ACCOUNT': os.environ.get('azure_storage_account'),
    'AZURE_STORAGE_BLOB_NAME': os.environ.get('azure_storage_blob_name'),
    'AZURE_STORAGE_CONTAINER': os.environ.get('azure_storage_container'),
    'AZURE_STORAGE_CONNECTION_STRING': os.environ.get('connection_string'),
}