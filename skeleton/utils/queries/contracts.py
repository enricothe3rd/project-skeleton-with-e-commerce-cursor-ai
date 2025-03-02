import json
from payroll.models.setup import (EmployeeContractTemplate, LeaveTemplate, AllowanceTemplate,
                                  DeductionTemplateGroup, WorkSetup, ScheduleTemplate)
from payroll.models.core import (EmployeeContract, Schedule, Employee)
from payroll.utils.general.general import Queries, ParseValues, EvaluateQueryResults, execute_raw_query
from payroll.utils.queries.statements import select as statements


class EmployeeContractTemplateQueries:
    def __init__(self, requests):
        self.request = requests
        self.body = json.loads(requests.body)

    def create(self):
        try:
            company_id = self.request.COOKIES['company_id']
            body = self.body['data']

            leave_template_object = LeaveTemplate(id=body['leave_template_id'])
            allowance_template_object = AllowanceTemplate(id=body['allowance_template_id'])
            deduction_template_header_object = DeductionTemplateGroup(id=body['deduction_group_id'])
            work_setup_object = WorkSetup(id=body['work_setup_id'])
            schedule_template_object = ScheduleTemplate(id=body['schedule_template_id'])

            params = {
                "name": body['name'],
                "hourly_rate": body['hourly_rate'],
                "daily_work_hours": body['daily_work_hours'],
                "is_max_mandatory": body['is_max_mandatory'],
                "leave_template_id": leave_template_object,
                "allowance_template_id": allowance_template_object,
                "deduction_template_header_id": deduction_template_header_object,
                "schedule_template_id": schedule_template_object,
                "is_require_attendance_approval": body['is_require_attendance_approval'],
                "work_setup_id": work_setup_object,
                "company_id": company_id
            }
            result = Queries(EmployeeContractTemplate).execute_create(params)

            return result[0]
        except KeyError as key_err:
            return {"error": str(key_err)}
        except Exception as ex:
            return {"error": str(ex)}

    def change(self):
        try:
            body = self.body['data']

            params = {
                "name": body['name'],
                "hourly_rate": body['hourly_rate'],
                "daily_work_hours": body['daily_work_hours'],
                "is_max_mandatory": body['is_max_mandatory'],
                "leave_template_id": body['leave_template_id'],
                "allowance_template_id": body['allowance_template_id'],
                "deduction_template_header_id": body['deduction_group_id'],
                "schedule_template_id": body['work_setup_id'],
                "is_require_attendance_approval": body['is_require_attendance_approval'],
                "work_setup_id": body['schedule_template_id']
            }
            result = Queries(EmployeeContractTemplate).execute_change(params, body['id'])

            return result[0]
        except KeyError as key_err:
            return {"error": str(key_err)}
        except Exception as ex:
            return {"error": str(ex)}

    def deactivate(self):
        try:
            body = self.body['data']

            result = Queries(EmployeeContractTemplate).execute_deactivate(body['id'])

            return result[0]
        except KeyError as key_err:
            return {"error": str(key_err)}
        except Exception as ex:
            return {"error": str(ex)}

    def reactivate(self):
        try:
            body = self.body['data']

            result = Queries(EmployeeContractTemplate).execute_reactivate(body['id'])

            return result[0]
        except KeyError as key_err:
            return {"error": str(key_err)}
        except Exception as ex:
            return {"error": str(ex)}

    def read(self):
        pass

    def validate(self):
        pass


