from django.db import connection
from payroll.utils.general.general import (ParseValues, fetchall_dictionary, build_conditions, execute_raw_query)
from payroll.utils.queries.statements import select_validations as validate
from payroll.utils.queries.statements import select as statements
from payroll.utils.queries.statements import select_payroll_generate as payroll_statements
from payroll.utils.general.response_builder import (BuildCheckBadgeNo, BuildShiftGenerate,
                                                    BuildShiftGenerateSuggestValue, BuildValidOTValues)


class ReadValidateBadge:
    def __init__(self, requests):
        self.requests = requests

    def execute(self):
        value = []
        company_id = self.requests.COOKIES['company_id']
        params = self.requests.GET.get("badge_no")
        query = validate.check_badge_no
        print(params)
        with connection.cursor() as cursor:
            cursor.execute(str(query).format(params, company_id))
            results = fetchall_dictionary(cursor)
        if len(results) > 0:
            value = BuildCheckBadgeNo(results).badge_no_data()
        return {
            "length": len(results),
            "value": value
        }


class ReadValidateShiftGenerate:
    def __init__(self, requests):
        self.requests = requests

    def execute(self):
        value = []
        params = self.requests.GET.get("filters")
        query = validate.validate_shift_generate
        conditions = build_conditions(params)
        with connection.cursor() as cursor:
            cursor.execute(str(query).format(conditions))
            results = fetchall_dictionary(cursor)
        if len(results) > 0:
            value = BuildShiftGenerate(results).validate()
        return {
            "length": len(results),
            "values": value
        }


class ReadSuggestValueShiftGenerate:
    def __init__(self, requests):
        self.requests = requests

    def execute(self):
        value = []
        # params = self.requests.GET.get("filters")
        company_id = self.requests.COOKIES['company_id']
        params = "company_id,=,"+company_id+",None"
        query = validate.shift_generate_suggest_value
        conditions = build_conditions(params)
        with connection.cursor() as cursor:
            cursor.execute(str(query).format(conditions))
            results = fetchall_dictionary(cursor)
        if len(results) > 0:
            value = BuildShiftGenerateSuggestValue(results).execute()
        return {
            "length": len(results),
            "values": value
        }


class ReadCheckDuplicateTimeEntry:
    def __init__(self, requests):
        self.requests = requests

    def execute(self):
        date = self.requests.GET.get("time_in")
        employee_badge = self.requests.GET.get("badge_no")
        date_obj = ParseValues([date]).parse_datetime_from_string()
        date_new_format = ParseValues(date_obj[0]).parse_date_to_string_ymd()
        raw_query = validate.validate_time_entry
        raw_values = execute_raw_query(
            raw_query.format(date_new_format, employee_badge)
        )
        if len(raw_values) > 0:
            return {"result": True, "value": raw_values}
        else:
            return {"result": False, "value": raw_values}


class ReadOTValidValues:
    def __init__(self, requests):
        self.requests = requests

    def execute(self):
        parser = ParseValues
        company_id = self.requests.COOKIES['company_id']
        params = self.requests.GET.get("filters")
        final = {
            "valid_ot_in": "",
            "valid_ot_out": "",
            "has_shift": False
        }
        config = execute_raw_query(
            payroll_statements.payroll_fetch_config.format(company_id)
        )
        raw_query = statements.attendances_get_one
        raw_values = execute_raw_query(
            raw_query.format(build_conditions(params))
        )
        if len(raw_values) > 0:
            attendance_values = raw_values[0]
            attendance_time_in = attendance_values["time_in"]
            if attendance_values["correction_approval_status"] == "APPROVED":
                attendance_time_in = attendance_values["correct_time_in"]
            shift_raw_query = validate.validate_ot_if_has_shift
            filter_time_in = parser(attendance_time_in).parse_date_to_string_ymd()
            shift_raw_values = execute_raw_query(
                shift_raw_query.format(filter_time_in, attendance_values["employee_id"])
            )
            final = BuildValidOTValues(
                attendance=attendance_values,
                shift=shift_raw_values,
                config=config[0]
            ).execute()
        return {"result": True, "value": final}


class ReadDepartmentDependencies:
    def __init__(self, requests):
        self.requests = requests

    def execute(self):
        company_id = self.requests.COOKIES['company_id']
        dept_id = self.requests.GET.get("id")
        raw_query = statements.get_department_usages.format(company_id, dept_id)
        raw_values = execute_raw_query(
            raw_query
        )
        return {"count": len(raw_values)}


class ReadTeamDependencies:
    def __init__(self, requests):
        self.requests = requests

    def execute(self):
        company_id = self.requests.COOKIES['company_id']
        team_id = self.requests.GET.get("id")
        raw_query = statements.get_department_usages.format(company_id, team_id)
        raw_values = execute_raw_query(
            raw_query
        )
        return {"count": len(raw_values)}


class ReadPositionsDependencies:
    def __init__(self, requests):
        self.requests = requests

    def execute(self):
        company_id = self.requests.COOKIES['company_id']
        team_id = self.requests.GET.get("id")
        raw_query = statements.get_positions_usages.format(company_id, team_id)
        raw_values = execute_raw_query(
            raw_query
        )
        return {"count": len(raw_values)}
