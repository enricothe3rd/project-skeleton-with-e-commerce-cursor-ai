import json
from payroll.models.setup import ScheduleTemplate, ScheduleTemplateLine
from payroll.models.core import Schedule, ScheduleLine, Employee
from payroll.utils.general.general import Queries, ParseValues, EvaluateQueryResults, execute_raw_query
from payroll.utils.queries.statements import select as statements


class ScheduleTemplateQueries:
    def __init__(self, requests):
        self.request = requests
        self.body = json.loads(requests.body)

    def create(self):
        try:
            company_id = self.request.COOKIES['company_id']
            header = self.body['headers']

            head_params = _BuildScheduleParameters(
                data=header,
                company_id=company_id
            ).header_create_params()

            head_result = Queries(ScheduleTemplate).execute_create(head_params)

            for line in self.body['lines']:
                line_params = _BuildScheduleParameters(
                    data=line,
                    head_obj=head_result[1]
                ).line_create_params()

                Queries(ScheduleTemplateLine).execute_create(line_params)

            return str(head_result[0])
        except KeyError as key_err:
            return {"KeyError": str(key_err)}
        except Exception as ex:
            return {"error": str(ex)}

    def change(self):
        try:
            header = self.body['headers']

            head_params = _BuildScheduleParameters(data=header).header_change_params()

            head_result = Queries(ScheduleTemplate).execute_change(head_params, header['id'])

            for line in self.body['lines']:
                if line['id'] == "New" or line['id'] is not None or line['id'] == "":
                    # Trigger CREATE
                    header_object = ScheduleTemplate(id=header['id'])
                    line_params = _BuildScheduleParameters(
                        data=line,
                        head_obj=header_object
                    ).line_create_params()

                    Queries(ScheduleTemplateLine).execute_create(line_params)
                else:
                    line_params = _BuildScheduleParameters(
                        data=line,
                        head_id=head_result[0]['id']
                    ).line_change_params()

                    Queries(ScheduleTemplateLine).execute_change(line_params, line['id'])

            return head_result[0]
        except KeyError as key_err:
            return {"error": str(key_err)}
        except Exception as ex:
            return {"error": str(ex)}

    def deactivate(self):
        try:
            body = self.body['headers']

            result = Queries(ScheduleTemplate).execute_deactivate(body['id'])

            return result[0]
        except KeyError as key_err:
            return {"error": str(key_err)}
        except Exception as ex:
            return {"error": str(ex)}

    def reactivate(self):
        try:
            body = self.body['headers']

            result = Queries(ScheduleTemplate).execute_reactivate(body['id'])

            return result[0]
        except KeyError as key_err:
            return {"error": str(key_err)}
        except Exception as ex:
            return {"error": str(ex)}

    def validate(self):
        pass

    def read(self):
        pass


