import logging

import whois

from config.config import DOMAIN_LOGS

logger = logging.getLogger(DOMAIN_LOGS['logger'])


def domain_whois(domain):
    """ enrich domains with WHOIS info """
    whois_results = {}
    iso8601 = '%Y-%m-%dT%H:%M:%S.%fZ'
    try:
        w = whois.whois(f'{domain}')
        if isinstance(w.creation_date, list):
            whois_results['creation_date'] = w.creation_date[0].strftime(iso8601)
        else:
            whois_results['creation_date'] = w.creation_date.strftime(iso8601)

        if isinstance(w.updated_date, list):
            whois_results['updated_date'] = w.updated_date[0].strftime(iso8601)
        else:
            whois_results['updated_date'] = w.updated_date.strftime(iso8601)

        if isinstance(w.expiration_date, list):
            whois_results['expiration_date'] = w.expiration_date[0].strftime(iso8601)
        else:
            whois_results['expiration_date'] = w.expiration_date.strftime(iso8601)

        whois_results['emails'] = w.emails
        whois_results['registrar'] = w.registrar
    except Exception as err:
        logger.error(f"Error getting WHOIS for domain '{domain}': {err}")

    return whois_results
