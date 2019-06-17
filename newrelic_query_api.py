#
# author: Paulo Monteiro
# version: 0.1
#

import json
import os
import re
import requests

SP = '_'
APDEX_FUNCTION_METRICS = ['count', 's', 't', 'f', 'score']
MAX_RETRIES = 5

def msg(message, *args, stop=True, **kwargs):
    """lazy man log"""
    print(message.format(*args))
    if stop:
        exit(1)


def to_datetime(timestamp):
    """converts a timestamp to a Sheets / Excel datetime"""
    EPOCH_START = 25569 # 1970-01-01 00:00:00
    SECONDS_IN_A_DAY = 86400
    return timestamp / SECONDS_IN_A_DAY + EPOCH_START


def get_results_header(contents, results):
    """extracts results header from the contents attribute"""
    header = []
    for content in contents:
        try:
            alias = content['alias']
            content = content['contents']
        except:
            alias = ''
        function = content['function']
        attribute = content.get('attribute', '')
        name = alias if alias else function + SP + attribute if attribute else function

        if function == 'funnel':
            for step in content['steps']:
                header.append(name + SP + str(step.replace(' ', SP)))

        elif function == 'percentile':
            for threshold in content['thresholds']:
                header.append(name + SP + str(threshold))

        elif function == 'rate':
            if not alias:
                of = content['of']
                name = name + SP + of['function'] + SP + of['attribute']
            header.append(name)

        elif function == 'histogram':
            start = content['start']
            size = content['bucketSize']
            for i in range(0, content['bucketCount']):
                end = start + size
                bucket = '%05.2f' % start + SP + '%05.2f' % end
                header.append(name + SP + bucket)
                start = end

        elif function == 'apdex':
            for metric in APDEX_FUNCTION_METRICS:
                header.append(name + SP + metric)

        elif function == 'events':
            for result in results:
                for event in result['events']:
                    for key in event:
                        if not key in header:
                            header.append(key)

        elif function == 'eventTypes':
            for result in results:
                for event in result['eventTypes']:
                    if not event in header:
                        header.append(event)

        elif function == 'keyset':
            for result in results:
                for event in result['allKeys']:
                    if not event in header:
                        header.append(event)

        else:
            header.append(name)

    return header


def get_facets_values(facet, header):
    """extracts facets values from the contents attribute"""
    values = {}
    if type(facet) is str:
        values.update({header[0]: facet})
    elif type(facet) is list:
        values.update({k:v for k,v in zip(header, facet)})

    return values


def get_results_values(results, header, include={}, offset=0):
    """extracts results values from the contents attribute"""
    values = {k:v for k,v in include.items()}
    index = 0
    for result in results:
        if 'percentiles' in result: # percentiles
            for percentile in result['percentiles'].values():
                values.update({header[offset+index]: percentile})
                index += 1

        elif 'histogram' in result: # histogram
            for histogram in result['histogram']:
                values.update({header[offset+index]: histogram})
                index += 1

        elif 'steps' in result: # funnel
            for step in result['steps']:
                values.update({header[offset+index]: step})
                index += 1

        elif 'eventTypes' in result:
            for event in result['eventTypes']:
                values.update({header[offset+index]: event})
                index += 1

        elif 'allKeys' in result:
            for event in result['allKeys']:
                values.update({header[offset+index]: event})
                index += 1

        elif 'score' in result: # apdex
            for metric in APDEX_FUNCTION_METRICS:
                values.update({header[offset+index]: result[metric]})
                index += 1

        else: # default aggregation
            
            values.update({header[offset+index]: list(result.values())[0]})
            index += 1

    return values


def get_single(results, header, include={}, offset=0):
    """ SELECT aggr1, aggr2, ... FROM ... """
    yield get_results_values(results, header, include, offset)


def get_events(results, header, include={}, offset=0):
    """ SELECT attr1, attr2, ... FROM ... """
    events = results[0]['events']
    for event in events:
        values = {**event, **include}
        row = {k:values.get(k, None) for k in header}
        yield row


def get_facets(results, header, include={}, offset=0):
    """ SELECT aggr1, aggr2, ... FROM ... FACET attr1, attr2, ... """
    for result in results:
        row = {k:v for k,v in include.items()}
        row.update(get_facets_values(result['name'], header[len(include):]))
        row.update(get_results_values(result['results'], header, {}, offset))
        yield row


def get_timeseries(results, header, include={}, offset=0, prefix=''):
    """ SELECT aggr1, aggr2, ... FROM ... TIMESERIES """
    for result in results:
        row = {k:v for k,v in include.items()}
        row.update({
            'datetime' + prefix: to_datetime(int(result['endTimeSeconds'])),
            'timestamp' + prefix: result['endTimeSeconds'],
            'timewindow' + prefix: result['endTimeSeconds'] - result['beginTimeSeconds'],
            'inspectedCount' + prefix: result['inspectedCount']
        })
        row.update(get_results_values(result['results'], header, {}, offset))
        yield row


