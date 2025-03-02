import datetime
from skeleton.utils.general.general import ParseValues


class ResponseBuilder:
    def __init__(self, data):
        self.data = data
        self.parser = ParseValues

    def detail(self):
        data = self.data['details'][0]
        data['birthday'] = self.parser(data['birthday']).parse_date_to_string()

        # DETAILS CONTAINS ONE RECORD ONLY
        return data

    def contract(self):
        data = self.data['contract'][0]
        data['date_start'] = self.parser(data['date_start']).parse_date_to_string()
        data['date_end'] = self.parser(data['date_end']).parse_date_to_string()

        # CONTRACT CONTAINS ONE RECORD ONLY
        return data

    def banks(self):
        return self.data['banks']

    def addresses(self):
        return self.data['addresses']

    def positions(self):
        return self.data['positions']

    def leaves(self):
        return self.data['leaves']

    def allowances(self):
        data = self.data['allowances']
        processed = []

        for value in data:
            value['date_from'] = self.parser(value['date_from']).parse_date_to_string()
            value['date_to'] = self.parser(value['date_to']).parse_date_to_string()

            processed.append(value)

        return processed

    def deductions(self):
        return self.data['deductions']

    def previous_employer(self):
        data = self.data['previous_employer'][0]
        data['employed_from'] = self.parser(data['employed_from']).parse_date_to_string()
        data['employed_to'] = self.parser(data['employed_to']).parse_date_to_string()

        return data

    # def deductions(self):
    #     header_raw = self.data['deductions_headers']
    #     lines_raw = self.data['deductions_lines']
    #     values = []
    #
    #     for head_val in header_raw:
    #         lines = []
    #
    #         header = {
    #             "id": head_val['id'],
    #             "name": head_val['name'],
    #             "is_mandatory": head_val['is_mandatory'],
    #             "date_from": self.parser(head_val['date_from']).parse_date_to_string(),
    #             "date_to": self.parser(head_val['date_to']).parse_date_to_string(),
    #             "category_id": head_val['category_id'],
    #             "category_name": head_val['category_name'],
    #             "employee_id": head_val['employee_id'],
    #         }
    #
    #         for lines_val in lines_raw:
    #             if lines_val['id'] == head_val['id']:
    #                 lines.append({
    #                     "id": lines_val['line_id'],
    #                     "deduction_type": lines_val['deduction_type'],
    #                     "fixed_amount": lines_val['fixed_amount'],
    #                     "employee_share": lines_val['employee_share'],
    #                     "salary_from": lines_val['salary_from'],
    #                     "salary_to": lines_val['salary_to'],
    #                     "percentage_amount": lines_val['percentage_amount'],
    #                 })
    #         values.append({
    #             "header": header,
    #             "lines": lines
    #         })
    #
    #     return values

    def schedules(self):
        # header_raw = self.data['schedules_headers'][0]
        header = self.data['schedules_headers'][0]
        lines_raw = self.data['schedules_lines']

        # for header_val in header_raw:
        lines = []

        header = {
            "id": header['id'],
            "name": header['name'],
            "date_from": self.parser(header['date_from']).parse_date_to_string(),
            "date_to": self.parser(header['date_to']).parse_date_to_string(),
            "is_flexi": header['is_flexi'],
            "is_manual_scheduled": header['is_manual_scheduled'],
            "employee_id": header['employee_id'],
        }

        for lines_val in lines_raw:
            if header['id'] == lines_val['id']:
                lines.append({
                    "id": lines_val['line_id'],
                    "day": lines_val['day'],
                    "time_from": self.parser(lines_val['time_from']).parse_time_to_string(),
                    "time_to": self.parser(lines_val['time_to']).parse_time_to_string(),
                    "is_carried": lines_val['is_carried'],
                    "duration": lines_val['duration'],
                })

        values = {
            "header": header,
            "lines": lines
        }

        return values

    def attendance_kiosk(self):
        data = self.data
        datetime_val = self.parser([data["time_in"], data["time_out"]]).parse_datetime_to_string()
        data["time_in"] = datetime_val[0]
        data["time_out"] = datetime_val[1]

        return data

    def attendance_crud(self):
        data = self.data[0]
        datetime_val = self.parser([
            data["time_in"],
            data["time_out"],
            data["correct_time_in"],
            data["correct_time_out"],
            data["ot_from"],
            data["ot_to"]
        ]).parse_datetime_to_string()

        data["time_in"] = datetime_val[0]
        data["time_out"] = datetime_val[1]

        return data


