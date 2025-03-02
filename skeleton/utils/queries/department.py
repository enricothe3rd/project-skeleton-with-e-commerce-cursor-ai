import json
from payroll.utils.general.general import Queries, ParseValues, EvaluateQueryResults
from payroll.models.setup import EmployeeContractTemplate
from payroll.models.core import (Department)


class DepartmentQueries:
    def __init__(self, requests):
        self.request = requests
        self.body = json.loads(requests.body)

    def create(self):
        try:
            company_id = self.request.COOKIES['company_id']
            body = self.body['data']
            contract_template_obj = EmployeeContractTemplate(id=body['contract_template_id'])

            params = {
                "name": body['name'],
                "contract_template_id": contract_template_obj,
                "company_id": company_id
            }
            result = Queries(Department).execute_create(params)

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
                "contract_template_id": body['contract_template_id'],
            }
            result = Queries(Department).execute_change(params, body['id'])

            return result[0]
        except KeyError as key_err:
            return {"error": str(key_err)}
        except Exception as ex:
            return {"error": str(ex)}

    def deactivate(self):
        try:
            body = self.body['data']
            result = Queries(Department).execute_deactivate(body['id'])

            return result[0]
        except KeyError as key_err:
            return {"error": str(key_err)}
        except Exception as ex:
            return {"error": str(ex)}

    def reactivate(self):
        try:
            body = self.body['data']
            result = Queries(Department).execute_reactivate(body['id'])

            return result[0]
        except KeyError as key_err:
            return {"error": str(key_err)}
        except Exception as ex:
            return {"error": str(ex)}

    def validate(self):
        pass

    def read(self):
        pass


class DepartmentsCRUD:
    def __init__(self, requests):
        self.request = requests
        self.body = json.loads(requests.body)

    def create_update(self):
        try:
            data = self.body
            results = []
            for values in data:
                if values["id"] != "" and values["id"] and not None and values["id"] != 0:
                    params = {
                        "name": values["name"],
                        "manager_id": values["manager_id"]
                    }
                    results.append(Queries(Department).execute_change(params, values["id"]))
                else:
                    params = {
                        "name": values["name"],
                        "manager_id": values["manager_id"],
                        "company_id": self.request.COOKIES['company_id']
                    }
                    results.append(Queries(Department).execute_create(params))
            if EvaluateQueryResults(results).execute_query_results():
                return {
                    "status": True,
                    "message": "All records was saved/updated successfully!",
                    "error": None
                }
            else:
                return {
                    "status": False,
                    "message": "Not all records was saved/updated.",
                    "error": None
                }
        except KeyError as key_err:
            return {"error": str(key_err)}
        except Exception as ex:
            return {"error": str(ex)}

    def archive(self):
        try:
            data = self.body
            print(data)
            result = Queries(Department).execute_deactivate(data["id"])

            if result[0]["status"]:
                return {
                    "status": True,
                    "message": "Department was archived.",
                    "error": None
                }
            else:
                return {
                    "status": False,
                    "message": "Archive of department failed.",
                    "error": "Archive Failed"
                }
        except KeyError as key_err:
            return {"error": str(key_err)}
        except Exception as ex:
            return {"error": str(ex)}

    def excel_import(self):
        pass
