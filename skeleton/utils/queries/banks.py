import json
from payroll.utils.general.general import Queries, EvaluateQueryResults
from payroll.models.core import EmployeeBankDetails, Employee


class BankQueries:
    def __init__(self, requests, employee_id):
        self.request = requests
        self.body = json.loads(requests.body)
        self.employee = employee_id

    def create(self):
        try:
            banks = self.body['data']['bank_details']
            employee = self.employee
            results = []

            for bank in banks:
                params = {
                    "bank_name": bank['bank_name'],
                    "bank_no": bank['bank_no'],
                    "employee_id": employee
                }

                results.append(Queries(EmployeeBankDetails).execute_create(params))

            return EvaluateQueryResults(results).execute_query_results()
        except KeyError as key_err:
            return {"error": str(key_err)}
        except Exception as ex:
            return {"error": str(ex)}

    def change(self):
        try:
            banks = self.body['data']['bank_details']
            employee = self.employee
            results = []

            for bank in banks:
                bank_id = bank['id']

                params = {
                    "bank_name": bank['bank_name'],
                    "bank_no": bank['bank_no'],
                }

                if bank_id == "":
                    params["employee_id"] = Employee(id=employee)
                    results.append(Queries(EmployeeBankDetails).execute_create(params))
                else:
                    params["employee_id"] = employee
                    results.append(Queries(EmployeeBankDetails).execute_change(params, bank_id))

            return EvaluateQueryResults(results).execute_query_results()
        except KeyError as key_err:
            return {"error": str(key_err)}
        except Exception as ex:
            return {"error": str(ex)}

    def deactivate(self):
        try:
            banks = self.body['archive']['banks']
            result = []

            if len(banks) > 0:
                for bank in banks:
                    print(bank)
                    result.append(Queries(EmployeeBankDetails).execute_deactivate(bank))

            return result
        except KeyError as key_err:
            return {"error": str(key_err)}
        except Exception as ex:
            return {"error": str(ex)}

    def reactivate(self):
        try:
            body = self.body['data']['allowances']
            result = []

            for bank in body:
                result.append(Queries(EmployeeBankDetails).execute_reactivate(bank['id']))

            return result
        except KeyError as key_err:
            return {"error": str(key_err)}
        except Exception as ex:
            return {"error": str(ex)}

    def remove(self):
        pass

    def validate(self):
        pass

    def read(self):
        pass

    def excel_import(self):
        pass
