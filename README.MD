# Introduction #

This repository aims to simplify the consumption of New Relic events gathered from the Insights Query API. Although the Insights API is very simple to use the challenge resides on getting a consistent result set. The returned payload can have different structures depending on the NRQL issued. This isn't a problem for quick adhoc requests but can become difficult to handle if we don't provide a well-known interface to the results.

# NRQL Use Cases #

This interface will always return a list of dictionaries from the parsed payload. Check the [Insights New Relic Reference](https://docs.newrelic.com/docs/insights/nrql-new-relic-query-language/nrql-reference/nrql-syntax-components-functions) if you need to refresh your NRQL knowledge.

All NRQL syntax constructions and valid combinations are supported:

* Show Event Types
* Select keyset() From ...
* Select * From ...
* Select attr1, attr2, ... From ...
* Select aggr1(), aggr2(), ... From ...
* Select aggr1(), aggr2(), ... From ... Compare With ...
* Select aggr1(), aggr2(), ... From ... Compare With ... Facet
* Select aggr1(), aggr2(), ... From ... Compare With ... Timeseries
* Select aggr1(), aggr2(), ... From ... Facet ...
* Select aggr1(), aggr2(), ... From ... Facet ... Timeseries
* Select aggr1(), aggr2(), ... From ... Timeseries

Standard aggregate functions are fully supported:

* min
* max
* sum
* average
* latest
* stddev
* percentage
* filter
* count
* rate

Complex aggregate functions fully supported:

* percentiles - denormalized, one percentile per attribute
* histogram - denormalized, one bucket per attribute
* apdex - all 5 attributes (s, f, t, count, score)
* funnel - denormalized, one step per attribute

The interface will use alias to name the output attributes whenever they are defined.

# Setup #

## Python 3 Virtual Environment ##

This repository is written in Python3. Install the proper Python3 package for your OS, fork, clone this repo and setup a Python3 virtual environment:

`cd ~`

`git clone https://github.com/ThyWoof/insights-cli`

`cd ~/insights-cli`

`pip install virtualenv`

`virtualenv env -pPython3`

`. env/bin/activate`

`pip install -r requirements.txt`

## Google Service Account ##

This command line client allows the output to be written to Google Sheets. A Google Service Account is required to use this option. To use a service account JSON file to access Google Drive, you need to first create a service account in Google API Console, then download the service account JSON file by completing the following steps using Google Chrome.

Before you begin:

1. A Google account has already been signed up for using Google Drive.
2. In Google API Console, your project has been created, the Google Drive API has been enabled, and the product name has been set. For more information about how to make these configuration, see [How to access Google Drive using client ID and secret](https://help.talend.com/reader/E3i03eb7IpvsigwC58fxQg/uEUUsDd_MSx64yoJgSa1xg?section=t-access_google_drive_using_client_id_and_secret).

Procedure:

1. Go to [Google API Console](https://console.developers.google.com/).
2. Open the [Service accounts page](https://console.developers.google.com/permissions/serviceaccounts). If prompted, select your project.
3. Click CREATE SERVICE ACCOUNT.
4. In the Create service account window, type a name for the service account, select Furnish a new private key and then the key type JSON.
5. Click Create. In the pop-up window, choose a folder and click Save to store your service account JSON file securely. This JSON file can then be used by Google Drive components and metadata wizard to access Google Drive via the OAuth method Service Account.

# Command Line Syntax #

## AdHoc Query Mode ##

The query command allows a single NRQL statement to be executed:

```
python insights-cli.py query
  -k <QUERY_API_KEY>
  -a <ACCOUNT_ID>
  -q <NRQL_QUERY>
```

## Batch Mode ##

The batch mode offers a very powerful option to automate data extraction from 1 or more New Relic Insights accounts. There are 3 batch modes available:

* batch-local, exports de results to local CSV files
* batch-google, exports the results to Google Sheets and optionally creates Pivot Tables
* batch-insights, exports the results back to an Insights custom event

All batch modes require an account list CSV input file and a YAML queries definition file.

*accounts.csv*


*queries.yaml*
 
### Local ###

```
insights-cli.py batch-local 
    [-h] 
    [-v VAULT_FILE] 
    -q QUERY_FILE 
    -a ACCOUNT_FILE 
    -o OUTPUT_FOLDER
    [-m MASTER_NAMES [MASTER_NAMES ...]]

optional arguments:
  -v VAULT_FILE, --vault-file VAULT_FILE
                        Local YAML vault file
                        [secret:{account_id,query_api_key}]
  -q QUERY_FILE, --query-file QUERY_FILE
                        Local YAML queries file [{name,nrql}]
  -a ACCOUNT_FILE, --account-file ACCOUNT_FILE
                        Local accounts list CSV file
                        [master_name,account_id,account_name,query_api_key]
  -o OUTPUT_FOLDER, --output-folder OUTPUT_FOLDER
                        Local output folder name
  -m MASTER_NAMES [MASTER_NAMES ...], --master-names MASTER_NAMES [MASTER_NAMES ...]
                        Filter master names from account list
```

### Google Sheets ###

```
insights-cli.py batch-google
    [-h]
    [-v VAULT_FILE]
    -q QUERY_FILE
    -a ACCOUNT_FILE_ID
    -o OUTPUT_FOLDER_ID
    -s SECRET_FILE 
    [-p PIVOT_FILE]
    [-m MASTER_NAMES [MASTER_NAMES ...]]

optional arguments:
  -v VAULT_FILE, --vault-file VAULT_FILE
                        Local YAML vault file
                        [secret:{account_id,query_api_key}]
  -q QUERY_FILE, --query-file QUERY_FILE
                        Local YAML queries file [{name,nrql}]
  -a ACCOUNT_FILE_ID, --account-file-id ACCOUNT_FILE_ID
                        Google accounts list Sheets id
                        [master_name,account_id,account_name,query_api_key]
  -o OUTPUT_FOLDER_ID, --output-folder-id OUTPUT_FOLDER_ID
                        Google Drive output Folder id
  -s SECRET_FILE, --secret-file SECRET_FILE
                        Google API secret file
  -p PIVOT_FILE, --pivot-file PIVOT_FILE
                        Local YAML pivot tables file
  -m MASTER_NAMES [MASTER_NAMES ...], --master-names MASTER_NAMES [MASTER_NAMES ...]
                        Filter master names from account list
```

### Insights ###

```
insights-cli.py batch-insights
    [-h]
    [-v VAULT_FILE]
    -q QUERY_FILE
    -a ACCOUNT_FILE
    -i INSERT_ACCOUNT_ID
    -k INSERT_API_KEY
    [-m MASTER_NAMES [MASTER_NAMES ...]]

optional arguments:
  -v VAULT_FILE, --vault-file VAULT_FILE
                        Local YAML vault file
                        [secret:{account_id,query_api_key}]
  -q QUERY_FILE, --query-file QUERY_FILE
                        Local YAML queries file [{name,nrql}]
  -a ACCOUNT_FILE, --account-file ACCOUNT_FILE
                        Local accounts list CSV file
                        [master_name,account_id,account_name,query_api_key]
  -i INSERT_ACCOUNT_ID, --insert-account-id INSERT_ACCOUNT_ID
                        New Relic Insights insert account id
  -k INSERT_API_KEY, --insert-api-key INSERT_API_KEY
                        New Relic Insights insert API key
  -m MASTER_NAMES [MASTER_NAMES ...], --master-names MASTER_NAMES [MASTER_NAMES ...]
                        Filter master names from account list
```

## Batch Mode Configuration Files ##

### Queries ###

### Vault ###