class ScheduleQueries:
    def __init__(self, requests, employee):
        self.request = requests
        self.body = json.loads(requests.body)
        self.employee = employee

    def create(self):
        try:
            schedules = self.body['data']['schedules']
            results = []

            # for schedules_dat in schedules:
            header = schedules['headers']
            parse_header_date = ParseValues([header['date_from'], header['date_to']]).parse_date_from_string()

            head_params = {
                "name": header['name'],
                "employee_id": self.employee,
                "date_from": parse_header_date[0],
                "date_to": parse_header_date[1],
                "is_flexi": header['is_flexi'],
                "is_manual_scheduled": header['is_manual_scheduled'],
            }

            head_result = Queries(Schedule).execute_create(head_params)
            results.append(head_result)

            for line in schedules['lines']:
                parse_line_time = ParseValues([line['time_from'], line['time_to']]).parse_time_from_string()

                line_params = {
                    "day": line['day'],
                    "time_from": parse_line_time[0],
                    "time_to": parse_line_time[1],
                    "is_carried": line['is_carried'],
                    "duration": line['duration'],
                    "schedule_id": head_result[1]
                }

                results.append(Queries(ScheduleLine).execute_create(line_params))

            return EvaluateQueryResults(results).execute_query_results()
        except KeyError as key_err:
            return {"error": str(key_err)}
        except Exception as ex:
            return {"error": str(ex)}

    def change(self):
        try:
            schedules = self.body['data']['schedules']
            employee = self.employee
            results = []

            header = schedules['headers']
            header_id = header['id']

            if header_id == '':
                self.employee = Employee(id=employee)
                return self.create()
            else:
                parse_header_date = ParseValues([header['date_from'], header['date_to']]).parse_date_from_string()
                print(str(parse_header_date))

                head_params = {
                    "name": header['name'],
                    "date_from": parse_header_date[0],
                    "date_to": parse_header_date[1],
                    "is_flexi": header['is_flexi'],
                    "is_manual_scheduled": header['is_manual_scheduled'],
                }

                head_result = Queries(Schedule).execute_change(head_params, header_id)
                results.append(head_result)

                for line in schedules['lines']:
                    line_id = line['id']
                    parse_line_time = ParseValues([line['time_from'], line['time_to']]).parse_time_from_string()

                    line_params = {
                        "day": line['day'],
                        "time_from": parse_line_time[0],
                        "time_to": parse_line_time[1],
                        "is_carried": line['is_carried'],
                        "duration": line['duration']
                    }

                    if line_id == "":
                        line_params["schedule_id"] = Schedule(id=header_id)
                        results.append(Queries(ScheduleLine).execute_create(line_params))
                    else:
                        line_params["schedule_id"] = header_id
                        results.append(Queries(ScheduleLine).execute_change(line_params, line_id))

                return EvaluateQueryResults(results).execute_query_results()

        except KeyError as key_err:
            return {"error": str(key_err)}
        except Exception as ex:
            return {"error": str(ex)}

    def deactivate(self):
        try:
            body = self.body['headers']

            result = Queries(Schedule).execute_deactivate(body['id'])

            return result[0]
        except KeyError as key_err:
            return {"error": str(key_err)}
        except Exception as ex:
            return {"error": str(ex)}

    def reactivate(self):
        try:
            body = self.body['headers']

            result = Queries(Schedule).execute_reactivate(body['id'])

            return result[0]
        except KeyError as key_err:
            return {"error": str(key_err)}
        except Exception as ex:
            return {"error": str(ex)}

    def delete_line(self):
        try:
            schedules = self.body['archive']['schedule_lines']
            result = []

            if len(schedules) > 0:
                for schedule in schedules:
                    result.append(Queries(ScheduleLine).execute_unrestricted_delete(schedule))

            return result
        except KeyError as key_err:
            return {"error": str(key_err)}
        except Exception as ex:
            return {"error": str(ex)}

    def read(self):
        pass

    def validate(self):
        pass

    def excel_import_header(self):
        try:
            schedule_header = self.body["data"]
            results = []
            matching_status = True
            compare_list_raw = self._fetch_related_data_header()

            for schedule in schedule_header:
                relational_validations = {"employee": False}
                for employee in compare_list_raw["employees"]:
                    employee_name = "{}{}{}{}".format(employee["first_name"], employee["middle_name"],
                                                      employee["last_name"], employee["suffix"])
                    if schedule["employee_id"].replace(' ', '') == employee_name.replace(' ', '') \
                            and schedule["employee_id"] is not None:
                        schedule["employee_id"] = employee["id"]
                        relational_validations["employee"] = True
                        break
                if not relational_validations["employee"]:
                    matching_status = False
                    break
            if matching_status:
                for schedule in schedule_header:
                    date_from = ParseValues([schedule["date_from"]]).parse_date_from_string()[0]
                    date_to = ParseValues([schedule["date_to"]]).parse_date_from_string()[0]
                    params = {
                        "employee_id_id": schedule["employee_id"],
                        "name": schedule["name"],
                        "date_from": date_from,
                        "date_to": date_to,
                        "is_flexi": schedule["is_flexi"],
                        "is_manual_scheduled": False
                    }
                    result = Queries(Schedule).execute_create(params)
                    results.append(result[0]["result"])
                return results
            else:
                return {"result": False, "message": "Error in the Schedules template."}
        except KeyError as key_err:
            return {"error": str(key_err)}
        except Exception as ex:
            return {"error": str(ex)}

    def excel_import_lines(self):
        try:
            schedule_lines = self.body["data"]
            results = []
            matching_status = True
            compare_list_raw = self._fetch_related_data_lines()

            for line in schedule_lines:
                relational_validations = {"schedule": False}
                for schedule in compare_list_raw["schedules"]:
                    if line["schedule_id"] == schedule["name"]:
                        line["schedule_id"] = schedule["id"]
                        relational_validations["schedule"] = True
                        break
                if not relational_validations["schedule"]:
                    matching_status = False
                    break
            if matching_status:
                for schedule in schedule_lines:
                    time_from = ParseValues([schedule["time_from"]]).parse_time_from_string()[0]
                    time_to = ParseValues([schedule["time_to"]]).parse_time_from_string()[0]
                    params = {
                        "schedule_id": schedule["schedule_id"],
                        "day": schedule["day"],
                        "time_from": time_from,
                        "time_to": time_to,
                        "is_carried": schedule["is_carried"],
                        "work_duration": schedule["work_duration"]
                    }
                    result = Queries(ScheduleLine).execute_create(params)
                    results.append(result[0]["result"])
                return results
            else:
                return {"result": False, "message": "Error in the Schedules template."}
        except KeyError as key_err:
            return {"error": str(key_err)}
        except Exception as ex:
            return {"error": str(ex)}

    def _fetch_related_data_header(self):
        company_id = self.body["company_id"]
        return {
            "employees": execute_raw_query(statements.get_all_employees.format(company_id)),
        }

    def _fetch_related_data_lines(self):
        company_id = self.body["company_id"]
        return {
            "schedules": execute_raw_query(statements.get_all_schedules.format(company_id)),
        }


