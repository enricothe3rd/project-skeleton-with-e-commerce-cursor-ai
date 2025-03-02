import datetime
import json
from payroll.utils.general.general import Queries, ParseValues, EvaluateQueryResults
from payroll.models.setup import LeaveTemplate, LeaveTemplateLine, LeaveType
from payroll.models.core import LeaveApplications, LeaveCredits, Employee, Schedule
from payroll.utils.queries.statements import select_validations as statements
from payroll.utils.general.general import (execute_raw_query)


class LeaveTemplateQueries:
    def __init__(self, requests):
        self.request = requests
        self.body = json.loads(requests.body)

    def create(self):
        try:
            company_id = self.request.COOKIES['company_id']
            header = self.body["header"]

            head_params = {
                "name": header["name"],
                "company_id": company_id
            }
            head_result = Queries(LeaveTemplate).execute_create(head_params)

            for line in self.body['line']:
                leave_type_object = LeaveType(id=line['leave_type_id'])

                line_params = {
                    "name": line['name'],
                    "leave_template_id": head_result[1],
                    "credits": line['credits'],
                    "leave_type_id": leave_type_object
                }
                Queries(LeaveTemplateLine).execute_create(line_params)

            return head_result[0]
        except KeyError as key_err:
            return {"error": str(key_err)}
        except Exception as ex:
            return {"error": str(ex)}

    def change(self):
        try:
            header = self.body['header']
            line_result = []

            head_params = {
                "name": header["name"]
            }
            head_result = Queries(LeaveTemplate).execute_change(head_params, header['id'])

            for line in self.body['line']:
                if line['id'] == "New" or line['id'] is None or line['id'] == "":
                    # Trigger CREATE
                    leave_template_object = LeaveTemplate(id=header['id'])
                    leave_type_object = LeaveType(id=line['leave_type_id'])

                    line_params = {
                        "name": line['name'],
                        "leave_template_id": leave_template_object,
                        "credits": line['credits'],
                        "leave_type_id": leave_type_object
                    }
                    res = Queries(LeaveTemplateLine).execute_create(line_params)
                    line_result.append(res[0])
                else:
                    # Trigger UPDATE
                    line_params = {
                        "name": line['name'],
                        "leave_template_id": head_result[0]['id'],
                        "credits": line['credits'],
                        "leave_type_id": line['leave_type_id']
                    }
                    Queries(LeaveTemplateLine).execute_change(line_params, line["id"])

            return [head_result[0], line_result]
        except KeyError as key_err:
            return {"error": str(key_err)}
        except Exception as ex:
            return {"error": str(ex)}

    def deactivate(self):
        pass

    def reactivate(self):
        pass

    def delete_line(self):
        try:
            body = self.body['line']

            leave_template_line_id = LeaveTemplateLine.objects.filter(id=body['id'])
            leave_template_line_id.delete()

            return {"message": "Leave Template Line was deleted", "keys": body['id']}
        except KeyError as key_err:
            return {"error": str(key_err)}
        except Exception as ex:
            return {"error": str(ex)}

    def delete(self):
        try:
            body = self.body['data']

            leave_template_object = LeaveTemplate.objects.filter(id=body['id'])
            leave_template_object.delete()

            return {"message": "Leave Template Line was deleted", "keys": body['id']}
        except KeyError as key_err:
            return {"error": str(key_err)}
        except Exception as ex:
            return {"error": str(ex)}

    def read(self):
        pass

    def validate(self):
        pass