class EmployeeContractQueries:
    def __init__(self, requests, employee_id):
        self.request = requests
        self.body = json.loads(requests.body)
        self.employee = employee_id

    def create(self):
        try:
            contract_det = self.body['data']['contract']
            employee = self.employee
            result = []

            parse_date = ParseValues([contract_det['date_start'], contract_det['date_end']]).parse_date_from_string()
            work_setup_object = WorkSetup(id=contract_det['work_setup_id'])

            params = {
                "name": contract_det['name'],
                "employee_id": employee,
                "hourly_rate": contract_det['hourly_rate'],
                "monthly_rate": contract_det['monthly_rate'],
                "employee_positions_id": contract_det['employee_positions_id'],
                "department_id": contract_det['department_id'],
                "team_id": contract_det['team_id'],
                "daily_work_hours": contract_det['daily_work_hours'],
                "factor_rate": contract_det['factor_rate'],
                "work_setup_id": work_setup_object,
                "date_start": parse_date[0],
                "date_end": parse_date[1],
            }
            result.append(Queries(EmployeeContract).execute_create(params))
            print(result)
            return EvaluateQueryResults(result).execute_query_results()
        except KeyError as key_err:
            print({"error": str(key_err)})
            return {"error": str(key_err)}
        except Exception as ex:
            print({"error": str(ex)})
            return {"error": str(ex)}

    def change(self):
        try:
            body = self.body['data']['contract']
            employee = self.employee

            if body['id'] == '':
                self.employee = Employee(id=employee)
                return self.create()
            else:
                results = []
                parse_date = ParseValues([body['date_start'], body['date_end']]).parse_date_from_string()
                params = {
                    "name": body['name'],
                    "hourly_rate": body['hourly_rate'],
                    "monthly_rate": body['monthly_rate'],
                    "employee_id": employee,
                    "daily_work_hours": body['daily_work_hours'],
                    "factor_rate": body['factor_rate'],
                    "employee_positions_id": body['employee_positions_id'],
                    "department_id": body['department_id'],
                    "team_id": body['team_id'],
                    "work_setup_id": body['work_setup_id'],
                    "is_monthly_salary": body['is_monthly_salary'],
                    "date_start": parse_date[0],
                    "date_end": parse_date[1],
                }
                results.append(Queries(EmployeeContract).execute_change(params, body['id']))
                return EvaluateQueryResults(results).execute_query_results()

        except KeyError as key_err:
            return {"error": str(key_err)}
        except Exception as ex:
            return {"error": str(ex)}

    def deactivate(self):
        try:
            body = self.body['data']

            result = Queries(Schedule).execute_deactivate(body['id'])

            return result[0]
        except KeyError as key_err:
            return {"error": str(key_err)}
        except Exception as ex:
            return {"error": str(ex)}

    def reactivate(self):
        try:
            body = self.body['data']

            result = Queries(Schedule).execute_reactivate(body['id'])

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
        try:
            contracts = self.body["data"]
            results = []
            matching_status = True
            compare_list_raw = self._fetch_related_data()

            # GET VALID DATA FOR RELATED DATA
            for contract in contracts:
                relational_validations = {"employee": False, "departments": False, "teams": False, "positions": False}
                for employee in compare_list_raw["employees"]:
                    employee_name = "{}{}{}{}".format(employee["first_name"], employee["middle_name"],
                                                      employee["last_name"], employee["suffix"])
                    if contract["employee_id"].replace(' ', '') == employee_name.replace(' ', '')\
                            and contract["employee_id"] is not None:
                        contract["employee_id"] = employee["id"]
                        relational_validations["employee"] = True
                        break
                for department in compare_list_raw["departments"]:
                    if contract["department_id"] == department["name"] and contract["department_id"] is not None:
                        contract["department_id"] = department["id"]
                        relational_validations["departments"] = True
                        break
                for position in compare_list_raw["positions"]:
                    if (contract["employee_positions_id"] == position["name"] and
                            contract["employee_positions_id"] is not None):
                        contract["employee_positions_id"] = position["id"]
                        relational_validations["teams"] = True
                        break
                for team in compare_list_raw["teams"]:
                    if contract["team_id"] == team["name"] and contract["team_id"] is not None:
                        contract["team_id"] = team["id"]
                        relational_validations["positions"] = True
                        break

                if not relational_validations["departments"]:
                    contract["department_id"] = None
                if not relational_validations["positions"]:
                    contract["employee_positions_id"] = None
                if not relational_validations["teams"]:
                    contract["team_id"] = None
                if not relational_validations["employee"]:
                    matching_status = False
                    break

            if matching_status:
                for contract in contracts:
                    date_start = ParseValues([contract["date_start"]]).parse_date_from_string()[0]
                    date_end = ParseValues([contract["date_end"]]).parse_date_from_string()[0]
                    params = {
                        "name": contract["name"],
                        "hourly_rate": contract["hourly_rate"],
                        "monthly_rate": contract["monthly_rate"],
                        "daily_work_hours": contract["daily_work_hours"],
                        "factor_rate": contract["factor_rate"],
                        "date_start": date_start,
                        "date_end": date_end,
                        "is_monthly_salary": contract["is_monthly_salary"],
                        "employee_positions_id": contract["employee_positions_id"],
                        "department_id": contract["department_id"],
                        "team_id": contract["team_id"],
                        "employee_id_id": contract["employee_id"],
                    }
                    result = Queries(EmployeeContract).execute_create(params)
                    results.append(result[0]["result"])
                return results
            else:
                return {"result": False, "message": "Error in the Contracts template."}
        except KeyError as key_err:
            return {"error": str(key_err)}
        except Exception as ex:
            return {"error": str(ex)}

    def _fetch_related_data(self):
        company_id = self.body["company_id"]
        return {
            "employees": execute_raw_query(statements.get_all_employees.format(company_id)),
            "departments": execute_raw_query(statements.get_all_departments.format(company_id)),
            "positions": execute_raw_query(statements.get_all_positions.format(company_id)),
            "teams": execute_raw_query(statements.get_all_teams.format(company_id)),
        }
