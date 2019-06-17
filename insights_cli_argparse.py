import argparse

def parse_cmdline():
    """parse the command line"""
    parser = argparse.ArgumentParser()
    parser.set_defaults(command=None)
    subparsers = parser.add_subparsers()
    prepare_query_parser(subparsers)
    prepare_batch_local_parser(subparsers)
    prepare_batch_google_parser(subparsers)
    prepare_batch_insights_parser(subparsers)
    args = parser.parse_args()
    error = parser.print_help if args.command == None else None
    return args, error


def prepare_query_parser(subparsers):
    query_parser = subparsers.add_parser('query')
    query_parser.set_defaults(command='do_query')
    query_parser.add_argument('-k', '--query-api-key',
        help='New Relic Insights query API key'
    )
    query_parser.add_argument('-a', '--account-id',
        help='New Relic account id',
        type=int
    )
    query_parser.add_argument('-o', '--output-file',
        help='Output file name'
    )
    query_parser.add_argument('-f', '--output-format',
        help='Output type',
        choices=['json', 'csv'],
        default='json'
    )
    query_parser.add_argument('-q', '--query',
        help='New Relic Insights query language https://docs.newrelic.com/docs/insights/nrql-new-relic-query-language/nrql-reference/nrql-syntax-components-functions',
        required=True
    )

def prepare_batch_local_parser(subparsers):
    batch_local_parser = subparsers.add_parser('batch-local')
    batch_local_parser.set_defaults(command='do_batch_local')
    batch_local_parser.add_argument('-v', '--vault-file',
        help='Local YAML vault file [secret:{account_id,query_api_key}]',
    )
    batch_local_parser.add_argument('-q', '--query-file',
        help='Local YAML queries file [{name,nrql}]',
        required=True
    )
    batch_local_parser.add_argument('-a', '--account-file',
        help='Local accounts list CSV file [master_name,account_id,account_name,query_api_key]',
        required=True
    )
    batch_local_parser.add_argument('-o', '--output-folder',
        help='Local output folder name',
        required=True
    )
    batch_local_parser.add_argument('-m', '--master-names',
        help='Filter master names from account list', nargs='+'
    )


def prepare_batch_google_parser(subparsers):
    batch_google_parser = subparsers.add_parser('batch-google')
    batch_google_parser.set_defaults(command='do_batch_google')
    batch_google_parser.add_argument('-v', '--vault-file',
        help='Local YAML vault file [secret:{account_id,query_api_key}]',
    )
    batch_google_parser.add_argument('-q', '--query-file',
        help='Local YAML queries file [{name,nrql}]',
        required=True
    )
    batch_google_parser.add_argument('-a', '--account-file-id',
        help='Google accounts list Sheets id [master_name,account_id,account_name,query_api_key]',
        required=True
    )
    batch_google_parser.add_argument('-o', '--output-folder-id',
        help='Google Drive output Folder id',
        required=True
    )
    batch_google_parser.add_argument('-s', '--secret-file',
        help='Google API secret file',
        required=True
    )
    batch_google_parser.add_argument('-p', '--pivot-file',
        help='Local YAML pivot tables file',
        default='pivots.yaml'
    )
    batch_google_parser.add_argument('-m', '--master-names',
        help='Filter master names from account list', nargs='+'
    )


def prepare_batch_insights_parser(subparsers):
    batch_insights_parser = subparsers.add_parser('batch-insights')
    batch_insights_parser.set_defaults(command='do_batch_insights')
    batch_insights_parser.add_argument('-v', '--vault-file',
        help='Local YAML vault file [secret:{account_id,query_api_key}]',
    )
    batch_insights_parser.add_argument('-q', '--query-file',
        help='Local YAML queries file [{name,nrql}]',
        required=True
    )
    batch_insights_parser.add_argument('-a', '--account-file',
        help='Local accounts list CSV file [master_name,account_id,account_name,query_api_key]',
        required=True
    )
    batch_insights_parser.add_argument('-i', '--insert-account-id',
        help='New Relic Insights insert account id',
        type=int,
        required=True
    )
    batch_insights_parser.add_argument('-k', '--insert-api-key',
        help='New Relic Insights insert API key',
        required=True
    )
    batch_insights_parser.add_argument('-m', '--master-names',
        help='Filter master names from account list', nargs='+'
    )