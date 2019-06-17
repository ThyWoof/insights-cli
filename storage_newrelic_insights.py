#
# author: Paulo Monteiro
# version: 0.1
#

import csv
import json
import requests


class StorageNewRelicInsights():

    INSIGHTS_MAX_EVENTS = 1000
    MAX_RETRIES = 5

    def __init__(self, account_file, insert_account_id, insert_api_key, timestamp=None):
        """init"""
        self.__account_file = account_file
        self.__headers = {
            'Content-Type': 'application/json',
            'X-Insert-Key': insert_api_key
        }
        self.__url = f'https://insights-collector.newrelic.com/v1/accounts/{insert_account_id}/events'
        self.__timestamp = timestamp

    def __gen_chunk(self, event_type, data=[], chunk_size=INSIGHTS_MAX_EVENTS):
        """slices data at chunk_size and generates a chunk with event_type injected in all dicts"""
        try:
            metadata = {'eventType': event_type, 'timestamp': self.__timestamp}
            for i in range(0, len(data), chunk_size):
                # metadata attributes have lower priority over event attributes
                yield [{**metadata, **event} for event in data[i:i+chunk_size]]
        except:
            pass

    def get_accounts(self):
        """returns a list of accounts dictionaries"""
        try:
            with open(self.__account_file) as f:
                csv_reader = csv.DictReader(f, delimiter=',')
                return list(dict(row) for row in csv_reader)
        except:
            return []

    def dump_data(self, master, event_type, data=[], max_retries=MAX_RETRIES):
        """appends the data to the event"""
        for chunk in self.__gen_chunk(event_type, data):
            succeeded = False
            count_retries = 0
            while not succeeded and count_retries < max_retries:
                try:
                    count_retries += 1
                    response = requests.post(
                        self.__url,
                        data=json.dumps(chunk),
                        headers=self.__headers
                    )
                    succeeded = (response.status_code == requests.codes.ok)
                except:
                    continue