def get_facets_timeseries(results, header, include={}, offset=0):
    """ SELECT aggr1(), aggr2(), ... FROM ... FACET attr1, attr2, ... TIMESERIES """
    for result in results:
        row = {k:v for k,v in include.items()}
        row.update(get_facets_values(result['name'], header[len(include):]))
        for timeseries in get_timeseries(result['timeSeries'], header, row, offset):
            yield timeseries


def get_compare(results, header, include={}, offset=0):
    """ SELECT aggr1(), aggr2(), ... FROM ... COMPARE WITH ... """
    current = results['current']['results']
    previous = results['previous']['results']
    header_previous = [v if i < offset else v + '_compare' for i,v in enumerate(header)]
    row = {k:v for k,v in include.items()}
    row.update(get_results_values(current, header, {}, offset))
    row.update(get_results_values(previous, header_previous, {}, offset))
    yield row


def get_compare_facets(results, header, include={}, offset=0):
    """ SELECT aggr1(), aggr2(), ... FROM ... COMPARE WITH ... FACET attr1, attr2, ... """
    facets_current = results['current']['facets']
    facets_previous = results['previous']['facets']
    header_previous = [v if i < offset else v + '_compare' for i,v in enumerate(header)]
    facets_curr_prev = zip(
        get_facets(facets_current, header, include, offset),
        get_facets(facets_previous, header_previous, include, offset)
    )
    for curr,prev in facets_curr_prev:
        curr.update(prev)
        yield curr


def get_compare_timeseries(results, header, include={}, offset=0):
    """ SELECT aggr1(), aggr2(), ... FROM ... COMPARE WITH ... TIMESERIES """
    timeseries_current = results['current']['timeSeries']
    timeseries_previous = results['previous']['timeSeries']
    header_previous = [v if i < offset else v + '_compare' for i,v in enumerate(header)]
    timeseries_curr_prev = zip(
        get_timeseries(timeseries_current, header, include, offset),
        get_timeseries(timeseries_previous, header_previous, include, offset, '_compare')
    )
    for curr,prev in timeseries_curr_prev:
        curr.update(prev)
        yield curr


