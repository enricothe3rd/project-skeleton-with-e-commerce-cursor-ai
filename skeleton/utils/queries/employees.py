import json
import requests
from django.conf import settings
from payroll.utils.general.general import Queries, ParseValues, EvaluateQueryResults
from payroll.models.core import Employee, EmployeeAddress
from payroll.utils.queries.contracts import EmployeeContractQueries
from payroll.utils.queries.deduction import DeductionQueries, DeductionEmployeeRelQueries
from payroll.utils.queries.schedule import ScheduleQueries
from payroll.utils.queries.allowance import AllowanceQueries
from payroll.utils.queries.leaves import LeaveQueries
from payroll.utils.queries.validations.core import ValidateEmployeeOnboarding
from payroll.utils.queries.positions import PositionsRelQueries
from payroll.utils.queries.banks import BankQueries
from payroll.utils.queries.previous_employment import PreviousEmploymentQueries
from payroll.utils.queries.read.read_core import EmployeeOnboardingResponse


class EmployeeOnboardingQueries:
    def __init__(self, request):
        self.request = request
        self.body = json.loads(request.body)

    def create(self, **data):
        res = ValidateEmployeeOnboarding(self.body['data']).execute()

        if res is True:
            other_detail_res = []
            construct_detail_res = EmployeeDetailsExecuteQuery(self.request)
            if "users" in self.body["data"]:
                detail_res = construct_detail_res.create(id=data["id"])
            else:
                detail_res = construct_detail_res.create()

            if detail_res[1]['status'] is True:
                other_detail_res = {
                    "contract": EmployeeContractQueries(self.request, detail_res[0]).create(),
                    "positions": PositionsRelQueries(self.request, detail_res[0]).create(),
                    "banks": BankQueries(self.request, detail_res[0]).create(),
                    "leaves": LeaveQueries(self.request).leave_credits_crud(detail_res[0]).create(),
                    "allowances": AllowanceQueries(self.request, detail_res[0]).create(),
                    "schedules": ScheduleQueries(self.request, detail_res[0]).create(),
                    "deductions": DeductionEmployeeRelQueries(self.request, detail_res[0]).create(),
                    "previous_employment": PreviousEmploymentQueries(self.request, detail_res[0]).create(),
                }

            evaluation_result = EvaluateQueryResults(other_detail_res).execute_batch_query_results()

            if evaluation_result is True:
                # Construct select query result response
                return EmployeeOnboardingResponse(detail_res[1]['id']).execute()
            else:
                # EXECUTE ROLLBACK
                return "Incomplete import"
        else:
            return "VALIDATION ERROR"

    def change(self, **data):
        res = ValidateEmployeeOnboarding(self.body['data']).execute()
        if res is True:
            employee_id = self.body['data']['details']['id']

            if "users" in self.body["data"]:
                detail_res = EmployeeDetailsExecuteQuery(self.request).change(
                    employee=employee_id, associated_user=data["id"]
                )
            else:
                detail_res = EmployeeDetailsExecuteQuery(self.request).change(employee=employee_id)

            other_detail_res = {
                "contract": EmployeeContractQueries(self.request, employee_id).change(),
                "positions": PositionsRelQueries(self.request, employee_id).change(),
                "banks": BankQueries(self.request, employee_id).change(),
                "leaves": LeaveQueries(self.request).leave_credits_crud(employee_id).change(),
                "allowances": AllowanceQueries(self.request, employee_id).change(),
                "schedules": ScheduleQueries(self.request, employee_id).change(),
                "deductions": DeductionEmployeeRelQueries(self.request, employee_id).change(),
                "previous_employment": PreviousEmploymentQueries(self.request, employee_id).change(),
            }

            evaluation_result = EvaluateQueryResults(other_detail_res).execute_batch_query_results()

            if evaluation_result is True:
                # Construct select query result response
                return EmployeeOnboardingResponse(detail_res[1]['id']).execute()
            else:
                # EXECUTE ROLLBACK
                return "Incomplete import"
        else:
            return "VALIDATION ERROR"


