import json


def convert_to_fixtures(rows):
    rows = prepare_data(iter(rows))
    return list(fixture(rows))


def prepare_data(rows):
    rows = discard_preamble(rows)
    rows = strip_trailing_columns(rows)
    rows = strip_whitespace(rows)
    rows = skip_empty(rows)
    return rows


def strip_trailing_columns(rows):
    for row in rows:
        yield row[:3]


def strip_whitespace(rows):
    for row in rows:
        group, name, code = row
        yield (group.strip(), name.strip(), code.strip())


def discard_preamble(rows):
    """
    Discard the first few rows of the CSV data, which provide some explanatory
    text and the column headers.
    """
    for i in range(6):
        next(rows)
    return rows


def skip_empty(rows):
    for row in rows:
        _, name, code = row
        if name and code:
            yield row


def fixture(rows):
    """
    Generate the fixture data structure for each row, extracting group
    fixtures as we go
    """
    group_index = 0
    for index, row in enumerate(rows, start=1):
        group, name, code = row
        if group:
            group_index += 1
            yield group_fixture(group_index, group)
        yield code_fixture(index, (group_index, name, code))


def group_fixture(index, name):
    return {
        'model': 'legalaid.MediaCodeGroup',
        'pk': index,
        'fields': {
            'name': name
        }
    }


def code_fixture(index, row):
    group, name, code = row
    return {
        'model': 'legalaid.MediaCode',
        'pk': index,
        'fields': {
            'group': group,
            'name': name,
            'code': code
        }
    }


class MediaCodeList(object):

    def __init__(self, csv_data):
        self.csv_data = list(csv_data)

    def as_json(self):
        fixtures = convert_to_fixtures(self.csv_data)
        return json.dumps(fixtures, indent=2)
