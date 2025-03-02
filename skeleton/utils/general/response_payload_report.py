import datetime
from skeleton.utils.general.general import ParseValues


class BuildPayrollReport:
    def __init__(self, raw_data):
        self.parser = ParseValues
        self.data = raw_data

    def build_query_response(self):
        data = self.data
        final = []

        for values in data:
            values['date'] = self.parser(values['date']).parse_date_to_string()

            final.append(values)

        return final