class LeaveTypeQueries:
    def __init__(self, requests):
        self.request = requests
        self.body = json.loads(requests.body)

    def create(self):
        try:
            company_id = self.request.COOKIES['company_id']
            body = self.body['data']

            params = {
                "name": body['name'],
                "initial_credits": body["initial_credits"],
                "grant_leave_after": body["grant_leave_after"],
                "convert_rate_percent": body['convert_rate_percent'],
                "is_paid": body['is_paid'],
                "is_reset": body['is_reset'],
                "is_convertible": body['is_convertible'],
                "is_applied_straight": body['is_applied_straight'],
                "company_id": company_id
            }
            # print(params)
            result = Queries(LeaveType).execute_create(params)

            return result[0]["status"]
        except KeyError as key_err:
            return {"error": str(key_err)}
        except Exception as ex:
            return {"error": str(ex)}

    def change(self):
        try:
            body = self.body['data']

            params = {
                "name": body['name'],
                "initial_credits": body["initial_credits"],
                "grant_leave_after": body["grant_leave_after"],
                "convert_rate_percent": body['convert_rate_percent'],
                "is_paid": body['is_paid'],
                "is_reset": body['is_reset'],
                "is_convertible": body['is_convertible'],
                "is_applied_straight": body['is_applied_straight'],
            }
            result = Queries(LeaveType).execute_change(params, body['id'])

            return result[0]["status"]
        except KeyError as key_err:
            return {"error": str(key_err)}
        except Exception as ex:
            return {"error": str(ex)}

    def deactivate(self):
        try:
            body = self.body['data']

            result = Queries(LeaveType).execute_deactivate(body['id'])

            return result[0]
        except KeyError as key_err:
            return {"error": str(key_err)}
        except Exception as ex:
            return {"error": str(ex)}

    def reactivate(self):
        try:
            body = self.body['data']

            result = Queries(LeaveType).execute_reactivate(body['id'])

            return result[0]
        except KeyError as key_err:
            return {"error": str(key_err)}
        except Exception as ex:
            return {"error": str(ex)}

    def read(self):
        pass

    def validate(self):
        pass

    def excel_import(self):
        pass


