#
# author: Paulo Monteiro
# version: 0.1
#

import csv
import os
import time

class StorageLocal():

    def __init__(self, account_file, output_folder, timestamp=None, prefix='RUN'):
        """init"""
        self.__cache = {}
        self.__account_file = account_file
        self.__output_folder = \
            os.path.join(
                output_folder,
                time.strftime(
                    f'{prefix}_%Y-%m-%d_%H-%M',
                    time.localtime() if not timestamp else timestamp
                )
            )

    #@contextmanager
    def __get_handle(self, name):
        """returns a file handle from the cache or creates a new one"""
        if not name in self.__cache:
            handler = open(os.path.join(self.__output_folder, name + '.csv'), 'w')
            self.__cache.update({name: handler})
            just_created = True
        else:
            just_created = False
        return self.__cache[name], just_created

    def get_accounts(self):
        """returns a list of accounts dictionaries"""
        try:
            with open(self.__account_file) as f:
                csv_reader = csv.DictReader(f, delimiter=',')
                return list(dict(row) for row in csv_reader)
        except:
            return []

    def dump_data(self, master, output_file, data=[]):
        """appends the data to the output file"""
        if not self.__cache:
            os.mkdir(self.__output_folder, mode=0o755)
        try:
            handle, just_created = self.__get_handle(master + '_' + output_file)
            csv_writer = csv.DictWriter(handle, fieldnames=data[0].keys())
            if just_created:
                csv_writer.writeheader()
            for row in data:
                csv_writer.writerow(row)
            handle.flush()
        except:
            pass

    def destroy(self):
        for filename in self.__cache:
            self.__cache[filename].close()