import json
import requests
import sys
from pprint import pprint

# Setup http logging for debug purposes
import logging
logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True


def create_dataset(dataset_dict):
    """ Create a dataset in MetaX.
    Returns:
        The identifier of the newly created dataset
    """
    r = requests.post('https://metax-test.csc.fi/rest/datasets/',
                    headers={
                        'Content-Type': 'application/json',
                        'Accept': 'application/json'
                    },
                    json=dataset_dict,
                    verify=False)
    r.raise_for_status()
    return r.json()['identifier']


def replace_dataset(id, dataset_dict):
    """ Replace existing dataset in MetaX with a new version """
    r = requests.put('https://metax-test.csc.fi/rest/datasets/{id}'.format(id=id),
                    headers={
                        'Content-Type': 'application/json',
                    },
                    json=dataset_dict,
                    verify=False)
    r.raise_for_status()


def delete_dataset(id):
    """ Delete a dataset from MetaX """
    r = requests.delete('https://metax-test.csc.fi/rest/datasets/{id}'.format(id=id),
                     verify=False)
    r.raise_for_status()