class _BuildScheduleParameters:
    def __init__(self, **params):
        self.params = params

    def header_create_params(self):
        data = self.params['data']
        company_id = self.params['company_id']
        parse_header_date = ParseValues([data['date_from'], data['date_to']]).parse_date_from_string()

        head_params = {
            "name": data['name'],
            "date_from": parse_header_date[0],
            "date_to": parse_header_date[1],
            "is_flexi": data['is_flexi'],
            "is_manual_scheduled": data['is_manual_scheduled'],
            "company_id": company_id
        }

        return head_params

    def header_change_params(self):
        data = self.params['data']
        parse_header_date = ParseValues([data['date_from'], data['date_to']]).parse_date_from_string()

        head_params = {
            "name": data['name'],
            "date_from": parse_header_date[0],
            "date_to": parse_header_date[1],
            "is_flexi": data['is_flexi'],
            "is_manual_scheduled": data['is_manual_scheduled'],
        }

        return head_params

    def line_create_params(self):
        data = self.params['data']
        head_result = self.params['head_obj']
        parse_line_time = ParseValues([data['time_from'], data['time_to']]).parse_time()

        line_params = {
            "day": data['day'],
            "time_from": parse_line_time[0],
            "time_to": parse_line_time[1],
            "is_carried": data['is_carried'],
            "duration": data['duration'],
            "schedule_template_id": head_result
        }

        return line_params

    def line_change_params(self):
        data = self.params['data']
        head_id = self.params['head_id']
        parse_line_time = ParseValues([data['time_from'], data['time_to']]).parse_time()
        line_params = {
            "day": data['day'],
            "time_from": parse_line_time[0],
            "time_to": parse_line_time[1],
            "is_carried": data['is_carried'],
            "duration": data['duration'],
            "schedule_template_id": head_id
        }

        return line_params

    def line_create_params_core(self):
        data = self.params['data']
        head_result = self.params['head_obj']
        parse_line_time = ParseValues([data['time_from'], data['time_to']]).parse_time()

        line_params = {
            "day": data['day'],
            "time_from": parse_line_time[0],
            "time_to": parse_line_time[1],
            "is_carried": data['is_carried'],
            "duration": data['duration'],
            "schedule_id": head_result
        }

        return line_params

    def line_change_params_core(self):
        data = self.params['data']
        head_id = self.params['head_id']
        parse_line_time = ParseValues([data['time_from'], data['time_to']]).parse_time()
        line_params = {
            "day": data['day'],
            "time_from": parse_line_time[0],
            "time_to": parse_line_time[1],
            "is_carried": data['is_carried'],
            "duration": data['duration'],
            "schedule_id": head_id
        }

        return line_params
