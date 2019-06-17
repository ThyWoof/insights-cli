#
# author: Paulo Monteiro
# version: 0.1
#

SHEET1_SHEET_ID=0
SHEET_DEFAULT_COLUMNS=26
SHEET_DEFAULT_ROWS=1000

def cell_snippet(x, is_date=False):
    """create the proper cell snippet depending on the value type"""
    if type(x) == int:
        return {
            'userEnteredValue': {'numberValue': x},
            'userEnteredFormat': {
                'numberFormat': {
                    'type': 'NUMBER',
                    'pattern': '#,##0'
                }
            }
        }
    elif type(x) == float:
       return {
           'userEnteredValue': {'numberValue': x},
           'userEnteredFormat': {
               'numberFormat': {
                    'type': 'DATE' if is_date else 'NUMBER',
                    'pattern': 'yyyy/mm/dd hh:mm:ss' if is_date else '#,##0.00'
               }
           }
       }
    else:
        return {
            'userEnteredValue': {'stringValue': x}
        }


def pivot_table_snippet(sheet_id, pivot, headers):
    """create a pivotTable snippet from a pivot dict and headers list"""
    try:
        rows = pivot['rows'].items()
    except:
        rows = {}
    try:
        columns = pivot['columns'].items()
    except:
        columns = {}
    try:
        values = pivot['values'].items()
    except:
        values = {}
    return {
        'source': {'sheetId': sheet_id},
        'rows': [{
            'sourceColumnOffset': headers.index(field),
            'showTotals': True if not attr else attr.get('showTotals', True),
            'sortOrder': 'ASCENDING' if not attr else attr.get('sortOrder', 'ASCENDING'),
        } for field,attr in rows],
        'columns': [{
            'sourceColumnOffset': headers.index(field),
            'showTotals': True if not attr else attr.get('showTotals', True),
            'sortOrder': 'ASCENDING' if not attr else attr.get('sortOrder', 'ASCENDING'),
        } for field,attr in columns],
        'values': [{
            'sourceColumnOffset': headers.index(field),
            'summarizeFunction': attr
        } for field,attr in values],
        'valueLayout': pivot.get('valueLayout', 'HORIZONTAL')
    }


def add_sheet_request(title):
    return {
        'addSheet': {
            'properties': {
                'title': title
            }
        }
    }


def delete_sheet_request(sheet_id):
    return {
        'deleteSheet': {
            'sheetId': sheet_id
        }
    }


def append_dimension_request(sheet_id, dimension, length):
    return {
        'appendDimension': {
            'sheetId': sheet_id,
            'dimension': dimension,
            'length': length
        }
    }


def delete_dimension_request(sheet_id, dimension, start_index=0, end_index=1):
    return {
        'deleteDimension': {
            'range': {
                'sheetId': sheet_id,
                'dimension': dimension,
                'startIndex': start_index,
                'endIndex': end_index
            }
        }
    }


def append_cells_request(sheet_id, rows):
    return {
        'appendCells': {
            'sheetId': sheet_id,
            'rows': rows,
            'fields': '*',
        }
    }


def pivot_request(pivot_sheet_id, pivot_table):
    return {
        'updateCells': {
            'rows': [
                {
                    'values': [
                        {
                            'pivotTable': pivot_table
                        }
                    ]
                }
            ],
            'start': {
                'sheetId': pivot_sheet_id
            },
            'fields': 'pivotTable'
        }
    }


def basic_filter_request(sheet_id):
    return {
        'setBasicFilter': {
            'filter': {
                'range': {
                    'sheetId': sheet_id
                }
            }
        }
    }


def format_header_request(sheet_id):
    return {
        'repeatCell': {
            'range': {
            'sheetId': sheet_id,
            'startRowIndex': 0,
            'endRowIndex': 1
            },
            'cell': {
                'userEnteredFormat': {
                    'horizontalAlignment' : 'CENTER',
                    'textFormat': {
                        'bold': True
                    }
                }
            },
            'fields': 'userEnteredFormat(textFormat,horizontalAlignment)'
        }
    }


def freeze_rows_request(sheet_id, frozen_row_count=1):
    return {
        'updateSheetProperties': {
            'properties': {
                'sheetId': sheet_id,
                'gridProperties': {
                    'frozenRowCount': frozen_row_count
                }
            },
            'fields': 'gridProperties.frozenRowCount'
        }
    }


def freeze_columns_request(sheet_id, frozen_column_count=1):
    return {
        'updateSheetProperties': {
            'properties': {
                'sheetId': sheet_id,
                'gridProperties': {
                    'frozenColumnCount': frozen_column_count
                }
            },
            'fields': 'gridProperties.frozenColumnCount'
        }
    }


def auto_resize_dimension_request(sheet_id, dimension='COLUMNS'):
    return {
        'autoResizeDimensions': {
            'dimensions': {
                'sheetId': sheet_id,
                'dimension': dimension
            }
        }
    }