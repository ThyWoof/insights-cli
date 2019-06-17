#
# insights-cli.py: command line interface to Insights Query API
#
# author: Paulo Monteiro
# version: 0.1
#

from contextlib import contextmanager
import csv
import json
import os
import sys
import yaml

from insights_cli_argparse import parse_cmdline
from newrelic_query_api import NewRelicQueryAPI
from storage_local import StorageLocal
from storage_google_drive import StorageGoogleDrive
from storage_newrelic_insights import StorageNewRelicInsights


def msg(message, *args, stop=True):
    """lazy man log"""
    print(message.format(*args))
    if stop:
        exit(1)


@contextmanager
def open_file(filename=None, mode='r', *args, **kwargs):
    """open method facade for regular files, stdin and stdout"""
    if filename == '-':
        stream = sys.stdin if 'r' in mode else sys.stdout
        handler = stream.buffer if 'b' in mode else stream
    else:
        handler = open(filename, mode, *args, **kwargs)
    try:
        yield handler
    finally:
        try:
            handler.close()
        except:
            pass


def open_yaml(yaml_file):
    """open and parse an yaml file"""
    try:
        with open_file(yaml_file) as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
    except FileNotFoundError:
        msg(f'error: cannot open file {yaml_file}')
    except yaml.YAMLError:
        msg(f'error: cannot parse file {yaml_file}')
    return data


def validate_vault(vault):
    """validate the vault"""
    try:
        {secret['account_id']:secret['query_api_key'] for secret in vault.values()}
    except AttributeError as error:
        msg('error: vault must be a dictionary')
    except KeyError as error:
        msg(f'error: secret needs an {error.args[0]} key')


def validate_queries(queries, keys):
    """validate the queries list"""
    try:
        [queries[0][key] for key in keys]
    except KeyError as error:
        msg(f'error: column {error.args[0]} in queries list expected')
    return len(queries)


def validate_accounts(accounts, keys):
    """validate the accounts list"""
    try:
        [accounts[0][key] for key in keys]
    except KeyError as error:
        msg(f'error: column {error.args[0]} in account list expected')
    return len(accounts)


def export_events(storage, vault_file, query_file, master_names):
    """executes all queries against all accounts and dump to storage"""
    vault = open_yaml(vault_file)
    validate_vault(vault)

    queries = open_yaml(query_file)
    len_queries = validate_queries(queries, ['name', 'nrql'])

    accounts = storage.get_accounts()
    len_accounts = validate_accounts(accounts, ['master_name', 'account_name', 'account_id', 'query_api_key'])

    for idx_account,account in enumerate(accounts):
        master_name = account['master_name']
        account_name = account['account_name']
        try:
            if not master_name in master_names:
                continue
        except:
            pass

        metadata = {k:v for k,v in account.items() if not 'key' in k}

        for idx_query,query in enumerate(queries):
            name = query['name']
            nrql = query['nrql']
            try:
                secret = query['secret']
                account_id = vault[secret]['account_id']
                query_api_key = vault[secret]['query_api_key']
            except:
                 account_id = account['account_id']
                 query_api_key = account['query_api_key']

            msg('account {}/{}: {} - {}, query {}/{}: {}',
                idx_account+1, len_accounts, account_id, account_name, idx_query+1, len_queries, name,
                stop=False
            )

            api = NewRelicQueryAPI(account_id, query_api_key)
            events = list(api.events(nrql, include=metadata, params=metadata))
            storage.dump_data(master_name, name, events)


def do_batch_local(query_file='', vault_file='', master_names=[], account_file='', output_folder='', **kargs):
    """batch-local command"""
    storage = StorageLocal(account_file, output_folder)
    export_events(storage, vault_file, query_file, master_names)
    storage.destroy()


def do_batch_google(query_file='', vault_file='', master_names=[], account_file_id='', output_folder_id='', secret_file='', pivot_file='', **kargs):
    """batch-local command"""
    storage = StorageGoogleDrive(account_file_id, output_folder_id, secret_file)
    export_events(storage, vault_file, query_file, master_names)
    pivots = open_yaml(pivot_file) if pivot_file else {}
    storage.format_data(pivots)


def do_batch_insights(query_file='', vault_file='', master_names=[], account_file='', insert_account_id='', insert_api_key='', **kargs):
    """batch-insights command"""
    storage = StorageNewRelicInsights(account_file, insert_account_id, insert_api_key)
    export_events(storage, vault_file, query_file, master_names)


def do_query(query='', output_file='', output_format='', account_id='', query_api_key='', **kargs):
    """query command"""
    if not account_id:
        account_id = os.getenv('NEW_RELIC_ACCOUNT_ID', '')
    if not account_id:
        msg('account id not provided or NEW_RELIC_ACCOUNT_ID env not set')

    if not query_api_key:
        query_api_key = os.getenv('NEW_RELIC_QUERY_API_KEY', '')
    if not query_api_key:
        msg('query api key not provided or NEW_RELIC_QUERY_API_KEY env not set')

    if not output_file:
        output_file = '-'

    if query == '-':
        with open_file(query) as f:
            nrql = f.read()
    else:
        nrql = query

    api = NewRelicQueryAPI(account_id, query_api_key)
    events = list(api.events(nrql, include={'account_id': account_id}))

    if not len(events):
        msg('warning: empty events list returned', stop=False)

    try:
        with open_file(output_file, 'w') as f:
            if output_format == 'json':
                json.dump(events, f, sort_keys=True, indent=4)
            elif events:
                csv_writer = csv.DictWriter(f, fieldnames=events[0].keys())
                csv_writer.writeheader()
                for event in events:
                    csv_writer.writerow(event)
    except:
        msg(f'error: cannot write to {output_file}')


if __name__ == '__main__':
    args, error = parse_cmdline()
    locals()[args.command](**vars(args)) if not error else error()