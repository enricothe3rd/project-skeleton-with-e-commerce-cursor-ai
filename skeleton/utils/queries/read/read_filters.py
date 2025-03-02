from django.db import connection
from payroll.utils.general.general import (fetchall_dictionary, build_conditions,)
from payroll.utils.queries.statements import select_filters as statement


class ReadDepartmentDropdown:
    def __init__(self, requests):
        self.requests = requests

    def execute(self):
        query = statement.department_filters.format("A.company_id = %s" % self.requests.COOKIES['company_id'])

        with connection.cursor() as cursor:
            cursor.execute(str(query))

            results = fetchall_dictionary(cursor)

        return {"values": results}


class ReadTeamDropdown:
    def __init__(self, requests):
        self.requests = requests

    def execute(self):
        query = statement.team_filters.format("A.company_id = %s" % self.requests.COOKIES['company_id'])

        with connection.cursor() as cursor:
            cursor.execute(str(query))

            results = fetchall_dictionary(cursor)

        return {"values": results}


class ReadPositionDropdown:
    def __init__(self, requests):
        self.requests = requests

    def execute(self):
        query = statement.position_filters.format("A.company_id = %s" % self.requests.COOKIES['company_id'])

        with connection.cursor() as cursor:
            cursor.execute(str(query))

            results = fetchall_dictionary(cursor)

        return {"values": results}


class ReadEmployeeDropdown:
    def __init__(self, requests):
        self.requests = requests

    def execute(self):
        conditions = build_conditions("%scompany_id,=,%s,None" % (self.requests.GET.get("filters"),
                                                                  self.requests.COOKIES['company_id']))
        query = statement.employee_filters.format(conditions)

        with connection.cursor() as cursor:
            cursor.execute(str(query))

            results = fetchall_dictionary(cursor)

        return {"values": results}


class ReadFiscalYearDropdown:
    def __init__(self, requests):
        self.requests = requests

    def execute(self):
        cid = self.requests.COOKIES['company_id']
        query = statement.fiscal_year_filters.format(cid)

        with connection.cursor() as cursor:
            cursor.execute(str(query))

            results = fetchall_dictionary(cursor)

        return {"values": results}
