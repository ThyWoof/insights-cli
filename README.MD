# Introduction #

This repository tries to simplify the consumption of New Relic events gathered from the Insights Query API. Although the Insights API is very simple to use the challenge resides on getting a consistent result set. The returned payload can have different structures depending on the NRQL issued. This isn't a problem for quick adhoc requests but can become difficult to handle if we don't provide a well-known interface to the results.

# NRQL Use Cases #

This interface will always return a list of dictionaries from the returned payload. Check the [Insights New Relic Reference](https://docs.newrelic.com/docs/insights/nrql-new-relic-query-language/nrql-reference/nrql-syntax-components-functions) if you need to refresh your NRQL knowledge.

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

## Batch Mode ##

### Local ###

### Google Sheets ###

### Insights ###

## Batch Mode Configuration Files ##

### Queries ###

### Vault ###