class LeaveQueries:
    def __init__(self, requests):
        self.request = requests
        self.body = json.loads(requests.body)
        self.duration = {
            'AM': 0.5,
            'PM': 0.5,
            'WHOLE': 1
        }

    def leave_application_crud(self):
        return self.LeaveApplicationQueries(self.request, self.body, self.duration)

    def leave_credits_crud(self, employee):
        return self.LeaveCreditsQueries(self.request, self.body, self.duration, employee)

    class LeaveApplicationQueries:
        def __init__(self, *args):
            self.request = args[0]
            self.body = args[1]
            self.duration = args[2]
            # self.employee = args[3]

        def create(self):
            try:
                company_id = self.request.COOKIES['company_id']
                body = self.body['data']

                if not self._check_leave_type(body['leave_credit_id']):
                    if (not self.has_schedule(body['date'], body['employee_id']) and
                            self.is_manually_scheduled(body['employee_id'])):
                        return {
                            'success': False,
                            'status': 'error',
                            'code': 'LVA001-C',
                            'message': 'Employee have no schedule on selected date.'
                        }
                    elif self.has_duplicate_entry(body['date'], body['employee_id']):
                        return {
                            'success': False,
                            'status': 'error',
                            'code': 'LVA002-C',
                            'message': 'Leave already applied on selected date.'
                        }
                    else:
                        parse_date = ParseValues([body['date']]).parse_date_from_string()
                        employee_obj = Employee(id=body['employee_id'])
                        leave_credit_obj = LeaveCredits(id=body['leave_credit_id'])

                        params = {
                            "employee_id": employee_obj,
                            "leave_credit": leave_credit_obj,
                            "date": parse_date[0],
                            "duration": body['duration'],
                            "company_id": company_id
                        }

                        result = Queries(LeaveApplications).execute_create(params)

                        if result[0]["status"]:
                            params = {
                                "credits": body['remaining_credit'] - self.duration[body['duration']]
                            }
                            Queries(LeaveCredits).execute_change(params, body['leave_credit_id'])

                            return {
                                'success': True,
                                'status': 'success',
                                'message': 'Leave Application was successfully saved!'
                            }
                        else:
                            return {
                                'success': False,
                                'status': 'error',
                                'code': 'LVA003-C',
                                'message': 'An error occurred.'
                            }
                else:
                    insert_result = True
                    result = self._qualify_application(body)
                    employee_obj = Employee(id=body['employee_id'])
                    leave_credit_obj = LeaveCredits(id=body['leave_credit_id'])
                    if result["result"]:
                        credit = len(result["date_arr"])
                        for date in result["date_arr"]:
                            origin_date = ParseValues([body['date']]).parse_date_from_string()
                            date_obj = ParseValues(date["datetime_from"]).parse_date_to_string()
                            parsed_date = ParseValues([date_obj]).parse_date_from_string()

                            params = {
                                "employee_id": employee_obj,
                                "leave_credit": leave_credit_obj,
                                "date": parsed_date[0],
                                "duration": "WHOLE",
                                "origin_date": origin_date[0],
                                "company_id": company_id
                            }
                            result = Queries(LeaveApplications).execute_create(params)

                            if not result[0]['status']:
                                insert_result = False
                        if insert_result:
                            params = {
                                "credits": body['remaining_credit'] - credit
                            }
                            Queries(LeaveCredits).execute_change(params, body['leave_credit_id'])
                            return {
                                'success': True,
                                'status': 'error',
                                'code': 'LVA004-C',
                                'message': 'Consecutive Application successfully applied.'
                            }
                        else:
                            return {
                                'success': False,
                                'status': 'error',
                                'code': 'LVA005-C',
                                'message': '''An error occurred on saving the application, please delete previous 
                                records and create new application again.'''
                            }
                    else:
                        return {
                            'success': False,
                            'status': 'error',
                            'code': 'LVA004-C',
                            'message': 'Cannot apply consecutive leaves. Please generate shifts first.'
                        }
            except KeyError as key_err:
                return {"error": str(key_err)}
            except Exception as ex:
                return {"error": str(ex)}

        def change(self):
            try:
                company_id = self.request.COOKIES['company_id']
                body = self.body['data']

                if body['approval_status'] == 'APPROVED':
                    return {
                        'success': False,
                        'status': 'error',
                        'code': 'LVA001-U',
                        'message': 'Cannot update an Approved Leave Application.'
                    }
                elif (not self.has_schedule(body['date'], body['employee_id']) and
                        self.is_manually_scheduled(body['employee_id'])):
                    return {
                        'success': False,
                        'status': 'error',
                        'code': 'LVA001-U',
                        'message': 'Employee have no schedule on selected date.'
                    }
                else:
                    if not self._check_leave_type(body['leave_credit_id']):
                        previous_values = self.fetch_previous_leave(body["id"])
                        parse_date = ParseValues([body['date']]).parse_date_from_string()

                        params = {
                            "employee_id": body['employee_id'],
                            "leave_credit": body['leave_credit_id'],
                            "date": parse_date[0],
                            "duration": body['duration'],
                            "company_id": company_id
                        }
                        result = Queries(LeaveApplications).execute_change(params, body['id'])

                        if result[0]["status"]:
                            remaining_credit = body['remaining_credit']

                            if self.duration[previous_values["duration"]] > self.duration[body['duration']]:
                                remaining_credit += 0.5
                            elif self.duration[previous_values["duration"]] < self.duration[body['duration']]:
                                remaining_credit -= 0.5
                            else:
                                remaining_credit = body['remaining_credit']

                            params = {
                                "credits": remaining_credit
                            }
                            Queries(LeaveCredits).execute_change(params, body['leave_credit_id'])

                            return {
                                'success': True,
                                'status': 'success',
                                'message': 'Leave Application was successfully saved!'
                            }
                        else:
                            return {
                                'success': False,
                                'status': 'error',
                                'code': 'LVA003-U',
                                'message': 'An error occurred.'
                            }
                    else:
                        update_result = True
                        result = self._qualify_application_update(body, "CHANGE")
                        if result["result"]:
                            for date in result["date_arr"]:
                                parse_date = ParseValues([body['date']]).parse_date_from_string()
                                params = {
                                    "leave_credit": body['leave_credit_id'],
                                    "date": date["datetime_from"],
                                    "origin_date": parse_date[0],
                                    "duration": body['duration'],
                                    "company_id": company_id
                                }
                                result = Queries(LeaveApplications).execute_change(params, date['id'])

                                if not result[0]['status']:
                                    update_result = False
                            if update_result:
                                return {
                                    'success': True,
                                    'status': 'success',
                                    'message': 'Leave Application was successfully updated!'
                                }
                            else:
                                return {
                                    'success': False,
                                    'status': 'error',
                                    'code': 'LVA005-U',
                                    'message': 'Update execution error!'
                                }
                        else:
                            return {
                                'success': False,
                                'status': 'error',
                                'code': 'LVA004-U',
                                'message': 'Cannot apply consecutive leaves. Please generate shifts first.'
                            }
            except KeyError as key_err:
                return {"error": str(key_err)}
            except Exception as ex:
                return {"error": str(ex)}

        def update_status(self):
            try:
                # company_id = self.request.COOKIES['company_id']
                body = self.body['data']

                if not self._check_leave_type(body['leave_credit_id']):
                    params = {
                        "approval_status": body["approval_status"]
                    }
                    result = Queries(LeaveApplications).execute_change(params, body['id'])

                    if result[0]["status"]:
                        # previous_values = self.fetch_previous_leave(body["id"])
                        if body['approval_status'] == "DECLINED":
                            remaining_credit = body['remaining_credit']

                            if body["duration"] != "WHOLE":
                                remaining_credit += 0.5
                            else:
                                remaining_credit += 1

                            params = {
                                "credits": remaining_credit
                            }
                            Queries(LeaveCredits).execute_change(params, body['leave_credit_id'])

                        return {
                            'success': True,
                            'status': 'success',
                            'message': 'Leave application was {}'.format(str(body['approval_status']).lower())
                        }
                    else:
                        return {
                            'success': False,
                            'status': 'error',
                            'code': 'LVA003-U',
                            'message': 'An error occurred.'
                        }
                else:
                    update_result = True
                    result = self._qualify_application_update(body, "STATUS")
                    credit = len(result["date_arr"])
                    if result["result"]:
                        for date in result["date_arr"]:
                            params = {
                                "approval_status": body["approval_status"]
                            }
                            result = Queries(LeaveApplications).execute_change(params, date['id'])

                            if not result[0]['status']:
                                update_result = False
                        if update_result:
                            if body["approval_status"] == "DECLINED":
                                params = {
                                    "credits": body["remaining_credit"] + credit
                                }
                                Queries(LeaveCredits).execute_change(params, body['leave_credit_id'])

                            return {
                                'success': True,
                                'status': 'success',
                                'message': 'Leave application was {}'.format(str(body['approval_status']).lower())
                            }
                        else:
                            return {
                                'success': False,
                                'status': 'error',
                                'code': 'LVA005-U',
                                'message': 'Update execution error!'
                            }
                    else:
                        return {
                            'success': False,
                            'status': 'error',
                            'code': 'LVA004-U',
                            'message': 'Cannot apply consecutive leaves. Please generate shifts first.'
                        }
            except KeyError as key_err:
                print(str(key_err))
                return {"error": str(key_err)}
            except Exception as ex:
                print(str(ex))
                return {"error": str(ex)}

        def deactivate(self):
            try:
                body = self.body['data']
                if body['approval_status'] == 'APPROVED':
                    return {
                        'success': False,
                        'status': 'error',
                        'code': 'LVA001-U',
                        'message': 'Cannot deactivate an Approved Leave Application.'
                    }
                elif body['approval_status'] == 'DECLINED':
                    return {
                        'success': False,
                        'status': 'error',
                        'code': 'LVA001-U',
                        'message': 'Cannot deactivate a Declined Leave Application.'
                    }
                else:
                    if not self._check_leave_type(body['leave_credit_id']):
                        result = Queries(LeaveApplications).execute_deactivate(body["id"])

                        if result[0]["status"]:
                            previous_values = self.fetch_previous_leave(body["id"])
                            remaining_credit = body['remaining_credit'] + self.duration[previous_values['duration']]

                            params = {
                                "credits": remaining_credit
                            }
                            Queries(LeaveCredits).execute_change(params, body['leave_credit_id'])

                            return {
                                'success': True,
                                'status': 'success',
                                'message': 'Leave Application successfully reverted.'
                            }
                        else:
                            return {
                                'success': False,
                                'status': 'error',
                                'code': 'LVA003-D',
                                'message': 'An error occurred.'
                            }
                    else:
                        update_result = True
                        result = self._qualify_application_update(body, "STATUS")
                        if result["result"]:
                            for date in result["date_arr"]:
                                deactivate_result = Queries(LeaveApplications).execute_deactivate(date['id'])

                                if not deactivate_result[0]['status']:
                                    update_result = False
                            if update_result:
                                params = {
                                    "credits": body['remaining_credit'] + len(result["date_arr"])
                                }
                                print(params)
                                Queries(LeaveCredits).execute_change(params, body['leave_credit_id'])

                                return {
                                    'success': True,
                                    'status': 'success',
                                    'message': 'Leave Application was successfully updated!'
                                }
                            else:
                                return {
                                    'success': False,
                                    'status': 'error',
                                    'code': 'LVA005-U',
                                    'message': 'Update execution error!'
                                }
                        else:
                            return {
                                'success': False,
                                'status': 'error',
                                'code': 'LVA004-U',
                                'message': 'Cannot apply consecutive leaves. Please generate shifts first.'
                            }
            except KeyError as key_err:
                return {"error": str(key_err)}
            except Exception as ex:
                return {"error": str(ex)}

        def reactivate(self):
            try:
                body = self.body['data']

                result = Queries(LeaveApplications).execute_reactivate(body['id'])

                return result[0]
            except KeyError as key_err:
                return {"error": str(key_err)}
            except Exception as ex:
                return {"error": str(ex)}

        def remove(self):
            pass

        @staticmethod
        def _qualify_application(data):
            query = statements.fetch_credits_number
            credits_raw = execute_raw_query(
                query.format(data["leave_credit_id"])
            )
            if len(credits_raw) > 0:
                date_arr = []
                result = False
                strikes = 30
                credit = round(credits_raw[0]["credits"])
                increment_date = ParseValues([data['date']]).parse_date_from_string()[0]

                while strikes != 0:
                    date_new_format = ParseValues(increment_date).parse_date_to_string_ymd()

                    raw_query = statements.validate_leave_to_schedule
                    raw_values = execute_raw_query(
                        raw_query.format(date_new_format, data["employee_id"])
                    )

                    if len(raw_values) > 0:
                        date_arr.append(raw_values[0])
                        credit -= 1
                    else:
                        strikes -= 1
                    if credit <= 0:
                        result = True
                        break
                    increment_date += datetime.timedelta(days=1)
                return {"result": result, "date_arr": date_arr}
            else:
                return {"result": False}

        @staticmethod
        def _qualify_application_update(data, update_type):
            origin_date_query = statements.fetch_origin_date
            origin_date_raw = execute_raw_query(
                origin_date_query.format(data["id"])
            )
            core_leave_count_query = statements.fetch_core_leave
            origin_date = ParseValues(origin_date_raw[0]["origin_date"]).parse_date_to_string_ymd()
            core_leave_raw = execute_raw_query(
                core_leave_count_query.format(origin_date, data["employee_id"], data["leave_credit_id"])
            )
            if len(core_leave_raw) > 0:
                date_arr = []
                result = False
                strikes = 30
                credit = len(core_leave_raw)
                index = 0
                if update_type == "CHANGE":
                    increment_date = ParseValues([data["date"]]).parse_date_from_string()[0]
                else:
                    increment_date = origin_date_raw[0]["origin_date"]

                while strikes != 0:
                    date_new_format = ParseValues(increment_date).parse_date_to_string_ymd()

                    raw_query = statements.validate_leave_to_schedule
                    raw_values = execute_raw_query(
                        raw_query.format(date_new_format, data["employee_id"])
                    )

                    if len(raw_values) > 0:
                        raw = raw_values[0]
                        raw["datetime_from"] = increment_date
                        raw["id"] = core_leave_raw[index]['id']
                        date_arr.append(raw)
                        credit -= 1
                        index += 1
                    else:
                        strikes -= 1
                    if credit <= 0:
                        result = True
                        break
                    increment_date += datetime.timedelta(days=1)
                return {"result": result, "date_arr": date_arr}
            else:
                return {"result": False}

        @staticmethod
        def _check_leave_type(leave_credit_id):
            query = statements.check_leave_type
            raw_values = execute_raw_query(
                query.format(leave_credit_id)
            )
            if len(raw_values) > 0:
                return raw_values[0]['is_applied_straight']
            else:
                return []

        @staticmethod
        def fetch_previous_leave(sid):
            leave_application_obj = LeaveApplications.objects.filter(id=sid)
            return leave_application_obj.values()[0]

        @staticmethod
        def has_duplicate_entry(date, employee):
            date_obj = ParseValues([date]).parse_date_from_string()
            date_new_format = ParseValues(date_obj[0]).parse_date_to_string_ymd()
            raw_query = statements.validate_duplicate
            raw_values = execute_raw_query(
                raw_query.format(date_new_format, employee)
            )
            if len(raw_values) > 0:
                return True
            else:
                return False

        @staticmethod
        def is_manually_scheduled(employee):
            employee_schedule_obj = Schedule.objects.filter(employee_id=employee)
            employee_schedule = employee_schedule_obj.values()[0]

            if employee_schedule["is_manual_attendance"]:
                return False
            else:
                return True

        @staticmethod
        def has_schedule(date, employee):
            date_obj = ParseValues([date]).parse_date_from_string()
            date_new_format = ParseValues(date_obj[0]).parse_date_to_string_ymd()

            raw_query = statements.validate_leave_to_schedule
            raw_values = execute_raw_query(
                raw_query.format(date_new_format, employee)
            )

            if len(raw_values) > 0:
                return True
            else:
                return False

        def read(self):
            pass

    class LeaveCreditsQueries:
        def __init__(self, *args):
            self.request = args[0]
            self.body = args[1]
            self.duration = args[2]
            self.employee = args[3]

        def create(self):
            try:
                leaves = self.body['data']['leaves']
                results = []

                for leaves_det in leaves:
                    leave_type_object = LeaveType(id=leaves_det['leave_type_id'])

                    params = {
                        "employee_id": self.employee,
                        "leave_type_id": leave_type_object,
                        "credits": leaves_det['credits']
                    }

                    results.append(Queries(LeaveCredits).execute_create(params))

                return EvaluateQueryResults(results).execute_query_results()
            except KeyError as key_err:
                return {"error": str(key_err)}
            except Exception as ex:
                return {"error": str(ex)}

        def change(self):
            try:
                leaves = self.body['data']['leaves']
                results = []

                for leaves_det in leaves:
                    leave_id = leaves_det['id']

                    params = {
                        "credits": leaves_det['credits']
                    }

                    if leave_id == "":
                        params["employee_id"] = Employee(id=self.employee)
                        params["leave_type_id"] = LeaveType(id=leaves_det['leave_type_id'])
                        results.append(Queries(LeaveCredits).execute_create(params))
                    else:
                        params["employee_id"] = self.employee
                        params["leave_type_id"] = leaves_det['leave_type_id']
                        results.append(Queries(LeaveCredits).execute_change(params, leave_id))

                return EvaluateQueryResults(results).execute_query_results()
            except KeyError as key_err:
                return {"error": str(key_err)}
            except Exception as ex:
                return {"error": str(ex)}

        def deactivate(self):
            try:
                leaves = self.body['archive']['leaves']
                result = []

                if len(leaves) > 0:
                    for leave in leaves:
                        result.append(Queries(LeaveCredits).execute_deactivate(leave))

                print(result)
                return result
            except KeyError as key_err:
                return {"error": str(key_err)}
            except Exception as ex:
                return {"error": str(ex)}

        def reactivate(self):
            try:
                body = self.body['data']

                result = Queries(LeaveCredits).execute_reactivate(body['id'])

                return result[0]
            except KeyError as key_err:
                return {"error": str(key_err)}
            except Exception as ex:
                return {"error": str(ex)}

        def validate(self):
            pass

        def read(self):
            pass

        def excel_import(self):
            pass

    class LeaveApplicationsApprovalQueries:
        def __init__(self, *args):
            self.request = args[0]
            self.body = args[1]

        def approve_leave_request(self):
            return self._approve_execute("APPROVED")

        def disapprove_leave_revoke(self):
            return self._approve_execute("PENDING")

        def disapprove_leave_request(self):
            return self._approve_execute("DENIED")

        def _approve_execute(self, status):
            try:
                approver_id = self.request.COOKIES['user_id']
                body = self.body['data']

                params = {
                    "approval_status": status,
                    "approval_remarks": body['approval_remarks'],
                    "approved_by": approver_id
                }
                result = Queries(LeaveApplications).execute_change(params, body['id'])

                return result[0]
            except KeyError as key_err:
                return {"error": str(key_err)}
            except Exception as ex:
                return {"error": str(ex)}
