import datetime
from skeleton.utils.general.general import ParseValues, execute_response_build
from skeleton.utils.general.response_builder import ResponseBuilder


class BuildEmployeeResponse:
    def __init__(self, raw_data):
        self.parser = ParseValues
        self.builder = ResponseBuilder
        self.data = raw_data

    def execute(self):
        build = self.builder(self.data)

        response_body_payload = {
            "detail":
                execute_response_build(self.data['details'], build.detail),
            "contract":
                execute_response_build(self.data['contract'], build.contract),
            "banks":
                execute_response_build(self.data['banks'], build.banks),
            "addresses":
                execute_response_build(self.data['addresses'], build.addresses),
            "positions":
                execute_response_build(self.data['positions'], build.positions),
            "leaves":
                execute_response_build(self.data['leaves'], build.leaves),
            "allowances":
                execute_response_build(self.data['allowances'], build.allowances),
            "deductions":
            # execute_response_build(self.data['deductions_headers'], build.deductions),
                execute_response_build(self.data['deductions'], build.deductions),
            "schedules":
                execute_response_build(self.data['schedules_headers'], build.schedules),
            "previous_employer":
                execute_response_build(self.data['previous_employer'], build.previous_employer),
        }

        final = {
            "status": True,
            "message": "Success",
            "payload": response_body_payload
        }

        return final

    # CALLED BY READ EMPLOYEES LIST
    def build_employee_detail(self):
        data = self.data
        final = []

        for values in data:
            values['birthday'] = self.parser(values['birthday']).parse_date_to_string()
            values['full_name'] = ("{0}, {1} {2}"
                                   .format(values['last_name'], values['first_name'], values['middle_name'])
                                   )
            values["date_create"] = self.parser(values['date_create']).parse_date_to_string()
            final.append(values)

        return final


class BuildAttendancesResponse:
    def __init__(self, raw_data):
        self.parser = ParseValues
        self.builder = ResponseBuilder
        self.data = raw_data

    def build_attendances_detail(self):
        data = self.data
        final = []

        for values in data:
            time = self.parser([values['time_in'], values['time_out']]).parse_datetime_to_string()
            correction = self.parser([values['correct_time_in'], values['correct_time_out']]).parse_datetime_to_string()
            overtime = self.parser([values['ot_from'], values['ot_to']]).parse_datetime_to_string()

            values['time_duration'] = self.parser([
                values['time_out'], values['time_in']
            ]).subtract_datetime_to_hours()

            values['correction_duration'] = self.parser([
                values['correct_time_out'], values['correct_time_in']
            ]).subtract_datetime_to_hours()

            values['ot_duration'] = self.parser([
                values['ot_to'], values['ot_from']
            ]).subtract_datetime_to_hours()

            values['time_in'] = time[0]
            values['time_out'] = time[1]

            values['valid_time_in'] = time[0]
            values['valid_time_out'] = time[1]

            if values['correction_approval_status'] == "APPROVED":
                values['valid_time_in'] = correction[0]
                values['valid_time_out'] = correction[1]
                values['time_duration'] = self.parser([
                    values['correct_time_out'], values['correct_time_in']
                ]).subtract_datetime_to_hours()

            values['correct_time_in'] = correction[0]
            values['correct_time_out'] = correction[1]

            values['ot_from'] = overtime[0]
            values['ot_to'] = overtime[1]

            values['time_in_out'] = "{} - {}".format(time[0], time[1])
            values['correction_in_out'] = "{} - {}".format(correction[0], correction[1])
            values['ot_from_to'] = "{} - {}".format(overtime[0], overtime[1])

            values['employee_full_name'] = (
                "{0}, {1} {2}"
                .format(
                    values['employee_last_name'],
                    values['employee_first_name'],
                    values['employee_middle_name'])
                )

            final.append(values)

        return final


class BuildLeaveApplicationResponse:
    def __init__(self, raw_data):
        self.parser = ParseValues
        self.data = raw_data

    def execute(self):
        data = self.data
        final = []

        for value in data:
            value['date'] = self.parser(value['date']).parse_date_to_string()

            value['employee_full_name'] = "{} {}, {} {} {}".format(
                value['employee_first_name'],
                value['employee_middle_name'],
                value['employee_last_name'],
                value['employee_suffix'],
                value['employee_professional_extensions'],
            )
            value['approver_full_name'] = "{} {}, {} {} {}".format(
                value['approver_first_name'],
                value['approver_middle_name'],
                value['approver_last_name'],
                value['approver_suffix'],
                value['approver_professional_extensions'],
            )

            final.append(value)

        return final