class NewRelicQueryAPI():
    """ interface to New Relic Query API that always returns a list of events

        standard aggregate functions fully supported:
            - min
            - max
            - sum
            - average
            - latest
            - stddev
            - percentage
            - filter
            - count
            - rate

        complex aggregate functions fully supported:
            - percentiles: denormalized, one percentile per attribute
            - histogram: denormalized, one bucket per attribute
            - apdex: all 5 attributes (s, f, t, count, score)
            - funnel: denormalized, one step per attribute

        show event types

        other functions:
            - keyset: stores a list of keys in one single attribute
            - uniques: stores a list of uniques in one single attribute

        all NRQL syntax supported:
            - events lists
            - single values
            - comparisons
                - duplicates all metrics with prefix _compared
                - stores timestamp_compared attribute
            - facets
            - timeseries
            - combinations of all above

        other tidbits:
            - create attribute names from function and attribute metadata
                - or from alias (if present) and attribute
            - timestamp is overwritten with the 'UNTIL TO' one
            - timewindow stores how many seconds in the analysis
                - analysis range is [timestamp - timewindows : timestamp]
    """

    def __init__(self, account_id=0, query_api_key='', logger=msg):
        """init"""
        self.__logger = logger
        if not account_id:
            account_id = os.getenv('NEW_RELIC_ACCOUNT_ID', '')
        if not account_id:
            self.__logger('account id not provided and env NEW_RELIC_ACCOUNT_ID not set')
        if not query_api_key:
            query_api_key = os.getenv('NEW_RELIC_QUERY_API_KEY', '')
        if not query_api_key:
            self.__logger('query api key not provided and env NEW_RELIC_QUERY_API_KEY not set')
        self.__headers = {
            'Accept': 'application/json',
            'X-Query-Key': query_api_key
        }
        self.__url = f'https://insights-api.newrelic.com/v1/accounts/{account_id}/query'

    def __parse_nrql(self, nrql, params):
        """ replace variables in nrql """
        pattern = re.compile(r'\{[a-zA-Z][\w]*}')
        for var in pattern.findall(nrql):
            param = var[1:-1]
            try:
                nrql = nrql.replace(var, str(params[param]))
            except:
                self.__logger(
                    'warning: cannot find {} in parameters dictionary', param, stop=False)
        return nrql

    def query(self, nrql, params={}, max_retries=MAX_RETRIES):
        """request a JSON result from the Insights Query API"""
        parsed_nrql = self.__parse_nrql(nrql, params)
        count_retries = 0
        status_code = 0
        while True:
            try:
                count_retries += 1
                response = requests.get(
                    self.__url, headers=self.__headers, params={'nrql': parsed_nrql})
                status_code = response.status_code
                if status_code == 200:
                    results = response.json()
                    break
                else:
                    self.__logger(
                        'warning: got a {} response fetching {} ({}/{})',
                        status_code, self.__url, count_retries, max_retries, stop=False)
            except requests.RequestException:
                if count_retries >= max_retries:
                    break
            finally:
                if count_retries >= max_retries and status_code != 200:
                    self.__logger(
                        'warning: gave up fetching {} after {} attempts',
                        self.__url, max_retries, stop=False)
                    results = []
                    break

        return results

    def events(self, nrql, include={}, params={}):
        """execute the nrql and convert to an events list"""
        response = self.query(nrql, params=params)
        try:
            metadata = response['metadata']
            contents = metadata['contents']
        except:
            return

        # determine the NRQL structure
        has_compare = 'compareWith' in metadata
        has_facets = 'facet' in metadata or 'facet' in contents
        has_timeseries = 'timeSeries' in metadata or 'timeSeries' in contents
        is_simple = not has_compare and not has_facets and not has_timeseries
        has_events = is_simple and len(contents) and 'order' in contents[0]
        has_single = is_simple and len(contents) and not 'order' in contents[0]

        # get facets attribute names
        if has_facets:
            if has_compare:
                facet = contents['facet']
            else:
                facet = metadata['facet']
        else:
            facet = None

        # normalize the contents list
        if has_timeseries and (has_compare or has_facets):
            contents = contents['timeSeries']['contents']
        elif has_timeseries and not (has_compare or has_facets):
            contents = metadata['timeSeries']['contents']
        elif has_compare and has_facets:
            contents = contents['contents']['contents']
        elif has_compare or has_facets:
            contents = contents['contents']
        else:
            contents = metadata['contents']

        # precalculate timestamps and add here to enforce sort order
        # they get overwritten later on if NRQL has a timeseries clause
        begintime = int(metadata.get('beginTimeMillis', 0) / 1000)
        timestamp = int(metadata.get('endTimeMillis', 0) / 1000)
        timewindow = timestamp - begintime
        compare_delta = int(metadata.get('compareWith', 0) / 1000)
        timestamp_compare = timestamp - compare_delta
        datetime = to_datetime(timestamp)
        datetime_compare = to_datetime(timestamp_compare)
        if not compare_delta:
            meta = {
                'datetime': datetime,
                'timewindow': timewindow,
                'timestamp': timestamp
            }
        else:
            meta = {
                'datetime': datetime,
                'datetime_compare': datetime_compare,
                'timewindow': timewindow,
                'timestamp': timestamp,
                'timestamp_compare': timestamp_compare
            }

        # select the proper parsing function and parameters
        if has_single:
            fetch_data = get_single
            results = response['results']

        elif has_events:
            fetch_data = get_events
            results = response['results']

        elif has_compare:
            if has_facets:
                fetch_data = get_compare_facets
            elif has_timeseries:
                fetch_data = get_compare_timeseries
            else:
                fetch_data = get_compare
            results = {k:response[k] for k in ['current', 'previous']}

        elif has_facets:
            if has_timeseries:
                fetch_data = get_facets_timeseries
            else:
                fetch_data = get_facets
            results = response['facets']

        elif has_timeseries:
            fetch_data = get_timeseries
            results = response['timeSeries']

        else:
            results = []

        # build the header and meta dictionary
        meta, _meta = {}, meta
        header = []
        for k,v in include.items():
            header.append(k)
            meta[k] = v
        for k,v in _meta.items():
            header.append(k)
            meta[k] = v
        offset = len(header)
        if type(facet) is list:
            header.extend(facet)
            offset += len(facet)
        elif type(facet) is str:
            header.append(facet)
            offset += 1
        header.extend(get_results_header(contents, results))

        # parse the result JSON and yield events
        for event in fetch_data(results, header, meta, offset):
            yield event

# run all test cases
if __name__ == "__main__":
    import sys, yaml
    with open('queries-samples.yaml') as f:
        queries = yaml.load(f, Loader=yaml.FullLoader)
    api = NewRelicQueryAPI()
    for query in queries:
        if len(sys.argv) == 1 or query['name'] in sys.argv:
            include = {'eventType': query['name']}
            params = {'some_since': '1 day ago', 'some_compare': '2 days ago', 'some_limit': 1}
            for event in api.events(query['nrql'], include=include, params=params):
                print(json.dumps(event, sort_keys=False, indent=4))