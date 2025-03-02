import json
from django.db import connection
from payroll.utils.queries.statements import select as statements
from payroll.utils.general.general import (fetchall_dictionary)
from payroll.utils.general.response_builder import ResponseBuilder


class ReadAttendanceLastRecord:
    def __init__(self, requests):
        self.request = requests
        self.body = json.loads(requests.body)

    def execute(self):
        company_id = self.request.COOKIES["company_id"]
        badge_no = self.body['data']['badge_no']
        query = statements.kiosk_get_last

        with connection.cursor() as cursor:
            cursor.execute(str(query).format(badge_no, company_id))

            results_raw = fetchall_dictionary(cursor)

            if len(results_raw) > 0:
                results = ResponseBuilder(results_raw[0]).attendance_kiosk()
            else:
                results = None

        return results


class ReadAttendancePunchResponse:
    def __init__(self, attendance_id):
        self.attendance_id = attendance_id

    def execute(self):
        attendance_id = self.attendance_id
        query = statements.kiosk_get_response

        with connection.cursor() as cursor:
            cursor.execute(str(query).format(attendance_id))

            results_raw = fetchall_dictionary(cursor)

            if len(results_raw) > 0:
                results = ResponseBuilder(results_raw[0]).attendance_kiosk()
            else:
                results = None

        return results