class BuildCheckBadgeNo:
    def __init__(self, data):
        self.data = data

    def badge_no_data(self):
        employee_data = self.data

        employee_data[0]['full_name'] = "{} {} {} {}, {}".format(
            employee_data[0]['first_name'],
            employee_data[0]['middle_name'],
            employee_data[0]['last_name'],
            employee_data[0]['suffix'],
            employee_data[0]['professional_extensions']
        )

        return employee_data


class BuildShiftGenerate:
    def __init__(self, data):
        self.data = data
        self.parser = ParseValues

    def validate(self):
        shift_generate_data = self.data
        final = []

        for values in shift_generate_data:
            values['date_from'] = self.parser(values['date_from']).parse_date_to_string()
            values['date_to'] = self.parser(values['date_to']).parse_date_to_string()

            final.append(values)

        return final


class BuildShiftGenerateSuggestValue:
    def __init__(self, data):
        self.data = data
        self.parser = ParseValues

    def execute(self):
        shift_generate_data = self.data
        final = []

        for values in shift_generate_data:
            values['date_next'] = self.parser(values['date_to'] + datetime.timedelta(days=15)).parse_date_to_string()
            values['date_to'] = self.parser(values['date_to'] + datetime.timedelta(days=1)).parse_date_to_string()
            final.append(values)

        return final


# ADD SCENARIO FOR FLEXI EMPLOYEES
class BuildValidOTValues:
    def __init__(self, **data):
        self.data = data
        self.parser = ParseValues

    def execute(self):
        final = {
            "valid_ot_in": "",
            "valid_ot_out": "",
            "ot_type": "Extended work hours",
            "is_qualified": True,
            "message": ""
        }
        config = self.data["config"]
        attendance = self.data["attendance"]
        break_before_ot = config["break_before_ot_minutes"] / 60
        time_in = attendance["time_in"]
        time_out = attendance["time_out"]
        if attendance["ot_approval_status"] == "PENDING" and attendance["ot_from"] is not None:
            final["valid_ot_in"] = self.parser([attendance["ot_from"]]).parse_datetime_to_string()[0]
            final["valid_ot_out"] = self.parser([attendance["ot_to"]]).parse_datetime_to_string()[0]
            final["is_qualified"] = True
            final["message"] = "Pending overtime application"
        elif attendance["ot_approval_status"] == "APPROVED":
            final["valid_ot_in"] = self.parser([attendance["ot_from"]]).parse_datetime_to_string()[0]
            final["valid_ot_out"] = self.parser([attendance["ot_to"]]).parse_datetime_to_string()[0]
            final["is_qualified"] = False
            final["message"] = "Overtime Application is already approved."
        else:
            if attendance["correction_approval_status"] == "APPROVED":
                time_in = attendance["correct_time_in"]
                time_out = attendance["correct_time_out"]
            if len(self.data["shift"]) > 0:
                shift = self.data["shift"][0]
                tardiness = self.parser([shift['datetime_from'], time_in]).subtract_datetime_to_minutes()
                undertime = self.parser([time_out, shift['datetime_to']]).subtract_datetime_to_minutes()
                if tardiness < 0 and abs(tardiness) > config['grace_time']:
                    final["is_qualified"] = False
                    final["message"] = "Employee is late."
                elif undertime < 0:
                    final["is_qualified"] = False
                    final["message"] = "Employee is undertime"
                else:
                    test_overtime = self.parser([
                        time_out,
                        shift["datetime_to"] + datetime.timedelta(hours=break_before_ot)
                    ]).subtract_datetime_to_hours()
                    if test_overtime < break_before_ot:
                        final["is_qualified"] = False
                        final["message"] = "Insufficient overtime hours"
                    else:
                        final["valid_ot_in"] = self.parser([
                            shift["datetime_to"] + datetime.timedelta(hours=break_before_ot)
                        ]).parse_datetime_to_string()[0]
                        final["valid_ot_out"] = self.parser([
                            time_out
                        ]).parse_datetime_to_string()[0]
                        final["message"] = "Valid application"
            else:
                final["valid_ot_in"] = self.parser([time_in]).parse_datetime_to_string()[0]
                final["valid_ot_out"] = self.parser([
                    time_in + datetime.timedelta(hours=9)
                ]).parse_datetime_to_string()[0]
                final["ot_type"] = "Rest day overtime"
                final["has_shift"]: False
                final["is_qualified"]: True
                final["message"] = "Rest day OT application"
        return final