class EmployeeDetailsExecuteQuery:
    def __init__(self, requests):
        self.request = requests
        self.body = json.loads(requests.body)

    def create(self, **data):
        try:
            company_id = self.request.COOKIES['company_id']
            body = self.body['data']

            if "users" in body:
                users = body["users"]
                details = body["details"]
                birthday = ParseValues([users['birthday']]).parse_date_from_string()

                if "company_id" in users:
                    company_id = users["company_id"]

                emp_params = {
                    "badge_no": details["badge_no"],  # AUTO GENERATE BADGE NUMBER
                    "image": details['image'],
                    "first_name": users['first_name'],
                    "middle_name": users['middle_name'],
                    "last_name": users['last_name'],
                    "suffix": users['suffix'],
                    "professional_extensions": users['professional_extensions'],
                    "sex": users['sex'],
                    "birthday": birthday[0],
                    "email": users['email'],
                    "mobile": users['mobile'],
                    "tin": users['tin'],
                    "sss_no": details["sss_no"],
                    "phic_no": details["phic_no"],
                    "hdmf_no": details["hdmf_no"],
                    "long_name": "%s - %s, %s %s %s %s" %
                                 (users['badge_no'], users['last_name'], users['first_name'],
                                  users['middle_name'], users['suffix'], users['professional_extensions']),
                    "company_id": company_id,
                    "associated_user_id": data["id"]
                }
            else:
                details = body['details']
                birthday = ParseValues([details['birthday']]).parse_date_from_string()

                if "company_id" in details:
                    company_id = details["company_id"]

                emp_params = {
                    "badge_no": details['badge_no'],  # AUTO GENERATE BADGE NUMBER
                    "image": details['image'],
                    "first_name": details['first_name'],
                    "middle_name": details['middle_name'],
                    "last_name": details['last_name'],
                    "suffix": details['suffix'],
                    "professional_extensions": details['professional_extensions'],
                    "sex": details['sex'],
                    "birthday": birthday[0],
                    "email": details['email'],
                    "mobile": details['mobile'],
                    "tin": details['tin'],
                    "is_manager": details['is_manager'],
                    "sss_no": details['sss_no'],
                    "phic_no": details['phic_no'],
                    "hdmf_no": details['hdmf_no'],
                    "long_name": "%s - %s, %s %s %s %s" %
                                 (details['badge_no'], details['last_name'], details['first_name'],
                                  details['middle_name'], details['suffix'], details['professional_extensions']),
                    "company_id": company_id
                }

            emp_result = Queries(Employee).execute_create(emp_params)
            for addresses in body['addresses']:
                address_params = {
                    "employee_id": emp_result[1],
                    "line": addresses['line'],
                    "barangay": addresses['barangay'],
                    "city": addresses['city'],
                    "province": addresses['province'],
                    "zip": addresses['zip'],
                }

                Queries(EmployeeAddress).execute_create(address_params)

            return emp_result[1], emp_result[0]
            # return str(emp_params)
        except KeyError as key_err:
            print("Key Error: " + str(key_err))
            return {"Key Error": str(key_err)}
        except Exception as ex:
            print(str(ex))
            return {"Exception Error": str(ex)}

    def change(self, **data):
        try:
            body = self.body['data']
            details = body['details']

            birthday = ParseValues([details['birthday']]).parse_date_from_string()

            emp_params = {
                "badge_no": details['badge_no'],  # AUTO GENERATE BADGE NUMBER
                "image": details['image'],
                "first_name": details['first_name'],
                "middle_name": details['middle_name'],
                "last_name": details['last_name'],
                "suffix": details['suffix'],
                "professional_extensions": details['professional_extensions'],
                "sex": details['sex'],
                "birthday": birthday[0],
                "email": details['email'],
                "mobile": details['mobile'],
                "tin": details['tin'],
                "sss_no": details['sss_no'],
                "phic_no": details['phic_no'],
                "hdmf_no": details['hdmf_no'],
                "is_manager": details['is_manager'],
            }
            if "associated_user" in data:
                emp_params["associated_user_id"] = data["associated_user"]
                old = Employee.objects.filter(associated_user_id=data["associated_user"]).values()
                if len(old) > 0:
                    Queries(Employee).execute_change(
                        {"associated_user_id": None}, old[0]["id"]
                    )

            emp_result = Queries(Employee).execute_change(emp_params, data["employee"])

            for addresses in body['addresses']:
                address_id = addresses['id']

                address_params = {
                    "line": addresses['line'],
                    "barangay": addresses['barangay'],
                    "city": addresses['city'],
                    "province": addresses['province'],
                    "zip": addresses['zip'],
                }

                if address_id == "":
                    address_params["employee_id"] = Employee(id=data["employee"])
                    Queries(EmployeeAddress).execute_create(address_params)
                else:
                    address_params["employee_id"] = data["employee"]
                    Queries(EmployeeAddress).execute_change(address_params, address_id)

            # return employee
            return emp_result[1], emp_result[0]
        except KeyError as key_err:
            return {"Key Error": str(key_err)}
        except Exception as ex:
            return {"Exception Error": str(ex)}

    def deactivate(self):
        try:
            body = self.body['data']
            result = Queries(Employee).execute_deactivate(body['id'])

            return result[0]
        except KeyError as key_err:
            return {"error": str(key_err)}
        except Exception as ex:
            return {"error": str(ex)}

    def reactivate(self):
        try:
            body = self.body['data']
            result = Queries(Employee).execute_reactivate(body['id'])

            return result[0]
        except KeyError as key_err:
            return {"error": str(key_err)}
        except Exception as ex:
            return {"error": str(ex)}

    def delete_line(self):
        try:
            addresses = self.body['archive']['addresses']
            result = []

            if len(addresses) > 0:
                for address in addresses:
                    result.append(Queries(EmployeeAddress).execute_unrestricted_delete(address))

            return result
        except KeyError as key_err:
            return {"error": str(key_err)}
        except Exception as ex:
            return {"error": str(ex)}

    def validate(self):
        pass

    def read(self):
        pass

    def excel_import(self):
        raw_users_list = self._fetch_initial_users_list()
        company_id = self.body["company_id"]
        employees = self.body["data"]
        results = []

        for employee in employees:
            employee["Associated User"] = None
            for user in raw_users_list:
                if (employee["First Name"] == user["first_name"] and employee["Middle Name"] == user["middle_name"]
                        and employee["Last Name"] == user["last_name"] and employee["Suffix"] == user["suffix"]):
                    employee["Associated User"] = user["id"]
                    break
            birthday = ParseValues([employee["birthday"]]).parse_date_from_string()
            params = {
                "badge_no": "",
                "first_name": employee["first_name"],
                "middle_name": employee["middle_name"],
                "last_name": employee["last_name"],
                "suffix": employee["suffix"],
                "professional_extensions": employee["professional_extensions"],
                "sex": employee["sex"],
                "birthday": birthday,
                "email": employee["email"],
                "mobile": employee["mobile"],
                "tin": employee["tin"],
                "company_id": company_id,
                "associated_user": employee["associated_user"],
                "long_name": "{}, {} {} {} {}".format(
                    employee["last_name"], employee["first_name"], employee["middle_name"],
                    employee["suffix"], employee["professional_extensions"]
                ),
                "sss_no": employee["sss_no"],
                "phic_no": employee["phic_no"],
                "hdmf_no": employee["hdmf_no"],
            }
            results.append(Queries(Employee).execute_create(params))
        return results

    def _fetch_initial_users_list(self):
        data = self.request
        cookies = {
            'level': data.COOKIES['level'],
            'company_id': data.COOKIES['company_id'],
            'token': data.COOKIES['token'],
            'user_id': data.COOKIES['user_id'],
        }
        response = requests.get(
            settings.USER_SERVICE_URL + "/users/users-list?filters=is_active,=,true,None",
            cookies=cookies,
            verify=False
        )
        response_dict = response.json()
        return response_dict
