import json
from payroll.utils.general.general import Queries, ParseValues, FetchValues
from payroll.models.setup import (TimeInSource)
from payroll.models.core import (Attendance, Employee, EmployeePositions)
from payroll.utils.queries.read.read_attendances import ReadAttendancePunchResponse
from payroll.utils.general.response_builder import ResponseBuilder


class AttendanceQueries:
    def __init__(self, requests):
        self.request = requests
        self.body = json.loads(requests.body)

    def crud(self):
        return self.AttendanceCrud(self.request, self.body)

    def kiosk(self):
        return self.KioskAttendance(self.request, self.body)

    def updating(self):
        return self.Updating(self.request, self.body)

    def excel_upload(self):
        return self.ExcelUpload(self.request, self.body)

    class AttendanceCrud:
        def __init__(self, *args):
            self.request = args[0]
            self.body = args[1]

        def create(self):
            try:
                company_id = self.request.COOKIES['company_id']
                body = self.body['data']

                time = ParseValues([body['time_in'], body['time_out']]).parse_datetime_from_string()
                employee_object = Employee(id=body["employee_id"])
                timein_source_object = TimeInSource(id=body["timein_source_id"])
                # approver_object = Employee(associated_user_id=body['attendance_approved_by_id'])

                params = {
                    "time_in": time[0],
                    "time_out": time[1],
                    "employee_id": employee_object,
                    "timein_source_id": timein_source_object,
                    "company_id": company_id,
                    "attendance_approval_status": body['attendance_approval_status'],

                    "manual_ot_duration": body['manual_ot_duration'],
                    "manual_undertime_duration": body['manual_undertime_duration'],
                    "manual_tardiness_duration": body['manual_tardiness_duration'],
                    "manual_attendance_type": body['manual_attendance_type'],
                    "manual_leave_applied": body['manual_leave_applied']
                }

                result = Queries(Attendance).execute_create(params)
                return str(result)
            except KeyError as key_err:
                print("ERR" + str(key_err))
                return {"error": str(key_err)}
            except Exception as ex:
                print("ERR" + str(ex))
                return {"error": str(ex)}

        def change(self):
            try:
                company_id = self.request.COOKIES['company_id']
                body = self.body['data']

                employee_id = self._fetch_employee_id(body['employee_badge_no'])
                time = ParseValues([body['time_in'], body['time_out']]).parse_datetime_from_string()
                time_correct = ParseValues(
                    [body['correct_time_in'], body['correct_time_out']]
                ).parse_datetime_from_string()
                overtime = ParseValues([body['ot_from'], body['ot_to']]).parse_datetime_from_string()

                params = {
                    "time_in": time[0],
                    "time_out": time[1],

                    "correct_time_in": time_correct[0],
                    "correct_time_out": time_correct[1],
                    "correction_remarks": body["correction_remarks"],

                    "ot_from": overtime[0],
                    "ot_to": overtime[1],

                    "employee_id": employee_id,
                    "timein_source_id": body["timein_source_id"],
                    "company_id": company_id,

                    "attendance_approval_status": body['attendance_approval_status'],
                    "correction_approval_status": body['correction_approval_status'],
                    "ot_approval_status": body['ot_approval_status'],

                    "attendance_approved_by_id": body['attendance_approved_by_id'],
                    "correction_approved_by_id": body['correction_approved_by_id'],
                    "ot_approved_by_id": body['ot_approved_by_id'],

                    "manual_ot_duration": body['manual_ot_duration'],
                    "manual_undertime_duration": body['manual_undertime_duration'],
                    "manual_tardiness_duration": body['manual_tardiness_duration'],
                    "manual_attendance_type": body['manual_attendance_type'],
                    "manual_leave_applied": body['manual_leave_applied']
                }
                print(body['attendance_approval_status'])

                result = Queries(Attendance).execute_change(params, body['id'])

                return str(result)
                # return ReadAttendancePunchResponse(result[0]["values"][0]['id']).execute()
            except KeyError as key_err:
                return {"error": str(key_err)}
            except Exception as ex:
                return {"error": str(ex)}

        def archive(self):
            try:
                attendance_id = self.body["id"]
                result = Queries(Attendance).execute_deactivate(attendance_id)
                return result["status"]
            except KeyError as key_err:
                return {"error": str(key_err)}
            except Exception as ex:
                return {"error": str(ex)}

        @staticmethod
        def _fetch_employee_id(badge):
            try:
                params = {
                    "badge_no": badge
                }
                result = FetchValues(Employee).fetch_one_row(params)

                return result[0]['id']
            except KeyError as key_err:
                return {"error": str(key_err)}
            except Exception as ex:
                return {"error": str(ex)}

        def validate(self):
            pass

        def read(self):
            pass

    class Updating:
        def __init__(self, *args):
            self.request = args[0]
            self.body = args[1]

        def time_correction(self):
            data = self.body['data']
            params = {
                "correct_time_in": data['correct_time_in'],
                "correct_time_out": data['correct_time_out']
            }
            return self._execute(params, data['id'])

        def overtime_request(self):
            data = self.body['data']
            params = {
                "ot_from": data['ot_from'],
                "ot_to": data['ot_to']
            }
            return self._execute(params, data['id'])

        def attendance_approved(self):
            return self._attendance_approval("APPROVED")

        def attendance_revert(self):
            return self._attendance_approval("PENDING")

        def attendance_denied(self):
            return self._attendance_approval("DENIED")

        def correction_approved(self):
            return self._time_correction_approval("APPROVED")

        def correction_revert(self):
            return self._time_correction_approval("PENDING")

        def correction_denied(self):
            return self._time_correction_approval("DENIED")

        def overtime_approved(self):
            return self._overtime_approval("APPROVED")

        def overtime_revert(self):
            return self._overtime_approval("PENDING")

        def overtime_denied(self):
            return self._overtime_approval("DENIED")

        def _attendance_approval(self, status):
            data = self.body['data']
            approver = self.request.COOKIES['user_id']
            params = {
                "is_attendance_approved": status,
                "attendance_approved_by": approver
            }
            return self._execute(params, data['id'])

        def _time_correction_approval(self, status):
            data = self.body['data']
            approver = self.request.COOKIES['user_id']
            params = {
                "is_correction_approved": status,
                "correction_approved_by": approver,
                "correction_remarks": data['correction_remarks']
            }
            return self._execute(params, data['id'])

        def _overtime_approval(self, status):
            data = self.body['data']
            approver = self.request.COOKIES['user_id']
            params = {
                "is_ot_approved": status,
                "ot_approved_by": approver
            }
            return self._execute(params, data['id'])

        @staticmethod
        def _execute(params, uid):
            try:
                result = Queries(Attendance).execute_change(params, uid)

                return result[0]
            except KeyError as key_err:
                return {"error": str(key_err)}
            except Exception as ex:
                return {"error": str(ex)}

    class KioskAttendance:
        def __init__(self, *args):
            self.request = args[0]
            self.body = args[1]

        def create(self):
            try:
                company_id = self.request.COOKIES['company_id']
                body = self.body['data']
                time = ParseValues(body['time']).parse_ymd_hms_from_string()
                employee_data = Employee.objects.filter(badge_no=body["badge_no"]).values()[0]
                employee_object = Employee(id=employee_data['id'])
                # timein_source_object = TimeInSource(id=body["timein_source_id"])
                # approver_object = Employee(associated_user_id=body['attendance_approved_by_id'])

                params = {
                    "time_in": time[0],
                    "employee_id": employee_object,
                    "company_id": company_id,
                    "attendance_approval_status": "APPROVED",
                    # "timein_source_id": timein_source_object,
                    # "attendance_approved_by": approver_object
                }
                result = Queries(Attendance).execute_create(params)
                return {
                    "status": result[0]["status"],
                    "first_name": employee_data["first_name"],
                    "time_in": ParseValues([result[0]["values"][0]["time_in"]]).parse_datetime_to_string()[0],
                    "time_out": ParseValues([result[0]["values"][0]["time_out"]]).parse_datetime_to_string()[0]
                }
            except KeyError as key_err:
                return {"error": str(key_err)}
            except Exception as ex:
                return {"error": str(ex)}

        def change(self, attendance):
            try:
                body = self.body['data']
                time = ParseValues(body['time']).parse_ymd_hms_from_string()
                employee_data = Employee.objects.filter(id=attendance["employee_id"]).values()[0]
                params = {
                    "time_out": time[0],
                }
                result = Queries(Attendance).execute_change(params, attendance["id"])
                return {
                    "status": result[0]["status"],
                    "first_name": employee_data["first_name"],
                    "time_in": ParseValues([result[0]["values"][0]["time_in"]]).parse_datetime_to_string()[0],
                    "time_out": ParseValues([result[0]["values"][0]["time_out"]]).parse_datetime_to_string()[0]
                }
            except KeyError as key_err:
                return {"error": str(key_err)}
            except Exception as ex:
                return {"error": str(ex)}

    class ExcelUpload:
        def __init__(self, *args):
            self.request = args[0]
            self.body = args[1]

        def process_data(self):
            pass

        def _execute(self):
            pass
