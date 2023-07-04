import contextlib
import logging
import os

import dnstwist

from config.config import DOMAIN_LOGS

logger = logging.getLogger(DOMAIN_LOGS['logger'])


def supress_stdout(func):
    def wrapper(*a, **ka):
        with open(os.devnull, 'w') as devnull:
            with contextlib.redirect_stdout(devnull):
                return func(*a, **ka)
    return wrapper


class Twisted:
    def __init__(self, target_domain):
        self.domain = target_domain
        self.active_lookalikes = self.run(self.domain)
    
    @supress_stdout
    def run(self, domain):
        """ Run the DomainMonitor 
        
        :param domain: domain to monitor
        :return data: list of active lookalike domains
        """
        logger.info("Running dnstwist...")
        try:
            data = dnstwist.run(domain=domain, registered=True, mxcheck=True, format='json', nameservers="1.1.1.1,8.8.8.8")
        
            # add original domain to each item in the list
            for result in data:
                result['event_type'] = 'result'
                result['original_domain'] = domain
                
        except Exception as err:
            logger.error(f"Error running dnstwist: {err}")

        return data
