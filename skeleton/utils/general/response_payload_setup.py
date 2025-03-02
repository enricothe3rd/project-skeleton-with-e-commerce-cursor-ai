import datetime
from skeleton.utils.general.general import ParseValues
from skeleton.utils.general.response_builder import ResponseBuilder


class BuildEmployeeShiftGenerated:
    def __init__(self, raw_data):
        self.parser = ParseValues
        self.builder = ResponseBuilder
        self.data = raw_data

    def execute(self):
        data = self.data
        final = []

        for values in data:
            values['date_from'] = self.parser(values['date_from']).parse_date_to_string()
            values['date_to'] = self.parser(values['date_to']).parse_date_to_string()

            final.append(values)

        return final


class BuildEmployeeShift:
    def __init__(self, raw_data):
        self.parser = ParseValues
        self.builder = ResponseBuilder
        self.data = raw_data

    def execute(self):
        data = self.data
        final = []

        for values in data:
            date = self.parser([values['datetime_from'], values['datetime_to']]).parse_datetime_to_string()
            values['datetime_from'] = date[0]
            values['datetime_to'] = date[1]

            values['generate_shift_date_from'] = self.parser(values['generate_shift_date_from']).parse_date_to_string()
            values['generate_shift_date_to'] = self.parser(values['generate_shift_date_to']).parse_date_to_string()

            values['employee_full_name'] = "{}, {} {} {} {}".format(
                values['employee_last_name'],
                values['employee_first_name'],
                values['employee_middle_name'],
                values['employee_suffix'],
                values['employee_professional_extensions']
            )
            values['created_by_full_name'] = "{}, {} {} {} {}".format(
                values['created_by_last_name'],
                values['created_by_first_name'],
                values['created_by_middle_name'],
                values['created_by_suffix'],
                values['created_by_professional_extensions']
            )

            final.append(values)

        return final


class BuildPositions:
    def __init__(self, raw_data):
        self.parser = ParseValues
        self.builder = ResponseBuilder
        self.data = raw_data

    def execute_list(self):
        final = []
        for position in self.data:
            if position["last_name"] is not None:
                position["full_name"] = "{}, {} {} {} {}".format(
                    position["last_name"],
                    position["first_name"],
                    position["middle_name"],
                    position["suffix"],
                    position["professional_extensions"]
                )
            final.append(position)
        return final

    def execute_header(self):
        return self.data[0]

    def execute_lines(self):
        return self.data


class BuildDepartments:
    def __init__(self, raw_data):
        self.parser = ParseValues
        self.builder = ResponseBuilder
        self.data = raw_data

    def execute_list(self):
        final = []
        for department in self.data:
            if department["last_name"] is not None:
                department["full_name"] = "{}, {} {} {} {}".format(
                    department["last_name"],
                    department["first_name"],
                    department["middle_name"],
                    department["suffix"],
                    department["professional_extensions"]
                )
            final.append(department)
        return final


class BuildTeams:
    def __init__(self, raw_data):
        self.parser = ParseValues
        self.builder = ResponseBuilder
        self.data = raw_data

    def execute_list(self):
        final = []
        for team in self.data:
            if team["last_name"] is not None:
                team["full_name"] = "{}, {} {} {} {}".format(
                    team["last_name"],
                    team["first_name"],
                    team["middle_name"],
                    team["suffix"],
                    team["professional_extensions"]
                )
            else:
                team["full_name"] = ""
            final.append(team)
        return final


class BuildHolidays:
    def __init__(self, raw_data):
        self.parser = ParseValues
        self.builder = ResponseBuilder
        self.data = raw_data

    def execute_list(self):
        final = []
        for holiday in self.data:
            holiday["date"] = self.parser(holiday["date"]).parse_date_to_string()
            final.append(holiday)
        return final


class BuildUsers:
    def __init__(self, raw_data):
        self.parser = ParseValues
        self.builder = ResponseBuilder
        self.data = raw_data

    def execute_list(self):
        data = self.data
        final = []
        for values in data:
            values["full_name"] = "{}, {} {}".format(
                values["last_name"], values["first_name"], values["middle_name"]
            )
            final.append(values)
        return final