class BuildLeaveCreditsResponse:
    def __init__(self, raw_data):
        self.parser = ParseValues
        self.data = raw_data

    def execute(self):
        data = self.data
        final = []

        for value in data:
            value['employee_full_name'] = "{} {}, {} {} {}".format(
                value['employee_first_name'],
                value['employee_middle_name'],
                value['employee_last_name'],
                value['employee_suffix'],
                value['employee_professional_extensions'],
            )

            final.append(value)

        return final


class BuildPayrollReleaseDataResponse:
    def __init__(self, raw_data):
        self.parser = ParseValues
        self.data = raw_data

    def build_list(self):
        data = self.data
        final = []

        for value in data:
            value["date"] = self.parser(value["date"]).parse_date_to_string()
            value["cutoff_date_from"] = self.parser(value["cutoff_date_from"]).parse_date_to_string()
            value["cutoff_date_to"] = self.parser(value["cutoff_date_to"]).parse_date_to_string()
            final.append(value)

        return final

    def build_one(self):
        data = self.data
        data["id"] = data["release_id"]
        data["date"] = self.parser(data["date"]).parse_date_to_string()
        data["cutoff_date_from"] = self.parser(data["cutoff_date_from"]).parse_date_to_string()
        data["cutoff_date_to"] = self.parser(data["cutoff_date_to"]).parse_date_to_string()
        return data

    def employee_build_list(self):
        data = self.data
        final = []
        for value in data:
            value["date"] = self.parser(value["date"]).parse_date_to_string()
            value["cutoff_date_from"] = self.parser(value["cutoff_date_from"]).parse_date_to_string()
            value["cutoff_date_to"] = self.parser(value["cutoff_date_to"]).parse_date_to_string()
            value["employee_full_name"] = "{}, {} {} {} {}".format(
                value["last_name"],
                value["first_name"],
                value["middle_name"],
                value["suffix"],
                value["professional_extensions"]
            )
            final.append(value)
        return final

    def employee_build_one(self):
        data = self.data
        parser = self.parser
        data["employee_full_name"] = "{}, {} {} {} {}".format(
            data["last_name"],
            data["first_name"],
            data["middle_name"],
            data["suffix"],
            data["professional_extensions"]
        )
        data["release_date"] = parser(data["release_date"]).parse_date_to_string()
        data["cutoff_date_from"] = parser(data["cutoff_date_from"]).parse_date_to_string()
        data["cutoff_date_to"] = parser(data["cutoff_date_to"]).parse_date_to_string()
        return data

    def employee_attendance_one(self):
        data = self.data
        final = []
        for value in data:
            date_values = self.parser([
                value["time_in"],
                value["time_out"],
                value["correct_time_in"],
                value["correct_time_out"],
                value["ot_from"],
                value["ot_to"],
            ]).parse_datetime_to_string()
            value["time_in"] = date_values[0]
            value["time_out"] = date_values[1]
            value["correct_time_in"] = date_values[2]
            value["correct_time_out"] = date_values[3]
            value["ot_from"] = date_values[4]
            value["ot_to"] = date_values[5]
            final.append(value)
        return final


class BuildBadgeNo:
    def __init__(self, raw_data):
        self.parser = ParseValues
        self.data = raw_data

    def badge_num(self):
        year = self.data[0]
        count = self.data[1] + 1
        return "{}-{:04}".format(year, count)


class BuildOtherDeductions:
    def __init__(self, raw_data):
        self.parser = ParseValues
        self.data = raw_data

    def build_list(self):
        final = []
        for data in self.data:
            data["date_from"] = self.parser(data["date_from"]).parse_date_to_string()
            data["date_to"] = self.parser(data["date_to"]).parse_date_to_string()
            final.append(data)
        return final


class BuildTaxPayments:
    def __init__(self, raw_data):
        self.parser = ParseValues
        self.data = raw_data

    def build(self):
        final = []
        for data in self.data:
            data["date"] = self.parser(data["date"]).parse_date_to_string()
            final.append(data)
        return final
