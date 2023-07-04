#!/usr/bin/env python3

import os
import concurrent.futures
import datetime
import json
import logging

import modules.azure_logging as LogToAzure
from config.config import DOMAIN_LIST, DOMAIN_LOGS, BASE, AZURE_CONFIG
from modules.twisted import Twisted
from modules.get_whois import domain_whois
from azure.identity import DefaultAzureCredential, ManagedIdentityCredential
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

logger = logging.getLogger(DOMAIN_LOGS['logger'])

DOMAINS = DOMAIN_LIST['filename']
AZURE_STORAGE_ACCOUNT = AZURE_CONFIG['AZURE_STORAGE_ACCOUNT']
AZURE_STORAGE_BLOB_NAME = AZURE_CONFIG['AZURE_STORAGE_BLOB_NAME']
AZURE_STORAGE_CONTAINER = AZURE_CONFIG['AZURE_STORAGE_CONTAINER']
AZURE_STORAGE_CONNECTION_STRING = AZURE_CONFIG['AZURE_STORAGE_CONNECTION_STRING']

class DomainMonitor:
    def __init__(self, domain):
        self.domain = domain
        self.dnstwist_results = self.check_lookalikes()
        self.whois_results = self.get_whois()

    def check_lookalikes(self):
        """ check domain using dnstwist for lookalike domains
        
        :param domain: domain to monitor
        """

        logger.info(f"Checking for lookalike domains for: {self.domain}...")
        results = Twisted(self.domain).active_lookalikes
        return results
        
    
    def get_whois(self):
        """ enrich domains with WHOIS info 
        
        :param dnstwist_results: list of active lookalike domains
        """

        for result_domain in self.dnstwist_results:
            logger.info(f"Checking WHOIS for: {result_domain['domain']}")
            # update dnstwist_results object with WHOIS info
            result_domain['whois'] = domain_whois(result_domain['domain'])

    def azure_logging(self):
        """ Log results to Azure """
        logger.info("Sending results to Azure...")
        try:
            json_results = json.dumps(self.dnstwist_results)
            LogToAzure.post_data(json_results)
        except Exception as err:
            logger.error(f"Error sending results to Azure: {err}")


def _logger():
    logger.setLevel(logging.INFO)
    # create file handler which logs even debug messages
    fh = logging.FileHandler(DOMAIN_LOGS['log_file'])
    fh.setLevel(logging.INFO)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s [%(process)d] - %(levelname)s - %(message)s',
                                   "%Y-%m-%d %H:%M:%S")
    fh.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(fh)


def check_domain(domain):
    dm = DomainMonitor(domain)
    dm.azure_logging()


if __name__ == "__main__":
    start_time = datetime.datetime.now()
    _logger()
    json_log = json.dumps([{'event_type': 'script_status', 'status': 'script started'}])
    LogToAzure.post_data(json_log)
    logger.info("Starting DomainMonitor...")

    try:
        account_url = f"https://{AZURE_STORAGE_ACCOUNT}.blob.core.windows.net"
        blob_service_client = BlobServiceClient(account_url, credential=ManagedIdentityCredential())
        container_client = blob_service_client.get_container_client(container=AZURE_STORAGE_CONTAINER)
    except Exception as err:
        logger.error(f"Error connecting to Azure Storage: {err}")
        json_log = json.dumps([{'event_type': 'script_status', 'status': f'Error connecting to Azure Storage: {err}'}])
        LogToAzure.post_data(json_log)
    
    download_file_path = os.path.join(BASE, 'domains.txt')

    # download domains list from storage account
    with open(file=download_file_path, mode="wb") as download_file:
        download_file.write(container_client.download_blob(AZURE_STORAGE_BLOB_NAME).readall())

    # check if there are any domains in the downloaded fil
    if os.stat(download_file_path).st_size == 0:
        logger.error("No domains found in file")
        json_log = json.dumps([{'event_type': 'script_status', 'status': 'No domains found in file'}])
        LogToAzure.post_data(json_log)
        exit(1)

    with open(download_file_path, 'r') as f:
        domains = f.read().splitlines()
        executor = concurrent.futures.ProcessPoolExecutor(max_workers=10)
        futures = [executor.submit(check_domain, domain) for domain in domains]
        concurrent.futures.wait(futures)
    
    delta = datetime.datetime.now() - start_time
    logger.info(f"Processing took {delta.total_seconds()} seconds")
    json_log = json.dumps([{'event_type': 'script_status', 'status': f'script completed and took {delta.total_seconds()} seconds'}])
    LogToAzure.post_data(json_log)
