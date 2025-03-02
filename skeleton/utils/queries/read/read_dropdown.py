import requests
from django.conf import settings
from django.db import connection
from payroll.utils.general.general import (fetchall_dictionary, build_conditions,)
from payroll.utils.queries.statements import select_async as statements


class ReadDeductionsDropdown:
    def __init__(self, request):
        self.request = request

    @staticmethod
    def execute():
        query = statements.deductions_async

        with connection.cursor() as cursor:
            cursor.execute(str(query))

            results = fetchall_dictionary(cursor)

        return {"value": results}


class ReadPositionsDropdown:
    def __init__(self, request):
        self.request = request

    def execute(self):
        company_id = self.request.COOKIES['company_id']
        forced_filters = self.request.GET.get("filters")
        filters = "is_active,=,True,AND;company_id,=," + company_id + ",AND;"
        if forced_filters is not None:
            filters = filters + forced_filters
        query = statements.positions_async
        with connection.cursor() as cursor:
            cursor.execute(str(query).format(build_conditions(filters)))

            results = fetchall_dictionary(cursor)
            print(results)

        return {"value": results}


class ReadDepartmentsDropdown:
    def __init__(self, request):
        self.request = request

    def execute(self):
        company_id = self.request.COOKIES['company_id']
        query = statements.departments_async

        with connection.cursor() as cursor:
            cursor.execute(str(query).format(company_id))

            results = fetchall_dictionary(cursor)

        return {"value": results}


class ReadLeaveCreditsDropdown:
    def __init__(self, request):
        self.request = request

    def execute(self):
        conditions = self.request.GET.get("filters")
        query = statements.leave_credits_async
        with connection.cursor() as cursor:
            cursor.execute(
                str(query.format(build_conditions(conditions)))
            )
            results = fetchall_dictionary(cursor)
        return {"value": results}


class ReadFiscalLinesDropdown:
    def __init__(self, request):
        self.request = request

    def execute(self):
        conditions = self.request.GET.get("filters")
        query = statements.fiscal_lines_async

        with connection.cursor() as cursor:
            cursor.execute(
                str(query.format(build_conditions(conditions)))
            )

            results = fetchall_dictionary(cursor)

        return {"value": results}


class ReadUnassociatedEmployeeDropdown:
    def __init__(self, request):
        self.request = request

    def execute(self):
        conditions = self.request.GET.get("filters")
        query = statements.unassociated_users_async
        filters = conditions + "is_active,=,True,AND;associated_user_id,IS,null,None"
        with connection.cursor() as cursor:
            cursor.execute(
                str(query.format(build_conditions(filters)))
            )
            results = fetchall_dictionary(cursor)

        return {"value": results}


class ReadEmployeesDropdown:
    def __init__(self, request):
        self.request = request

    def execute(self):
        conditions = self.request.GET.get("filters")
        query = statements.unassociated_users_async
        filters = "is_active,=,True,AND;" + conditions
        with connection.cursor() as cursor:
            cursor.execute(
                str(query.format(build_conditions(filters)))
            )
            results = fetchall_dictionary(cursor)
        return {"value": results}


class ReadOtherIncomeTypeDropdown:
    def __init__(self, request):
        self.request = request

    def execute(self):
        conditions = self.request.GET.get("filters")
        query = statements.other_income_types_async
        filters = "is_active,=,True,AND;" + conditions
        with connection.cursor() as cursor:
            cursor.execute(
                str(query.format(build_conditions(filters)))
            )
            results = fetchall_dictionary(cursor)
        return {"value": results}


class ReadOtherBenefitsTypeDropdown:
    def __init__(self, request):
        self.request = request

    def execute(self):
        conditions = self.request.GET.get("filters")
        query = statements.other_benefits_types_async
        filters = "is_active,=,True,AND;" + conditions
        with connection.cursor() as cursor:
            cursor.execute(
                str(query.format(build_conditions(filters)))
            )
            results = fetchall_dictionary(cursor)
        return {"value": results}


class ReadUserTypeDropdown:
    def __init__(self, request):
        self.request = request

    def execute(self):
        conditions = self.request.GET.get("filters")
        cookies = {
            'company_id': self.request.COOKIES['company_id'],
            'token': self.request.COOKIES['token'],
            'user_id': self.request.COOKIES['user_id'],
            'level': self.request.COOKIES['level'],
        }
        response = requests.get(
            settings.USER_SERVICE_URL + '/users/user_type_select-read-as-pre-requisites?level=company&filters=' +
            conditions,
            cookies=cookies,
            verify=False
        )
        return response.json()
