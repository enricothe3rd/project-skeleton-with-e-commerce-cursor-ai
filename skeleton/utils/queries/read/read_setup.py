import datetime

import requests
from django.conf import settings
from payroll.utils.general.general import (execute_raw_query, build_conditions)
from payroll.utils.queries.statements import select as statements
from payroll.utils.queries.statements import setup_select as setup_statements
from payroll.utils.general.response_payload_setup import (BuildEmployeeShiftGenerated, BuildEmployeeShift,
                                                          BuildPositions, BuildUsers, BuildDepartments, BuildTeams,
                                                          BuildHolidays)
from payroll.utils.general.general import ParseValues
from payroll.models.core import Config


class ExecFetchAssociatedUser:
    def __init__(self, request):
        self.requests = request

    def read(self):
        uid = self.requests.COOKIES["user_id"]
        query = setup_statements.read_associated_user
        raw_data = execute_raw_query(query.format(uid))
        if len(raw_data) > 0:
            return raw_data[0]
        else:
            return {"id": 0}


class ReadEmployeeShiftGenerated:
    def __init__(self, request):
        self.requests = request

    def read_list(self):
        conditions = self.requests.GET.get("filters")

        raw_query = statements.shift_generated_list
        raw_values = execute_raw_query(
            raw_query.format(build_conditions(conditions))
        )

        values = BuildEmployeeShiftGenerated(raw_values).execute()

        return {"value": values}

    def read_one(self):
        conditions = self.requests.GET.get("filters")

        raw_query = statements.shift_generated_list
        raw_values = execute_raw_query(
            raw_query.format(build_conditions(conditions))
        )

        values = BuildEmployeeShiftGenerated(raw_values).execute()

        return {"value": values}


class ReadShift:
    def __init__(self, request):
        self.requests = request

    def read_list(self):
        conditions = self.requests.GET.get("filters")

        raw_query = statements.shift_list_get
        raw_values = execute_raw_query(
            raw_query.format(build_conditions(conditions))
        )

        values = BuildEmployeeShift(raw_values).execute()

        return {"value": values}

    def read_one(self):
        conditions = self.requests.GET.get("filters")

        raw_query = statements.shift_list_get
        raw_values = execute_raw_query(
            raw_query.format(build_conditions(conditions))
        )

        values = BuildEmployeeShift(raw_values).execute()

        return {"value": values}

    def read_list_re_execute(self):
        date_obj = (ParseValues([self.requests.GET.get("date_from"), self.requests.GET.get("date_to")]).
                    parse_date_from_string())
        date_from_param = ParseValues(date_obj[0]).parse_date_to_string_ymd()
        date_to_param = ParseValues(date_obj[1] + datetime.timedelta(days=1)).parse_date_to_string_ymd()  # OBSERVATION
        employee_id = self.requests.GET.get("eid")
        filters = ("datetime_from::text >= '%s' AND datetime_to::text <= '%s' AND employee_id_id = %s" %
                   (date_from_param, date_to_param, employee_id))

        raw_query = statements.shift_list_get
        raw_values = execute_raw_query(
            raw_query.format(filters)
        )

        values = BuildEmployeeShift(raw_values).execute()

        return {"value": values}


class ReadPositions:
    def __init__(self, request):
        self.requests = request

    def read_list(self):
        conditions = self.requests.GET.get("filters")

        raw_query = setup_statements.read_positions_list_header
        raw_values = execute_raw_query(
            raw_query.format(build_conditions(conditions))
        )

        values = BuildPositions(raw_values).execute_list()

        return {"value": values}

    def read_one(self):
        conditions = self.requests.GET.get("filters")

        raw_query_header = setup_statements.read_positions_list_header
        raw_query_lines = setup_statements.read_positions_line

        raw_values_header = execute_raw_query(
            raw_query_header.format(build_conditions(conditions))
        )
        raw_query_lines = execute_raw_query(
            raw_query_lines.format(build_conditions(conditions))
        )

        header = BuildPositions(raw_values_header).execute_header()
        lines = BuildPositions(raw_query_lines).execute_lines()

        final = {
            "data": {
                "header": header,
                "lines": lines
            }
        }

        return {"values": final}


class ReadDepartments:
    def __init__(self, request):
        self.requests = request

    def read_list(self):
        conditions = self.requests.GET.get("filters")
        query = setup_statements.read_departments
        raw_values = execute_raw_query(query.format(build_conditions(conditions)))
        return {"value": BuildDepartments(raw_values).execute_list()}

    def read_one(self):
        conditions = self.requests.GET.get("filters")
        query = setup_statements.read_departments
        raw_values = execute_raw_query(query.format(build_conditions(conditions)))
        return {"value": raw_values}


class ReadTeams:
    def __init__(self, request):
        self.requests = request

    def read_list(self):
        conditions = self.requests.GET.get("filters")
        query = setup_statements.read_teams
        raw_values = execute_raw_query(query.format(build_conditions(conditions)))
        return {"value": BuildTeams(raw_values).execute_list()}


class ReadHolidays:
    def __init__(self, request):
        self.requests = request

    def read_list(self):
        conditions = self.requests.GET.get("filters")
        query = setup_statements.read_holidays
        raw_values = execute_raw_query(query.format(build_conditions(conditions)))
        return {"value": BuildHolidays(raw_values).execute_list()}


class ReadUsers:
    def __init__(self, request):
        self.requests = request

    def read_list(self):
        conditions = self.requests.GET.get("filters")
        cookies = {
            'company_id': self.requests.COOKIES['company_id'],
            'token': self.requests.COOKIES['token'],
            'user_id': self.requests.COOKIES['user_id'],
            'level': self.requests.COOKIES['level'],
        }
        response = requests.get(
            settings.USER_SERVICE_URL + '/users/users-list?filters=' + conditions,
            cookies=cookies,
            verify=False
        )
        return {"value": BuildUsers(response.json()).execute_list()}

    def read_one(self):
        conditions = self.requests.GET.get("filters")
        cookies = {
            'company_id': self.requests.COOKIES['company_id'],
            'token': self.requests.COOKIES['token'],
            'user_id': self.requests.COOKIES['user_id'],
            'level': self.requests.COOKIES['level'],
        }
        response = requests.get(
            settings.USER_SERVICE_URL + '/users/users-list?filters=' + conditions,
            cookies=cookies,
            verify=False
        )
        raw_values = []
        user_dict = response.json()
        if len(user_dict) > 0:
            assoc_user_filter = "associated_user_id,=,{},None".format(user_dict[0]["id"])
            raw_query = setup_statements.read_users_list
            raw_values = execute_raw_query(
                raw_query.format(build_conditions(assoc_user_filter))
            )
        if len(raw_values) > 0:
            user_dict[0]["associated_user_name"] = raw_values[0]["long_name"]
            user_dict[0]["associated_user_id"] = raw_values[0]["id"]
        return user_dict


class ReadCompanies:
    def __init__(self, request):
        self.requests = request

    def read_list(self):
        conditions = self.requests.GET.get("filters")
        cookies = {
            'company_id': self.requests.COOKIES['company_id'],
            'token': self.requests.COOKIES['token'],
            'user_id': self.requests.COOKIES['user_id'],
            'level': self.requests.COOKIES['level'],
        }
        response = requests.get(
            settings.USER_SERVICE_URL + '/users/companies-list?filters=' + conditions,
            cookies=cookies,
            verify=False
        )
        return {"value": response.json()}

    def read_one(self):
        conditions = self.requests.GET.get("filters")
        cookies = {
            'company_id': self.requests.COOKIES['company_id'],
            'token': self.requests.COOKIES['token'],
            'user_id': self.requests.COOKIES['user_id'],
            'level': self.requests.COOKIES['level'],
        }
        response = requests.get(
            settings.USER_SERVICE_URL + '/users/companies-one?filters=' + conditions,
            cookies=cookies,
            verify=False
        )
        return response.json()

    def check_duplicate(self):
        conditions = self.requests.GET.get("tin")
        cookies = {
            'company_id': self.requests.COOKIES['company_id'],
            'token': self.requests.COOKIES['token'],
            'user_id': self.requests.COOKIES['user_id'],
            'level': self.requests.COOKIES['level'],
        }
        response = requests.get(
            settings.USER_SERVICE_URL + '/users/check-duplicate-company?tin=' + conditions,
            cookies=cookies,
            verify=False
        )
        return response.json()

    def get_active_company_list(self):
        query = setup_statements.read_all_company_with_config.format(self.requests)
        raw = execute_raw_query(query)
        return raw


class FetchGeneralSettings:
    def __init__(self, request):
        self.requests = request

    def read_one(self):
        company_id = self.requests.GET.get("company_id")
        raw_values = Config.objects.filter(company_id=company_id)
        if len(raw_values) > 0:
            return raw_values.values()[0]
        else:
            return {
                "fiscal_end": "December/31",
                "payroll_schedule": "SEMI_MONTHLY",
                "grace_time": 15,
                "active_kiosk": "Kiosk-1",
                "is_leave_precise": True,
                "salary_cycle": "15TH-END",
                "time_precision": "minute",
                "months_before_regularization": 6,
                "attendance_rounding": "ROUND-DOWN",
                "overtime_rounding": "ROUND-UP",
                "tardiness_rounding": "ROUND-UP",
                "undertime_rounding": "ROUND-UP",
                "forecasted_allowance_tax": True,
                "break_in_between_minutes": 0,
                "lunch_break_duration_minutes": 60,
                "max_untaxable_allowance": 90000,
                "manual_encoding_only": False,
                "break_before_ot_minutes": 60,
                "force_user_employee_link": True,
                "auto_generate_badge": True
            }
